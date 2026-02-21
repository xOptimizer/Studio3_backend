# Flask REST API (Virtual Instructor style)

Python Flask backend with **PostgreSQL** (SQLAlchemy 2.0), **Alembic**, and **Redis**. Layout: routes → controllers → services / DAOs.

**Documentation:** See the [`docs/`](docs/) folder:
- [**Project setup**](docs/README.md) – prerequisites, env, DB, Redis, run, troubleshooting
- [**API reference**](docs/API.md) – endpoints, request/response format, auth

## Stack

- **Flask 3** – app factory, blueprints, CORS
- **SQLAlchemy 2** – engine, session, models (no Flask-SQLAlchemy)
- **Alembic** – migrations (`alembic/`)
- **PostgreSQL** – `psycopg2-binary`
- **Redis** – sessions, OTP, OAuth state
- **JWT** – access tokens; refresh token in httpOnly cookie
- **Gunicorn** – production WSGI

## Env

- **`.env`** – optional; loaded first
- **`.env.development`** – when `FLASK_ENV=development`
- **`.env.production`** – when `FLASK_ENV=production`

Copy `.env.example` and set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `SECRET_KEY` (and SMTP / Google OAuth if used).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Set DATABASE_URL, REDIS_URL in .env.development (or .env)
alembic upgrade head
```

## Run

- **Dev:** `FLASK_ENV=development python run.py` (or `python run.py`; default env is development)
- **Prod:** `FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:9000 wsgi:app`

## Layout

```
project_root/
├── run.py                 # Entry: load env, check DB+Redis, create app
├── wsgi.py                # Gunicorn entry
├── src/
│   ├── app.py             # Flask app, CORS, blueprints, error handler
│   ├── middlewares/       # error_handler, auth_middleware (JWT + Redis session)
│   ├── shared/
│   │   ├── config/         # database.py, redis_client.py
│   │   ├── models/         # SQLAlchemy models (users, accounts, sessions, refresh_tokens, password_reset_tokens)
│   │   ├── utils/          # AppError, api_response, messages, jwt_utils, logger
│   │   ├── notification/  # email_service
│   │   └── templates/     # OTP, password-reset HTML
│   └── modules/
│       ├── auth/           # auth_routes, auth_controller, auth_dao, services (OTP, password_reset), google_oauth_service
│       ├── user/           # user_routes, user_controller, user_dao
│       └── sessions/       # session_service (Redis), refresh_token_dao
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── .env.development / .env.production / .env.example
```

## API

- **Health:** `GET /` → `{ "message": "Virtual Instructor Backend Running" }`
- **Auth** (`/api/auth`):
  - `POST /otp/generate`, `POST /otp/resend` – body `{ "email" }`
  - `POST /register` – body `{ "name", "email", "password", "otp" }`
  - `POST /login` – body `{ "email", "password" }`
  - `POST /refresh` – cookie `refreshToken`
  - `POST /logout`, `POST /logout-all` (protected)
  - `POST /forget-password`, `POST /reset-password`
  - `GET /google`, `GET /google/callback`
- **User** (`/api/user`):
  - `GET /getall` – protected; `{ "users", "count" }`

Responses: `{ "success": true, "message": "...", "data": ... }` or `{ "success": false, "message": "..." }`.

## Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```
