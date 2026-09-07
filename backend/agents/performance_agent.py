from typing import Optional, List
from backend.models.schemas import (
    PerformanceReport, AdaptiveAdjustment, MockTest, QuizSubmission, Roadmap, RoadmapDay, RoadmapTask
)
from backend.models.state import SessionState
from backend.tools.performance_analyzer import PerformanceAnalyzerTool
from backend.services.gemini_service import gemini_service
from backend.memory.memory_manager import MemoryManager
from backend.utils.logger import log_agent_start, log_agent_action, log_agent_end, log_memory_op

class PerformanceAnalysisAgent:
    @staticmethod
    def analyze_performance_and_adapt(
        test: MockTest,
        submission: QuizSubmission,
        current_roadmap: Optional[Roadmap],
        state: SessionState
    ) -> tuple[PerformanceReport, AdaptiveAdjustment]:
        """
        Analyzes actual user test responses, computes exact accuracy, identifies weak topics,
        saves score & adaptive adjustments to persistent memory, and adaptively modifies upcoming schedule.
        """
        student_name = state.student_input.name if state.student_input and state.student_input.name else "Student"
        
        start_time = log_agent_start(
            "Performance Analysis Agent",
            f"Candidate: '{student_name}' | Session ID: {submission.session_id} | Answers Submitted: {len(submission.answers)}",
            state=state
        )

        # 1. Deterministic Scoring via Tool
        report = PerformanceAnalyzerTool.analyze_submission(test, submission, state=state)

        # 2. Memory Recall & Progress Trend Analysis
        log_memory_op(
            "READ",
            f"Checking prior test attempt history for candidate '{student_name}' in SQLite DB...",
            state=state
        )
        history = MemoryManager.get_student_history(student_name)
        
        trend_msg = ""
        if history["has_history"] and history["attempt_count"] > 0:
            last_score = history["last_score"]
            diff = round(report.score_percentage - (last_score or 0.0), 1)
            sign = "+" if diff >= 0 else ""
            trend_msg = f"Previous Attempt Score: {last_score}% -> Current Score: {report.score_percentage}% ({sign}{diff}% change)"
            log_agent_action("Performance Analysis Agent", f"[PROGRESS TREND] {trend_msg}", state=state)
        else:
            trend_msg = f"First attempt recorded for '{student_name}'. Initial Score: {report.score_percentage}%"
            log_agent_action("Performance Analysis Agent", f"[PROGRESS INITIAL] {trend_msg}", state=state)

        # 3. Save Mock Test Attempt to SQLite Memory DB
        MemoryManager.save_mock_attempt(submission.session_id, student_name, report)
        log_memory_op(
            "WRITE",
            f"Saved mock test attempt for '{student_name}' to SQLite DB.",
            f"Score: {report.score_percentage}% | Correct: {report.correct_count}/{report.total_questions} | Weak Topics: {report.weak_topics}",
            state=state
        )

        # 4. Generate Adaptive Schedule Adjustments via Gemini
        log_agent_action("Performance Analysis Agent", "Generating adaptive schedule adjustments based on actual weak topics...", state=state)

        prompt = f"""
Analyze student test results and suggest adaptive schedule modifications:
- Candidate Name: {student_name}
- Current Score: {report.score_percentage}% ({report.correct_count} correct / {report.total_questions} total)
- Historical Performance Context: {trend_msg}
- Topic-wise Accuracy: {report.topic_accuracy}
- Difficulty Accuracy: {report.difficulty_accuracy}
- Identified Strong Topics: {', '.join(report.strong_topics)}
- Identified Weak Topics: {', '.join(report.weak_topics)}

Task:
1. Provide specific concepts to revise immediately.
2. Recommend targeted practice exercises.
3. Suggest explicit next-day preparation schedule changes to increase focus on weak areas.

Return JSON format:
{{
  "concepts_to_revise": ["..."],
  "recommended_practice": ["..."],
  "next_day_schedule_changes": ["..."]
}}
"""
        raw_json = gemini_service.generate_json(
            prompt,
            system_instruction="You are an adaptive educational AI mentor. Suggest practical, actionable study adjustments based strictly on test results.",
            purpose=f"Adaptive Performance Remediation for {student_name}",
            state=state
        )

        concepts = []
        practice = []
        schedule_changes = []

        if raw_json and isinstance(raw_json, dict):
            concepts = raw_json.get("concepts_to_revise", [])
            practice = raw_json.get("recommended_practice", [])
            schedule_changes = raw_json.get("next_day_schedule_changes", [])

        if not concepts:
            concepts = [f"Re-study core fundamentals of {t}" for t in report.weak_topics] or ["Review incorrect answers"]
        if not practice:
            practice = [f"Solve 10 targeted practice questions on {t}" for t in report.weak_topics] or ["Complete additional practice quiz"]
        if not schedule_changes:
            schedule_changes = [f"Shift Day 2 morning schedule to double time spent on {t}" for t in report.weak_topics] or ["Increase daily review time"]

        # Adaptively update upcoming roadmap days
        updated_days: List[RoadmapDay] = []
        if current_roadmap and current_roadmap.days:
            for day in current_roadmap.days:
                new_tasks = []
                for task in day.tasks:
                    # If task topic is in weak topics, bump priority to High and expand duration
                    if any(wt.lower() in task.topic.lower() or task.topic.lower() in wt.lower() for wt in report.weak_topics):
                        new_topic = task.topic if task.topic.startswith("[REINFORCED]") else f"[REINFORCED] {task.topic}"
                        new_tasks.append(RoadmapTask(
                            topic=new_topic,
                            subtopics=task.subtopics + ["Targeted Weakness Remediation"],
                            duration_hours=round(task.duration_hours * 1.3, 1),
                            priority="High",
                            practice_task=f"EXTRA PRACTICE: {task.practice_task}",
                            expected_outcome=f"Achieve >80% accuracy in {task.topic}"
                        ))
                    else:
                        new_tasks.append(task)
                
                updated_days.append(RoadmapDay(
                    day_number=day.day_number,
                    day_title=day.day_title,
                    tasks=new_tasks,
                    total_hours=round(sum(t.duration_hours for t in new_tasks), 1)
                ))

        adjustment = AdaptiveAdjustment(
            weak_topics_addressed=report.weak_topics,
            concepts_to_revise=concepts,
            recommended_practice=practice,
            next_day_schedule_changes=schedule_changes,
            updated_roadmap_days=updated_days
        )

        # 5. Save Adaptive Adjustment to SQLite Memory DB
        MemoryManager.save_adaptive_adjustment(submission.session_id, student_name, adjustment)
        log_memory_op(
            "WRITE",
            f"Saved adaptive adjustment record for '{student_name}' to SQLite DB.",
            f"Weak Topics Addressed: {adjustment.weak_topics_addressed} | Next Day Changes: {len(adjustment.next_day_schedule_changes)}",
            state=state
        )

        log_agent_end(
            "Performance Analysis Agent",
            f"Adaptive learning loop completed. Score: {report.score_percentage}%. Roadmap updated to reinforce {len(report.weak_topics)} weak areas.",
            start_time,
            state=state
        )

        return report, adjustment

