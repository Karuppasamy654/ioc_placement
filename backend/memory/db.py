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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

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
