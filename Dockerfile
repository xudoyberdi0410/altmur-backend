
# Dockerfile for FastAPI app (production build)
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && pip install uv && uv pip install --system --no-cache-dir .

COPY . .

# Use Uvicorn for FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
