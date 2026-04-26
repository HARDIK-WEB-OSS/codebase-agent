import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import APP_HOST, APP_PORT, DEBUG, verify_config
from api.routers import ingest, query

app = FastAPI(title="Codebase Onboarding Agent", version="0.1.0", docs_url="/docs" if DEBUG else None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(ingest.router)
app.include_router(query.router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/health")
async def health():
    config = verify_config()
    return {"status": "ok", "config": config["settings"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)
