# CampusGuide AI - SAU M.Tech. (CSE) Department Q&A Assistant

A production-grade Knowledge-Based Reasoning System built using Flask, SWI-Prolog, PySwip, and dynamic student transcript context.

## 4-Stage Logical Architecture
1. **Stage 1 (Natural Language Input)**: Cleans and tokenizes incoming student queries.
2. **Stage 2 (NLP & Entity Slot Parser)**: Maps queries to intent categories (`PREREQUISITE_CHECK`, `CREDIT_QUERY`, `ELIGIBILITY_CHECK`, `POLICY_QUERY`, `ELECTIVE_RECOMMENDATION`) and canonical course codes.
3. **Stage 3 (Ambiguity & Confidence Layer)**: Computes slot-binding confidence. Halts execution and asks clarification questions for vague inputs like "Tell me about AI".
4. **Stage 4 (SWI-Prolog Logical Deduction)**: Executes backward/forward chaining over dynamic transcript facts and Horn clauses via PySwip.

## Setup Instructions

1. **Install SWI-Prolog**:
   - Ubuntu/Debian: `sudo apt-get install swi-prolog`
   - macOS: `brew install swi-prolog`
   - Windows: Download installer from https://www.swi-prolog.org/ and append the `bin` directory to system `PATH`.

2. **Install Python Packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.
