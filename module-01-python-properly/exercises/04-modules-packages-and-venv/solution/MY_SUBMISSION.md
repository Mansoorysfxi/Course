# Example submission — Exercise 04

This is what a completed `MY_SUBMISSION.md` looks like. Your own version
will have your own venv's exact package versions (they change over time —
that's expected and fine) but should have the same overall shape.

## 1. Commands run

```bash
mkdir ~/questpkg-project
cd ~/questpkg-project
python -m venv .venv
source .venv/Scripts/activate
pip install requests
pip freeze > requirements.txt
cat requirements.txt

mkdir questpkg
touch questpkg/__init__.py questpkg/models.py questpkg/formatting.py touch main.py
# ... edited each file in VS Code ...

python main.py
python -m questpkg.formatting
```

## 2. `requirements.txt`

```
certifi==2026.7.22
charset-normalizer==3.4.9
idna==3.18
requests==2.34.2
urllib3==2.7.0
```

(Only `requests` was installed directly — the other four are its own
dependencies, exactly as Lesson 00 described `pip freeze` capturing
everything installed, direct or transitive.)

## 3. Output of `python main.py`

```
Slay the Dragon [Hard] — 500 gold (In progress)
Water the Plants [Trivial] — 5 gold (Complete)
```

## 4. Output of `python -m questpkg.formatting`

```
Slay the Dragon [Hard] — 500 gold (In progress)
```

(For reference, running `python questpkg/formatting.py` directly instead
produces `ImportError: attempted relative import with no known parent
package` — this is expected, per the exercise's own callout, and is *why*
`-m questpkg.formatting` was used instead.)
