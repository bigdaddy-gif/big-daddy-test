from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(title="ClawBot Setup Pro API")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(api_router)
