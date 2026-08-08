"""Every /api/auth route -- new in Module 07. See
lessons/06-building-signup-login.md for the full line-by-line walkthrough
of `signup` and `login`, and lessons/07-protecting-routes-with-dependencies.md
for `me`, this file's one genuinely *protected* route, included here
mostly as a small, self-contained example of `CurrentUser` in action
before app/routers/quests.py leans on it for real.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import repository
from app.dependencies import CurrentUser, DbSession
from app.models import Token, UserCreate, UserPublic
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, session: DbSession):
    """Creates a new account. Note this route takes zero authentication --
    it has no `current_user: CurrentUser` parameter, unlike everything in
    app/routers/quests.py -- which is exactly right: you cannot be
    required to already be logged in before you're allowed to create the
    account you'd log in *with*. Not every route in an API should be
    protected; lessons/07-protecting-routes-with-dependencies.md's
    "which routes should NOT require a token" section names signup and
    login as the two canonical examples.
    """
    existing = await repository.get_user_by_email(session, data.email)
    if existing is not None:
        # Deliberately a plain 400, not 409 ("Conflict") -- see
        # lessons/06-building-signup-login.md's aside on why this course
        # keeps this one simple; a real product might use 409 here and
        # would also think hard about whether revealing "this email is
        # already registered" at all is itself a small information leak
        # (it lets someone probe which emails have accounts) -- a
        # trade-off worth knowing about even though this app accepts it.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with that email already exists.",
        )
    user = await repository.create_user(session, data.email, hash_password(data.password))
    return UserPublic(id=user.id, email=user.email, created_at=user.created_at.isoformat())


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
):
    """Exchanges an email + password for a JWT access token.

    `OAuth2PasswordRequestForm` (imported from `fastapi.security`) is a
    FastAPI-provided dependency that reads `application/x-www-form-urlencoded`
    form fields named `username` and `password` -- **not** JSON, unlike
    every other route body in this backend -- because this is the one
    endpoint deliberately shaped to match the OAuth2 "Resource Owner
    Password Credentials" grant's own wire format (see
    lessons/05-oauth2-conceptual.md), which is what lets FastAPI's
    `/docs` "Authorize" button work against this route with zero extra
    configuration, and is why this backend needed to add `python-multipart`
    to requirements.txt (see lessons/00-setup.md) -- parsing form data is
    a separate job from parsing JSON, handled by a separate package.
    `form_data.username` is genuinely this user's *email* here, not a
    separate username field this app doesn't have -- see
    lessons/06-building-signup-login.md's box on that naming mismatch.
    """
    user = await repository.get_user_by_email(session, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        # One error, both causes ("no such account" and "wrong password"),
        # for the exact same reason app/dependencies.py's
        # `get_current_user` collapses three token failures into one
        # response: telling a caller *which* one was wrong tells an
        # attacker whether a given email even has an account at all.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserPublic)
async def me(current_user: CurrentUser):
    """Returns whoever the caller's own token identifies them as. Exists
    partly as a genuinely useful "am I logged in, and as whom" endpoint
    the frontend calls once on load (see
    frontend/src/context/AuthContext.tsx), and partly as the smallest
    possible worked example of a protected route: the *entire* mechanism
    is the `current_user: CurrentUser` parameter below -- nothing else in
    this function does any authentication work at all."""
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
    )
