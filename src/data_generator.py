import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

SKILLS = [
    'farming_seeds',      # Hand-planting seeds
    'farming_pruning',    # Pruning plants
    'farming_weeding',    # Weeding
    'farming_thinning',   # Thinning
    'farming_harvesting', # Hand-harvesting delicate crops
    'soil_preparation',   # Soil preparation
    'plumbing',
    'electrical',
    'carpentry',
    'painting',
    'masonry',
    'welding',
    'cleaning',
]

def generate_workers(n=1000):
    workers = []
    for i in range(n):
        workers.append({
            'worker_id': f'W{i:05d}',
            'skill': random.choice(SKILLS),
            'experience_years': random.randint(0, 30),
            'latitude': 28.6139 + random.uniform(-0.5, 0.5),
            'longitude': 77.2090 + random.uniform(-0.5, 0.5),
            'availability': random.choice(['morning', 'afternoon', 'evening', 'full_day']),
            'expected_wage': random.randint(300, 1500),
            'rating': round(random.uniform(2.5, 5.0), 1),
            'has_transport': random.choice([True, False])
        })
    return pd.DataFrame(workers)

def generate_jobs(n=500):
    jobs = []
    for i in range(n):
        jobs.append({
            'job_id': f'J{i:05d}',
            'required_skill': random.choice(SKILLS),
            'latitude': 28.6139 + random.uniform(-0.3, 0.3),
            'longitude': 77.2090 + random.uniform(-0.3, 0.3),
            'num_workers_needed': random.randint(1, 5),
            'budget': random.randint(1000, 10000),
            'duration_hours': random.randint(2, 12),
            'job_date': str(fake.date_this_month()),
            'job_time': random.choice(['08:00', '10:00', '12:00', '14:00', '16:00'])
        })
    return pd.DataFrame(jobs)

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    
    print("Generating workers...")
    workers = generate_workers(1000)
    workers.to_csv('data/workers.csv', index=False)
    print(f"Saved {len(workers)} workers to data/workers.csv")
    
    print("Generating jobs...")
    jobs = generate_jobs(500)
    jobs.to_csv('data/jobs.csv', index=False)
    print(f"Saved {len(jobs)} jobs to data/jobs.csv")
    
    print("\nSample worker:")
    print(workers.head(2))
    print("\nSample job:")
    print(jobs.head(2))