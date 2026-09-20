import json
import time
import os
import sys
import psutil
import redis

sys.path.append('src')
from or_tools_matcher import WorkerMatcher

WORKER_NAME = os.getenv('WORKER_NAME', 'worker-1')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6380))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

_process = psutil.Process()
_process.cpu_percent(interval=None)

print(f"[{WORKER_NAME}] Loading matcher...")
matcher = WorkerMatcher()

# Initialize metrics so dispatcher can see us
r.hset(f'metrics:{WORKER_NAME}', mapping={
    'cpu': 0, 'memory': 0, 'queue': 0,
    'latency': 0, 'max_latency': 0, 'jobs_processed': 0
})

print(f"[{WORKER_NAME}] Started. Pulling from Redis queue 'jobs:{WORKER_NAME}'...")

job_count = 0
latency_window = []

while True:
    try:
        # Blocking pop from Redis (5 sec timeout)
        item = r.blpop(f'jobs:{WORKER_NAME}', timeout=5)
        if item is None:
            continue

        job = json.loads(item[1])
        r.hincrby(f'metrics:{WORKER_NAME}', 'queue', -1)

        start = time.perf_counter()
        matched = matcher.match(job)
        latency = (time.perf_counter() - start) * 1000

        latency_window.append(latency)
        if len(latency_window) > 10:
            latency_window.pop(0)
        avg_latency = sum(latency_window) / len(latency_window)

        job_count += 1

        max_key = f'max_latency:{WORKER_NAME}'
        current_max = float(r.get(max_key) or 0)
        if latency > current_max:
            r.set(max_key, latency)

        r.hset(f'metrics:{WORKER_NAME}', mapping={
            'cpu': round(_process.cpu_percent(interval=None), 2),
            'memory': round(_process.memory_percent(), 2),
            'queue': int(r.hget(f'metrics:{WORKER_NAME}', 'queue') or 0),
            'latency': round(avg_latency, 2),
            'max_latency': round(float(r.get(max_key) or 0), 2),
            'jobs_processed': job_count
        })

        result = {
            'worker_name': WORKER_NAME,
            'job_id': job['job_id'],
            'matched_workers': [m['worker_id'] for m in matched],
            'latency_ms': round(latency, 2),
            'timestamp': time.time()
        }
        r.rpush('results', json.dumps(result))

        if job_count % 50 == 0:
            print(f"[{WORKER_NAME}] Processed {job_count} jobs (avg latency {avg_latency:.1f}ms)")

    except Exception as e:
        print(f"[{WORKER_NAME}] ERROR: {e}")
        time.sleep(0.5)