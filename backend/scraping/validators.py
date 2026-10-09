import urllib.parse
from typing import Dict, Any, Tuple

class RecordValidator:
    """
    Validation engine that enforces data completeness, valid URLs,
    non-empty titles, and rejects malformed or dummy records.
    """

    FORBIDDEN_DUMMY_TEXTS = {
        "lorem ipsum", "test title", "dummy job", "undefined",
        "null", "sample description", "fake posting", "test company"
    }

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def validate_job_posting(record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates job posting fields. Returns (is_valid, reason).
        """
        title = str(record.get("title", "")).strip()
        company = str(record.get("company", "")).strip()
        url = str(record.get("original_url", "")).strip()
        description = str(record.get("description", "")).strip()

        if not title or len(title) < 3:
            return False, "Job title is empty or too short (minimum 3 characters)"

        if not company or len(company) < 2:
            return False, "Company name is empty or too short (minimum 2 characters)"

        if not RecordValidator._is_valid_url(url):
            return False, f"Invalid or missing original_url: '{url}'"

        if not description or len(description) < 20:
            return False, "Job description is missing or too short (minimum 20 characters)"

        title_lower = title.lower()
        if any(dummy in title_lower for dummy in RecordValidator.FORBIDDEN_DUMMY_TEXTS):
            return False, f"Job title '{title}' contains dummy/placeholder text."

        return True, "Valid"

    @staticmethod
    def validate_learning_resource(record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates learning resource fields. Returns (is_valid, reason).
        """
        title = str(record.get("title", "")).strip()
        url = str(record.get("original_url", "")).strip()
        description = str(record.get("description", "")).strip()

        if not title or len(title) < 3:
            return False, "Resource title is empty or too short (minimum 3 characters)"

        if not RecordValidator._is_valid_url(url):
            return False, f"Invalid or missing original_url: '{url}'"

        if not description or len(description) < 15:
            return False, "Resource description is missing or too short (minimum 15 characters)"

        title_lower = title.lower()
        if any(dummy in title_lower for dummy in RecordValidator.FORBIDDEN_DUMMY_TEXTS):
            return False, f"Resource title '{title}' contains dummy/placeholder text."

        return True, "Valid"
