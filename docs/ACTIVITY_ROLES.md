# Activity-based user roles

User role(s) can be set at onboarding and **updated from activity** on the platform. Role is primary interest only (no permission checks).

## Flow

- **Onboarding:** First-time users choose role via PATCH `/api/user/me` (e.g. `artist`, `collector`, `enthusiast`, or comma-separated like `artist,collector`).
- **Activity:** When you add features for posting art, purchasing, or saving/favoriting, wire them to the activity pipeline so role can be recalculated.
- **Recalc:** After each relevant action and/or via the periodic CLI job.

## Integration: post / purchase / save handlers

When you implement **artwork/post creation**, **purchase/order completion**, or **save/favorite**:

1. **Increment the count** for the current user and activity kind:
   - After creating a post/artwork: `increment_activity(db, user_id, "post")`
   - After completing a purchase: `increment_activity(db, user_id, "purchase")`
   - After adding a save/favorite: `increment_activity(db, user_id, "save")`

2. **Recalculate role** so `user.role` is updated from counts:
   - `recalculate_user_role(db, user_id)`

**Imports:**

```python
from src.modules.user.user_activity_dao import increment_activity
from src.modules.user.role_from_activity import recalculate_user_role
```

Use activity kinds `"post"`, `"purchase"`, or `"save"` (see `src.shared.constants.ACTIVITY_KINDS`).

Example (in a future “create post” handler):

```python
# after creating the post and committing
increment_activity(db, current_user_id, "post")
recalculate_user_role(db, current_user_id)
```

## Periodic job

Run role recalculation for all users (e.g. daily via cron):

```bash
FLASK_APP=src.app:create_app flask recalc-roles
```

This uses activity counts in `user_activity_counts` and updates `users.role` (single or comma-separated, e.g. `artist,collector`) when the computed role differs.

## Multiple roles

If a user is active in more than one category (e.g. both posting and buying), they get all applicable roles. Stored as comma-separated in `users.role`; API returns `role` as an array when multiple (e.g. `["artist", "collector"]`).
