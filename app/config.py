import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# Detect serverless environment (Vercel, AWS Lambda, etc.)
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

def get_writable_dir(sub_dir: str) -> Path:
    """Returns a writable directory path (fallback to /tmp in serverless/Vercel)"""
    candidate = BASE_DIR / sub_dir
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = candidate / ".write_test"
        test_file.touch(exist_ok=True)
        test_file.unlink(missing_ok=True)
        return candidate
    except (OSError, PermissionError):
        tmp_candidate = Path(tempfile.gettempdir()) / "ecommerce" / sub_dir
        tmp_candidate.mkdir(parents=True, exist_ok=True)
        return tmp_candidate

class Settings:
    PROJECT_NAME: str = "CRESCENDO E-Commerce API with Google Sheet & AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    BASE_DIR: Path = BASE_DIR
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Google Sheet Configuration
    # The ID can be extracted from URL: https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    GOOGLE_APPS_SCRIPT_URL: str = os.getenv("GOOGLE_APPS_SCRIPT_URL", "")
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "service_account.json"))
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", os.getenv("GOOGLE_CREDENTIALS_JSON", ""))
    
    # Google Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Storage directories (Safe for Vercel Serverless)
    UPLOAD_DIR: Path = get_writable_dir("uploads")
    IMAGES_DIR: Path = get_writable_dir("uploads/images")
    VIDEOS_DIR: Path = get_writable_dir("uploads/videos")
    DATA_DIR: Path = get_writable_dir("data")
    
    # Base URL for serving uploaded files
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

settings = Settings()
