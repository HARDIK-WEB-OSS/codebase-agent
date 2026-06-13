"""
Quick latency benchmark — no RAGAS, no OpenAI key needed.
Run: python tests/bench_latency.py
"""
import time
import requests
import statistics

BASE_URL = "http://localhost:8000"
REPO_NAME = "pallets_flask"

QUERIES = [
    "How does Flask handle routing?",
    "What is the application context?",
    "How do blueprints work?",
    "What is the g object?",
    "How does session management work?",
]

def main():
    print("Running latency benchmark...\n")
    latencies = []

    for q in QUERIES:
        start = time.time()
        r = requests.post(
            f"{BASE_URL}/query/",
            json={"repo_name": REPO_NAME, "question": q, "provider": "groq"},
            timeout=60
        )
        lat = round(time.time() - start, 2)
        latencies.append(lat)
        status = "✓" if r.status_code == 200 else "✗"
        print(f"  {status} [{lat}s] {q[:55]}")

    print(f"\n  Mean:   {round(statistics.mean(latencies), 2)}s")
    print(f"  Median: {round(statistics.median(latencies), 2)}s")
    print(f"  P95:    {round(sorted(latencies)[int(len(latencies)*0.95)], 2)}s")
    print(f"  Max:    {round(max(latencies), 2)}s")

if __name__ == "__main__":
    main()
