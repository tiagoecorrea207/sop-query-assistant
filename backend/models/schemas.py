from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditEntryOut(BaseModel):
    question:      str
    answer:        str
    sources:       list[str]
    response_type: str
    timestamp:     str


class ExportPayload(BaseModel):
    entries: list[AuditEntryOut]


class WebSopPayload(BaseModel):
    url: str


class HealthOut(BaseModel):
    status:      str
    model:       str
    chunk_count: int
