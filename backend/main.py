from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.url_detector import analyze_url
from services.message_detector import analyze_message
from services.fusion_engine import scan_threat


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="SovereignShield API",
    description="AI-powered Indian scam and phishing detection platform",
    version="1.0.0"
)


# --------------------------------------------------
# STATIC FRONTEND
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static"
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class ScanRequest(BaseModel):
    message: str


class URLRequest(BaseModel):
    url: str


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "project": "SovereignShield",
        "status": "online",
        "message": "SovereignShield API is running"
    }


# --------------------------------------------------
# FRONTEND
# --------------------------------------------------

@app.get("/app")
def frontend():

    return FileResponse(
        str(FRONTEND_DIR / "index.html")
    )


# --------------------------------------------------
# FULL THREAT SCAN
# --------------------------------------------------

@app.post("/scan")
def scan_message(request: ScanRequest):

    return scan_threat(request.message)


# --------------------------------------------------
# URL ANALYSIS
# --------------------------------------------------

@app.post("/analyze-url")
def analyze_url_endpoint(request: URLRequest):

    return analyze_url(request.url)


# --------------------------------------------------
# MESSAGE ANALYSIS
# --------------------------------------------------

@app.post("/analyze-message")
def analyze_message_endpoint(request: ScanRequest):

    return analyze_message(request.message)