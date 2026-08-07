import os
from datetime import datetime, timezone

NOTES_FILE = "/data/notes.txt"

os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)

timestamp = datetime.now(timezone.utc).isoformat()
with open(NOTES_FILE, "a") as f:
    f.write(f"{timestamp} - a quest log entry\n")

print("All notes so far:")
with open(NOTES_FILE) as f:
    print(f.read())
