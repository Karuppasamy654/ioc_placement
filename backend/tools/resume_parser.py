import os
import re
from typing import Optional
from backend.models.schemas import ResumeData

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
    def parse_file(file_path: str) -> ResumeData:
        """
        Extracts raw text from PDF or DOCX resume and structures technical details.
        """
        if not os.path.exists(file_path):
            return ResumeData(extracted_text="")

        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        if ext == ".pdf":
            if fitz is not None:
                try:
                    doc = fitz.open(file_path)
                    for page in doc:
                        extracted_text += page.get_text() + "\n"
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] PDF extraction error: {e}")
            else:
                print("[RESUME PARSER TOOL WARNING] PyMuPDF (fitz) is not installed.")

        elif ext in [".docx", ".doc"]:
            if docx is not None:
                try:
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        extracted_text += para.text + "\n"
                except Exception as e:
                    print(f"[RESUME PARSER TOOL ERROR] DOCX extraction error: {e}")
            else:
                print("[RESUME PARSER TOOL WARNING] python-docx is not installed.")

        else:
            print(f"[RESUME PARSER TOOL WARNING] Unsupported file extension: {ext}")

        if not extracted_text.strip():
            return ResumeData(extracted_text="")

        return ResumeParserTool._structure_resume_text(extracted_text)

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
