# Lesson 08 — SQL Injection, and Why the ORM Already Protects You

## What you'll learn

- What SQL injection actually is, with a real, concrete example of a query breaking.
- Why it works: mixing untrusted user input directly into a SQL string blurs the line between "code" and "data."
- Exactly why SQLAlchemy (Module 06) already protects every query in this backend against it — by default, without anyone having to remember to do anything.
- What a **parameterized query** (a "prepared statement") actually is, mechanically.
- The one way a developer *could* still reintroduce this vulnerability even while using an ORM, and how to recognize it.

## Why this matters

SQL injection has been on the OWASP Top 10 (the security industry's
standard list of the most critical web application risks) for essentially
its entire history, and remains a real, common cause of serious
real-world breaches decades after it was first documented — not because
it's hard to prevent, but because it's easy to reintroduce by accident,
one string-concatenated query at a time. This lesson exists specifically
to close a loop Module 06 opened but deliberately deferred: every query
in `app/repository.py` has, since Module 06, already been safe from this
attack — this lesson finally explains *why*, in enough depth that you'd
recognize the unsafe pattern immediately if you ever saw it, in this
course or anywhere else.

## Prerequisites

Module 06 (SQL fundamentals — `SELECT`/`WHERE` clauses specifically —
and SQLAlchemy's query-building API, `select()`/`.where()`, already used
throughout `app/repository.py`).

## The concept, explained simply

Think of a SQL query like a fill-in-the-blank form letter, and the values
a user supplies (a search term, a login email) as what goes in the
blanks. **SQL injection** happens when a system builds that letter by
literally pasting user-supplied text directly into the middle of the
letter's own template — so if the "blank" text itself contains
punctuation the template's *own* language understands (SQL's own quote
marks, semicolons, keywords), the user's input stops being just "data
filled into a blank" and starts being treated as *part of the letter's
own instructions*. A user who understands the template's grammar can
write input that rewrites the letter's meaning entirely.

## The details

### A concrete, broken example (never actually run in this codebase)

Imagine — hypothetically, and this pattern does **not** exist anywhere in
QuestLog — a login check built like this:

```python
# DO NOT DO THIS. Shown only to demonstrate the vulnerability.
query = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
```

If `email` and `password` come from an ordinary user typing normal
values, this looks harmless. But nothing stops an attacker from typing,
into the email field:

```
' OR '1'='1
```

The resulting string becomes:

```sql
SELECT * FROM users WHERE email = '' OR '1'='1' AND password = ''
```

`'1'='1'` is always true, and thanks to plain SQL's operator precedence,
this `OR` can end up matching **every row in the table**, regardless of
the real password — depending on the exact query, an attacker can walk
straight past a login check with no valid credentials at all, purely by
exploiting the fact that their "data" was pasted directly into the
"code." More advanced injected input can go much further: reading data
from *other* tables the query was never meant to touch, or in the worst
cases, modifying or deleting data outright.

### Why SQLAlchemy already prevents this, by default

Every query in `app/repository.py` — for example, `get_quest`:

```python
stmt = select(QuestRow).where(QuestRow.id == quest_id, QuestRow.owner_id == owner_id)
```

`quest_id` and `owner_id` here are ordinary Python variables that could,
in principle, hold anything at all — including a string containing SQL
syntax. **This is completely safe anyway**, and the reason is
mechanical, not just "SQLAlchemy is careful": `QuestRow.id == quest_id`
does not paste `quest_id`'s text into a SQL string at all. It builds an
**expression object** describing "compare this column to this value,"
and when SQLAlchemy actually sends the query to Postgres, it sends the
SQL template and the actual values **completely separately**, using
Postgres's own **parameterized query** protocol (sometimes called a
**prepared statement**): the query sent to the database literally looks
like `SELECT * FROM quests WHERE id = $1 AND owner_id = $2`, with `$1`
and `$2` as genuine placeholders, and `quest_id`/`owner_id`'s actual
values sent afterward, as pure data, over a completely separate channel
from the query's own text. Postgres itself never re-parses those values
as SQL syntax at all — there is no way for a value, however maliciously
crafted, to "become" part of the query's structure, because the
database's own protocol keeps structure and data in two genuinely
separate places, at the wire-protocol level, not just by convention.

**This is why the login example above is broken and QuestLog's own login
(Lesson 06) is not**, even though both ultimately ask "does a row exist
matching this email/password?" — Lesson 06's `repository.get_user_by_email`
uses `select(User).where(User.email == email)`, exactly the same
parameterized pattern as every other query in this file. Go re-read that
function now and confirm this for yourself: there is no f-string, no
`.format()`, no `%`-formatting anywhere building a SQL string out of
`email`.

### You can still shoot yourself in the foot — the one exception

SQLAlchemy provides an **escape hatch** for genuinely rare cases needing
truly dynamic SQL structure (not just dynamic *values*) — raw SQL via
`sqlalchemy.text()`. If a project ever builds a `text()` query by
f-string-interpolating a raw value directly into it, exactly the same
vulnerability from the broken example above comes right back, ORM or not:

```python
# UNSAFE, even with SQLAlchemy, if you ever wrote it this way:
await session.execute(text(f"SELECT * FROM users WHERE email = '{email}'"))

# SAFE: still using text(), but with a genuine bound parameter:
await session.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

QuestLog's `app/repository.py` never uses `text()` at all — every query
is built with SQLAlchemy's own expression API (`select()`, `.where()`,
`func.count()`, and so on), which makes this specific mistake structurally
hard to make by accident. The general, memorable rule, true in *any*
language or ORM, not just Python/SQLAlchemy: **never build a query by
pasting a variable's raw text directly into a SQL string** (via
f-strings, `.format()`, `%`, or plain concatenation) — always use your
database library's own placeholder/parameter mechanism, whatever it's
called, and let the library keep structure and data separate for you.

## Common mistakes & gotchas

- **Believing "using an ORM" automatically means "safe from SQL
  injection," full stop, no exceptions.** It's safe as long as you stick
  to the ORM's own query-building API — the `text()` escape hatch above
  is the one way to reintroduce the exact same vulnerability underneath
  an ORM, and it looks deceptively similar to safe code at a glance.
- **Assuming input validation (e.g. `EmailStr`, `min_length`) is what
  prevents SQL injection.** It isn't, and conflating the two is a common
  misunderstanding — Pydantic validation (Module 05) rejects malformed
  *shapes* of data before your own code runs; parameterized queries
  prevent a *syntactically valid* string from being mis-treated as code
  once it reaches the database. QuestLog benefits from both, for
  different reasons, but only one of them (parameterized queries) is
  what specifically stops SQL injection.
- **Thinking this attack only applies to login forms.** Any place user
  input flows into a query is a candidate — a search box, a filter
  parameter, a sort column name (`app/routers/quests.py`'s own
  `quest_line` query parameter is exactly this shape, and it's safe for
  the identical reason: it flows into `.where(QuestLine.name ==
  quest_line)`, a parameterized comparison, never a raw string).

## How this connects

Module 06 built every one of QuestLog's queries using SQLAlchemy's
expression API, which is precisely why this module can now say, credibly,
"this backend has been safe from SQL injection since Module 06" — this
lesson is the promised explanation of *why*, closing a loop that module
deliberately left open (see that module's own repository.py docstring
framing, if you want to look back). Lesson 09 turns to a different class
of attack (XSS/CSRF) that lives on the *frontend*/browser side of this
same "don't let untrusted input control something it shouldn't" family
of problems.

## Quick self-check

1. In the broken login example, what specifically does the attacker's `' OR '1'='1` input exploit?
2. What is a parameterized query, mechanically, and why does it prevent the attack above even if the exact same malicious string is supplied as a value?
3. Does using SQLAlchemy's ORM API guarantee safety from SQL injection in every possible case? What's the one exception, and what would make it unsafe again?
4. Why doesn't Pydantic's input validation (e.g. `EmailStr`) by itself prevent SQL injection?
5. Point to one specific line in `app/repository.py` and explain, mechanically, why it's safe even though it uses a variable whose value ultimately comes from an HTTP request.
