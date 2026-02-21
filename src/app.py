"""Flask app: middleware (CORS, JSON), blueprints /api/auth and /api/user, global error handler."""
import os
from flask import Flask
from flask_cors import CORS

from src.middlewares.error_handler import register_error_handler

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["JSON_SORT_KEYS"] = False

    # CORS: allow frontend origin
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS(app, origins=[frontend_url], supports_credentials=True)

    # Blueprints
    from src.modules.auth.auth_routes import auth_bp
    from src.modules.user.user_routes import user_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    # Health at root
    @app.get("/")
    def health():
        return {"message": "Virtual Instructor Backend Running"}, 200

    # Global error handler (register last)
    register_error_handler(app)

    return app
