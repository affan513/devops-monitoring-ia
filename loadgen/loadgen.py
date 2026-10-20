"""Tiny load generator: sends a weighted mix of requests to the web app."""
import os
import random
import time
import urllib.request
import urllib.error

BASE = os.getenv("TARGET", "http://webapp:5000")
PATHS = ["/", "/fast", "/fast", "/slow", "/cpu", "/memory", "/error", "/health"]
WEIGHTS = [2, 5, 5, 2, 2, 0.3, 1.5, 1]

while True:
    path = random.choices(PATHS, WEIGHTS)[0]
    try:
        urllib.request.urlopen(BASE + path, timeout=5).read()
    except (urllib.error.URLError, OSError):
        pass
    time.sleep(random.uniform(0.05, 0.4))
