# A DELIBERATELY naive, single-stage Dockerfile -- your task (see
# INSTRUCTIONS.md) is to rewrite this as a multi-stage build and measure
# the real difference. Notice this doesn't even use --no-cache-dir --
# on purpose, so pip's own download cache (real, meaningful size for a
# package like pandas, which pulls in numpy and others) sits inside this
# image's final layer, with no way to remove it after the fact short of
# rebuilding differently.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
