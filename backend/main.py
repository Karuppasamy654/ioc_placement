import os
import uuid
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

from backend.models.schemas import StudentInput, QuizSubmission, UserRegisterInput, UserLoginInput
from backend.models.state import state_manager
from backend.agents.orchestrator import OrchestratorAgent
from backend.memory.memory_manager import MemoryManager
from backend.tools.resume_parser import ResumeParserTool
from backend.utils.ics_exporter import ICSExporter
from backend.utils.logger import log_event

app = FastAPI(
    title="AI Placement Agent API",
    description="Adaptive placement preparation & dynamic mock test system powered by multi-agent AI.",
    version="1.0.0"
)

# Enable CORS for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join(tempfile.gettempdir(), "placement_agent_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

# Static Frontend Serving (Serves full React UI directly on http://localhost:8000)
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "AI Placement Agent API is running"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Placement Agent API",
        "version": "1.0.0"
    }

@app.post("/api/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    target_company: str = Form(...),
    target_role: str = Form(...),
    prep_days: int = Form(14),
    daily_hours: float = Form(4.0),
    current_skills: str = Form(""),
    resume: Optional[UploadFile] = File(None)
):
    try:
        # Check if username already exists
        existing = MemoryManager.get_user_by_username(username)
        if existing:
            raise HTTPException(status_code=400, detail=f"Username '{username}' is already registered. Please login instead.")

        saved_resume_path = None
        if resume and resume.filename:
            ext = os.path.splitext(resume.filename)[1].lower()
            if ext not in [".pdf", ".docx", ".doc"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid PDF (.pdf) or Word (.docx) resume.")

            saved_resume_path = os.path.join(TEMP_DIR, f"resume_reg_{username}{ext}")
            with open(saved_resume_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            # Strict Resume Validation (Format, readability, candidate name match)
            val_res = ResumeParserTool.validate_resume(saved_resume_path, name)
            if not val_res.is_valid or not val_res.name_matched:
                raise HTTPException(status_code=400, detail=val_res.error_message)

        reg_input = UserRegisterInput(
            username=username,
            email=email,
            password=password,
            name=name,
            target_company=target_company,
            target_role=target_role,
            prep_days=prep_days,
            daily_hours=daily_hours,
            current_skills=current_skills
        )

        user_acc = MemoryManager.create_user(reg_input)

        # Trigger initial pipeline generation for user
        session_id = str(uuid.uuid4())
        student_input = StudentInput(
            name=name,
            target_company=target_company,
            target_role=target_role,
            prep_days=prep_days,
            daily_hours=daily_hours,
            current_skills=current_skills
        )

        OrchestratorAgent.run_preparation_pipeline_with_session(session_id, student_input, saved_resume_path)

        return {
            "status": "success",
            "message": "User account created successfully.",
            "user": user_acc,
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] /api/register error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
def login_user(login_data: UserLoginInput):
    user_acc = MemoryManager.authenticate_user(login_data.username, login_data.password)
    if not user_acc:
        raise HTTPException(status_code=401, detail="Invalid username or password. Please check your credentials.")

    # Retrieve existing user session history or profile
    history = MemoryManager.get_student_history(user_acc.name)
    
    return {
        "status": "success",
        "user": user_acc,
        "history": history
    }

@app.post("/api/prepare")
async def prepare_placement(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    target_company: str = Form(...),
    target_role: str = Form(...),
    prep_days: int = Form(...),
    daily_hours: float = Form(...),
    current_skills: str = Form(""),
    resume: Optional[UploadFile] = File(None)
):
    try:
        student_input = StudentInput(
            name=name,
            target_company=target_company,
            target_role=target_role,
            prep_days=prep_days,
            daily_hours=daily_hours,
            current_skills=current_skills
        )

        saved_resume_path = None
        if resume and resume.filename:
            ext = os.path.splitext(resume.filename)[1].lower()
            if ext not in [".pdf", ".docx", ".doc"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid PDF (.pdf) or Word (.docx) resume.")

            saved_resume_path = os.path.join(TEMP_DIR, f"resume_{name.replace(' ', '_')}{ext}")
            with open(saved_resume_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            # Strict Resume Validation (Format, text length, candidate name match)
            val_res = ResumeParserTool.validate_resume(saved_resume_path, name)
            if not val_res.is_valid or not val_res.name_matched:
                raise HTTPException(status_code=400, detail=val_res.error_message)

        session_id = str(uuid.uuid4())
        
        # Pre-register session state & log immediate startup event
        state = state_manager.get_or_create_session(session_id)
        state.student_input = student_input
        log_event("Orchestrator", f"Workflow initialized for student '{student_input.name}' (Target: {student_input.target_role} @ {student_input.target_company})", "STARTED", state)

        # Start multi-agent workflow in background task
        background_tasks.add_task(
            OrchestratorAgent.run_preparation_pipeline_with_session,
            session_id,
            student_input,
            saved_resume_path
        )

        return {
            "status": "success",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] /api/prepare error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export-calendar-ics")
def export_calendar_ics(session_id: str = Query(...)):
    state = state_manager.get_session(session_id)
    if not state or not state.roadmap:
        raise HTTPException(status_code=404, detail="Active study roadmap not found for calendar export.")

    cand_name = state.student_input.name if state.student_input else "Student"
    ics_content = ICSExporter.generate_ics_content(state.roadmap, candidate_name=cand_name)

    ics_filename = f"placement_prep_{cand_name.replace(' ', '_')}.ics"
    temp_path = os.path.join(TEMP_DIR, ics_filename)
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(ics_content)

    return FileResponse(
        temp_path,
        media_type="text/calendar",
        filename=ics_filename
    )

@app.get("/api/session-status")
def get_session_status(session_id: str = Query(...)):
    state = state_manager.get_session(session_id)
    if not state:
        return {"status": "processing", "is_complete": False}
    
    is_complete = bool(state.roadmap and state.profile and state.mock_test)
    return {
        "status": "completed" if is_complete else "processing",
        "is_complete": is_complete,
        "profile": state.profile,
        "company_research": state.company_research,
        "roadmap": state.roadmap,
        "mock_test_ready": bool(state.mock_test and state.mock_test.questions)
    }

@app.get("/api/mock-test")
def get_mock_test(session_id: str = Query(...)):
    state = state_manager.get_session(session_id)
    if not state or not state.mock_test:
        raise HTTPException(status_code=404, detail="Mock test not found for this session ID.")
    
    return {
        "status": "success",
        "mock_test": state.mock_test
    }

@app.post("/api/submit-test")
def submit_test(submission: QuizSubmission):
    try:
        report, adjustment = OrchestratorAgent.process_test_submission(submission)
        return {
            "status": "success",
            "performance": report,
            "adaptive_adjustment": adjustment
        }
    except Exception as e:
        print(f"[API ERROR] /api/submit-test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent-events")
def get_agent_events(session_id: str = Query(...)):
    state = state_manager.get_session(session_id)
    if not state:
        return {"status": "success", "events": []}
    
    return {
        "status": "success",
        "events": [event.model_dump() for event in state.events]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

