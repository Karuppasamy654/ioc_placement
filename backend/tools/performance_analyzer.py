from typing import List, Dict
from backend.models.schemas import MockTest, QuizSubmission, PerformanceReport, UserAnswerDetail

class PerformanceAnalyzerTool:
    @staticmethod
    def analyze_submission(test: MockTest, submission: QuizSubmission) -> PerformanceReport:
        """
        Calculates exact deterministic test statistics, topic accuracy, and difficulty metrics.
        """
        total_questions = len(test.questions)
        submission_map = {ans.question_index: ans.selected_option.strip() for ans in submission.answers}
        
        correct_count = 0
        incorrect_count = 0
        answered_count = len(submission_map)

        topic_totals: Dict[str, int] = {}
        topic_corrects: Dict[str, int] = {}

        diff_totals: Dict[str, int] = {}
        diff_corrects: Dict[str, int] = {}

        detailed_answers: List[UserAnswerDetail] = []

        for idx, q in enumerate(test.questions):
            user_selected = submission_map.get(idx, "No Answer")
            correct_opt = q.correct_answer.strip()
            
            # Check correctness: exact match or option index match
            is_corr = False
            if user_selected != "No Answer":
                if user_selected == correct_opt:
                    is_corr = True
                elif user_selected in q.options and correct_opt in q.options:
                    if q.options.index(user_selected) == q.options.index(correct_opt):
                        is_corr = True
            
            if is_corr:
                correct_count += 1
            elif user_selected != "No Answer":
                incorrect_count += 1

            # Topic tracking
            topic = q.topic or "General"
            topic_totals[topic] = topic_totals.get(topic, 0) + 1
            if is_corr:
                topic_corrects[topic] = topic_corrects.get(topic, 0) + 1

            # Difficulty tracking
            diff = q.difficulty.lower() if q.difficulty else "medium"
            diff_totals[diff] = diff_totals.get(diff, 0) + 1
            if is_corr:
                diff_corrects[diff] = diff_corrects.get(diff, 0) + 1

            detailed_answers.append(UserAnswerDetail(
                question_index=idx,
                question_text=q.question,
                selected_option=user_selected,
                correct_answer=correct_opt,
                is_correct=is_corr,
                topic=topic,
                difficulty=diff,
                explanation=q.explanation
            ))

        score_percentage = round((correct_count / total_questions) * 100.0, 1) if total_questions > 0 else 0.0

        # Topic accuracy calculation
        topic_accuracy: Dict[str, float] = {}
        strong_topics: List[str] = []
        weak_topics: List[str] = []

        for top, tot in topic_totals.items():
            corr = topic_corrects.get(top, 0)
            acc = round((corr / tot) * 100.0, 1)
            topic_accuracy[top] = acc
            if acc >= 70.0:
                strong_topics.append(top)
            elif acc <= 50.0:
                weak_topics.append(top)

        # If weak topics empty but overall score < 80%, pick lowest scoring topics
        if not weak_topics and topic_accuracy:
            sorted_topics = sorted(topic_accuracy.items(), key=lambda x: x[1])
            if sorted_topics[0][1] < 100.0:
                weak_topics.append(sorted_topics[0][0])

        # Difficulty accuracy calculation
        difficulty_accuracy: Dict[str, float] = {}
        for d_key, tot in diff_totals.items():
            corr = diff_corrects.get(d_key, 0)
            difficulty_accuracy[d_key] = round((corr / tot) * 100.0, 1)

        return PerformanceReport(
            session_id=submission.session_id,
            total_questions=total_questions,
            answered_questions=answered_count,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            score_percentage=score_percentage,
            topic_accuracy=topic_accuracy,
            difficulty_accuracy=difficulty_accuracy,
            strong_topics=strong_topics,
            weak_topics=weak_topics,
            detailed_answers=detailed_answers
        )
