"""
In-memory simulator for Centralized vs Static vs Adaptive scheduling.
Uses the same XGBoost + OR-Tools logic as the real distributed system,
but simulates the scheduling behavior without Kafka.
"""
import time
import random
import pandas as pd
import sys
sys.path.append('src')
from or_tools_matcher import WorkerMatcher


class SimulatedWorker:
    def __init__(self, name):
        self.name = name
        self.jobs_processed = 0
        self.total_latency = 0.0
        self.max_latency = 0.0
        self.cpu = 0.0
        self.queue = 0

    def process(self, matcher, job):
        start = time.perf_counter()
        matched = matcher.match(job)
        latency = (time.perf_counter() - start) * 1000
        self.jobs_processed += 1
        self.total_latency += latency
        self.max_latency = max(self.max_latency, latency)
        self.cpu = min(100.0, 30 + random.uniform(0, 40) + latency / 2)
        return matched, latency

    @property
    def avg_latency(self):
        return self.total_latency / max(1, self.jobs_processed)

    def to_dict(self):
        return {
            'name': self.name,
            'jobs_processed': self.jobs_processed,
            'avg_latency': round(self.avg_latency, 2),
            'max_latency': round(self.max_latency, 2),
            'cpu': round(self.cpu, 2),
        }


class Simulator:
    def __init__(self):
        self.matcher = WorkerMatcher()
        self.jobs_df = pd.read_csv('data/jobs.csv')

    def _sample_jobs(self, n):
        return [self.jobs_df.sample(1).iloc[0].to_dict() for _ in range(n)]

    def run_centralized(self, n_jobs=50):
        worker = SimulatedWorker('worker-1')
        jobs = self._sample_jobs(n_jobs)
        for job in jobs:
            worker.process(self.matcher, job)
        return {
            'setup': 'centralized',
            'workers': [worker.to_dict()],
            'total_jobs': n_jobs,
            'avg_latency': round(worker.avg_latency, 2),
            'max_latency': round(worker.max_latency, 2),
            'throughput': round(n_jobs / max(0.001, worker.total_latency / 1000), 2),
            'load_imbalance': 0.0,
        }

    def run_static(self, n_jobs=50, n_workers=3):
        workers = [SimulatedWorker(f'worker-{i+1}') for i in range(n_workers)]
        jobs = self._sample_jobs(n_jobs)
        for i, job in enumerate(jobs):
            target = workers[i % n_workers]
            target.process(self.matcher, job)
        return self._summarize('static', workers, n_jobs)

    def run_adaptive(self, n_jobs=50, n_workers=3):
        workers = [SimulatedWorker(f'worker-{i+1}') for i in range(n_workers)]
        jobs = self._sample_jobs(n_jobs)
        for job in jobs:
            target = min(workers, key=lambda w: w.cpu + w.queue * 10)
            target.queue += 1
            target.process(self.matcher, job)
            target.queue -= 1
        return self._summarize('adaptive', workers, n_jobs)

    def _summarize(self, setup, workers, n_jobs):
        latencies = [w.avg_latency for w in workers]
        max_lat = max(w.max_latency for w in workers)
        job_counts = [w.jobs_processed for w in workers]
        avg_jobs = sum(job_counts) / len(job_counts)
        imbalance = (max(job_counts) - min(job_counts)) / max(1, avg_jobs) * 100
        total_time = sum(w.total_latency for w in workers) / 1000

        return {
            'setup': setup,
            'workers': [w.to_dict() for w in workers],
            'total_jobs': n_jobs,
            'avg_latency': round(sum(latencies) / len(latencies), 2),
            'max_latency': round(max_lat, 2),
            'throughput': round(n_jobs / max(0.001, total_time), 2),
            'load_imbalance': round(imbalance, 2),
        }

    def run_all(self, n_jobs=50):
        return {
            'centralized': self.run_centralized(n_jobs),
            'static': self.run_static(n_jobs),
            'adaptive': self.run_adaptive(n_jobs),
        }


if __name__ == '__main__':
    sim = Simulator()
    results = sim.run_all(30)
    import json
    print(json.dumps(results, indent=2))
