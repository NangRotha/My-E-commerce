from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.models import (
    PromoCode, PromoCodeCreate, PromoCodeUpdate,
    PromoValidateRequest, PromoValidateResponse
)
from app.sheets_db import db

router = APIRouter(prefix="/promo-codes", tags=["Promo Codes & Discounts"])

@router.get("", response_model=List[PromoCode])
def list_promo_codes():
    return db.get_promo_codes()

@router.post("", response_model=PromoCode, status_code=201)
def create_promo_code(promo_in: PromoCodeCreate):
    existing = db.get_promo_by_code(promo_in.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"Promo code '{promo_in.code}' already exists")
    created = db.create_promo_code(promo_in.model_dump())
    return created

@router.put("/{promo_id}", response_model=PromoCode)
def update_promo_code(promo_id: str, updates: PromoCodeUpdate):
    updated = db.update_promo_code(promo_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Promo code not found")
    return updated

@router.delete("/{promo_id}")
def delete_promo_code(promo_id: str):
    success = db.delete_promo_code(promo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Promo code not found")
    return {"message": "Promo code deleted successfully", "id": promo_id}

@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo_code(req: PromoValidateRequest):
    code = req.code.strip().upper()
    cart_total = float(req.cart_total)
    
    promo = db.get_promo_by_code(code)
    if not promo:
        return PromoValidateResponse(
            is_valid=False,
            message="Invalid promo code. Please check and try again.",
            discount_amount=0.0,
            final_total=cart_total
        )
        
    if not promo.get("is_active"):
        return PromoValidateResponse(
            is_valid=False,
            message="This promo code is currently inactive.",
            discount_amount=0.0,
            final_total=cart_total
        )

    # Check expiry
    expiry = promo.get("expiry_date")
    if expiry:
        try:
            exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            if datetime.now().date() > exp_date:
                return PromoValidateResponse(
                    is_valid=False,
                    message=f"This promo code expired on {expiry}.",
                    discount_amount=0.0,
                    final_total=cart_total
                )
        except Exception:
            pass

    # Check usage limit
    usage_limit = promo.get("usage_limit")
    used_count = promo.get("used_count", 0)
    if usage_limit is not None and used_count >= usage_limit:
        return PromoValidateResponse(
            is_valid=False,
            message="This promo code has reached its maximum usage limit.",
            discount_amount=0.0,
            final_total=cart_total
        )

    # Check minimum order
    min_order = promo.get("min_order", 0.0)
    if cart_total < min_order:
        return PromoValidateResponse(
            is_valid=False,
            message=f"Minimum order of ${min_order:.2f} required to use code {code}.",
            discount_amount=0.0,
            final_total=cart_total
        )

    # Calculate discount
    discount_val = promo.get("discount_value", 0.0)
    discount_type = promo.get("discount_type", "percentage")
    if discount_type == "percentage":
        discount_amount = round(cart_total * (discount_val / 100.0), 2)
    else:
        discount_amount = min(cart_total, discount_val)
        
    final_total = max(0.0, round(cart_total - discount_amount, 2))

    return PromoValidateResponse(
        is_valid=True,
        message=f"Promo code '{code}' applied! Saved ${discount_amount:.2f}",
        discount_amount=discount_amount,
        final_total=final_total,
        promo_code=code,
        discount_type=discount_type,
        discount_value=discount_val
    )
