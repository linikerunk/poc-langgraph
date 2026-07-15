import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from agent import analyze_logs


app = FastAPI(
    title="POC LangAI API",
    description="API for monitoring and analyzing logs with LangChain",
    version="0.1.0",
)


class LogAnalysisRequest(BaseModel):
    service_name: str = "unknown"
    logs: str


@app.get("/", summary="Health check")
def root() -> dict:
    return {
        "message": "POC LangAI API is running",
        "endpoints": ["/analyze-logs"],
    }


@app.post("/analyze-logs", summary="Analyze logs and detect incidents")
def analyze_logs_endpoint(payload: LogAnalysisRequest) -> dict:
    if not payload.logs or not payload.logs.strip():
        raise HTTPException(status_code=400, detail="logs cannot be empty")

    result = analyze_logs(payload.logs, payload.service_name)
    return {
        "service_name": payload.service_name,
        "analysis": result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
