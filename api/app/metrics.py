"""Prometheus metrics configuration for FastAPI.

Uses prometheus-fastapi-instrumentator to expose:
- http_requests_total (counter with status, method, path)
- http_request_duration_seconds (histogram with method, path, le)
- fastapi_model_loaded (gauge: 1 when model loaded, 0 otherwise)
"""

from __future__ import annotations

from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Custom gauge: 1 if model is loaded, 0 otherwise.
model_loaded_gauge = Gauge(
    "fastapi_model_loaded",
    "Whether a model is currently loaded (1=yes, 0=no)",
)

# FastAPI instrumentator with sensible defaults for ML serving.
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)