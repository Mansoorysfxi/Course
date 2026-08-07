# Lesson 08 — NoSQL Overview: Document Stores and Key-Value Stores

## What you'll learn

- What "NoSQL" actually means (it's a category, not one technology).
- When a document store (e.g. MongoDB) fits better than a relational database.
- What a key-value store (e.g. Redis) is, and what caching means.
- Why QuestLog stays on Postgres, and where Redis will actually enter this course.

## Why this matters

Postgres isn't the only kind of database, and it isn't always the right
one. Knowing *when* you'd reach for something else — even before you've
used it hands-on — is what lets you make an informed choice on a real
project instead of defaulting to whatever you learned first.

## Prerequisites

Lessons 01–07 (you need to know what a relational database's structure and
guarantees actually are, to appreciate what these alternatives trade away).

## The concept, explained simply

"NoSQL" is an umbrella term for databases that *aren't* structured as
fixed-schema tables of rows — it covers several genuinely different
designs, unified mainly by what they're *not*. The two you should know by
name:

**Document store** (e.g. MongoDB): instead of rows in a fixed-column
table, you store whole "documents" (usually JSON-shaped) that don't all
have to share the same structure. Two "quest" documents in a hypothetical
document-store version of QuestLog could each have completely different
fields — one includes an extra `dueDate`, one doesn't — with no `ALTER
TABLE` migration required to allow it. This flexibility trades away
Postgres's strict enforcement (Lesson 02's Consistency guarantee, and
foreign keys from Lesson 01) — nothing stops a document from being
malformed except your application code choosing to validate it. A document
store shines when your data's shape genuinely varies a lot record-to-record,
or changes so often that a rigid schema would be constant friction — think
"catalog of arbitrary user-generated content" more than "structured
business records with clear relationships." QuestLog's actual data (quests
with a small, stable, well-known set of fields, tightly related to a user
and a quest line) is exactly the shape relational databases are good at —
which is why this course doesn't use one for QuestLog itself.

**Key-value store** (e.g. Redis): the simplest possible model — you store
a value under a key and look it up by that exact key, extremely fast,
usually held entirely in memory (RAM) rather than on disk. This trades away
almost everything a relational database offers (no `JOIN`, no `WHERE`
filtering on arbitrary columns, often no guaranteed durability across a
restart unless specifically configured) in exchange for raw speed on the
one operation it does: "give me the value for this exact key, right now."

## The details

### Caching, explained

**Caching** means keeping a copy of some expensive-to-compute or
expensive-to-fetch result somewhere fast to read, so repeated requests for
the same thing don't redo the expensive work every time. Concretely, once
QuestLog has real traffic: `quest_line_stats` (Lesson 04's `GROUP BY`
query) recomputes its aggregate from scratch on every single request, even
if nothing changed since the last call one second ago. A cache would store
that result under a key like `"quest_line_stats"` in Redis, with a short
expiration, and serve *that* instantly for repeat requests instead of
re-querying Postgres every time — trading a small amount of staleness
(the result might be a few seconds old) for a large reduction in database
load.

This is a real, common production pattern — game server analogues include
caching a leaderboard snapshot rather than recomputing rankings from raw
match data on every single client request.

### Why this stays conceptual for now

Redis genuinely enters this course hands-on in **Module 10** (Docker),
specifically because that's where you'll run it as a second service
alongside Postgres via `docker-compose`, per `RUNNING_PROJECT.md` — adding
it now, before Docker makes running multiple services trivial, would mean
a second separate manual Windows install for a feature QuestLog doesn't
critically need yet. This lesson exists so the *concept* (and the
vocabulary: document store, key-value store, caching) is taught before it's
needed, per Rule 1 — you'll recognize it immediately in Module 10 rather
than meeting it cold.

### A quick decision framework

- Data has a clear, stable structure and real relationships you'll query
  across (Lesson 04's joins)? → relational (Postgres). **This is QuestLog.**
- Data's shape varies wildly per record, or the schema changes so often a
  migration (Lesson 07) every time would be painful? → consider a document
  store.
- You need extremely fast, simple key→value lookups, often as a cache in
  front of a "real" database rather than as the only source of truth? →
  consider a key-value store (Redis).

These aren't mutually exclusive in a real system — many production
applications, QuestLog included by Module 10, use Postgres as the
authoritative store *and* Redis as a cache in front of it, each doing the
job it's actually good at.

## Common mistakes & gotchas

- **Treating "NoSQL" as one specific technology.** It's a category
  containing genuinely different designs (document, key-value, and others
  like graph or wide-column databases not covered here) — "NoSQL vs SQL"
  is a less useful question than "which specific trade-off does my data
  need?"
- **Using a cache as if it were the source of truth.** A cache can expire,
  be evicted, or simply be wrong for a few seconds by design — never store
  something in Redis-as-a-cache and delete the only other copy.
- **Reaching for a document store just because a schema feels annoying to
  design up front.** Lesson 09 addresses this directly — schema design
  effort up front usually pays for itself; "our data doesn't have a fixed
  shape" is a real, specific reason, not a general excuse to skip
  modeling.

## How this connects

Module 10 makes this lesson concrete: QuestLog gains a real Redis
container via `docker-compose`, caching `quest_line_stats` exactly as
described above. Lesson 09 continues the schema-design thread this lesson
touched on, specifically for the relational side QuestLog actually uses.

## Quick self-check

1. What does "NoSQL" refer to as a category, and name its two main flavors covered here?
2. What does a document store trade away in exchange for flexible, per-record structure?
3. What is caching, in your own words, and what's the trade-off it makes?
4. Why does QuestLog use Postgres rather than a document store for its quest data?
