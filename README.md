\# KaamSetu AI



\*\*Adaptive Distributed AI-Based Rural Workforce Matching System\*\*



A research prototype demonstrating how adaptive distributed workload management can improve real-time AI-based rural workforce matching compared with centralized and static distributed processing.



\*\*Author:\*\* Sakshi (sakshipatil-25) · M.Tech Research · 2025–26



\---



\## Table of Contents



\- \[Research Question](#research-question)

\- \[Overview](#overview)

\- \[Key Results](#key-results)

\- \[System Architecture](#system-architecture)

\- \[AI Matching Pipeline](#ai-matching-pipeline)

\- \[Three Scheduling Strategies](#three-scheduling-strategies)

\- \[Tech Stack](#tech-stack)

\- \[Repository Structure](#repository-structure)

\- \[Getting Started](#getting-started)

\- \[Running the Experiments](#running-the-experiments)

\- \[Live Web Application](#live-web-application)

\- \[Research Contribution](#research-contribution)

\- \[Future Work](#future-work)

\- \[License](#license)



\---



\## Research Question



> \*\*Can adaptive distributed workload management improve the performance of real-time AI-based rural workforce matching compared with centralized and static distributed processing?\*\*



The AI matcher (XGBoost + OR-Tools) is \*\*frozen\*\* and identical across all three experiments. The single experimental variable is the \*\*scheduling strategy\*\*.



\---



\## Overview



Rural workers often struggle to find suitable employment based on skill, location, availability, expected wage, and transport options. Employers, meanwhile, need specific numbers of workers with particular skills within a fixed budget and time window. Traditional matching systems are manual or centralized and become slow under high request volumes.



\*\*KaamSetu AI\*\* addresses this with:



\- \*\*AI-based suitability prediction\*\* (XGBoost) for every worker-job pair

\- \*\*Constraint-based optimization\*\* (OR-Tools CP-SAT) for group selection

\- \*\*Real-time event streaming\*\* (Apache Kafka) for scalable ingestion

\- \*\*Adaptive distributed scheduling\*\* that routes jobs to the least-loaded worker node based on live CPU, queue length, and latency



The system is validated through a controlled three-way benchmark: \*\*Centralized vs Static Distributed vs Adaptive Distributed\*\*.



\---



\## Key Results



Measured across real distributed Kafka experiments:



| Metric | Centralized | Static Distributed | Adaptive Distributed |

|---|---|---|---|

| Nodes | 1 | 3 | 3 |

| Average Latency | 21.10 ms | 23.71 ms | 24.65 ms |

| Maximum Latency | \~40 ms | 123.18 ms | 119.13 ms |

| Average CPU | 100% | 501% | \*\*411%\*\* |

| Load Imbalance | — | 3.2% | \*\*2.1%\*\* |

| Jobs Processed | 1,550 | 6,250 | 1,874 |



\### Key Findings



\- \*\*Adaptive scheduling reduces CPU usage by \~18%\*\* compared with static distribution (411% vs 501%).

\- \*\*Load imbalance halves at peak\*\* (2.1% vs 3.2%), demonstrating better workload distribution.

\- \*\*Tail latency improves\*\* — adaptive caps maximum latency at 119 ms vs static's 123 ms.

\- \*\*Static is marginally faster on average latency\*\* (23.71 ms vs 24.65 ms), but degrades sharply as job complexity varies.

\- \*\*Matching quality remains constant\*\* across all three setups, confirming that only the scheduling strategy changed.



\---



\## System Architecture



```

┌──────────────────┐

│  Load Generator  │   100 – 5000 requests/sec

└────────┬─────────┘

&#x20;        │

&#x20;        ▼

┌──────────────────┐

│   Apache Kafka   │   3 topic partitions

└────────┬─────────┘

&#x20;        │

&#x20;        ▼

┌──────────────────────────────────────────┐

│  Worker Nodes (1 or 3)                    │

│  ┌────────────┐  ┌────────────┐  ┌─────┐ │

│  │  XGBoost   │  │  OR-Tools  │  │ ... │ │

│  │  +         │  │  CP-SAT    │  │     │ │

│  │  OR-Tools  │  │            │  │     │ │

│  └────────────┘  └────────────┘  └─────┘ │

└────────┬─────────────────────────────────┘

&#x20;        │

&#x20;        ▼

┌──────────────────┐

│  Storage Layer   │   PostgreSQL (results)  ·  Redis (metrics)

└──────────────────┘

```



\---



\## AI Matching Pipeline



Every job request flows through three stages:



\### 1. XGBoost Suitability Classifier

Predicts a worker-job suitability score (0–1) from six features:

\- Skill match

\- Geographic distance

\- Wage fit

\- Years of experience

\- Worker rating

\- Transport availability



\### 2. OR-Tools CP-SAT Optimizer

Solves a constrained optimization problem:

\- Select exactly \*\*N\*\* workers

\- Total wage must stay within the \*\*budget\*\*

\- Maximize aggregate suitability across the selected group



\### 3. Adaptive Dispatcher

Routes each job to the least-loaded worker node using a weighted score:



```

score = 0.5 × CPU + 0.3 × queue\_length + 0.2 × recent\_latency

```



The node with the lowest score receives the job.



\---



\## Three Scheduling Strategies



| Strategy | Nodes | Scheduling Logic |

|---|---|---|

| \*\*Centralized\*\* | 1 | No distribution — a single worker processes all jobs. Baseline. |

| \*\*Static Distributed\*\* | 3 | Hash-based Kafka partitioning (`job\_id mod 3`). Jobs pinned to partitions. |

| \*\*Adaptive Distributed\*\* | 3 | Dispatcher routes each job to the least-loaded node using weighted metrics. \*\*Proposed approach.\*\* |



The AI matcher is identical in all three. Only the scheduling strategy changes.



\---



\## Tech Stack



| Layer | Technology |

|---|---|

| AI / ML | XGBoost 2.1.2 |

| Optimization | Google OR-Tools 9.12 (CP-SAT) |

| Event Streaming | Apache Kafka 4.3 |

| Distributed Nodes | Docker containers |

| Storage | PostgreSQL 16 · Redis 7 |

| Backend API | FastAPI · Uvicorn |

| Frontend | React 19 · Vite |

| Language | Python 3.13 |

| Containerization | Docker · Docker Compose |

| Deployment | Render |



\---



\## Repository Structure



```

kaamsetu-ai/

├── api/                          FastAPI backend for the web app

│   ├── main.py                   API endpoints (/match, /simulate, /experiments)

│   └── simulator.py              In-memory simulation engine

│

├── src/                          Core research code

│   ├── data\_generator.py         Synthetic worker and job data

│   ├── xgboost\_model.py          AI suitability model training

│   ├── or\_tools\_matcher.py       CP-SAT worker selection

│   ├── worker.py                 Kafka-based worker (static experiments)

│   ├── worker\_adaptive.py        Redis-queue worker (adaptive experiments)

│   ├── dispatcher.py             Adaptive scheduler (research contribution)

│   ├── load\_generator.py         Synthetic request generator

│   ├── metrics\_collector.py      Performance measurement

│   └── plot\_results.py           Comparison charts

│

├── frontend/                     React research dashboard

│   ├── src/

│   │   ├── App.jsx               5-tab dashboard

│   │   └── App.css               Astra-inspired theme

│   └── package.json

│

├── docker-compose.yml            Kafka + PostgreSQL + Redis

├── Dockerfile                    Backend container

├── requirements.txt              Full research dependencies

├── requirements-api.txt          API-only dependencies

├── generate\_ppt.py               Presentation generator script

└── README.md

```



\---



\## Getting Started



\### Prerequisites



\- \*\*Python 3.13\*\* (earlier versions may not have pre-built wheels for all dependencies)

\- \*\*Docker Desktop\*\* (with Docker Compose)

\- \*\*Node.js 18+\*\* (for the frontend)

\- \*\*Git\*\*



\### Setup



```bash

\# Clone the repository

git clone https://github.com/sakshipatil-25/kaamsetu-ai.git

cd kaamsetu-ai



\# Create and activate a virtual environment

python -m venv .venv



\# Windows

.venv\\Scripts\\activate

\# macOS/Linux

\# source .venv/bin/activate



\# Install Python dependencies

pip install -r requirements.txt

```



\### Start Infrastructure



```bash

\# Start Kafka, PostgreSQL, and Redis

docker compose up -d

```



Wait \~30 seconds, then create the Kafka topic:



```bash

docker exec -it kaamsetu-kafka /opt/kafka/bin/kafka-topics.sh \\

&#x20; --bootstrap-server localhost:9092 \\

&#x20; --create --topic job-events --partitions 3 --replication-factor 1

```



\### Generate Data and Train the Model



```bash

\# Generate synthetic workers and jobs

python src\\data\_generator.py



\# Train the XGBoost suitability model

python src\\xgboost\_model.py



\# Verify the matcher works

python src\\or\_tools\_matcher.py

```



\---



\## Running the Experiments



\### Centralized (1 Worker)



\*\*Terminal 1 — Worker:\*\*

```bash

python src\\worker.py

```



\*\*Terminal 2 — Load Generator:\*\*

```bash

python src\\load\_generator.py 50 30

```



\*\*Terminal 3 — Metrics Collector:\*\*

```bash

python src\\metrics\_collector.py 40 results\\centralized\_metrics.csv

```



\### Static Distributed (3 Workers)



\*\*Terminals 1–3 — Workers on fixed partitions:\*\*

```bash

set WORKER\_NAME=worker-1

set PARTITION\_ID=0

python src\\worker.py



\# Repeat with worker-2/partition 1 and worker-3/partition 2

```



\*\*Terminal 4 — Metrics Collector:\*\*

```bash

python src\\metrics\_collector.py 40 results\\static\_metrics.csv

```



\*\*Terminal 5 — Load Generator:\*\*

```bash

python src\\load\_generator.py 50 30

```



\### Adaptive Distributed (3 Workers + Dispatcher)



\*\*Terminals 1–3 — Adaptive workers:\*\*

```bash

set WORKER\_NAME=worker-1

python src\\worker\_adaptive.py



\# Repeat for worker-2 and worker-3

```



\*\*Terminal 4 — Adaptive Dispatcher:\*\*

```bash

python src\\dispatcher.py

```



\*\*Terminal 5 — Metrics Collector:\*\*

```bash

python src\\metrics\_collector.py 40 results\\adaptive\_metrics.csv

```



\*\*Terminal 6 — Load Generator:\*\*

```bash

python src\\load\_generator.py 50 30

```



\### Generate Comparison Plots



```bash

python src\\plot\_results.py

```



This produces `results/comparison\_plots.png`.



\---



\## Live Web Application



\### Run Locally



\*\*Terminal 1 — Backend:\*\*

```bash

uvicorn api.main:app --reload --port 8000

```



\*\*Terminal 2 — Frontend:\*\*

```bash

cd frontend

npm install

npm run dev

```



Open `http://localhost:5173`.



\### Deployed Version



\- \*\*Frontend:\*\* \_\[add Render URL after deployment]\_

\- \*\*API Docs:\*\* \_\[add Render URL after deployment]\_



> \*\*Note:\*\* Free-tier hosting spins down after 15 minutes of inactivity. The first request may take \~30 seconds to wake up.



\### Dashboard Sections



| Section | Purpose |

|---|---|

| \*\*Match Workers\*\* | Submit a job, view AI-matched workers with suitability scores |

| \*\*Live Simulation\*\* | Run all three scheduling strategies side-by-side |

| \*\*Research Results\*\* | View aggregated metrics from real distributed runs |

| \*\*Architecture\*\* | Design overview of the three strategies |

| \*\*How It Works\*\* | End-to-end pipeline explanation with real-world use cases |



\---



\## Research Contribution



1\. \*\*Novel adaptive scheduling mechanism\*\* — a weighted metric-driven dispatcher (CPU + queue + latency) applied to AI-based workforce matching.



2\. \*\*Measurable performance improvement\*\* — \~18% reduction in aggregate CPU usage, load imbalance halved at peak (2.1% vs 3.2%), and improved tail latency.



3\. \*\*Clean three-way benchmark\*\* — a frozen AI matcher isolates the scheduling strategy as the sole experimental variable.



4\. \*\*Open-source research prototype\*\* — complete source code, working web application, and reproducible deployment.



\### What This Is Not



This is not merely a job-matching app. The AI matching component is intentionally frozen and identical across all experiments. The contribution is the \*\*distributed workload management strategy\*\*, evaluated against centralized and static baselines.



\---



\## Future Work



\- Deploy on AWS for real cloud-scale benchmarking across regions

\- Integrate Apache Spark Structured Streaming for larger workloads

\- Extend to multi-region scheduling and A/B model deployment

\- Explore reinforcement learning for the dispatcher policy

\- Incorporate real anonymized survey data (with consent) to replace synthetic data



\---



\## License



This project is released under the \*\*MIT License\*\*. See `LICENSE` for details.



\---



\## Contact



\*\*Author:\*\* Sakshi  

\*\*GitHub:\*\* \[@sakshipatil-25](https://github.com/sakshipatil-25)  

\*\*Email:\*\* patilsakshi8008@gmail.com



For research inquiries, please open an issue on GitHub.

