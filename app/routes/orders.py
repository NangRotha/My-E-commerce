from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Order, OrderCreate, OrderStatusUpdate
from app.sheets_db import db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=List[Order])
def list_orders():
    return db.get_orders()

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str):
    order = db.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("", response_model=Order, status_code=201)
def create_order(order_in: OrderCreate):
    created = db.create_order(order_in.model_dump())
    return created

@router.put("/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, body: OrderStatusUpdate):
    updated = db.update_order_status(order_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated
