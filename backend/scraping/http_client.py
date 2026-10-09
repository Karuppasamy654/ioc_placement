import time
import random
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any
from backend.scraping.robots_policy import SSRFProtection

try:
    import httpx
except ImportError:
    httpx = None

class ResilientHTTPClient:
    """
    Production-grade HTTP client with SSRF protection, domain rate-limiting,
    bounded retries with exponential backoff & jitter, explicit timeouts,
    and response size safety limits.
    """
    DEFAULT_USER_AGENT = "IOCPlacementAgentBot/1.0 (+https://github.com/Karuppasamy654/ioc_placement)"
    _last_request_time: Dict[str, float] = {}

    def __init__(
        self,
        timeout_seconds: float = 12.0,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        max_response_bytes: int = 5 * 1024 * 1024, # 5 MB limit
        user_agent: Optional[str] = None
    ):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_response_bytes = max_response_bytes
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT

    def _apply_rate_limit(self, domain: str, min_interval_seconds: float = 1.0):
        now = time.time()
        last_time = ResilientHTTPClient._last_request_time.get(domain, 0.0)
        elapsed = now - last_time
        if elapsed < min_interval_seconds:
            sleep_time = min_interval_seconds - elapsed
            time.sleep(sleep_time)
        ResilientHTTPClient._last_request_time[domain] = time.time()

    def fetch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        rate_limit_rps: float = 1.0
    ) -> Dict[str, Any]:
        """
        Fetches URL content safely and returns a dictionary with status, content, headers, and error details.
        """
        is_safe, error_msg = SSRFProtection.is_url_safe(url)
        if not is_safe:
            return {
                "success": False,
                "status_code": 403,
                "error": f"SSRF Protection Rejected URL: {error_msg}",
                "content": "",
                "headers": {},
                "url": url
            }

        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()

        min_interval = 1.0 / max(rate_limit_rps, 0.1)
        self._apply_rate_limit(domain, min_interval)

        request_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/json,application/rss+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if headers:
            request_headers.update(headers)

        attempt = 0
        last_exception_msg = ""

        while attempt < self.max_retries:
            attempt += 1
            try:
                if httpx is not None:
                    with httpx.Client(
                        timeout=httpx.Timeout(self.timeout_seconds, connect=5.0),
                        follow_redirects=True,
                        max_redirects=5
                    ) as client:
                        response = client.get(url, headers=request_headers)
                        
                        # Validate final redirected URL for SSRF safety
                        final_url = str(response.url)
                        is_final_safe, final_err = SSRFProtection.is_url_safe(final_url)
                        if not is_final_safe:
                            return {
                                "success": False,
                                "status_code": 403,
                                "error": f"SSRF Protection Rejected Redirect URL: {final_err}",
                                "content": "",
                                "headers": {},
                                "url": final_url
                            }

                        if len(response.content) > self.max_response_bytes:
                            return {
                                "success": False,
                                "status_code": 413,
                                "error": f"Response payload size ({len(response.content)} bytes) exceeds limit ({self.max_response_bytes} bytes)",
                                "content": "",
                                "headers": dict(response.headers),
                                "url": final_url
                            }

                        if response.status_code == 200:
                            return {
                                "success": True,
                                "status_code": 200,
                                "error": "",
                                "content": response.text,
                                "bytes": response.content,
                                "headers": dict(response.headers),
                                "url": final_url
                            }
                        elif response.status_code in {429, 503, 502, 504}:
                            # Exponential backoff on rate limit or server errors
                            retry_after = response.headers.get("Retry-After")
                            if retry_after and retry_after.isdigit():
                                sleep_sec = float(retry_after)
                            else:
                                sleep_sec = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                            time.sleep(sleep_sec)
                            last_exception_msg = f"HTTP {response.status_code} server error"
                        else:
                            return {
                                "success": False,
                                "status_code": response.status_code,
                                "error": f"HTTP {response.status_code} error response",
                                "content": response.text,
                                "headers": dict(response.headers),
                                "url": final_url
                            }
                else:
                    # Fallback standard library urllib
                    req = urllib.request.Request(url, headers=request_headers)
                    with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                        content_bytes = resp.read(self.max_response_bytes + 1)
                        if len(content_bytes) > self.max_response_bytes:
                            return {
                                "success": False,
                                "status_code": 413,
                                "error": "Response size exceeds maximum allowed limit.",
                                "content": "",
                                "headers": {},
                                "url": url
                            }
                        text = content_bytes.decode("utf-8", errors="ignore")
                        return {
                            "success": True,
                            "status_code": resp.status,
                            "error": "",
                            "content": text,
                            "bytes": content_bytes,
                            "headers": dict(resp.headers),
                            "url": url
                        }

            except Exception as e:
                last_exception_msg = str(e)
                sleep_sec = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                time.sleep(sleep_sec)

        return {
            "success": False,
            "status_code": 504,
            "error": f"Failed after {self.max_retries} attempts. Last error: {last_exception_msg}",
            "content": "",
            "headers": {},
            "url": url
        }
