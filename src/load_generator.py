import json
import time
import sys
import pandas as pd
from kafka import KafkaProducer

KAFKA_SERVERS = 'localhost:9093'
TOPIC = 'job-events'

def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1,
        linger_ms=5
    )

def generate_load(requests_per_second, duration_seconds=30):
    producer = create_producer()
    jobs_df = pd.read_csv('data/jobs.csv')
    
    total_requests = requests_per_second * duration_seconds
    interval = 1.0 / requests_per_second
    
    print(f"Sending {total_requests} requests at {requests_per_second} req/s for {duration_seconds}s...")
    
    start_time = time.time()
    sent = 0
    
    for i in range(total_requests):
        job = jobs_df.sample(1).iloc[0].to_dict()
        job['job_date'] = str(job['job_date'])
        job['job_time'] = str(job['job_time'])
        
        producer.send(TOPIC, value=job)
        sent += 1
        
        next_time = start_time + (i + 1) * interval
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    producer.flush()
    producer.close()
    elapsed = time.time() - start_time
    print(f"Done. Sent {sent} requests in {elapsed:.1f}s (actual rate: {sent/elapsed:.1f} req/s)")

if __name__ == "__main__":
    rate = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    generate_load(rate, duration)