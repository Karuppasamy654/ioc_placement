import json
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional, Dict, Any

from backend.models.schemas import (
    ScrapingSourceCreate, ScrapingSourceUpdate, ScrapingSourceOut,
    ScrapeRunOut, JobPostingOut, LearningResourceOut, ScrapingHealthMetrics
)
from backend.scraping.source_registry import SourceRegistry
from backend.scraping.ingestion_service import IngestionService
from backend.scraping.monitoring import MonitoringService
from backend.memory.db import get_db_connection

router = APIRouter(prefix="/api", tags=["scraping"])


# ---------------------------------------------------------------------
# SOURCE REGISTRATION & MANAGEMENT ENDPOINTS
# ---------------------------------------------------------------------

@router.get("/scraping/sources", response_model=List[ScrapingSourceOut])
def list_scraping_sources(
    category: Optional[str] = Query(None, description="Filter by category: 'jobs' or 'learning'"),
    enabled_only: bool = Query(False, description="Filter enabled sources only")
):
    """
    List all configured data sources in the source registry.
    """
    return SourceRegistry.list_sources(category=category, enabled_only=enabled_only)


@router.post("/scraping/sources", response_model=ScrapingSourceOut, status_code=201)
def register_scraping_source(source_input: ScrapingSourceCreate):
    """
    Register a new data source with SSRF verification and access checks.
    """
    try:
        source_dict = source_input.model_dump()
        new_source = SourceRegistry.register_source(source_dict)
        return new_source
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source registration failed: {e}")


@router.patch("/scraping/sources/{source_id}", response_model=ScrapingSourceOut)
def update_scraping_source(
    source_id: int = Path(..., ge=1),
    updates: ScrapingSourceUpdate = ...
):
    """
    Update configuration of a source (enable/disable, crawl interval, rate limit).
    """
    try:
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        updated = SourceRegistry.update_source(source_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Source ID {source_id} not found.")
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/scraping/sources/{source_id}/run", response_model=Dict[str, Any])
def trigger_manual_ingestion_run(source_id: int = Path(..., ge=1)):
    """
    Manually trigger an immediate permitted ingestion run for a source.
    """
    source = SourceRegistry.get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source ID {source_id} not found.")

    try:
        result = IngestionService.run_source_ingestion(source_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion run failed: {e}")


# ---------------------------------------------------------------------
# RUN HISTORY & MONITORING ENDPOINTS
# ---------------------------------------------------------------------

@router.get("/scraping/runs", response_model=List[ScrapeRunOut])
def get_scrape_run_history(
    limit: int = Query(50, ge=1, le=200),
    source_id: Optional[int] = Query(None)
):
    """
    View execution history of scraping runs.
    """
    return IngestionService.get_run_history(limit=limit, source_id=source_id)


@router.get("/scraping/runs/{run_id}", response_model=ScrapeRunOut)
def inspect_scrape_run(run_id: int = Path(..., ge=1)):
    """
    Inspect details and metrics of a specific scrape run.
    """
    run = IngestionService.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run ID {run_id} not found.")
    return run


@router.get("/scraping/health", response_model=ScrapingHealthMetrics)
def get_scraping_system_health():
    """
    Subsystem health and freshness metrics.
    """
    return MonitoringService.get_health_metrics()


# ---------------------------------------------------------------------
# INGESTED JOBS & LEARNING RESOURCES QUERY ENDPOINTS
# ---------------------------------------------------------------------

@router.get("/jobs", response_model=List[JobPostingOut])
def search_stored_jobs(
    company: Optional[str] = Query(None, description="Filter by company name"),
    role_type: Optional[str] = Query(None, description="Filter by role type: 'internship', 'full_time', 'graduate'"),
    location: Optional[str] = Query(None, description="Filter by location or work arrangement"),
    skill: Optional[str] = Query(None, description="Filter by required skill"),
    q: Optional[str] = Query(None, description="General search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search and filter ingested real job postings.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM job_postings WHERE status = 'active'"
    params = []

    if company:
        query += " AND LOWER(company) LIKE ?"
        params.append(f"%{company.lower()}%")

    if role_type:
        query += " AND role_type = ?"
        params.append(role_type.lower())

    if location:
        query += " AND (LOWER(location) LIKE ? OR LOWER(work_arrangement) LIKE ?)"
        params.extend([f"%{location.lower()}%", f"%{location.lower()}%"])

    if skill:
        query += " AND LOWER(required_skills_json) LIKE ?"
        params.append(f"%{skill.lower()}%")

    if q:
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(company) LIKE ?)"
        params.extend([f"%{q.lower()}%", f"%{q.lower()}%", f"%{q.lower()}%"])

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["required_skills"] = json.loads(d.get("required_skills_json") or '[]')
        except Exception:
            d["required_skills"] = []
        results.append(d)

    return results


@router.get("/jobs/{job_id}", response_model=JobPostingOut)
def get_job_by_id(job_id: int = Path(..., ge=1)):
    """
    Retrieve a single ingested job posting by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Job posting ID {job_id} not found.")

    d = dict(row)
    try:
        d["required_skills"] = json.loads(d.get("required_skills_json") or '[]')
    except Exception:
        d["required_skills"] = []
    return d


@router.get("/resources", response_model=List[LearningResourceOut])
def search_stored_resources(
    category: Optional[str] = Query(None, description="Filter by topic category: 'python', 'react', 'fastapi', etc."),
    topic: Optional[str] = Query(None, description="Filter by specific topic"),
    q: Optional[str] = Query(None, description="General search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search stored technical learning resources.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM learning_resources WHERE status = 'active'"
    params = []

    if category:
        query += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.lower()}%")

    if topic:
        query += " AND LOWER(topics_json) LIKE ?"
        params.append(f"%{topic.lower()}%")

    if q:
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([f"%{q.lower()}%", f"%{q.lower()}%"])

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["topics"] = json.loads(d.get("topics_json") or '[]')
        except Exception:
            d["topics"] = []
        results.append(d)

    return results
