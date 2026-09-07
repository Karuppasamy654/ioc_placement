from typing import Optional
from backend.models.schemas import MockTest, StudentProfile, CompanyResearch, Roadmap
from backend.models.state import SessionState
from backend.tools.question_generator import QuestionGeneratorTool
from backend.memory.memory_manager import MemoryManager
from backend.utils.logger import log_agent_start, log_agent_action, log_agent_end, log_memory_op

class MockTestAgent:
    @staticmethod
    def generate_mock_test(
        session_id: str,
        profile: StudentProfile,
        company_research: CompanyResearch,
        roadmap: Optional[Roadmap],
        state: SessionState,
        question_count: int = 55
    ) -> MockTest:
        """
        Coordinates the dynamic generation of 50-60 placement MCQs tailored to the student and their memory history.
        """
        start_time = log_agent_start(
            "Mock Test Agent",
            f"Candidate: '{profile.name}' | Target Question Count: {question_count} | Role: {profile.target_role}",
            state=state
        )

        log_memory_op(
            "READ",
            f"Checking persistent memory for past weak topics for student '{profile.name}'...",
            state=state
        )
        history = MemoryManager.get_student_history(profile.name)
        past_weak_topics = history.get("previous_weak_topics", [])

        if past_weak_topics:
            log_agent_action(
                "Mock Test Agent",
                f"[MEMORY RECALL] Prior weak topics ({past_weak_topics}) will be given higher representation in test question pool.",
                state=state
            )

        questions = QuestionGeneratorTool.generate_mock_test_questions(
            profile=profile,
            company_research=company_research,
            roadmap=roadmap,
            target_count=question_count,
            state=state
        )

        mock_test = MockTest(
            session_id=session_id,
            total_questions=len(questions),
            questions=questions
        )

        log_agent_end(
            "Mock Test Agent",
            f"Mock test created successfully with {len(questions)} distinct MCQs.",
            start_time,
            state=state
        )

        return mock_test

