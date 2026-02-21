"""WSGI entry for gunicorn (production)."""
import os

# Load env before app
from pathlib import Path
from dotenv import load_dotenv
BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
env = os.getenv("FLASK_ENV", "production")
load_dotenv(BASE / f".env.{env}")

import sys
sys.path.insert(0, str(BASE))

from src.app import create_app
app = create_app()
