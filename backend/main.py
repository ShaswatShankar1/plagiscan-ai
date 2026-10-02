from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import analyze, rewrite

app = FastAPI(title="PlagiScan AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(rewrite.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}
