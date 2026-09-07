from typing import Optional, List
from backend.models.schemas import StudentProfile, CompanyResearch, Roadmap, RoadmapDay, RoadmapTask
from backend.models.state import SessionState
from backend.services.gemini_service import gemini_service
from backend.utils.logger import log_event

class RoadmapAgent:
    @staticmethod
    def generate_roadmap(
        profile: StudentProfile,
        company_research: CompanyResearch,
        state: SessionState
    ) -> Roadmap:
        """
        Dynamically generates a personalized multi-day preparation schedule matching student available days and daily study hours.
        """
        log_event("Roadmap Agent", f"Generating dynamic {profile.prep_days}-day roadmap ({profile.daily_hours} hrs/day)...", "STARTED", state)

        research_context = ""
        if company_research.research_available:
            research_context = f"Company Hiring Focus & Key Skills: {', '.join(company_research.key_skills)}\nSearch Excerpt: {company_research.role_description[:500]}"
        else:
            research_context = f"Note: Company-specific live data unavailable. Base strategy strictly on target role '{profile.target_role}'."

        prompt = f"""
Create a highly personalized, dynamic day-by-day placement preparation roadmap.

Student Profile & Constraints:
- Candidate Name: {profile.name}
- Target Company: {profile.target_company}
- Target Role: {profile.target_role}
- Total Preparation Days: {profile.prep_days}
- Daily Available Hours: {profile.daily_hours}
- Proven Strong Areas: {', '.join(profile.strong_areas)}
- Identified Weak Areas: {', '.join(profile.weak_areas)}
- Identified Resume/Skill Gaps: {', '.join(profile.resume_gaps)}
- Research Context: {research_context}

DYNAMIC ALLOCATION RULES:
1. Generate EXACTLY {profile.prep_days} days.
2. The total hours per day MUST sum to approximately {profile.daily_hours} hours.
3. If candidate is strong in DSA, allocate minimal basic DSA time and focus on advanced patterns.
4. If candidate is weak in specific topics (e.g. DBMS, System Design), allocate significantly more time to those.
5. If total prep days is short (1-5 days), prioritize high-yield interview topics and mock tests. If longer (6-30 days), include deep subject domain revision and project reviews.
6. Tailor topics specifically for {profile.target_role} (e.g. Frontend = React/CSS/DOM/Web Performance; Backend = DB/APIs/Concurrency/Caching).

Return JSON format:
{{
  "overview": "High-level summary of the tailored strategy...",
  "days": [
    {{
      "day_number": 1,
      "day_title": "Day 1 Title",
      "tasks": [
        {{
          "topic": "Topic Name",
          "subtopics": ["Subtopic 1", "Subtopic 2"],
          "duration_hours": 2.5,
          "priority": "High",
          "practice_task": "Specific coding/reading task",
          "expected_outcome": "Outcome metric"
        }}
      ]
    }}
  ]
}}
"""
        raw_json = gemini_service.generate_json(prompt, system_instruction="You are a senior technical mentor creating strict, dynamic preparation roadmaps in valid JSON.")

        days_list: List[RoadmapDay] = []
        overview = f"Tailored {profile.prep_days}-day strategy for {profile.target_role} at {profile.target_company}."

        if raw_json and isinstance(raw_json, dict):
            overview = raw_json.get("overview", overview)
            raw_days = raw_json.get("days", [])
            for d in raw_days:
                tasks_list = []
                day_hours = 0.0
                for t in d.get("tasks", []):
                    dur = float(t.get("duration_hours", 2.0))
                    day_hours += dur
                    tasks_list.append(RoadmapTask(
                        topic=t.get("topic", "Technical Preparation"),
                        subtopics=t.get("subtopics", []),
                        duration_hours=dur,
                        priority=t.get("priority", "Medium"),
                        practice_task=t.get("practice_task", "Solve practice problems"),
                        expected_outcome=t.get("expected_outcome", "Master concept fundamentals")
                    ))
                days_list.append(RoadmapDay(
                    day_number=int(d.get("day_number", len(days_list) + 1)),
                    day_title=d.get("day_title", f"Day {len(days_list) + 1}"),
                    tasks=tasks_list,
                    total_hours=round(day_hours, 1)
                ))

        # Dynamic fallback if JSON parsing failed or incomplete day count
        if len(days_list) < profile.prep_days:
            for i in range(len(days_list) + 1, profile.prep_days + 1):
                tasks = [
                    RoadmapTask(
                        topic=f"{profile.target_role} Core Domain Focus - Part {i}",
                        subtopics=["Data Structures", "System Design", "Problem Solving"],
                        duration_hours=round(profile.daily_hours / 2, 1),
                        priority="High",
                        practice_task=f"Practice 3 LeetCode problems related to {profile.target_role}",
                        expected_outcome="Sub-hour problem solving velocity"
                    ),
                    RoadmapTask(
                        topic="Core CS & Company Practice",
                        subtopics=["DBMS", "Operating Systems", "Networking"],
                        duration_hours=round(profile.daily_hours / 2, 1),
                        priority="Medium",
                        practice_task="Revise technical notes and interview questions",
                        expected_outcome="Clean conceptual recall"
                    )
                ]
                days_list.append(RoadmapDay(
                    day_number=i,
                    day_title=f"Day {i}: Intensive Preparation",
                    tasks=tasks,
                    total_hours=profile.daily_hours
                ))

        roadmap = Roadmap(
            total_days=profile.prep_days,
            daily_hours=profile.daily_hours,
            days=days_list,
            overview=overview
        )

        log_event(
            "Roadmap Agent",
            f"Roadmap generated successfully with {len(roadmap.days)} personalized study days.",
            "COMPLETED",
            state
        )

        return roadmap
