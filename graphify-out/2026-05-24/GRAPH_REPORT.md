# Graph Report - .  (2026-05-24)

## Corpus Check
- Corpus is ~8,587 words - fits in a single context window. You may not need a graph.

## Summary
- 244 nodes · 392 edges · 29 communities (20 shown, 9 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Authentication Controllers and Logic|Authentication Controllers and Logic]]
- [[_COMMUNITY_Redis Sessions and OTP Limits|Redis Sessions and OTP Limits]]
- [[_COMMUNITY_Auth Database Access|Auth Database Access]]
- [[_COMMUNITY_Service Diagnostics and SMTP|Service Diagnostics and SMTP]]
- [[_COMMUNITY_Authentication Routes|Authentication Routes]]
- [[_COMMUNITY_User Activity Role Recalculation|User Activity Role Recalculation]]
- [[_COMMUNITY_User Management Logic|User Management Logic]]
- [[_COMMUNITY_App Setup and Error Handling|App Setup and Error Handling]]
- [[_COMMUNITY_Request Auth and JWT Verification|Request Auth and JWT Verification]]
- [[_COMMUNITY_Database Config and Sessions|Database Config and Sessions]]
- [[_COMMUNITY_Alembic Database Migrations|Alembic Database Migrations]]
- [[_COMMUNITY_Shared Configuration Package|Shared Configuration Package]]
- [[_COMMUNITY_Graphify Integration Assets|Graphify Integration Assets]]
- [[_COMMUNITY_Session Services Initialization|Session Services Initialization]]
- [[_COMMUNITY_Main Src Package Initialization|Main Src Package Initialization]]
- [[_COMMUNITY_Shared Project Constants|Shared Project Constants]]
- [[_COMMUNITY_Shared Package Initialization|Shared Package Initialization]]
- [[_COMMUNITY_Notification Package Initialization|Notification Package Initialization]]
- [[_COMMUNITY_Email Template Package Initialization|Email Template Package Initialization]]
- [[_COMMUNITY_API Response Messages|API Response Messages]]

## God Nodes (most connected - your core abstractions)
1. `AppError` - 25 edges
2. `get_redis_client()` - 18 edges
3. `Base` - 12 edges
4. `_respond()` - 12 edges
5. `success_response()` - 9 edges
6. `_issue_session_and_tokens()` - 9 edges
7. `otp_generate()` - 9 edges
8. `get_or_create_user_from_google()` - 9 edges
9. `recalculate_user_role()` - 9 edges
10. `get_logger()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Activity-Based User Roles Design` --references--> `UserActivityCount`  [INFERRED]
  docs/ACTIVITY_ROLES.md → src/shared/models/user_activity_count.py
- `Activity-Based User Roles Design` --references--> `increment_activity()`  [EXTRACTED]
  docs/ACTIVITY_ROLES.md → src/modules/user/user_activity_dao.py
- `Activity-Based User Roles Design` --references--> `recalculate_user_role()`  [EXTRACTED]
  docs/ACTIVITY_ROLES.md → src/modules/user/role_from_activity.py
- `main()` --calls--> `check_db_connection()`  [EXTRACTED]
  run.py → src/shared/config/database.py
- `main()` --calls--> `check_redis_connection()`  [EXTRACTED]
  run.py → src/shared/config/redis_client.py

## Hyperedges (group relationships)
- **User Roles and Activity-Based Recalculation Flow** — docs_activity_roles_design, user_user_activity_dao_increment_activity, user_role_from_activity_recalculate_user_role, models_user_activity_count_useractivitycount [INFERRED 0.85]

## Communities (29 total, 9 thin omitted)

### Community 0 - "Authentication Controllers and Logic"
Cohesion: 0.08
Nodes (43): forget_password(), google_callback(), google_redirect(), _hash_password(), _hash_refresh_secret(), _issue_session_and_tokens(), login(), otp_generate() (+35 more)

### Community 1 - "Redis Sessions and OTP Limits"
Cohesion: 0.11
Nodes (24): logout(), logout_all(), create_state(), Store state in Redis, return state string., get_redis_client(), Return the global Redis client (create if needed)., acquire_lock(), check_resend_limit() (+16 more)

### Community 2 - "Auth Database Access"
Cohesion: 0.11
Nodes (11): Auth-related DB access: users (by email, create), accounts, password_reset_token, Base, Declarative base for all models., DeclarativeBase, Account, Account model (OAuth/linked accounts)., SQLAlchemy models - import all so Alembic can discover them., Session model (optional DB session; app may use Redis only). (+3 more)

### Community 3 - "Service Diagnostics and SMTP"
Cohesion: 0.11
Nodes (18): check_db_connection(), Run SELECT 1 to verify DB is reachable., check_redis_connection(), close_redis(), Single Redis connection client., Close the Redis connection (call on shutdown)., Ping Redis to verify it's reachable., Send email via SMTP (from env). (+10 more)

### Community 4 - "Authentication Routes"
Cohesion: 0.15
Nodes (18): _apply_cookie_ops(), forget_password(), login(), logout(), logout_all(), otp_generate(), otp_resend(), Auth Blueprint: /api/auth. (+10 more)

### Community 5 - "User Activity Role Recalculation"
Cohesion: 0.17
Nodes (15): Activity-Based User Roles Design, API Reference Documentation, Project Setup Instructions, UserActivityCount, Flask REST API Project, compute_role_from_counts(), Compute user role(s) from activity counts; recalculate and persist. Multiple rol, Return list of roles for every category where user is active (count >= threshold (+7 more)

### Community 6 - "User Management Logic"
Cohesion: 0.22
Nodes (14): get_me(), getall(), User controller: request/response; calls DAO; returns (data, status)., Return role as array when multiple (comma-separated), else as string or None., Protected: return { users, count }., Protected: return current user profile (for onboarding check and profile)., Protected: set/update current user role (onboarding or toggle). Role is primary, _role_for_response() (+6 more)

### Community 7 - "App Setup and Error Handling"
Cohesion: 0.25
Nodes (8): Global exception handler: AppError -> status_code + message; else 500 + generic, register_error_handler(), Flask app: middleware (CORS, JSON), blueprints /api/auth and /api/user, global e, error_response(), internal_error_response(), Success and error response helpers - same shape as reference., Return JSON: { success: false, message }., Generic 500 response.

### Community 8 - "Request Auth and JWT Verification"
Cohesion: 0.20
Nodes (8): auth_required(), Bearer JWT + Redis session check; set g.user = { id, session_id }., Decorator: verify JWT, check Redis session exists, set g.user., JWT sign and verify using secret from env., Sign payload (e.g. sub, sessionId) with expiry; return JWT string., Verify JWT and return payload or None if invalid/expired., sign_access_token(), verify_access_token()

### Community 9 - "Database Config and Sessions"
Cohesion: 0.33
Nodes (5): get_db(), SQLAlchemy 2.0 engine, session factory, and declarative Base., Remove query params that psycopg2 does not accept (e.g. pgbouncer=true from Supa, Yield a DB session; caller must close/commit/rollback., _sanitize_database_url()

### Community 10 - "Alembic Database Migrations"
Cohesion: 0.60
Nodes (4): get_url(), Alembic environment: uses src shared database and models (no Flask)., run_migrations_offline(), run_migrations_online()

## Knowledge Gaps
- **2 isolated node(s):** `Graphify Workflow`, `Graphify Rules`
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Authentication Controllers and Logic` to `Redis Sessions and OTP Limits`, `Service Diagnostics and SMTP`, `User Management Logic`, `App Setup and Error Handling`, `Request Auth and JWT Verification`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `User` connect `Auth Database Access` to `Authentication Controllers and Logic`, `User Management Logic`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `Base` connect `Auth Database Access` to `Database Config and Sessions`, `Alembic Database Migrations`, `User Activity Role Recalculation`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Base` (e.g. with `User` and `UserActivityCount`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Entry: load env (by FLASK_ENV), connect DB + Redis, then run Flask app. Exit on`, `WSGI entry for gunicorn (production).`, `Alembic environment: uses src shared database and models (no Flask).` to the rest of the system?**
  _80 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Authentication Controllers and Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.08067375886524823 - nodes in this community are weakly interconnected._
- **Should `Redis Sessions and OTP Limits` be split into smaller, more focused modules?**
  _Cohesion score 0.11076923076923077 - nodes in this community are weakly interconnected._