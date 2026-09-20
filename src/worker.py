import json
import time
import os
import sys
import psutil
import redis
from kafka import KafkaConsumer, TopicPartition

sys.path.append('src')
from or_tools_matcher import WorkerMatcher

# Configuration from environment
WORKER_NAME = os.getenv('WORKER_NAME', 'worker-1')
KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', 'localhost:9093')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6380))
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'job-events')

# Partition assignment (for distributed experiments)
PARTITION_ID = int(os.getenv('PARTITION_ID', '0'))

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Process handle for accurate CPU/memory metrics
_process = psutil.Process()
_process.cpu_percent(interval=None)

# Initialize matcher
print(f"[{WORKER_NAME}] Loading matcher...")
matcher = WorkerMatcher()

# Create Kafka consumer with manual partition assignment
consumer = KafkaConsumer(
    bootstrap_servers=KAFKA_SERVERS,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    api_version=(3, 0, 0),
    consumer_timeout_ms=60000,
    request_timeout_ms=40000,
    session_timeout_ms=30000,
    heartbeat_interval_ms=10000
)
consumer.assign([TopicPartition(KAFKA_TOPIC, PARTITION_ID)])

print(f"[{WORKER_NAME}] Started. Listening on partition {PARTITION_ID} of '{KAFKA_TOPIC}'...")

job_count = 0
latency_window = []

while True:
    try:
        msg = next(consumer)
    except StopIteration:
        continue
    except Exception as e:
        print(f"[{WORKER_NAME}] Consumer error: {e}")
        time.sleep(1)
        continue

    job = msg.value
    start = time.perf_counter()

    try:
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
            'queue': 0,
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

        print(f"[{WORKER_NAME}] Job {job['job_id']} -> {len(matched)} workers in {latency:.1f}ms")

    except Exception as e:
        print(f"[{WORKER_NAME}] ERROR processing {job.get('job_id', 'unknown')}: {e}")