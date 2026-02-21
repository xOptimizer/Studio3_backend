# Project Setup

This guide walks you through setting up and running the Flask REST API backend.

## Prerequisites

- **Python 3.9+**
- **PostgreSQL** – running and accessible
- **Redis** – running and accessible
- (Optional) **SMTP** – for OTP and password-reset emails  
- (Optional) **Google OAuth** – for Google sign-in

## 1. Clone and enter the project

```bash
cd /path/to/Server
```

## 2. Virtual environment

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Environment variables

Environment is selected by `FLASK_ENV`:

- **Development:** `FLASK_ENV=development` → loads `.env` then `.env.development`
- **Production:** `FLASK_ENV=production` → loads `.env` then `.env.production`

**Steps:**

1. Copy the example file:
   ```bash
   cp .env.example .env.development
   ```
2. Edit `.env.development` and set at least:
   - `DATABASE_URL` – PostgreSQL connection string (e.g. `postgresql://user:password@localhost:5432/flask_app_dev`)
   - `REDIS_URL` – Redis connection (e.g. `redis://localhost:6379/0`)
   - `JWT_SECRET` – secret for signing JWTs (use a strong value in production)
   - `SECRET_KEY` – Flask secret (use a strong value in production)

Optional for full features:

- **SMTP** – `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` (and optionally `SMTP_PORT`) for OTP and password-reset emails
- **Google OAuth** – `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `BACKEND_URL`, `FRONTEND_URL`, `OAUTH_SUCCESS_PATH`
- **CORS** – `FRONTEND_URL` (used for CORS and redirects)

## 5. Database

1. Create a PostgreSQL database (e.g. `flask_app_dev`).
2. Run migrations from the project root:
   ```bash
   alembic upgrade head
   ```
3. To create a new migration after changing models:
   ```bash
   alembic revision --autogenerate -m "Describe your change"
   alembic upgrade head
   ```

## 6. Redis

Ensure Redis is running and reachable at the URL set in `REDIS_URL`. The app uses Redis for:

- Sessions (login state)
- OTP storage and rate limits
- OAuth state (Google)

## 7. Run the application

**Development:**

```bash
FLASK_ENV=development python3 run.py
```

Or, with default env as development:

```bash
python run.py
```

The server listens on `0.0.0.0:PORT` (default `PORT=9000`).

**Production (Gunicorn):**

```bash
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:9000 wsgi:app
```

Set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, and `SECRET_KEY` in `.env.production` or the process environment.

## 8. Verify

- **Health:** Open or curl `http://localhost:9000/`  
  Expected: `{ "message": "Virtual Instructor Backend Running" }`
- **API:** See [API documentation](API.md) for endpoints and examples.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `Database connection failed` | PostgreSQL is running; `DATABASE_URL` is correct; DB exists; network/firewall. |
| `Redis connection failed` | Redis is running; `REDIS_URL` is correct. |
| `ModuleNotFoundError: src` | Run commands from the **project root** (where `run.py` and `src/` are). |
| OTP / reset emails not sent | SMTP vars set in env; no errors in `logs/error.log`. |
| Google OAuth fails | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `BACKEND_URL`, `FRONTEND_URL` set; redirect URI in Google Console matches `BACKEND_URL/api/auth/google/callback`. |

Logs are written under the `logs/` directory (e.g. `error.log`, `combined.log`).
