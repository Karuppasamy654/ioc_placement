import os
import sqlite3
import json
from typing import Dict, Any, List, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "placement_memory.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes SQLite tables for persistent student profiles, resume data, roadmaps, and quiz performance.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 0. User Accounts Table for Authentication
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        target_company TEXT,
        target_role TEXT,
        prep_days INTEGER DEFAULT 14,
        daily_hours REAL DEFAULT 4.0,
        current_skills TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 1. Student Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        target_company TEXT,
        target_role TEXT,
        prep_days INTEGER,
        daily_hours REAL,
        user_skills TEXT,
        strong_areas TEXT,
        weak_areas TEXT,
        resume_gaps TEXT,
        ats_score REAL DEFAULT 75.0,
        resume_score_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure migration for existing databases
    try:
        cursor.execute("ALTER TABLE student_profiles ADD COLUMN ats_score REAL DEFAULT 75.0;")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE student_profiles ADD COLUMN resume_score_json TEXT;")
    except sqlite3.OperationalError:
        pass  # Column already exists


    # 2. Resume Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        file_name TEXT,
        technical_skills TEXT,
        projects TEXT,
        education TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Roadmaps Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        student_name TEXT NOT NULL,
        total_days INTEGER,
        daily_hours REAL,
        overview TEXT,
        days_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Mock Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        total_questions INTEGER,
        answered_questions INTEGER,
        correct_count INTEGER,
        incorrect_count INTEGER,
        score_percentage REAL,
        topic_accuracy_json TEXT,
        difficulty_accuracy_json TEXT,
        strong_topics_json TEXT,
        weak_topics_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Adaptive Adjustments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adaptive_adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        weak_topics_addressed_json TEXT,
        concepts_to_revise_json TEXT,
        schedule_changes_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
