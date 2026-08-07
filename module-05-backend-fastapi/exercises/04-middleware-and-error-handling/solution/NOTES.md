# Notes on the reference solution

- The middleware is registered once, applies to every route including `GET /vault` (which
  needed zero changes itself) -- concrete proof middleware really is unconditional, per
  Lesson 05, unlike a dependency which only applies where explicitly used.
- `VaultLockedError` carries no HTTP knowledge at all (no status code, no response shape) --
  `reveal_item` just raises a plain, meaningful domain exception; the *shape* of the 409 is
  decided in exactly one place, the handler, per Lesson 06.
- `VaultItemOut` (not `VaultItem`) is used as every route's `response_model` -- `owner_note`
  is never serialized out, regardless of what the underlying stored object contains,
  because `response_model` filters at serialization time, not by the route "remembering"
  to strip a field manually.

**Verified:** run with `uvicorn main:app --reload`. `curl -i -X POST
http://127.0.0.1:8000/vault/item-001/reveal` (locked) returns `409` with the exact
specified `detail`; every response, including `GET /vault`, carries an
`X-Response-Time-Ms` header (confirm with `curl -i`); `curl
http://127.0.0.1:8000/vault/item-002/reveal` (unlocked) returns `200` with no
`owner_note` field anywhere in the body.
