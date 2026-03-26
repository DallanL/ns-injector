FROM python:3.12-slim-bookworm

# Create a dedicated non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./

# Secure ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Run uvicorn securely
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
