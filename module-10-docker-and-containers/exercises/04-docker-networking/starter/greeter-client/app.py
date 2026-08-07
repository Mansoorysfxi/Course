import os
import urllib.error
import urllib.request

# GREETER_HOST is deliberately read from an environment variable, not
# hardcoded -- your job (see INSTRUCTIONS.md) is to run this container
# such that this correctly resolves to the greeter-server container.
host = os.environ.get("GREETER_HOST", "localhost")
url = f"http://{host}:5000"

print(f"Attempting to reach greeter-server at: {url}")
try:
    with urllib.request.urlopen(url, timeout=5) as response:
        print(response.read().decode())
except (urllib.error.URLError, ConnectionError) as exc:
    print(f"FAILED to reach {url}: {exc}")
