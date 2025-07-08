from fastapi import FastAPI
from src.core.settings import settings

app = FastAPI(
    title="AltMur Backend",
    description="Backend for AltMur, a social media platform.",
    version="0.1.0",
)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}