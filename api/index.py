import sys
from pathlib import Path

# Add project root directory to sys.path so 'app' and its modules can always be imported
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app

# Handler for Vercel Serverless Function (ASGI)
handler = app
