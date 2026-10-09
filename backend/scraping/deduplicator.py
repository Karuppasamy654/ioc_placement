import hashlib
import json
from typing import Dict, Any, Tuple, Optional
from backend.memory.db import get_db_connection
from backend.scraping.normalizer import DataNormalizer

class RecordDeduplicator:
    """
    Computes stable content hashes and identifies repeated records
    using canonical URLs and SHA-256 fingerprinting.
    """

    @staticmethod
    def compute_content_hash(data_dict: Dict[str, Any]) -> str:
        """
        Generates a deterministic SHA-256 hash of record payload.
        """
        keys_to_hash = ["title", "company", "description", "required_skills", "category", "original_url"]
        sub_dict = {k: data_dict.get(k) for k in keys_to_hash if k in data_dict}
        serialized = json.dumps(sub_dict, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def is_job_duplicate(canonical_url: str, content_hash: str) -> Tuple[bool, Optional[int]]:
        """
        Checks SQLite database for duplicate job by canonical_url or content_hash.
        Returns (is_duplicate, existing_record_id).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, content_hash FROM job_postings WHERE canonical_url = ?", (canonical_url,))
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return True, row["id"]

        cursor.execute("SELECT id FROM job_postings WHERE content_hash = ?", (content_hash,))
        row_hash = cursor.fetchone()
        conn.close()
        
        if row_hash:
            return True, row_hash["id"]

        return False, None

    @staticmethod
    def is_resource_duplicate(canonical_url: str, content_hash: str) -> Tuple[bool, Optional[int]]:
        """
        Checks SQLite database for duplicate learning resource.
        Returns (is_duplicate, existing_record_id).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, content_hash FROM learning_resources WHERE canonical_url = ?", (canonical_url,))
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return True, row["id"]

        cursor.execute("SELECT id FROM learning_resources WHERE content_hash = ?", (content_hash,))
        row_hash = cursor.fetchone()
        conn.close()

        if row_hash:
            return True, row_hash["id"]

        return False, None
