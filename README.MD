Lyftr AI Backend Assignment
Containerized Webhook API

# Features
## Webhook Ingestion

1. HMAC-SHA256 signature verification
2. Exactly-once message ingestion using idempotency
3. Graceful handling of duplicate messages

## Message Retrieval

1. Paginated listing with limit and offset
2. Filters: sender (from), timestamp (since), free-text search (q)
3. Deterministic ordering (ts ASC, message_id ASC)

## Analytics

1. Total messages count
2. Unique sender count
3. Top senders by message volume
4. First and last message timestamps

## Observability

1. Liveness and readiness probes
2. Prometheus-style metrics
3. Structured JSON logging

## Deployment

1. SQLite database stored in Docker volume
2. Fully containerized using Docker and Docker Compose
3. Configuration via environment variables (12-factor style)

# Tech Stack

Python 3.11
FastAPI
SQLite
Docker & Docker Compose

# Setup Used:
VSCode + Copilot + ChatGPT

# Project Structure

├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── storage.py
│   ├── schemas.py
│   ├── logging_utils.py
│   └── metrics.py
│
├── tests/
│   ├── test_webhook.py
│   ├── test_messages.py
│   └── test_stats.py
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md

## Setting Environment Variables
### Linux / macOS
```
export WEBHOOK_SECRET=testsecret
export DATABASE_URL=sqlite:////data/app.db
```
### Windows (PowerShell)
```
$env:WEBHOOK_SECRET="testsecret"
$env:DATABASE_URL="sqlite:////data/app.db"
```
# Running the Application
## Start the Service
```
make up
```

API will be available at:

http://localhost:8000

## Stop the Service
```
make down
```
## View Logs
```
make logs
```
# API Usage
## Health Endpoints
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready