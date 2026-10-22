from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.sheets_db import db
from app.routes import (
    products,
    promo_codes,
    settings as settings_router,
    slides,
    orders,
    uploads,
    ai,
    realtime
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="E-Commerce Backend with Google Sheets Database, Media Uploads, and AI Customer Assistant"
)

# Enable CORS for Frontend-User (3000) and Frontend-Admin (3001) and any client origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for uploads (images & videos) safely
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

try:
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
except Exception as e:
    print(f"Notice: StaticFiles mount for uploads skipped or already mounted: {e}")

# Include Routers
app.include_router(products.router, prefix=settings.API_PREFIX)
app.include_router(promo_codes.router, prefix=settings.API_PREFIX)
app.include_router(settings_router.router, prefix=settings.API_PREFIX)
app.include_router(slides.router, prefix=settings.API_PREFIX)
app.include_router(orders.router, prefix=settings.API_PREFIX)
app.include_router(uploads.router, prefix=settings.API_PREFIX)
app.include_router(ai.router, prefix=settings.API_PREFIX)
app.include_router(realtime.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db.get_status(),
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
