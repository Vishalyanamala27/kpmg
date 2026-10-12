# CampusTrack — Student Success Platform

College-portal-style analytics prototype: 1120 students (CSE/AIML/AIDS/CSDS/ECE/EEE/CS-IoT × Years 1–4 × Sec A–E), per-student attendance/marks/records, improvement plans, class timetables with timings, and a Groq AI study agent.

## Quickstart (2 min demo)
1. `pip install pandas numpy`
2. `python data_generator_v2.py` → 640 students (CSE/AIML/AIDS/CSDS × Years 1–4 × Sec A–E) + 80 class timetables with timings
3. `python scoring.py` → success scores + risk flags
4. `python study_planner.py` → study plans + improvement feeds → `dashboard/data.js`
5. `python -m http.server` inside `dashboard/`, open `index.html`.

## What's inside
| Path | Purpose |
|---|---|
| `data_generator.py` | Simulates 7 source systems (500 students, realistic correlations) |
| `scoring.py` | Success Score + dual risk model + 6 segments + per-student explainability |
| `dashboard/index.html` + `dashboard/data.js` | Interactive dashboard: KPIs, charts, filters, student profiles, intervention queue |
| `SUCCESS_SCORE_NOTE.md` | Scoring methodology (deliverable) |
| `PRESENTATION_OUTLINE.md` | 5-minute demo script + slide plan (deliverable) |

## Dashboard tour (college-portal style, no aggregate cards)
- **Find Student:** Year → Branch (CSE/AIML/AIDS/CSDS) → Section (A–E) → roll-ordered list; or global search.
- **Student page (per-student, like the college register):** blue RollNo/Name banner; **Attendance** table (Sl.No, Code, Subject, Short Name, Attended/Held/%) with red <75% rows + recovery warning; **Marks** (current vs last test); **Records & Assignments**; **Improvement Plan** (gap analysis, CGPA/skill targets, weekly study timetable); **Class Timetable** (Mon–Sat with timings, periods-per-week, today's schedule highlighted).
- **AI Study Agent:** floating bubble → popup card with suggestion chips, voice input, and send button. Paste a Groq key in Connection settings (saved in browser only); student-aware via "Ask AI Agent".
- Attendance below 75% always shows: "You are maintaining low attendance — attend the next N classes without fail."

## Key insight to land
147 of 500 students (29%) need attention — but each gets a concrete plan: e.g. "82 in DBMS but 47 in Networks → shift 3.3 hrs/week into Networks problem practice to cross 60 in 3 weeks."
