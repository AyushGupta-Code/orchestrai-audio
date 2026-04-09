# Minimal Docker image for running the local demo pipeline.
#
# This image keeps the default experience simple:
# - installs the repository
# - uses the normal stub fallback path
# - lets a caller override the request by replacing the container command

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts
COPY templates ./templates
COPY data ./data

RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --no-cache-dir -e .

CMD ["python", "scripts/run_demo.py", "Generate 2 hours of calm rain ambience for studying"]

