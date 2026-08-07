"""Exercise 03 -- Protect a Route with a Dependency (reference solution).

See INSTRUCTIONS.md for the full task and Lesson 07 for the full
explanation of the pattern this file applies.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "exercise-03-practice-secret-never-reuse-this-32bytesplus"
ALGORITHM = "HS256"

app = FastAPI(title="Vault API (Exercise 03)")


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


USERS: dict[str, dict] = {
    "alice": {"username": "alice", "hashed_password": _hash("wonderland")},
}


def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    claims = {"sub": username, "iat": now, "exp": now + timedelta(minutes=30)}
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# TODO 1, solved: an OAuth2PasswordBearer pointed at this app's own
# "/login" route. tokenUrl only affects the auto-generated OpenAPI docs'
# "Authorize" button -- it has no effect on this dependency's runtime
# behavior (Lesson 07).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# TODO 2, solved: mirrors app/dependencies.py's real get_current_user
# (Lesson 07) almost exactly -- the only real difference is looking the
# user up in a plain dict instead of querying a database.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise credentials_exception

    username = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = USERS.get(username)
    if user is None:
        raise credentials_exception

    return user


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
    return {"message": "Anyone can see this, logged in or not."}


# TODO 3, solved: the ENTIRE mechanism protecting this route is the
# `current_user: Annotated[dict, Depends(get_current_user)]` parameter
# below -- nothing in this function's body manually checks for a token.
@app.get("/secret")
async def secret(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"message": f"Hello, {current_user['username']}! The secret number is 42."}
