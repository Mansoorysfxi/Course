# A deliberately simple, single-stage Dockerfile -- this exercise's whole
# point is the CI workflow that builds/pushes THIS image, not the
# Dockerfile itself (Module 10 already taught Dockerfile-writing in
# full). Provided as-is so you can focus entirely on
# lessons/08-deploying-questlog-with-ci-cd.md's own build-and-push
# pattern, applied here in miniature.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
