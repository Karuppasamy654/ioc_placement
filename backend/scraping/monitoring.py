from typing import Dict, Any, Optional
from backend.memory.db import get_db_connection
from backend.scraping.source_registry import SourceRegistry

class MonitoringService:
    """
    Monitors ingestion metrics, source health statistics, and system freshness.
    """

    @staticmethod
    def get_health_metrics() -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Active vs Disabled Sources
        cursor.execute("SELECT COUNT(*) FROM scraping_sources WHERE enabled = 1")
        active_sources_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scraping_sources WHERE enabled = 0")
        disabled_sources_count = cursor.fetchone()[0]

        # Total Scrape Runs
        cursor.execute("SELECT COUNT(*) FROM scrape_runs")
        total_scrape_runs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scrape_runs WHERE status = 'completed'")
        successful_runs_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scrape_runs WHERE status = 'failed'")
        failed_runs_count = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(finish_time) FROM scrape_runs")
        last_run_timestamp = cursor.fetchone()[0]

        # Ingested Records
        cursor.execute("SELECT COUNT(*) FROM job_postings")
        total_jobs_ingested = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM job_postings WHERE status = 'active'")
        active_jobs_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM learning_resources")
        total_learning_resources = cursor.fetchone()[0]

        conn.close()

        status_str = "healthy"
        if failed_runs_count > 0 and (failed_runs_count >= (total_scrape_runs or 1) * 0.5):
            status_str = "degraded"

        return {
            "status": status_str,
            "active_sources_count": active_sources_count,
            "disabled_sources_count": disabled_sources_count,
            "total_scrape_runs": total_scrape_runs,
            "successful_runs_count": successful_runs_count,
            "failed_runs_count": failed_runs_count,
            "total_jobs_ingested": total_jobs_ingested,
            "active_jobs_count": active_jobs_count,
            "total_learning_resources": total_learning_resources,
            "last_run_timestamp": last_run_timestamp,
            "system_uptime_status": "operational"
        }
