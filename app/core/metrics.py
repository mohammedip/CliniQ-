from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.routing import APIRouter
import time
import psutil

# ─── Metrics Definition ────────────────────────────────────────────────────────

# Request count by endpoint and status
REQUEST_COUNT = Counter(
    "cliniq_request_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

# Request latency
REQUEST_LATENCY = Histogram(
    "cliniq_request_latency_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

# RAG specific metrics
RAG_REQUEST_COUNT = Counter(
    "cliniq_rag_requests_total",
    "Total RAG queries",
    ["status"]  # success, failed, ungrounded
)

RAG_LATENCY = Histogram(
    "cliniq_rag_latency_seconds",
    "RAG query latency in seconds",
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 180.0]
)

RAG_ANSWER_QUALITY = Gauge(
    "cliniq_rag_answer_quality",
    "Latest RAG answer quality score (grounded=1, ungrounded=0)"
)

# Error count
ERROR_COUNT = Counter(
    "cliniq_errors_total",
    "Total number of errors",
    ["endpoint", "error_type"]
)

# Infrastructure
CPU_USAGE = Gauge("cliniq_cpu_usage_percent", "CPU usage percent")
RAM_USAGE = Gauge("cliniq_ram_usage_percent", "RAM usage percent")
RAM_USED_MB = Gauge("cliniq_ram_used_mb", "RAM used in MB")


# ─── Middleware ────────────────────────────────────────────────────────────────

async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        latency = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=request.url.path
        ).observe(latency)

        if response.status_code >= 500:
            ERROR_COUNT.labels(
                endpoint=request.url.path,
                error_type="server_error"
            ).inc()

        return response

    except Exception as e:
        ERROR_COUNT.labels(
            endpoint=request.url.path,
            error_type=type(e).__name__
        ).inc()
        raise


# ─── RAG Metrics Helpers ───────────────────────────────────────────────────────

def record_rag_query(latency: float, grounded: bool, failed: bool = False):
    """Call this after each RAG query to record metrics."""
    if failed:
        RAG_REQUEST_COUNT.labels(status="failed").inc()
    elif grounded:
        RAG_REQUEST_COUNT.labels(status="success").inc()
        RAG_ANSWER_QUALITY.set(1.0)
    else:
        RAG_REQUEST_COUNT.labels(status="ungrounded").inc()
        RAG_ANSWER_QUALITY.set(0.0)

    RAG_LATENCY.observe(latency)


# ─── Infrastructure Metrics ────────────────────────────────────────────────────

def update_system_metrics():
    """Update CPU and RAM metrics."""
    CPU_USAGE.set(psutil.cpu_percent())
    ram = psutil.virtual_memory()
    RAM_USAGE.set(ram.percent)
    RAM_USED_MB.set(ram.used / 1024 / 1024)


# ─── Metrics endpoint router ───────────────────────────────────────────────────

metrics_router = APIRouter(tags=["monitoring"])


@metrics_router.get("/metrics")
async def metrics():
    update_system_metrics()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )