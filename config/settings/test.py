from .base import *  # noqa: F401,F403

DEBUG = False

# In-memory SQLite for fast test runs.
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
