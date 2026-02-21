"""Entry: load env (by FLASK_ENV), connect DB + Redis, then run Flask app. Exit on connection failure."""
import os
import sys
from pathlib import Path

# Load env before any app/config imports
BASE_DIR = Path(__file__).resolve().parent
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
env_name = os.getenv("FLASK_ENV", "development")
env_file = BASE_DIR / f".env.{env_name}"
if env_file.exists():
    load_dotenv(env_file)

# Ensure project root on path
sys.path.insert(0, str(BASE_DIR))

from src.shared.config.database import check_db_connection
from src.shared.config.redis_client import check_redis_connection, close_redis
from src.shared.utils.logger import get_logger

logger = get_logger("run")

def main():
    if not check_db_connection():
        logger.error("Database connection failed. Check DATABASE_URL.")
        sys.exit(1)
    if not check_redis_connection():
        logger.error("Redis connection failed. Check REDIS_URL.")
        sys.exit(1)

    from src.app import create_app
    app = create_app()

    port = int(os.getenv("PORT", 9000))
    try:
        app.run(host="0.0.0.0", port=port)
    finally:
        close_redis()

if __name__ == "__main__":
    main()
