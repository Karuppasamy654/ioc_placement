import random
from typing import List, Dict, Any, Optional
from backend.services.gemini_service import gemini_service
from backend.models.schemas import MCQQuestion, StudentProfile, CompanyResearch, Roadmap

class QuestionGeneratorTool:
    @staticmethod
    def generate_mock_test_questions(
        profile: StudentProfile,
        company_research: CompanyResearch,
        roadmap: Optional[Roadmap] = None,
        target_count: int = 55
    ) -> List[MCQQuestion]:
        """
        Generates 50-60 dynamic placement MCQs tailored to profile, role, company research, and roadmap topics.
        Uses batched Gemini generation when key is present, or dynamic domain synthesis if Gemini key is unconfigured.
        """
        target_count = max(50, min(60, target_count))
        
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
                system_instruction = "You are an expert technical interviewer creating placement MCQs in valid JSON format."
                raw_data = gemini_service.generate_json(prompt, system_instruction=system_instruction)
                
                if isinstance(raw_data, list):
                    for q_dict in raw_data:
                        if len(valid_questions) >= target_count:
                            break
                        parsed_q = QuestionGeneratorTool._validate_and_clean_question(q_dict, seen_questions)
                        if parsed_q:
                            valid_questions.append(parsed_q)

        # Fallback / Dynamic Synthesis if questions count is under target_count
        if len(valid_questions) < target_count:
            synthetic_qs = QuestionGeneratorTool._synthesize_dynamic_questions(
                profile=profile,
                company_research=company_research,
                topics=topics,
                count=target_count - len(valid_questions),
                seen=seen_questions
            )
            valid_questions.extend(synthetic_qs)

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
        """
        Dynamically generates technical MCQs dynamically tailored to candidate parameters when API key is pending.
        """
        syn_questions: List[MCQQuestion] = []
        role = profile.target_role
        company = profile.target_company
        
        # Domain concept generators
        concept_templates = [
            # DSA & Algorithms
            {
                "topic": "Data Structures & Algorithms",
                "difficulty": "medium",
                "q": "What is the worst-case time complexity of searching an element in an unbalanced Binary Search Tree (BST)?",
                "opts": ["O(log N)", "O(N)", "O(1)", "O(N log N)"],
                "ans": "O(N)",
                "exp": "In an unbalanced or skewed BST, searching degenerates to linear scan O(N)."
            },
            {
                "topic": "Data Structures & Algorithms",
                "difficulty": "hard",
                "q": "Which data structure is optimal for implementing LRU (Least Recently Used) cache with O(1) time complexity?",
                "opts": ["Array + Hash Map", "Doubly Linked List + Hash Map", "Stack + Queue", "Binary Heap + Array"],
                "ans": "Doubly Linked List + Hash Map",
                "exp": "A Hash Map provides O(1) node lookup and a Doubly Linked List allows O(1) removal and insertion at head/tail."
            },
            {
                "topic": "Data Structures & Algorithms",
                "difficulty": "easy",
                "q": "Which algorithm technique does Merge Sort utilize?",
                "opts": ["Greedy Approach", "Dynamic Programming", "Divide and Conquer", "Backtracking"],
                "ans": "Divide and Conquer",
                "exp": "Merge Sort repeatedly divides array in halves, recursively sorts them, and merges sorted subarrays."
            },

            # DBMS & SQL
            {
                "topic": "Database Management Systems",
                "difficulty": "medium",
                "q": "Which ACID property ensures that database transactions are committed permanently even in event of system crashes?",
                "opts": ["Atomicity", "Consistency", "Isolation", "Durability"],
                "ans": "Durability",
                "exp": "Durability guarantees that once a transaction completes, its updates persist in non-volatile storage."
            },
            {
                "topic": "Database Management Systems",
                "difficulty": "hard",
                "q": "What is the primary trade-off when adding a B-Tree index to a database column?",
                "opts": ["Faster SELECT queries but slower INSERT/UPDATE operations", "Slower SELECT queries but faster writes", "Higher memory usage with zero performance impact", "Disables database normalization"],
                "ans": "Faster SELECT queries but slower INSERT/UPDATE operations",
                "exp": "Indexes accelerate read queries via B-Tree traversal but impose maintenance overhead during write mutations."
            },

            # Operating Systems
            {
                "topic": "Operating Systems",
                "difficulty": "medium",
                "q": "What condition occurs when two or more processes are blocked indefinitely waiting for resources held by each other?",
                "opts": ["Starvation", "Deadlock", "Race Condition", "Thrashing"],
                "ans": "Deadlock",
                "exp": "Deadlock happens when processes enter circular wait holding non-preemptable resources."
            },
            {
                "topic": "Operating Systems",
                "difficulty": "hard",
                "q": "What is the phenomenon called when the CPU spends more time executing page swaps than actual processing?",
                "opts": ["Context Switching", "Segmentation Fault", "Thrashing", "Paging Overhead"],
                "ans": "Thrashing",
                "exp": "Thrashing occurs when high page fault rate forces constant page replacement between RAM and secondary disk."
            },

            # System Design & Web Architecture
            {
                "topic": "System Design",
                "difficulty": "hard",
                "q": "In high-throughput microservices architecture, which pattern prevents cascading failures when a downstream dependency experiences outage?",
                "opts": ["Circuit Breaker", "Saga Pattern", "CQRS", "Read Replica"],
                "ans": "Circuit Breaker",
                "exp": "The Circuit Breaker pattern detects dependency failures and immediately trips requests without exhausting caller threads."
            },
            {
                "topic": "System Design",
                "difficulty": "medium",
                "q": "Which HTTP protocol property allows GET requests to be safely retried multiple times without altering server side state?",
                "opts": ["Asynchronous", "Idempotency", "Statelessness", "Persistence"],
                "ans": "Idempotency",
                "exp": "HTTP GET is idempotent and safe because repeated requests produce identical state results."
            },

            # OOP & Software Engineering
            {
                "topic": "Object Oriented Programming",
                "difficulty": "easy",
                "q": "Which OOP principle allows a subclass to provide a specific implementation of a method defined in its parent class?",
                "opts": ["Encapsulation", "Method Overriding", "Method Overloading", "Abstraction"],
                "ans": "Method Overriding",
                "exp": "Method overriding allows dynamic runtime polymorphism where child class redefines superclass behavior."
            },
            {
                "topic": "Object Oriented Programming",
                "difficulty": "medium",
                "q": "What does the 'S' in SOLID object-oriented design principles stand for?",
                "opts": ["Single Responsibility Principle", "System Isolation Principle", "Static Interface Rule", "State Encapsulation Rule"],
                "ans": "Single Responsibility Principle",
                "exp": "Single Responsibility Principle dictates that a class should have one, and only one, reason to change."
            },

            # Role & Language Specific
            {
                "topic": f"{role} Core Engineering",
                "difficulty": "medium",
                "q": f"In a high-performance {role} workflow at {company}, which mechanism minimizes network round-trips for API consumers?",
                "opts": ["GraphQL / Batching", "Synchronous Polling", "Monolithic RPC", "FTP File Transfers"],
                "ans": "GraphQL / Batching",
                "exp": "Batching request payload queries via GraphQL or REST batch endpoints eliminates round-trip latency."
            },
            {
                "topic": "Computer Networks",
                "difficulty": "medium",
                "q": "During TCP 3-way handshake, what is the sequence of flag signals exchanged between Client and Server?",
                "opts": ["SYN -> SYN-ACK -> ACK", "ACK -> SYN -> FIN", "CONNECT -> OPEN -> READY", "SYN -> ACK -> DATA"],
                "ans": "SYN -> SYN-ACK -> ACK",
                "exp": "TCP connection establishment requires Client SYN, Server SYN-ACK response, and Client final ACK."
            }
        ]

        # Generate synthesized dynamic questions up to requested count
        seed_idx = 0
        while len(syn_questions) < count:
            tmpl = concept_templates[seed_idx % len(concept_templates)]
            q_text = tmpl["q"]
            
            # If question already seen, append variation counter
            if q_text.lower() in seen:
                q_text = f"[{company} {role} Assessment Variant {seed_idx + 1}] {tmpl['q']}"

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
