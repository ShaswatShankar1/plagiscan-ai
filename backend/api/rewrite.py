from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class RewriteRequest(BaseModel):
    text: str
    mode: str = "Standard"

class RewriteResponse(BaseModel):
    original: str
    rewritten: str

@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3")
    
    prompt = f"Rewrite the following text to improve originality while preserving meaning and academic integrity. Mode: {request.mode}\n\nText: {request.text}\n\nRewritten text:"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "original": request.text,
                "rewritten": data.get("response", "").strip()
            }
    except Exception as e:
        # Prompt requirement: "If a service is unavailable, show the actual service state."
        raise HTTPException(
            status_code=503, 
            detail=f"Rewrite service is temporarily unavailable. Could not connect to AI Provider at {ollama_url}. Details: {str(e)}"
        )
