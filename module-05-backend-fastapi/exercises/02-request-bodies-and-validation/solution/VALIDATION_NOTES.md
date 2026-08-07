# Validation notes (reference)

Recorded from actually running `solution/main.py` and sending each request via `curl`.

**1. Omitting `character_class` entirely** (`{"name": "Aria", "level": 5}`):
- `type`: `"missing"`
- `loc`: `["body", "character_class"]`
- `msg`: `"Field required"`

**2. `level: 150`:**
- `type`: `"less_than_equal"`
- `loc`: `["body", "level"]`
- `msg`: `"Input should be less than or equal to 100"`

**3. `character_class: "necromancer"`:**
- `type`: `"literal_error"`
- `loc`: `["body", "character_class"]`
- `msg`: `"Input should be 'warrior', 'mage', 'rogue' or 'cleric'"`

All three were never routed into `create_adventurer`'s body at all — FastAPI's own
validation layer (Lesson 03) rejected each request before any of this file's own code ran.
