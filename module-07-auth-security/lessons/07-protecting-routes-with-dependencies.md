# Lesson 07 — Protecting Routes with Dependencies

## What you'll learn

- What a FastAPI **security scheme** is, and exactly what `OAuth2PasswordBearer` does (and doesn't do).
- How `get_current_user` turns a raw `Authorization` header into a real, verified `User` — and what happens, precisely, for each of three different ways a token can be invalid.
- How one new dependency (`CurrentUser`) makes an entire route "protected," and why a route with no such parameter is reachable by anyone.
- How authorization (Lesson 01) gets enforced concretely: every quest query now requires an `owner_id`, and why a missing/wrong-owner quest returns `404`, never `403`.
- Why the frontend's `ProtectedRoute` is a UX convenience, not the real security boundary — and how to prove that to yourself directly.

## Why this matters

Lesson 06 built the ability to log in. This lesson is what actually makes
that login *matter* anywhere else in the app: without this lesson's
work, `/api/quests` would still be wide open to anyone, logged in or not,
exactly as it was through Module 06. This is the lesson where Lesson 01's
two concepts (authentication, authorization) both become real, enforced
code for the first time.

## Prerequisites

Lesson 01 (authn vs. authz vocabulary), Lesson 04 (what
`decode_access_token` actually verifies), Lesson 06 (where the token this
lesson checks actually comes from), Module 05, Lesson 04 (FastAPI's
`Depends()` mechanism — this lesson assumes you already understand how a
dependency function gets called and its return value injected; it does
not re-explain `Depends()` from scratch).

## The concept, explained simply

Recall the security-guard analogy from Lesson 01: authentication is the
guard checking a badge is real; authorization is each individual door
deciding whether *that specific, already-verified* badge-holder may pass.
This lesson builds both, as FastAPI dependencies — recall from Module 05
that a dependency is a plain function FastAPI calls *before* your route's
own code runs, injecting whatever it returns as a parameter. This
lesson's `get_current_user` is the "guard checking the badge" dependency;
`get_quest_or_404`'s owner check is the "does this specific door open for
this specific badge" logic — and, crucially, they are **two separate
functions**, exactly mirroring Lesson 01's insistence that authentication
and authorization are separate steps, never one merged check.

## The details

### `OAuth2PasswordBearer` — reading the header, nothing more

`backend/app/dependencies.py`:

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
```

This creates a **security scheme** — a FastAPI object that knows how to
extract credentials from a request in one specific, standard way. This
particular one does exactly two things, and no more:

1. Reads the `Authorization` header and, if it's shaped like
   `Bearer <token>`, extracts just the `<token>` part as a plain string.
2. If that header is **missing entirely**, raises a `401` itself,
   automatically — before any of your own code runs.

**What it explicitly does NOT do:** check whether the token is genuine,
unexpired, or names a real user. It has no idea what a JWT even is — it
would extract the string `"garbage"` from a header reading `Bearer
garbage` just as happily as a real token, and hand that string onward.
All of the *actual verification* is the next function's job.

`tokenUrl="/api/auth/login"` doesn't affect this scheme's runtime
behavior at all — it exists purely so FastAPI's auto-generated OpenAPI
docs (Module 05, Lesson 07) know which endpoint's "Authorize" button in
`/docs` should collect a username/password and exchange them for a token,
letting you try protected routes directly from the interactive docs UI.

### `get_current_user` — the real verification

```python
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DbSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = await repository.get_user_by_id(session, user_id)
    if user is None:
        raise credentials_exception
    return user
```

**Line by line, and the "one error, three failure reasons" design:**

- `token: Annotated[str, Depends(oauth2_scheme)]` — FastAPI runs
  `oauth2_scheme` first (Module 05's dependency-chaining mechanism), so
  by the time this function's own body starts, the `Authorization` header
  has already been confirmed present and Bearer-shaped.
- `decode_access_token(token)` (Lesson 04) — verifies the signature and
  expiry. `InvalidTokenError` (PyJWT's base exception class — covering a
  forged signature, a malformed token, *and* an expired one, since
  `ExpiredSignatureError` is itself a subclass of it) is caught, and
  turned into the exact same `401` regardless of which specific thing was
  wrong with the token.
- `payload.get("sub")` — pulls the user id claim back out. If it's
  somehow missing (it never should be, since `create_access_token` always
  sets it — but defensive code doesn't assume its own invariants hold
  forever), the same `401` fires.
- `repository.get_user_by_id(session, user_id)` — the token might be
  perfectly genuine and unexpired, but the account it names could have
  been deleted *after* the token was issued. Same `401` again.

**Why one error for three different causes:** telling a caller
*specifically* "your token expired" vs. "your token is forged" vs. "that
account no longer exists" hands an attacker a free diagnostic tool for
probing this system — Lesson 01 already introduced this "one error,
multiple causes" principle for login; this is the same principle applied
to token verification.

### `CurrentUser` — the parameter that makes a route "protected"

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

Every route that writes `current_user: CurrentUser` in its signature
triggers this entire dependency chain (`oauth2_scheme` →
`get_current_user`) before that route's own body ever executes. **This
one parameter is the entire mechanism.** Compare `app/routers/quests.py`
against Module 06's version of the same file: every route gained exactly
one new parameter, `current_user: CurrentUser`, and nothing else about
how FastAPI wires them up needed to change. A route with no such
parameter — like `POST /api/auth/signup` (Lesson 06) — is reachable by
anyone, token or not, which is exactly correct for that specific route
(you cannot be required to already be logged in to create the account
you'd log in with).

### Authorization: `get_quest_or_404`, and why 404 not 403

```python
async def get_quest_or_404(quest_id: str, session: DbSession, current_user: CurrentUser) -> Quest:
    quest = await repository.get_quest(session, quest_id, owner_id=current_user.id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quest with id '{quest_id}'")
    return quest
```

And in `app/repository.py`, `get_quest`'s actual query:

```python
stmt = (
    select(QuestRow)
    .options(selectinload(QuestRow.quest_line))
    .where(QuestRow.id == quest_id, QuestRow.owner_id == owner_id)
)
```

**The key design decision:** both conditions (`id == quest_id` AND
`owner_id == owner_id`) are combined in **one** `WHERE` clause, not
checked as two separate steps ("fetch the quest, then separately check if
`quest.owner_id == current_user.id`"). This means a quest that exists but
belongs to someone else produces the **exact same result** — `None`, and
therefore a `404` — as a quest that doesn't exist at all. HTTP's own
`403 Forbidden` status code would be a tempting, seemingly more "honest"
choice here — but returning `403` would leak real information: it would
confirm to a caller that a quest with that specific id genuinely exists,
just belongs to someone else, letting an attacker probe for valid quest
ids one guess at a time even without ever seeing their contents. This
specific mistake — accidentally revealing that a resource *exists* via a
different response, even while correctly denying access to its *contents*
— is a real, named category of vulnerability called **IDOR** (Insecure
Direct Object Reference), and combining both conditions into a single
query is what closes it off here, for free, rather than requiring a
second, separate defensive check.

Every other quest route (`list_quests`, `create_quest`, `update_quest`,
`delete_quest`, `quest_line_stats` — all in `app/repository.py`) follows
the identical pattern: `owner_id` is a required parameter, always sourced
from `current_user.id`, never from anything a client could supply
directly (there is no `owner_id` field a request body could set — check
`QuestCreate`/`QuestUpdate` in `app/models.py` and confirm this for
yourself).

### The frontend's `ProtectedRoute` — and why it isn't the real lock

`frontend/src/components/ProtectedRoute.tsx`:

```tsx
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
```

This exists purely for **user experience** — redirecting someone who
isn't logged in to `/login` instead of showing them a page that
immediately fails every request it makes. It is genuinely useful, and
genuinely not a security boundary: nothing stops a determined user from
opening their browser's developer console and calling
`fetch("http://localhost:8000/api/quests")` directly, completely
bypassing this component, React, and the entire frontend. **Prove this to
yourself:** with the backend running and *not* logged in anywhere, open
your browser's console on any page and run exactly that `fetch()` call —
you'll get the same `401` the backend always produces, because the *real*
lock is `CurrentUser` on the backend, checked on every single request no
matter where it came from. Exercise 04 has you do this formally, including
attempting to reach a *specific quest id* belonging to a different
account, and confirming the backend still returns `404` even when called
directly, with no frontend involved at all.

## Common mistakes & gotchas

- **Adding `current_user: CurrentUser` to a route but never actually
  using it for anything.** This still protects the route (any request
  without a valid token still gets rejected before the route body runs)
  — `app/routers/quests.py`'s single-quest `GET` route is a real example:
  it has no explicit `current_user` parameter of its own at all, because
  `get_quest_or_404` (its own dependency) already requires and uses one.
  The presence of `Depends(get_quest_or_404)` in that route's signature is
  what protects it, transitively — you can't reach that dependency's
  successful return value without first passing through its own,
  authenticated, owner-checked query.
- **Checking ownership as a second step after fetching a resource, in
  Python, instead of in the query's own `WHERE` clause.** Functionally
  similar in the success case, but see the IDOR discussion above for why
  the query-level approach is the one that avoids leaking a resource's
  existence through a different response code.
- **Trusting the frontend's `ProtectedRoute` as "the" security check.**
  See the box above — it's UX, not enforcement. If you ever find yourself
  writing an authorization rule *only* in frontend code, that rule
  doesn't actually exist from a security standpoint.

## How this connects

Lesson 01 named authentication and authorization; this lesson is where
both become real, running code, completing this module's core "make
QuestLog multi-user" arc started in Lesson 02. Lessons 08–10 turn to a
different angle on the same theme — specific, named attacks (SQL
injection, XSS, CSRF, and CORS misconfiguration) that a system with real
authentication now has meaningfully more at stake in defending against,
since there's now something worth stealing (an account, a token) that
Module 06's single-shared-user design never had.

## Quick self-check

1. What exactly does `OAuth2PasswordBearer` do, and what does it explicitly *not* do?
2. Name the three distinct failure reasons `get_current_user` collapses into one `401` response, and explain why collapsing them is deliberate.
3. What single parameter, added to a route's signature, is the entire mechanism that makes it "protected" — and what happens to a request with no valid token to a route that lacks it?
4. Why does requesting someone else's quest return `404` instead of `403`, and what specific vulnerability category does that choice avoid?
5. How would you prove, without touching any frontend code at all, that QuestLog's authorization is enforced server-side rather than only by `ProtectedRoute`?
