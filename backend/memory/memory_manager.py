import json
import sqlite3
from typing import Dict, Any, List, Optional
from backend.memory.db import get_db_connection
from backend.models.schemas import StudentProfile, ResumeData, Roadmap, PerformanceReport, AdaptiveAdjustment

class MemoryManager:
    @staticmethod
    def get_student_history(name: str) -> Dict[str, Any]:
        """
        Loads all previous student history from SQLite DB for second-run adaptive learning.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch Profile
        cursor.execute("SELECT * FROM student_profiles WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        profile_row = cursor.fetchone()

        # 2. Fetch Attempts
        cursor.execute("SELECT * FROM mock_attempts WHERE LOWER(student_name) = LOWER(?) ORDER BY created_at ASC", (name.strip(),))
        attempt_rows = cursor.fetchall()

        # 3. Fetch Roadmaps
        cursor.execute("SELECT * FROM roadmaps WHERE LOWER(student_name) = LOWER(?) ORDER BY created_at ASC", (name.strip(),))
        roadmap_rows = cursor.fetchall()

        conn.close()

        if not profile_row and not attempt_rows and not roadmap_rows:
            return {
                "has_history": False,
                "attempt_count": 0,
                "previous_weak_topics": [],
                "previous_strong_topics": [],
                "repeated_weaknesses": [],
                "last_score": None,
                "average_score": None,
                "previous_roadmaps_count": 0,
                "previous_target_company": None,
                "previous_target_role": None,
                "attempts_summary": []
            }

        # Analyze historical weak topics across attempts
        topic_weak_counts: Dict[str, int] = {}
        all_weak_topics: List[str] = []
        all_strong_topics: List[str] = []
        scores: List[float] = []
        attempts_summary = []

        for row in attempt_rows:
            s_val = float(row["score_percentage"]) if row["score_percentage"] is not None else 0.0
            scores.append(s_val)

            w_list = json.loads(row["weak_topics_json"]) if row["weak_topics_json"] else []
            st_list = json.loads(row["strong_topics_json"]) if row["strong_topics_json"] else []

            for wt in w_list:
                topic_weak_counts[wt] = topic_weak_counts.get(wt, 0) + 1
                if wt not in all_weak_topics:
                    all_weak_topics.append(wt)

            for st in st_list:
                if st not in all_strong_topics:
                    all_strong_topics.append(st)

            attempts_summary.append({
                "session_id": row["session_id"],
                "score_percentage": s_val,
                "correct_count": row["correct_count"],
                "total_questions": row["total_questions"],
                "weak_topics": w_list,
                "date": row["created_at"]
            })

        # Identify topics weak in >1 session (repeated mistakes)
        repeated_weaknesses = [t for t, count in topic_weak_counts.items() if count >= 2 or (len(attempt_rows) == 1 and count >= 1)]

        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        return {
            "has_history": True,
            "attempt_count": len(attempt_rows),
            "previous_weak_topics": all_weak_topics,
            "previous_strong_topics": all_strong_topics,
            "repeated_weaknesses": repeated_weaknesses,
            "last_score": scores[-1] if scores else None,
            "average_score": avg_score,
            "previous_roadmaps_count": len(roadmap_rows),
            "previous_target_company": profile_row["target_company"] if profile_row else None,
            "previous_target_role": profile_row["target_role"] if profile_row else None,
            "attempts_summary": attempts_summary
        }

    @staticmethod
    def save_student_profile(profile: StudentProfile):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO student_profiles (
            name, target_company, target_role, prep_days, daily_hours,
            user_skills, strong_areas, weak_areas, resume_gaps, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(name) DO UPDATE SET
            target_company=excluded.target_company,
            target_role=excluded.target_role,
            prep_days=excluded.prep_days,
            daily_hours=excluded.daily_hours,
            user_skills=excluded.user_skills,
            strong_areas=excluded.strong_areas,
            weak_areas=excluded.weak_areas,
            resume_gaps=excluded.resume_gaps,
            updated_at=CURRENT_TIMESTAMP;
        """, (
            profile.name.strip(),
            profile.target_company,
            profile.target_role,
            profile.prep_days,
            profile.daily_hours,
            json.dumps(profile.user_skills),
            json.dumps(profile.strong_areas),
            json.dumps(profile.weak_areas),
            json.dumps(profile.resume_gaps)
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def save_resume_analysis(student_name: str, file_name: str, resume_data: ResumeData):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO resume_analyses (
            student_name, file_name, technical_skills, projects, education
        ) VALUES (?, ?, ?, ?, ?);
        """, (
            student_name.strip(),
            file_name,
            json.dumps(resume_data.technical_skills),
            json.dumps(resume_data.projects),
            json.dumps(resume_data.education)
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def save_roadmap(session_id: str, student_name: str, roadmap: Roadmap):
        conn = get_db_connection()
        cursor = conn.cursor()

        days_dict_list = [d.model_dump() for d in roadmap.days]

        cursor.execute("""
        INSERT INTO roadmaps (
            session_id, student_name, total_days, daily_hours, overview, days_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            days_json=excluded.days_json,
            overview=excluded.overview;
        """, (
            session_id,
            student_name.strip(),
            roadmap.total_days,
            roadmap.daily_hours,
            roadmap.overview,
            json.dumps(days_dict_list)
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def save_mock_attempt(session_id: str, student_name: str, report: PerformanceReport):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO mock_attempts (
            session_id, student_name, total_questions, answered_questions,
            correct_count, incorrect_count, score_percentage,
            topic_accuracy_json, difficulty_accuracy_json,
            strong_topics_json, weak_topics_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            session_id,
            student_name.strip(),
            report.total_questions,
            report.answered_questions,
            report.correct_count,
            report.incorrect_count,
            report.score_percentage,
            json.dumps(report.topic_accuracy),
            json.dumps(report.difficulty_accuracy),
            json.dumps(report.strong_topics),
            json.dumps(report.weak_topics)
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def save_adaptive_adjustment(session_id: str, student_name: str, adjustment: AdaptiveAdjustment):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO adaptive_adjustments (
            session_id, student_name, weak_topics_addressed_json,
            concepts_to_revise_json, schedule_changes_json
        ) VALUES (?, ?, ?, ?, ?);
        """, (
            session_id,
            student_name.strip(),
            json.dumps(adjustment.weak_topics_addressed),
            json.dumps(adjustment.concepts_to_revise),
            json.dumps(adjustment.next_day_schedule_changes)
        ))

        conn.commit()
        conn.close()

memory_manager = MemoryManager()
