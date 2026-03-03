FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install deps first (better caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy app
COPY . .

# Cloud Run uses PORT env var (usually 8080)
CMD ["sh", "-c", "uv run python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]