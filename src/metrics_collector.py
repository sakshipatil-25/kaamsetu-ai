import redis
import time
import pandas as pd
from datetime import datetime
import sys

r = redis.Redis(host='localhost', port=6380, decode_responses=True)

def collect_metrics(duration_seconds, output_file):
    metrics = []
    start = time.time()
    print(f"Collecting metrics for {duration_seconds}s...")
    
    while time.time() - start < duration_seconds:
        timestamp = datetime.now().isoformat()
        keys = r.keys('metrics:*')
        for key in keys:
            worker_name = key.replace('metrics:', '')
            m = r.hgetall(key)
            if m:
                metrics.append({
                    'timestamp': timestamp,
                    'worker': worker_name,
                    'cpu': float(m.get('cpu', 0)),
                    'memory': float(m.get('memory', 0)),
                    'queue': int(m.get('queue', 0)),
                    'latency': float(m.get('latency', 0)),
                    'max_latency': float(m.get('max_latency', 0)),
                    'jobs_processed': int(m.get('jobs_processed', 0))
                })
        time.sleep(0.2)
    
    df = pd.DataFrame(metrics)
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} records to {output_file}")
    
    if len(df) > 0:
        print("\nSummary:")
        print(f"  Avg CPU: {df['cpu'].mean():.2f}%")
        print(f"  Max CPU: {df['cpu'].max():.2f}%")
        print(f"  Avg Memory: {df['memory'].mean():.2f}%")
        print(f"  Avg Latency: {df['latency'].mean():.2f}ms")
        print(f"  Max Latency: {df['max_latency'].max():.2f}ms")
        print(f"  Total Jobs Processed: {df['jobs_processed'].max()}")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    output = sys.argv[2] if len(sys.argv) > 2 else 'results/centralized_metrics.csv'
    collect_metrics(duration, output)