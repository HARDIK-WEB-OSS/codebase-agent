import requests
import time

BASE_URL = "http://localhost:8000"
REPO_NAME = "HARDIK-WEB-OSS_codebase-agent"

from eval_dataset_private import EVAL_DATASET_PRIVATE

def query(question):
    start = time.time()
    r = requests.post(f"{BASE_URL}/query/",
        json={"repo_name": REPO_NAME, "question": question, "provider": "groq"},
        timeout=60)
    latency = round(time.time() - start, 2)
    if r.status_code == 200:
        return r.json().get("answer", ""), latency
    return "", latency

def main():
    print("=" * 60)
    print("  Private Repo Eval — HARDIK-WEB-OSS/codebase-agent")
    print("=" * 60)

    passed_file = 0
    passed_fn = 0
    latencies = []
    total = len(EVAL_DATASET_PRIVATE)

    for i, item in enumerate(EVAL_DATASET_PRIVATE):
        print(f"\n[{i+1}/{total}] {item['question']}")
        answer, latency = query(item["question"])
        latencies.append(latency)

        file_hit = item["ground_truth_file"] in answer
        fn_hit = item["ground_truth_fn"] in answer

        if file_hit: passed_file += 1
        if fn_hit: passed_fn += 1

        print(f"  File hit : {'✓' if file_hit else '✗'} (expected: {item['ground_truth_file']})")
        print(f"  Fn hit   : {'✓' if fn_hit else '✗'} (expected: {item['ground_truth_fn']})")
        print(f"  Latency  : {latency}s")
        time.sleep(3)

    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  File-level precision : {passed_file}/{total} ({round(passed_file/total*100)}%)")
    print(f"  Function precision   : {passed_fn}/{total} ({round(passed_fn/total*100)}%)")
    print(f"  Avg latency          : {round(sum(latencies)/len(latencies), 2)}s")
    print(f"  Median latency       : {round(sorted(latencies)[len(latencies)//2], 2)}s")
    print("=" * 60)

if __name__ == "__main__":
    main()
