import json
import time
import os
import sys
import redis
from kafka import KafkaConsumer

KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', 'localhost:9093')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'job-events')
DISPATCHER_PARTITION = int(os.getenv('DISPATCHER_PARTITION', '0'))

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6380))

WORKERS = ['worker-1', 'worker-2', 'worker-3']

# Weighted scoring weights (tunable — this is your research parameter)
W_CPU = 0.5
W_QUEUE = 0.3
W_LATENCY = 0.2

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_worker_metrics(worker_name):
    """Fetch current metrics for a worker from Redis."""
    m = r.hgetall(f'metrics:{worker_name}')
    return {
        'cpu': float(m.get('cpu', 0)),
        'queue': int(m.get('queue', 0)),
        'latency': float(m.get('latency', 0)),
    }


def score_worker(metrics):
    """Lower score = better worker. Weighted combination."""
    return (W_CPU * metrics['cpu'] +
            W_QUEUE * metrics['queue'] * 10 +
            W_LATENCY * metrics['latency'])


def choose_best_worker():
    """Pick the worker with the lowest weighted score."""
    best = None
    best_score = float('inf')
    for w in WORKERS:
        m = get_worker_metrics(w)
        s = score_worker(m)
        if s < best_score:
            best_score = s
            best = w
    return best, best_score


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

# Listen on ALL partitions — the dispatcher is the single consumer
from kafka import TopicPartition
consumer.assign([TopicPartition(KAFKA_TOPIC, p) for p in [0, 1, 2]])

print(f"[dispatcher] Started. Routing jobs from '{KAFKA_TOPIC}' to {WORKERS}...")
print(f"[dispatcher] Policy weights: cpu={W_CPU}, queue={W_QUEUE}, latency={W_LATENCY}")

dispatch_count = 0
dispatch_stats = {w: 0 for w in WORKERS}

while True:
    try:
        msg = next(consumer)
    except StopIteration:
        continue
    except Exception as e:
        print(f"[dispatcher] Consumer error: {e}")
        time.sleep(1)
        continue

    job = msg.value

    try:
        target, score = choose_best_worker()

        # Push job to worker's Redis queue
        r.rpush(f'jobs:{target}', json.dumps(job))
        r.hincrby(f'metrics:{target}', 'queue', 1)

        dispatch_count += 1
        dispatch_stats[target] += 1

        # Print every 50 jobs to avoid flooding
        if dispatch_count % 50 == 0:
            print(f"[dispatcher] Dispatched {dispatch_count} jobs. Distribution: {dispatch_stats}")
            r.hset('dispatcher:stats', mapping={
                'total_dispatched': dispatch_count,
                **{f'to_{w}': dispatch_stats[w] for w in WORKERS}
            })

    except Exception as e:
        print(f"[dispatcher] ERROR: {e}")