from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class StudentInput(BaseModel):
    name: str = Field(..., description="Student name")
    target_company: str = Field(..., description="Target company")
    target_role: str = Field(..., description="Target job role")
    prep_days: int = Field(..., ge=1, le=90, description="Preparation timeframe in days")
    daily_hours: float = Field(..., ge=1.0, le=16.0, description="Daily available study hours")
    current_skills: str = Field("", description="Comma-separated or free-text current skills")

class ResumeValidationResult(BaseModel):
    is_valid: bool
    name_matched: bool
    character_count: int = 0
    error_message: str = ""

class ResumeScoreData(BaseModel):
    resume_score: float = 0.0 # 0.0 to 100.0
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    formatting_feedback: List[str] = Field(default_factory=list)
    actionable_improvements: List[str] = Field(default_factory=list)

class UserRegisterInput(BaseModel):
    username: str = Field(..., min_length=3, description="Unique username")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=4, description="User password")
    name: str = Field(..., description="Student full name")
    target_company: str = Field(..., description="Target company")
    target_role: str = Field(..., description="Target job role")
    prep_days: int = Field(14, ge=1, le=90)
    daily_hours: float = Field(4.0, ge=1.0, le=16.0)
    current_skills: str = Field("")

class UserLoginInput(BaseModel):
    username: str = Field(..., description="Registered username")
    password: str = Field(..., description="User password")

class UserAccount(BaseModel):
    id: int
    username: str
    email: str
    name: str
    target_company: str
    target_role: str
    prep_days: int
    daily_hours: float
    current_skills: str

class ResumeData(BaseModel):
    education: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    extracted_text: str = ""

class StudentProfile(BaseModel):
    name: str
    target_company: str
    target_role: str
    prep_days: int
    daily_hours: float
    user_skills: List[str]
    resume_data: Optional[ResumeData] = None
    strong_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    relevant_tech_for_role: List[str] = Field(default_factory=list)
    resume_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    ats_resume_score: float = 75.0
    resume_score_details: Optional[ResumeScoreData] = None

class CompanyResearchSource(BaseModel):
    title: str
    source_type: str
    url: str
    category: str = "general" # study, careers, general

class CompanyResearch(BaseModel):
    company_name: str
    role_name: str
    official_info: str = ""
    role_description: str = ""
    key_skills: List[str] = Field(default_factory=list)
    hiring_process: List[str] = Field(default_factory=list)
    research_available: bool = True
    sources: List[CompanyResearchSource] = Field(default_factory=list)
    study_links: List[CompanyResearchSource] = Field(default_factory=list)
    official_careers_url: str = ""
    notes: str = ""


class RoadmapTask(BaseModel):
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    duration_hours: float
    priority: str = "Medium"  # High, Medium, Low
    practice_task: str
    expected_outcome: str

class RoadmapDay(BaseModel):
    day_number: int
    day_title: str
    tasks: List[RoadmapTask] = Field(default_factory=list)
    total_hours: float = 0.0

class Roadmap(BaseModel):
    total_days: int
    daily_hours: float
    days: List[RoadmapDay] = Field(default_factory=list)
    overview: str = ""

class MCQQuestion(BaseModel):
    question: str
    options: List[str]  # Must have exactly 4 options
    correct_answer: str # Exact text of option or option index
    topic: str
    difficulty: str = "medium" # easy, medium, hard
    explanation: str

class MockTest(BaseModel):
    session_id: str
    total_questions: int
    questions: List[MCQQuestion]

class AnswerItem(BaseModel):
    question_index: int
    selected_option: str

class QuizSubmission(BaseModel):
    session_id: str
    answers: List[AnswerItem]

class UserAnswerDetail(BaseModel):
    question_index: int
    question_text: str
    selected_option: str
    correct_answer: str
    is_correct: bool
    topic: str
    difficulty: str
    explanation: str

class PerformanceReport(BaseModel):
    session_id: str
    total_questions: int
    answered_questions: int
    correct_count: int
    incorrect_count: int
    score_percentage: float
    topic_accuracy: Dict[str, float] = Field(default_factory=dict)
    difficulty_accuracy: Dict[str, float] = Field(default_factory=dict)
    strong_topics: List[str] = Field(default_factory=list)
    weak_topics: List[str] = Field(default_factory=list)
    detailed_answers: List[UserAnswerDetail] = Field(default_factory=list)

class AdaptiveAdjustment(BaseModel):
    weak_topics_addressed: List[str] = Field(default_factory=list)
    concepts_to_revise: List[str] = Field(default_factory=list)
    recommended_practice: List[str] = Field(default_factory=list)
    next_day_schedule_changes: List[str] = Field(default_factory=list)
    updated_roadmap_days: List[RoadmapDay] = Field(default_factory=list)

class AgentEvent(BaseModel):
    timestamp: str
    agent_name: str
    event_type: str
    message: str
    status: str = "INFO"  # STARTED, COMPLETED, FAILED, INFO
