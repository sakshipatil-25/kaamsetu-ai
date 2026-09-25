from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import sys
sys.path.append('src')
sys.path.append('api')
from or_tools_matcher import WorkerMatcher
from simulator import Simulator
import auth as auth_module
import services as research_services

app = FastAPI(title="KaamSetu AI Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

matcher = WorkerMatcher()
simulator = Simulator()


# ============================================================
# Models
# ============================================================
class JobRequest(BaseModel):
    required_skill: str
    latitude: float
    longitude: float
    num_workers_needed: int
    budget: int
    duration_hours: int


class SimulateRequest(BaseModel):
    n_jobs: Optional[int] = 50


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # 'employer' | 'worker' | 'admin'
    phone: Optional[str] = None
    location: Optional[str] = None
    skill: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ============================================================
# Auth dependency
# ============================================================
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.replace('Bearer ', '')
    payload = auth_module.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = auth_module.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ============================================================
# Root & Health
# ============================================================
@app.get("/")
def root():
    return {
        "service": "KaamSetu AI",
        "version": "2.1",
        "endpoints": [
            "/auth/signup", "/auth/login", "/auth/me",
            "/match", "/simulate", "/experiments", "/architecture",
            "/admin/users", "/admin/stats",
            "/jobs", "/jobs/{id}/accept",
            "/research/wage", "/research/travel", "/research/group",
        ],
    }

@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# Auth endpoints
# ============================================================
@app.post("/auth/signup")
def signup(req: SignupRequest):
    if req.role not in ('employer', 'worker', 'admin'):
        raise HTTPException(status_code=400, detail="Invalid role")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user = auth_module.create_user(
        email=req.email.lower().strip(),
        password=req.password,
        full_name=req.full_name,
        role=req.role,
        phone=req.phone,
        location=req.location,
        skill=req.skill,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = auth_module.create_token(user['id'], user['email'], user['role'])
    return {
        "token": token,
        "user": auth_module.user_to_public(user),
    }


@app.post("/auth/login")
def login(req: LoginRequest):
    user = auth_module.get_user_by_email(req.email.lower().strip())
    if not user or not auth_module.verify_password(req.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth_module.create_token(user['id'], user['email'], user['role'])
    return {
        "token": token,
        "user": auth_module.user_to_public(user),
    }


@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return {"user": auth_module.user_to_public(user)}


# ============================================================
# Admin endpoints
# ============================================================
@app.get("/admin/users")
def admin_list_users(role: Optional[str] = None, user: dict = Depends(require_admin)):
    users = auth_module.list_all_users(role_filter=role)
    return {"count": len(users), "users": users}


@app.get("/admin/stats")
def admin_stats(user: dict = Depends(require_admin)):
    all_users = auth_module.list_all_users()
    return {
        "total_users": len(all_users),
        "employers": len([u for u in all_users if u['role'] == 'employer']),
        "workers": len([u for u in all_users if u['role'] == 'worker']),
        "admins": len([u for u in all_users if u['role'] == 'admin']),
    }


# ============================================================
# Existing matching endpoints
# ============================================================
@app.post("/match")
def match_workers(job: JobRequest):
    try:
        job_dict = job.model_dump()
        matched = matcher.match(job_dict)
        return {"matched_workers": matched, "count": len(matched)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate")
def simulate(req: SimulateRequest):
    try:
        n = max(5, min(req.n_jobs, 200))
        results = simulator.run_all(n)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/experiments")
def experiments():
    return {
        "centralized": {
            "setup": "centralized", "nodes": 1,
            "avg_latency": 21.10, "max_latency": 40.0,
            "avg_cpu": 100.0, "max_cpu": 100.0,
            "jobs_processed": 1550, "load_imbalance": 0.0,
        },
        "static": {
            "setup": "static", "nodes": 3,
            "avg_latency": 23.71, "max_latency": 123.18,
            "avg_cpu": 501.05, "max_cpu": 945.80,
            "jobs_processed": 6250, "load_imbalance": 3.2,
        },
        "adaptive": {
            "setup": "adaptive", "nodes": 3,
            "avg_latency": 24.65, "max_latency": 119.13,
            "avg_cpu": 411.53, "max_cpu": 767.80,
            "jobs_processed": 1874, "load_imbalance": 2.1,
        },
    }


@app.get("/architecture")
def architecture():
    return {
        "research_question": "Can adaptive distributed workload management improve real-time AI-based rural workforce matching?",
        "setups": [
            {"name": "Centralized", "nodes": 1, "scheduling": "None — single worker processes all jobs", "kafka_partitions": 1},
            {"name": "Static Distributed", "nodes": 3, "scheduling": "Hash-based Kafka partitioning (job_id % 3)", "kafka_partitions": 3},
            {"name": "Adaptive Distributed", "nodes": 3, "scheduling": "Weighted score (CPU 0.5 + queue 0.3 + latency 0.2)", "kafka_partitions": 3},
        ],
        "frozen_components": ["XGBoost suitability model", "OR-Tools CP-SAT matcher"],
    }
# ============================================================
# Job endpoints
# ============================================================
class JobPostRequest(BaseModel):
    required_skill: str
    num_workers_needed: int
    budget: int
    duration_hours: int
    latitude: Optional[float] = 28.6139
    longitude: Optional[float] = 77.2090


class JobAcceptRequest(BaseModel):
    pass  # Worker identity comes from the JWT token


@app.post("/jobs")
def post_job(req: JobPostRequest, user: dict = Depends(get_current_user)):
    """Employer posts a new job."""
    if user['role'] != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can post jobs")

    # Run the AI matcher to get candidate workers
    job_dict = req.model_dump()
    try:
        matched = matcher.match(job_dict)
    except Exception:
        matched = []

    job = auth_module.create_job(
        employer_id=user['id'],
        employer_name=user['full_name'],
        required_skill=req.required_skill,
        num_workers_needed=req.num_workers_needed,
        budget=req.budget,
        duration_hours=req.duration_hours,
        latitude=req.latitude,
        longitude=req.longitude,
        matched_count=len(matched),
    )
    return {"job": job, "matched_workers": matched}


@app.get("/jobs")
def get_jobs(
    status: Optional[str] = None,
    skill: Optional[str] = None,
    mine: Optional[bool] = False,
    user: dict = Depends(get_current_user),
):
    """List jobs. Workers see all open jobs; employers see their own or all."""
    employer_id = user['id'] if (mine and user['role'] == 'employer') else None

    jobs = auth_module.list_jobs(
        status=status or ('open' if user['role'] == 'worker' else None),
        skill=skill,
        employer_id=employer_id,
    )

    # For workers, sort so their skill matches appear first
    if user['role'] == 'worker' and user.get('skill'):
        worker_skill = user['skill']
        jobs.sort(key=lambda j: 0 if j['required_skill'] == worker_skill else 1)

    # Annotate each job with whether this user has accepted it
    import json as _json
    for j in jobs:
        accepted = _json.loads(j.get('accepted_by') or '[]')
        j['accepted_by_me'] = user['full_name'] in accepted
        j['accepted_count'] = len(accepted)

    return {"count": len(jobs), "jobs": jobs}
@app.post("/jobs/{job_id}/accept")
def accept_job_endpoint(job_id: int, user: dict = Depends(get_current_user)):
    """Worker accepts a job."""
    if user['role'] != 'worker':
        raise HTTPException(status_code=403, detail="Only workers can accept jobs")
    job = auth_module.accept_job(job_id, user['full_name'])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job}

# ============================================================
# Research endpoints — Wage, Travel, Group Matching
# ============================================================
class WageRequest(BaseModel):
    required_skill: str
    duration_hours: int = 8
    num_workers: int = 1
    month: Optional[int] = None


class TravelRequest(BaseModel):
    job_latitude: float
    job_longitude: float
    worker_ids: List[str]


class GroupRequest(BaseModel):
    required_skill: str
    num_workers_needed: int
    budget: int
    male_required: Optional[int] = None
    female_required: Optional[int] = None
    max_distance_km: float = 50.0
    job_latitude: float = 28.6139
    job_longitude: float = 77.2090


@app.post("/research/wage")
def research_wage(req: WageRequest):
    """Estimate expected wage per worker and total labour cost."""
    return research_services.estimate_wage(
        required_skill=req.required_skill,
        duration_hours=req.duration_hours,
        month=req.month,
        num_workers=req.num_workers,
    )


@app.post("/research/travel")
def research_travel(req: TravelRequest):
    """Plan shared transportation for a set of workers going to a job."""
    import pandas as pd
    df = pd.read_csv('data/workers.csv')
    matched = df[df['worker_id'].isin(req.worker_ids)]
    worker_locations = [
        {
            'worker_id': row['worker_id'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
        }
        for _, row in matched.iterrows()
    ]
    return research_services.plan_travel(
        job_lat=req.job_latitude,
        job_lon=req.job_longitude,
        worker_locations=worker_locations,
    )


@app.post("/research/group")
def research_group(req: GroupRequest):
    """
    Multi-constraint group matching.
    Returns the proposed AI solution plus two baselines for comparison.
    """
    import pandas as pd
    df = pd.read_csv('data/workers.csv')
    workers = df.to_dict('records')

    ai_result = research_services.match_group(
        available_workers=workers,
        required_skill=req.required_skill,
        num_workers_needed=req.num_workers_needed,
        budget=req.budget,
        male_required=req.male_required,
        female_required=req.female_required,
        max_distance_km=req.max_distance_km,
        job_lat=req.job_latitude,
        job_lon=req.job_longitude,
    )

    nearest = research_services.nearest_worker_baseline(
        available_workers=workers,
        required_skill=req.required_skill,
        num_workers_needed=req.num_workers_needed,
        job_lat=req.job_latitude,
        job_lon=req.job_longitude,
    )

    skill = research_services.skill_based_baseline(
        available_workers=workers,
        required_skill=req.required_skill,
        num_workers_needed=req.num_workers_needed,
    )

    # Wage estimation for comparison
    wage = research_services.estimate_wage(
        required_skill=req.required_skill,
        duration_hours=8,
        num_workers=req.num_workers_needed,
    )

    return {
        'proposed': ai_result,
        'baseline_nearest': nearest,
        'baseline_skill': skill,
        'wage_estimate': wage,
    }

# ============================================================
# Fair Wage Check
# ============================================================
class FairWageRequest(BaseModel):
    required_skill: str
    num_workers_needed: int
    budget: int
    duration_hours: int = 8


@app.post("/research/fair-wage")
def fair_wage_check(req: FairWageRequest):
    """
    Compare the employer's offered wage against the market reference.
    Returns a warning level and suggested adjustment.
    """
    market = research_services.estimate_wage(
        required_skill=req.required_skill,
        duration_hours=req.duration_hours,
        num_workers=req.num_workers_needed,
    )

    offered_per_worker = req.budget / max(1, req.num_workers_needed)
    market_per_worker = market['per_worker']
    ratio = offered_per_worker / max(1, market_per_worker)

    if ratio >= 0.9:
        status = 'fair'
        message = 'Offered wage is in line with the local market reference.'
    elif ratio >= 0.75:
        status = 'low'
        message = (
            f'Offered wage (₹{int(offered_per_worker)}/worker) is below the local '
            f'market reference (₹{market_per_worker}/worker). Consider increasing '
            f'the budget to attract skilled workers.'
        )
    else:
        status = 'very_low'
        message = (
            f'Offered wage (₹{int(offered_per_worker)}/worker) is significantly below '
            f'the local market reference (₹{market_per_worker}/worker). This may result '
            f'in low worker acceptance.'
        )

    return {
        'status': status,
        'message': message,
        'offered_per_worker': int(offered_per_worker),
        'market_per_worker': market_per_worker,
        'ratio': round(ratio, 2),
        'market_total': market['total'],
        'notes': market['notes'],
    }

# ============================================================
# Digital Work Order / Bill
# ============================================================
class WorkOrderRequest(BaseModel):
    job_id: int


@app.post("/research/work-order")
def generate_work_order(req: WorkOrderRequest, user: dict = Depends(get_current_user)):
    """
    Generate a digital work order with itemized costs.
    Employer-only.
    """
    if user['role'] != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can generate work orders")

    job = auth_module.get_job_by_id(req.job_id)
    if not job or job['employer_id'] != user['id']:
        raise HTTPException(status_code=404, detail="Job not found")

    # Labour cost
    wage = research_services.estimate_wage(
        required_skill=job['required_skill'],
        duration_hours=job['duration_hours'],
        num_workers=job['num_workers_needed'],
    )

    # Travel cost — assume avg 10 km per worker, ₹12/km round trip
    travel_per_worker = 10 * research_services.RURAL_TRAVEL_COST_PER_KM * 2
    total_travel = travel_per_worker * job['num_workers_needed']

    # Platform fee — flat 2% of labour cost (informational)
    platform_fee = int(wage['total'] * 0.02)
    subtotal = wage['total'] + total_travel + platform_fee

    return {
        'work_order_id': f'WO-{job["id"]:05d}',
        'issued_to': user['full_name'],
        'issued_by': 'KaamSetu AI',
        'job': {
            'skill': job['required_skill'],
            'num_workers': job['num_workers_needed'],
            'budget': job['budget'],
            'duration_hours': job['duration_hours'],
            'status': job['status'],
            'created_at': job['created_at'],
        },
        'line_items': [
            {
                'label': f"Labour — {job['num_workers_needed']} workers × {job['duration_hours']} hrs",
                'detail': f"₹{wage['per_worker']} per worker",
                'amount': wage['total'],
            },
            {
                'label': f"Transport — {job['num_workers_needed']} workers (shared)",
                'detail': f"~10 km per trip × ₹{research_services.RURAL_TRAVEL_COST_PER_KM}/km",
                'amount': total_travel,
            },
            {
                'label': 'Platform fee (informational)',
                'detail': '2% of labour cost',
                'amount': platform_fee,
            },
        ],
        'subtotal': subtotal,
        'budget': job['budget'],
        'within_budget': subtotal <= job['budget'],
        'generated_at': str(__import__('datetime').datetime.now()),
        'notes': wage['notes'],
    }

# ============================================================
# Demand Forecasting
# ============================================================
@app.get("/research/forecast")
def demand_forecast(user: dict = Depends(get_current_user)):
    """
    Predict labour demand for the next 7 days based on historical job data,
    season, and skill-specific patterns.
    """
    import pandas as pd
    import datetime

    jobs_df = pd.read_csv('data/jobs.csv')
    current_month = datetime.datetime.now().month

    # Aggregate jobs by skill
    skill_counts = jobs_df['required_skill'].value_counts().to_dict()

    # Seasonal multiplier by skill type
    def season_factor(skill, month):
        # Agriculture peaks during harvest (Sep-Nov)
        if skill.startswith('farming_') or skill == 'soil_preparation':
            if month in (9, 10, 11):
                return 1.4
            elif month in (5, 6, 7):
                return 1.2
            else:
                return 1.0
        # Construction peaks in dry season (Nov-Mar)
        elif skill in ('masonry', 'carpentry', 'painting'):
            if month in (11, 12, 1, 2, 3):
                return 1.25
            else:
                return 1.0
        # Plumbing/electrical steady year-round
        else:
            return 1.0

    forecasts = []
    for skill, base_count in skill_counts.items():
        sf = season_factor(skill, current_month)
        # Predicted demand = base historical × seasonal factor (with slight smoothing)
        predicted = int(base_count * sf * 0.15)  # 15% of annual avg per week
        confidence = 'high' if sf > 1.2 else ('medium' if sf > 1.0 else 'low')
        trend = 'rising' if sf > 1.15 else ('falling' if sf < 0.95 else 'stable')
        forecasts.append({
            'skill': skill,
            'skill_label': skill.replace('_', ' '),
            'historical_jobs': base_count,
            'predicted_next_week': max(1, predicted),
            'season_factor': sf,
            'trend': trend,
            'confidence': confidence,
        })

    # Sort by predicted demand
    forecasts.sort(key=lambda x: -x['predicted_next_week'])

    # Overall insights
    top_skill = forecasts[0] if forecasts else None
    high_demand_count = len([f for f in forecasts if f['trend'] == 'rising'])

    return {
        'forecast_date': str(datetime.date.today()),
        'current_month': current_month,
        'skills': forecasts,
        'summary': {
            'top_skill': top_skill['skill_label'] if top_skill else None,
            'top_skill_demand': top_skill['predicted_next_week'] if top_skill else 0,
            'rising_skills': high_demand_count,
            'total_predicted_jobs': sum(f['predicted_next_week'] for f in forecasts),
        },
        'insight': (
            f"High demand expected for '{top_skill['skill_label']}' next week "
            f"(~{top_skill['predicted_next_week']} jobs). "
            f"{high_demand_count} skill categories are trending upward."
            if top_skill else "No data available yet."
        ),
    }
# ============================================================
# Worker Availability
# ============================================================
class AvailabilityRequest(BaseModel):
    days: List[str]  # e.g. ['Monday', 'Tuesday']


@app.get("/worker/availability")
def get_availability(user: dict = Depends(get_current_user)):
    """Get worker's saved availability."""
    if user['role'] != 'worker':
        raise HTTPException(status_code=403, detail="Worker access required")
    avail = auth_module.get_worker_availability(user['id'])
    return {"days": avail}


@app.post("/worker/availability")
def set_availability(req: AvailabilityRequest, user: dict = Depends(get_current_user)):
    """Save worker's availability."""
    if user['role'] != 'worker':
        raise HTTPException(status_code=403, detail="Worker access required")
    avail = auth_module.set_worker_availability(user['id'], req.days)
    return {"days": avail, "saved": True}