import re
from flask import Flask, render_template, request, jsonify
from sau_kb_engine import SAUIntegratedMTechEngine

app = Flask(__name__)

# Initialize SWI-Prolog KB Engine
engine = SAUIntegratedMTechEngine("sau_integrated_mtech_cse.pl")

AVAILABLE_COURSES = {
    # Core Courses (12)
    "cse401": "Computer Organization and Design",
    "cse402": "Database Systems",
    "cse403": "Mathematical Foundations of Computer Science",
    "cse404": "Operating Systems Design",
    "cse405": "Programming and Data Structures",
    "cse406": "Computer Networks",
    "cse407": "Design and Analysis of Algorithms",
    "cs501":  "Data Mining",
    "cs502":  "Fundamentals of Artificial Intelligence",
    "cs503":  "Fundamentals of Machine Learning",
    "cs504":  "Optimization Techniques",
    "cs505":  "Advanced Data Structure and Algorithms",

    # Track 1 Electives: Artificial Intelligence & Machine Learning (9)
    "cs_e501": "Advanced Machine Learning",
    "cs_e502": "AI and ML Techniques for Cyber Security",
    "cs_e503": "Big Data Analytics",
    "cs_e504": "Advanced Artificial Intelligence",
    "cs_e505": "Deep Learning",
    "cs_e506": "Evolutionary Algorithms",
    "cs_e507": "Information Retrieval",
    "cs_e508": "Natural Language Processing",
    "cs_e510": "Reinforcement Learning",

    # Track 2 Electives: Advanced Networks & Systems (6)
    "cs_e521": "Blockchain Technology",
    "cs_e522": "Cloud Computing",
    "cs_e523": "Cryptography and Network Security",
    "cs_e524": "Distributed Systems",
    "cs_e525": "Internet of Things",
    "cs_e529": "Software Defined Networking",

    # General Electives (3)
    "cs_e541": "Distributed Machine Learning",
    "cs_e544": "Logic for Computer Science",
    "cs_e550": "Theory of Computation",
}

COURSE_ALIASES = {
    # Core Courses
    "coa": "cse401",
    "cod": "cse401",
    "computer organization": "cse401",
    "computer organization and design": "cse401",

    "dbms": "cse402",
    "database": "cse402",
    "database systems": "cse402",

    "mfcs": "cse403",
    "math foundations": "cse403",
    "mathematical foundations": "cse403",
    "mathematical foundations of computer science": "cse403",

    "os": "cse404",
    "osd": "cse404",
    "operating systems": "cse404",
    "operating systems design": "cse404",

    "pds": "cse405",
    "data structures": "cse405",
    "programming and data structures": "cse405",

    "cn": "cse406",
    "networks": "cse406",
    "computer networks": "cse406",

    "daa": "cse407",
    "algorithms": "cse407",
    "design and analysis of algorithms": "cse407",

    "dm": "cs501",
    "data mining": "cs501",

    "fai": "cs502",
    "ai": "cs502",
    "artificial intelligence": "cs502",
    "fundamentals of ai": "cs502",
    "fundamentals of artificial intelligence": "cs502",

    "fml": "cs503",
    "ml": "cs503",
    "machine learning": "cs503",
    "fundamentals of ml": "cs503",
    "fundamentals of machine learning": "cs503",

    "ot": "cs504",
    "optimization": "cs504",
    "optimization techniques": "cs504",

    "adsa": "cs505",
    "advanced algorithms": "cs505",
    "advanced data structures": "cs505",
    "advanced data structure and algorithms": "cs505",

    # Track 1: AI & ML Electives
    "aml": "cs_e501",
    "advanced ml": "cs_e501",
    "advanced machine learning": "cs_e501",

    "cyber security": "cs_e502",
    "cybersecurity": "cs_e502",
    "ai for cyber security": "cs_e502",
    "ai and ml techniques for cyber security": "cs_e502",

    "bda": "cs_e503",
    "big data": "cs_e503",
    "big data analytics": "cs_e503",

    "aai": "cs_e504",
    "advanced ai": "cs_e504",
    "advanced artificial intelligence": "cs_e504",
    "computational intelligence": "cs_e504",

    "dl": "cs_e505",
    "deep learning": "cs_e505",

    "ea": "cs_e506",
    "evolutionary": "cs_e506",
    "evolutionary algorithms": "cs_e506",

    "ir": "cs_e507",
    "information retrieval": "cs_e507",

    "nlp": "cs_e508",
    "natural language processing": "cs_e508",

    "rl": "cs_e510",
    "reinforcement learning": "cs_e510",

    # Track 2: Networks & Systems Electives
    "blockchain": "cs_e521",
    "blockchain technology": "cs_e521",

    "cloud": "cs_e522",
    "cloud computing": "cs_e522",

    "cns": "cs_e523",
    "cryptography": "cs_e523",
    "network security": "cs_e523",
    "cryptography and network security": "cs_e523",

    "distributed systems": "cs_e524",

    "iot": "cs_e525",
    "internet of things": "cs_e525",

    "sdn": "cs_e529",
    "software defined networking": "cs_e529",

    # General Electives
    "dml": "cs_e541",
    "distributed ml": "cs_e541",
    "distributed machine learning": "cs_e541",

    "lcs": "cs_e544",
    "logic": "cs_e544",
    "logic for computer science": "cs_e544",

    "toc": "cs_e550",
    "theory of computation": "cs_e550",
}


def extract_course_code(raw_query: str) -> str | None:
    q = raw_query.strip().lower()
    # 1. Direct course code match (e.g., cse401, cs_e505)
    for code in AVAILABLE_COURSES:
        if re.search(rf"\b{re.escape(code)}\b", q):
            return code
    # 2. Longest-first alias match with word boundaries
    for alias in sorted(COURSE_ALIASES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", q):
            return COURSE_ALIASES[alias]
    return None


@app.route("/")
def index():
    return render_template("index.html", courses=AVAILABLE_COURSES)


@app.route("/api/query", methods=["POST"])
def query_advising():
    data = request.json or {}
    student_id = data.get("student_id", "s101")
    track = data.get("track", "aiml")
    completed = data.get("completed_courses", [])
    raw_query = data.get("query", "").strip()

    if not raw_query:
        return jsonify({"error": "Empty query received."}), 400

    q_lower = raw_query.lower()

    stage_1 = {
        "status": "COMPLETED",
        "description": f"Received query: '{raw_query}'"
    }

    target_course_code = extract_course_code(raw_query)
    target_course_title = (
        AVAILABLE_COURSES.get(target_course_code, target_course_code.upper())
        if target_course_code
        else None
    )
    intent = "UNKNOWN"
    if "prerequisite" in q_lower or "prereq" in q_lower or "require" in q_lower:
        intent = "PREREQUISITE_CHECK"
    elif "credit" in q_lower or "how many credits" in q_lower:
        intent = "CREDIT_QUERY"
    elif (
        "elective" in q_lower
        or "recommend" in q_lower
        or "what can i take" in q_lower
        or "what next" in q_lower
    ):
        intent = "ELECTIVE_RECOMMENDATION"
    elif "eligible" in q_lower or "can i take" in q_lower or "enroll" in q_lower:
        intent = "ELIGIBILITY_CHECK"
    elif "policy" in q_lower or "attendance" in q_lower or "grading" in q_lower or "rules" in q_lower:
        intent = "POLICY_QUERY"
    elif "help" in q_lower or "what is" in q_lower or "explain" in q_lower:
        intent = "GENERAL_INFO"
    # intent = "UNKNOWN"
    # if "prerequisite" in q_lower or "prereq" in q_lower or "require" in q_lower:
    #     intent = "PREREQUISITE_CHECK"
    # elif "credit" in q_lower or "how many credits" in q_lower:
    #     intent = "CREDIT_QUERY"
    # elif "eligible" in q_lower or "can i take" in q_lower or "enroll" in q_lower:
    #     intent = "ELIGIBILITY_CHECK"
    # elif "policy" in q_lower or "attendance" in q_lower or "grading" in q_lower or "rules" in q_lower:
    #     intent = "POLICY_QUERY"
    # elif "elective" in q_lower or "recommend" in q_lower or "what can i take" in q_lower or "what next" or "what electives can i take next" in q_lower:
    #     intent = "ELECTIVE_RECOMMENDATION"
    # elif "tell me about" in q_lower or "what is" in q_lower or "explain" in q_lower:
    #     intent = "GENERAL_INFO"

    stage_2 = {
        "status": "COMPLETED",
        "intent": intent,
        "extracted_entity": target_course_code,
        "entity_title": target_course_title,
        "description": f"Intent: {intent} | Entity: {target_course_title or target_course_code or 'None'}"
    }

    confidence = 0.0
    if intent != "UNKNOWN":
        confidence += 0.5
    if target_course_code:
        confidence += 0.5
    elif intent in ["POLICY_QUERY", "ELECTIVE_RECOMMENDATION"]:
        confidence += 0.5

    stage_3 = {
        "status": "COMPLETED",
        "confidence": confidence,
        "description": f"Confidence score: {confidence:.2f}."
    }

    if confidence < 0.6 and not (intent in ["POLICY_QUERY", "ELECTIVE_RECOMMENDATION"]):
        if "tell me about" in q_lower or intent == "GENERAL_INFO":
            missing_text = f"Your question about '{raw_query}' is broad. Did you mean to ask for the prerequisites, credits, or course eligibility for {target_course_title or 'a specific course'}?"
        else:
            missing_text = "I couldn't confidently map your question to a department course or policy rule. Please specify a course code (e.g. FML, Deep Learning, cs_e505) or ask 'Can I take Advanced AI?'"

        stage_3["status"] = "NEEDS_CLARIFICATION"
        stage_3["description"] = "Underspecified query detected. Clarification requested."
        
        return jsonify({
            "status": "ambiguous",
            "stages": {
                "input": stage_1,
                "nlp": stage_2,
                "ambiguity": stage_3,
                "reasoning": {"status": "SKIPPED", "description": "Halted prior to logic execution due to low confidence."}
            },
            "confidence": confidence,
            "answer": missing_text,
            "trace": [
                "1. Natural Language input parsed.",
                "2. Extracted entities underspecified.",
                "3. Ambiguity Handler halted execution to prevent statistical hallucination."
            ]
        })

    engine.set_student_state(student_id=student_id, track=track, completed_courses=completed)
    
    stage_4 = {
        "status": "COMPLETED",
        "description": "Executed SWI-Prolog Horn clause rules via PySwip."
    }

    answer = ""
    trace = []
    prolog_payload = {}

    if intent == "PREREQUISITE_CHECK" or (intent == "GENERAL_INFO" and target_course_code):
        if not target_course_code:
            return jsonify({
                "status": "ambiguous",
                "stages": {"input": stage_1, "nlp": stage_2, "ambiguity": {"status": "FAILED", "confidence": 0.4}, "reasoning": {"status": "SKIPPED"}},
                "confidence": 0.4,
                "answer": "Which course would you like to check prerequisites for? (e.g., Advanced AI, Deep Learning, FML)",
                "trace": ["1. Prerequisites requested without target course specification."]
            })

        prereqs = engine.get_prerequisites(target_course_code)
        details = engine.get_course_details(target_course_code)
        prolog_payload = {"course": details, "prerequisites": prereqs}

        if prereqs:
            req_str = ", ".join([f"{p['code'].upper()} ({p['title']})" for p in prereqs])
            answer = f"The prerequisite(s) for **{details['title']} ({target_course_code.upper()})** is/are: **{req_str}**."
        else:
            answer = f"**{details['title']} ({target_course_code.upper()})** has no prerequisite courses. It is an introductory core requirement."

        trace = [
            f"Goal: prereq({target_course_code}, RequiredPrereq)",
            f"1. Query Prolog KB for ground facts of {target_course_code}.",
            f"2. Found {len(prereqs)} prerequisite clause(s) in Prolog KB.",
            f"3. Direct logical deduction completed with 100% determinism."
        ]

    elif intent == "CREDIT_QUERY":
        if not target_course_code:
            return jsonify({
                "status": "ambiguous",
                "stages": {"input": stage_1, "nlp": stage_2, "ambiguity": {"status": "FAILED", "confidence": 0.4}, "reasoning": {"status": "SKIPPED"}},
                "confidence": 0.4,
                "answer": "Which course's credit count are you asking about? (e.g., How many credits is FML?)",
                "trace": ["1. Credit query missing target course."]
            })

        details = engine.get_course_details(target_course_code)
        prolog_payload = details
        answer = f"**{details['title']} ({target_course_code.upper()})** is a **{details['credits']} credit hour** course."
        trace = [
            f"Goal: course({target_course_code}, Category, Credits, Title)",
            f"1. Unified course ground fact: credits = {details['credits']}.",
            "2. Retracted runtime dynamic predicates; rule evaluation succeeded."
        ]

    elif intent == "ELIGIBILITY_CHECK":
        if not target_course_code:
            return jsonify({
                "status": "ambiguous",
                "stages": {"input": stage_1, "nlp": stage_2, "ambiguity": {"status": "FAILED", "confidence": 0.5}, "reasoning": {"status": "SKIPPED"}},
                "confidence": 0.5,
                "answer": "Which course are you inquiring about for enrollment eligibility? (e.g., Can I take Advanced AI?)",
                "trace": ["1. Eligibility request missing target course entity."]
            })

        eval_res = engine.evaluate_course_eligibility(student_id, target_course_code)
        prolog_payload = eval_res
        trace = eval_res["proof_trace"]

        c_title = engine.get_course_details(target_course_code).get("title", target_course_code.upper())

        if eval_res["already_completed"]:
            answer = f"You have already completed **{c_title} ({target_course_code.upper()})**."
        elif eval_res["eligible"]:
            answer = f"**Yes, you are ELIGIBLE to take {c_title} ({target_course_code.upper()}).** All required prerequisites have been satisfied on your transcript."
        else:
            missing_str = ", ".join([f"{m['code'].upper()} ({m['title']})" for m in eval_res["missing_prerequisites"]])
            answer = f"**No, you are NOT ELIGIBLE to take {c_title} ({target_course_code.upper()}) yet.** Missing required prerequisite(s): **{missing_str}**."

    elif intent == "POLICY_QUERY":
        policy_key = "attendance" if "attendance" in q_lower else ("grading" if "grading" in q_lower else "prerequisites")
        policy_res = engine.query_policy(policy_key)
        prolog_payload = policy_res
        answer = f"**Department Policy ({policy_key.capitalize()}):** {policy_res.get('text', 'No policy fact found.')}"
        trace = policy_res.get("proof_trace", ["1. Direct policy predicate search in Prolog database."])

    elif intent == "ELECTIVE_RECOMMENDATION":
        electives_res = engine.get_available_track_electives(student_id)
        prolog_payload = electives_res
        trace = electives_res["proof_trace"]

        el_list = electives_res["eligible_electives"]
        if el_list:
            formatted_el = [f"**{e['code'].upper()}** ({e['title']})" for e in el_list]
            answer = f"Based on your declared track (**{track.upper()}**) and completed prerequisites, you are eligible to take: {', '.join(formatted_el)}."
        else:
            answer = f"No track electives are available yet for **{track.upper()}** track. Complete foundational core prerequisites first."

    return jsonify({
        "status": "success",
        "stages": {
            "input": stage_1,
            "nlp": stage_2,
            "ambiguity": stage_3,
            "reasoning": stage_4
        },
        "confidence": confidence,
        "answer": answer,
        "trace": trace,
        "prolog_data": prolog_payload
    })


@app.route("/api/compare", methods=["POST"])
def compare_llm():
    data = request.json or {}
    raw_query = data.get("query", "").strip()

    llm_analysis = {
        "llm_answer": f"For '{raw_query}', typically students need basic programming or introductory AI courses. (Note: Generic statistical LLMs may hallucinate non-existent course codes like CS999 or fail to enforce exact prerequisite chains).",
        "tradeoff_discussion": (
            "**Reliability Trade-Off Analysis:**\n\n"
            "1. **Deterministic Prolog KB**: Returns 100% accurate, rule-verifiable answers based on exact ground facts and Horn clauses. Zero hallucinations, but strictly requires explicit slot binding.\n"
            "2. **Statistical LLM**: Highly versatile with freeform language, but vulnerable to hallucinating nonexistent course codes, missing complex prerequisite chains, or assuming default policies without verifying student context."
        )
    }
    return jsonify(llm_analysis)


if __name__ == "__main__":
    app.run(debug=True, port=5000)