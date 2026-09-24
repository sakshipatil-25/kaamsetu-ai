"""
KaamSetu AI — Research Services
Wage estimation, travel planning, and group matching.

These implement the multi-constraint optimization described in the research proposal:
    Minimize:  αW + βD + γT + δM
    where:
        W = total wage
        D = travel distance
        T = transportation cost
        M = mismatch penalty
    subject to:
        WorkersSelected = WorkersRequired
        SkillMatch ≥ RequiredSkill
        Availability = 1
        Gender/age constraints (optional)
"""
import math
from typing import List, Dict, Optional


# ============================================================
# 1. WAGE ESTIMATION
# ============================================================

# Base daily wage by skill (₹, market reference for rural Maharashtra)
BASE_WAGE = {
    'farming_seeds':      450,
    'farming_pruning':    450,
    'farming_weeding':    400,
    'farming_thinning':   400,
    'farming_harvesting': 500,
    'soil_preparation':   420,
    'plumbing':           800,
    'electrical':         850,
    'carpentry':          750,
    'painting':           650,
    'masonry':            700,
    'welding':            900,
    'cleaning':           350,
}

# Seasonal multiplier (agriculture peaks during harvest)
SEASONAL_MULTIPLIER = {
    1: 0.95,   # Jan
    2: 0.95,
    3: 1.00,   # Mar
    4: 1.05,   # Apr
    5: 1.10,   # May
    6: 1.15,   # Jun (monsoon start)
    7: 1.10,   # Jul
    8: 1.05,   # Aug
    9: 1.15,   # Sep (harvest)
    10: 1.20,  # Oct (peak harvest)
    11: 1.10,  # Nov
    12: 1.00,  # Dec
}

# Work complexity multiplier (based on duration/area)
COMPLEXITY_MULTIPLIER = {
    'small':  0.9,   # <= 4 hours
    'medium': 1.0,   # 5-8 hours
    'large':  1.15,  # > 8 hours
}


def estimate_wage(required_skill: str, duration_hours: int = 8,
                  month: Optional[int] = None, num_workers: int = 1) -> Dict:
    """
    Estimate expected wage per worker and total labour cost.

    Returns:
        {
            'per_worker': int,       # ₹ per worker
            'total': int,            # ₹ total
            'base_wage': int,
            'seasonal_factor': float,
            'complexity_factor': float,
            'notes': [str]           # reasoning
        }
    """
    base = BASE_WAGE.get(required_skill, 500)

    if month is None:
        import datetime
        month = datetime.datetime.now().month
    seasonal = SEASONAL_MULTIPLIER.get(month, 1.0)

    if duration_hours <= 4:
        complexity_key = 'small'
    elif duration_hours <= 8:
        complexity_key = 'medium'
    else:
        complexity_key = 'large'
    complexity = COMPLEXITY_MULTIPLIER[complexity_key]

    # Compute final
    per_worker = int(round(base * seasonal * complexity, -1))  # round to 10s
    total = per_worker * num_workers

    notes = [
        f"Base wage for '{required_skill.replace('_', ' ')}': ₹{base}",
        f"Seasonal factor (month {month}): ×{seasonal}",
        f"Complexity factor ({duration_hours}h): ×{complexity}",
    ]

    return {
        'per_worker': per_worker,
        'total': total,
        'base_wage': base,
        'seasonal_factor': seasonal,
        'complexity_factor': complexity,
        'notes': notes,
    }


# ============================================================
# 2. TRAVEL MATCHING
# ============================================================

# Cost per km for shared rural transport (₹)
RURAL_TRAVEL_COST_PER_KM = 12

# Vehicle capacity (workers per shared vehicle)
VEHICLE_CAPACITY = 6


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two points in km using the Haversine formula."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def plan_travel(job_lat: float, job_lon: float,
                worker_locations: List[Dict]) -> Dict:
    """
    Given a job location and a list of worker locations, group workers by
    proximity into shared vehicles and compute travel cost.

    worker_locations: [{'worker_id': str, 'latitude': float, 'longitude': float}, ...]

    Returns:
        {
            'total_distance_km': float,
            'avg_distance_km': float,
            'total_cost': int,
            'vehicles_needed': int,
            'groups': [
                {
                    'vehicle': int,
                    'workers': [str],
                    'pickup_point': {'lat': float, 'lon': float},
                    'distance_to_job_km': float,
                    'cost': int
                },
                ...
            ]
        }
    """
    if not worker_locations:
        return {
            'total_distance_km': 0, 'avg_distance_km': 0,
            'total_cost': 0, 'vehicles_needed': 0, 'groups': []
        }

    # Compute distance from each worker to the job
    enriched = []
    for w in worker_locations:
        d = haversine_km(w['latitude'], w['longitude'], job_lat, job_lon)
        enriched.append({**w, 'distance_to_job': d})

    # Sort by distance and greedily group into vehicles
    enriched.sort(key=lambda x: x['distance_to_job'])
    groups = []
    vehicle_num = 1
    for i in range(0, len(enriched), VEHICLE_CAPACITY):
        chunk = enriched[i:i + VEHICLE_CAPACITY]
        # Pickup point = centroid of workers in this vehicle
        avg_lat = sum(w['latitude'] for w in chunk) / len(chunk)
        avg_lon = sum(w['longitude'] for w in chunk) / len(chunk)
        # Distance from pickup point to job
        pickup_to_job = haversine_km(avg_lat, avg_lon, job_lat, job_lon)
        cost = int(round(pickup_to_job * RURAL_TRAVEL_COST_PER_KM * 2))  # round trip
        groups.append({
            'vehicle': vehicle_num,
            'workers': [w['worker_id'] for w in chunk],
            'pickup_point': {'lat': round(avg_lat, 6), 'lon': round(avg_lon, 6)},
            'distance_to_job_km': round(pickup_to_job, 2),
            'cost': cost,
        })
        vehicle_num += 1

    total_distance = sum(w['distance_to_job'] for w in enriched)
    avg_distance = total_distance / len(enriched)
    total_cost = sum(g['cost'] for g in groups)

    return {
        'total_distance_km': round(total_distance, 2),
        'avg_distance_km': round(avg_distance, 2),
        'total_cost': total_cost,
        'vehicles_needed': len(groups),
        'groups': groups,
    }


# ============================================================
# 3. GROUP MATCHING
# ============================================================

def match_group(available_workers: List[Dict], required_skill: str,
                num_workers_needed: int, budget: int,
                male_required: Optional[int] = None,
                female_required: Optional[int] = None,
                max_distance_km: float = 50.0,
                job_lat: float = 28.6139, job_lon: float = 77.2090) -> Dict:
    """
    Select the optimal group of workers respecting skill, gender, distance,
    and budget constraints.

    This is the multi-constraint optimizer:
        Minimize:  αW + βD + δM
        where W = wage, D = distance, M = mismatch penalty
    """
    # Filter by skill and distance
    candidates = []
    for w in available_workers:
        if w.get('skill') != required_skill:
            continue
        d = haversine_km(w['latitude'], w['longitude'], job_lat, job_lon)
        if d > max_distance_km:
            continue
        candidates.append({**w, 'distance_km': d})

    if not candidates:
        return {
            'selected': [],
            'total_wage': 0,
            'total_travel': 0,
            'satisfied': False,
            'reason': 'No workers matching skill within range',
        }

    # Split by gender
    males = [w for w in candidates if w.get('gender') == 'M']
    females = [w for w in candidates if w.get('gender') == 'F']
    others = [w for w in candidates if w.get('gender') not in ('M', 'F')]

    def pick(pool, n):
        """Pick n workers with lowest score = 0.5*wage + 0.3*distance + 0.2*(-rating)."""
        def score(w):
            return 0.5 * w.get('expected_wage', 500) + \
                   0.3 * w['distance_km'] * 100 + \
                   0.2 * (5 - w.get('rating', 4)) * 100
        return sorted(pool, key=score)[:n]

    selected = []
    if male_required is not None:
        selected += pick(males, male_required)
    if female_required is not None:
        selected += pick(females, female_required)

    # If no gender split specified, take the best from all candidates
    if not selected:
        selected = pick(candidates, num_workers_needed)
    else:
        # Fill remaining from all
        remaining = num_workers_needed - len(selected)
        if remaining > 0:
            already = {w['worker_id'] for w in selected}
            remaining_pool = [w for w in candidates if w['worker_id'] not in already]
            selected += pick(remaining_pool, remaining)

    # Check budget constraint
    total_wage = sum(w.get('expected_wage', 500) for w in selected)
    total_travel = sum(w['distance_km'] for w in selected)

    satisfied = (
        len(selected) >= num_workers_needed and
        total_wage <= budget and
        (male_required is None or len([w for w in selected if w.get('gender') == 'M']) >= male_required) and
        (female_required is None or len([w for w in selected if w.get('gender') == 'F']) >= female_required)
    )

    reason = None
    if len(selected) < num_workers_needed:
        reason = f"Only {len(selected)} workers available (needed {num_workers_needed})"
    elif total_wage > budget:
        reason = f"Total wage ₹{total_wage} exceeds budget ₹{budget}"

    return {
        'selected': [w['worker_id'] for w in selected],
        'selected_details': [
            {
                'worker_id': w['worker_id'],
                'gender': w.get('gender', 'U'),
                'expected_wage': w.get('expected_wage', 500),
                'distance_km': round(w['distance_km'], 2),
                'rating': w.get('rating', 4.0),
            }
            for w in selected
        ],
        'total_wage': total_wage,
        'total_travel': round(total_travel, 2),
        'satisfied': satisfied,
        'reason': reason,
    }


# ============================================================
# 4. BASELINES (for comparison)
# ============================================================

def nearest_worker_baseline(available_workers: List[Dict], required_skill: str,
                            num_workers_needed: int,
                            job_lat: float, job_lon: float) -> Dict:
    """Baseline 1: Pick the N nearest workers with the required skill."""
    candidates = []
    for w in available_workers:
        if w.get('skill') != required_skill:
            continue
        d = haversine_km(w['latitude'], w['longitude'], job_lat, job_lon)
        candidates.append({**w, 'distance_km': d})

    candidates.sort(key=lambda x: x['distance_km'])
    selected = candidates[:num_workers_needed]
    total_wage = sum(w.get('expected_wage', 500) for w in selected)
    total_distance = sum(w['distance_km'] for w in selected)

    return {
        'strategy': 'nearest_worker',
        'selected': [w['worker_id'] for w in selected],
        'total_wage': total_wage,
        'total_distance_km': round(total_distance, 2),
        'avg_distance_km': round(total_distance / max(1, len(selected)), 2),
    }


def skill_based_baseline(available_workers: List[Dict], required_skill: str,
                         num_workers_needed: int) -> Dict:
    """Baseline 2: Pick workers by skill + rating only."""
    candidates = [w for w in available_workers if w.get('skill') == required_skill]
    candidates.sort(key=lambda x: -x.get('rating', 4.0))
    selected = candidates[:num_workers_needed]

    total_wage = sum(w.get('expected_wage', 500) for w in selected)
    return {
        'strategy': 'skill_based',
        'selected': [w['worker_id'] for w in selected],
        'total_wage': total_wage,
        'avg_rating': round(
            sum(w.get('rating', 4.0) for w in selected) / max(1, len(selected)), 2
        ),
    }