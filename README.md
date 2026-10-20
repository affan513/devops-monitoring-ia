# Containerized Application Monitoring and Performance Analysis
Theory IA – DevOps | Tools: **Docker + Prometheus + Grafana (+ cAdvisor)**

Group: Ammar Kazi (16010124810), Soham Patil (16010124816), Affan Ansari (16010124820) | Faculty: MMP

## Architecture
```
 loadgen --HTTP--> webapp (Flask, /metrics) <--scrape-- Prometheus <--query-- Grafana
                   cAdvisor (container CPU/mem/net) <--scrape--^
```

## Run
```bash
docker compose up -d --build
```
| Service    | URL                          | Notes                    |
|------------|------------------------------|--------------------------|
| Web app    | http://localhost:5000        | /, /fast, /slow, /cpu, /memory, /error, /health, /metrics |
| Prometheus | http://localhost:9090        | Status > Targets, Alerts |
| cAdvisor   | http://localhost:8080        | raw container metrics    |
| Grafana    | http://localhost:3000        | admin / admin; dashboard "Containerized Application Monitoring" is auto-provisioned |

Stop: `docker compose down` (add `-v` to wipe data).

## Verify
1. Prometheus > Status > Targets: `webapp`, `cadvisor`, `prometheus` all **UP**.
2. Grafana > Dashboards > *Containerized Application Monitoring*: panels update every 5 s.
3. Trigger alerts: `docker stop webapp` -> `WebAppDown` fires after ~15 s. `docker start webapp` to recover.
4. Spike CPU/memory: `for i in $(seq 1 200); do curl -s localhost:5000/cpu >/dev/null; done`

## Useful PromQL
```
sum(rate(app_http_requests_total[1m]))                                  # requests/sec
histogram_quantile(0.95, sum(rate(app_http_request_duration_seconds_bucket[1m])) by (le))  # p95 latency
sum(rate(container_cpu_usage_seconds_total{name="webapp"}[1m])) * 100   # CPU %
container_memory_usage_bytes{name="webapp"}                             # memory
```

## DevOps pipeline (CI/CD + security)
`.github/workflows/ci-cd.yml` runs on every push and pull request:

| Stage | What it does |
|-------|--------------|
| test | unit tests, `promtool check config/rules`, `docker compose config`, dashboard JSON validation |
| security | Trivy scan of the repo (vulnerabilities, secrets, misconfigurations) and of the built image; fails on CRITICAL findings |
| deploy | `docker compose up` on the runner (infrastructure as code), then `scripts/smoke_test.sh` checks the app, all Prometheus targets and the Grafana dashboard |
| publish | on `main` only: pushes the web app image to GitHub Container Registry |

Version control: all code, Prometheus rules and the Grafana dashboard live in Git.

## Performance test
```bash
python scripts/loadtest.py http://localhost:5000/fast 30 10   # URL, seconds, threads
```
Compare its output with the dashboard (requests/s, p95 latency, webapp CPU/memory) and with
`docker stats` to record the monitoring stack's own overhead.

## Layout
```
app/          Flask app + Dockerfile (instrumented with prometheus_client)
loadgen/      traffic generator container
prometheus/   prometheus.yml, alert.rules.yml
scripts/      smoke_test.sh (post-deploy check), loadtest.py
.github/      CI/CD workflow
grafana/      provisioning (datasource, dashboard provider) + dashboard JSON
docker-compose.yml
```
