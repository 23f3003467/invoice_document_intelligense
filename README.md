# Document Intelligence Starter

Upload a PDF → classify it → extract structured fields → flag exceptions → store it.
No frontend required — you test it through the auto-generated Swagger UI.

## Pipeline (also the order to learn it in)

1. `extraction.py` — PDF text extraction (with OCR fallback for scans)
2. `llm_service.py` — LLM classification + structured field extraction
3. `routing.py` — plain rule-based flagging (no AI)
4. `database.py` — SQLite storage
5. `main.py` — FastAPI wiring it all together

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

For OCR fallback (scanned PDFs) you also need system packages:
```bash
# Mac
brew install poppler tesseract

# Ubuntu/Debian
sudo apt install poppler-utils tesseract-ocr
```

Set your API key:
```windows
$env:OLLAMA_URL="http://localhost:11434"
$env:MODEL_NAME="llama3.2"
$env:NEXT_PUBLIC_API_BASE="http://127.0.0.1:8000"
```

## Run

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs**, expand `POST /process-document`,
click "Try it out", upload a PDF, execute. That's your whole pipeline
running end to end.

`GET /documents` shows everything you've processed so far.

## Where to take it from here

- Add per-doc-type extraction schemas instead of one generic `ExtractedFields`
  (an invoice and an ID card don't share fields — this is the natural next step)
- Add a `/documents/{id}/review` endpoint so a human can correct flagged docs
- Swap SQLite for Postgres
- Add a minimal HTML upload form (or a small React/Next.js frontend — genuinely
  optional, the whole project works without one)
- Batch endpoint: accept multiple files, process concurrently
