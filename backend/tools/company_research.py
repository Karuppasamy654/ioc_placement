import urllib.parse
import urllib.request
import re
from typing import List, Dict, Any
from backend.models.schemas import CompanyResearch, CompanyResearchSource
from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

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
    def research_company_and_role(company_name: str, role_name: str, state=None) -> CompanyResearch:
        start_time = log_tool_start("Company Research Tool", f"company='{company_name}', role='{role_name}'", state=state)
        
        query = f"{company_name} {role_name} interview process placement technical skills requirements"
        sources: List[CompanyResearchSource] = []
        snippets: List[str] = []

        log_tool_process("Company Research Tool", f"Executing web search query: '{query}'", state=state)

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
                log_tool_process("Company Research Tool", f"DuckDuckGo API notice: {e}", state=state)

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
                    log_tool_process("Company Research Tool", f"httpx request notice: {e}", state=state)

            if not raw_html:
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10.0) as resp:
                        if resp.status == 200:
                            raw_html = resp.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    log_tool_process("Company Research Tool", f"urllib request notice: {e}", state=state)

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

        # 4. Generate Curated Real Technical Study Links & Official Careers URLs
        study_links: List[CompanyResearchSource] = [
            CompanyResearchSource(
                title="LeetCode Top Interview Questions & Patterns",
                source_type="Coding Practice & DSA",
                url="https://leetcode.com/problemset/all/",
                category="study"
            ),
            CompanyResearchSource(
                title="GeeksforGeeks CS Core Fundamentals & Quiz",
                source_type="CS Domain Knowledge",
                url="https://www.geeksforgeeks.org/computer-science-projects/",
                category="study"
            ),
            CompanyResearchSource(
                title="System Design Primer (GitHub Reference)",
                source_type="Architecture & System Design",
                url="https://github.com/donnemartin/system-design-primer",
                category="study"
            ),
            CompanyResearchSource(
                title="Developer Roadmaps & Skill Guides",
                source_type="Role Preparation Roadmap",
                url="https://roadmap.sh",
                category="study"
            )
        ]

        # Official company careers map
        comp_lower = company_name.lower().strip()
        official_careers = f"https://www.google.com/search?q={urllib.parse.quote(company_name + ' official careers job portal')}"
        
        if "google" in comp_lower:
            official_careers = "https://careers.google.com"
        elif "microsoft" in comp_lower:
            official_careers = "https://careers.microsoft.com"
        elif "amazon" in comp_lower:
            official_careers = "https://www.amazon.jobs"
        elif "meta" in comp_lower or "facebook" in comp_lower:
            official_careers = "https://www.metacareers.com"
        elif "apple" in comp_lower:
            official_careers = "https://www.apple.com/careers"
        elif "netflix" in comp_lower:
            official_careers = "https://jobs.netflix.com"
        elif "tcs" in comp_lower or "tata" in comp_lower:
            official_careers = "https://www.tcs.com/careers"
        elif "infosys" in comp_lower:
            official_careers = "https://www.infosys.com/careers/"
        elif "wipro" in comp_lower:
            official_careers = "https://careers.wipro.com"
        elif "accenture" in comp_lower:
            official_careers = "https://www.accenture.com/in-en/careers"

        # Handle research unavailability without fabricating data
        if not snippets or len(sources) == 0:
            result_summary = f"Live research unavailable for '{company_name}'. Falling back to role-based prep for '{role_name}'."
            log_tool_result("Company Research Tool", result_summary, start_time, state=state)
            return CompanyResearch(
                company_name=company_name,
                role_name=role_name,
                official_info=f"Live external company data for '{company_name}' is currently unavailable.",
                role_description=f"Standard target role requirements for {role_name}.",
                key_skills=["DSA", "System Design", "DBMS", "Problem Solving"],
                hiring_process=["Online Technical Screening", "Technical Coding Rounds", "System Design Round", "HR Round"],
                research_available=False,
                sources=[],
                study_links=study_links,
                official_careers_url=official_careers,
                notes="Company-specific research could not be retrieved from external sources. System will fall back to general role-based preparation."
            )

        combined_info = "\n\n".join(snippets)
        extracted_skills = []
        keywords = ["dsa", "python", "java", "system design", "sql", "dbms", "react", "node", "c++", "aws", "algorithms", "data structures", "oop", "operating systems", "networking"]
        for kw in keywords:
            if kw in combined_info.lower():
                extracted_skills.append(kw.upper() if len(kw) <= 3 else kw.title())

        result_summary = f"{len(sources)} real research sources retrieved | {len(extracted_skills)} role skills identified"
        log_tool_result("Company Research Tool", result_summary, start_time, state=state)

        return CompanyResearch(
            company_name=company_name,
            role_name=role_name,
            official_info=f"Real web research compiled for {company_name} targeting {role_name}.",
            role_description=combined_info[:1500],
            key_skills=list(set(extracted_skills)) if extracted_skills else ["DSA", "System Design", "DBMS"],
            hiring_process=["Online Assessment / Aptitude + Technical", "Technical Coding Interview", "System Architecture / Live Problem Solving", "HR & Culture Fit"],
            research_available=True,
            sources=sources,
            study_links=study_links,
            official_careers_url=official_careers,
            notes="Sources retrieved from live public search results and curated learning indexes."
        )

