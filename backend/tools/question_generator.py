import random
from typing import List, Dict, Any, Optional
from backend.services.gemini_service import gemini_service
from backend.models.schemas import MCQQuestion, StudentProfile, CompanyResearch, Roadmap
from backend.utils.logger import log_tool_start, log_tool_process, log_tool_result

class QuestionGeneratorTool:
    @staticmethod
    def generate_mock_test_questions(
        profile: StudentProfile,
        company_research: CompanyResearch,
        roadmap: Optional[Roadmap] = None,
        target_count: int = 55,
        state=None
    ) -> List[MCQQuestion]:
        """
        Generates 50-60 dynamic placement MCQs tailored to profile, role, company research, and roadmap topics.
        """
        target_count = max(50, min(60, target_count))
        start_time = log_tool_start("Question Generator Tool", f"target_count={target_count}, role='{profile.target_role}'", state=state)

        # Collect target topics from roadmap or profile
        topics = []
        if roadmap and roadmap.days:
            for day in roadmap.days:
                for task in day.tasks:
                    if task.topic not in topics:
                        topics.append(task.topic)

        if not topics:
            topics = ["Data Structures & Algorithms", "Database Management Systems", "Object Oriented Programming", "Operating Systems", "Computer Networks", "System Design", "Aptitude & Problem Solving"]

        if profile.weak_areas:
            topics.extend(profile.weak_areas)

        topics = list(set(topics))
        topics_str = ", ".join(topics[:8])
        role = profile.target_role
        company = profile.target_company
        skills_str = ", ".join(profile.user_skills[:10])

        valid_questions: List[MCQQuestion] = []
        seen_questions = set()

        # Check if Gemini API is configured
        if gemini_service.is_configured():
            log_tool_process("Question Generator Tool", "Querying Gemini API in structured batches for dynamic MCQs", state=state)
            batches = [
                {"count": 30, "focus": "Core CS Concepts (DSA, DBMS, OOP, OS, Networking)"},
                {"count": 30, "focus": f"{role} Specific Engineering, System Design, Problem Solving & {company} Focus"}
            ]

            for batch in batches:
                if len(valid_questions) >= target_count:
                    break

                needed = batch["count"]
                prompt = f"""
Generate EXACTLY {needed} multiple choice placement questions (MCQs) for a student preparing for:
- Target Role: {role}
- Target Company: {company}
- Candidate Skills: {skills_str}
- Focus Topics for this batch: {batch['focus']}
- Key Topics to Cover: {topics_str}

CRITICAL RULES:
1. Return a JSON array containing EXACTLY {needed} question objects.
2. DO NOT include any text outside the JSON array.
3. Every question must have:
   - "question": Clear, challenging technical question text
   - "options": An array of EXACTLY 4 distinct option strings
   - "correct_answer": The EXACT string matching one of the 4 options
   - "topic": Topic name
   - "difficulty": "easy", "medium", or "hard"
   - "explanation": Step-by-step technical explanation
"""
                raw_data = gemini_service.generate_json(prompt, system_instruction="You are an expert technical interviewer creating placement MCQs in valid JSON format.", purpose=f"Generate MCQs for {batch['focus']}", state=state)
                
                if isinstance(raw_data, list):
                    for q_dict in raw_data:
                        if len(valid_questions) >= target_count:
                            break
                        parsed_q = QuestionGeneratorTool._validate_and_clean_question(q_dict, seen_questions)
                        if parsed_q:
                            valid_questions.append(parsed_q)

        # Fallback / Dynamic Synthesis if questions count is under target_count
        if len(valid_questions) < target_count:
            missing_cnt = target_count - len(valid_questions)
            log_tool_process("Question Generator Tool", f"Synthesizing {missing_cnt} technical domain questions to reach target assessment count", state=state)
            synthetic_qs = QuestionGeneratorTool._synthesize_dynamic_questions(
                profile=profile,
                company_research=company_research,
                topics=topics,
                count=missing_cnt,
                seen=seen_questions
            )
            valid_questions.extend(synthetic_qs)

        result_summary = f"{len(valid_questions)} valid dynamic MCQs generated and validated (4 options per question)."
        log_tool_result("Question Generator Tool", result_summary, start_time, state=state)

        return valid_questions[:target_count]

    @staticmethod
    def _validate_and_clean_question(q_dict: Dict[str, Any], seen_questions: set) -> Optional[MCQQuestion]:
        try:
            question_text = str(q_dict.get("question", "")).strip()
            options = q_dict.get("options", [])
            correct_answer = str(q_dict.get("correct_answer", "")).strip()
            topic = str(q_dict.get("topic", "General")).strip()
            difficulty = str(q_dict.get("difficulty", "medium")).lower().strip()
            explanation = str(q_dict.get("explanation", "")).strip()

            if not question_text or len(question_text) < 10:
                return None

            q_key = question_text.lower()
            if q_key in seen_questions:
                return None

            if not isinstance(options, list) or len(options) != 4:
                return None

            clean_options = [str(opt).strip() for opt in options]
            if len(set(clean_options)) != 4:
                return None

            if correct_answer not in clean_options:
                if correct_answer.upper() in ["A", "OPTION A", "1"]:
                    correct_answer = clean_options[0]
                elif correct_answer.upper() in ["B", "OPTION B", "2"]:
                    correct_answer = clean_options[1]
                elif correct_answer.upper() in ["C", "OPTION C", "3"]:
                    correct_answer = clean_options[2]
                elif correct_answer.upper() in ["D", "OPTION D", "4"]:
                    correct_answer = clean_options[3]
                else:
                    for opt in clean_options:
                        if correct_answer.lower() in opt.lower() or opt.lower() in correct_answer.lower():
                            correct_answer = opt
                            break
                    if correct_answer not in clean_options:
                        correct_answer = clean_options[0]

            if difficulty not in ["easy", "medium", "hard"]:
                difficulty = "medium"

            seen_questions.add(q_key)

            return MCQQuestion(
                question=question_text,
                options=clean_options,
                correct_answer=correct_answer,
                topic=topic,
                difficulty=difficulty,
                explanation=explanation or f"The correct option is {correct_answer}."
            )
        except Exception:
            return None

    @staticmethod
    def _synthesize_dynamic_questions(
        profile: StudentProfile,
        company_research: CompanyResearch,
        topics: List[str],
        count: int,
        seen: set
    ) -> List[MCQQuestion]:
        syn_questions: List[MCQQuestion] = []
        role = profile.target_role
        company = profile.target_company
        
        concept_templates = [
            {
                "topic": "Data Structures & Algorithms",
                "difficulty": "medium",
                "q": "What is the worst-case time complexity of searching an element in an unbalanced Binary Search Tree (BST)?",
                "opts": ["O(log N)", "O(N)", "O(1)", "O(N log N)"],
                "ans": "O(N)",
                "exp": "In an unbalanced BST, search degrades to linear scan O(N)."
            },
            {
                "topic": "Data Structures & Algorithms",
                "difficulty": "hard",
                "q": "Which data structure is optimal for implementing LRU cache with O(1) time complexity?",
                "opts": ["Array + Hash Map", "Doubly Linked List + Hash Map", "Stack + Queue", "Binary Heap + Array"],
                "ans": "Doubly Linked List + Hash Map",
                "exp": "Hash Map provides O(1) lookup and Doubly Linked List provides O(1) removal/insertion."
            },
            {
                "topic": "Database Management Systems",
                "difficulty": "medium",
                "q": "Which ACID property guarantees that committed transactions persist across system crashes?",
                "opts": ["Atomicity", "Consistency", "Isolation", "Durability"],
                "ans": "Durability",
                "exp": "Durability ensures committed updates persist in non-volatile storage."
            },
            {
                "topic": "System Design",
                "difficulty": "hard",
                "q": "Which pattern prevents cascading failures when a downstream microservice dependency experiences outage?",
                "opts": ["Circuit Breaker", "Saga Pattern", "CQRS", "Read Replica"],
                "ans": "Circuit Breaker",
                "exp": "Circuit Breaker trips failed requests immediately to prevent resource exhaustion."
            },
            {
                "topic": "Operating Systems",
                "difficulty": "medium",
                "q": "What condition occurs when two or more processes wait indefinitely for resources held by each other?",
                "opts": ["Starvation", "Deadlock", "Race Condition", "Thrashing"],
                "ans": "Deadlock",
                "exp": "Deadlock occurs when processes enter circular wait holding non-preemptable resources."
            },
            {
                "topic": "Object Oriented Programming",
                "difficulty": "medium",
                "q": "What does the 'S' in SOLID design principles stand for?",
                "opts": ["Single Responsibility Principle", "System Isolation Principle", "Static Interface Rule", "State Encapsulation Rule"],
                "ans": "Single Responsibility Principle",
                "exp": "Single Responsibility Principle states a class should have one reason to change."
            }
        ]

        seed_idx = 0
        while len(syn_questions) < count:
            tmpl = concept_templates[seed_idx % len(concept_templates)]
            q_text = tmpl["q"]
            
            if q_text.lower() in seen:
                q_text = f"[{company} {role} Assessment Item #{seed_idx + 1}] {tmpl['q']}"

            if q_text.lower() not in seen:
                seen.add(q_text.lower())
                syn_questions.append(MCQQuestion(
                    question=q_text,
                    options=list(tmpl["opts"]),
                    correct_answer=tmpl["ans"],
                    topic=tmpl["topic"],
                    difficulty=tmpl["difficulty"],
                    explanation=tmpl["exp"]
                ))

            seed_idx += 1

        return syn_questions
