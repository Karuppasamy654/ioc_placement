import os
import sqlite3
import json
from typing import Dict, Any, List, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "placement_memory.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes SQLite tables for persistent student profiles, resume data, roadmaps, and quiz performance.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=60000;")

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

    # 6. Scraping Sources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraping_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        base_url TEXT NOT NULL,
        category TEXT DEFAULT 'jobs',
        source_type TEXT DEFAULT 'html',
        enabled INTEGER DEFAULT 1,
        permitted_paths_json TEXT DEFAULT '["/"]',
        crawl_interval_minutes INTEGER DEFAULT 60,
        rate_limit_rps REAL DEFAULT 1.0,
        extraction_config_json TEXT DEFAULT '{}',
        last_successful_run TIMESTAMP,
        last_error TEXT,
        robots_verified INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Scrape Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scrape_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finish_time TIMESTAMP,
        status TEXT DEFAULT 'running',
        records_discovered INTEGER DEFAULT 0,
        records_inserted INTEGER DEFAULT 0,
        records_updated INTEGER DEFAULT 0,
        duplicates_count INTEGER DEFAULT 0,
        failures_count INTEGER DEFAULT 0,
        error_log TEXT DEFAULT '',
        metrics_json TEXT DEFAULT '{}',
        FOREIGN KEY(source_id) REFERENCES scraping_sources(id)
    );
    """)

    # 8. Job Postings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        canonical_url TEXT UNIQUE NOT NULL,
        external_id TEXT DEFAULT '',
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        role_type TEXT DEFAULT 'full_time',
        description TEXT NOT NULL,
        required_skills_json TEXT DEFAULT '[]',
        qualifications TEXT DEFAULT '',
        location TEXT DEFAULT '',
        work_arrangement TEXT DEFAULT 'onsite',
        salary_or_stipend TEXT DEFAULT '',
        application_deadline TEXT DEFAULT '',
        original_url TEXT NOT NULL,
        publication_date TIMESTAMP,
        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content_hash TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        validation_status TEXT DEFAULT 'valid',
        FOREIGN KEY(source_id) REFERENCES scraping_sources(id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON job_postings(company);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_role_type ON job_postings(role_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_canonical ON job_postings(canonical_url);")

    # 9. Learning Resources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        canonical_url TEXT UNIQUE NOT NULL,
        external_id TEXT DEFAULT '',
        title TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        description TEXT NOT NULL,
        topics_json TEXT DEFAULT '[]',
        difficulty_level TEXT DEFAULT 'intermediate',
        original_url TEXT NOT NULL,
        publication_date TIMESTAMP,
        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content_hash TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        validation_status TEXT DEFAULT 'valid',
        FOREIGN KEY(source_id) REFERENCES scraping_sources(id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_category ON learning_resources(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_canonical ON learning_resources(canonical_url);")

    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
