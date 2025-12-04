############################
# Stage 1 — Builder
############################
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


############################
# Stage 2 — Runtime
############################
FROM python:3.11-slim

WORKDIR /app

# Set timezone to UTC
ENV TZ=UTC

# Install system packages (cron, tzdata)
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Setup directories for volumes
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Install cron job
COPY crontab.txt /etc/cron.d/mycron
COPY cronjob.sh /cronjob.sh
RUN chmod 0644 /etc/cron.d/mycron && chmod +x /cronjob.sh

# Register cron job
RUN crontab /etc/cron.d/mycron

# Expose API port
EXPOSE 8080

# Start both cron + FastAPI
CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080