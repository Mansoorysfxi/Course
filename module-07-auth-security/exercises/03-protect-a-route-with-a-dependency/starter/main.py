"""Exercise 03 -- Protect a Route with a Dependency.

A small, standalone "vault" API -- NOT QuestLog. See INSTRUCTIONS.md for
the full task. Three things are marked `# TODO`; everything else
(including /login) is already working, using exactly the patterns
Lessons 02/04/06 already taught.

Run with:  uvicorn main:app --reload
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

SECRET_KEY = "exercise-03-practice-secret-never-reuse-this-32bytesplus"
ALGORITHM = "HS256"

app = FastAPI(title="Vault API (Exercise 03)")


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# A plain in-memory dict standing in for a real database, on purpose --
# this exercise is about the *dependency* pattern, not persistence.
# Seeded once, at import time, with one user: alice / wonderland.
USERS: dict[str, dict] = {
    "alice": {"username": "alice", "hashed_password": _hash("wonderland")},
}


def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    claims = {"sub": username, "iat": now, "exp": now + timedelta(minutes=30)}
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# --- TODO 1: create an OAuth2PasswordBearer instance, pointed at this
# app's own "/login" route (see Lesson 07's own oauth2_scheme). ---
oauth2_scheme = None  # TODO: replace with a real OAuth2PasswordBearer(...)


# --- TODO 2: implement this dependency. It should:
#   1. Take `token: Annotated[str, Depends(oauth2_scheme)]`.
#   2. Call decode_access_token(token); catch jwt.InvalidTokenError and
#      raise a 401 (with headers={"WWW-Authenticate": "Bearer"}).
#   3. Look up the `sub` claim in USERS; if it's missing or not found,
#      raise the SAME 401 (do not distinguish the two cases in the
#      response -- see Lesson 07's "one error, three failure reasons").
#   4. Return the matching entry from USERS (a dict with "username").
async def get_current_user(): # TODO: add the right parameter(s) here
    raise NotImplementedError


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = USERS.get(form_data.username)
    if user is None or not _verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user["username"]), "token_type": "bearer"}


@app.get("/public")
async def public():
    """Deliberately requires no authentication at all -- contrast this
    with /secret below."""
    return {"message": "Anyone can see this, logged in or not."}


# --- TODO 3: add whatever parameter is needed to make this route
# require a valid token (using get_current_user, above), then return
# {"message": f"Hello, {username}! The secret number is 42."}
@app.get("/secret")
async def secret():
    raise NotImplementedError
