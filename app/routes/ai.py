from fastapi import APIRouter
from typing import List, Dict, Any
from app.models import AIChatRequest, AIChatResponse
from app.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Customer Assistant"])

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(req: AIChatRequest):
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    result = ai_service.chat(req.message, history=history_dicts)
    return AIChatResponse(
        reply=result.get("reply", ""),
        suggested_products=result.get("suggested_products", []),
        suggested_promos=result.get("suggested_promos", [])
    )

@router.get("/quick-prompts")
def get_quick_prompts() -> List[Dict[str, str]]:
    return [
        {"label": "🎁 កូដបញ្ចុះតម្លៃ (Promo Codes)", "prompt": "តើមានកូដបញ្ចុះតម្លៃអ្វីខ្លះនៅថ្ងៃនេះ?"},
        {"label": "🎧 ទំនិញអេឡិចត្រូនិច (Electronics)", "prompt": "ណែនាំទំនិញអេឡិចត្រូនិក និងកាសស្ដាប់ល្បីៗ"},
        {"label": "🚚 សេវាដឹកជញ្ជូន (Delivery Info)", "prompt": "តើសេវាដឹកជញ្ជូន និងការបង់ប្រាក់យ៉ាងដូចម្តេច?"},
        {"label": "⚡ Discount Deals", "prompt": "What are the best discount products right now?"}
    ]
