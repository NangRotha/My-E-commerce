import os
import re
from typing import Dict, Any, List, Optional
from app.config import settings
from app.sheets_db import db

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Google GenAI Client: {e}")

    def chat(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Chat endpoint for customer replay/assistant.
        Extracts relevant products, promo codes, and generates friendly Khmer / English responses.
        """
        # Fetch current store context
        store_settings = db.get_settings()
        all_products = db.get_products()
        all_promos = [p for p in db.get_promo_codes() if p.get("is_active")]
        
        # Prepare matching products based on user query
        matched_products = self._find_matching_products(user_message, all_products)
        matched_promos = self._find_relevant_promos(user_message, all_promos)

        # Try Gemini API if client is available
        if self.client:
            try:
                system_instruction = self._build_system_instruction(store_settings, all_products, all_promos)
                # Build prompt with conversation context
                prompt = f"Customer says: \"{user_message}\"\n\nContext:\nStore Name: {store_settings.get('store_name')}\nPhone: {store_settings.get('contact_phone')}\n\nRespond to the customer politely in the same language they used (Khmer or English). Suggest relevant products and active promo codes if appropriate."
                
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": 0.7
                    }
                )
                
                if response and response.text:
                    return {
                        "reply": response.text.strip(),
                        "suggested_products": matched_products[:3],
                        "suggested_promos": [p["code"] for p in matched_promos[:2]]
                    }
            except Exception as e:
                print(f"Gemini API error, falling back to smart reply engine: {e}")

        # Intelligent Fallback Engine (Khmer & English smart matching)
        return self._smart_rule_reply(user_message, store_settings, all_products, all_promos, matched_products, matched_promos)

    def _find_matching_products(self, query: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        q = query.lower()
        matched = []
        for p in products:
            title = p.get("title", "").lower()
            cat = p.get("category", "").lower()
            desc = p.get("description", "").lower()
            # check common terms
            terms = [w for w in re.split(r"\s+", q) if len(w) > 2]
            score = 0
            for t in terms:
                if t in title:
                    score += 3
                if t in cat:
                    score += 2
                if t in desc:
                    score += 1
            if score > 0:
                matched.append((score, p))
                
        matched.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched]

    def _find_relevant_promos(self, query: str, promos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        q = query.lower()
        promo_words = ["discount", "promo", "promocode", "coupon", "code", "បញ្ចុះតម្លៃ", "ប្រូម៉ូសិន", "កូដ", "ចុះថ្លៃ"]
        if any(w in q for w in promo_words):
            return promos
        return promos[:2]

    def _build_system_instruction(self, store_settings: Dict[str, Any], products: List[Dict[str, Any]], promos: List[Dict[str, Any]]) -> str:
        prods_summary = "\n".join([
            f"- {p['title']} (Category: {p.get('category')}, Price: ${p.get('price')}, Sale: ${p.get('discount_price') or 'None'}, Stock: {p.get('stock')})"
            for p in products[:15]
        ])
        promos_summary = "\n".join([
            f"- Code: {pr['code']}, Discount: {pr['discount_value']}{'%' if pr['discount_type'] == 'percentage' else '$'}, Min Order: ${pr['min_order']}"
            for pr in promos
        ])
        
        return f"""You are the friendly and professional AI Shopping Assistant for '{store_settings.get('store_name', 'Our Store')}'.
You help customers instantly replay to their questions, find products, explain discounts and promo codes, and provide delivery or payment info.

Store Information:
- Phone: {store_settings.get('contact_phone')}
- Email: {store_settings.get('contact_email')}
- Announcement: {store_settings.get('announcement')}

Available Active Products:
{prods_summary}

Active Promo Codes:
{promos_summary}

Instructions:
1. Always be polite, helpful, and welcoming.
2. If customer asks in Khmer, reply in natural, polite Khmer (អរគុណ, សូមជម្រាបជូន, ...).
3. If customer asks in English, reply in friendly English.
4. If customer asks about discounts or promo codes, mention the code clearly so they can use it at checkout!
5. If customer asks for product recommendations, recommend 1 to 3 items from our catalog with prices.
6. Keep replies concise and easy to read on mobile.
"""

    def _smart_rule_reply(self, message: str, store_settings: Dict[str, Any], products: List[Dict[str, Any]], promos: List[Dict[str, Any]], matched_products: List[Dict[str, Any]], matched_promos: List[Dict[str, Any]]) -> Dict[str, Any]:
        msg = message.lower().strip()
        store_name = store_settings.get("store_name", "E-Store")
        phone = store_settings.get("contact_phone", "+855 12 345 678")

        # 1. Check for Promocodes / Discounts query (Khmer & English)
        promo_keywords = ["promo", "discount", "code", "coupon", "voucher", "បញ្ចុះតម្លៃ", "ចុះថ្លៃ", "ប្រូម៉ូសិន", "កូដ"]
        if any(k in msg for k in promo_keywords):
            if promos:
                promo_list_kh = "\n".join([f"✨ កូដ '{p['code']}' បញ្ចុះតម្លៃ {p['discount_value']}{'%' if p['discount_type'] == 'percentage' else '$'} (សម្រាប់ការទិញចាប់ពី ${p['min_order']})" for p in promos])
                promo_list_en = "\n".join([f"✨ Code '{p['code']}': {p['discount_value']}{'%' if p['discount_type'] == 'percentage' else '$'} OFF (Min order ${p['min_order']})" for p in promos])
                
                is_khmer = any(ord(c) >= 0x1780 and ord(c) <= 0x17FF for c in message)
                if is_khmer:
                    reply = f"សួស្តីបាទ/ចាស! ហាង {store_name} យើងខ្ញុំមានប្រូម៉ូសិនពិសេសដូចខាងក្រោម៖\n\n{promo_list_kh}\n\nលោកអ្នកអាចយកកូដនេះទៅបំពេញនៅទំព័រ Cart/Checkout ដើម្បីទទួលបានការបញ្ចុះតម្លៃភ្លាមៗ!"
                else:
                    reply = f"Hello! Here are the active promo codes available at {store_name}:\n\n{promo_list_en}\n\nSimply apply these codes at the Cart/Checkout page to get your instant discount!"
            else:
                reply = f"Currently all our products already feature best direct discounts! Feel free to check our catalog."
                
            return {
                "reply": reply,
                "suggested_products": [p for p in products if p.get("discount_price")][:3],
                "suggested_promos": [p["code"] for p in promos]
            }

        # 2. Check for Specific Product Search
        if matched_products:
            p = matched_products[0]
            price_str = f"${p.get('discount_price')}" if p.get('discount_price') else f"${p.get('price')}"
            is_khmer = any(ord(c) >= 0x1780 and ord(c) <= 0x17FF for c in message)
            if is_khmer:
                reply = f"បាទ/ចាស! សម្រាប់ទំនិញ '{p.get('title')}' យើងមានក្នុងស្តុកស្រាប់ តម្លៃពិសេសត្រឹមតែ {price_str}។ លោកអ្នកអាចចុចមើលព័ត៌មានលម្អិត រូបភាព និងវីដេអូបានខាងក្រោមបាទ/ចាស!"
            else:
                reply = f"Yes! We have '{p.get('title')}' available in stock for only {price_str}. You can view the full details, multiple gallery photos and video preview below!"
            return {
                "reply": reply,
                "suggested_products": matched_products[:3],
                "suggested_promos": [pr["code"] for pr in promos[:1]]
            }

        # 3. Check for Delivery / Shipping / Payment queries
        delivery_keywords = ["delivery", "ship", "shipping", "fee", "payment", "aba", "bakong", "ដឹក", "ថ្លៃដឹក", "ផ្ញើ", "បង់ប្រាក់", "ទូទាត់"]
        if any(k in msg for k in delivery_keywords):
            is_khmer = any(ord(c) >= 0x1780 and ord(c) <= 0x17FF for c in message)
            if is_khmer:
                reply = f"សេវាដឹកជញ្ជូន និងការទូទាត់ប្រាក់៖\n🚚 សេវាដឹកជញ្ជូនរហ័សទូទាំងប្រទេសកម្ពុជា (ភ្នំពេញ ១-២ ម៉ោង ឬ ២៤ ម៉ោងតាមខេត្ត)\n💳 ទទួលទូទាត់តាមរយៈ ABA PAY, Bakong KHQR និងទូទាត់ពេលទំនិញដល់ដៃ (Cash on Delivery)។"
            else:
                reply = f"Shipping & Payment Information:\n🚚 Fast delivery across Cambodia (1-2 hours in Phnom Penh, 24-48 hours nationwide).\n💳 We accept ABA PAY, Bakong KHQR, and Cash on Delivery (COD)!"
            return {
                "reply": reply,
                "suggested_products": products[:2],
                "suggested_promos": [p["code"] for p in promos[:1]]
            }

        # 4. Check for Contact / Location
        contact_keywords = ["contact", "phone", "address", "location", "call", "លេខ", "ទាក់ទង", "ទីតាំង", "ហាងនៅឯណា"]
        if any(k in msg for k in contact_keywords):
            is_khmer = any(ord(c) >= 0x1780 and ord(c) <= 0x17FF for c in message)
            if is_khmer:
                reply = f"ព័ត៌មានទំនាក់ទំនងហាង {store_name}៖\n📞 លេខទូរស័ព្ទ៖ {phone}\n📧 អ៊ីមែល៖ {store_settings.get('contact_email')}\nលោកអ្នកអាចទាក់ទងមកក្រុមការងារយើងខ្ញុំបានគ្រប់ពេលវេលា!"
            else:
                reply = f"Contact Details for {store_name}:\n📞 Phone: {phone}\n📧 Email: {store_settings.get('contact_email')}\nOur support team is ready to assist you!"
            return {
                "reply": reply,
                "suggested_products": [],
                "suggested_promos": []
            }

        # 5. Default Greeting / General assistance
        is_khmer = any(ord(c) >= 0x1780 and ord(c) <= 0x17FF for c in message)
        if is_khmer:
            reply = f"សួស្តីបាទ/ចាស! ខ្ញុំជាជំនួយការឆ្លាតវៃ AI ប្រចាំហាង {store_name}។ ខ្ញុំអាចជួយលោកអ្នកស្វែងរកទំនិញ ណែនាំផលិតផលល្អៗ ផ្តល់កូដបញ្ចុះតម្លៃ និងឆ្លើយតបព័ត៌មានផ្សេងៗបាន។ តើខ្ញុំអាចជួយអ្វីលោកអ្នកនៅថ្ងៃនេះ?"
        else:
            reply = f"Hello! I am the AI Shopping Assistant for {store_name}. I can help you discover exciting products, find discounts & promo codes, and check delivery options. How can I assist you today?"

        return {
            "reply": reply,
            "suggested_products": products[:3],
            "suggested_promos": [p["code"] for p in promos[:2]]
        }

ai_service = AIService()
