import os
import re
from typing import Optional
from backend.models.schemas import ResumeData
from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

# Guarded imports for optional document parsers
try:
    import fitz  # type: ignore # PyMuPDF
except ImportError:
    fitz = None

try:
    import docx  # type: ignore # python-docx
except ImportError:
    docx = None

class ResumeParserTool:
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
                    print(f"[RESUME PARSER TOOL ERROR] PDF extraction error: {e}")
            else:
                log_tool_process("Resume Parser Tool", "PyMuPDF not installed, skipping PDF text extraction", state=state)

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
                log_tool_process("Resume Parser Tool", "python-docx not installed, skipping DOCX text extraction", state=state)

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
