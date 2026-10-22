from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Slide, SlideCreate, SlideUpdate
from app.sheets_db import db

router = APIRouter(prefix="/slides", tags=["Banner Slides CRUD"])

@router.get("", response_model=List[Slide])
def list_slides(active_only: bool = Query(False, description="Filter only active slides")):
    return db.get_slides(active_only=active_only)

@router.post("", response_model=Slide, status_code=201)
def create_slide(slide_in: SlideCreate):
    created = db.create_slide(slide_in.model_dump())
    return created

@router.put("/{slide_id}", response_model=Slide)
def update_slide(slide_id: str, updates: SlideUpdate):
    updated = db.update_slide(slide_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Slide not found")
    return updated

@router.delete("/{slide_id}")
def delete_slide(slide_id: str):
    success = db.delete_slide(slide_id)
    if not success:
        raise HTTPException(status_code=404, detail="Slide not found")
    return {"message": "Slide deleted successfully", "id": slide_id}
