import os
import tempfile
import pytest
from backend.tools.company_research import CompanyResearchTool, _RESEARCH_CACHE
from backend.tools.resume_parser import ResumeParserTool
from backend.tools.question_generator import QuestionGeneratorTool
from backend.tools.performance_analyzer import PerformanceAnalyzerTool
from backend.models.schemas import StudentProfile, MockTest, QuizSubmission, AnswerItem

def test_company_research_cache():
    # 1. Initial lookup populates cache
    res1 = CompanyResearchTool.research_company_and_role("TestCompany", "Software Engineer")
    assert res1.company_name == "TestCompany"

    cache_key = "testcompany::software engineer"
    assert cache_key in _RESEARCH_CACHE

    # 2. Subsequent lookup triggers cache hit
    res2 = CompanyResearchTool.research_company_and_role("TestCompany", "Software Engineer")
    assert res2 is res1  # Exact object reference returned from cache

def test_resume_validation_edge_cases():
    # Invalid non-existent file
    val_none = ResumeParserTool.validate_resume("non_existent_file.pdf", "John Doe")
    assert not val_none.is_valid
    assert "not uploaded" in val_none.error_message.lower()

    # Invalid extension with existing file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_txt:
        tmp_txt.write(b"sample text")
        tmp_txt_path = tmp_txt.name

    try:
        val_ext = ResumeParserTool.validate_resume(tmp_txt_path, "John Doe")
        assert not val_ext.is_valid
        assert "invalid file format" in val_ext.error_message.lower()
    finally:
        if os.path.exists(tmp_txt_path):
            os.remove(tmp_txt_path)


    # Empty text file fallback
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"%PDF-1.4 empty pdf stream")
        tmp_path = tmp.name

    try:
        val_empty = ResumeParserTool.validate_resume(tmp_path, "John Doe")
        assert not val_empty.is_valid
        assert "unreadable or empty" in val_empty.error_message.lower()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_performance_analyzer_math():
    # Construct mock test with 4 questions
    mock_test = MockTest(
        session_id="test_math_session",
        total_questions=4,
        questions=[
            {
                "question": "Q1?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "topic": "DSA",
                "difficulty": "easy",
                "explanation": "Exp 1"
            },
            {
                "question": "Q2?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "topic": "DSA",
                "difficulty": "medium",
                "explanation": "Exp 2"
            },
            {
                "question": "Q3?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "C",
                "topic": "System Design",
                "difficulty": "hard",
                "explanation": "Exp 3"
            },
            {
                "question": "Q4?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "D",
                "topic": "System Design",
                "difficulty": "hard",
                "explanation": "Exp 4"
            }
        ]
    )

    submission = QuizSubmission(
        session_id="test_math_session",
        answers=[
            AnswerItem(question_index=0, selected_option="A"),  # Correct
            AnswerItem(question_index=1, selected_option="B"),  # Correct
            AnswerItem(question_index=2, selected_option="X"),  # Wrong
            AnswerItem(question_index=3, selected_option="X")   # Wrong
        ]
    )



    report = PerformanceAnalyzerTool.analyze_submission(mock_test, submission)

    assert report.total_questions == 4
    assert report.correct_count == 2
    assert report.score_percentage == 50.0
    assert "DSA" in report.strong_topics
    assert "System Design" in report.weak_topics
