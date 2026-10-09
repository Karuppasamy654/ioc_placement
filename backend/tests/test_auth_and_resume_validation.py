import sys
import os
import shutil
import tempfile
import uuid
import zipfile
try:
    import fitz  # type: ignore # PyMuPDF
except ImportError:
    fitz = None
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

def create_sample_docx(file_path: str, text_content: str):
    """Creates a valid .docx file using standard library zipfile without external C dependencies."""
    with zipfile.ZipFile(file_path, 'w') as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        escaped = text_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        paras = "".join([f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in escaped.split("\n")])
        xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{paras}</w:body></w:document>'
        z.writestr('word/document.xml', xml)

def create_sample_resume(file_path: str, candidate_name: str, content_text: str):
    """Utility helper to dynamically create a valid PDF or DOCX file with sample resume text."""
    ext = os.path.splitext(file_path)[1].lower()
    text = f"RESUME OF {candidate_name.upper()}\n\n"
    text += f"Email: {candidate_name.lower().replace(' ', '.')}@example.com | Phone: +1-555-0199\n\n"
    text += "SUMMARY:\n"
    text += content_text + "\n"
    text += "SKILLS:\nPython, React, FastApi, SQL, Docker, Data Structures, Algorithms\n"
    text += "EXPERIENCE:\nSoftware Engineer at TechCorp (2022 - Present)\n"
    text += "- Developed scalable microservices using Python and FastAPI.\n"
    text += "- Built real-time dashboard UI using React.js.\n"

    if ext == ".pdf" and fitz is not None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=11)
        doc.save(file_path)
        doc.close()
    else:
        create_sample_docx(file_path, text)

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
        short_doc_path = os.path.join(temp_dir, "short_resume.docx")
        create_sample_docx(short_doc_path, "John Doe Resume short")

        val_res2 = ResumeParserTool.validate_resume(short_doc_path, "John Doe")
        assert not val_res2.is_valid
        assert "less than 100 characters" in val_res2.error_message
        print(f"[OK] Short resume caught correctly: {val_res2.error_message}")

        # 2b. Test Resume Validation - Non-Resume Document (e.g. Essay/Report)
        print("\n--- 2b. Testing Non-Resume Document Rejection ---")
        essay_doc_path = os.path.join(temp_dir, "essay_document.docx")
        essay_text = "Alice Smith wrote a long essay about climate change and renewable energy sources including solar, wind, and hydroelectric power systems across global regions over decades of environmental policy research."
        create_sample_docx(essay_doc_path, essay_text)

        val_res_essay = ResumeParserTool.validate_resume(essay_doc_path, "Alice Smith")
        assert not val_res_essay.is_valid
        assert "does not appear to be a valid Resume" in val_res_essay.error_message
        print(f"[OK] Non-resume document rejected correctly: {val_res_essay.error_message}")

        # 3. Test Resume Validation - Candidate Name Mismatch
        print("\n--- 3. Testing Candidate Name Mismatch ---")
        resume_alice_path = os.path.join(temp_dir, "alice_resume.docx")
        long_body = "Professional Software Developer with extensive hands-on experience in backend architectures, cloud computing, continuous integration, and modern database management systems."
        create_sample_resume(resume_alice_path, "Alice Smith", long_body)

        val_res3 = ResumeParserTool.validate_resume(resume_alice_path, "Bob Williams")
        assert not val_res3.is_valid
        assert not val_res3.name_matched
        assert "was not found anywhere in the uploaded resume" in val_res3.error_message
        print(f"[OK] Name mismatch caught correctly: {val_res3.error_message}")

        # 4. Test Resume Validation - Successful Name Match
        print("\n--- 4. Testing Successful Resume Validation & Name Match ---")
        val_res4 = ResumeParserTool.validate_resume(resume_alice_path, "Alice Smith")
        assert val_res4.is_valid
        assert val_res4.name_matched
        assert not val_res4.error_message
        print(f"[OK] Resume valid and candidate name matched successfully!")

        # 5. Test API Registration Endpoint with Resume Validation
        print("\n--- 5. Testing API Registration Endpoint (/api/register) ---")
        reg_username = f"alice_user_{uuid.uuid4().hex[:6]}"
        
        with open(resume_alice_path, "rb") as f:
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
                files={"resume": ("alice_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
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
