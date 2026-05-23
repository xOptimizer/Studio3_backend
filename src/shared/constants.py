"""Shared constants (e.g. user roles, activity kinds).

User role is primary interest / primary use only (artist, collector, enthusiast).
It is not used for permission checks—artists can purchase, collectors can post.
"""

ALLOWED_ROLES = ("artist", "collector", "enthusiast")

# Activity kinds for role-from-activity (increment_activity).
ACTIVITY_KINDS = ("post", "purchase", "save")
