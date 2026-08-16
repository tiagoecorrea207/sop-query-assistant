from fastapi import FastAPI  # type: ignore[import]
import os

from starlette.middleware.cors import CORSMiddleware

from db.models import init_db
from db.seed import seed
from routers import query, ingest, export

app = FastAPI(
    title       = "Pharmaceutical SOP Query Assistant",
    description = "RAG-powered Q&A over pharmaceutical SOPs and audit criteria.",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(export.router)


@app.on_event("startup")
async def startup():
    init_db()
    if os.getenv("SKIP_SEED", "0").lower() not in ("1", "true"):
        seed()
