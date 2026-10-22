from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Product, ProductCreate, ProductUpdate
from app.sheets_db import db

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[Product])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(False, description="Filter featured products only"),
    search: Optional[str] = Query(None, description="Search query in title/description")
):
    return db.get_products(category=category, featured_only=featured, query=search)

@router.get("/categories", response_model=List[str])
def list_categories():
    products = db.get_products()
    cats = set(["All"])
    for p in products:
        if p.get("category"):
            cats.add(p["category"])
    return sorted(list(cats))

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = db.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=Product, status_code=201)
def create_product(product_in: ProductCreate):
    created = db.create_product(product_in.model_dump())
    return created

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: str, updates: ProductUpdate):
    updated = db.update_product(product_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
def delete_product(product_id: str):
    success = db.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully", "id": product_id}
