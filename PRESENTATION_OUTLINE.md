# Demo & Slides — 5-Minute Plan

## Slide 1 — Problem (30s)
Data lives in 7 silos (ERP, LMS, placement cell…); faculty see marks too late.
We unify it into **one student view → one score → one action list**.

## Slide 2 — Approach (45s)
Pipeline: `raw_*.csv (7 sources)` → `students_integrated.csv` → `scoring.py`
→ `students_scored.csv` → dashboard. Score = 7-pillar weighted composite
(Acad 30 · Att 15 · LMS 15 · Place 15 · Engage 10 · Skills 10 · Feedback 5).
Dual risk lenses (academic + placement) + 6 actionable segments.

## Slide 3 — Live demo (2.5 min)
1. Year 3 → Section B roster: roll-ordered, CGPA with semester delta, absent counts, pending records.
2. Open a weak-vs-strong profile: 80+ in one subject, sub-50 in another → gap summary, weekly study timetable, tips.
3. Timetables tab: class schedule + personal study plan for that student.
4. AI Tutor: ask a subject doubt with the student's record attached (Groq key) — then show offline fallback.

## Slide 4 — Insight that pays (45s)
Every flagged student gets a **personal study plan from their own mark gaps**
(strong vs weak subjects → hours → weekly timetable), and mentors track the
**improvement feed**: deltas, on-time records, attendance recovery.

## Slide 5 — What's next (30s)
Plug real SIS/LMS APIs, fit weights on actual outcomes, add term-over-term
trend alerts + SMS nudges. Ask: pilot in one department next semester?
