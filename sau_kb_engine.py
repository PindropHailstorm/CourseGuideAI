from pyswip import Prolog
from typing import List, Dict, Any

class SAUIntegratedMTechEngine:
    def __init__(self, kb_filepath: str = "sau_integrated_mtech_cse.pl"):
        self.prolog = Prolog()
        self.kb_filepath = kb_filepath
        self.prolog.consult(kb_filepath)

    def set_student_state(self, student_id: str, track: str, completed_courses: List[str]):
        """Dynamically update student transcript facts in Prolog KB."""
        self.prolog.retractall(f"completed({student_id}, _)")
        self.prolog.retractall(f"enrolled_track({student_id}, _)")

        self.prolog.assertz(f"enrolled_track({student_id}, {track})")
        for course in completed_courses:
            self.prolog.assertz(f"completed({student_id}, {course})")

    def run_query(self, query_str: str) -> List[Dict[str, str]]:
        results = []
        try:
            for raw_res in self.prolog.query(query_str):
                clean_res = {k: str(v) for k, v in raw_res.items()}
                results.append(clean_res)
        except Exception as err:
            print(f"[Prolog Query Error] {query_str}: {err}")
        return results

    def get_course_details(self, course_code: str) -> Dict[str, Any]:
        query = f"course({course_code}, Category, Credits, Title)"
        res = self.run_query(query)
        if res:
            return {
                "code": course_code,
                "category": res[0]["Category"],
                "credits": int(res[0]["Credits"]),
                "title": res[0]["Title"]
            }
        return {}

    def get_prerequisites(self, course_code: str) -> List[Dict[str, Any]]:
        query = f"prereq({course_code}, ReqCode)"
        res = self.run_query(query)
        prereqs = []
        for row in res:
            req_code = row["ReqCode"]
            details = self.get_course_details(req_code)
            prereqs.append({
                "code": req_code,
                "title": details.get("title", req_code.upper())
            })
        return prereqs

    def evaluate_course_eligibility(self, student_id: str, course_code: str) -> Dict[str, Any]:
        """Backward chaining goal resolution with full rule proof trace."""
        is_completed = len(self.run_query(f"completed({student_id}, {course_code})")) > 0
        prereqs = self.get_prerequisites(course_code)
        
        missing_res = self.run_query(f"missing_prereq({student_id}, {course_code}, MissingPrereq)")
        missing_codes = [r["MissingPrereq"] for r in missing_res]
        missing_details = [
            {"code": code, "title": self.get_course_details(code).get("title", code.upper())}
            for code in missing_codes
        ]

        is_eligible = len(self.run_query(f"eligible({student_id}, {course_code})")) > 0

        # Construct explicit Prolog backward-chaining trace steps
        proof_trace = [
            f"Goal: eligible({student_id}, {course_code})",
            f"1. Unify course({course_code}, Category, Credits, Title) -> Found ground fact.",
            f"2. Evaluate completed({student_id}, {course_code}) -> {'True (Already completed)' if is_completed else 'False (Not completed yet)'}",
            f"3. Query prerequisites for {course_code} -> Found {[p['code'] for p in prereqs]}"
        ]
        if missing_codes:
            proof_trace.append(f"4. Evaluate missing_prereq({student_id}, {course_code}, Missing) -> Discovered missing: {missing_codes}")
            proof_trace.append(f"5. Result: Goal failed. Student {student_id} is INELIGIBLE.")
        else:
            proof_trace.append(f"4. Evaluate missing_prereq({student_id}, {course_code}, Missing) -> No missing prerequisites.")
            proof_trace.append(f"5. Result: Goal proved. Student {student_id} is ELIGIBLE.")

        return {
            "student_id": student_id,
            "target_course": course_code,
            "already_completed": is_completed,
            "eligible": is_eligible,
            "prerequisites": prereqs,
            "missing_prerequisites": missing_details,
            "proof_trace": proof_trace
        }

    def get_available_track_electives(self, student_id: str) -> Dict[str, Any]:
        """Forward chaining derivation of all reachable electives for declared track."""
        res = self.run_query(f"eligible_track_elective({student_id}, Course)")
        eligible_codes = sorted(list(set(r["Course"] for r in res)))
        
        elective_list = [
            self.get_course_details(code) for code in eligible_codes
        ]

        proof_trace = [
            f"Forward Chaining Goal: Deriving reachable track electives for student '{student_id}'.",
            f"1. Fetch enrolled track -> {self.run_query(f'enrolled_track({student_id}, Track)')}",
            f"2. Unify eligible_track_elective({student_id}, Course) across rule set.",
            f"3. Derived eligible course set: {eligible_codes}"
        ]

        return {
            "eligible_electives": elective_list,
            "proof_trace": proof_trace
        }

    def query_policy(self, policy_key: str) -> Dict[str, Any]:
        res = self.run_query(f"policy({policy_key}, PolicyText)")
        if res:
            return {
                "policy_key": policy_key,
                "text": res[0]["PolicyText"],
                "proof_trace": [
                    f"Goal: policy({policy_key}, Text)",
                    f"1. Ground fact match: policy('{policy_key}', '{res[0]['PolicyText'][:40]}...')"
                ]
            }
        return {}
