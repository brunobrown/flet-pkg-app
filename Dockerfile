FROM python:3.12-slim

# Flet web needs these for Flutter client rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (production only, no dev group)
RUN uv sync --no-dev --frozen

# Copy application code
COPY main.py config.py settings.toml ./
COPY src/ src/
COPY assets/ assets/

# Port used by the Flet web server
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD curl -f http://localhost:8001/ || exit 1

# Run the Flet app in web mode
CMD ["uv", "run", "flet", "run", "main.py", "--web", "--port", "8001", "--host", "0.0.0.0"]