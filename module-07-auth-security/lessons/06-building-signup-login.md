# Lesson 06 — Building Real Signup and Login

## What you'll learn

- How to build a real `POST /api/auth/signup` route, line by line.
- How to build a real `POST /api/auth/login` route using FastAPI's `OAuth2PasswordRequestForm`, line by line.
- Why login's request body is form-encoded, not JSON, and what package that requires.
- The frontend's half of the contract: where the token is stored, how it's attached to future requests, and how a page reload restores a logged-in session.
- How to run this yourself, end to end, and watch a real signup → login → authenticated request happen.

## Why this matters

Every lesson so far in this module has been building toward exactly this
moment: real, working code that lets someone create an account and log
in. This lesson wires Lesson 02's password hashing and Lesson 04's JWT
creation into actual HTTP routes, and wires the frontend's `fetch()`
calls (Module 03's mechanics, applied here) into a real login form. After
this lesson, QuestLog has a genuinely new capability it didn't have in
Module 06 at all: accounts.

## Prerequisites

Lesson 02 (`hash_password`/`verify_password`), Lesson 04
(`create_access_token`/`decode_access_token`), Lesson 05 (why
`OAuth2PasswordRequestForm` is shaped the way it is), Module 05 (FastAPI
routes, Pydantic request bodies, `Depends`), Module 04 (React state,
context, controlled forms — this lesson's frontend half assumes you can
read a `useState`/`useEffect`-based component without re-explanation).

## The concept, explained simply

A login system, reduced to its essentials, is two questions and a
receipt: "can you prove you're allowed to have this identity?" (signup —
create the identity in the first place), "prove it, right now, this
time" (login — verify a specific attempt), and "here's your receipt,
which you'll show me instead of re-proving yourself every single time"
(the token). This lesson builds exactly those three things as real code,
reusing every mechanism the last five lessons already explained — nothing
in this lesson introduces new cryptography or new concepts; it's entirely
about *wiring already-understood pieces together*.

## The details

### The backend: `POST /api/auth/signup`

`backend/app/routers/auth.py`:

```python
@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, session: DbSession):
    existing = await repository.get_user_by_email(session, data.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with that email already exists.",
        )
    user = await repository.create_user(session, data.email, hash_password(data.password))
    return UserPublic(id=user.id, email=user.email, created_at=user.created_at.isoformat())
```

**Line by line:**
- `data: UserCreate` — FastAPI reads and validates the JSON request body
  against `UserCreate` (`app/models.py`): `email` must be
  email-shaped (Pydantic's `EmailStr`, backed by the `email-validator`
  package installed in Lesson 00), `password` must be at least 8
  characters. A request failing either check never reaches this
  function's body at all — it gets FastAPI's automatic `422` response
  instead (Module 05, Lesson 03's validation mechanics, unchanged).
- `repository.get_user_by_email(session, data.email)` — checks whether
  this email is already registered, *before* attempting to create
  anything.
- The `400` raised if it is: a deliberate, clean rejection rather than
  letting Postgres's own `UNIQUE` constraint on `users.email`
  (`db_models.py`) raise a raw database integrity error, which would
  otherwise surface as an unhelpful `500 Internal Server Error`.
- `hash_password(data.password)` — Lesson 02's function, called exactly
  once, right here, on the one plain-text password this entire request
  will ever hold. Notice `data.password` (the plain text) is never
  logged, stored, or passed anywhere else in this function.
- `repository.create_user(session, data.email, ...)` — inserts the new
  row, taking an **already-hashed** password as its parameter (see that
  function's own docstring for why this boundary matters).
- The final `UserPublic(...)` construction deliberately builds the
  response by hand, listing exactly the three safe fields — there is no
  path through this function where `user.hashed_password` could
  accidentally leak into a response, because the response model doesn't
  have a field for it at all (Module 05, Lesson 03's `response_model`
  mechanics: even if this function accidentally returned the whole `User`
  ORM object, FastAPI would still filter the response down to
  `UserPublic`'s fields only — a second, independent layer of protection).

### The backend: `POST /api/auth/login`

```python
@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
):
    user = await repository.get_user_by_email(session, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)
```

**Line by line:**
- `form_data: Annotated[OAuth2PasswordRequestForm, Depends()]` — FastAPI
  reads `username` and `password` from a **form-encoded** request body
  (not JSON — see the "why form data" box below), via
  `OAuth2PasswordRequestForm`, a class FastAPI itself provides
  specifically for this exact grant shape (Lesson 05). `form_data.username`
  holds this app's *email* — QuestLog has no separate concept of a
  username at all, it just accepts OAuth2's fixed field name and treats
  it as an email address throughout.
- `user is None or not verify_password(...)` — **one single check for
  two different real causes** ("no account with that email" and "wrong
  password for that account"), producing the exact same error either way.
  This is deliberate, not lazy — see the "one error, two causes" box in
  Lesson 01's authorization discussion for the general principle: telling
  a caller *which* one failed would let an attacker use this endpoint to
  discover which email addresses even have accounts, one guess at a time
  (an example of an **information disclosure** issue, a real category of
  security bug beyond this module's named attacks).
- `create_access_token(subject=user.id)` — Lesson 04's function, called
  only once verification succeeds.
- `Token(access_token=access_token)` — `token_type` defaults to
  `"bearer"` (`app/models.py`'s `Token` model), matching the
  `Authorization: Bearer <token>` header shape this app uses everywhere
  else.

**Why form data, not JSON, for this one route:** `OAuth2PasswordRequestForm`
reads `application/x-www-form-urlencoded` fields, per OAuth2's own spec
convention for this grant — not this app's own preference. Parsing form
data (of *either* kind, urlencoded or multipart) is a job FastAPI
delegates to the `python-multipart` package (installed in Lesson 00);
without it installed, FastAPI raises a clear startup error the moment a
route uses `Form(...)` or `OAuth2PasswordRequestForm` at all.

### Try it with curl

```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "hero@questlog.local", "password": "very-secret-1"}'
```
**Expected:** a `201` response with `{"id": "...", "email":
"hero@questlog.local", "createdAt": "..."}`.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d "username=hero@questlog.local&password=very-secret-1"
```
**Expected:** `{"access_token": "eyJ...", "token_type": "bearer"}`.

**Try it yourself:** run the login `curl` again with a deliberately wrong
password, and confirm you get a `401` with the exact same message you'd
get for an email that was never registered at all — proving the "one
error, two causes" design from above.

### The frontend's half of the contract

Three new files work together (`frontend/src/`):

**`api/http.ts`** — the shared low-level layer, extracted from Module
06's `questsApi.ts` so both `authApi.ts` and `questsApi.ts` can build on
it:

```typescript
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  // ...fetch(), attaching Authorization: Bearer <token> whenever one exists...
}
```

**Why a shared file:** without it, either every API-calling file would
need its own private copy of "attach the token, handle a 401" logic
(duplication — the same reason `app/repository.py` is the *one* seam
between routes and the database, per that file's own docstring), or
`questsApi.ts` would need to import from `authApi.ts` for no good reason.
`getStoredToken`/`setStoredToken`/`clearStoredToken` wrap the browser's
`localStorage` (Lesson 03 already discussed *why* `localStorage`, and
the trade-off against a cookie) behind three small functions, so no other
file in this app touches `localStorage` directly.

**`api/authApi.ts`** — three thin functions calling the three backend
routes above (`signup`, `login`, `fetchCurrentUser`). `login` builds a
`URLSearchParams` (form data, matching the backend's expectation) instead
of `JSON.stringify` (used by every other request in this app).

**`context/AuthContext.tsx`** — owns the one piece of state every other
component cares about: `user`. Its login function does the two real HTTP
calls a "log in and immediately know who you are" flow actually needs:

```typescript
const login = useCallback(async (email: string, password: string) => {
  const token = await authApi.login(email, password);
  setStoredToken(token.access_token);
  const currentUser = await authApi.fetchCurrentUser();
  setUser(currentUser);
}, []);
```

**Why two requests, not one:** `POST /api/auth/login` (the backend route
above) intentionally returns only a token — never the user's own details
— because that's the OAuth2-shaped contract this endpoint borrows
(Lesson 05). Getting the actual account details back is a second,
separate call to `GET /api/auth/me` (Lesson 07's smallest example of a
protected route), made only *after* the token from the first call is
already stored — which is also exactly what proves, for real, that the
token this app just received actually works for a protected request, not
just that login "succeeded" in some abstract sense.

**The "restore session on page reload" effect** — the part of this
lesson's frontend code that most directly demonstrates *why* a token
needs to live somewhere that survives a reload (`localStorage`, not React
state):

```typescript
useEffect(() => {
  if (!getStoredToken()) { setLoading(false); return; }
  authApi.fetchCurrentUser()
    .then((currentUser) => setUser(currentUser))
    .catch(() => setUser(null))   // http.ts already cleared an invalid token
    .finally(() => setLoading(false));
}, []);
```

Reloading the page always resets every piece of React state back to its
initial value — `user` would start as `null` on every single page load,
logging you out on every refresh, if this effect didn't exist. Because
the *token* survived in `localStorage` (untouched by a reload), this
effect can ask the backend "whose token is this, still?" and restore
`user` from a real answer — this is the entire reason `loading` exists as
a separate piece of state from `user`: `ProtectedRoute` (Lesson 07) must
wait for this one-time check to finish before deciding whether to
redirect to `/login`, or it would incorrectly bounce a genuinely
logged-in user to the login page for a split second on every reload.

## Common mistakes & gotchas

- **Sending login as JSON instead of form data.** `OAuth2PasswordRequestForm`
  expects `application/x-www-form-urlencoded` fields; a JSON body to this
  specific route produces a `422`. This is the single most common mistake
  when first calling this endpoint by hand — double-check `Content-Type`
  and body format against the `curl` examples above.
- **Forgetting `python-multipart`.** Without it, FastAPI raises a clear
  error the moment this route is defined, not just when it's called —
  confirmed installed in Lesson 00.
- **Trying to read the current user directly from the login response.**
  `POST /api/auth/login` returns only `{"access_token", "token_type"}` —
  there is no user information in that response at all. `GET /api/auth/me`
  is the only route that returns account details, and only once
  authenticated.
- **Forgetting `AuthProvider` must wrap `QuestsProvider`.** `QuestsContext.tsx`
  calls `useAuth()` internally (Lesson 07 covers exactly why); if
  `AuthProvider` isn't an ancestor in `main.tsx`, this throws
  `"useAuth() must be called from inside an <AuthProvider>."` immediately.

## How this connects

This lesson is where every prior lesson's individual piece — hashing
(02), token creation (04), the borrowed OAuth2 shape (05) — becomes one
real, callable feature. Lesson 07 is the direct next step: making every
*other* route in this app (the actual quests) require exactly the token
this lesson's login route hands back, and scoping what each token's
holder is allowed to see.

## Quick self-check

1. Why does `signup` check for an existing email *before* calling `repository.create_user`, rather than just letting the database's own `UNIQUE` constraint catch it?
2. Why does `login` return the exact same error for "no such email" and "wrong password"?
3. Why is `POST /api/auth/login`'s request body form-encoded instead of JSON, and what package does that require?
4. Why does `AuthContext.tsx`'s `login` function make two separate HTTP requests instead of one?
5. What specific problem does `AuthContext`'s "restore session" effect solve, and why can't that problem be solved with React state alone?
