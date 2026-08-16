from fastapi import APIRouter, UploadFile, HTTPException
import os
import sys
import traceback
from rag.ingestion import ingest_pdf_bytes, ingest_docx_bytes, ingest_web_sop
from rag.validation import (
    validate_sop_structure, classify_audit_document,
    extract_text_from_pdf,
)
from models.schemas import WebSopPayload, HealthOut
from db.vectorstore import get_vectorstore

router = APIRouter()


@router.post("/ingest-audit")
async def ingest_audit(file: UploadFile):
    """
    Upload an audit criteria document (PDF or DOCX).
    Validates file type, extractability, and document classification.
    """
    try:
        filename = file.filename or ""

        if not filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(400, "Only PDF and DOCX files are supported.")

        contents = await file.read()

        if len(contents) < 100:
            raise HTTPException(400, "File appears empty or unreadable.")

        # Extract text for classification
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(contents)
        else:
            import tempfile
            from langchain_community.document_loaders import Docx2txtLoader
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                f.write(contents)
                tmp = f.name
            try:
                docs = Docx2txtLoader(tmp).load()
                text = " ".join(d.page_content for d in docs)
            finally:
                os.unlink(tmp)

        if len(text.strip()) < 300:
            raise HTTPException(400, "Could not extract readable text from this file.")

        # Optional: skip LLM classification when debugging or when Anthropic
        # credentials/models are not available. Set SKIP_CLASSIFICATION=1 to
        # bypass and allow ingestion to proceed.
        skip_cls = os.getenv("SKIP_CLASSIFICATION", "0").lower() in ("1", "true")
        if not skip_cls:
            if not classify_audit_document(text):
                raise HTTPException(422,
                    "This does not appear to be an audit criteria document. "
                    "Please upload the correct file.")
        else:
            print("Skipping classification (SKIP_CLASSIFICATION=1)", file=sys.stderr)

        # Ingest
        if filename.lower().endswith(".pdf"):
            chunk_count = ingest_pdf_bytes(contents, filename)
        else:
            chunk_count = ingest_docx_bytes(contents, filename)

        return {"status": "ingested", "filename": filename, "chunks": chunk_count}
    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        raise HTTPException(500, f"Internal server error: {e}")


@router.post("/ingest-web-sop")
async def add_web_sop(payload: WebSopPayload):
    """Fetch a web page and ingest it as a SOP."""
    try:
        chunk_count = await ingest_web_sop(payload.url)
    except Exception as e:
        raise HTTPException(422, str(e))
    return {"status": "ingested", "url": payload.url, "chunks": chunk_count}


@router.get("/health", response_model=HealthOut)
def health():
    try:
        vs    = get_vectorstore()
        docs  = vs.similarity_search("test", k=1)
        count = len(docs)
    except Exception:
        count = 0
    return HealthOut(
        status      = "ok",
        model       = f"{os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620')} · all-MiniLM-L6-v2 · pgvector",
        chunk_count = count,
    )
