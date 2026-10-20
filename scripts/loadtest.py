"""Simple load test for the performance section of the report.
Usage: python scripts/loadtest.py [url] [seconds] [threads]
Prints throughput and latency percentiles; compare with the Grafana dashboard.
"""
import statistics
import sys
import threading
import time
import urllib.request

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/fast"
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
threads = int(sys.argv[3]) if len(sys.argv) > 3 else 10
lat, errors, lock = [], 0, threading.Lock()


def worker(stop):
    global errors
    while time.time() < stop:
        t = time.time()
        try:
            urllib.request.urlopen(url, timeout=5).read()
            ok = True
        except Exception:
            ok = False
        with lock:
            lat.append(time.time() - t)
            if not ok:
                errors += 1


stop = time.time() + duration
ts = [threading.Thread(target=worker, args=(stop,)) for _ in range(threads)]
[t.start() for t in ts]
[t.join() for t in ts]
lat.sort()
q = lambda p: lat[min(len(lat) - 1, int(len(lat) * p))] * 1000
print(f"requests={len(lat)} errors={errors} rps={len(lat)/duration:.1f}")
print(f"latency ms: mean={statistics.mean(lat)*1000:.1f} p50={q(.5):.1f} p95={q(.95):.1f} p99={q(.99):.1f}")
