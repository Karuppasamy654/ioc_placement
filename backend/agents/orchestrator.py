import os
import time
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
from backend.utils.logger import print_banner, print_section, print_state_transition, log_agent_start, log_agent_action, log_agent_end, log_tool_start, log_tool_process, log_tool_result

class OrchestratorAgent:
    @staticmethod
    def run_preparation_pipeline(student_input: StudentInput, resume_path: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        return OrchestratorAgent.run_preparation_pipeline_with_session(session_id, student_input, resume_path)

    @staticmethod
    def run_preparation_pipeline_with_session(session_id: str, student_input: StudentInput, resume_path: Optional[str] = None) -> str:
        """
        Executes the initial preparation pipeline:
        Profile Agent -> Resume Parser Tool -> Company Research Tool -> Roadmap Agent -> Mock Test Agent
        """
        pipeline_start = time.time()
        state = state_manager.get_or_create_session(session_id)
        state.student_input = student_input

        print_banner(
            f"AGENTIC AI PLACEMENT PREPARATION PIPELINE",
            f"Candidate: {student_input.name} | Role: {student_input.target_role} @ {student_input.target_company} | Session: {session_id[:8]}"
        )

        print_state_transition("INIT", "PROFILE_ANALYSIS", state=state)

        # 1. Parse Resume if uploaded
        resume_data = None
        if resume_path and os.path.exists(resume_path):
            tool_start = log_tool_start("Resume Parser Tool", f"Parsing file: '{os.path.basename(resume_path)}'", state=state)
            log_tool_process("Resume Parser Tool", "Extracting text, technical skills, projects, and education history...", state=state)
            resume_data = ResumeParserTool.parse_file(resume_path)
            state.resume_data = resume_data
            log_tool_result(
                "Resume Parser Tool",
                f"Extracted {len(resume_data.technical_skills)} skills & {len(resume_data.projects)} projects.",
                tool_start,
                state=state
            )

        # 2. Profile Analysis Agent
        print_section("PROFILE ANALYSIS AGENT", emoji="👤")
        profile = ProfileAnalysisAgent.analyze_profile(student_input, resume_data, state)
        state.profile = profile

        print_state_transition("PROFILE_ANALYSIS", "COMPANY_RESEARCH", state=state)

        # 3. Company Research Tool
        print_section("COMPANY & ROLE RESEARCH TOOL", emoji="🔍")
        res_start = log_tool_start("Company Research Tool", f"Company: '{student_input.target_company}' | Role: '{student_input.target_role}'", state=state)
        log_tool_process("Company Research Tool", "Performing search & gathering live hiring criteria...", state=state)
        company_research = CompanyResearchTool.research_company_and_role(student_input.target_company, student_input.target_role)
        state.company_research = company_research
        if company_research.research_available:
            log_tool_result("Company Research Tool", f"Retrieved hiring criteria with {len(company_research.sources)} web sources.", res_start, state=state)
        else:
            log_tool_result("Company Research Tool", f"Live web search unavailable. Using curated {student_input.target_role} benchmarks.", res_start, state=state)

        print_state_transition("COMPANY_RESEARCH", "ROADMAP_GENERATION", state=state)

        # 4. Roadmap Agent
        print_section("DYNAMIC ROADMAP AGENT", emoji="🗺️")
        roadmap = RoadmapAgent.generate_roadmap(profile, company_research, state)
        state.roadmap = roadmap

        print_state_transition("ROADMAP_GENERATION", "MOCK_TEST_GENERATION", state=state)

        # 5. Mock Test Agent
        print_section("DYNAMIC MOCK TEST AGENT", emoji="📝")
        mock_test = MockTestAgent.generate_mock_test(
            session_id=session_id,
            profile=profile,
            company_research=company_research,
            roadmap=roadmap,
            state=state,
            question_count=55
        )
        state.mock_test = mock_test

        print_state_transition("MOCK_TEST_GENERATION", "COMPLETED", state=state)

        total_duration = round(time.time() - pipeline_start, 2)
        print_banner(
            f"WORKFLOW COMPLETED SUCCESSFULLY IN {total_duration}s",
            f"Generated {len(roadmap.days)} Roadmap Days & {len(mock_test.questions)} MCQs | Session: {session_id}"
        )

        return session_id

    @staticmethod
    def process_test_submission(submission: QuizSubmission) -> tuple[PerformanceReport, AdaptiveAdjustment]:
        """
        Executes performance evaluation & adaptive learning workflow following test submission.
        """
        submission_start = time.time()
        state = state_manager.get_session(submission.session_id)
        if not state or not state.mock_test:
            raise ValueError(f"Session {submission.session_id} not found or missing active mock test.")

        print_banner(
            "TEST SUBMISSION & ADAPTIVE EVALUATION PIPELINE",
            f"Session: {submission.session_id[:8]} | Total Submitted Answers: {len(submission.answers)}"
        )

        print_state_transition("SUBMITTED", "PERFORMANCE_EVALUATION", state=state)

        print_section("PERFORMANCE EVALUATION & ADAPTIVE AGENT", emoji="📊")
        report, adjustment = PerformanceAnalysisAgent.analyze_performance_and_adapt(
            test=state.mock_test,
            submission=submission,
            current_roadmap=state.roadmap,
            state=state
        )

        state.performance = report
        state.adaptive_adjustment = adjustment

        print_state_transition("PERFORMANCE_EVALUATION", "ADAPTIVE_LEARNING", state=state)

        # If updated roadmap days present, update active roadmap in state
        if state.roadmap and adjustment.updated_roadmap_days:
            state.roadmap.days = adjustment.updated_roadmap_days

        print_state_transition("ADAPTIVE_LEARNING", "COMPLETED", state=state)

        total_duration = round(time.time() - submission_start, 2)
        print_banner(
            f"EVALUATION & ADAPTIVE LOOP COMPLETED IN {total_duration}s",
            f"Score: {report.score_percentage}% | Updated Roadmap Days: {len(state.roadmap.days if state.roadmap else 0)}"
        )

        return report, adjustment

