from ortools.sat.python import cp_model
import joblib
import numpy as np
import pandas as pd
import os

class WorkerMatcher:
    def __init__(self, model_path='models/xgboost_suitability.pkl'):
        self.model = joblib.load(model_path)
        self.workers_df = pd.read_csv('data/workers.csv')
    
    def _features(self, worker, job):
        """Build feature vector for XGBoost."""
        skill_match = 1 if worker['skill'] == job['required_skill'] else 0
        dist = np.sqrt((worker['latitude'] - job['latitude'])**2 + 
                       (worker['longitude'] - job['longitude'])**2)
        wage_fit = 1 if worker['expected_wage'] <= job['budget'] / job['num_workers_needed'] else 0
        return np.array([[
            skill_match,
            dist,
            wage_fit,
            worker['experience_years'],
            worker['rating'],
            int(worker['has_transport'])
        ]])
    
    def match(self, job, max_candidates=30):
        """Select optimal workers for a job using XGBoost + CP-SAT."""
        # Step 1: Filter candidates by skill
        candidates = self.workers_df[
            self.workers_df['skill'] == job['required_skill']
        ].head(max_candidates).reset_index(drop=True)
        
        if len(candidates) == 0:
            return []
        
        # Step 2: Get suitability scores from XGBoost
        scores = []
        for _, worker in candidates.iterrows():
            features = self._features(worker, job)
            scores.append(float(self.model.predict(features)[0]))
        
        # Step 3: CP-SAT optimization
        model = cp_model.CpModel()
        n = len(candidates)
        x = [model.NewBoolVar(f'w{i}') for i in range(n)]
        
        # Constraint: exactly num_workers_needed selected
        num_needed = min(job['num_workers_needed'], n)
        model.Add(sum(x) == num_needed)
        
        # Constraint: total wages within budget
        wages = candidates['expected_wage'].values
        # Scale to integers for CP-SAT
        scaled_wages = [int(w * 100) for w in wages]
        scaled_budget = int(job['budget'] * 100)
        model.Add(sum(x[i] * scaled_wages[i] for i in range(n)) <= scaled_budget)
        
        # Objective: maximize total suitability (scale to int)
        scaled_scores = [int(s * 10000) for s in scores]
        model.Maximize(sum(x[i] * scaled_scores[i] for i in range(n)))
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2.0
        solver.parameters.num_search_workers = 1  # Deterministic
        status = solver.Solve(model)
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            selected = [
                {
                    'worker_id': candidates.iloc[i]['worker_id'],
                    'suitability_score': scores[i]
                }
                for i in range(n) if solver.Value(x[i]) == 1
            ]
            return selected
        return []


if __name__ == "__main__":
    print("Testing OR-Tools matcher...")
    matcher = WorkerMatcher()
    
    # Test with one sample job
    jobs = pd.read_csv('data/jobs.csv')
    sample_job = jobs.iloc[0].to_dict()
    print(f"\nSample job: {sample_job['job_id']}")
    print(f"Required skill: {sample_job['required_skill']}")
    print(f"Workers needed: {sample_job['num_workers_needed']}")
    print(f"Budget: {sample_job['budget']}")
    
    import time
    start = time.perf_counter()
    matched = matcher.match(sample_job)
    latency = (time.perf_counter() - start) * 1000
    
    print(f"\nMatched {len(matched)} workers in {latency:.1f}ms:")
    for m in matched:
        print(f"  {m['worker_id']} - suitability: {m['suitability_score']:.3f}")