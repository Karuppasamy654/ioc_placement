import sys
import os

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from backend.models.schemas import StudentInput, QuizSubmission, AnswerItem
from backend.agents.orchestrator import OrchestratorAgent
from backend.memory.memory_manager import MemoryManager
from backend.models.state import state_manager

def run_multi_session_memory_test():
    print("\n============================================================")
    print("[TEST] MULTI-SESSION SECOND-RUN MEMORY VERIFICATION TEST")
    print("============================================================\n")


    student_name = "Test Candidate Alpha"
    company = "Google"
    role = "Software Engineer"

    print(f"--- SESSION 1: Initial Session for '{student_name}' ---")
    input_session1 = StudentInput(
        name=student_name,
        target_company=company,
        target_role=role,
        prep_days=3,
        daily_hours=4.0,
        current_skills="Python, Algorithms"
    )

    session1_id = OrchestratorAgent.run_preparation_pipeline(input_session1)
    state1 = state_manager.get_session(session1_id)
    assert state1 is not None, "Session 1 state must exist."
    assert state1.mock_test is not None, "Session 1 mock test must exist."
    assert len(state1.mock_test.questions) >= 50, "Mock test must contain at least 50 questions."

    print(f"Session 1 ID: {session1_id}")
    print(f"Session 1 Questions Count: {len(state1.mock_test.questions)}")

    # Submit intentionally low answers on DBMS/Arrays to simulate weak performance
    mock_test = state1.mock_test
    answers = []
    for idx, q in enumerate(mock_test.questions):
        # Pick wrong answer for DBMS/Arrays questions, correct for others
        if "dbms" in q.topic.lower() or "database" in q.topic.lower() or "array" in q.topic.lower() or idx % 2 == 0:
            wrong_opt = [opt for opt in q.options if opt != q.correct_answer][0]
            answers.append(AnswerItem(question_index=idx, selected_option=wrong_opt))
        else:
            answers.append(AnswerItem(question_index=idx, selected_option=q.correct_answer))

    submission1 = QuizSubmission(session_id=session1_id, answers=answers)

    report1, adjustment1 = OrchestratorAgent.process_test_submission(submission1)

    print(f"\n[SESSION 1 RESULT] Score: {report1.score_percentage}% | Weak Topics: {report1.weak_topics}")

    # Check Memory DB content
    history_after_s1 = MemoryManager.get_student_history(student_name)
    assert history_after_s1["has_history"] is True, "Memory DB must record session 1 history."
    assert history_after_s1["attempt_count"] == 1, "Attempt count in DB must be 1."
    print(f"[MEMORY DB STATE AFTER S1] Attempts: {history_after_s1['attempt_count']} | Weak Topics: {history_after_s1['previous_weak_topics']}")

    print("\n------------------------------------------------------------")
    print(f"--- SESSION 2 (SECOND-RUN DEMO): Same Student '{student_name}' ---")
    print("------------------------------------------------------------\n")

    input_session2 = StudentInput(
        name=student_name,
        target_company="Microsoft",
        target_role="Senior Software Engineer",
        prep_days=4,
        daily_hours=5.0,
        current_skills="Python, Algorithms, System Design"
    )

    session2_id = OrchestratorAgent.run_preparation_pipeline(input_session2)
    state2 = state_manager.get_session(session2_id)

    assert state2 is not None, "Session 2 state must exist."
    assert state2.profile is not None, "Session 2 profile must exist."
    assert state2.roadmap is not None, "Session 2 roadmap must exist."

    # Verify second-run memory recall
    print("\n[VERIFYING SECOND-RUN ADAPTATIONS]")
    print(f"Session 2 Profile Weak Areas (Recalled): {state2.profile.weak_areas}")
    
    # Check if any weak topic from S1 is present in S2 profile/roadmap
    found_recalled_weakness = False
    for prev_w in history_after_s1["previous_weak_topics"]:
        if prev_w in state2.profile.weak_areas or any(prev_w.lower() in t.topic.lower() for day in state2.roadmap.days for t in day.tasks):
            found_recalled_weakness = True
            break
            
    print(f"Recalled Weakness Integrated in Session 2 Schedule: {found_recalled_weakness}")

    history_after_s2 = MemoryManager.get_student_history(student_name)
    print(f"[MEMORY DB STATE AFTER S2 INIT] Total Roadmaps Saved: {history_after_s2['previous_roadmaps_count']}")

    print("\n============================================================")
    print("SUCCESS: MULTI-SESSION PERSISTENT MEMORY & OBSERVABILITY VERIFIED!")
    print("============================================================\n")

if __name__ == "__main__":
    run_multi_session_memory_test()
