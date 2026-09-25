"""
KaamSetu AI — Authentication & Jobs Module
JWT-based auth with three roles: employer, worker, admin.
Users and jobs stored in SQLite for zero-config deployment.
"""
import os
import json
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ============================================================
# Config
# ============================================================
DB_PATH = Path(__file__).parent.parent / 'data' / 'users.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv('JWT_SECRET', 'kaamsetu-dev-secret-change-in-prod-2026')
ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 days


# ============================================================
# Database setup
# ============================================================
def init_db():
    """Create users, jobs, and worker_availability tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('employer', 'worker', 'admin')),
            phone TEXT,
            location TEXT,
            skill TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER NOT NULL,
            employer_name TEXT NOT NULL,
            required_skill TEXT NOT NULL,
            num_workers_needed INTEGER NOT NULL,
            budget INTEGER NOT NULL,
            duration_hours INTEGER NOT NULL,
            latitude REAL DEFAULT 28.6139,
            longitude REAL DEFAULT 77.2090,
            status TEXT DEFAULT 'open',
            accepted_by TEXT DEFAULT '[]',
            matched_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS worker_availability (
            user_id INTEGER PRIMARY KEY,
            days TEXT DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


def seed_demo_users():
    """Create demo accounts if they don't exist."""
    demo_users = [
        {
            'email': 'employer@demo.com',
            'password': 'demo123',
            'full_name': 'Demo Employer',
            'role': 'employer',
            'phone': '9876543210',
            'location': 'Pune, Maharashtra',
            'skill': None,
        },
        {
            'email': 'worker@demo.com',
            'password': 'demo123',
            'full_name': 'Demo Worker',
            'role': 'worker',
            'phone': '9876543211',
            'location': 'Pune, Maharashtra',
            'skill': 'farming_seeds',
        },
        {
            'email': 'admin@demo.com',
            'password': 'demo123',
            'full_name': 'Demo Admin',
            'role': 'admin',
            'phone': '9876543212',
            'location': 'Pune, Maharashtra',
            'skill': None,
        },
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for u in demo_users:
        cur.execute('SELECT id FROM users WHERE email = ?', (u['email'],))
        if cur.fetchone() is None:
            pw_hash = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute('''
                INSERT INTO users (email, password_hash, full_name, role, phone, location, skill)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (u['email'], pw_hash, u['full_name'], u['role'], u['phone'], u['location'], u['skill']))

    conn.commit()
    conn.close()


# ============================================================
# Password hashing
# ============================================================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# ============================================================
# JWT tokens
# ============================================================
def create_token(user_id: int, email: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ============================================================
# User CRUD
# ============================================================
def create_user(email: str, password: str, full_name: str, role: str,
                phone: str = None, location: str = None, skill: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        pw_hash = hash_password(password)
        cur.execute('''
            INSERT INTO users (email, password_hash, full_name, role, phone, location, skill)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, pw_hash, full_name, role, phone, location, skill))
        conn.commit()
        user_id = cur.lastrowid
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_all_users(role_filter: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if role_filter:
        cur.execute('SELECT id, email, full_name, role, phone, location, skill, created_at FROM users WHERE role = ?', (role_filter,))
    else:
        cur.execute('SELECT id, email, full_name, role, phone, location, skill, created_at FROM users')
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def user_to_public(user: dict) -> dict:
    """Strip password hash before returning to client."""
    if not user:
        return None
    return {
        'id': user['id'],
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user['role'],
        'phone': user.get('phone'),
        'location': user.get('location'),
        'skill': user.get('skill'),
        'created_at': str(user.get('created_at', '')),
    }


# ============================================================
# Job CRUD
# ============================================================
def create_job(employer_id: int, employer_name: str, required_skill: str,
               num_workers_needed: int, budget: int, duration_hours: int,
               latitude: float = 28.6139, longitude: float = 77.2090,
               matched_count: int = 0):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO jobs (employer_id, employer_name, required_skill, num_workers_needed,
                          budget, duration_hours, latitude, longitude, matched_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (employer_id, employer_name, required_skill, num_workers_needed,
          budget, duration_hours, latitude, longitude, matched_count))
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return get_job_by_id(job_id)


def get_job_by_id(job_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_jobs(status: str = None, skill: str = None, employer_id: int = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = 'SELECT * FROM jobs WHERE 1=1'
    params = []
    if status:
        query += ' AND status = ?'
        params.append(status)
    if skill:
        query += ' AND required_skill = ?'
        params.append(skill)
    if employer_id:
        query += ' AND employer_id = ?'
        params.append(employer_id)
    query += ' ORDER BY created_at DESC'
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def accept_job(job_id: int, worker_name: str):
    """Add worker to job's accepted list."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    accepted = json.loads(row['accepted_by'] or '[]')
    if worker_name in accepted:
        conn.close()
        return dict(row)
    accepted.append(worker_name)
    new_status = 'filled' if len(accepted) >= row['num_workers_needed'] else 'open'
    cur.execute(
        'UPDATE jobs SET accepted_by = ?, status = ? WHERE id = ?',
        (json.dumps(accepted), new_status, job_id)
    )
    conn.commit()
    cur.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    updated = cur.fetchone()
    conn.close()
    return dict(updated)


# ============================================================
# Worker Availability CRUD
# ============================================================
def get_worker_availability(user_id: int):
    """Get saved availability days for a worker."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT days FROM worker_availability WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return []
    return json.loads(row[0] or '[]')


def set_worker_availability(user_id: int, days: list):
    """Upsert worker's availability."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO worker_availability (user_id, days, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            days = excluded.days,
            updated_at = CURRENT_TIMESTAMP
    ''', (user_id, json.dumps(days)))
    conn.commit()
    conn.close()
    return days


# ============================================================
# Init on import
# ============================================================
init_db()
seed_demo_users()