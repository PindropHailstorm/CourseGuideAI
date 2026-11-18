% ==============================================================================
% SOUTH ASIAN UNIVERSITY - INTEGRATED M.TECH. (CSE) KNOWLEDGE BASE
% ==============================================================================

:- dynamic completed/2.      % completed(Student, CourseCode)
:- dynamic enrolled_track/2. % enrolled_track(Student, Track)

% ------------------------------------------------------------------------------
% 1. GROUND FACTS: COURSES (Code, Category, Credits, Description)
% ------------------------------------------------------------------------------
course(cse401, core, 4, 'Computer Organization and Design').
course(cse402, core, 4, 'Database Systems').
course(cse403, core, 4, 'Mathematical Foundations of Computer Science').
course(cse404, core, 4, 'Operating Systems Design').
course(cse405, core, 4, 'Programming and Data Structures').
course(cse406, core, 4, 'Computer Networks').
course(cse407, core, 4, 'Design and Analysis of Algorithms').
course(cs501,  core, 4, 'Data Mining').
course(cs502,  core, 4, 'Fundamentals of Artificial Intelligence').
course(cs503,  core, 4, 'Fundamentals of Machine Learning').
course(cs504,  core, 4, 'Optimization Techniques').
course(cs505,  core, 4, 'Advanced Data Structure and Algorithms').

% Electives: Track AIML
course(cs_e501, track_aiml, 4, 'Advanced Machine Learning').
course(cs_e502, track_aiml, 4, 'AI and ML Techniques for Cyber Security').
course(cs_e503, track_aiml, 4, 'Big Data Analytics').
course(cs_e504, track_aiml, 4, 'Advanced Artificial Intelligence').
course(cs_e505, track_aiml, 4, 'Deep Learning').
course(cs_e506, track_aiml, 4, 'Evolutionary Algorithms').
course(cs_e507, track_aiml, 4, 'Information Retrieval').
course(cs_e508, track_aiml, 4, 'Natural Language Processing').
course(cs_e510, track_aiml, 4, 'Reinforcement Learning').

% Electives: Track Networks
course(cs_e521, track_networks, 4, 'Blockchain Technology').
course(cs_e522, track_networks, 4, 'Cloud Computing').
course(cs_e523, track_networks, 4, 'Cryptography and Network Security').
course(cs_e524, track_networks, 4, 'Distributed Systems').
course(cs_e525, track_networks, 4, 'Internet of Things').
course(cs_e529, track_networks, 4, 'Software Defined Networking').

% General Electives
course(cs_e541, ge, 4, 'Distributed Machine Learning').
course(cs_e544, ge, 4, 'Logic for Computer Science').
course(cs_e550, ge, 4, 'Theory of Computation').

% ------------------------------------------------------------------------------
% 2. GROUND FACTS: PREREQUISITES
% ------------------------------------------------------------------------------
prereq(cse407, cse405). % Algorithms requires Data Structures
prereq(cs503,  cse403). % Machine Learning requires Math Foundations
prereq(cs503,  cse405). % Machine Learning requires Data Structures
prereq(cs505,  cse407). % Advanced Algorithms requires Algorithms
prereq(cs_e501, cs503). % Advanced ML requires Fundamentals of ML
prereq(cs_e504, cs502). % Advanced AI requires Fundamentals of AI
prereq(cs_e505, cs503). % Deep Learning requires Fundamentals of ML
prereq(cs_e508, cs502). % NLP requires Fundamentals of AI
prereq(cs_e524, cse406). % Distributed Systems requires Computer Networks
prereq(cs_e529, cse406). % SDN requires Computer Networks

% ------------------------------------------------------------------------------
% 3. GROUND FACTS: ACADEMIC POLICIES
% ------------------------------------------------------------------------------
policy(attendance, 'Minimum 60% attendance is required in each registered course to be eligible for end-semester examinations, with at least 70% overall.').
policy(grading, 'Evaluation follows a 10-point relative letter grading system (A+, A, B+, B, C, D, F). Pass mark per course is 40%.').
policy(credit_limit, 'The standard semester load is 16-24 credit hours. Maximum 24 credits per semester allowed. Overload requires departmental committee waiver.').
policy(prerequisites, 'Prerequisite requirements cannot be bypassed automatically. A student must complete all designated prerequisite courses before registering for advanced courses.').
policy(repeat, 'Courses with F grade must be repeated in subsequent semesters when offered.').

% ------------------------------------------------------------------------------
% 4. INFERENCE RULES (Horn Clauses)
% ------------------------------------------------------------------------------

% Check prerequisites requirement
has_prereq(Course, Required) :-
    prereq(Course, Required).

% Identify missing prerequisites for a student
missing_prereq(Student, Course, MissingPrereq) :-
    prereq(Course, MissingPrereq),
    \+ completed(Student, MissingPrereq).

% Check if all prerequisites are met
all_prereqs_met(Student, Course) :-
    course(Course, _, _, _),
    \+ missing_prereq(Student, Course, _).

% Course eligibility check
eligible(Student, Course) :-
    course(Course, _, _, _),
    \+ completed(Student, Course),
    all_prereqs_met(Student, Course).

% Elective derivation for student track
eligible_track_elective(Student, Course) :-
    enrolled_track(Student, Track),
    (
      (Track == aiml, course(Course, track_aiml, _, _));
      (Track == networks, course(Course, track_networks, _, _));
      (Track == general, (course(Course, track_aiml, _, _); course(Course, track_networks, _, _); course(Course, ge, _, _)))
    ),
    eligible(Student, Course).
