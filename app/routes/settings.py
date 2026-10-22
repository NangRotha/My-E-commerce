from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from typing import Dict, Any
from app.models import StoreSettings, StoreSettingsUpdate, ToggleStoreRequest
from app.sheets_db import db

router = APIRouter(prefix="/settings", tags=["Store Settings & Customization"])

@router.get("", response_model=StoreSettings)
def get_store_settings():
    return db.get_settings()

@router.put("", response_model=StoreSettings)
def update_store_settings(updates: StoreSettingsUpdate):
    updated = db.update_settings(updates.model_dump(exclude_unset=True))
    return updated

@router.post("/toggle-store")
def toggle_store(req: ToggleStoreRequest):
    """
    Toggle frontend-user online/offline (Maintenance mode).
    When is_store_active is false, frontend-user shows maintenance / closed page.
    """
    new_status = db.toggle_store_status(req.is_store_active)
    return {
        "success": True,
        "is_store_active": new_status,
        "message": "Store is now Online" if new_status else "Store is now Closed (Maintenance Mode)"
    }

@router.get("/sheets-status")
def get_sheets_status():
    """Return status of Google Sheet connection and sync"""
    return db.get_status()

@router.post("/connect-sheets")
def connect_sheets(payload: Dict[str, Any] = Body(...)):
    spreadsheet_id = payload.get("spreadsheet_id")
    if not spreadsheet_id:
        raise HTTPException(status_code=400, detail="Spreadsheet ID or URL is required")
        
    connected = db.try_connect_sheets(spreadsheet_id=spreadsheet_id)
    return {
        "success": connected,
        "status": db.get_status()
    }

@router.post("/upload-credentials")
def upload_credentials(payload: Dict[str, Any] = Body(...)):
    """Save service account JSON string pasted by the admin"""
    credentials_json = payload.get("credentials_json")
    if not credentials_json:
        raise HTTPException(status_code=400, detail="credentials_json is required")
    res = db.save_service_account_credentials(credentials_json)
    return res

@router.post("/upload-credentials-file")
async def upload_credentials_file(file: UploadFile = File(...)):
    """Upload service_account.json file directly"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        res = db.save_service_account_credentials(text)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

@router.post("/export-to-sheets")
def export_to_sheets():
    """Push all current products, promocodes, slides, and settings into Google Sheet"""
    return db.export_all_to_google_sheet()

@router.post("/sync-now")
def sync_now():
    """Force an instant re-sync from Google Sheet"""
    db._sync_sheets_to_local(force=True)
    return {
        "success": True,
        "status": db.get_status(),
        "message": "Google Sheet synchronization complete!"
    }

