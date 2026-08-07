# Reference solution -- see INSTRUCTIONS.md's acceptance criteria for
# exactly what this needs to satisfy. Ordering matters here: requirements
# first, installed, THEN application code -- see
# lessons/02-dockerfiles-layers-and-caching.md.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
