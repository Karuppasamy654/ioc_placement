import os
import re
from typing import Optional
from backend.models.schemas import ResumeData, ResumeValidationResult
from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

# Guarded imports for optional document parsers
try:
    import fitz  # type: ignore # PyMuPDF
except ImportError:
    fitz = None

try:
    import pypdf  # type: ignore # pypdf (pure Python PDF reader)
except ImportError:
    pypdf = None

try:
    import docx  # type: ignore # python-docx
except ImportError:
    docx = None

class ResumeParserTool:
    @staticmethod
    def validate_resume(file_path: str, candidate_name: str) -> ResumeValidationResult:
        """
        Validates file format, minimum readable text, and verifies candidate name matching.
        """
        try:
            if not file_path or not os.path.exists(file_path):
                return ResumeValidationResult(
                    is_valid=False,
                    name_matched=False,
                    error_message="Resume file was not uploaded or file path is invalid. Please select a valid PDF/DOCX resume file."
                )

            ext = os.path.splitext(file_path)[1].lower()
            if ext not in [".pdf", ".docx", ".doc"]:
                return ResumeValidationResult(
                    is_valid=False,
                    name_matched=False,
                    error_message=f"Invalid file format '{ext}'. Please upload a valid PDF (.pdf) or Word (.docx) resume file."
                )

            resume_data = ResumeParserTool.parse_file(file_path)
            extracted_text = (resume_data.extracted_text or "") if resume_data else ""
            char_count = len(extracted_text.strip())

            if char_count < 100:
                return ResumeValidationResult(
                    is_valid=False,
                    name_matched=False,
                    character_count=char_count,
                    error_message="Uploaded resume file is unreadable or empty (less than 100 characters extracted). Please upload a text-based PDF/DOCX resume."
                )

            # Strict Resume Content Validation: Document MUST contain typical resume section keywords
            resume_keywords = [
                "education", "experience", "skill", "skills", "project", "projects",
                "work history", "employment", "certification", "certifications",
                "qualification", "qualifications", "curriculum vitae", "resume", "summary",
                "achievement", "achievements", "b.tech", "b.e", "bachelor", "master", "gpa", "cgpa", "degree"
            ]
            text_lower = extracted_text.lower()
            matched_keywords = set()
            for kw in resume_keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    matched_keywords.add(kw)

            if len(matched_keywords) < 2:
                return ResumeValidationResult(
                    is_valid=False,
                    name_matched=False,
                    character_count=char_count,
                    error_message="Uploaded document does not appear to be a valid Resume / CV. A valid resume must contain standard section headings (such as Education, Work Experience, Technical Skills, or Projects)."
                )

            # Candidate name matching safely
            cand_name_str = candidate_name or ""
            name_tokens = [t.strip().lower() for t in cand_name_str.split() if len(t.strip()) >= 3]
            
            name_matched = False
            if not name_tokens:
                name_matched = True
            else:
                name_matched = any(token in text_lower for token in name_tokens)

            if not name_matched:
                return ResumeValidationResult(
                    is_valid=False,
                    name_matched=False,
                    character_count=char_count,
                    error_message=f"Candidate name '{candidate_name}' was not found anywhere in the uploaded resume. Please upload your own resume matching your registered name."
                )

            return ResumeValidationResult(
                is_valid=True,
                name_matched=True,
                character_count=char_count,
                error_message=""
            )
        except Exception as e:
            print(f"[RESUME VALIDATION ERROR] {e}")
            return ResumeValidationResult(
                is_valid=False,
                name_matched=False,
                error_message="Resume processing error. Please ensure your uploaded file is a readable PDF or Word document."
            )

    @staticmethod
    def parse_file(file_path: str, state=None) -> ResumeData:
        """
        Extracts raw text from PDF or DOCX resume and structures technical details.
        """
        start_time = log_tool_start("Resume Parser Tool", f"file={os.path.basename(file_path)}", state=state)

        if not os.path.exists(file_path):
            log_tool_result("Resume Parser Tool", "File not found. Returning empty resume profile.", start_time, state=state)
            return ResumeData(extracted_text="")

        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        if ext == ".pdf":
            if fitz is not None:
                log_tool_process("Resume Parser Tool", "Extracting PDF text using PyMuPDF (fitz)", state=state)
                try:
                    doc = fitz.open(file_path)
                    for page in doc:
                        extracted_text += page.get_text() + "\n"
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] PyMuPDF PDF extraction error: {e}")

            if len(extracted_text.strip()) < 50 and pypdf is not None:
                log_tool_process("Resume Parser Tool", "Extracting PDF text using pypdf reader", state=state)
                try:
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            extracted_text += t + "\n"
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] pypdf extraction error: {e}")

            if len(extracted_text.strip()) < 50:
                log_tool_process("Resume Parser Tool", "Extracting PDF text using raw stream decoder fallback", state=state)
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                        strings = re.findall(rb"\(([^()]{3,})\)\s*T[jJ]", content)
                        if strings:
                            extracted_text += " ".join(s.decode("latin1", errors="ignore") for s in strings)
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] Raw PDF stream fallback error: {e}")

        elif ext in [".docx", ".doc"]:
            if docx is not None:
                log_tool_process("Resume Parser Tool", "Extracting DOCX paragraphs using python-docx", state=state)
                try:
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        extracted_text += para.text + "\n"
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] DOCX extraction error: {e}")
            else:
                log_tool_process("Resume Parser Tool", "Extracting DOCX text using standard zipfile/xml parser", state=state)
                try:
                    import zipfile
                    import xml.etree.ElementTree as ET
                    with zipfile.ZipFile(file_path) as z:
                        xml_bytes = z.read('word/document.xml')
                        root = ET.fromstring(xml_bytes)
                        extracted_text = " ".join(root.itertext())
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] Zip/XML DOCX fallback error: {e}")

        char_count = len(extracted_text.strip())
        if char_count == 0:
            log_tool_result("Resume Parser Tool", "0 characters extracted from file.", start_time, state=state)
            return ResumeData(extracted_text="")

        log_tool_process("Resume Parser Tool", f"Structuring candidate skills and projects from {char_count} extracted characters", state=state)
        structured_data = ResumeParserTool._structure_resume_text(extracted_text)

        result_summary = f"{char_count} characters extracted | {len(structured_data.technical_skills)} skills found | {len(structured_data.projects)} projects found"
        log_tool_result("Resume Parser Tool", result_summary, start_time, state=state)

        return structured_data

    @staticmethod
    def _structure_resume_text(text: str) -> ResumeData:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        known_langs = ["python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "sql", "html", "css", "kotlin", "swift", "r", "php"]
        known_frameworks = ["react", "node.js", "express", "fastapi", "django", "flask", "next.js", "vue", "angular", "spring boot", "tailwind", "bootstrap"]
        known_databases = ["postgresql", "mysql", "mongodb", "sqlite", "redis", "dynamodb", "oracle", "cassandra"]
        
        tech_skills = []
        prog_langs = []
        frameworks = []
        databases = []
        education = []
        projects = []
        experience = []

        text_lower = text.lower()

        for lang in known_langs:
            if re.search(r"\b" + re.escape(lang) + r"\b", text_lower):
                prog_langs.append(lang.capitalize() if len(lang) > 3 else lang.upper())

        for fw in known_frameworks:
            if re.search(r"\b" + re.escape(fw) + r"\b", text_lower):
                frameworks.append(fw.title())

        for db in known_databases:
            if re.search(r"\b" + re.escape(db) + r"\b", text_lower):
                databases.append(db.title())

        tech_skills = list(set(prog_langs + frameworks + databases))

        for line in lines:
            if any(term in line.lower() for term in ["b.tech", "b.e", "bachelor", "master", "m.tech", "university", "college", "degree", "gpa", "cgpa"]):
                education.append(line)

        for line in lines:
            if any(term in line.lower() for term in ["project", "developed", "built", "implemented", "system", "app"]):
                if len(line) > 15:
                    projects.append(line)

        for line in lines:
            if any(term in line.lower() for term in ["intern", "engineer", "developer", "experience", "role", "company"]):
                if len(line) > 15:
                    experience.append(line)

        return ResumeData(
            education=education[:4],
            technical_skills=tech_skills,
            programming_languages=prog_langs,
            frameworks=frameworks,
            databases=databases,
            projects=projects[:5],
            certifications=[],
            experience=experience[:4],
            achievements=[],
            extracted_text=text[:3000]
        )
