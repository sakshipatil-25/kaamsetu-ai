from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append('src')
sys.path.append('api')
from or_tools_matcher import WorkerMatcher
from simulator import Simulator

app = FastAPI(title="KaamSetu AI Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kaamsetu-frontend.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

matcher = WorkerMatcher()
simulator = Simulator()


class JobRequest(BaseModel):
    required_skill: str
    latitude: float
    longitude: float
    num_workers_needed: int
    budget: int
    duration_hours: int


class SimulateRequest(BaseModel):
    n_jobs: Optional[int] = 50


@app.get("/")
def root():
    return {
        "service": "KaamSetu AI",
        "version": "1.0",
        "endpoints": ["/match", "/simulate", "/experiments", "/architecture"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


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
            "setup": "centralized",
            "nodes": 1,
            "avg_latency": 21.10,
            "max_latency": 40.0,
            "avg_cpu": 100.0,
            "max_cpu": 100.0,
            "jobs_processed": 1550,
            "load_imbalance": 0.0,
        },
        "static": {
            "setup": "static",
            "nodes": 3,
            "avg_latency": 23.71,
            "max_latency": 123.18,
            "avg_cpu": 501.05,
            "max_cpu": 945.80,
            "jobs_processed": 6250,
            "load_imbalance": 3.2,
        },
        "adaptive": {
            "setup": "adaptive",
            "nodes": 3,
            "avg_latency": 24.65,
            "max_latency": 119.13,
            "avg_cpu": 411.53,
            "max_cpu": 767.80,
            "jobs_processed": 1874,
            "load_imbalance": 2.1,
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