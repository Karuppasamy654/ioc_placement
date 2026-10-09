import json
import sqlite3
from typing import List, Dict, Any, Optional
from backend.memory.db import get_db_connection
from backend.scraping.robots_policy import SSRFProtection

DEFAULT_SEED_SOURCES = [
    # JOBS / INTERNSHIPS SOURCES
    {
        "name": "RemoteOK Tech Jobs Feed",
        "base_url": "https://remoteok.com/api",
        "category": "jobs",
        "source_type": "api",
        "enabled": True,
        "permitted_paths_json": '["/api"]',
        "crawl_interval_minutes": 60,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"format": "json"}'
    },
    {
        "name": "WeWorkRemotely Programming Jobs",
        "base_url": "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
        "category": "jobs",
        "source_type": "rss",
        "enabled": True,
        "permitted_paths_json": '["/categories"]',
        "crawl_interval_minutes": 60,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"format": "rss"}'
    },
    {
        "name": "Microsoft Careers Portal",
        "base_url": "https://careers.microsoft.com",
        "category": "jobs",
        "source_type": "html",
        "enabled": False, # Requires admin verification for HTML scraping
        "permitted_paths_json": '["/"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 0.5,
        "extraction_config_json": '{"format": "html", "selectors": {"title": "h1", "company": "Microsoft"}}'
    },
    {
        "name": "Google Careers Portal",
        "base_url": "https://www.google.com/about/careers/applications/",
        "category": "jobs",
        "source_type": "html",
        "enabled": False, # Requires admin verification
        "permitted_paths_json": '["/about/careers"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 0.5,
        "extraction_config_json": '{"format": "html"}'
    },
    {
        "name": "Amazon Jobs Portal",
        "base_url": "https://www.amazon.jobs",
        "category": "jobs",
        "source_type": "html",
        "enabled": False,
        "permitted_paths_json": '["/"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 0.5,
        "extraction_config_json": '{"format": "html"}'
    },

    # TECHNICAL LEARNING & PREPARATION SOURCES
    {
        "name": "Python Official Documentation & News",
        "base_url": "https://docs.python.org/3/",
        "category": "learning",
        "source_type": "html",
        "enabled": True,
        "permitted_paths_json": '["/3/"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"topic": "python"}'
    },
    {
        "name": "React Documentation Learn",
        "base_url": "https://react.dev/learn",
        "category": "learning",
        "source_type": "html",
        "enabled": True,
        "permitted_paths_json": '["/learn"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"topic": "react"}'
    },
    {
        "name": "FastAPI Documentation",
        "base_url": "https://fastapi.tiangolo.com/",
        "category": "learning",
        "source_type": "html",
        "enabled": True,
        "permitted_paths_json": '["/"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"topic": "fastapi"}'
    },
    {
        "name": "Git Documentation",
        "base_url": "https://git-scm.com/doc",
        "category": "learning",
        "source_type": "html",
        "enabled": True,
        "permitted_paths_json": '["/doc"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"topic": "git"}'
    },
    {
        "name": "scikit-learn Documentation",
        "base_url": "https://scikit-learn.org/stable/",
        "category": "learning",
        "source_type": "html",
        "enabled": True,
        "permitted_paths_json": '["/stable/"]',
        "crawl_interval_minutes": 120,
        "rate_limit_rps": 1.0,
        "extraction_config_json": '{"topic": "scikit-learn"}'
    }
]

class SourceRegistry:
    """
    Manages configured scraping sources and pre-seeds default official sources.
    """

    @staticmethod
    def seed_default_sources():
        """
        Inserts default seed sources if they do not exist.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        for source in DEFAULT_SEED_SOURCES:
            cursor.execute("""
            INSERT INTO scraping_sources (
                name, base_url, category, source_type, enabled,
                permitted_paths_json, crawl_interval_minutes, rate_limit_rps, extraction_config_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                base_url=excluded.base_url,
                category=excluded.category,
                source_type=excluded.source_type;
            """, (
                source["name"],
                source["base_url"],
                source["category"],
                source["source_type"],
                1 if source["enabled"] else 0,
                source["permitted_paths_json"],
                source["crawl_interval_minutes"],
                source["rate_limit_rps"],
                source["extraction_config_json"]
            ))

        conn.commit()
        conn.close()

    @staticmethod
    def list_sources(category: Optional[str] = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM scraping_sources WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if enabled_only:
            query += " AND enabled = 1"

        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        sources = []
        for row in rows:
            d = dict(row)
            d["enabled"] = bool(d["enabled"])
            d["robots_verified"] = bool(d["robots_verified"])
            try:
                d["permitted_paths"] = json.loads(d.get("permitted_paths_json") or '["/"]')
            except Exception:
                d["permitted_paths"] = ["/"]
            try:
                d["extraction_config"] = json.loads(d.get("extraction_config_json") or '{}')
            except Exception:
                d["extraction_config"] = {}
            sources.append(d)

        return sources

    @staticmethod
    def get_source_by_id(source_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scraping_sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        d = dict(row)
        d["enabled"] = bool(d["enabled"])
        d["robots_verified"] = bool(d["robots_verified"])
        try:
            d["permitted_paths"] = json.loads(d.get("permitted_paths_json") or '["/"]')
        except Exception:
            d["permitted_paths"] = ["/"]
        try:
            d["extraction_config"] = json.loads(d.get("extraction_config_json") or '{}')
        except Exception:
            d["extraction_config"] = {}
        return d

    @staticmethod
    def register_source(source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers a new scraping source with SSRF verification.
        """
        base_url = source_data.get("base_url", "").strip()
        is_safe, error_msg = SSRFProtection.is_url_safe(base_url)
        if not is_safe:
            raise ValueError(f"SSRF Protection Rejected Base URL: {error_msg}")

        name = source_data.get("name", "").strip()
        category = source_data.get("category", "jobs").strip()
        source_type = source_data.get("source_type", "html").strip()
        enabled = 1 if source_data.get("enabled", True) else 0
        permitted_paths = source_data.get("permitted_paths", ["/"])
        crawl_interval = source_data.get("crawl_interval_minutes", 60)
        rate_limit = source_data.get("rate_limit_rps", 1.0)
        extraction_config = source_data.get("extraction_config", {})

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO scraping_sources (
                name, base_url, category, source_type, enabled,
                permitted_paths_json, crawl_interval_minutes, rate_limit_rps, extraction_config_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                base_url,
                category,
                source_type,
                enabled,
                json.dumps(permitted_paths),
                crawl_interval,
                rate_limit,
                json.dumps(extraction_config)
            ))
            new_id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Scraping source with name '{name}' already exists.")

        conn.close()
        return SourceRegistry.get_source_by_id(new_id)

    @staticmethod
    def update_source(source_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = SourceRegistry.get_source_by_id(source_id)
        if not existing:
            return None

        if "base_url" in updates and updates["base_url"]:
            is_safe, error_msg = SSRFProtection.is_url_safe(updates["base_url"])
            if not is_safe:
                raise ValueError(f"SSRF Protection Rejected Base URL: {error_msg}")

        conn = get_db_connection()
        cursor = conn.cursor()

        field_map = {
            "name": updates.get("name"),
            "base_url": updates.get("base_url"),
            "category": updates.get("category"),
            "source_type": updates.get("source_type"),
            "enabled": (1 if updates["enabled"] else 0) if "enabled" in updates and updates["enabled"] is not None else None,
            "permitted_paths_json": json.dumps(updates["permitted_paths"]) if "permitted_paths" in updates and updates["permitted_paths"] is not None else None,
            "crawl_interval_minutes": updates.get("crawl_interval_minutes"),
            "rate_limit_rps": updates.get("rate_limit_rps"),
            "extraction_config_json": json.dumps(updates["extraction_config"]) if "extraction_config" in updates and updates["extraction_config"] is not None else None,
        }

        set_clause = []
        params = []
        for col, val in field_map.items():
            if val is not None:
                set_clause.append(f"{col} = ?")
                params.append(val)

        if not set_clause:
            conn.close()
            return existing

        set_clause.append("updated_at = CURRENT_TIMESTAMP")
        params.append(source_id)

        query = f"UPDATE scraping_sources SET {', '.join(set_clause)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return SourceRegistry.get_source_by_id(source_id)


# Pre-seed default sources on module import
SourceRegistry.seed_default_sources()
