# Graph Report - Server  (2026-05-24)

## Corpus Check
- 56 files · ~9,560 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 366 nodes · 504 edges · 37 communities (26 shown, 11 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4ea1ea37`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]

## God Nodes (most connected - your core abstractions)
1. `AppError` - 25 edges
2. `get_redis_client()` - 18 edges
3. `Endpoints (copy into Postman)` - 15 edges
4. `Base` - 12 edges
5. `_respond()` - 12 edges
6. `Project Setup` - 11 edges
7. `success_response()` - 9 edges
8. `_issue_session_and_tokens()` - 9 edges
9. `otp_generate()` - 9 edges
10. `get_or_create_user_from_google()` - 9 edges

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

## Communities (37 total, 11 thin omitted)

### Community 0 - "Authentication Controllers and Logic"
Cohesion: 0.07
Nodes (48): forget_password(), google_callback(), google_redirect(), _hash_password(), _hash_refresh_secret(), _issue_session_and_tokens(), login(), logout() (+40 more)

### Community 1 - "Redis Sessions and OTP Limits"
Cohesion: 0.12
Nodes (22): otp_generate(), otp_resend(), get_redis_client(), Return the global Redis client (create if needed)., Send email via SMTP (from env)., Send email with given HTML body. Returns True on success., send_email(), acquire_lock() (+14 more)

### Community 2 - "Auth Database Access"
Cohesion: 0.11
Nodes (12): Auth-related DB access: users (by email, create), accounts, password_reset_token, Base, Declarative base for all models., DeclarativeBase, Account, Account model (OAuth/linked accounts)., SQLAlchemy models - import all so Alembic can discover them., Session model (optional DB session; app may use Redis only). (+4 more)

### Community 3 - "Service Diagnostics and SMTP"
Cohesion: 0.09
Nodes (25): check_db_connection(), Run SELECT 1 to verify DB is reachable., check_redis_connection(), close_redis(), Single Redis connection client., Close the Redis connection (call on shutdown)., Ping Redis to verify it's reachable., Global exception handler: AppError -> status_code + message; else 500 + generic (+17 more)

### Community 4 - "Authentication Routes"
Cohesion: 0.10
Nodes (24): _apply_cookie_ops(), forget_password(), login(), logout(), logout_all(), otp_generate(), otp_resend(), Auth Blueprint: /api/auth. (+16 more)

### Community 5 - "User Activity Role Recalculation"
Cohesion: 0.10
Nodes (28): Activity-Based User Roles Design, API Reference Documentation, Project Setup Instructions, Flask REST API Project, compute_role_from_counts(), Compute user role(s) from activity counts; recalculate and persist. Multiple rol, Return list of roles for every category where user is active (count >= threshold, Load activity counts, compute role(s), persist as comma-separated if different. (+20 more)

### Community 6 - "User Management Logic"
Cohesion: 0.06
Nodes (34): Auth – Forget password, Auth – Google OAuth (browser), Auth – Login, Auth – Logout, Auth – Logout all (protected), Auth – OTP generate, Auth – OTP resend, Auth – Refresh (+26 more)

### Community 7 - "App Setup and Error Handling"
Cohesion: 0.10
Nodes (20): 1. Clone and enter the project, 2. Virtual environment, 3. Install dependencies, 4. Environment variables, 5. Database, 6. Redis, 7. Run the application, 8. Verify (+12 more)

### Community 8 - "Request Auth and JWT Verification"
Cohesion: 0.14
Nodes (13): 1. Environment variables, 2. Saving the access token, 3. Cookies (refresh / logout), 4. Suggested flow for testing, API Documentation (Postman-ready), code:javascript (var json = pm.response.json();), code:json ({), code:json ({) (+5 more)

### Community 9 - "Database Config and Sessions"
Cohesion: 0.17
Nodes (11): API, code:bash (python3 -m venv .venv), code:block2 (project_root/), code:bash (alembic upgrade head), Env, Flask REST API, Layout, Migrations (+3 more)

### Community 10 - "Alembic Database Migrations"
Cohesion: 0.60
Nodes (4): get_url(), Alembic environment: uses src shared database and models (no Flask)., run_migrations_offline(), run_migrations_online()

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (8): Activity-based user roles, code:python (from src.modules.user.user_activity_dao import increment_act), code:python (# after creating the post and committing), code:bash (FLASK_APP=src.app:create_app flask recalc-roles), Flow, Integration: post / purchase / save handlers, Multiple roles, Periodic job

### Community 30 - "Community 30"
Cohesion: 0.29
Nodes (6): info, description, name, _postman_id, schema, item

### Community 31 - "Community 31"
Cohesion: 0.29
Nodes (6): id, name, _postman_exported_at, _postman_exported_using, _postman_variable_scope, values

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (6): info, description, name, _postman_id, schema, item

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (6): id, name, _postman_exported_at, _postman_exported_using, _postman_variable_scope, values

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (5): get_db(), SQLAlchemy 2.0 engine, session factory, and declarative Base., Remove query params that psycopg2 does not accept (e.g. pgbouncer=true from Supa, Yield a DB session; caller must close/commit/rollback., _sanitize_database_url()

## Knowledge Gaps
- **80 isolated node(s):** `_postman_id`, `name`, `description`, `schema`, `item` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Authentication Controllers and Logic` to `Redis Sessions and OTP Limits`, `Service Diagnostics and SMTP`, `Authentication Routes`, `User Activity Role Recalculation`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `User` connect `Auth Database Access` to `Authentication Controllers and Logic`, `User Activity Role Recalculation`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `Base` connect `Auth Database Access` to `Alembic Database Migrations`, `Community 36`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Base` (e.g. with `User` and `UserActivityCount`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Entry: load env (by FLASK_ENV), connect DB + Redis, then run Flask app. Exit on`, `WSGI entry for gunicorn (production).`, `_postman_id` to the rest of the system?**
  _158 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Authentication Controllers and Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.07256894049346879 - nodes in this community are weakly interconnected._
- **Should `Redis Sessions and OTP Limits` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._