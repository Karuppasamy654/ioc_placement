import re
import json
from typing import List, Dict, Any, Optional
from backend.memory.db import get_db_connection

from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

def defend_against_prompt_injection(text: str) -> str:
    """
    Sanitizes arbitrary scraped webpage text before supplying it to AI LLM prompts.
    Strips prompt override directives, system prompt leak attempts, and executable script markers.
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove attempts to override agent instructions
    forbidden_patterns = [
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"disregard\s+(all\s+)?(previous\s+)?instructions",
        r"system prompt:",
        r"new instruction:",
        r"you are now a",
        r"do not follow the previous rules"
    ]

    sanitized = text
    for pat in forbidden_patterns:
        sanitized = re.sub(pat, "[FILTERED PROMPT INJECTION ATTEMPT]", sanitized, flags=re.IGNORECASE)

    # Neutralize HTML tags or markdown executable blocks
    sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    return sanitized.strip()


class JobDiscoveryTool:
    """
    Tool used by Placement Agents (Job Discovery Agent, Skill Analysis Agent)
    to query real ingested job postings and internships from SQLite DB.
    """

    @staticmethod
    def search_jobs(
        company: Optional[str] = None,
        role_type: Optional[str] = None,
        skill: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 10,
        state=None
    ) -> List[Dict[str, Any]]:
        start_time = log_tool_start("Job Discovery Tool", f"company='{company}', role='{role_type}', skill='{skill}', query='{query}'", state=state)
        
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM job_postings WHERE status = 'active'"
        params = []

        if company:
            sql += " AND LOWER(company) LIKE ?"
            params.append(f"%{company.lower()}%")

        if role_type:
            sql += " AND role_type = ?"
            params.append(role_type.lower())

        if skill:
            sql += " AND LOWER(required_skills_json) LIKE ?"
            params.append(f"%{skill.lower()}%")

        if query:
            sql += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(company) LIKE ?)"
            params.extend([f"%{query.lower()}%", f"%{query.lower()}%", f"%{query.lower()}%"])

        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        log_tool_process("Job Discovery Tool", f"Executing database query: '{sql}' with parameters {params}", state=state)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        jobs = []
        for r in rows:
            d = dict(r)
            try:
                d["required_skills"] = json.loads(d.get("required_skills_json") or '[]')
            except Exception:
                d["required_skills"] = []
            d["description"] = defend_against_prompt_injection(d.get("description", ""))
            jobs.append(d)
        
        summary = f"Retrieved {len(jobs)} active job postings from memory database."
        log_tool_result("Job Discovery Tool", summary, start_time, state=state)
        return jobs


class LearningResourceTool:
    """
    Tool used by Roadmap & Learning Agents to query approved learning resources
    from official documentation and ingested courses.
    """

    @staticmethod
    def search_resources(
        topic: Optional[str] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 10,
        state=None
    ) -> List[Dict[str, Any]]:
        start_time = log_tool_start("Learning Resource Tool", f"topic='{topic}', category='{category}', query='{query}'", state=state)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM learning_resources WHERE status = 'active'"
        params = []

        if category:
            sql += " AND LOWER(category) LIKE ?"
            params.append(f"%{category.lower()}%")

        if topic:
            sql += " AND LOWER(topics_json) LIKE ?"
            params.append(f"%{topic.lower()}%")

        if query:
            sql += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
            params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])

        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        log_tool_process("Learning Resource Tool", f"Querying verified learning documentation DB: {topic or category or query or 'all'}", state=state)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        resources = []
        for r in rows:
            d = dict(r)
            try:
                d["topics"] = json.loads(d.get("topics_json") or '[]')
            except Exception:
                d["topics"] = []
            d["description"] = defend_against_prompt_injection(d.get("description", ""))
            resources.append(d)

        summary = f"Retrieved {len(resources)} verified technical documentation items."
        log_tool_result("Learning Resource Tool", summary, start_time, state=state)
        return resources

