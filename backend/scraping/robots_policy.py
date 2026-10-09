import urllib.parse
import urllib.robotparser
import socket
import ipaddress
from typing import Tuple

class SSRFProtection:
    """
    Prevents Server-Side Request Forgery (SSRF) by validating target schemes,
    hostnames, and checking resolved IP addresses against private/reserved ranges.
    """
    BLOCKED_SCHEMES = {"file", "ftp", "gopher", "dict", "sftp", "ldap", "tftp"}
    ALLOWED_SCHEMES = {"http", "https"}

    @staticmethod
    def is_url_safe(url: str) -> Tuple[bool, str]:
        if not url or not isinstance(url, str):
            return False, "URL is empty or invalid type"

        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            return False, f"Invalid URL structure: {e}"

        scheme = (parsed.scheme or "").lower()
        if scheme not in SSRFProtection.ALLOWED_SCHEMES:
            return False, f"Forbidden URL scheme '{scheme}'. Only HTTP/HTTPS allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL missing hostname"

        hostname_lower = hostname.lower()
        if hostname_lower in {"localhost", "loopback", "127.0.0.1", "::1", "0.0.0.0"}:
            return False, "Access to localhost/loopback address is restricted."

        # Check for private or loopback IP directly
        try:
            ip_obj = ipaddress.ip_address(hostname_lower)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_multicast:
                return False, f"Access to private/reserved IP address '{hostname_lower}' is restricted."
        except ValueError:
            # Hostname is a domain name, attempt safe DNS resolution check
            try:
                ip_list = socket.getaddrinfo(hostname, None)
                for item in ip_list:
                    resolved_ip_str = item[4][0]
                    resolved_ip = ipaddress.ip_address(resolved_ip_str)
                    if resolved_ip.is_private or resolved_ip.is_loopback or resolved_ip.is_reserved:
                        return False, f"Domain '{hostname}' resolves to restricted private IP '{resolved_ip_str}'."
            except socket.gaierror:
                # Unable to resolve IP at policy check time, allow network request layer to handle connection timeout safely
                pass

        return True, "URL is safe"


class RobotsPolicy:
    """
    Parses robots.txt files for target hosts and enforces permitted path rules.
    """
    _cache = {}

    @staticmethod
    def is_allowed(url: str, user_agent: str = "IOCPlacementAgentBot/1.0") -> bool:
        is_safe, _ = SSRFProtection.is_url_safe(url)
        if not is_safe:
            return False

        try:
            parsed = urllib.parse.urlparse(url)
            host_base = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = f"{host_base}/robots.txt"

            if host_base not in RobotsPolicy._cache:
                parser = urllib.robotparser.RobotFileParser()
                parser.set_url(robots_url)
                try:
                    parser.read()
                    RobotsPolicy._cache[host_base] = parser
                except Exception:
                    # If robots.txt fetch fails or does not exist, default to permissive
                    RobotsPolicy._cache[host_base] = None

            rp = RobotsPolicy._cache.get(host_base)
            if rp is None:
                return True

            return rp.can_fetch(user_agent, url)
        except Exception:
            return True
