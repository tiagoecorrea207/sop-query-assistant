"""
Document ingestion pipeline.
Handles .docx SOPs, uploaded audit criteria PDFs, and web SOPs.
"""
import os
import tempfile
import httpx
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from pypdf import PdfReader
from langchain.schema import Document
from db.vectorstore import store
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " "],
)


def ingest_pdf_bytes(file_bytes: bytes, filename: str) -> int:
    """Ingest an uploaded PDF (audit criteria)."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(file_bytes)
        tmp = f.name
    try:
        reader = PdfReader(tmp)
        text_pages = [p.extract_text() or "" for p in reader.pages]
        full_text = "\n".join(text_pages)
        doc = Document(page_content=full_text, metadata={"source": filename, "doc_type": "audit_criteria"})
        chunks = splitter.split_documents([doc])
        for i, c in enumerate(chunks):
            c.metadata.update({
                "source":    filename,
                "doc_type":  "audit_criteria",
                "chunk_idx": i,
            })
        return store(chunks)
    finally:
        os.unlink(tmp)


def ingest_docx_bytes(file_bytes: bytes, filename: str) -> int:
    """Ingest an uploaded DOCX (audit criteria)."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(file_bytes)
        tmp = f.name
    try:
        loader = Docx2txtLoader(tmp)
        docs   = loader.load()
        chunks = splitter.split_documents(docs)
        for i, c in enumerate(chunks):
            c.metadata.update({
                "source":    filename,
                "doc_type":  "audit_criteria",
                "chunk_idx": i,
            })
        return store(chunks)
    finally:
        os.unlink(tmp)


async def ingest_web_sop(url: str) -> int:
    """Fetch a web page and ingest its text content as a SOP."""
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        r.raise_for_status()

    text = BeautifulSoup(r.text, "html.parser").get_text(separator="\n").strip()
    if len(text) < 200:
        raise ValueError(f"URL returned no usable content: {url}")

    doc    = Document(
        page_content=text,
        metadata={"source": url, "doc_type": "web"}
    )
    chunks = splitter.split_documents([doc])
    for i, c in enumerate(chunks):
        c.metadata["chunk_idx"] = i
    return store(chunks)
