import re
import urllib.parse
from datetime import datetime, timezone
from typing import List, Optional

class DataNormalizer:
    """
    Normalizes raw scraped fields (URLs, dates, text, skills, role types, locations).
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Produces a canonical URL by removing tracking query params (utm_*, ref, etc.) and fragment anchors.
        """
        if not url or not isinstance(url, str):
            return ""

        url = url.strip()
        try:
            parsed = urllib.parse.urlparse(url)
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            path = parsed.path or "/"

            # Filter query parameters
            query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
            filtered_params = []
            for k, v in query_params:
                k_lower = k.lower()
                if not (k_lower.startswith("utm_") or k_lower in {"ref", "fbclid", "gclid", "spm", "source"}):
                    filtered_params.append((k, v))

            query_str = urllib.parse.urlencode(filtered_params) if filtered_params else ""
            canonical = urllib.parse.urlunparse((scheme, netloc, path, "", query_str, ""))
            return canonical.rstrip("/") if path != "/" else canonical
        except Exception:
            return url

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return ""
        # Replace multiple spaces/newlines with a single clean space
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned

    @staticmethod
    def normalize_date(date_str: Optional[str]) -> str:
        """
        Converts various date formats (RFC 822, ISO 8601, YYYY-MM-DD) to ISO 8601 UTC timestamp.
        """
        if not date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

        date_str = date_str.strip()

        # Try standard ISO 8601 format
        for fmt in (
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%d %b %Y",
            "%b %d, %Y"
        ):
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
            except ValueError:
                continue

        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    @staticmethod
    def normalize_role_type(text: str) -> str:
        lower = text.lower()
        if any(term in lower for term in ["intern", "coop", "co-op", "trainee", "apprentice"]):
            return "internship"
        if any(term in lower for term in ["grad", "graduate", "fresher", "entry level", "entry-level"]):
            return "graduate"
        if any(term in lower for term in ["part time", "part-time"]):
            return "part_time"
        if any(term in lower for term in ["contract", "temporary", "freelance"]):
            return "contract"
        return "full_time"

    @staticmethod
    def normalize_work_arrangement(text: str) -> str:
        lower = text.lower()
        if "remote" in lower or "work from home" in lower or "wfh" in lower:
            return "remote"
        if "hybrid" in lower or "flexible" in lower:
            return "hybrid"
        return "onsite"

    @staticmethod
    def normalize_skills(skills_input: list) -> List[str]:
        if not skills_input:
            return []

        known_canonical = {
            "python": "Python", "java": "Java", "cpp": "C++", "c++": "C++",
            "c#": "C#", "csharp": "C#", "javascript": "JavaScript", "js": "JavaScript",
            "typescript": "TypeScript", "ts": "TypeScript", "sql": "SQL",
            "react": "React", "react.js": "React", "node": "Node.js", "node.js": "Node.js",
            "fastapi": "FastAPI", "django": "Django", "flask": "Flask",
            "aws": "AWS", "azure": "Azure", "gcp": "GCP", "docker": "Docker",
            "kubernetes": "Kubernetes", "k8s": "Kubernetes", "git": "Git",
            "dsa": "Data Structures & Algorithms", "algorithms": "Algorithms",
            "system design": "System Design", "dbms": "DBMS", "html": "HTML",
            "css": "CSS", "scikit-learn": "scikit-learn", "numpy": "NumPy",
            "pandas": "Pandas", "pytorch": "PyTorch", "tensorflow": "TensorFlow"
        }

        normalized_set = set()
        for item in skills_input:
            if not item:
                continue
            item_clean = str(item).strip().lower()
            if item_clean in known_canonical:
                normalized_set.add(known_canonical[item_clean])
            else:
                if len(item_clean) >= 2:
                    normalized_set.add(item_clean.capitalize())

        return sorted(list(normalized_set))
