"""
KaamSetu AI — Authentication Module
JWT-based auth with three roles: employer, worker, admin.
Users stored in SQLite for zero-config deployment.
"""
import os
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
    """Create users table if it doesn't exist."""
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
# Init on import
# ============================================================
init_db()
seed_demo_users()