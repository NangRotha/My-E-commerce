import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.sheets_db import db

router = APIRouter(prefix="/realtime", tags=["Real-time Sync"])

@router.get("/version")
def get_realtime_version():
    """
    Ultra-lightweight endpoint for client polling to detect any database changes
    within milliseconds.
    """
    settings_data = db.get_settings()
    return {
        "version": db.version,
        "last_updated": db.last_updated,
        "is_store_active": settings_data.get("is_store_active", True),
        "store_name": settings_data.get("store_name", ""),
        "store_logo": settings_data.get("store_logo", ""),
        "announcement": settings_data.get("announcement", ""),
        "sheets_connected": db.is_connected,
        "mode": "google_sheets" if db.is_connected else "local_database"
    }

@router.get("/events")
async def stream_realtime_events(request: Request):
    """
    Server-Sent Events (SSE) stream for real-time live database updates.
    Both frontend-user and frontend-admin connect to this stream to receive
    sub-second push events when any data (products, orders, settings, promos, slides)
    is created, updated, or synced with Google Sheet.
    """
    async def event_generator():
        q = db.subscribe()
        try:
            # 1. Send initial handshake with current store state
            handshake = {
                "version": db.version,
                "event": "connected",
                "timestamp": db.last_updated,
                "data": {
                    "is_store_active": db.get_settings().get("is_store_active", True),
                    "store_name": db.get_settings().get("store_name", ""),
                    "sheets_connected": db.is_connected
                }
            }
            yield f"data: {json.dumps(handshake)}\n\n"

            # 2. Stream subsequent real-time change events as they happen
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=12.0)
                    yield f"data: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP/SSE connection alive
                    yield ": ping\n\n"
        finally:
            db.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
