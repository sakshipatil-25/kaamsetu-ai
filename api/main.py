from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import sys
sys.path.append('src')
sys.path.append('api')
from or_tools_matcher import WorkerMatcher
from simulator import Simulator
import auth as auth_module

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
        "version": "2.0",
        "endpoints": [
            "/auth/signup", "/auth/login", "/auth/me",
            "/match", "/simulate", "/experiments", "/architecture",
            "/admin/users", "/admin/stats"
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