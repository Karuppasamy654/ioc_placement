# AI PLACEMENT AGENT
### Personalized Placement Preparation & Adaptive Mock Test System

[![Agentic AI](https://img.shields.io/badge/Architecture-Agentic%20AI-00f2fe?style=for-the-badge)](https://github.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-10b981?style=for-the-badge)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018-4facfe?style=for-the-badge)](https://react.dev)
[![Gemini API](https://img.shields.io/badge/AI Engine-Gemini%20Flash-7f53ac?style=for-the-badge)](https://ai.google.dev)

---

## 1. Project Overview

The **AI Placement Agent** is an autonomous multi-agent software engineering system engineered to revolutionize campus placement and job interview preparation. Unlike generic learning management platforms or static flashcard tools, this system acts as a personalized technical mentor. It autonomously parses student resumes, researches live company hiring requirements, generates dynamic 50–60 question placement assessments, and adaptively updates the student's study roadmap based on actual test performance.

---

## 2. Problem Statement

Students preparing for technical placements face critical challenges with traditional prep methods:
- **Generic, One-Size-Fits-All Roadmaps**: Standard roadmaps fail to account for candidate-specific skill gaps, target companies, or remaining preparation time.
- **Static & Hardcoded Practice Tests**: Conventional test banks expose students to stale questions that do not reflect actual job descriptions or company tech stacks.
- **Lack of Adaptive Feedback**: Traditional platforms treat test taking as a terminal step without feeding test results back into future study plans.
- **Surface-Level Resume Assessment**: Students rarely understand how their current project portfolio aligns with role requirements.

---

## 3. Proposed Solution

The **AI Placement Agent** solves these issues through a closed-loop multi-agent architecture:
1. **Dynamic Student Profiling**: Analyzes self-reported skills + uploaded PDF/DOCX resumes to map technical competencies.
2. **Real-time Company Research**: Scrapes live job requirements and interview patterns using web research tools.
3. **Personalized Schedule Generation**: Constructs day-by-day study roadmaps scaled strictly to available days and daily study hours.
4. **Dynamic 50–60 MCQ Placement Test**: Queries Gemini API to produce context-aware technical MCQs matching target roles and candidate gaps.
5. **Adaptive Learning Loop**: Deterministically evaluates answer accuracy, identifies weak topics, and automatically modifies upcoming study schedules.

---

## 4. Key Features

- 🤖 **Multi-Agent Collaboration**: Orchestrates 5 specialized agents with shared state execution.
- 📄 **Resume Parser Tool**: Extracts technical skills, projects, and education from PDF/DOCX files (PyMuPDF & python-docx).
- 🌐 **Company Research Tool**: Fetches live web information and candidate requirements with source transparency.
- ⚡ **Dynamic 50–60 MCQ Generator**: Generates 50–60 placement questions tailored to candidates without pre-written data.
- 📊 **Deterministic Performance Analyzer**: Evaluates exact scores, topic accuracy, and difficulty metrics in pure Python.
- 🔄 **Adaptive Schedule Adjustment**: Automatically shifts future study schedules to reinforce weak areas detected during mock tests.
- 🖥️ **Dual Progress Visibility**: Displays execution progress in terminal stdout and real-time frontend dashboard.
- 🔗 **Source Transparency**: Provides clickable reference links for company research sources.

---

## 5. Why Agentic AI?

Traditional AI tools follow a simple **User → Prompt → Model → Response** pattern. The AI Placement Agent implements true **Agentic AI**:

| Aspect | Traditional Chatbot | AI Placement Agent (Agentic) |
| :--- | :--- | :--- |
| **Execution Flow** | Single prompt-response turn | Multi-step autonomous graph pipeline |
| **Tool Usage** | None / Manual prompt copying | Autonomous invocation of 4 deterministic tools |
| **State Management** | Stateless conversation window | Shared mutable `SessionState` across agents |
| **Task Decomposition**| Expects human to break down tasks | Autonomous separation into profile, research, roadmap, test, and performance tasks |
| **Feedback Loop** | Static output | Closed-loop adaptive learning (Test Score → Weak Topic Detection → Roadmap Update) |

---

## 6. System Architecture

```
                       +-----------------------------------+
                       |           Student Input           |
                       | (Name, Role, Company, Days, Hours)|
                       +-----------------------------------+
                                         |
                                         v
                       +-----------------------------------+
                       |         ORCHESTRATOR AGENT        |
                       |       (Shared Session State)      |
                       +-----------------------------------+
                                   |           ^
                    +--------------+           +--------------+
                    |                                         |
                    v                                         v
     +-----------------------------+           +-----------------------------+
     |   PROFILE ANALYSIS AGENT    |           |     COMPANY RESEARCH TOOL   |
     |    (Skill & Gap Extraction) |           |  (DuckDuckGo / Live Web API)|
     +-----------------------------+           +-----------------------------+
                    |                                         |
                    +--------------+           +--------------+
                                   |           |
                                   v           v
                       +-----------------------------------+
                       |           ROADMAP AGENT           |
                       |     (Dynamic Multi-Day Plan)      |
                       +-----------------------------------+
                                         |
                                         v
                       +-----------------------------------+
                       |          MOCK TEST AGENT          |
                       |  (Question Generation Tool / Gemini)|
                       +-----------------------------------+
                                         |
                                         v
                       +-----------------------------------+
                       |       Student Takes Mock Test     |
                       |           (50-60 MCQs)            |
                       +-----------------------------------+
                                         |
                                         v
                       +-----------------------------------+
                       |    PERFORMANCE ANALYSIS AGENT     |
                       |  (Performance Analyzer Tool Math) |
                       +-----------------------------------+
                                         |
                                         v
                       +-----------------------------------+
                       |    ADAPTIVE LEARNING LOOP UPDATES  |
                       |     (Upcoming Schedule Modified)  |
                       +-----------------------------------+
```

---

## 7. Agent Architecture

### 1. Orchestrator Agent
- **Purpose**: Controls workflow pipeline, manages shared state transitions, logs terminal output, and handles errors.
- **Inputs**: `StudentInput`, uploaded resume file.
- **Processing**: Initializes session state, sequences agent nodes, appends execution logs.
- **Outputs**: Active `SessionState` containing profile, roadmap, questions, and performance.

### 2. Profile Analysis Agent
- **Purpose**: Combines user inputs and resume text to generate structured candidate profile.
- **Inputs**: `StudentInput`, `ResumeData`.
- **Processing**: Identifies strong skills, gaps, and role recommendations via Gemini reasoning.
- **Outputs**: `StudentProfile`.

### 3. Roadmap Agent
- **Purpose**: Generates customized multi-day schedule matching study hours and candidate gaps.
- **Inputs**: `StudentProfile`, `CompanyResearch`.
- **Processing**: Allocates study hours dynamically (e.g. less basic DSA for strong candidates, more DBMS for weak candidates).
- **Outputs**: `Roadmap`.

### 4. Mock Test Agent
- **Purpose**: Coordinates dynamic generation of 50–60 MCQs tailored to profile and roadmap.
- **Inputs**: `StudentProfile`, `CompanyResearch`, `Roadmap`.
- **Processing**: Calls `QuestionGeneratorTool` with Gemini API in structured batches.
- **Outputs**: `MockTest`.

### 5. Performance Analysis Agent
- **Purpose**: Evaluates actual user answers and adaptively updates future schedule.
- **Inputs**: `MockTest`, `QuizSubmission`, current `Roadmap`.
- **Processing**: Calls `PerformanceAnalyzerTool` for arithmetic scoring, then invokes Gemini to generate schedule adjustments.
- **Outputs**: `PerformanceReport`, `AdaptiveAdjustment`.

---

## 8. Tool Architecture

### 1. Resume Parser Tool
- **Function**: Extracts text from `.pdf` (PyMuPDF) and `.docx` (python-docx) files; categorizes skills, education, and projects without inventing data.

### 2. Company Research Tool
- **Function**: Searches live web APIs (DuckDuckGo search) for company hiring trends, required technologies, and reference URLs. Returns `research_available = False` if search fails.

### 3. Question Generation Tool
- **Function**: Queries Gemini API with strict JSON schemas in parallel batches to produce 50–60 validated MCQs with exact option matching and deduplication.

### 4. Performance Analyzer Tool
- **Function**: Deterministic Python tool calculating total questions, correct/incorrect count, percentage score, topic-wise accuracy, and difficulty breakdown.

---

## 9. End-to-End Workflow

1. Student enters name, target company, target role, prep days, study hours, skills, and optional resume.
2. **Orchestrator Agent** initializes pipeline and logs `[ORCHESTRATOR] Workflow started`.
3. **Resume Parser Tool** extracts text and skills from uploaded document.
4. **Profile Agent** identifies strong skills and gaps.
5. **Company Research Tool** fetches live company info and source URLs.
6. **Roadmap Agent** creates a personalized multi-day schedule.
7. **Question Generator Tool** generates 50–60 placement questions.
8. Student completes mock test and submits answers.
9. **Performance Analyzer Tool** computes score and topic accuracy.
10. **Performance Agent** modifies upcoming roadmap days to reinforce weak topics.

---

## 10. Adaptive Learning Loop

```
Initial Student Profile
          │
          ▼
   Generated Roadmap
          │
          ▼
50-60 Question Mock Test
          │
          ▼
Deterministic Scoring (Python)
          │
          ▼
Weak Topic Identification
          │
          ▼
Roadmap & Schedule Adjustment
```

---

## 11. Gemini API Integration

- **Model Selection**: Centralized wrapper in `backend/services/gemini_service.py` using fallback model cascade (`gemini-2.5-flash`, `gemini-1.5-flash`).
- **Structured JSON Mode**: Uses `responseMimeType: "application/json"` and Pydantic validation.
- **Security**: API key stored strictly in `.env` (`GEMINI_API_KEY`); never exposed in frontend or logs.

---

## 12. Data Flow

```
StudentInput + Resume File -> ResumeParserTool -> ResumeData
StudentInput + ResumeData -> ProfileAgent -> StudentProfile
StudentProfile + WebSearch -> CompanyResearchTool -> CompanyResearch
StudentProfile + CompanyResearch -> RoadmapAgent -> Roadmap
StudentProfile + CompanyResearch + Roadmap -> QuestionGeneratorTool -> MockTest (50-60 MCQs)
MockTest + QuizSubmission -> PerformanceAnalyzerTool -> PerformanceReport
PerformanceReport + Roadmap -> PerformanceAgent -> AdaptiveAdjustment (Updated Roadmap)
```

---

## 13. Technology Stack

| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Frontend** | UI & Dashboard | React 18, Vite, Vanilla CSS (Glassmorphism), Lucide Icons |
| **Backend** | REST API Server | Python 3.13, FastAPI, Uvicorn, Pydantic v2 |
| **AI / LLM Engine** | Reasoning & Generation | Google Gemini API (gemini-2.5-flash / gemini-1.5-flash) |
| **Resume Parsing** | Document Extraction | PyMuPDF (fitz), python-docx |
| **Research** | Live Web Search | DuckDuckGo Search (`duckduckgo-search` / `ddgs`) |
| **State Graph** | Agent Workflow | Shared In-Memory Session State & Node Graph |

---

## 14. Project Structure

```
IOC_PROJECT/
├── backend/
│   ├── main.py                     # FastAPI routes & CORS setup
│   ├── agents/
│   │   ├── orchestrator.py          # Orchestrator Agent
│   │   ├── profile_agent.py         # Profile Analysis Agent
│   │   ├── roadmap_agent.py         # Roadmap Agent
│   │   ├── mock_test_agent.py       # Mock Test Agent
│   │   └── performance_agent.py     # Performance Analysis Agent
│   ├── tools/
│   │   ├── resume_parser.py         # Resume Parser Tool
│   │   ├── company_research.py      # Company Research Tool
│   │   ├── question_generator.py    # Question Generator Tool
│   │   └── performance_analyzer.py  # Performance Analyzer Tool
│   ├── services/
│   │   └── gemini_service.py        # Gemini API centralized wrapper
│   ├── models/
│   │   ├── schemas.py               # Pydantic schemas
│   │   └── state.py                 # Shared session state manager
│   ├── workflows/
│   │   └── placement_graph.py       # State graph definitions
│   └── utils/
│       └── logger.py                # Terminal log formatting
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StudentForm.jsx      # Setup form component
│   │   │   ├── AgentActivity.jsx    # Real-time event log component
│   │   │   ├── Roadmap.jsx          # Roadmap dashboard component
│   │   │   ├── ResumeGap.jsx        # Skill gap breakdown component
│   │   │   ├── MockTest.jsx         # Quiz interface component
│   │   │   ├── Results.jsx          # Performance analytics component
│   │   │   └── Sources.jsx          # Research source component
│   │   ├── App.jsx                  # Main container
│   │   ├── api.js                   # Axios HTTP client
│   │   ├── main.jsx                 # React DOM entry point
│   │   └── styles.css               # Glassmorphism styling
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 15. UI/UX Design

The application uses a high-end dark glassmorphism dashboard design:
- **Landing Form**: Clean inputs with icons, file drag-and-drop, and privacy disclaimers.
- **Agent Activity**: Real-time agent status checkmarks + live terminal stream.
- **Roadmap Cards**: Multi-day timeline cards with topic badges, durations, and practice outcomes.
- **Mock Test UI**: Question navigator grid, option cards, progress indicators, and submit dialogs.
- **Performance Dashboard**: Percentage score ring, topic accuracy bars, and adaptive recommendations.
- **Source Transparency View**: Verified web search URLs.

---

## 16. Installation

### Prerequisites
- Python 3.10+
- Node.js v18+

### 1. Clone Repository & Setup Virtual Environment

```bash
cd d:\Documents\IOC_PROJECT

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 17. Environment Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=8000
HOST=0.0.0.0
```

*(You can copy from `.env.example`: `cp .env.example .env`)*

---

## 18. Running the Application

### Option A: Run Backend & Frontend in Parallel

**Terminal 1 (Backend FastAPI Server):**
```bash
# Make sure venv is activated
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend React Vite Server):**
```bash
cd frontend
npm run dev
```

Open browser at `http://localhost:3000`.

---

## 19. Demo Workflow (2-Minute Sequence)

1. Open `http://localhost:3000`.
2. Fill out Student Form:
   - Name: `Alex Johnson`
   - Target Company: `Google`
   - Target Role: `Full Stack Engineer`
   - Prep Days: `5` | Daily Hours: `4`
   - Current Skills: `JavaScript, Python, React, SQL`
3. Upload sample resume PDF or DOCX (optional).
4. Click **"Generate My Personalized Preparation Plan"**.
5. Switch to **Agent Execution** tab — show live terminal logs streaming backend events!
6. Click **Roadmap** tab — inspect personalized 5-day preparation strategy.
7. Click **Mock Test** tab — start the 50–60 dynamic question assessment.
8. Answer questions and click **Submit Assessment**.
9. View **Performance** tab — show score percentage, topic breakdown, and updated schedule!
10. View **Sources** tab — inspect live web research URLs.

---

## 20. API Documentation

### `GET /api/health`
- **Purpose**: API health check.
- **Response**: `{"status": "healthy", "service": "AI Placement Agent API"}`

### `POST /api/prepare`
- **Purpose**: Executes initial multi-agent pipeline.
- **Request (Multipart Form)**: `name`, `target_company`, `target_role`, `prep_days`, `daily_hours`, `current_skills`, `resume` (file).
- **Response**: `{"session_id": "...", "profile": {...}, "company_research": {...}, "roadmap": {...}}`

### `GET /api/mock-test?session_id={id}`
- **Purpose**: Retrieves generated 50–60 question mock test for session.
- **Response**: `{"mock_test": {"total_questions": 55, "questions": [...]}}`

### `POST /api/submit-test`
- **Purpose**: Evaluates test submission and adapts roadmap.
- **Request Body**: `{"session_id": "...", "answers": [{"question_index": 0, "selected_option": "O(N^2)"}]}`
- **Response**: `{"performance": {...}, "adaptive_adjustment": {...}}`

### `GET /api/agent-events?session_id={id}`
- **Purpose**: Retrieves real-time agent execution events for terminal log stream.
- **Response**: `{"events": [{"timestamp": "17:05:12", "agent_name": "Profile Agent", ...}]}`

---

## 21. Error Handling

- **Missing Resume**: System cleanly proceeds using self-reported student inputs.
- **Search Unavailability**: Displays "Company research unavailable" without fabricating fake statistics.
- **Gemini API Failures**: Automatically retries using model fallbacks (`gemini-2.5-flash` -> `gemini-1.5-flash`).
- **Malformed JSON**: Uses Pydantic validation & regex parsing repair.

---

## 22. Security

- API keys stored strictly in `.env`.
- Frontend has zero access to server secrets.
- Input file extensions (`.pdf`, `.docx`) and sizes validated.
- Zero secret logging in terminal or browser.

---

## 23. Limitations

- Web research depends on public search availability.
- Company interview patterns change over time.
- Voice/video mock interview evaluations are not included in MVP.

---

## 24. Future Enhancements

- 🎤 **Voice Interview Agent**: Interactive real-time audio mock interviews.
- 💻 **Live Code Sandbox**: Integrated Python/JS code execution environment.
- 📅 **Google Calendar Export**: One-click sync for daily prep roadmaps.

---

## 25. Ethical / Responsible AI

- Does not guarantee placement outcomes; serves as an educational accelerator.
- Transparently displays source URLs.
- Handles student data with privacy-first temporary in-memory processing.

---

## 26. Testing

- `GET /api/health`: Verified HTTP 200 OK.
- `Resume Parser`: Verified text extraction from PyMuPDF & docx.
- `50-60 Question Generator`: Verified schema compliance & 4 options per question.
- `Performance Analyzer`: Verified 0–100% mathematical precision.

---

## 27. Evaluation Highlights

- **Multi-Agent Architecture**: Real agent state graph collaboration.
- **No Dummy Data**: 100% dynamic generation via Gemini & web research.
- **4 Real Tools**: Resume Parser, Company Research, Question Generator, Performance Analyzer.
- **Adaptive Learning Loop**: Closed feedback loop updating future study plans.
- **Professional UI/UX**: Clean dark glassmorphism dashboard.

---

## 28. Conclusion

The **AI Placement Agent** demonstrates how multi-agent AI architectures, external tools, and closed-loop feedback systems transform passive learning into an intelligent, adaptive preparation experience.
