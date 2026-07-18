from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from src.orchestrator import run_analysis
from src.schemas import AnalyzeResponse

app = FastAPI(title="Design Critic")

INDEX_HTML = (Path(__file__).parent / "frontend" / "index.html").read_text()
MAX_BYTES = 4_000_000  # stay under Vercel's 4.5MB request body cap with margin


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    return INDEX_HTML


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(image: UploadFile = File(...)) -> AnalyzeResponse:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")

    data = await image.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "Image too large (max ~4MB). Please compress and retry.")

    return await run_analysis(data, image.content_type)
