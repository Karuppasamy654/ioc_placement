import sys
import os

# Ensure backend modules can be imported relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.models.schemas import StudentInput, QuizSubmission, AnswerItem
from backend.agents.orchestrator import OrchestratorAgent
from backend.models.state import state_manager

def test_full_agent_pipeline():
    print("====================================================")
    print("       STARTING AGENTIC AI PIPELINE TEST")
    print("====================================================\n")

    student_input = StudentInput(
        name="Test Student",
        target_company="Google",
        target_role="Full Stack Engineer",
        prep_days=5,
        daily_hours=4.0,
        current_skills="Python, JavaScript, Data Structures, SQL"
    )

    # 1. Run preparation pipeline
    print("--- 1. Testing Preparation Pipeline ---")
    session_id = OrchestratorAgent.run_preparation_pipeline(student_input, resume_path=None)
    print(f"[OK] Preparation pipeline completed! Session ID: {session_id}")

    state = state_manager.get_session(session_id)
    assert state is not None, "SessionState should exist."
    assert state.profile is not None, "StudentProfile should be generated."
    assert state.company_research is not None, "CompanyResearch should be generated."
    assert state.roadmap is not None, "Roadmap should be generated."
    assert state.mock_test is not None, "MockTest should be generated."

    print(f"\n[OK] Profile Gaps: {state.profile.resume_gaps[:2]}")
    print(f"[OK] Research Sources Count: {len(state.company_research.sources)}")
    print(f"[OK] Roadmap Days: {len(state.roadmap.days)} days")
    print(f"[OK] Questions Generated: {state.mock_test.total_questions} questions")

    assert 50 <= state.mock_test.total_questions <= 60, f"Expected 50-60 questions, got {state.mock_test.total_questions}"

    first_q = state.mock_test.questions[0]
    print(f"\n--- Sample Generated Question 1 ---")
    print(f"Q: {first_q.question}")
    print(f"Options: {first_q.options}")
    print(f"Correct Answer: {first_q.correct_answer}")
    print(f"Topic: {first_q.topic} | Difficulty: {first_q.difficulty}")

    assert len(first_q.options) == 4, "Every question must have 4 options."

    # 2. Test Test Submission & Adaptive Performance Analysis
    print("\n--- 2. Testing Test Submission & Adaptive Learning ---")
    mock_answers = []
    for idx, q in enumerate(state.mock_test.questions):
        selected = q.correct_answer if idx % 2 == 0 else q.options[(q.options.index(q.correct_answer) + 1) % 4]
        mock_answers.append(AnswerItem(question_index=idx, selected_option=selected))

    submission = QuizSubmission(session_id=session_id, answers=mock_answers)
    report, adjustment = OrchestratorAgent.process_test_submission(submission)

    print(f"[OK] Quiz Evaluation Complete!")
    print(f"Score: {report.score_percentage}% ({report.correct_count}/{report.total_questions} correct)")
    print(f"Identified Weak Topics: {report.weak_topics}")
    print(f"Next-Day Schedule Changes: {adjustment.next_day_schedule_changes}")

    print("\n====================================================")
    print("       ALL PIPELINE CHECKS PASSED SUCCESSFULLY!")
    print("====================================================")

if __name__ == "__main__":
    test_full_agent_pipeline()
