"""
Step 6: The API.
One endpoint that runs the full pipeline end to end:
  upload -> extract text -> classify -> extract fields -> flag -> store

Run it with:
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs for the built-in test UI —
no frontend needed to prove this works.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException

from extraction import extract_text
from llm_service import classify_document, extract_fields, LLMProcessingError
from routing import evaluate_flags
from models import ProcessedDocument
from database import init_db, save_document, list_documents

app = FastAPI(title="Document Intelligence Starter")


@app.on_event("startup")
def startup():
    init_db()


@app.post("/process-document", response_model=ProcessedDocument)
async def process_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported in this starter.")

    file_bytes = await file.read()
    text = extract_text(file_bytes)
    if not text.strip():
        raise HTTPException(422, "Could not extract any text from this document.")

    try:
        classification = classify_document(text)
        fields = extract_fields(text, classification.doc_type)
    except LLMProcessingError as e:
        # Clean 502 instead of a raw traceback when the model output
        # can't be parsed/validated even after the built-in retry.
        raise HTTPException(502, f"AI processing failed: {e}")

    flagged, flag_reason = evaluate_flags(classification, fields)

    doc = ProcessedDocument(
        filename=file.filename,
        classification=classification,
        fields=fields,
        flagged=flagged,
        flag_reason=flag_reason,
    )
    doc.id = save_document(doc)
    return doc


@app.get("/documents")
def get_documents():
    return list_documents()


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}