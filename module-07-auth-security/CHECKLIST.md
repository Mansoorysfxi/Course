# Module 07 — Checklist

Complete this after finishing all four exercises and the capstone project,
and after your module-end review ("Check my module").

## Self-assessment

- [ ] I can state, in one sentence each, the difference between authentication and authorization, and give a QuestLog-specific example of each.
- [ ] I can explain what a salt is, where it's stored, and why hashing the same password twice with `bcrypt` produces two different-looking outputs.
- [ ] I can explain why hashing (not encryption) is the correct tool for storing a password, and why a fast, generic hash function like SHA-256 is a bad choice for this job.
- [ ] I can compare session-based and JWT-based authentication honestly — what each stores, where, and the real trade-off around instant logout/revocation — without just saying "JWTs are better."
- [ ] I can name a JWT's three parts in order and explain what's inside each one, and I can decode a real token's payload by hand, using nothing but `base64`/`json`, with no secret key.
- [ ] I understand precisely what "signed, not encrypted" means, and I can explain why tampering with a JWT's payload breaks verification even though anyone can read that payload without any key at all.
- [ ] I can name OAuth2's four roles and walk through the Authorization Code flow step by step using a real "Login with X" example, and I can explain exactly which (narrower) part of OAuth2's shape QuestLog's own login endpoint borrows, and why QuestLog isn't doing real third-party OAuth2 at all.
- [ ] I can explain what `OAuth2PasswordBearer` does and does NOT do, and I can explain what single parameter added to a FastAPI route makes it "protected."
- [ ] I can explain why QuestLog returns `404`, not `403`, when a quest exists but belongs to someone else, and I can name the vulnerability category (IDOR) that choice avoids.
- [ ] I can explain, mechanically, why SQLAlchemy's query-building API already prevents SQL injection, and I can point to the one escape hatch (`text()` with a string-interpolated value) that would reintroduce it.
- [ ] I can explain why React's plain `{expression}` JSX interpolation already prevents stored XSS by default, and I know the one prop (`dangerouslySetInnerHTML`) that turns that protection off.
- [ ] I can explain why CSRF is fundamentally a cookie problem, and why QuestLog's own token design (a manually-set `Authorization` header, not a cookie) is naturally resistant to it — and what that same design choice costs with respect to XSS.
- [ ] I can precisely define "origin" (all three parts) and explain why a CORS preflight `OPTIONS` request happens for QuestLog's real requests specifically.
- [ ] I can explain why `SECRET_KEY` has no default value in `app/config.py`, and what happens at startup if one is missing.
- [ ] I have actually run the full signup → login → protected-request flow myself, in the real browser UI, and confirmed a fresh account sees zero quests while the seeded demo account sees its five.
- [ ] I have proven, directly via my browser's dev console (not just by reading about it), that a bare `fetch()` with no token gets `401`, and a token belonging to a *different* account still gets `404` on someone else's quest.
- [ ] All four exercises were reviewed and scored 7/10 or higher (or revised until they were).

## Spaced-repetition review questions from earlier modules

1. **(Module 00 — Git)** What do the three Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) each represent, and what must you do with all three before a merge can be completed?
2. **(Module 01 — Python)** What does Python's `@lru_cache` decorator actually do to a function it wraps (see this module's `app/config.py`'s `get_settings`), and why does that matter for a function that does real file I/O like reading a `.env` file?
3. **(Module 02 — Web Fundamentals)** What does "HTTP is stateless" actually mean, and how do this module's two mechanisms for staying logged in (a session cookie, or a JWT) each solve that same underlying problem in a genuinely different way?
4. **(Module 04 — React)** Why does `AuthContext.tsx`'s "restore session on page reload" logic need to live inside a `useEffect`, and specifically why can't a JWT surviving in `localStorage` be enough on its own to keep a user looking "logged in" after a page reload?
5. **(Module 06 — Databases)** What is the real difference between a foreign key (a database-level concept) and SQLAlchemy's `relationship()` (an ORM-level convenience), and where in this module's `db_models.py` do you see both used for the exact same connection (`Quest.owner_id`)?

## Before you move on to Module 08

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your Module 07 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 08 README to see what's coming next — the first major milestone, a real automated test suite added to this exact, now-authenticated QuestLog.
