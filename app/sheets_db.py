import json
import uuid
import os
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from app.config import settings

# Sheet Column Definitions
PRODUCTS_HEADERS = ["id", "title", "description", "price", "discount_price", "category", "stock", "images", "videos", "is_featured", "badge", "rating", "review_count", "created_at"]
PROMO_HEADERS = ["id", "code", "discount_type", "discount_value", "min_order", "expiry_date", "usage_limit", "used_count", "is_active", "created_at"]
SETTINGS_HEADERS = ["key", "value"]
SLIDES_HEADERS = ["id", "title", "subtitle", "image_url", "link_url", "button_text", "is_active", "display_order", "created_at"]
ORDERS_HEADERS = ["id", "customer_name", "customer_phone", "customer_address", "items_json", "total_amount", "discount_amount", "final_amount", "promo_code", "status", "notes", "created_at"]

DEFAULT_SEED_DATA = {
    "settings": {
        "store_name": "CRESCENDO",
        "store_logo": "https://images.unsplash.com/photo-1545127398-14699f92334b?w=200&auto=format&fit=crop&q=80",
        "is_store_active": True,
        "contact_phone": "+855 12 888 999",
        "contact_email": "hello@crescendo-audio.com",
        "announcement": "🔥 Special Audio Deals: Use code 'CRESCENDO30' for 30% OFF on all premium audio gear!"
    },
    "slides": [
        {
            "id": "slide-1",
            "title": "Feel the Sound. Live the Moment.",
            "subtitle": "Premium audio gear designed for those who love pure sound and modern style.",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1600&auto=format&fit=crop&q=80",
            "link_url": "/products",
            "button_text": "Shop Now",
            "is_active": True,
            "display_order": 1,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "slide-2",
            "title": "Unrivaled Acoustic Precision",
            "subtitle": "Studio-grade sound reproduction with adaptive active noise cancellation.",
            "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=1600&auto=format&fit=crop&q=80",
            "link_url": "/products?category=Headphones",
            "button_text": "Explore Headphones",
            "is_active": True,
            "display_order": 2,
            "created_at": datetime.now().isoformat()
        }
    ],
    "promo_codes": [
        {
            "id": "promo-1",
            "code": "CRESCENDO30",
            "discount_type": "percentage",
            "discount_value": 30.0,
            "min_order": 20.0,
            "expiry_date": "2026-12-31",
            "usage_limit": 500,
            "used_count": 18,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "promo-2",
            "code": "WELCOME10",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order": 10.0,
            "expiry_date": "2026-12-31",
            "usage_limit": 1000,
            "used_count": 45,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "promo-3",
            "code": "SAVE15USD",
            "discount_type": "fixed",
            "discount_value": 15.0,
            "min_order": 50.0,
            "expiry_date": "2026-12-31",
            "usage_limit": 200,
            "used_count": 12,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ],
    "products": [
        {
            "id": "prod-1",
            "title": "Earbud Y168A",
            "description": "True wireless stereo earbuds with active noise cancellation, deep acoustic punch, touch controls, and compact wireless charging case.",
            "price": 270.0,
            "discount_price": None,
            "category": "Earbuds",
            "stock": 42,
            "images": [
                "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [
                "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
            ],
            "is_featured": True,
            "badge": "New",
            "rating": 5.0,
            "review_count": 128,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "prod-2",
            "title": "Pro X168A",
            "description": "High-definition over-ear studio headphones with spatial audio, breathable memory foam cushions, RGB illumination and dual noise-isolating mics.",
            "price": 250.0,
            "discount_price": None,
            "category": "Headphones",
            "stock": 35,
            "images": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [
                "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
            ],
            "is_featured": True,
            "badge": "Best Seller",
            "rating": 5.0,
            "review_count": 96,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "prod-3",
            "title": "Speaker P168A",
            "description": "360-degree portable omnidirectional speaker with ambient RGB halo ring, IPX7 waterproof rating, rich bass and 24-hour battery life.",
            "price": 240.0,
            "discount_price": None,
            "category": "Speakers",
            "stock": 28,
            "images": [
                "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [],
            "is_featured": True,
            "badge": "Sale",
            "rating": 5.0,
            "review_count": 74,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "prod-4",
            "title": "Fast GaN Power Adapter 65W",
            "description": "Ultra-compact Gallium Nitride 65W dual port wall charger for laptops, smartphones, and wireless earbuds with smart power distribution.",
            "price": 32.0,
            "discount_price": 28.0,
            "category": "Accessories",
            "stock": 60,
            "images": [
                "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [],
            "is_featured": True,
            "badge": "Hot",
            "rating": 4.9,
            "review_count": 64,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "prod-5",
            "title": "Wireless Charger Pad 15W",
            "description": "Sleek aluminum and tempered glass magnetic fast wireless charging pad with intelligent heat management.",
            "price": 35.0,
            "discount_price": None,
            "category": "Wireless Charger",
            "stock": 50,
            "images": [
                "https://images.unsplash.com/photo-1622445262464-84b1456045b6?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [],
            "is_featured": True,
            "badge": "New",
            "rating": 4.8,
            "review_count": 88,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "prod-6",
            "title": "Ultra Studio ANC Headphones",
            "description": "Engineered with titanium drivers, hybrid active noise cancellation, and 40 hours of playtime for true audiophiles.",
            "price": 199.0,
            "discount_price": 159.0,
            "category": "Headphones",
            "stock": 30,
            "images": [
                "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80"
            ],
            "videos": [],
            "is_featured": False,
            "badge": "Sale",
            "rating": 4.9,
            "review_count": 112,
            "created_at": datetime.now().isoformat()
        }
    ],
    "orders": [
        {
            "id": "ORD-1001",
            "customer_name": "Sophea Chan",
            "customer_phone": "012889900",
            "customer_address": "Street 271, Sangkat Boeung Tumpun, Phnom Penh",
            "items": [
                {
                    "product_id": "prod-1",
                    "title": "Sony WH-1000XM5 Wireless Headphones",
                    "price": 329.0,
                    "quantity": 1,
                    "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80"
                }
            ],
            "total_amount": 329.0,
            "discount_amount": 65.8,
            "final_amount": 263.2,
            "promo_code": "SUPER20",
            "status": "processing",
            "notes": "Please call before arrival",
            "created_at": datetime.now().isoformat()
        }
    ]
}

def extract_spreadsheet_id(input_str: str) -> str:
    """Extract clean Google Sheet ID from full URL or return direct ID"""
    if not input_str:
        return ""
    input_str = input_str.strip()
    # Check if full URL
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", input_str)
    if match:
        return match.group(1)
    return input_str

class GoogleSheetDatabase:
    def __init__(self):
        self.db_path = settings.DATA_DIR / "db.json"
        self.client = None
        self.spreadsheet = None
        self.is_connected = False
        self.connection_error = None
        self.spreadsheet_id = extract_spreadsheet_id(settings.SPREADSHEET_ID)
        self.service_account_path = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        self.service_account_email = None
        
        # Real-time caching variables (TTL in seconds to prevent 429 quota exhaustion)
        self.last_sync_time = 0
        self.SYNC_TTL = 3.0  # 3 seconds cache for real-time reads

        # Real-time Event Pub/Sub & Version tracking
        self.version = 1
        self.last_updated = time.time()
        self._subscribers = []
        
        # Initialize local storage first
        self._init_local_db()
        self._read_service_account_email()
        # Attempt connecting to Google Sheet
        self.try_connect_sheets()

    def notify_change(self, event_type: str, payload: Optional[Dict[str, Any]] = None):
        """Broadcast real-time change event to all SSE & polling subscribers"""
        self.version += 1
        self.last_updated = time.time()
        msg = {
            "version": self.version,
            "event": event_type,
            "timestamp": self.last_updated,
            "data": payload or {}
        }
        dead = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(msg)
            except Exception:
                dead.append(q)
        for d in dead:
            if d in self._subscribers:
                self._subscribers.remove(d)

    def subscribe(self):
        """Register an async queue subscriber for real-time SSE stream"""
        import asyncio
        q = asyncio.Queue(maxsize=100)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q):
        """Remove subscriber queue"""
        if q in self._subscribers:
            self._subscribers.remove(q)


    def _read_service_account_email(self):
        """Extract client_email from env var or service_account.json if present"""
        raw_env_cred = settings.GOOGLE_SERVICE_ACCOUNT_JSON or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        if raw_env_cred:
            try:
                import base64
                cred_str = raw_env_cred.strip()
                if not cred_str.startswith("{"):
                    try:
                        cred_str = base64.b64decode(cred_str).decode("utf-8")
                    except Exception:
                        pass
                cred = json.loads(cred_str)
                self.service_account_email = cred.get("client_email")
                return
            except Exception:
                pass

        for candidate in [
            Path(self.service_account_path),
            settings.DATA_DIR / "service_account.json",
            settings.BASE_DIR / "service_account.json",
            settings.BASE_DIR.parent / "service_account.json"
        ]:
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        cred = json.load(f)
                        self.service_account_email = cred.get("client_email")
                        self.service_account_path = str(candidate)
                        return
                except Exception:
                    pass

    def _init_local_db(self):
        """Initialize local JSON cache with seed or bundled data if not present"""
        if not self.db_path.exists():
            # Check if pre-bundled db.json exists in project data directory
            bundled = settings.BASE_DIR / "data" / "db.json"
            if bundled.exists() and bundled != self.db_path:
                try:
                    with open(bundled, "r", encoding="utf-8") as bf:
                        data = json.load(bf)
                    with open(self.db_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return
                except Exception:
                    pass
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SEED_DATA, f, indent=2, ensure_ascii=False)
        else:
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k in ["settings", "slides", "promo_codes", "products", "orders"]:
                        if k not in data:
                            data[k] = DEFAULT_SEED_DATA[k]
                    with open(self.db_path, "w", encoding="utf-8") as f2:
                        json.dump(data, f2, indent=2, ensure_ascii=False)
            except Exception:
                with open(self.db_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_SEED_DATA, f, indent=2, ensure_ascii=False)

    def _load_local_data(self) -> Dict[str, Any]:
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SEED_DATA.copy()

    def _save_local_data(self, data: Dict[str, Any]):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_service_account_credentials(self, json_content: str) -> Dict[str, Any]:
        """Save raw JSON credentials to service_account.json and test connection"""
        try:
            cred_dict = json.loads(json_content) if isinstance(json_content, str) else json_content
            if "client_email" not in cred_dict or "private_key" not in cred_dict:
                return {"success": False, "error": "Invalid Google Service Account JSON (missing client_email or private_key)"}
            
            # Fix escaped newlines if needed
            if isinstance(cred_dict.get("private_key"), str) and "\\n" in cred_dict["private_key"]:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

            target_file = settings.BASE_DIR / "service_account.json"
            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump(cred_dict, f, indent=2)
            except (OSError, PermissionError):
                # Fallback to writable DATA_DIR (for serverless environments)
                target_file = settings.DATA_DIR / "service_account.json"
                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump(cred_dict, f, indent=2)
                
            self.service_account_path = str(target_file)
            self.service_account_email = cred_dict.get("client_email")
            
            # If spreadsheet ID is already configured, attempt connection
            if self.spreadsheet_id:
                self.try_connect_sheets(self.spreadsheet_id)
                
            return {
                "success": True,
                "client_email": self.service_account_email,
                "message": f"Service account saved! Please make sure to share your Google Sheet with '{self.service_account_email}' as Editor."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to save service account: {str(e)}"}

    def try_connect_sheets(self, spreadsheet_id: Optional[str] = None, service_account_file: Optional[str] = None) -> bool:
        """Attempt to authenticate and open Google Sheet with gspread"""
        raw_id = spreadsheet_id or self.spreadsheet_id or os.getenv("SPREADSHEET_ID", "")
        target_sheet_id = extract_spreadsheet_id(raw_id)

        if not target_sheet_id:
            self.is_connected = False
            self.connection_error = "Missing Google Spreadsheet ID. Please enter your Google Sheet ID or URL."
            return False

        import gspread

        # 1. First check if raw credentials are provided via environment variable (Perfect for Vercel)
        raw_env_cred = settings.GOOGLE_SERVICE_ACCOUNT_JSON or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        if raw_env_cred:
            try:
                import base64
                cred_str = raw_env_cred.strip()
                if not cred_str.startswith("{"):
                    try:
                        cred_str = base64.b64decode(cred_str).decode("utf-8")
                    except Exception:
                        pass
                cred_dict = json.loads(cred_str)
                if isinstance(cred_dict.get("private_key"), str) and "\\n" in cred_dict["private_key"]:
                    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                self.client = gspread.service_account_from_dict(cred_dict)
                self.service_account_email = cred_dict.get("client_email")
                self.spreadsheet = self.client.open_by_key(target_sheet_id)
                self.spreadsheet_id = target_sheet_id
                self.is_connected = True
                self.connection_error = None
                self._ensure_sheets_exist()
                self._sync_sheets_to_local(force=True)
                return True
            except Exception as e:
                print(f"Notice: Attempt with GOOGLE_SERVICE_ACCOUNT_JSON failed: {e}")

        # 2. Locate service account file
        target_account_file = service_account_file or self.service_account_path or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
        if not Path(target_account_file).exists():
            for alt in [
                settings.DATA_DIR / "service_account.json",
                settings.BASE_DIR / "service_account.json",
                settings.BASE_DIR.parent / "service_account.json"
            ]:
                if alt.exists():
                    target_account_file = str(alt)
                    self.service_account_path = str(alt)
                    break

        if not Path(target_account_file).exists():
            self.is_connected = False
            self.connection_error = f"Service account credentials not found. Please upload or paste your service_account.json, or configure GOOGLE_SERVICE_ACCOUNT_JSON environment variable."
            return False

        try:
            self.client = gspread.service_account(filename=target_account_file)
            self.spreadsheet = self.client.open_by_key(target_sheet_id)
            self.spreadsheet_id = target_sheet_id
            self.is_connected = True
            self.connection_error = None
            self._read_service_account_email()
            
            # Setup worksheets if needed
            self._ensure_sheets_exist()
            # Initial pull to local cache
            self._sync_sheets_to_local(force=True)
            return True
        except Exception as e:
            self.is_connected = False
            err_msg = str(e)
            if "PERMISSION_DENIED" in err_msg or "403" in err_msg:
                email_hint = f" Ensure you have shared your Google Sheet with '{self.service_account_email}' as Editor." if self.service_account_email else ""
                self.connection_error = f"Google Sheet Permission Denied (403).{email_hint}"
            elif "404" in err_msg or "SpreadsheetNotFound" in err_msg:
                self.connection_error = f"Google Spreadsheet not found for ID '{target_sheet_id}'. Please verify the Sheet URL/ID."
            else:
                self.connection_error = f"Google Sheet connection error: {err_msg}"
            return False

    def get_status(self) -> Dict[str, Any]:
        title = None
        if self.is_connected and self.spreadsheet:
            try:
                title = self.spreadsheet.title
            except Exception:
                title = "Connected Sheet"
        return {
            "is_connected": self.is_connected,
            "mode": "google_sheets" if self.is_connected else "local_database",
            "spreadsheet_id": self.spreadsheet_id or "Not configured",
            "spreadsheet_title": title,
            "service_account_email": self.service_account_email,
            "service_account_file": self.service_account_path,
            "has_credentials": bool(Path(self.service_account_path).exists() if self.service_account_path else False),
            "status_message": "Google Sheet Active & Synchronized in Real-Time" if self.is_connected else self.connection_error or "Operating in local cache mode"
        }

    def _ensure_sheets_exist(self):
        """Ensure all required sheets exist in Google Spreadsheet with proper headers and initial seed data if new"""
        if not self.is_connected or not self.spreadsheet:
            return
        
        try:
            existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            required = [
                ("Settings", SETTINGS_HEADERS),
                ("Products", PRODUCTS_HEADERS),
                ("PromoCodes", PROMO_HEADERS),
                ("Slides", SLIDES_HEADERS),
                ("Orders", ORDERS_HEADERS)
            ]
            
            for name, headers in required:
                if name not in existing_sheets:
                    try:
                        ws = self.spreadsheet.add_worksheet(title=name, rows=100, cols=len(headers) + 2)
                        ws.append_row(headers)
                    except Exception as e:
                        print(f"Error creating sheet {name}: {e}")
                else:
                    try:
                        ws = self.spreadsheet.worksheet(name)
                        current_rows = ws.get_all_values()
                        if not current_rows:
                            ws.append_row(headers)
                    except Exception as e:
                        print(f"Error checking sheet headers {name}: {e}")
        except Exception as e:
            print(f"Error in _ensure_sheets_exist: {e}")

    def export_all_to_google_sheet(self) -> Dict[str, Any]:
        """Push all current local products, promocodes, slides, and settings into the Google Sheet"""
        if not self.is_connected or not self.spreadsheet:
            return {"success": False, "error": "Google Sheet is not connected"}
            
        try:
            data = self._load_local_data()
            
            # 1. Push Settings
            ws_settings = self.spreadsheet.worksheet("Settings")
            ws_settings.clear()
            settings_rows = [SETTINGS_HEADERS]
            for k, v in data.get("settings", {}).items():
                settings_rows.append([str(k), str(v)])
            ws_settings.update("A1", settings_rows)

            # 2. Push Products
            ws_prods = self.spreadsheet.worksheet("Products")
            ws_prods.clear()
            prod_rows = [PRODUCTS_HEADERS]
            for p in data.get("products", []):
                prod_rows.append([
                    p.get("id", ""),
                    p.get("title", ""),
                    p.get("description", ""),
                    p.get("price", 0.0),
                    p.get("discount_price") if p.get("discount_price") is not None else "",
                    p.get("category", "General"),
                    p.get("stock", 10),
                    json.dumps(p.get("images", [])),
                    json.dumps(p.get("videos", [])),
                    str(p.get("is_featured", False)),
                    p.get("badge") or "",
                    p.get("rating", 5.0),
                    p.get("review_count", 128),
                    p.get("created_at", "")
                ])
            ws_prods.update("A1", prod_rows)

            # 3. Push PromoCodes
            ws_promos = self.spreadsheet.worksheet("PromoCodes")
            ws_promos.clear()
            promo_rows = [PROMO_HEADERS]
            for pr in data.get("promo_codes", []):
                promo_rows.append([
                    pr.get("id", ""),
                    pr.get("code", ""),
                    pr.get("discount_type", "percentage"),
                    pr.get("discount_value", 0.0),
                    pr.get("min_order", 0.0),
                    pr.get("expiry_date") or "",
                    pr.get("usage_limit") or "",
                    pr.get("used_count", 0),
                    str(pr.get("is_active", True)),
                    pr.get("created_at", "")
                ])
            ws_promos.update("A1", promo_rows)

            # 4. Push Slides
            ws_slides = self.spreadsheet.worksheet("Slides")
            ws_slides.clear()
            slide_rows = [SLIDES_HEADERS]
            for s in data.get("slides", []):
                slide_rows.append([
                    s.get("id", ""),
                    s.get("title", ""),
                    s.get("subtitle", ""),
                    s.get("image_url", ""),
                    s.get("link_url", "/products"),
                    s.get("button_text", "Shop Now"),
                    str(s.get("is_active", True)),
                    s.get("display_order", 1),
                    s.get("created_at", "")
                ])
            ws_slides.update("A1", slide_rows)

            # 5. Push Orders
            ws_orders = self.spreadsheet.worksheet("Orders")
            ws_orders.clear()
            order_rows = [ORDERS_HEADERS]
            for o in data.get("orders", []):
                order_rows.append([
                    o.get("id", ""),
                    o.get("customer_name", ""),
                    o.get("customer_phone", ""),
                    o.get("customer_address", ""),
                    json.dumps(o.get("items", [])),
                    o.get("total_amount", 0.0),
                    o.get("discount_amount", 0.0),
                    o.get("final_amount", 0.0),
                    o.get("promo_code") or "",
                    o.get("status", "pending"),
                    o.get("notes") or "",
                    o.get("created_at", "")
                ])
            ws_orders.update("A1", order_rows)

            self.last_sync_time = time.time()
            return {"success": True, "message": "All products, promocodes, slides, and settings successfully pushed to Google Sheet!"}
        except Exception as e:
            return {"success": False, "error": f"Failed to push to Google Sheet: {str(e)}"}

    def _sync_sheets_to_local(self, force: bool = False):
        """Fetch remote Google Sheets data into local cache in real-time"""
        if not self.is_connected or not self.spreadsheet:
            return

        now = time.time()
        if not force and (now - self.last_sync_time) < self.SYNC_TTL:
            return

        try:
            local = self._load_local_data()
            
            # 1. Sync Settings
            try:
                ws_settings = self.spreadsheet.worksheet("Settings")
                rows = ws_settings.get_all_values()
                if len(rows) > 1:
                    st = local.get("settings", {})
                    for r in rows[1:]:
                        if len(r) >= 2 and r[0]:
                            k, v = r[0], r[1]
                            if k == "is_store_active":
                                st[k] = v.lower() == "true"
                            else:
                                st[k] = v
                    local["settings"] = st
            except Exception as e:
                print(f"Error syncing Settings from sheet: {e}")

            # 2. Sync Products
            try:
                ws_prod = self.spreadsheet.worksheet("Products")
                prod_rows = ws_prod.get_all_records()
                if prod_rows:
                    new_prods = []
                    for p in prod_rows:
                        if not p.get("id"):
                            continue
                        imgs = p.get("images", "")
                        if isinstance(imgs, str):
                            try:
                                imgs = json.loads(imgs) if imgs.startswith("[") else ([x.strip() for x in imgs.split(",") if x.strip()])
                            except Exception:
                                imgs = [imgs] if imgs else []
                        vids = p.get("videos", "")
                        if isinstance(vids, str):
                            try:
                                vids = json.loads(vids) if vids.startswith("[") else ([x.strip() for x in vids.split(",") if x.strip()])
                            except Exception:
                                vids = [vids] if vids else []
                        new_prods.append({
                            "id": str(p.get("id")),
                            "title": str(p.get("title", "")),
                            "description": str(p.get("description", "")),
                            "price": float(p.get("price", 0.0) or 0.0),
                            "discount_price": float(p.get("discount_price")) if p.get("discount_price") not in ("", None) else None,
                            "category": str(p.get("category", "General")),
                            "stock": int(p.get("stock", 10) or 10),
                            "images": imgs,
                            "videos": vids,
                            "is_featured": str(p.get("is_featured", "")).lower() == "true",
                            "badge": str(p.get("badge")) if p.get("badge") else None,
                            "rating": float(p.get("rating", 5.0) or 5.0),
                            "review_count": int(p.get("review_count", 128) or 128),
                            "created_at": str(p.get("created_at") or datetime.now().isoformat())
                        })
                    if new_prods:
                        local["products"] = new_prods
            except Exception as e:
                print(f"Error syncing Products from sheet: {e}")

            # 3. Sync Promo Codes
            try:
                ws_promo = self.spreadsheet.worksheet("PromoCodes")
                promo_rows = ws_promo.get_all_records()
                if promo_rows:
                    new_promos = []
                    for pr in promo_rows:
                        if not pr.get("id"):
                            continue
                        new_promos.append({
                            "id": str(pr.get("id")),
                            "code": str(pr.get("code", "")).upper(),
                            "discount_type": str(pr.get("discount_type", "percentage")),
                            "discount_value": float(pr.get("discount_value", 0.0) or 0.0),
                            "min_order": float(pr.get("min_order", 0.0) or 0.0),
                            "expiry_date": str(pr.get("expiry_date")) if pr.get("expiry_date") else None,
                            "usage_limit": int(pr.get("usage_limit")) if pr.get("usage_limit") not in ("", None) else None,
                            "used_count": int(pr.get("used_count", 0) or 0),
                            "is_active": str(pr.get("is_active", "")).lower() == "true",
                            "created_at": str(pr.get("created_at") or datetime.now().isoformat())
                        })
                    if new_promos:
                        local["promo_codes"] = new_promos
            except Exception as e:
                print(f"Error syncing PromoCodes from sheet: {e}")

            # 4. Sync Slides
            try:
                ws_slides = self.spreadsheet.worksheet("Slides")
                slide_rows = ws_slides.get_all_records()
                if slide_rows:
                    new_slides = []
                    for s in slide_rows:
                        if not s.get("id"):
                            continue
                        new_slides.append({
                            "id": str(s.get("id")),
                            "title": str(s.get("title", "")),
                            "subtitle": str(s.get("subtitle", "")),
                            "image_url": str(s.get("image_url", "")),
                            "link_url": str(s.get("link_url", "/products")),
                            "button_text": str(s.get("button_text", "Shop Now")),
                            "is_active": str(s.get("is_active", "")).lower() == "true",
                            "display_order": int(s.get("display_order", 1) or 1),
                            "created_at": str(s.get("created_at") or datetime.now().isoformat())
                        })
                    if new_slides:
                        local["slides"] = new_slides
            except Exception as e:
                print(f"Error syncing Slides from sheet: {e}")

            # 5. Sync Orders
            try:
                ws_orders = self.spreadsheet.worksheet("Orders")
                order_rows = ws_orders.get_all_records()
                if order_rows:
                    new_orders = []
                    for ord in order_rows:
                        if not ord.get("id"):
                            continue
                        items_raw = ord.get("items_json", "[]")
                        try:
                            items_parsed = json.loads(items_raw) if isinstance(items_raw, str) else items_raw
                        except Exception:
                            items_parsed = []
                        new_orders.append({
                            "id": str(ord.get("id")),
                            "customer_name": str(ord.get("customer_name", "")),
                            "customer_phone": str(ord.get("customer_phone", "")),
                            "customer_address": str(ord.get("customer_address", "")),
                            "items": items_parsed,
                            "total_amount": float(ord.get("total_amount", 0.0) or 0.0),
                            "discount_amount": float(ord.get("discount_amount", 0.0) or 0.0),
                            "final_amount": float(ord.get("final_amount", 0.0) or 0.0),
                            "promo_code": str(ord.get("promo_code")) if ord.get("promo_code") else None,
                            "status": str(ord.get("status", "pending")),
                            "notes": str(ord.get("notes")) if ord.get("notes") else None,
                            "created_at": str(ord.get("created_at") or datetime.now().isoformat())
                        })
                    if new_orders:
                        local["orders"] = new_orders
            except Exception as e:
                print(f"Error syncing Orders from sheet: {e}")

            self._save_local_data(local)
            self.last_sync_time = time.time()
            self.notify_change("sheets_synced", {"timestamp": self.last_sync_time})
        except Exception as e:
            print(f"Error syncing sheets to local: {e}")

    # ==================== REAL-TIME SETTINGS OPERATIONS ====================
    def get_settings(self) -> Dict[str, Any]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        return data.get("settings", DEFAULT_SEED_DATA["settings"])

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_local_data()
        current = data.get("settings", DEFAULT_SEED_DATA["settings"])
        for k, v in new_settings.items():
            if v is not None:
                current[k] = v
        data["settings"] = current
        self._save_local_data(data)
        
        # Write to Google Sheets if connected
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Settings")
                ws.clear()
                rows = [SETTINGS_HEADERS]
                for k, v in current.items():
                    rows.append([str(k), str(v)])
                ws.update("A1", rows)
                self.last_sync_time = time.time()
            except Exception as e:
                print(f"Google Sheet settings update error: {e}")
                
        self.notify_change("settings_updated", current)
        return current

    def toggle_store_status(self, is_active: bool) -> bool:
        settings_dict = self.get_settings()
        settings_dict["is_store_active"] = is_active
        self.update_settings(settings_dict)
        return is_active

    # ==================== REAL-TIME PRODUCTS OPERATIONS ====================
    def get_products(self, category: Optional[str] = None, featured_only: bool = False, query: Optional[str] = None) -> List[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        prods = data.get("products", [])
        
        if category and category.lower() != "all":
            prods = [p for p in prods if p.get("category", "").lower() == category.lower()]
            
        if featured_only:
            prods = [p for p in prods if p.get("is_featured") is True]
            
        if query:
            q = query.lower().strip()
            prods = [
                p for p in prods 
                if q in p.get("title", "").lower() 
                or q in p.get("description", "").lower() 
                or q in p.get("category", "").lower()
            ]
            
        return prods

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        for p in data.get("products", []):
            if p.get("id") == product_id:
                return p
        return None

    def create_product(self, prod_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_local_data()
        new_prod = {
            "id": f"prod-{uuid.uuid4().hex[:8]}",
            "title": prod_data.get("title", ""),
            "description": prod_data.get("description", ""),
            "price": float(prod_data.get("price", 0.0)),
            "discount_price": float(prod_data["discount_price"]) if prod_data.get("discount_price") is not None else None,
            "category": prod_data.get("category", "General"),
            "stock": int(prod_data.get("stock", 10)),
            "images": prod_data.get("images", []),
            "videos": prod_data.get("videos", []),
            "is_featured": bool(prod_data.get("is_featured", False)),
            "badge": prod_data.get("badge") or None,
            "rating": float(prod_data.get("rating", 5.0)),
            "review_count": int(prod_data.get("review_count", 128)),
            "created_at": datetime.now().isoformat()
        }
        data.setdefault("products", []).insert(0, new_prod)
        self._save_local_data(data)

        # Google Sheets Sync
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Products")
                row = [
                    new_prod["id"],
                    new_prod["title"],
                    new_prod["description"],
                    new_prod["price"],
                    new_prod["discount_price"] if new_prod["discount_price"] is not None else "",
                    new_prod["category"],
                    new_prod["stock"],
                    json.dumps(new_prod["images"]),
                    json.dumps(new_prod["videos"]),
                    str(new_prod["is_featured"]),
                    new_prod["badge"] or "",
                    new_prod["rating"],
                    new_prod["review_count"],
                    new_prod["created_at"]
                ]
                ws.append_row(row)
                self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error appending product to Google Sheet: {e}")
                
        self.notify_change("products_updated", {"action": "create", "product": new_prod})
        return new_prod

    def update_product(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._load_local_data()
        products = data.get("products", [])
        target = None
        for p in products:
            if p.get("id") == product_id:
                for k, v in updates.items():
                    if v is not None:
                        p[k] = v
                target = p
                break
                
        if not target:
            return None
            
        data["products"] = products
        self._save_local_data(data)

        # Google Sheets Sync
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Products")
                cell = ws.find(product_id)
                if cell:
                    row_idx = cell.row
                    updated_row = [
                        target["id"],
                        target["title"],
                        target["description"],
                        target["price"],
                        target["discount_price"] if target.get("discount_price") is not None else "",
                        target["category"],
                        target["stock"],
                        json.dumps(target.get("images", [])),
                        json.dumps(target.get("videos", [])),
                        str(target.get("is_featured", False)),
                        target.get("badge") or "",
                        target.get("rating", 5.0),
                        target.get("review_count", 128),
                        target.get("created_at", "")
                    ]
                    ws.update(f"A{row_idx}:N{row_idx}", [updated_row])
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error updating product in Google Sheet: {e}")
                
        self.notify_change("products_updated", {"action": "update", "product": target})
        return target

    def delete_product(self, product_id: str) -> bool:
        data = self._load_local_data()
        products = data.get("products", [])
        initial_len = len(products)
        products = [p for p in products if p.get("id") != product_id]
        if len(products) == initial_len:
            return False
            
        data["products"] = products
        self._save_local_data(data)

        # Google Sheets Sync
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Products")
                cell = ws.find(product_id)
                if cell:
                    ws.delete_rows(cell.row)
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error deleting product in Google Sheet: {e}")
                
        self.notify_change("products_updated", {"action": "delete", "product_id": product_id})
        return True


    # ==================== REAL-TIME PROMO CODES OPERATIONS ====================
    def get_promo_codes(self) -> List[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        return data.get("promo_codes", [])

    def get_promo_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        self._sync_sheets_to_local()
        clean_code = code.strip().upper()
        data = self._load_local_data()
        for p in data.get("promo_codes", []):
            if p.get("code", "").upper() == clean_code:
                return p
        return None

    def create_promo_code(self, promo_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_local_data()
        new_promo = {
            "id": f"promo-{uuid.uuid4().hex[:6]}",
            "code": promo_data.get("code", "").strip().upper(),
            "discount_type": promo_data.get("discount_type", "percentage"),
            "discount_value": float(promo_data.get("discount_value", 0.0)),
            "min_order": float(promo_data.get("min_order", 0.0)),
            "expiry_date": promo_data.get("expiry_date"),
            "usage_limit": promo_data.get("usage_limit"),
            "used_count": 0,
            "is_active": bool(promo_data.get("is_active", True)),
            "created_at": datetime.now().isoformat()
        }
        data.setdefault("promo_codes", []).insert(0, new_promo)
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("PromoCodes")
                row = [
                    new_promo["id"],
                    new_promo["code"],
                    new_promo["discount_type"],
                    new_promo["discount_value"],
                    new_promo["min_order"],
                    new_promo["expiry_date"] or "",
                    new_promo["usage_limit"] or "",
                    new_promo["used_count"],
                    str(new_promo["is_active"]),
                    new_promo["created_at"]
                ]
                ws.append_row(row)
                self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error appending promo to Google Sheet: {e}")

        self.notify_change("promos_updated", {"action": "create", "promo": new_promo})
        return new_promo


    def update_promo_code(self, promo_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._load_local_data()
        promos = data.get("promo_codes", [])
        target = None
        for p in promos:
            if p.get("id") == promo_id:
                for k, v in updates.items():
                    if v is not None:
                        if k == "code":
                            p[k] = v.strip().upper()
                        else:
                            p[k] = v
                target = p
                break
        if not target:
            return None
        data["promo_codes"] = promos
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("PromoCodes")
                cell = ws.find(promo_id)
                if cell:
                    row = [
                        target["id"],
                        target["code"],
                        target["discount_type"],
                        target["discount_value"],
                        target["min_order"],
                        target.get("expiry_date") or "",
                        target.get("usage_limit") or "",
                        target.get("used_count", 0),
                        str(target.get("is_active", True)),
                        target.get("created_at", "")
                    ]
                    ws.update(f"A{cell.row}:J{cell.row}", [row])
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error updating promo in Google Sheet: {e}")
                
        self.notify_change("promos_updated", {"action": "update", "promo": target})
        return target

    def delete_promo_code(self, promo_id: str) -> bool:
        data = self._load_local_data()
        promos = data.get("promo_codes", [])
        initial_len = len(promos)
        promos = [p for p in promos if p.get("id") != promo_id]
        if len(promos) == initial_len:
            return False
        data["promo_codes"] = promos
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("PromoCodes")
                cell = ws.find(promo_id)
                if cell:
                    ws.delete_rows(cell.row)
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error deleting promo in Google Sheet: {e}")
        self.notify_change("promos_updated", {"action": "delete", "promo_id": promo_id})
        return True


    def increment_promo_usage(self, code: str):
        clean = code.strip().upper()
        data = self._load_local_data()
        for p in data.get("promo_codes", []):
            if p.get("code", "").upper() == clean:
                p["used_count"] = p.get("used_count", 0) + 1
                self._save_local_data(data)
                
                # Update in Google Sheet
                if self.is_connected and self.spreadsheet:
                    try:
                        ws = self.spreadsheet.worksheet("PromoCodes")
                        cell = ws.find(p["id"])
                        if cell:
                            # Column H is used_count (8th column)
                            ws.update_cell(cell.row, 8, p["used_count"])
                    except Exception as e:
                        print(f"Error updating promo usage in sheet: {e}")
                break

    # ==================== REAL-TIME SLIDES OPERATIONS ====================
    def get_slides(self, active_only: bool = False) -> List[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        slides = data.get("slides", [])
        if active_only:
            slides = [s for s in slides if s.get("is_active") is True]
        slides.sort(key=lambda x: x.get("display_order", 1))
        return slides

    def create_slide(self, slide_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_local_data()
        new_slide = {
            "id": f"slide-{uuid.uuid4().hex[:6]}",
            "title": slide_data.get("title", ""),
            "subtitle": slide_data.get("subtitle", ""),
            "image_url": slide_data.get("image_url", ""),
            "link_url": slide_data.get("link_url", "/products"),
            "button_text": slide_data.get("button_text", "Shop Now"),
            "is_active": bool(slide_data.get("is_active", True)),
            "display_order": int(slide_data.get("display_order", len(data.get("slides", [])) + 1)),
            "created_at": datetime.now().isoformat()
        }
        data.setdefault("slides", []).append(new_slide)
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Slides")
                row = [
                    new_slide["id"],
                    new_slide["title"],
                    new_slide["subtitle"],
                    new_slide["image_url"],
                    new_slide["link_url"],
                    new_slide["button_text"],
                    str(new_slide["is_active"]),
                    new_slide["display_order"],
                    new_slide["created_at"]
                ]
                ws.append_row(row)
                self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error appending slide to Google Sheet: {e}")
        self.notify_change("slides_updated", {"action": "create", "slide": new_slide})
        return new_slide

    def update_slide(self, slide_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._load_local_data()
        slides = data.get("slides", [])
        target = None
        for s in slides:
            if s.get("id") == slide_id:
                for k, v in updates.items():
                    if v is not None:
                        s[k] = v
                target = s
                break
        if not target:
            return None
        data["slides"] = slides
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Slides")
                cell = ws.find(slide_id)
                if cell:
                    row = [
                        target["id"],
                        target["title"],
                        target["subtitle"],
                        target["image_url"],
                        target["link_url"],
                        target["button_text"],
                        str(target.get("is_active", True)),
                        target.get("display_order", 1),
                        target.get("created_at", "")
                    ]
                    ws.update(f"A{cell.row}:I{cell.row}", [row])
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error updating slide in Google Sheet: {e}")
        self.notify_change("slides_updated", {"action": "update", "slide": target})
        return target

    def delete_slide(self, slide_id: str) -> bool:
        data = self._load_local_data()
        slides = data.get("slides", [])
        initial_len = len(slides)
        slides = [s for s in slides if s.get("id") != slide_id]
        if len(slides) == initial_len:
            return False
        data["slides"] = slides
        self._save_local_data(data)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Slides")
                cell = ws.find(slide_id)
                if cell:
                    ws.delete_rows(cell.row)
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error deleting slide in Google Sheet: {e}")
        self.notify_change("slides_updated", {"action": "delete", "slide_id": slide_id})
        return True


    # ==================== REAL-TIME ORDERS OPERATIONS ====================
    def get_orders(self) -> List[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        orders = data.get("orders", [])
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return orders

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        self._sync_sheets_to_local()
        data = self._load_local_data()
        for o in data.get("orders", []):
            if o.get("id") == order_id:
                return o
        return None

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_local_data()
        items = order_data.get("items", [])
        total = sum(item.get("price", 0.0) * item.get("quantity", 1) for item in items)
        
        # Calculate discount
        discount_amount = 0.0
        promo_code = order_data.get("promo_code")
        if promo_code:
            promo = self.get_promo_by_code(promo_code)
            if promo and promo.get("is_active"):
                if promo.get("discount_type") == "percentage":
                    discount_amount = round(total * (promo.get("discount_value", 0.0) / 100.0), 2)
                else:
                    discount_amount = min(total, promo.get("discount_value", 0.0))
                self.increment_promo_usage(promo_code)

        final_amount = max(0.0, round(total - discount_amount, 2))
        
        new_order = {
            "id": f"ORD-{int(datetime.now().timestamp())}",
            "customer_name": order_data.get("customer_name"),
            "customer_phone": order_data.get("customer_phone"),
            "customer_address": order_data.get("customer_address"),
            "items": items,
            "total_amount": round(total, 2),
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "promo_code": promo_code,
            "status": "pending",
            "notes": order_data.get("notes"),
            "created_at": datetime.now().isoformat()
        }
        
        data.setdefault("orders", []).insert(0, new_order)
        self._save_local_data(data)

        # Real-time append to Google Sheet
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Orders")
                row = [
                    new_order["id"],
                    new_order["customer_name"],
                    new_order["customer_phone"],
                    new_order["customer_address"],
                    json.dumps(new_order["items"]),
                    new_order["total_amount"],
                    new_order["discount_amount"],
                    new_order["final_amount"],
                    new_order["promo_code"] or "",
                    new_order["status"],
                    new_order.get("notes") or "",
                    new_order["created_at"]
                ]
                ws.append_row(row)
                self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error appending order to Google Sheet: {e}")
                
        self.notify_change("orders_updated", {"action": "create", "order": new_order})
        return new_order

    def update_order_status(self, order_id: str, status: str) -> Optional[Dict[str, Any]]:
        data = self._load_local_data()
        orders = data.get("orders", [])
        target = None
        for o in orders:
            if o.get("id") == order_id:
                o["status"] = status
                target = o
                break
        if not target:
            return None
        data["orders"] = orders
        self._save_local_data(data)

        # Real-time update in Google Sheet
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("Orders")
                cell = ws.find(order_id)
                if cell:
                    # Column J is status (10th column)
                    ws.update_cell(cell.row, 10, status)
                    self.last_sync_time = time.time()
            except Exception as e:
                print(f"Error updating order status in Google Sheet: {e}")
        self.notify_change("orders_updated", {"action": "update_status", "order_id": order_id, "status": status})
        return target


db = GoogleSheetDatabase()
