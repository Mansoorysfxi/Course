"""Reads the database connection string from this process's environment.

See this exercise's own INSTRUCTIONS.md, Setup section, for what
DATABASE_URL should look like and why it deliberately points at a
*separate* database from the real `project/questlog/backend`. Kept in its
own tiny file, rather than inline in database.py, purely so main.py and
Alembic's env.py can both import just this one value without importing
anything else.
"""

import os

# Deliberately a DIFFERENT database name ("questlog_exercise04") from the
# real capstone's "questlog" database -- this exercise is a separate,
# disposable practice copy of the backend, and reusing the exact same
# database name/URL as the real project/questlog/backend would risk this
# exercise's migrations and seed data colliding with (or being wiped by)
# the capstone's own Lesson 00 "drop and recreate questlog" step, or vice
# versa. See INSTRUCTIONS.md's Setup section for the one extra `CREATE
# DATABASE` command this requires versus the main capstone.
DEFAULT_DATABASE_URL = (
    "postgresql+asyncpg://questlog:questlog_dev_password@localhost:5432/questlog_exercise04"
)

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
