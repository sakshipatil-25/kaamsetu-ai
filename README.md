# KaamSetu AI

**An Intelligent Distributed Platform for Real-Time Rural Workforce Matching, Wage Estimation, and Resource Coordination**

A full-stack M.Tech research prototype demonstrating multi-constraint AI matching, adaptive distributed scheduling, wage estimation, and demand forecasting for rural workforce coordination.

**Author:** Sakshi (sakshipatil-25) · M.Tech Research · 2025–26

**Live Deployment:** https://kaamsetu-frontend.onrender.com

---

## Table of Contents

- [Research Objective](#research-objective)
- [What This Platform Does](#what-this-platform-does)
- [Live Demo](#live-demo)
- [Key Features](#key-features)
- [Research Design](#research-design)
- [Experimental Results](#experimental-results)
- [System Architecture](#system-architecture)
- [Multi-Constraint Optimization](#multi-constraint-optimization)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Running Experiments](#running-experiments)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Research Objective

> **Can an AI-based multi-constraint matching and optimization model improve rural worker-employer matching by reducing total hiring cost, travel distance, and matching time while satisfying skill, availability, and workforce requirements?**

The **AI matcher** (XGBoost + OR-Tools) is **frozen** and identical across all experiments. The single experimental variable is the **scheduling strategy**.

---

## What This Platform Does

KaamSetu AI is an intelligent platform connecting rural workers with employers through:

1. **AI-powered multi-constraint matching** — XGBoost predicts suitability, OR-Tools CP-SAT selects optimal groups
2. **Adaptive distributed scheduling** — Apache Kafka streams jobs across multiple worker nodes with load-aware routing
3. **Wage estimation** — Season and complexity-aware market wage prediction
4. **Travel planning** — Groups workers by proximity into shared vehicles
5. **Fair wage warnings** — Alerts employers when their offer is below market rate
6. **Digital work orders** — Itemized invoices with labour, transport, and platform costs
7. **Demand forecasting** — Predicts seasonal labour demand by skill category
8. **Worker availability tracking** — Persistent day-by-day availability

---

## Live Demo

**Try it now:** https://kaamsetu-frontend.onrender.com

### Demo Accounts

| Role | Email | Password | Can Do |
|---|---|---|---|
| **Employer** | `employer@demo.com` | `demo123` | Post jobs, view AI matches, generate work orders, view demand forecast |
| **Worker** | `worker@demo.com` | `demo123` | Browse jobs, accept work, update availability |
| **Admin** | `admin@demo.com` | `demo123` | System statistics, user management, run simulations |

> **Note:** Free-tier hosting sleeps after 15 minutes of inactivity. First request may take ~30–45 seconds to wake up.

**API Docs:** https://kaamsetu-api-y0yc.onrender.com/docs

---

## Key Features

### 1. AI-Powered Worker Matching

Given a job request (skill, location, workers needed, budget, duration), the system:
- Filters 1,000 workers by skill and distance
- Scores each candidate with an XGBoost classifier (six features: skill match, distance, wage fit, experience, rating, transport availability)
- Selects the optimal group using OR-Tools CP-SAT under skill, budget, and headcount constraints
- Returns workers ranked by suitability score

**Typical latency:** 15–25 ms per job

### 2. Adaptive Distributed Scheduling

Three scheduling strategies are implemented and experimentally compared:
- **Centralized** — single worker node processes all jobs
- **Static Distributed** — hash-based Kafka partitioning (job_id mod 3)
- **Adaptive Distributed** — weighted dispatcher (0.5×CPU + 0.3×queue + 0.2×latency)

### 3. Wage Estimation

Predicts per-worker and total labour cost from:
- **Base wage** by skill (e.g., farming_harvesting: ₹500, electrical: ₹850)
- **Seasonal factor** (agricultural harvest peaks in Sep–Nov at ×1.2–1.4)
- **Complexity factor** (short jobs ×0.9, medium ×1.0, long ×1.15)

### 4. Travel Planning

Uses the Haversine formula to compute distances, then:
- Groups workers into shared vehicles (capacity 6)
- Picks a centroid pickup point per vehicle
- Estimates round-trip transportation cost (₹12/km)

### 5. Fair Wage Warning

Compares the employer's offered wage against the market reference. Flags:
- **Green** if offer ≥ 90% of market
- **Yellow** if 75–90% of market
- **Red** if < 75% of market

### 6. Digital Work Order

Generates an itemized invoice with:
- Labour cost (per-worker × count × hours)
- Transportation cost (shared vehicle estimate)
- Platform fee (2%, informational)
- Budget comparison (within budget / exceeds by ₹X)
- Print/PDF export

### 7. Demand Forecasting

Analyzes historical job data with seasonal multipliers to predict next-week demand by skill. Flags rising/stable/falling trends with confidence levels.

### 8. Worker Availability

Workers can mark which days they're available. Saves to SQLite and persists across sessions.

### 9. Three-Role Access Control

JWT-based authentication with three distinct interfaces:
- **Employer** — job posting, matching, work orders, forecasting
- **Worker** — job browsing, acceptance, availability
- **Admin** — user management, system statistics, simulations

### 10. Multi-Constraint Optimization with Baselines

The proposed optimizer is benchmarked against two baselines:
- **Nearest-Worker** — picks N nearest workers with the required skill
- **Skill-Based** — picks top-rated workers with the required skill

---

## Research Design

The study compares three scheduling strategies with an identical AI matcher:

| Setup | Nodes | Scheduling Logic |
|---|---|---|
| Centralized | 1 | Single worker processes all jobs |
| Static Distributed | 3 | Hash-based Kafka partitioning |
| Adaptive Distributed | 3 | Weighted dispatcher (CPU + queue + latency) |

### Evaluation Metrics

**Distributed computing:**
- End-to-end latency (average, maximum)
- Throughput (jobs/sec)
- CPU and memory utilization
- Load imbalance across nodes
- Scalability and network overhead

**Matching quality:**
- Matching success rate
- Skill-match score
- Constraint violations
- Average travel distance
- Total labour cost

**Optimization:**
- Wage savings vs baselines
- Distance savings vs baselines

---

## Experimental Results

### Scheduling Strategy Comparison

| Metric | Centralized | Static | Adaptive |
|---|---|---|---|
| Nodes | 1 | 3 | 3 |
| Average Latency | 21.10 ms | 23.71 ms | 24.65 ms |
| Maximum Latency | ~40 ms | 123.18 ms | 119.13 ms |
| Average CPU | 100% | 501% | **411%** |
| Load Imbalance | — | 3.2% | **2.1%** |
| Jobs Processed | 1,550 | 6,250 | 1,874 |

**Key findings:**
- Adaptive scheduling reduces CPU usage by ~18% compared to static (411% vs 501%)
- Adaptive achieves 2.1% load imbalance vs static's 3.2%
- Adaptive caps tail latency better (119 ms vs 123 ms)
- Centralized achieves lowest per-job latency but no horizontal scaling

### Multi-Constraint Optimization vs Baselines

Sample comparison (3 workers, painting job, ₹5,000 budget):

| Strategy | Workers | Total Wage | Avg Distance |
|---|---|---|---|
| **Multi-Constraint AI** (proposed) | 3 | ₹1,786 | 7.21 km |
| Nearest Worker | 3 | ₹2,355 | 3.83 km |
| Skill-Based | 3 | ₹1,862 | — |

**Finding:** The proposed multi-constraint optimizer reduces total wage by ~24% vs the nearest-worker baseline and ~4% vs the skill-based baseline, while maintaining acceptable distance.

---

## System Architecture

```
                     ┌──────────────────────┐
                     │   React Frontend     │
                     │  (Landing + App + Auth)
                     └──────────┬───────────┘
                                │ REST API
                                ▼
                     ┌──────────────────────┐
                     │   FastAPI Backend    │
                     │  ┌────────────────┐  │
                     │  │ XGBoost +      │  │
                     │  │ OR-Tools       │  │
                     │  └────────────────┘  │
                     │  ┌────────────────┐  │
                     │  │ Research       │  │
                     │  │ Services       │  │
                     │  │ (Wage, Travel, │  │
                     │  │  Forecast)     │  │
                     │  └────────────────┘  │
                     └──────────┬───────────┘
                                │
                     ┌──────────┴───────────┐
                     │   SQLite (users,     │
                     │    jobs, availability)
                     └──────────────────────┘
```

**Experimental setup (local + deployable via Docker):**
```
Load Generator → Apache Kafka (3 partitions) → Worker Nodes (1 or 3)
                                                    ↓
                                          PostgreSQL + Redis
```

---

## Multi-Constraint Optimization

The core research algorithm minimizes:

```
Cost = α·W + β·D + γ·T + δ·M
```

Where:
- `W` = total wage
- `D` = travel distance
- `T` = transportation cost
- `M` = mismatch penalty

**Subject to:**
- `WorkersSelected = WorkersRequired`
- `SkillMatch ≥ RequiredSkill`
- `Availability = 1`
- Gender ratio constraints (optional)
- Distance ≤ max_distance_km

The optimizer uses a scoring function:
```
score(w) = 0.5 × expected_wage + 0.3 × distance × 100 + 0.2 × (5 - rating) × 100
```

Workers with the lowest scores are selected.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **AI / ML** | XGBoost 2.1.2 |
| **Optimization** | Google OR-Tools 9.12 (CP-SAT) |
| **Event Streaming** | Apache Kafka 4.3 |
| **Distributed Nodes** | Docker containers |
| **Data Storage** | SQLite (users/jobs), PostgreSQL 16 (experimental metrics), Redis 7 |
| **Backend API** | FastAPI · Uvicorn |
| **Authentication** | JWT (PyJWT) · bcrypt |
| **Frontend** | React 19 · Vite · React Router |
| **Language** | Python 3.13 |
| **Containerization** | Docker · Docker Compose |
| **Deployment** | Render (backend + static frontend) |

---

## Repository Structure

```
kaamsetu-ai/
├── api/                          FastAPI backend
│   ├── main.py                   All API endpoints
│   ├── auth.py                   JWT auth + users/jobs DB
│   ├── services.py               Research services (wage, travel, matching)
│   └── simulator.py              In-memory scheduling simulator
│
├── src/                          Core research code
│   ├── data_generator.py         Synthetic worker/job data
│   ├── xgboost_model.py          AI suitability training
│   ├── or_tools_matcher.py       CP-SAT worker selection
│   ├── worker.py                 Kafka-based worker (static)
│   ├── worker_adaptive.py        Redis-queue worker (adaptive)
│   ├── dispatcher.py             Adaptive scheduler
│   ├── load_generator.py         Request generator
│   ├── metrics_collector.py      Performance measurement
│   └── plot_results.py           Comparison charts
│
├── frontend/                     React dashboard
│   └── src/
│       ├── Landing.jsx           Marketing landing page
│       ├── Login.jsx             Authentication
│       ├── Signup.jsx            Registration
│       ├── App.jsx               Main dashboard (role-based)
│       ├── ResearchPanels.jsx    Wage / Travel / Group matching panels
│       ├── FairWagePanel.jsx     Fair wage warning
│       ├── WorkOrderModal.jsx    Digital work order
│       ├── DemandForecast.jsx    Forecast page
│       └── auth.js               Auth helpers + JWT storage
│
├── data/                         Generated datasets
│   ├── workers.csv               1,000 workers (13 skills, gender, age)
│   ├── jobs.csv                  500 jobs
│   └── users.db                  SQLite (users + jobs + availability)
│
├── models/                       Trained AI model
│   └── xgboost_suitability.pkl   Frozen XGBoost model
│
├── results/                      Experiment outputs
│   ├── centralized_metrics.csv
│   ├── static_metrics.csv
│   ├── adaptive_metrics.csv
│   └── comparison_plots.png
│
├── docker-compose.yml            Kafka + PostgreSQL + Redis
├── Dockerfile                    Backend container
├── requirements.txt              Full research dependencies
├── requirements-api.txt          API-only dependencies
├── generate_ppt.py               Presentation generator
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.13
- Docker Desktop
- Node.js 18+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/sakshipatil-25/kaamsetu-ai.git
cd kaamsetu-ai

# Create and activate a Python virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic data (only needed once)
python src\data_generator.py

# Train the XGBoost model (only needed once)
python src\xgboost_model.py
```

### Run Locally

**Terminal 1 — Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## Running Experiments

### Centralized Baseline

```bash
# Terminal 1
python src\worker.py

# Terminal 2
python src\load_generator.py 50 30

# Terminal 3
python src\metrics_collector.py 40 results\centralized_metrics.csv
```

### Static Distributed

```bash
# Terminals 1-3 (one per partition)
set WORKER_NAME=worker-1
set PARTITION_ID=0
python src\worker.py
# Repeat for worker-2/partition 1, worker-3/partition 2
```

### Adaptive Distributed

```bash
# Terminals 1-3
set WORKER_NAME=worker-1
python src\worker_adaptive.py
# Repeat for worker-2 and worker-3

# Terminal 4 — Dispatcher
python src\dispatcher.py

# Terminal 5 — Load
python src\load_generator.py 50 30
```

### Generate Comparison Plots

```bash
python src\plot_results.py
```

Produces `results/comparison_plots.png`.

---

## Documentation

| Document | Purpose |
|---|---|
| `README.md` | This file — project overview |
| `KaamSetu_AI_Presentation.pptx` | Research presentation (14 slides) |
| `/docs` (Swagger) | Interactive API explorer |
| Source code comments | Inline documentation |

---

## Contributing

This is a research prototype. For questions or collaboration:

- Open an issue on GitHub
- Contact the author via the email listed in commits

---

## License

MIT License — see `LICENSE` file for details.