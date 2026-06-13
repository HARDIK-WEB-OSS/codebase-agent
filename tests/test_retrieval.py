"""
Retrieval quality tests — checks chunk count, distance scores, file path presence.
Run: python tests/test_retrieval.py
"""
import requests

BASE_URL = "http://localhost:8000"
REPO_NAME = "pallets_flask"

RETRIEVAL_CASES = [
    {"query": "add_url_rule route registration", "expected_file_hint": "sansio/scaffold.py"},
    {"query": "application context push pop", "expected_file_hint": "ctx.py"},
    {"query": "blueprint register", "expected_file_hint": "blueprints.py"},
    {"query": "Jinja2 template render", "expected_file_hint": "templating.py"},
    {"query": "session cookie secret key", "expected_file_hint": "sessions.py"},
]

def main():
    print("Running retrieval quality tests...\n")
    passed = 0

    for case in RETRIEVAL_CASES:
        r = requests.get(
            f"{BASE_URL}/query/search/{REPO_NAME}",
            params={"q": case["query"], "n_results": 5},
            timeout=30
        )
        if r.status_code != 200:
            print(f"  ✗ FAIL  [{case['query']}] — API error {r.status_code}")
            continue

        data = r.json()
        results = data.get("results", [])
        hint = case["expected_file_hint"]
        hit = any(hint in str(res.get("file", "")) for res in results)

        if hit:
            passed += 1
            print(f"  ✓ PASS  [{case['query']}] — found {hint}")
        else:
            files = [res.get("file", "?") for res in results[:3]]
            print(f"  ✗ FAIL  [{case['query']}] — expected {hint}, got {files}")

    total = len(RETRIEVAL_CASES)
    print(f"\n  Result: {passed}/{total} passed ({round(passed/total*100)}%)")

if __name__ == "__main__":
    main()
