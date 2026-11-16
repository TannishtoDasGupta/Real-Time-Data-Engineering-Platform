# Real-Time Data Engineering Platform

Event ingestion and aggregation API built with FastAPI and a persistent SQLite event log. Events are schema-validated, assigned caller-controlled IDs for idempotency, stored once, and summarized by event type.

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open /docs. API: POST /events, GET /events, GET /metrics, GET /health.

## Architecture evolution
SQLite is a local demo adapter. For distributed workloads, replace it with Kafka and consumer groups, add a schema registry, dead-letter topic, replay controls, observability, and an outbox for transactional event publishing. Event handlers should remain idempotent because at-least-once delivery can repeat messages.
