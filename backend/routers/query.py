"""
WebSocket /query endpoint.

Protocol:
  Client → Server: { "question": "...", "web_sop_urls": [...] }
  Server → Client: { "type": "token",   "value": "..." }        (streaming)
                   { "type": "done",    "answer": "...",
                     "sources": [...],  "response_type": "...",
                     "web_errors": [...] }
                   { "type": "error",   "value": "..." }
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from rag.chain import run_query
from rag.ingestion import ingest_web_sop
from db.models import SessionLocal, QueryLog

router = APIRouter()


@router.websocket("/query")
async def query_ws(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            raw  = await websocket.receive_text()
            data = json.loads(raw)

            question     = data.get("question", "").strip()
            web_sop_urls = data.get("web_sop_urls", [])

            if not question:
                await websocket.send_json({
                    "type": "error", "value": "question is required"
                })
                continue

            # Fetch any web SOPs — failures are non-fatal
            web_errors = []
            for url in web_sop_urls:
                try:
                    await ingest_web_sop(url)
                except Exception as e:
                    web_errors.append(str(e))

            # Run RAG pipeline in thread pool (synchronous chain)
            loop   = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: run_query(question)
            )

            # Persist to query log
            db.add(QueryLog(
                question      = question,
                answer        = result["answer"],
                response_type = result["type"],
                sources       = result["sources"],
            ))
            db.commit()

            # Send result
            await websocket.send_json({
                "type":          "done",
                "answer":        result["answer"],
                "sources":       result["sources"],
                "response_type": result["type"],
                "web_errors":    web_errors,
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "value": str(e)})
        except Exception:
            pass
    finally:
        db.close()
