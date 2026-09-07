from typing import Dict, Any, List, Optional
import datetime
from backend.models.schemas import (
    StudentInput, ResumeData, StudentProfile, CompanyResearch,
    Roadmap, MockTest, PerformanceReport, AdaptiveAdjustment, AgentEvent
)

class SessionState:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.student_input: Optional[StudentInput] = None
        self.resume_data: Optional[ResumeData] = None
        self.profile: Optional[StudentProfile] = None
        self.company_research: Optional[CompanyResearch] = None
        self.roadmap: Optional[Roadmap] = None
        self.mock_test: Optional[MockTest] = None
        self.performance: Optional[PerformanceReport] = None
        self.adaptive_adjustment: Optional[AdaptiveAdjustment] = None
        self.events: List[AgentEvent] = []

    def add_event(self, agent_name: str, message: str, event_type: str = "LOG", status: str = "INFO") -> AgentEvent:
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        event = AgentEvent(
            timestamp=now_str,
            agent_name=agent_name,
            event_type=event_type,
            message=message,
            status=status
        )
        self.events.append(event)
        return event

class StateManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id)
        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

state_manager = StateManager()
