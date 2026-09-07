import sys
import os
import shutil
import tempfile
import uuid
import fitz  # PyMuPDF
from fastapi.testclient import TestClient

# Ensure backend modules can be imported relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app
from backend.tools.resume_parser import ResumeParserTool
from backend.memory.memory_manager import MemoryManager
from backend.utils.ics_exporter import ICSExporter
from backend.models.schemas import UserRegisterInput, Roadmap, RoadmapDay, RoadmapTask

client = TestClient(app)

def create_sample_pdf(file_path: str, candidate_name: str, content_text: str):
    """Utility helper to dynamically create a valid PDF file with sample resume text."""
    doc = fitz.open()
    page = doc.new_page()
    text = f"RESUME OF {candidate_name.upper()}\n\n"
    text += f"Email: {candidate_name.lower().replace(' ', '.')}@example.com | Phone: +1-555-0199\n\n"
    text += "SUMMARY:\n"
    text += content_text + "\n"
    text += "SKILLS:\nPython, React, FastApi, SQL, Docker, Data Structures, Algorithms\n"
    text += "EXPERIENCE:\nSoftware Engineer at TechCorp (2022 - Present)\n"
    text += "- Developed scalable microservices using Python and FastAPI.\n"
    text += "- Built real-time dashboard UI using React.js.\n"
    
    page.insert_text((50, 50), text, fontsize=11)
    doc.save(file_path)
    doc.close()

def test_resume_validation_and_auth():
    print("====================================================")
    print("  TESTING RESUME VALIDATION, AUTH & ICS EXPORTER")
    print("====================================================\n")

    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Test Resume Validation - Invalid File Extension
        print("--- 1. Testing Invalid Resume File Extension ---")
        invalid_txt_path = os.path.join(temp_dir, "resume.txt")
        with open(invalid_txt_path, "w") as f:
            f.write("Some text format")
        
        val_res1 = ResumeParserTool.validate_resume(invalid_txt_path, "John Doe")
        assert not val_res1.is_valid
        assert "Invalid file format" in val_res1.error_message
        print(f"[OK] Invalid extension caught correctly: {val_res1.error_message}")

        # 2. Test Resume Validation - Short/Unreadable Text (<100 chars)
        print("\n--- 2. Testing Short/Unreadable Resume Text (<100 chars) ---")
        short_pdf_path = os.path.join(temp_dir, "short_resume.pdf")
        doc = fitz.open()
        p = doc.new_page()
        p.insert_text((50, 50), "John Doe Resume short", fontsize=11)
        doc.save(short_pdf_path)
        doc.close()

        val_res2 = ResumeParserTool.validate_resume(short_pdf_path, "John Doe")
        assert not val_res2.is_valid
        assert "less than 100 characters" in val_res2.error_message
        print(f"[OK] Short resume caught correctly: {val_res2.error_message}")

        # 3. Test Resume Validation - Candidate Name Mismatch
        print("\n--- 3. Testing Candidate Name Mismatch ---")
        pdf_alice_path = os.path.join(temp_dir, "alice_resume.pdf")
        long_body = "Professional Software Developer with extensive hands-on experience in backend architectures, cloud computing, continuous integration, and modern database management systems."
        create_sample_pdf(pdf_alice_path, "Alice Smith", long_body)

        val_res3 = ResumeParserTool.validate_resume(pdf_alice_path, "Bob Williams")
        assert val_res3.is_valid  # Format & length are valid
        assert not val_res3.name_matched
        assert "was not found anywhere in the uploaded resume" in val_res3.error_message
        print(f"[OK] Name mismatch caught correctly: {val_res3.error_message}")

        # 4. Test Resume Validation - Successful Name Match
        print("\n--- 4. Testing Successful Resume Validation & Name Match ---")
        val_res4 = ResumeParserTool.validate_resume(pdf_alice_path, "Alice Smith")
        assert val_res4.is_valid
        assert val_res4.name_matched
        assert not val_res4.error_message
        print(f"[OK] Resume valid and candidate name matched successfully!")

        # 5. Test API Registration Endpoint with Resume Validation
        print("\n--- 5. Testing API Registration Endpoint (/api/register) ---")
        reg_username = f"alice_user_{uuid.uuid4().hex[:6]}"
        
        with open(pdf_alice_path, "rb") as f:
            response = client.post(
                "/api/register",
                data={
                    "username": reg_username,
                    "email": f"alice_{reg_username}@example.com",
                    "password": "SecurePassword123!",
                    "name": "Alice Smith",
                    "target_company": "Google",
                    "target_role": "Backend Engineer",
                    "prep_days": 7,
                    "daily_hours": 3.0,
                    "current_skills": "Python, SQL, Algorithms"
                },
                files={"resume": ("alice_resume.pdf", f, "application/pdf")}
            )

        assert response.status_code == 200, f"Registration failed: {response.text}"
        res_json = response.json()
        assert res_json["status"] == "success"
        assert res_json["user"]["username"] == reg_username
        print(f"[OK] User registration succeeded for username '{reg_username}'! Session ID: {res_json.get('session_id')}")

        # 6. Test Duplicate Registration Prevention
        print("\n--- 6. Testing Duplicate Registration Prevention ---")
        response_dup = client.post(
            "/api/register",
            data={
                "username": reg_username,
                "email": f"alice_{reg_username}@example.com",
                "password": "SecurePassword123!",
                "name": "Alice Smith",
                "target_company": "Google",
                "target_role": "Backend Engineer",
                "prep_days": 7,
                "daily_hours": 3.0,
                "current_skills": "Python, SQL"
            }
        )
        assert response_dup.status_code == 400
        assert "already registered" in response_dup.json()["detail"]
        print(f"[OK] Duplicate registration rejected correctly: {response_dup.json()['detail']}")

        # 7. Test User Login Authentication
        print("\n--- 7. Testing User Login Authentication (/api/login) ---")
        login_res = client.post(
            "/api/login",
            json={
                "username": reg_username,
                "password": "SecurePassword123!"
            }
        )
        assert login_res.status_code == 200
        assert login_res.json()["status"] == "success"
        assert login_res.json()["user"]["username"] == reg_username
        print(f"[OK] Login successful!")

        # Invalid password check
        bad_login_res = client.post(
            "/api/login",
            json={
                "username": reg_username,
                "password": "WrongPassword!"
            }
        )
        assert bad_login_res.status_code == 401
        print(f"[OK] Invalid login password rejected correctly (HTTP 401)")

        # 8. Test iCalendar (.ics) Exporter
        print("\n--- 8. Testing iCalendar (.ics) Exporter ---")
        sample_roadmap = Roadmap(
            total_days=2,
            daily_hours=3.0,
            overview="2-day backend preparation plan",
            days=[
                RoadmapDay(
                    day_number=1,
                    day_title="Data Structures & System Design",
                    tasks=[
                        RoadmapTask(topic="Arrays", subtopics=["Hashing"], duration_hours=1.5, priority="High", practice_task="Implement LRU Cache", expected_outcome="Understand cache O(1)")
                    ],
                    total_hours=3.0
                ),
                RoadmapDay(
                    day_number=2,
                    day_title="Mock Test & Behavioral Prep",
                    tasks=[
                        RoadmapTask(topic="Mock Test", subtopics=["MCQs"], duration_hours=1.5, priority="High", practice_task="Practice MCQs", expected_outcome="80%+ score")
                    ],
                    total_hours=3.0
                )
            ]
        )
        ics_text = ICSExporter.generate_ics_content(sample_roadmap, candidate_name="Alice Smith")
        assert "BEGIN:VCALENDAR" in ics_text
        assert "END:VCALENDAR" in ics_text
        assert "Day 1: Data Structures & System Design" in ics_text
        assert "Day 2: Mock Test & Behavioral Prep" in ics_text
        print(f"[OK] ICS content generated correctly:\n{ics_text[:200]}...\n")

        print("====================================================")
        print("    ALL AUTH & RESUME VALIDATION CHECKS PASSED!")
        print("====================================================")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_resume_validation_and_auth()
