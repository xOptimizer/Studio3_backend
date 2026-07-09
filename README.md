# Studiothree Discover — Backend API

Python Flask backend for **Studiothree Discover** (mobile + web). PostgreSQL (SQLAlchemy 2.0), Alembic, and Redis. Layout: routes → controllers → services / DAOs.

**Documentation:** See the [`docs/`](docs/) folder:
- [**Project setup**](docs/README.md) – prerequisites, env, DB, Redis, run, troubleshooting
- [**API reference**](docs/API.md) – endpoints, request/response format, auth

## Stack

- **Flask 3** – app factory, blueprints, CORS
- **SQLAlchemy 2** – engine, session, models (no Flask-SQLAlchemy)
- **Alembic** – migrations (`alembic/`)
- **PostgreSQL** – `psycopg2-binary`
- **Redis** – sessions, OTP
- **JWT** – access tokens; refresh token in httpOnly cookie
- **boto3 / S3** – media presign uploads (images + video); dev-mode placeholder URLs when unconfigured
- **Gunicorn** – production WSGI

## Env

- **`.env`** – optional; loaded first
- **`.env.development`** – when `FLASK_ENV=development`
- **`.env.production`** – when `FLASK_ENV=production`

Copy `.env.example` and set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `SECRET_KEY` (and SMTP if used).

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
│   │   ├── models/         # SQLAlchemy models (users, accounts, sessions, refresh_tokens,
│   │   │                    # password_reset_tokens, username_history, pieces, posts,
│   │   │                    # follows/likes/comments/saves/collections, series/series_pieces)
│   │   ├── utils/          # AppError, api_response, messages, jwt_utils, logger, rate_limit, async_handler
│   │   ├── storage/        # s3_client, s3_paths, s3_service (presign, media URL validation)
│   │   ├── username/       # normalize, validate, allocate, claim, blocklist, suggest
│   │   ├── notification/  # email_service
│   │   └── templates/     # OTP, password-reset HTML
│   └── modules/
│       ├── auth/           # auth_routes, auth_controller, auth_dao, services (OTP, password_reset)
│       ├── user/            # profile, onboarding, seller mode/analytics, saved pieces, public content routes
│       ├── media/           # presign upload controller
│       ├── pieces/          # pieces_routes, pieces_controller, pieces_dao
│       ├── posts/           # posts_routes, posts_controller, posts_dao
│       ├── social/          # follow/like/save/comments (social_routes, social_controller, social_dao)
│       ├── feeds/           # following/explore/for-you, cursor pagination
│       ├── series/          # series_routes, series_controller, series_dao
│       └── sessions/       # session_service (Redis), refresh_token_dao
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── .env.development / .env.production / .env.example
```

## API

- **Health:** `GET /` → `{ "message": "Studiothree Discover API running" }`
- **Auth** (`/api/auth`): OTP generate/resend, register (`phone` optional), login, refresh, logout, logout-all, forget/reset password, username availability check
- **User** (`/api/user`): profile get/update, username change, role/onboarding, seller enable/disable/status/analytics, saved pieces, public profile by username
- **Media** (`/api/media`): S3 presign (image + video)
- **Pieces / Posts** (`/api/pieces`, `/api/posts`): create/edit/detail (enriched with author, likes, comments, series), comments GET, related posts
- **Social** (`/api`): follow/unfollow, like/unlike, save/unsave, comment create
- **Feeds** (`/api/feed`): following, explore, for-you — cursor-paginated
- **Series** (`/api/series`, `/api/users/:username/series`): group a user's pieces into a series

Full endpoint reference with request/response shapes: [`docs/API.md`](docs/API.md).

Responses: `{ "success": true, "message": "...", "data": ... }` or `{ "success": false, "message": "..." }`.

## Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```
