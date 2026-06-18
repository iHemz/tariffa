# Logging Patterns

Structured logging patterns for observability and debugging in tariffa's `apps/api` (Python / FastAPI) backend.

## Table of Contents

- [Logger Setup](#logger-setup)
- [Log Levels](#log-levels)
- [Structured Logging](#structured-logging)
- [Contextual Logging](#contextual-logging)
- [Correlation IDs](#correlation-ids)
- [Error Logging](#error-logging)
- [Performance Logging](#performance-logging)
- [Best Practices](#best-practices)

---

## Logger Setup

### Basic Usage

We use Python's standard `logging` module configured for structured (JSON) output. Get a logger by module name and log with structured fields, never f-string-interpolated values.

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Shipment created")
logger.warning("Rate limit approaching")
logger.error("Failed to extract invoice")
```

### Logger Configuration

Logging is configured once at startup:

- `app/core/logging.py` — configures the root logger with a JSON formatter and the correlation-ID filter
- Structured fields are passed via the `extra={...}` argument and rendered into the JSON record

```python
# app/core/logging.py — configured once on app startup
import logging
from app.core.logging import configure_logging

configure_logging()  # call from the FastAPI lifespan / startup hook
```

---

## Log Levels

### Available Log Levels

```python
logger.debug("Detailed debugging information")
logger.info("General informational messages")
logger.warning("Warning messages for potential issues")
logger.error("Error messages for failures")
```

### When to Use Each Level

**Debug:**
- Detailed information for development
- Only emitted in non-production environments
- Tracing execution flow through the pipeline stages

**Info:**
- General application flow
- Important domain events (shipment uploaded, classification completed)
- Successful operations

**Warning:**
- Potential issues that don't break functionality
- Low-confidence classifications, retried LLM calls
- Performance concerns

**Error:**
- Failures that need attention
- Exceptions, failed pipeline stages, LLM refusals

---

## Structured Logging

### Basic Structured Logging

Pass structured context through `extra`, not by formatting it into the message string. This keeps the message stable (good for grouping) and the fields queryable.

```python
# Simple message with context
logger.info("Shipment created", extra={"shipment_id": "shp_123", "user_id": "usr_456"})

# Error with additional context
logger.error(
    "Invoice extraction failed",
    extra={
        "shipment_id": "shp_123",
        "document_id": "doc_789",
        "error": str(error),
    },
)
```

### Module-Scoped Loggers

Use one logger per module (`logging.getLogger(__name__)`). The module name is included in every record, giving you the same "which component logged this" context that child loggers provide.

```python
# app/services/extraction.py
import logging

logger = logging.getLogger(__name__)

logger.info("Fetching documents", extra={"shipment_id": shipment_id})
# Record includes: logger name "app.services.extraction"
```

### Service-Level Logging

```python
# app/services/classification.py
import logging

logger = logging.getLogger(__name__)


class ClassificationService:
    async def classify(self, line_item: LineItem, *, user_id: str) -> Classification:
        logger.info(
            "Classifying line item",
            extra={"user_id": user_id, "description": line_item.description},
        )
        try:
            result = await self._agent.run(line_item)
            logger.info(
                "Classification complete",
                extra={"hs_code": result.hs_code, "confidence": result.confidence},
            )
            return result
        except Exception as error:
            logger.error(
                "Classification failed",
                extra={"user_id": user_id, "error": str(error)},
            )
            raise
```

---

## Contextual Logging

### Adding Context to Logs

Include the relevant identifiers in every log so a record is self-describing. Use consistent key names across the codebase (`shipment_id`, `user_id`, `document_id`, `hs_code`).

```python
logger.info(
    "Processing shipment",
    extra={
        "shipment_id": shipment.id,
        "user_id": shipment.user_id,
        "document_count": len(shipment.documents),
        "status": shipment.status,
    },
)

logger.error(
    "Regulatory lookup failed",
    extra={
        "regulator": "NAFDAC",
        "hs_code": "28289010",
        "duration_ms": 1234,
    },
)
```

### Pipeline-Stage Context

Each pipeline stage logs under its module logger, so the stage is identifiable from the record's logger name. Add the stage explicitly when it isn't obvious:

```python
logger.info("Stage started", extra={"stage": "compliance_check", "shipment_id": shipment_id})
```

---

## Correlation IDs

### Automatic Correlation IDs

A correlation ID is attached to every request and propagated to all logs emitted while handling it, so you can trace a single shipment upload through extraction → classification → compliance → Form M draft.

The correlation ID is stored in a `contextvars.ContextVar` (set by middleware on each incoming request) and injected into every log record by a logging filter.

```python
# app/core/correlation.py
import contextvars

correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)
```

```python
# Set once per request via middleware; every subsequent log includes it
logger.info("Request started")
# Record includes: correlation_id="abc123"
```

### Correlation ID Source

- `app/core/correlation.py` — the `ContextVar` and helpers
- A FastAPI middleware reads an inbound `X-Correlation-ID` header (or generates one) and sets the var
- A logging filter copies the current correlation ID onto every record
- `contextvars` propagates correctly across `async`/`await`, so the ID follows the request through awaited calls

### Propagating to Background Tasks

`ContextVar` values do not automatically cross into a FastAPI background task. Capture the ID and re-set it inside the task:

```python
from app.core.correlation import correlation_id_var

cid = correlation_id_var.get()

def work() -> None:
    correlation_id_var.set(cid)
    logger.info("Background work started")

background_tasks.add_task(work)
```

---

## Error Logging

### Basic Error Logging

Use `logger.exception(...)` inside an `except` block — it captures the traceback automatically. Use `logger.error(..., exc_info=True)` if you're not directly in the handler.

```python
try:
    await risky_operation()
except Exception:
    logger.exception("Operation failed", extra={"operation": "risky_operation"})
    raise
```

### Error Logging in Services

```python
async def perform_operation(self, shipment_id: str):
    logger.info("Starting operation", extra={"shipment_id": shipment_id})
    try:
        shipment = await self.repository.get(shipment_id)
        if shipment is None:
            logger.warning("Shipment not found", extra={"shipment_id": shipment_id})
            raise NotFoundError(f"Shipment not found: {shipment_id}")

        # business logic...

        logger.info("Operation complete", extra={"shipment_id": shipment_id})
        return result
    except Exception:
        logger.exception("Operation failed", extra={"shipment_id": shipment_id})
        raise
```

### Error Logging in API Routes

```python
from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/shipments")
async def create_shipment(payload: CreateShipment, user_id: str = Depends(current_user)):
    logger.info("POST /shipments", extra={"user_id": user_id})
    try:
        shipment = await shipment_service.create(payload, user_id=user_id)
        logger.info("Shipment created", extra={"shipment_id": shipment.id})
        return shipment
    except Exception:
        logger.exception("Failed to create shipment", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="Failed to create shipment")
```

---

## Performance Logging

### Timing Operations

```python
import time

start = time.perf_counter()
await expensive_operation()
duration_ms = (time.perf_counter() - start) * 1000

logger.info(
    "Operation complete",
    extra={"operation": "expensive_operation", "duration_ms": round(duration_ms, 1)},
)
```

### Reusable Timing Helper

```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def timed(operation: str, *, warn_over_ms: float = 1000.0):
    start = time.perf_counter()
    logger.info("started", extra={"operation": operation})
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        level = logging.WARNING if duration_ms > warn_over_ms else logging.INFO
        logger.log(
            level,
            "finished",
            extra={"operation": operation, "duration_ms": round(duration_ms, 1)},
        )


# Usage
async with timed("classify_shipment"):
    await classify(shipment)
```

LLM calls are the dominant latency in this pipeline — time the extraction, classification, and compliance stages so slow runs surface in logs.

---

## Best Practices

### DO

1. **Use structured fields** — pass context via `extra={...}`, not f-strings.
2. **Use module loggers** — `logging.getLogger(__name__)` in every module.
3. **Log important domain events** — uploads, stage completions, status changes.
4. **Rely on correlation IDs** — automatic per request; verify they propagate into background tasks.
5. **Log errors with `logger.exception`** — captures the traceback and context.
6. **Use appropriate levels** — debug for dev, info for production flow.
7. **Log performance metrics** — duration of LLM calls and pipeline stages.

### DON'T

1. **Don't log sensitive data** — API keys, tokens, or raw credentials. Treat uploaded document contents carefully; log identifiers and metadata, not full payloads.
2. **Don't over-log** — avoid logging inside tight loops.
3. **Don't use `print()`** — always use the configured logger.
4. **Don't log without context** — include the relevant identifiers.
5. **Don't swallow errors** — log with context, then re-raise.
6. **Don't interpolate context into the message** — keep messages stable, put data in `extra`.

---

## Common Patterns

### Pattern 1: Service Method Logging

```python
logger = logging.getLogger(__name__)


class ShipmentService:
    async def create(self, payload: CreateShipment, *, user_id: str) -> Shipment:
        logger.info("Creating shipment", extra={"user_id": user_id})
        try:
            shipment = await self.repository.create(payload, user_id=user_id)
            logger.info("Shipment created", extra={"shipment_id": shipment.id, "user_id": user_id})
            return shipment
        except Exception:
            logger.exception("Failed to create shipment", extra={"user_id": user_id})
            raise
```

### Pattern 2: API Route Logging

```python
@router.post("/shipments")
async def create_shipment(payload: CreateShipment, user_id: str = Depends(current_user)):
    logger.info("POST /shipments", extra={"user_id": user_id})
    try:
        shipment = await shipment_service.create(payload, user_id=user_id)
        logger.info("Shipment created", extra={"shipment_id": shipment.id})
        return shipment
    except Exception:
        logger.exception("Failed to create shipment", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Pattern 3: Background-Task Logging

```python
def process_shipment(shipment_id: str, cid: str | None) -> None:
    correlation_id_var.set(cid)  # carry the request's correlation ID into the task
    logger.info("Processing shipment", extra={"shipment_id": shipment_id})
    try:
        logger.info("Extraction started", extra={"shipment_id": shipment_id})
        # run extraction → classification → compliance → Form M draft
        logger.info("Processing complete", extra={"shipment_id": shipment_id})
    except Exception:
        logger.exception("Shipment processing failed", extra={"shipment_id": shipment_id})


background_tasks.add_task(process_shipment, shipment.id, correlation_id_var.get())
```

---

## Log Format

### Standard Log Record (JSON)

```json
{
  "timestamp": "2026-06-18T10:30:00.000Z",
  "level": "INFO",
  "logger": "app.services.classification",
  "correlation_id": "abc123",
  "message": "Classification complete",
  "hs_code": "28289010",
  "confidence": 0.94
}
```

### Record Components

- **timestamp** — ISO 8601
- **level** — DEBUG, INFO, WARNING, ERROR
- **logger** — the module logger name (component context)
- **correlation_id** — request tracking ID
- **message** — stable, human-readable message
- **extra fields** — structured context merged into the record

---

## See Also

- [Validation Patterns](./validation.md) — Pydantic validation at API and pipeline boundaries
