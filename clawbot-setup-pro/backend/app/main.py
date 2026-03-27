from fastapi import FastAPI

app = FastAPI(title="ClawBot Setup Pro API")

@app.get("/health")
def health():
    return {"ok": True}
