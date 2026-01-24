# Climate AI Collective - Services Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder

# Install system dependencies and security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Upgrade pip and wheel to fix CVE-2026-24049 (wheel), then install dependencies
# Also ensure jaraco.context>=6.1.0 for CVE-2026-23949
RUN pip install --no-cache-dir --upgrade pip wheel>=0.46.2 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "jaraco.context>=6.1.0"

# Final stage
FROM python:3.11-slim

# Install runtime dependencies and security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy application code
COPY services/ ./services/
COPY context/ ./context/

# Create non-root user
RUN useradd -m -u 1000 climateai && \
    chown -R climateai:climateai /app

USER climateai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
