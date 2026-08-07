# Reference solution — exact command sequence

This exercise's "solution" is a sequence of commands, not code — `app.py`
and `Dockerfile` here are identical to `starter/`.

```bash
# Setup
docker build -t quest-notes .

# Part 1 -- no volume, three separate runs
docker run --rm quest-notes   # 1 note
docker run --rm quest-notes   # still 1 note -- a brand new container each time
docker run --rm quest-notes   # still 1 note

# Part 2 -- with a named volume
docker volume create quest-notes-data
docker run --rm -v quest-notes-data:/data quest-notes   # 1 note
docker run --rm -v quest-notes-data:/data quest-notes   # 2 notes
docker run --rm -v quest-notes-data:/data quest-notes   # 3 notes
docker run --rm -v quest-notes-data:/data quest-notes   # 4 notes

# Prove removing the volume actually deletes the data
docker volume rm quest-notes-data
docker run --rm -v quest-notes-data:/data quest-notes   # back to 1 note (a fresh, empty volume was recreated)

# Cleanup
docker volume rm quest-notes-data
```
