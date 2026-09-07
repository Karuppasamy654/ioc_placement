import os
import uuid
from typing import Optional
from backend.models.schemas import StudentInput, StudentProfile, CompanyResearch, Roadmap, MockTest, PerformanceReport, AdaptiveAdjustment, QuizSubmission
from backend.models.state import state_manager, SessionState
from backend.tools.resume_parser import ResumeParserTool
from backend.tools.company_research import CompanyResearchTool
from backend.agents.profile_agent import ProfileAnalysisAgent
from backend.agents.roadmap_agent import RoadmapAgent
from backend.agents.mock_test_agent import MockTestAgent
from backend.agents.performance_agent import PerformanceAnalysisAgent
from backend.utils.logger import log_event

class OrchestratorAgent:
    @staticmethod
    def run_preparation_pipeline(student_input: StudentInput, resume_path: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        return OrchestratorAgent.run_preparation_pipeline_with_session(session_id, student_input, resume_path)

    @staticmethod
    def run_preparation_pipeline_with_session(session_id: str, student_input: StudentInput, resume_path: Optional[str] = None) -> str:
        """
        Executes the initial pipeline using a pre-allocated session_id:
        Profile Agent -> Resume Parser Tool -> Company Research Tool -> Roadmap Agent -> Mock Test Agent
        """
        state = state_manager.get_or_create_session(session_id)
        state.student_input = student_input

        log_event("Orchestrator", f"Workflow started for student '{student_input.name}' (Target: {student_input.target_role} @ {student_input.target_company})", "STARTED", state)

        # 1. Parse Resume if uploaded
        resume_data = None
        if resume_path and os.path.exists(resume_path):
            log_event("Resume Parser Tool", f"Parsing uploaded resume file '{os.path.basename(resume_path)}'...", "STARTED", state)
            resume_data = ResumeParserTool.parse_file(resume_path)
            state.resume_data = resume_data
            log_event("Resume Parser Tool", f"Extracted {len(resume_data.technical_skills)} skills and {len(resume_data.projects)} projects from resume.", "COMPLETED", state)

        # 2. Profile Analysis Agent
        profile = ProfileAnalysisAgent.analyze_profile(student_input, resume_data, state)
        state.profile = profile

        # 3. Company Research Tool
        log_event("Company Research Tool", f"Researching live market standards for {student_input.target_company} targeting {student_input.target_role}...", "STARTED", state)
        company_research = CompanyResearchTool.research_company_and_role(student_input.target_company, student_input.target_role)
        state.company_research = company_research
        if company_research.research_available:
            log_event("Company Research Tool", f"Retrieved {len(company_research.sources)} real research sources.", "COMPLETED", state)
        else:
            log_event("Company Research Tool", f"Company search unavailable for {student_input.target_company}. Falling back to role-based target strategy.", "WARNING", state)

        # 4. Roadmap Agent
        roadmap = RoadmapAgent.generate_roadmap(profile, company_research, state)
        state.roadmap = roadmap

        # 5. Mock Test Agent (Pre-generate or prepare dynamic quiz)
        mock_test = MockTestAgent.generate_mock_test(
            session_id=session_id,
            profile=profile,
            company_research=company_research,
            roadmap=roadmap,
            state=state,
            question_count=55
        )
        state.mock_test = mock_test

        log_event("Orchestrator", f"Preparation workflow completed successfully. Session ID: {session_id}", "COMPLETED", state)
        return session_id

    @staticmethod
    def process_test_submission(submission: QuizSubmission) -> tuple[PerformanceReport, AdaptiveAdjustment]:
        """
        Executes performance evaluation & adaptive learning workflow following test submission.
        """
        state = state_manager.get_session(submission.session_id)
        if not state or not state.mock_test:
            raise ValueError(f"Session {submission.session_id} not found or missing active mock test.")

        log_event("Orchestrator", "Received test submission. Triggering Performance Analysis Agent...", "STARTED", state)

        report, adjustment = PerformanceAnalysisAgent.analyze_performance_and_adapt(
            test=state.mock_test,
            submission=submission,
            current_roadmap=state.roadmap,
            state=state
        )

        state.performance = report
        state.adaptive_adjustment = adjustment

        # If updated roadmap days present, update active roadmap in state
        if state.roadmap and adjustment.updated_roadmap_days:
            state.roadmap.days = adjustment.updated_roadmap_days

        log_event("Orchestrator", "Adaptive learning workflow complete. Next-day schedule updated.", "COMPLETED", state)

        return report, adjustment
