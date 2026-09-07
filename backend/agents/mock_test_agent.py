from typing import Optional
from backend.models.schemas import MockTest, StudentProfile, CompanyResearch, Roadmap
from backend.models.state import SessionState
from backend.tools.question_generator import QuestionGeneratorTool
from backend.utils.logger import log_event

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
        Coordinates the dynamic generation of 50-60 placement MCQs tailored to the student.
        """
        log_event("Mock Test Agent", f"Initializing dynamic quiz generation (Target: {question_count} questions)...", "STARTED", state)
        log_event("Question Generation Tool", f"Querying Gemini API to produce tailored questions for {profile.target_role}...", "STARTED", state)

        questions = QuestionGeneratorTool.generate_mock_test_questions(
            profile=profile,
            company_research=company_research,
            roadmap=roadmap,
            target_count=question_count
        )

        mock_test = MockTest(
            session_id=session_id,
            total_questions=len(questions),
            questions=questions
        )

        log_event("Question Generation Tool", f"Generated and validated {len(questions)} distinct MCQs.", "COMPLETED", state)
        log_event("Mock Test Agent", f"Mock test created successfully with {len(questions)} questions.", "COMPLETED", state)

        return mock_test
