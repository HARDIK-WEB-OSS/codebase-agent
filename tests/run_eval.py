"""
Codebase Agent — RAGAS Evaluation Pipeline
Run: python tests/run_eval.py
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
REPO_URL = "https://github.com/pallets/flask"
REPO_NAME = "pallets_flask"

# ── RAGAS imports ──────────────────────────────────────────────────────────────
try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("[WARN] RAGAS not installed. Only latency + basic scores will run.")

from eval_dataset import EVAL_DATASET


def check_server():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False


def ingest_repo_skip():
    print(f"\n[1/3] Ingesting {REPO_URL} ...")
    r = requests.post(f"{BASE_URL}/ingest/", json={"github_url": REPO_URL}, timeout=300)
    if r.status_code == 200:
        print("     ✓ Ingestion complete")
    else:
        print(f"     ✗ Ingestion failed: {r.text}")
        exit(1)


def query_agent(question: str) -> dict:
    start = time.time()
    r = requests.post(
        f"{BASE_URL}/query/",
        json={"repo_name": REPO_NAME, "question": question, "provider": "groq"},
        timeout=60
    )
    latency = round(time.time() - start, 2)
    if r.status_code == 200:
        data = r.json()
        return {
            "answer": data.get("answer", ""),
            "contexts": data.get("contexts", [data.get("context", "")]),
            "latency": latency,
            "status": "ok"
        }
    return {"answer": "", "contexts": [], "latency": latency, "status": "error"}


def run_basic_eval(results: list) -> dict:
    """Basic metrics without RAGAS — for quick resume numbers."""
    total = len(results)
    success = sum(1 for r in results if r["status"] == "ok")
    avg_latency = round(sum(r["latency"] for r in results) / total, 2)
    p95_latency = round(sorted(r["latency"] for r in results)[int(total * 0.95)], 2)

    # Keyword overlap score (poor man's relevancy)
    scores = []
    for r in results:
        if not r["answer"]:
            scores.append(0)
            continue
        gt_words = set(r["ground_truth"].lower().split())
        ans_words = set(r["answer"].lower().split())
        overlap = len(gt_words & ans_words) / len(gt_words) if gt_words else 0
        scores.append(round(overlap, 3))

    avg_keyword_overlap = round(sum(scores) / len(scores), 3)

    return {
        "total_questions": total,
        "successful_queries": success,
        "success_rate": f"{round(success/total*100, 1)}%",
        "avg_latency_sec": avg_latency,
        "p95_latency_sec": p95_latency,
        "avg_keyword_overlap": avg_keyword_overlap,
    }


def run_ragas_eval(results: list) -> dict:
    """Full RAGAS evaluation — faithfulness, relevancy, precision, recall."""
    dataset = Dataset.from_dict({
        "question":   [r["question"] for r in results if r["status"] == "ok"],
        "answer":     [r["answer"]   for r in results if r["status"] == "ok"],
        "contexts":   [r["contexts"] for r in results if r["status"] == "ok"],
        "ground_truth": [r["ground_truth"] for r in results if r["status"] == "ok"],
    })

    print("\n[3/3] Running RAGAS metrics (needs OpenAI key for judge LLM)...")
    score = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    return {
        "faithfulness":       round(score["faithfulness"], 3),
        "answer_relevancy":   round(score["answer_relevancy"], 3),
        "context_precision":  round(score["context_precision"], 3),
        "context_recall":     round(score["context_recall"], 3),
    }


def main():
    print("=" * 60)
    print("  Codebase Agent — Evaluation Pipeline")
    print("=" * 60)

    # Server check
    if not check_server():
        print("\n[ERROR] Server not running. Start it first:")
        print("  uvicorn api.main:app --reload --port 8000")
        exit(1)
    print("\n[✓] Server is up")

    # Ingest
    pass

    # Query all questions
    print(f"\n[2/3] Running {len(EVAL_DATASET)} queries...")
    results = []
    for i, item in enumerate(EVAL_DATASET):
        print(f"     [{i+1}/{len(EVAL_DATASET)}] {item['question'][:60]}...")
        result = query_agent(item["question"])
        result["question"]     = item["question"]
        result["ground_truth"] = item["ground_truth"]
        results.append(result)
        time.sleep(3)  # rate limit buffer

    # Basic metrics
    basic = run_basic_eval(results)
    print("\n── Basic Metrics ─────────────────────────────────────────")
    for k, v in basic.items():
        print(f"   {k:<30} {v}")

    # RAGAS metrics
    ragas_scores = {}
    if RAGAS_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        ragas_scores = run_ragas_eval(results)
        print("\n── RAGAS Metrics ─────────────────────────────────────────")
        for k, v in ragas_scores.items():
            print(f"   {k:<30} {v}")
    else:
        print("\n[SKIP] RAGAS skipped — set OPENAI_API_KEY in .env to enable")

    # Save full report
    report = {
        "timestamp": datetime.now().isoformat(),
        "repo": REPO_URL,
        "basic_metrics": basic,
        "ragas_metrics": ragas_scores,
        "raw_results": results,
    }
    with open("tests/eval_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n── Resume Numbers (copy these) ───────────────────────────")
    print(f"   Success rate:    {basic['success_rate']}")
    print(f"   Avg latency:     {basic['avg_latency_sec']}s")
    print(f"   P95 latency:     {basic['p95_latency_sec']}s")
    if ragas_scores:
        print(f"   Faithfulness:    {ragas_scores['faithfulness']}")
        print(f"   Answer Relevancy:{ragas_scores['answer_relevancy']}")

    print("\n[✓] Full report saved → tests/eval_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
