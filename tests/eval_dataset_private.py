EVAL_DATASET_PRIVATE = [
    {
        "question": "Which function handles the POST /ingest/ endpoint?",
        "ground_truth_file": "api/routers/ingest.py",
        "ground_truth_fn": "ingest_repo"
    },
    {
        "question": "Which function builds the dependency graph from a repository path?",
        "ground_truth_file": "ingestion/graph_builder.py",
        "ground_truth_fn": "build_graph"
    },
    {
        "question": "Which function searches ChromaDB for similar code chunks?",
        "ground_truth_file": "rag/vector_store.py",
        "ground_truth_fn": "search_chunks"
    },
    {
        "question": "Which function converts graph results into embeddable chunks?",
        "ground_truth_file": "rag/embedder.py",
        "ground_truth_fn": "chunks_from_graph_result"
    },
    {
        "question": "Which function routes LLM calls between Groq and Ollama?",
        "ground_truth_file": "llm/router.py",
        "ground_truth_fn": "generate"
    },
    {
        "question": "Which file contains the Groq API client implementation?",
        "ground_truth_file": "llm/groq_client.py",
        "ground_truth_fn": "generate"
    },
    {
        "question": "Where is the ChromaDB persistent client initialized?",
        "ground_truth_file": "rag/vector_store.py",
        "ground_truth_fn": "_get_client"
    },
    {
        "question": "Which function clones a GitHub repository?",
        "ground_truth_file": "ingestion/cloner.py",
        "ground_truth_fn": "clone_repo"
    },
    {
        "question": "Where is the FastAPI app created and configured?",
        "ground_truth_file": "api/main.py",
        "ground_truth_fn": "app"
    },
    {
        "question": "Which function retrieves relevant code chunks for a query?",
        "ground_truth_file": "rag/retriever.py",
        "ground_truth_fn": "retrieve"
    },
]
