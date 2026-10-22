from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== PRODUCT MODELS ====================
class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, description="Product title / name")
    description: str = Field("", description="Detailed product description")
    price: float = Field(..., ge=0, description="Original price")
    discount_price: Optional[float] = Field(None, ge=0, description="Discounted sale price if any")
    category: str = Field("General", description="Product category")
    stock: int = Field(10, ge=0, description="Available stock quantity")
    images: List[str] = Field(default_factory=list, description="List of image URLs or file paths")
    videos: List[str] = Field(default_factory=list, description="List of video URLs or file paths")
    is_featured: bool = Field(False, description="Whether to show in featured section")
    badge: Optional[str] = Field(None, description="Badge tag e.g. New, Best Seller, Sale")
    rating: float = Field(5.0, description="Rating from 1.0 to 5.0")
    review_count: int = Field(128, description="Number of customer reviews")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    badge: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

class Product(ProductBase):
    id: str
    created_at: str


# ==================== PROMO CODE MODELS ====================
class PromoCodeBase(BaseModel):
    code: str = Field(..., min_length=2, description="Promo coupon code e.g. SAVE20")
    discount_type: Literal["percentage", "fixed"] = Field("percentage", description="Discount type")
    discount_value: float = Field(..., gt=0, description="Percentage (e.g. 20) or fixed amount ($)")
    min_order: float = Field(0.0, ge=0, description="Minimum order amount required to use code")
    expiry_date: Optional[str] = Field(None, description="Expiry date string YYYY-MM-DD")
    usage_limit: Optional[int] = Field(None, ge=1, description="Maximum total uses allowed")
    is_active: bool = Field(True, description="Whether promo code is active")

class PromoCodeCreate(PromoCodeBase):
    pass

class PromoCodeUpdate(BaseModel):
    code: Optional[str] = None
    discount_type: Optional[Literal["percentage", "fixed"]] = None
    discount_value: Optional[float] = None
    min_order: Optional[float] = None
    expiry_date: Optional[str] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None

class PromoCode(PromoCodeBase):
    id: str
    used_count: int = 0
    created_at: str

class PromoValidateRequest(BaseModel):
    code: str
    cart_total: float

class PromoValidateResponse(BaseModel):
    is_valid: bool
    message: str
    discount_amount: float = 0.0
    final_total: float = 0.0
    promo_code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None

# ==================== STORE SETTINGS MODELS ====================
class StoreSettings(BaseModel):
    store_name: str = Field("E-Khmer Mart", description="Store name")
    store_logo: str = Field("https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=150&auto=format&fit=crop&q=80", description="Logo URL or path")
    is_store_active: bool = Field(True, description="Master toggle for Frontend User store (open/close)")
    contact_phone: str = Field("+855 12 888 999", description="Store contact phone")
    contact_email: str = Field("contact@ekhmermart.com", description="Store contact email")
    announcement: str = Field("🎉 Welcome! Get 15% OFF your first order with code WELCOME15!", description="Top announcement banner")

class StoreSettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    store_logo: Optional[str] = None
    is_store_active: Optional[bool] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    announcement: Optional[str] = None

class ToggleStoreRequest(BaseModel):
    is_store_active: bool

# ==================== BANNER SLIDE MODELS ====================
class SlideBase(BaseModel):
    title: str = Field(..., description="Slide headline")
    subtitle: str = Field("", description="Slide description or subtext")
    image_url: str = Field(..., description="Banner background or hero image URL")
    link_url: str = Field("/products", description="Link destination")
    button_text: str = Field("Shop Now", description="Button text")
    is_active: bool = Field(True, description="Whether slide is displayed")
    display_order: int = Field(1, description="Order sequence")

class SlideCreate(SlideBase):
    pass

class SlideUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    button_text: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class Slide(SlideBase):
    id: str
    created_at: str

# ==================== ORDER MODELS ====================
class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int
    image: Optional[str] = None

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_phone: str = Field(..., min_length=6)
    customer_address: str = Field(..., min_length=4)
    items: List[OrderItem] = Field(..., min_items=1)
    promo_code: Optional[str] = None
    notes: Optional[str] = None

class Order(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_address: str
    items: List[OrderItem]
    total_amount: float
    discount_amount: float
    final_amount: float
    promo_code: Optional[str] = None
    status: str = "pending" # pending, confirmed, processing, shipped, delivered, cancelled
    notes: Optional[str] = None
    created_at: str

class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]

# ==================== AI CHAT MODELS ====================
class AIChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class AIChatRequest(BaseModel):
    message: str
    history: List[AIChatMessage] = Field(default_factory=list)

class AIChatResponse(BaseModel):
    reply: str
    suggested_products: List[Product] = Field(default_factory=list)
    suggested_promos: List[str] = Field(default_factory=list)
