"""Application configuration, read from environment variables (and, for
local development, a `.env` file) via **pydantic-settings** -- confirmed
during this module's research (August 2026) as the current, officially
recommended way to manage settings in a FastAPI project, replacing
Module 06's plain `os.environ.get(...)` approach now that this module
introduces genuine secrets (a JWT signing key) that must never be
hardcoded. See lessons/11-secrets-config-and-logging.md for the full
explanation of every line below, and lessons/00-setup.md for how the
`.env` file this reads is created.

Distinct from Module 06's `config.py`, which was a single hardcoded
`DEFAULT_DATABASE_URL` constant plus one `os.environ.get()` call -- that
approach doesn't scale to "several settings, one of which is a secret that
must exist and must never be committed to Git," which is exactly this
module's situation.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """One field per configuration value the app needs. pydantic-settings
    reads each field's value, in order of priority, from: (1) a real
    process environment variable of the same name (case-insensitive by
    default), (2) the `.env` file named below, (3) the field's own default
    here, if any. A field with **no default** (`secret_key` below) makes
    pydantic-settings raise a clear validation error at startup if it's
    missing anywhere -- "fail fast and loud," not "silently run with
    `None` and break mysteriously three requests later." See
    lessons/11-secrets-config-and-logging.md's "why no default for
    SECRET_KEY" box.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # A sensible local-dev default -- identical value to Module 06's
    # DEFAULT_DATABASE_URL, just now expressed as a Settings field instead
    # of a module-level constant, so every setting lives in one place.
    database_url: str = (
        "postgresql+asyncpg://questlog:questlog_dev_password@localhost:5432/questlog"
    )

    # No default on purpose -- see the class docstring above. Every learner
    # generates their own random value in lessons/00-setup.md; there is no
    # "sensible default" for a secret, because a shared default would not
    # be a secret at all.
    secret_key: str

    # The signing algorithm JWTs use (lessons/04-jwt-structure-in-depth.md
    # explains exactly what this controls). HS256 is this course's choice --
    # see that lesson for why.
    algorithm: str = "HS256"

    # How long a freshly-issued access token stays valid, in minutes.
    access_token_expire_minutes: int = 60

    # A single comma-separated string, not a Python list -- environment
    # variables are always plain text, so a list has to be encoded into one
    # string somehow. The `cors_origins` property below is what actually
    # turns this into a real Python list any code that wants origins should
    # use. See lessons/10-cors-in-depth.md.
    #
    # `validation_alias="CORS_ORIGINS"` -- without this, pydantic-settings
    # would look for an environment variable matching this *field's own
    # name* (`CORS_ORIGINS_RAW`), which is an internal implementation
    # detail this app's `.env` file shouldn't have to know or spell
    # correctly. The alias is the env var name a human actually sets;
    # `cors_origins_raw` is just what this class calls it internally,
    # before the property below turns it into a real list.
    cors_origins_raw: str = Field(
        default="http://localhost:5173", validation_alias="CORS_ORIGINS"
    )

    @property
    def cors_origins(self) -> list[str]:
        """Splits `cors_origins_raw` on commas and strips whitespace from
        each piece, so `CORS_ORIGINS=http://localhost:5173, http://localhost:4173`
        in a `.env` file works whether or not there's a space after the
        comma."""
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """`@lru_cache` (Module 01's decorator lesson, applied for real) means
    `Settings()` -- which reads the environment and `.env` file -- only
    actually runs once per process, the first time this function is
    called; every later call instantly returns that same cached object
    instead of re-reading the environment. This matters because
    `Settings()` doing real file I/O (reading `.env`) on every single
    request, potentially from several different modules that each import
    `get_settings`, would be wasteful and pointless -- configuration
    doesn't change while the app is running."""
    return Settings()


# A module-level instance, resolved once at import time, so the rest of
# this backend can write `from app.config import settings` and use
# `settings.database_url` etc. directly, exactly the same ergonomics as
# Module 06's plain `DATABASE_URL` constant -- just backed by real
# validation now instead of a bare `os.environ.get()`.
settings = get_settings()

# Kept as a plain module-level name too, so app/database.py and
# alembic/env.py -- both written in Module 06 against a `DATABASE_URL`
# constant -- need zero changes despite config.py's internals being
# rewritten. See lessons/11-secrets-config-and-logging.md's "the contract
# doesn't change" box for why this small compatibility shim is worth
# keeping rather than "cleaning up."
DATABASE_URL = settings.database_url
