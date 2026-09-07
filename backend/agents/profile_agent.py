from typing import Optional
from backend.models.schemas import StudentInput, ResumeData, StudentProfile
from backend.models.state import SessionState
from backend.services.gemini_service import gemini_service
from backend.utils.logger import log_event

class ProfileAnalysisAgent:
    @staticmethod
    def analyze_profile(student_input: StudentInput, resume_data: Optional[ResumeData], state: SessionState) -> StudentProfile:
        """
        Analyzes student inputs and resume data to produce a structured student profile and skill gap analysis.
        """
        log_event("Profile Analysis Agent", "Analyzing student profile, current skills, and uploaded resume...", "STARTED", state)

        user_skills_list = [s.strip() for s in student_input.current_skills.split(",") if s.strip()]
        
        # Combine user entered skills + resume skills if available
        if resume_data and resume_data.technical_skills:
            user_skills_list = list(set(user_skills_list + resume_data.technical_skills))

        # Build prompt for Gemini to identify gaps vs target role
        resume_summary = ""
        if resume_data and resume_data.extracted_text:
            resume_summary = f"""
Extracted Resume Summary:
- Education: {', '.join(resume_data.education)}
- Programming Languages: {', '.join(resume_data.programming_languages)}
- Frameworks: {', '.join(resume_data.frameworks)}
- Databases: {', '.join(resume_data.databases)}
- Key Projects: {'; '.join(resume_data.projects[:3])}
- Work Experience: {'; '.join(resume_data.experience[:2])}
"""
        else:
            resume_summary = "No resume uploaded. Analysis based strictly on student-provided inputs."

        prompt = f"""
Analyze the student candidate profile for placement preparation:
- Name: {student_input.name}
- Target Company: {student_input.target_company}
- Target Role: {student_input.target_role}
- Preparation Window: {student_input.prep_days} days ({student_input.daily_hours} hours/day)
- Self-Reported Skills: {', '.join(user_skills_list)}
{resume_summary}

Task:
Identify:
1. Candidate's core strong technical areas based ONLY on provided evidence.
2. Weaker or less-evidenced technical areas.
3. Essential technical skills required for a {student_input.target_role} at {student_input.target_company}.
4. Skill gaps between current profile and target role requirements.
5. Specific actionable recommendations for preparation.

Return JSON format:
{{
  "strong_areas": ["..."],
  "weak_areas": ["..."],
  "relevant_tech_for_role": ["..."],
  "resume_gaps": ["..."],
  "recommendations": ["..."]
}}
"""
        raw_json = gemini_service.generate_json(prompt, system_instruction="You are an expert technical interviewer and career assessment agent. Do not fabricate missing information.")

        strong = []
        weak = []
        relevant_tech = []
        gaps = []
        recs = []

        if raw_json and isinstance(raw_json, dict):
            strong = raw_json.get("strong_areas", [])
            weak = raw_json.get("weak_areas", [])
            relevant_tech = raw_json.get("relevant_tech_for_role", [])
            gaps = raw_json.get("resume_gaps", [])
            recs = raw_json.get("recommendations", [])

        # Fallback if Gemini unconfigured or returned empty
        if not strong and user_skills_list:
            strong = user_skills_list[:3]
        if not gaps:
            gaps = [f"Advanced System Design for {student_input.target_role}", "Company-specific coding patterns"]
        if not recs:
            recs = ["Focus daily on high-priority weak areas", "Practice timed mock assessments"]

        profile = StudentProfile(
            name=student_input.name,
            target_company=student_input.target_company,
            target_role=student_input.target_role,
            prep_days=student_input.prep_days,
            daily_hours=student_input.daily_hours,
            user_skills=user_skills_list,
            resume_data=resume_data,
            strong_areas=strong,
            weak_areas=weak,
            relevant_tech_for_role=relevant_tech,
            resume_gaps=gaps,
            recommendations=recs
        )

        log_event(
            "Profile Analysis Agent",
            f"Profile analysis complete. Identified {len(gaps)} skill gaps and {len(strong)} strong areas.",
            "COMPLETED",
            state
        )

        return profile
