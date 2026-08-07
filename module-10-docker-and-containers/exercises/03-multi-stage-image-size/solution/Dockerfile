# Reference solution -- see INSTRUCTIONS.md.
# ---- Stage 1: builder ----
FROM python:3.14-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: final image ----
FROM python:3.14-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .

CMD ["python", "app.py"]
