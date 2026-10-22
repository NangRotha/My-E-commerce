import os
import uuid
import base64
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.config import settings

router = APIRouter(prefix="/upload", tags=["Media Uploads"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".mkv", ".avi"}

def get_base_url(request: Request) -> str:
    if settings.BACKEND_URL and "localhost" not in settings.BACKEND_URL:
        return settings.BACKEND_URL.rstrip("/")
    return str(request.base_url).rstrip("/")

def get_image_mime(ext: str) -> str:
    ext = ext.lower()
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    if ext == ".gif":
        return "image/gif"
    if ext == ".svg":
        return "image/svg+xml"
    return "image/jpeg"

@router.post("/images", response_model=List[str])
async def upload_multiple_images(request: Request, files: List[UploadFile] = File(...)):
    """Upload multiple image files and return their public URLs (or data URLs on serverless)"""
    urls = []
    base_url = get_base_url(request)
    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' has unsupported image type. Allowed: {list(ALLOWED_IMAGE_EXTENSIONS)}")
        
        content = await file.read()

        # In serverless environment (Vercel), convert directly to data URL so it never 404s
        if settings.IS_VERCEL:
            mime = get_image_mime(ext)
            b64 = base64.b64encode(content).decode("utf-8")
            urls.append(f"data:{mime};base64,{b64}")
            continue

        unique_name = f"{uuid.uuid4().hex[:10]}{ext}"
        dest_path = settings.IMAGES_DIR / unique_name
        with open(dest_path, "wb") as buffer:
            buffer.write(content)
            
        file_url = f"{base_url}/uploads/images/{unique_name}"
        urls.append(file_url)
        
    return urls

@router.post("/videos", response_model=List[str])
async def upload_multiple_videos(request: Request, files: List[UploadFile] = File(...)):
    """Upload multiple video files and return their public URLs"""
    urls = []
    base_url = get_base_url(request)
    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' has unsupported video type. Allowed: {list(ALLOWED_VIDEO_EXTENSIONS)}")
        
        content = await file.read()
        unique_name = f"{uuid.uuid4().hex[:10]}{ext}"
        dest_path = settings.VIDEOS_DIR / unique_name
        
        with open(dest_path, "wb") as buffer:
            buffer.write(content)
            
        file_url = f"{base_url}/uploads/videos/{unique_name}"
        urls.append(file_url)
        
    return urls

@router.post("/single")
async def upload_single(request: Request, file: UploadFile = File(...)):
    """Upload a single image/video (e.g. store logo or banner)"""
    ext = Path(file.filename or "").suffix.lower()
    is_image = ext in ALLOWED_IMAGE_EXTENSIONS
    is_video = ext in ALLOWED_VIDEO_EXTENSIONS
    
    if not is_image and not is_video:
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    content = await file.read()

    # In serverless environment (Vercel), convert images directly to data URL for 100% persistence
    if settings.IS_VERCEL and is_image:
        mime = get_image_mime(ext)
        b64 = base64.b64encode(content).decode("utf-8")
        url = f"data:{mime};base64,{b64}"
        return {"url": url, "filename": file.filename or "upload", "type": "image"}

    target_dir = settings.IMAGES_DIR if is_image else settings.VIDEOS_DIR
    sub_dir = "images" if is_image else "videos"
    
    unique_name = f"{uuid.uuid4().hex[:10]}{ext}"
    dest_path = target_dir / unique_name
    
    with open(dest_path, "wb") as buffer:
        buffer.write(content)
        
    base_url = get_base_url(request)
    url = f"{base_url}/uploads/{sub_dir}/{unique_name}"
    return {"url": url, "filename": file.filename or "upload", "type": "image" if is_image else "video"}
