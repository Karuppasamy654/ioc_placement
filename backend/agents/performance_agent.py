from typing import Optional, List
from backend.models.schemas import (
    PerformanceReport, AdaptiveAdjustment, MockTest, QuizSubmission, Roadmap, RoadmapDay, RoadmapTask
)
from backend.models.state import SessionState
from backend.tools.performance_analyzer import PerformanceAnalyzerTool
from backend.services.gemini_service import gemini_service
from backend.utils.logger import log_event

class PerformanceAnalysisAgent:
    @staticmethod
    def analyze_performance_and_adapt(
        test: MockTest,
        submission: QuizSubmission,
        current_roadmap: Optional[Roadmap],
        state: SessionState
    ) -> tuple[PerformanceReport, AdaptiveAdjustment]:
        """
        Analyzes actual user test responses, computes exact accuracy, identifies weak topics, and adaptively modifies upcoming schedule.
        """
        log_event("Performance Analysis Agent", "Analyzing submitted test responses...", "STARTED", state)
        log_event("Performance Analyzer Tool", "Executing deterministic scoring and topic-wise accuracy calculation...", "STARTED", state)

        report = PerformanceAnalyzerTool.analyze_submission(test, submission)

        log_event(
            "Performance Analyzer Tool",
            f"Analysis complete: Score = {report.score_percentage}% ({report.correct_count}/{report.total_questions} correct). Identified weak topics: {', '.join(report.weak_topics) or 'None'}.",
            "COMPLETED",
            state
        )

        # Call Gemini for high-level adaptive recommendations based on calculated performance
        log_event("Performance Analysis Agent", "Generating adaptive schedule adjustments based on actual weak topics...", "STARTED", state)

        prompt = f"""
Analyze student test results and suggest adaptive schedule modifications:
- Overall Score: {report.score_percentage}% ({report.correct_count} correct / {report.total_questions} total)
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
        raw_json = gemini_service.generate_json(prompt, system_instruction="You are an adaptive educational AI mentor. Suggest practical, actionable study adjustments based strictly on test results.")

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
                        new_tasks.append(RoadmapTask(
                            topic=f"[REINFORCED] {task.topic}",
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

        log_event(
            "Performance Analysis Agent",
            f"Adaptive learning loop completed. Updated upcoming roadmap to reinforce {len(report.weak_topics)} weak areas.",
            "COMPLETED",
            state
        )

        return report, adjustment
