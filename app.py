# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
FastAPI Server for GPT-5 Structured Proofreader
===============================================
Serves the premium proofreader web interface and provides the backend API 
endpoint for interacting with Replicate's Structured Model API.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure we import the proofreading logic from our existing module
from proofreader import proofread_text

# Load environment variables
load_dotenv()

# Verify API key exists
if not os.environ.get("REPLICATE_API_TOKEN"):
    print("[WARNING] REPLICATE_API_TOKEN is not set in the environment.")

app = FastAPI(title="GPT-5 Structured Proofreader API")

# Request model for text input
class ProofreadRequest(BaseModel):
    text: str
    language: str = "en-US"

@app.post("/api/proofread")
async def api_proofread(payload: ProofreadRequest):
    """
    Receives text, calls the GPT-5 Structured API, and returns structured feedback.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        # Run the existing structured proofreading function
        result = proofread_text(text, language=payload.language)
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while communicating with the AI service: {err}"
        )

# Mount the static frontend directory.
# StaticFiles with html=True automatically maps "/" to "index.html" in the directory.
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    print(f"[ERROR] Static folder not found at: {static_dir}")

if __name__ == "__main__":
    # Start the server on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
