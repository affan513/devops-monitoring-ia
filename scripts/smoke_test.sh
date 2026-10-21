#!/usr/bin/env bash
# Post-deploy check: app healthy, Prometheus scraping all targets, Grafana dashboard loaded.
set -euo pipefail
retry() { for _ in $(seq 1 30); do "$@" && return 0; sleep 3; done; return 1; }

echo "Waiting for web app..."
retry curl -fsS http://localhost:5000/health >/dev/null
echo "Waiting for Prometheus targets to be UP..."
check_targets() {
  curl -fsS http://localhost:9090/api/v1/targets \
   | python3 -c "import sys,json; t=json.load(sys.stdin)['data']['activeTargets']; sys.exit(0 if t and all(x['health']=='up' for x in t) else 1)"
}
retry check_targets
echo "Waiting for Grafana dashboard..."
retry curl -fsS -u admin:admin "http://localhost:3001/api/search?query=Containerized" | grep -q "Containerized Application Monitoring"
echo "Smoke test passed."
