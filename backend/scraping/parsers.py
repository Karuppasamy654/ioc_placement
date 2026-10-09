import re
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from typing import List, Dict, Any
from backend.scraping.normalizer import DataNormalizer

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    BeautifulSoup = None

class RSSParser:
    """
    Parses RSS 2.0 / Atom feed XML structures into job or learning records.
    """

    @staticmethod
    def parse_jobs_rss(xml_content: str, base_url: str, source_name: str) -> List[Dict[str, Any]]:
        records = []
        if not xml_content:
            return records

        try:
            root = ET.fromstring(xml_content)
        except Exception as e:
            print(f"[RSS PARSER ERROR] XML parsing failed for {source_name}: {e}")
            return records

        # RSS 2.0 items or Atom entries
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items:
            title_node = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
            link_node = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
            desc_node = item.find("description") or item.find("{http://www.w3.org/2005/Atom}summary") or item.find("{http://www.w3.org/2005/Atom}content")
            pub_date_node = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}updated") or item.find("{http://www.w3.org/2005/Atom}published")

            title_text = title_node.text.strip() if title_node is not None and title_node.text else ""
            if not title_text:
                continue

            link_text = ""
            if link_node is not None:
                if link_node.text and link_node.text.strip():
                    link_text = link_node.text.strip()
                elif "href" in link_node.attrib:
                    link_text = link_node.attrib["href"].strip()

            if not link_text:
                continue

            raw_desc = desc_node.text if desc_node is not None and desc_node.text else ""
            clean_desc = DataNormalizer.normalize_text(raw_desc)

            # Strip HTML tags from description if BeautifulSoup available
            if BeautifulSoup and "<" in clean_desc:
                try:
                    soup = BeautifulSoup(raw_desc, "html.parser")
                    clean_desc = soup.get_text(" ", strip=True)
                except Exception:
                    pass

            pub_date = DataNormalizer.normalize_date(pub_date_node.text if pub_date_node is not None else None)

            # Extract company & location heuristics from title/description
            company = source_name
            if ":" in title_text:
                parts = title_text.split(":", 1)
                company = parts[0].strip()
                title_text = parts[1].strip()
            elif " at " in title_text:
                parts = title_text.split(" at ", 1)
                title_text = parts[0].strip()
                company = parts[1].strip()

            # Extract skills heuristic
            skills = DataNormalizer.normalize_skills(re.findall(r"\b[A-Za-z0-9+#.-]{2,15}\b", clean_desc))

            records.append({
                "title": title_text,
                "company": company,
                "role_type": DataNormalizer.normalize_role_type(title_text + " " + clean_desc),
                "description": clean_desc if len(clean_desc) >= 20 else (title_text + " - Full position details available on source listing page."),
                "required_skills": skills[:8],
                "qualifications": "Degree in Computer Science or related engineering domain.",
                "location": "Remote / Global",
                "work_arrangement": DataNormalizer.normalize_work_arrangement(title_text + " " + clean_desc),
                "salary_or_stipend": "",
                "application_deadline": "",
                "original_url": link_text,
                "publication_date": pub_date
            })

        return records


class JSONAPIParser:
    """
    Parses structured JSON API responses (such as RemoteOK API).
    """

    @staticmethod
    def parse_remoteok_jobs(json_data: Any, source_name: str) -> List[Dict[str, Any]]:
        records = []
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except Exception:
                return records

        if not isinstance(json_data, list):
            return records

        for item in json_data:
            if not isinstance(item, dict):
                continue

            title = item.get("position") or item.get("title")
            if not title:
                continue

            company = item.get("company") or "Tech Employer"
            url = item.get("url") or item.get("apply_url")
            if not url:
                continue
            if not url.startswith("http"):
                url = "https://remoteok.com" + url

            desc = item.get("description") or ""
            if BeautifulSoup and "<" in desc:
                try:
                    soup = BeautifulSoup(desc, "html.parser")
                    desc = soup.get_text(" ", strip=True)
                except Exception:
                    pass

            clean_desc = DataNormalizer.normalize_text(desc)
            tags = item.get("tags") or []
            skills = DataNormalizer.normalize_skills(tags)

            location = item.get("location") or "Remote"
            date_str = item.get("date")

            records.append({
                "title": title,
                "company": company,
                "role_type": DataNormalizer.normalize_role_type(title + " " + clean_desc),
                "description": clean_desc if len(clean_desc) >= 20 else (title + " - Full remote position description."),
                "required_skills": skills[:10],
                "qualifications": "Bachelor's degree or equivalent practical experience.",
                "location": location,
                "work_arrangement": "remote",
                "salary_or_stipend": f"${item.get('salary_min', 0)} - ${item.get('salary_max', 0)} USD" if item.get("salary_min") else "",
                "application_deadline": "",
                "original_url": url,
                "publication_date": DataNormalizer.normalize_date(date_str)
            })

        return records


class HTMLScraperParser:
    """
    Parses permitted public HTML documentation and career webpages into structured records.
    """

    @staticmethod
    def parse_learning_html(html_content: str, base_url: str, source_name: str, topic: str = "general") -> List[Dict[str, Any]]:
        records = []
        if not html_content:
            return records

        title = source_name
        description = ""
        extracted_links = []

        if BeautifulSoup:
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                # Strip non-content scripts and styles
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()

                title_tag = soup.find("title") or soup.find("h1")
                if title_tag:
                    title = title_tag.get_text(" ", strip=True)

                # Extract main paragraph content
                paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "h2", "h3"]) if len(p.get_text(strip=True)) > 25]
                description = "\n".join(paragraphs[:8])

                # Collect links to sub-topics
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    link_title = a.get_text(" ", strip=True)
                    if href and len(link_title) > 10 and not href.startswith("#") and not href.startswith("javascript:"):
                        full_url = urljoin(base_url, href)
                        extracted_links.append((link_title, full_url))
            except Exception as e:
                print(f"[HTML PARSER ERROR] BeautifulSoup error for {source_name}: {e}")

        if not description:
            description = DataNormalizer.normalize_text(html_content[:2000])

        if len(description) >= 15:
            records.append({
                "title": f"{source_name} - {title}",
                "category": topic,
                "description": description[:1800],
                "topics": DataNormalizer.normalize_skills([topic] + title.split()),
                "difficulty_level": "intermediate",
                "original_url": base_url,
                "publication_date": DataNormalizer.normalize_date(None)
            })

        # Add top sub-topic links as individual learning resources
        for link_title, link_url in extracted_links[:5]:
            records.append({
                "title": f"{topic.capitalize()} Guide: {link_title[:80]}",
                "category": topic,
                "description": f"Official documentation and technical guide for {link_title} in {topic.capitalize()}.",
                "topics": DataNormalizer.normalize_skills([topic, link_title]),
                "difficulty_level": "intermediate",
                "original_url": link_url,
                "publication_date": DataNormalizer.normalize_date(None)
            })

        return records
