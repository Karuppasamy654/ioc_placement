from typing import Optional
from backend.models.schemas import StudentInput, ResumeData, StudentProfile, ResumeScoreData
from backend.models.state import SessionState
from backend.services.gemini_service import gemini_service
from backend.memory.memory_manager import MemoryManager
from backend.utils.logger import log_agent_start, log_agent_action, log_agent_end, log_memory_op

class ProfileAnalysisAgent:
    @staticmethod
    def analyze_profile(student_input: StudentInput, resume_data: Optional[ResumeData], state: SessionState) -> StudentProfile:
        """
        Analyzes student inputs, resume data, and persistent memory history to produce a structured student profile, ATS score, and skill gap analysis.
        """
        start_time = log_agent_start(
            "Profile Analysis Agent",
            f"Candidate: '{student_input.name}' | Role: '{student_input.target_role}' @ '{student_input.target_company}' | Prep Window: {student_input.prep_days} days",
            state=state
        )

        # 1. Query Persistent Memory History
        log_memory_op(
            "READ",
            f"Checking persistent memory DB for prior sessions of student '{student_input.name}'...",
            state=state
        )
        history = MemoryManager.get_student_history(student_input.name)

        if history["has_history"]:
            past_summary = (
                f"History Found! {history['attempt_count']} previous test attempt(s) | "
                f"Previous Weak Topics: {history['previous_weak_topics']} | "
                f"Repeated Weaknesses: {history['repeated_weaknesses']} | "
                f"Last Score: {history['last_score']}%"
            )
            log_memory_op("READ RESULT", f"Candidate '{student_input.name}' has existing preparation history.", past_summary, state=state)
            log_agent_action(
                "Profile Analysis Agent",
                f"[MEMORY RECALL] Prior student history loaded: {len(history['previous_weak_topics'])} previous weak topics identified.",
                state=state
            )
        else:
            log_memory_op("READ RESULT", f"No prior history found for candidate '{student_input.name}'. Proceeding with initial profile analysis.", state=state)

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

        memory_context = ""
        if history["has_history"]:
            memory_context = f"""
PERSISTENT MEMORY LEARNING HISTORY:
- Previous Mock Test Attempts: {history['attempt_count']}
- Past Weak Topics: {', '.join(history['previous_weak_topics'])}
- Repeated Weaknesses across sessions: {', '.join(history['repeated_weaknesses'])}
- Last Recorded Test Score: {history['last_score']}%
(Note: Treat past weak topics as high-priority focus areas for this session).
"""

        prompt = f"""
Analyze the student candidate profile for placement preparation and calculate ATS resume match score:
- Name: {student_input.name}
- Target Company: {student_input.target_company}
- Target Role: {student_input.target_role}
- Preparation Window: {student_input.prep_days} days ({student_input.daily_hours} hours/day)
- Self-Reported Skills: {', '.join(user_skills_list)}
{resume_summary}
{memory_context}

Task:
Identify:
1. Candidate's core strong technical areas based ONLY on provided evidence.
2. Weaker or less-evidenced technical areas (include past unmastered weak topics if applicable).
3. Essential technical skills required for a {student_input.target_role} at {student_input.target_company}.
4. Skill gaps between current profile and target role requirements.
5. Actionable recommendations for preparation.
6. ATS Compatibility Score (0-100%) against target company/role standards.
7. Matched skills & Missing skills required for ATS pass.
8. What needs to be changed in the resume (formatting feedback & actionable resume modifications).

Return JSON format:
{{
  "strong_areas": ["..."],
  "weak_areas": ["..."],
  "relevant_tech_for_role": ["..."],
  "resume_gaps": ["..."],
  "recommendations": ["..."],
  "ats_score": 78.5,
  "matched_skills": ["..."],
  "missing_skills": ["..."],
  "formatting_feedback": ["..."],
  "actionable_improvements": ["..."]
}}
"""
        log_agent_action("Profile Analysis Agent", "Sending candidate profile & resume to Gemini for ATS compatibility scoring and skill gap analysis...", state=state)
        raw_json = gemini_service.generate_json(
            prompt,
            system_instruction="You are an expert ATS screener and technical career mentor. Do not fabricate missing information.",
            purpose=f"Profile ATS Score & Gap Analysis for {student_input.name}",
            state=state
        )

        strong = []
        weak = []
        relevant_tech = []
        gaps = []
        recs = []
        ats_score = 75.0
        matched_sk = []
        missing_sk = []
        fmt_fb = []
        act_imp = []

        if raw_json and isinstance(raw_json, dict):
            strong = raw_json.get("strong_areas", [])
            weak = raw_json.get("weak_areas", [])
            relevant_tech = raw_json.get("relevant_tech_for_role", [])
            gaps = raw_json.get("resume_gaps", [])
            recs = raw_json.get("recommendations", [])
            ats_score = float(raw_json.get("ats_score", 75.0))
            matched_sk = raw_json.get("matched_skills", [])
            missing_sk = raw_json.get("missing_skills", [])
            fmt_fb = raw_json.get("formatting_feedback", [])
            act_imp = raw_json.get("actionable_improvements", [])

        # Fallback if Gemini unconfigured or returned empty
        if not strong and user_skills_list:
            strong = user_skills_list[:3]
        if not weak and history.get("previous_weak_topics"):
            weak = history["previous_weak_topics"]
        if not gaps:
            gaps = [f"Advanced System Design for {student_input.target_role}", "Company-specific coding patterns"]
        if not recs:
            recs = ["Focus daily on high-priority weak areas", "Practice timed mock assessments"]

        if not fmt_fb:
            fmt_fb = ["Add quantitative achievements (% performance improvement) to your project descriptions."]
        if not act_imp:
            act_imp = [f"Explicitly list core skills required for {student_input.target_role} in a prominent Technical Skills section."]

        # Guarantee historical weak topics are in weak_areas if candidate had prior sessions
        if history["has_history"]:
            for past_w in history["previous_weak_topics"]:
                if past_w not in weak and past_w not in strong:
                    weak.append(past_w)

        resume_score_details = ResumeScoreData(
            resume_score=ats_score,
            matched_skills=matched_sk if matched_sk else user_skills_list[:4],
            missing_skills=missing_sk if missing_sk else gaps[:3],
            formatting_feedback=fmt_fb,
            actionable_improvements=act_imp
        )

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
            recommendations=recs,
            ats_resume_score=ats_score,
            resume_score_details=resume_score_details
        )

        # 2. Save Student Profile to Persistent Memory
        MemoryManager.save_student_profile(profile)
        log_memory_op(
            "WRITE",
            f"Saved student profile for '{profile.name}' with ATS Score {ats_score}% to SQLite database.",
            f"Strong: {len(strong)} | Weak: {len(weak)} | Gaps: {len(gaps)} | ATS Score: {ats_score}%",
            state=state
        )

        log_agent_end(
            "Profile Analysis Agent",
            f"Profile analysis complete. ATS Match Score: {ats_score}%. Identified {len(gaps)} skill gaps and {len(weak)} weak areas.",
            start_time,
            state=state
        )

        return profile


