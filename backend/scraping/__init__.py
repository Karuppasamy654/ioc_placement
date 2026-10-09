"""
Web Scraping and Data Ingestion Subsystem for IOC Placement Agent.
"""

from backend.scraping.ingestion_service import IngestionService
from backend.scraping.source_registry import SourceRegistry
from backend.scraping.scheduler import ScrapingScheduler
from backend.scraping.monitoring import MonitoringService

__all__ = [
    "IngestionService",
    "SourceRegistry",
    "ScrapingScheduler",
    "MonitoringService"
]
