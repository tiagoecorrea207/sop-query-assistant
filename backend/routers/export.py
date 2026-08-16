from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from export.pdf import build_pdf
from models.schemas import ExportPayload

router = APIRouter()


@router.post("/export-pdf")
def export_pdf(payload: ExportPayload):
    """Export the accumulated output panel entries as a styled PDF."""
    try:
        pdf_bytes = build_pdf([e.model_dump() for e in payload.entries])
    except Exception as exc:
        raise HTTPException(503, f"PDF export failed: {exc}") from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=audit-session.pdf"
        },
    )
