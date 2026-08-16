"""
Document validation.
Checks whether uploaded files are genuine SOPs or audit criteria documents.
"""
from pypdf import PdfReader
import tempfile
import os
from langchain_anthropic import ChatAnthropic
from fastapi import HTTPException
import anthropic
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

SOP_SIGNALS = [
    "purpose", "scope", "procedure", "responsibility",
    "sop", "standard operating", "revision", "approved",
]


def validate_sop_structure(text: str) -> bool:
    """
    Returns True if the text contains enough structural signals
    to be considered a valid SOP document.
    Requires at least 3 of 8 signals.
    """
    text_lower = text.lower()
    matches    = sum(1 for s in SOP_SIGNALS if s in text_lower)
    return matches >= 3


def classify_audit_document(text: str) -> bool:
    """
    Uses Claude to classify whether a document is audit criteria.
    Returns True if it is, False otherwise.
    """
    try:
        llm = ChatAnthropic(model=ANTHROPIC_MODEL)
        response = llm.invoke(
            f"Read the excerpt below and classify the document.\n"
            f"Respond with exactly one word: AUDIT_CRITERIA or NOT_AUDIT_CRITERIA.\n\n"
            f"Excerpt:\n{text[:2000]}"
        )
        return response.content.strip() == "AUDIT_CRITERIA"
    except anthropic.NotFoundError:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        raise HTTPException(503, f"Anthropic model not found: {ANTHROPIC_MODEL}. Set ANTHROPIC_MODEL to a valid model for your account.")
    except Exception as e:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        raise HTTPException(502, f"Anthropic request failed: {e}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF for validation."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(file_bytes)
        tmp = f.name
    try:
        reader = PdfReader(tmp)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)
    finally:
        os.unlink(tmp)
