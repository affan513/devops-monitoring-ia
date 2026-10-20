"""Demo web application instrumented for Prometheus."""
import random
import time

from flask import Flask, jsonify, request, g
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_http_requests_total", "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds", "HTTP request latency in seconds",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
IN_PROGRESS = Gauge("app_http_requests_in_progress", "Requests being processed")


@app.before_request
def start_timer():
    g.start = time.time()
    IN_PROGRESS.inc()


@app.after_request
def record_metrics(response):
    if request.endpoint != "metrics":
        elapsed = time.time() - g.start
        endpoint = request.path
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint).observe(elapsed)
    IN_PROGRESS.dec()
    return response


@app.route("/")
def index():
    return jsonify(message="Hello from the containerized app", status="ok")


@app.route("/fast")
def fast():
    return jsonify(result="fast response")


@app.route("/slow")
def slow():
    time.sleep(random.uniform(0.2, 1.2))
    return jsonify(result="slow response")


@app.route("/cpu")
def cpu():
    """Burn CPU so container CPU usage is visible on the dashboard."""
    n = 0
    end = time.time() + random.uniform(0.1, 0.4)
    while time.time() < end:
        n += sum(i * i for i in range(1000))
    return jsonify(result="cpu work done")


_leak = []


@app.route("/memory")
def memory():
    """Allocate ~5 MB per call (capped) so memory growth is visible."""
    if len(_leak) < 40:
        _leak.append(bytearray(5 * 1024 * 1024))
    return jsonify(allocated_mb=len(_leak) * 5)


@app.route("/error")
def error():
    if random.random() < 0.5:
        return jsonify(error="simulated failure"), 500
    return jsonify(result="lucky"), 200


@app.route("/health")
def health():
    return jsonify(status="healthy")


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
