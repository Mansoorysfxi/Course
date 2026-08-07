"""Reads the database connection string from this process's environment.

See lessons/00-setup.md for what DATABASE_URL should look like and
lessons/06-sqlalchemy-with-fastapi.md for exactly how `engine` (built from
this value) is used. Kept in its own tiny file, rather than inline in
database.py, purely so main.py and Alembic's env.py can both import just
this one value without importing anything else.
"""

import os

# A sensible local-dev default so `uvicorn app.main:app --reload` still
# works immediately after following lessons/00-setup.md's exact steps,
# without forcing every learner to set an environment variable by hand
# first. A real deployment (Module 11) would never rely on a default like
# this -- it would set DATABASE_URL explicitly, to a real production
# database, every time.
DEFAULT_DATABASE_URL = (
    "postgresql+asyncpg://questlog:questlog_dev_password@localhost:5432/questlog"
)

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
