# My-E-commerce

FastAPI Backend with Google Sheets Database, Media Uploads, and Google Gemini AI Shopping Assistant.

Deployed live on **Vercel Serverless Functions**.

## 🌐 Live Production API
- **Base URL**: https://backend-nu-two-91.vercel.app
- **API Prefix**: https://backend-nu-two-91.vercel.app/api
- **Interactive Swagger Docs**: https://backend-nu-two-91.vercel.app/docs

## 📁 Repository Structure
```
.
├── api/
│   └── index.py             # Vercel Serverless Function entrypoint (ASGI)
├── app/
│   ├── main.py              # FastAPI application, CORS, routers & static mounts
│   ├── config.py            # App settings & safe paths for Vercel (/tmp fallback)
│   ├── sheets_db.py         # Google Sheets real-time engine & local cache fallback
│   ├── ai_service.py        # Google Gemini 2.0 Flash AI customer chat assistant
│   ├── models.py            # Pydantic models & validation schemas
│   └── routes/              # Modular REST API endpoints
│       ├── products.py      # Products & categories CRUD
│       ├── promo_codes.py   # Discount coupons & cart validation
│       ├── settings.py      # Store settings & master online/offline toggle
│       ├── slides.py        # Banner sliders CRUD
│       ├── orders.py        # Customer checkout & order management
│       ├── uploads.py       # Multiple image/video upload handlers
│       ├── ai.py            # AI chat replay & prompt suggestions
│       └── realtime.py      # Real-time sync & polling version endpoint
├── data/
│   └── db.json              # Bundled product catalog & store seed data
├── vercel.json              # Vercel serverless routing configuration
├── pyproject.toml           # Python package configuration (>=3.12)
├── requirements.txt         # Core dependencies
└── .python-version          # Pinned to Python 3.12
```

## 🛠️ Local Development
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
