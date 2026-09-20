import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import joblib
import os

np.random.seed(42)

def create_training_data(workers, jobs, max_pairs_per_job=50):
    """Create worker-job pairs with suitability labels."""
    pairs = []
    
    for _, job in jobs.iterrows():
        # Filter workers with matching skill for efficiency
        candidates = workers[workers['skill'] == job['required_skill']].head(max_pairs_per_job)
        
        for _, worker in candidates.iterrows():
            skill_match = 1  # Already filtered
            dist = np.sqrt((worker['latitude'] - job['latitude'])**2 + 
                          (worker['longitude'] - job['longitude'])**2)
            wage_fit = 1 if worker['expected_wage'] <= job['budget'] / job['num_workers_needed'] else 0
            
            suitability = (0.4 * skill_match + 
                          0.3 * (1 - min(dist, 1)) + 
                          0.2 * wage_fit + 
                          0.1 * (worker['rating'] / 5.0))
            
            pairs.append({
                'skill_match': skill_match,
                'distance': dist,
                'wage_fit': wage_fit,
                'experience': worker['experience_years'],
                'rating': worker['rating'],
                'has_transport': int(worker['has_transport']),
                'suitability': suitability
            })
    
    return pd.DataFrame(pairs)

if __name__ == "__main__":
    os.makedirs('models', exist_ok=True)
    
    print("Loading data...")
    workers = pd.read_csv('data/workers.csv')
    jobs = pd.read_csv('data/jobs.csv')
    
    print("Creating training pairs...")
    data = create_training_data(workers, jobs)
    print(f"Created {len(data)} worker-job pairs")
    
    X = data[['skill_match', 'distance', 'wage_fit', 'experience', 
              'rating', 'has_transport']]
    y = data['suitability']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Train R2: {train_score:.4f}")
    print(f"Test R2: {test_score:.4f}")
    
    joblib.dump(model, 'models/xgboost_suitability.pkl')
    print("Model saved to models/xgboost_suitability.pkl")