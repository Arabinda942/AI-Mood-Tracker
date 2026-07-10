"""
Auro — Mental Health Mood Tracker
SQLite database layer.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "auro.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            age INTEGER,
            sex TEXT,
            email TEXT,
            location TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,     -- 1 (very low) to 10 (excellent)
            anxiety_score INTEGER,           -- 1 to 10
            sleep_hours REAL,
            exercise_minutes INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, log_date),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cbt_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            exercise_type TEXT NOT NULL,     -- e.g. 'thought_record', 'gratitude', 'reframe'
            situation TEXT,
            automatic_thought TEXT,
            evidence_for TEXT,
            evidence_against TEXT,
            balanced_thought TEXT,
            mood_before INTEGER,
            mood_after INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(name, phone, age, sex, email, location, password_hash):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (name, phone, age, sex, email, location, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, age, sex, email, location, password_hash, datetime.utcnow().isoformat()))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id


def get_user_by_phone(phone):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def upsert_mood_log(user_id, log_date, mood_score, anxiety_score, sleep_hours, exercise_minutes, notes):
    conn = get_db()
    conn.execute("""
        INSERT INTO mood_logs (user_id, log_date, mood_score, anxiety_score, sleep_hours, exercise_minutes, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, log_date) DO UPDATE SET
            mood_score=excluded.mood_score,
            anxiety_score=excluded.anxiety_score,
            sleep_hours=excluded.sleep_hours,
            exercise_minutes=excluded.exercise_minutes,
            notes=excluded.notes
    """, (user_id, log_date, mood_score, anxiety_score, sleep_hours, exercise_minutes, notes, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_mood_logs(user_id, limit=90):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM mood_logs WHERE user_id = ?
        ORDER BY log_date ASC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return rows


def add_cbt_entry(user_id, entry_date, exercise_type, situation, automatic_thought,
                   evidence_for, evidence_against, balanced_thought, mood_before, mood_after):
    conn = get_db()
    conn.execute("""
        INSERT INTO cbt_entries (user_id, entry_date, exercise_type, situation, automatic_thought,
            evidence_for, evidence_against, balanced_thought, mood_before, mood_after, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, entry_date, exercise_type, situation, automatic_thought,
          evidence_for, evidence_against, balanced_thought, mood_before, mood_after,
          datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_cbt_entries(user_id, limit=50):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM cbt_entries WHERE user_id = ?
        ORDER BY entry_date DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return rows
