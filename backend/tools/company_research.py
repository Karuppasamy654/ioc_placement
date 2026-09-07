import urllib.parse
import urllib.request
import re
from typing import List, Dict, Any
from backend.models.schemas import CompanyResearch, CompanyResearchSource

# Guarded optional imports with type ignore for MSYS2 / static IDE linters
try:
    import httpx  # type: ignore
except ImportError:
    httpx = None

try:
    from ddgs import DDGS  # type: ignore
except ImportError:
    try:
        from duckduckgo_search import DDGS  # type: ignore
    except ImportError:
        DDGS = None

class CompanyResearchTool:
    @staticmethod
    def research_company_and_role(company_name: str, role_name: str) -> CompanyResearch:
        query = f"{company_name} {role_name} interview process placement technical skills requirements"
        sources: List[CompanyResearchSource] = []
        snippets: List[str] = []

        # 1. Attempt DuckDuckGo search package if available
        if DDGS is not None:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                    for res in results:
                        title = res.get("title", "Web Search Result")
                        href = res.get("href", "")
                        body = res.get("body", "")
                        if href and body:
                            sources.append(CompanyResearchSource(
                                title=title,
                                source_type="Web Search / Career Info",
                                url=href
                            ))
                            snippets.append(f"[{title}] {body}")
            except Exception as e:
                print(f"[COMPANY RESEARCH TOOL WARNING] DuckDuckGo search error: {e}")

        # 2. Attempt HTTP request via httpx or urllib if no sources retrieved yet
        if not sources:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            raw_html = ""
            if httpx is not None:
                try:
                    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                        resp = client.get(url, headers=headers)
                        if resp.status_code == 200:
                            raw_html = resp.text
                except Exception as e:
                    print(f"[COMPANY RESEARCH TOOL WARNING] httpx fallback error: {e}")

            if not raw_html:
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10.0) as resp:
                        if resp.status == 200:
                            raw_html = resp.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    print(f"[COMPANY RESEARCH TOOL WARNING] urllib fallback error: {e}")

            if raw_html:
                urls = re.findall(r'class="result__url"\s+href="([^"]+)"', raw_html)
                titles = re.findall(r'class="result__snippet"[^>]*>([^<]+)<', raw_html)
                for i in range(min(len(urls), len(titles), 4)):
                    clean_url = urls[i].strip()
                    clean_snippet = titles[i].strip()
                    if not clean_url.startswith("http"):
                        clean_url = "https://" + clean_url
                    sources.append(CompanyResearchSource(
                        title=f"{company_name} Role Info Source #{i+1}",
                        source_type="Search Result",
                        url=clean_url
                    ))
                    snippets.append(clean_snippet)

        # 3. Handle research unavailability without fabricating data
        if not snippets or len(sources) == 0:
            print(f"[COMPANY RESEARCH TOOL INFO] Live research unavailable for {company_name}. Falling back to role-based target strategy.")
            return CompanyResearch(
                company_name=company_name,
                role_name=role_name,
                official_info=f"Live external company data for '{company_name}' is currently unavailable.",
                role_description=f"Standard target role requirements for {role_name}.",
                key_skills=[],
                hiring_process=[],
                research_available=False,
                sources=[],
                notes="Company-specific research could not be retrieved from external sources. System will fall back to general role-based preparation."
            )

        combined_info = "\n\n".join(snippets)
        extracted_skills = []
        keywords = ["dsa", "python", "java", "system design", "sql", "dbms", "react", "node", "c++", "aws", "algorithms", "data structures", "oop", "operating systems", "networking"]
        for kw in keywords:
            if kw in combined_info.lower():
                extracted_skills.append(kw.upper() if len(kw) <= 3 else kw.title())

        return CompanyResearch(
            company_name=company_name,
            role_name=role_name,
            official_info=f"Real web research compiled for {company_name} targeting {role_name}.",
            role_description=combined_info[:1500],
            key_skills=list(set(extracted_skills)),
            hiring_process=["Online Assessment / Aptitude + Technical", "Technical Coding Interview", "System Architecture / Live Problem Solving", "HR & Culture Fit"],
            research_available=True,
            sources=sources,
            notes="Sources retrieved from live public search results."
        )
