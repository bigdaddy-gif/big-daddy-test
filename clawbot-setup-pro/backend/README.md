# Backend (FastAPI)

## Run (dev)
```bash
python3 -m venv .venv  # may require python3-venv on Debian/Ubuntu
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health: `GET /health`
