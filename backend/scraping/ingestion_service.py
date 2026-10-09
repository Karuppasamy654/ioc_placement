import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from backend.memory.db import get_db_connection
from backend.scraping.source_registry import SourceRegistry
from backend.scraping.robots_policy import RobotsPolicy, SSRFProtection
from backend.scraping.http_client import ResilientHTTPClient
from backend.scraping.normalizer import DataNormalizer
from backend.scraping.deduplicator import RecordDeduplicator
from backend.scraping.validators import RecordValidator
from backend.scraping.parsers import RSSParser, JSONAPIParser, HTMLScraperParser

from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

class IngestionService:
    """
    Coordinates fetching, parsing, normalizing, validating, deduplicating,
    and persisting records from configured public data sources.
    """

    @staticmethod
    def run_source_ingestion(source_id: int) -> Dict[str, Any]:
        source = SourceRegistry.get_source_by_id(source_id)
        if not source:
            raise ValueError(f"Source with ID {source_id} not found.")

        source_name = source["name"]
        base_url = source["base_url"]
        category = source["category"]
        source_type = source["source_type"]
        rate_limit = source.get("rate_limit_rps", 1.0)
        extraction_config = source.get("extraction_config", {})

        start_logging_time = log_tool_start("Scraping Engine", f"source='{source_name}', category='{category}', url='{base_url}'")

        # Create scrape run record in SQLite DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO scrape_runs (source_id, source_name, status, start_time)
        VALUES (?, ?, 'running', CURRENT_TIMESTAMP)
        """, (source_id, source_name))
        run_id = cursor.lastrowid
        conn.commit()
        conn.close()

        start_time_sec = time.time()
        discovered = 0
        inserted = 0
        updated = 0
        duplicates = 0
        failures = 0
        error_logs = []

        try:
            log_tool_process("Scraping Engine", f"Checking SSRF and robots.txt rules for {base_url}")
            # 1. SSRF & Robots Check
            is_safe, ssrf_msg = SSRFProtection.is_url_safe(base_url)
            if not is_safe:
                raise ValueError(f"SSRF Protection Error: {ssrf_msg}")

            if not RobotsPolicy.is_allowed(base_url):
                raise ValueError(f"Robots policy forbids fetching source URL: {base_url}")

            log_tool_process("Scraping Engine", f"Fetching payload from {base_url} via ResilientHTTPClient...")
            client = ResilientHTTPClient(timeout_seconds=15.0, max_retries=3)
            response = client.fetch(base_url, rate_limit_rps=rate_limit)

            if not response["success"]:
                raise ValueError(f"HTTP Fetch Failed (Status {response['status_code']}): {response['error']}")

            raw_content = response["content"]

            # 3. Parse Records based on source type & category
            parsed_records: List[Dict[str, Any]] = []

            if source_type == "rss":
                if category == "jobs":
                    parsed_records = RSSParser.parse_jobs_rss(raw_content, base_url, source_name)
                else:
                    parsed_records = RSSParser.parse_jobs_rss(raw_content, base_url, source_name)
            elif source_type == "api":
                if "remoteok" in base_url.lower():
                    parsed_records = JSONAPIParser.parse_remoteok_jobs(raw_content, source_name)
                else:
                    try:
                        data = json.loads(raw_content)
                        parsed_records = JSONAPIParser.parse_remoteok_jobs(data, source_name)
                    except Exception as e:
                        error_logs.append(f"JSON parsing error: {e}")
            elif source_type == "html":
                topic = extraction_config.get("topic", category)
                if category == "learning":
                    parsed_records = HTMLScraperParser.parse_learning_html(raw_content, base_url, source_name, topic=topic)
                else:
                    parsed_records = HTMLScraperParser.parse_learning_html(raw_content, base_url, source_name, topic=topic)

            discovered = len(parsed_records)

            # 4. Process Each Record (Normalize, Validate, Deduplicate, Persist)
            for record in parsed_records:
                try:
                    if category == "jobs":
                        ins, upd, dup, err = IngestionService._process_job_record(record, source_id, source_name)
                    else:
                        ins, upd, dup, err = IngestionService._process_learning_record(record, source_id, source_name)

                    inserted += ins
                    updated += upd
                    duplicates += dup
                    if err:
                        failures += 1
                        error_logs.append(err)
                except Exception as rec_err:
                    failures += 1
                    error_logs.append(f"Record processing error: {rec_err}")

            finish_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
            duration_sec = round(time.time() - start_time_sec, 2)
            status_str = "completed" if failures == 0 or inserted > 0 else "failed"

            metrics = {
                "duration_seconds": duration_sec,
                "discovered": discovered,
                "inserted": inserted,
                "updated": updated,
                "duplicates": duplicates,
                "failures": failures
            }

            # Update Scrape Run Record
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE scrape_runs SET
                finish_time = ?,
                status = ?,
                records_discovered = ?,
                records_inserted = ?,
                records_updated = ?,
                duplicates_count = ?,
                failures_count = ?,
                error_log = ?,
                metrics_json = ?
            WHERE id = ?
            """, (
                finish_time_str,
                status_str,
                discovered,
                inserted,
                updated,
                duplicates,
                failures,
                "\n".join(error_logs[:10]),
                json.dumps(metrics),
                run_id
            ))

            # Update Source Record Status
            cursor.execute("""
            UPDATE scraping_sources SET
                last_successful_run = ?,
                last_error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (finish_time_str, "\n".join(error_logs[:2]) if error_logs else "", source_id))

            conn.commit()
            conn.close()

            return {
                "run_id": run_id,
                "source_id": source_id,
                "source_name": source_name,
                "status": status_str,
                "discovered": discovered,
                "inserted": inserted,
                "updated": updated,
                "duplicates": duplicates,
                "failures": failures,
                "duration_seconds": duration_sec,
                "errors": error_logs
            }

        except Exception as run_err:
            finish_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
            err_msg = str(run_err)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE scrape_runs SET
                finish_time = ?,
                status = 'failed',
                failures_count = 1,
                error_log = ?
            WHERE id = ?
            """, (finish_time_str, err_msg, run_id))

            cursor.execute("""
            UPDATE scraping_sources SET
                last_error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (err_msg, source_id))

            conn.commit()
            conn.close()

            return {
                "run_id": run_id,
                "source_id": source_id,
                "source_name": source_name,
                "status": "failed",
                "discovered": 0,
                "inserted": 0,
                "updated": 0,
                "duplicates": 0,
                "failures": 1,
                "errors": [err_msg]
            }

    @staticmethod
    def _process_job_record(record: Dict[str, Any], source_id: int, source_name: str) -> Tuple[int, int, int, str]:
        # Normalize fields
        raw_url = record.get("original_url", "")
        canonical_url = DataNormalizer.normalize_url(raw_url)
        record["original_url"] = raw_url
        record["canonical_url"] = canonical_url

        record["title"] = DataNormalizer.normalize_text(record.get("title"))
        record["company"] = DataNormalizer.normalize_text(record.get("company"))
        record["description"] = DataNormalizer.normalize_text(record.get("description"))
        record["required_skills"] = DataNormalizer.normalize_skills(record.get("required_skills", []))

        # Validate
        is_valid, val_reason = RecordValidator.validate_job_posting(record)
        if not is_valid:
            return 0, 0, 0, f"Validation failed for '{record.get('title')}': {val_reason}"

        content_hash = RecordDeduplicator.compute_content_hash(record)
        is_dup, existing_id = RecordDeduplicator.is_job_duplicate(canonical_url, content_hash)

        conn = get_db_connection()
        cursor = conn.cursor()

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

        if is_dup and existing_id:
            cursor.execute("""
            UPDATE job_postings SET
                last_seen_at = ?,
                last_verified_at = ?,
                status = 'active'
            WHERE id = ?
            """, (now_str, now_str, existing_id))
            conn.commit()
            conn.close()
            return 0, 1, 1, ""

        cursor.execute("""
        INSERT INTO job_postings (
            source_id, source_name, canonical_url, external_id, title, company,
            role_type, description, required_skills_json, qualifications, location,
            work_arrangement, salary_or_stipend, application_deadline, original_url,
            publication_date, first_seen_at, last_seen_at, last_verified_at, content_hash,
            status, validation_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 'valid')
        """, (
            source_id,
            source_name,
            canonical_url,
            record.get("external_id", ""),
            record["title"],
            record["company"],
            record.get("role_type", "full_time"),
            record["description"],
            json.dumps(record["required_skills"]),
            record.get("qualifications", ""),
            record.get("location", "Remote"),
            record.get("work_arrangement", "onsite"),
            record.get("salary_or_stipend", ""),
            record.get("application_deadline", ""),
            raw_url,
            record.get("publication_date", now_str),
            now_str,
            now_str,
            now_str,
            content_hash
        ))
        conn.commit()
        conn.close()
        return 1, 0, 0, ""

    @staticmethod
    def _process_learning_record(record: Dict[str, Any], source_id: int, source_name: str) -> Tuple[int, int, int, str]:
        raw_url = record.get("original_url", "")
        canonical_url = DataNormalizer.normalize_url(raw_url)
        record["original_url"] = raw_url
        record["canonical_url"] = canonical_url

        record["title"] = DataNormalizer.normalize_text(record.get("title"))
        record["description"] = DataNormalizer.normalize_text(record.get("description"))
        record["topics"] = DataNormalizer.normalize_skills(record.get("topics", []))

        is_valid, val_reason = RecordValidator.validate_learning_resource(record)
        if not is_valid:
            return 0, 0, 0, f"Validation failed for resource '{record.get('title')}': {val_reason}"

        content_hash = RecordDeduplicator.compute_content_hash(record)
        is_dup, existing_id = RecordDeduplicator.is_resource_duplicate(canonical_url, content_hash)

        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

        if is_dup and existing_id:
            cursor.execute("""
            UPDATE learning_resources SET
                last_seen_at = ?,
                last_verified_at = ?,
                status = 'active'
            WHERE id = ?
            """, (now_str, now_str, existing_id))
            conn.commit()
            conn.close()
            return 0, 1, 1, ""

        cursor.execute("""
        INSERT INTO learning_resources (
            source_id, source_name, canonical_url, external_id, title, category,
            description, topics_json, difficulty_level, original_url, publication_date,
            first_seen_at, last_seen_at, last_verified_at, content_hash, status, validation_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 'valid')
        """, (
            source_id,
            source_name,
            canonical_url,
            record.get("external_id", ""),
            record["title"],
            record.get("category", "general"),
            record["description"],
            json.dumps(record["topics"]),
            record.get("difficulty_level", "intermediate"),
            raw_url,
            record.get("publication_date", now_str),
            now_str,
            now_str,
            now_str,
            content_hash
        ))
        conn.commit()
        conn.close()
        return 1, 0, 0, ""

    @staticmethod
    def get_run_history(limit: int = 50, source_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM scrape_runs WHERE 1=1"
        params = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        runs = []
        for r in rows:
            d = dict(r)
            try:
                d["metrics"] = json.loads(d.get("metrics_json") or '{}')
            except Exception:
                d["metrics"] = {}
            runs.append(d)
        return runs

    @staticmethod
    def get_run_by_id(run_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scrape_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        try:
            d["metrics"] = json.loads(d.get("metrics_json") or '{}')
        except Exception:
            d["metrics"] = {}
        return d
