"""Enriched student data generator v3 — branch/section structure.
Branches: CSE, AIML, AIDS, CSDS x Years 1-4 x Sections A-E.
Per student: subject-wise marks (current vs last test), per-subject
attendance (held/attended), lab records, assignments, CGPA, absents.
Timetables per branch-year-section with real period timings.
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import date, timedelta

RNG = np.random.default_rng(11)
BASE = Path(__file__).parent
OUT = BASE / "data"
OUT.mkdir(exist_ok=True)

BRANCHES = {"CSE": "05", "AIML": "ML", "AIDS": "DS", "CSDS": "CS",
            "ECE": "04", "EEE": "02", "CS-IoT": "IO"}
SECTIONS = ["A", "B", "C", "D", "E"]
PER_SECTION = 8

BASE_SUBJECTS = {
    1: {"theory": [("MA101", "Mathematics I", "M1"), ("PH101", "Physics", "PHY"),
                   ("CH101", "Chemistry", "CHE"), ("CS101", "Programming in C", "C-PROG"),
                   ("EN101", "English", "ENG")],
        "labs": [("PHL101", "Physics Lab", "PHY LAB"), ("CSL101", "C Programming Lab", "C LAB")]},
    2: {"theory": [("MA201", "Mathematics II", "M2"), ("CS201", "Data Structures", "DS"),
                   ("CS202", "Digital Electronics", "DE"), ("CS203", "OOP Through Java", "OOPTJ"),
                   ("ES201", "Environmental Science", "ES")],
        "labs": [("CSL201", "Data Structures Lab", "DS LAB"), ("CSL202", "Java Lab", "JAVA LAB")]},
    3: {"theory": [("CS301", "DBMS", "DBMS"), ("CS302", "Operating Systems", "OS"),
                   ("CS303", "Computer Networks", "CN"), ("CS304", "Web Technologies", "WT"),
                   ("CS305", "Machine Learning", "ML")],
        "labs": [("CSL301", "DBMS Lab", "DBMS LAB"), ("CSL302", "Networks Lab", "CN LAB")]},
    4: {"theory": [("CS401", "Cloud Computing", "CC"), ("CS402", "Cyber Security", "CYS"),
                   ("CS403", "AI Elective", "AIE"), ("CS404", "DevOps", "DEVOPS"),
                   ("CS405", "Project Work", "PROJ")],
        "labs": [("CSL401", "Cloud Lab", "CC LAB"), ("CSL402", "Project Lab", "PROJ LAB")]},
}
# full subject tables for ECE / EEE / CS-IoT (year 1 stays common for all)
BRANCH_TABLES = {
    ("ECE", 2): {"theory": [("MA201", "Mathematics II", "M2"), ("EC201", "Electronic Devices & Circuits", "EDC"),
                            ("EC202", "Digital Electronics", "DE"), ("EC203", "Signals & Systems", "SS"),
                            ("EC204", "Network Theory", "NT")],
                 "labs": [("ECL201", "ED Circuits Lab", "EDC LAB"), ("ECL202", "Digital Lab", "DIG LAB")]},
    ("ECE", 3): {"theory": [("EC301", "Analog Communication", "AC"), ("EC302", "Microprocessors & Microcontrollers", "MPMC"),
                            ("EC303", "Electromagnetic Waves", "EMW"), ("EC304", "VLSI Design", "VLSI"),
                            ("EC305", "Digital Signal Processing", "DSP")],
                 "labs": [("ECL301", "Communication Lab", "COMM LAB"), ("ECL302", "MP Lab", "MP LAB")]},
    ("ECE", 4): {"theory": [("EC401", "Wireless Communication", "WC"), ("EC402", "Embedded Systems", "ESYS"),
                            ("EC403", "Optical Communication", "OC"), ("EC404", "ML for Engineers", "MLE"),
                            ("EC405", "Project Work", "PROJ")],
                 "labs": [("ECL401", "Embedded Lab", "EMB LAB"), ("ECL402", "Project Lab", "PROJ LAB")]},
    ("EEE", 2): {"theory": [("MA201", "Mathematics II", "M2"), ("EE201", "Electrical Circuits", "ECKT"),
                            ("EE202", "Digital Electronics", "DE"), ("EE203", "Electromagnetic Fields", "EMF"),
                            ("EE204", "Measurements & Instrumentation", "MI")],
                 "labs": [("EEL201", "Circuits Lab", "CKT LAB"), ("EEL202", "Measurements Lab", "MI LAB")]},
    ("EEE", 3): {"theory": [("EE301", "Power Systems I", "PS1"), ("EE302", "Electrical Machines I", "EM1"),
                            ("EE303", "Control Systems", "CSYS"), ("EE304", "Power Electronics", "PE"),
                            ("EE305", "Microprocessors", "MP")],
                 "labs": [("EEL301", "Machines Lab", "MACH LAB"), ("EEL302", "Power Electronics Lab", "PE LAB")]},
    ("EEE", 4): {"theory": [("EE401", "Power Systems II", "PS2"), ("EE402", "Electrical Machines II", "EM2"),
                            ("EE403", "Smart Grid", "SG"), ("EE404", "Electric Vehicles", "EV"),
                            ("EE405", "Project Work", "PROJ")],
                 "labs": [("EEL401", "Simulations Lab", "SIM LAB"), ("EEL402", "Project Lab", "PROJ LAB")]},
    ("CS-IoT", 2): {"theory": [("MA201", "Mathematics II", "M2"), ("CS201", "Data Structures", "DS"),
                               ("CS202", "Digital Electronics", "DE"), ("IO203", "Sensors & Actuators", "S&A"),
                               ("IO204", "OOP Through Java", "OOPTJ")],
                    "labs": [("CSL201", "Data Structures Lab", "DS LAB"), ("IOL202", "IoT Basics Lab", "IOT LAB")]},
    ("CS-IoT", 3): {"theory": [("CS301", "DBMS", "DBMS"), ("CS302", "Operating Systems", "OS"),
                               ("IO303", "Computer Networks", "CN"), ("IO304", "Embedded C & IoT", "EIOT"),
                               ("IO305", "Machine Learning", "ML")],
                    "labs": [("IOL301", "IoT Lab", "IOT LAB"), ("IOL302", "Networks Lab", "CN LAB")]},
    ("CS-IoT", 4): {"theory": [("IO401", "Cloud for IoT", "CIOT"), ("IO402", "IoT Security", "ISEC"),
                               ("IO403", "Edge Computing", "EDGE"), ("IO404", "AI Elective", "AIE"),
                               ("IO405", "Project Work", "PROJ")],
                    "labs": [("IOL401", "Cloud IoT Lab", "CIOT LAB"), ("IOL402", "Project Lab", "PROJ LAB")]},
}
ELECTIVE = {
    2: {"AIML": ("AI201", "AI Foundations", "AIF"), "AIDS": ("DS201", "Data Handling", "DH"),
        "CSDS": ("SD201", "Statistics for Data Science", "SDS")},
    3: {"AIML": ("AI301", "Neural Networks", "NN"), "AIDS": ("DS301", "Data Visualization", "DV"),
        "CSDS": ("SD301", "Big Data Basics", "BD")},
    4: {"AIML": ("AI401", "Deep Learning", "DL"), "AIDS": ("DS401", "MLOps", "MLOPS"),
        "CSDS": ("SD401", "Data Engineering", "DE2")},
}

NAMES = ["Aarav", "Diya", "Arjun", "Ananya", "Vivaan", "Ishita", "Kabir", "Meera",
         "Rohan", "Sneha", "Aditya", "Priya", "Karan", "Neha", "Rahul", "Pooja",
         "Sahil", "Riya", "Manav", "Tanvi", "Vishal", "Kiran", "Divya", "Harsha"]
SURNAMES = ["Sharma", "Patel", "Reddy", "Iyer", "Khan", "Gupta", "Nair", "Singh",
            "Das", "Kulkarni", "Yanamala", "Chowdary", "Naidu", "Rao", "Varma"]

SEM_START = date(2026, 7, 13)
PERIOD_TIMES = ["9:00 - 10:00", "10:00 - 11:00", "11:15 - 12:15",
                "1:00 - 2:00", "2:00 - 3:00", "3:15 - 4:15"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def absent_dates(n):
    seen, d, out = set(), SEM_START, []
    while len(out) < n and d < date(2026, 11, 30):
        if d.weekday() < 6 and d not in seen and RNG.random() < 0.3:
            seen.add(d)
            out.append(d)
        d += timedelta(days=1)
    return [x.strftime("%d %b") for x in sorted(out)]


def subjects_for(year, branch):
    if (branch, year) in BRANCH_TABLES:
        t = BRANCH_TABLES[(branch, year)]
        return t["theory"], t["labs"]
    th = list(BASE_SUBJECTS[year]["theory"])
    if year in ELECTIVE and branch in ELECTIVE[year]:
        th[4] = ELECTIVE[year][branch]
    return th, BASE_SUBJECTS[year]["labs"]


students, detailed = [], []
sid = 0
for branch in BRANCHES:
    for year in (1, 2, 3, 4):
        adm = 27 - year  # admission batch
        th_subs, lab_subs = subjects_for(year, branch)
        for sec in SECTIONS:
            for n in range(1, PER_SECTION + 1):
                sid += 1
                ability = RNG.normal(0, 1)
                engage = RNG.normal(0, 1)
                rate = float(np.clip(0.78 + 0.07 * ability + 0.05 * engage + RNG.normal(0, 0.07), 0.3, 0.99))
                name = f"{RNG.choice(NAMES)} {RNG.choice(SURNAMES)}"
                student_id = f"STU{str(sid).zfill(3)}"
                roll_no = f"{adm}491{BRANCHES[branch]}{sec}{n:02d}"

                subs = []
                for code, sname, short in th_subs:
                    cur = float(np.clip(62 + 12 * ability + RNG.normal(0, 9), 25, 99).round(0))
                    prev = float(np.clip(cur + RNG.normal(0, 7), 20, 99).round(0))
                    held = int(RNG.integers(38, 47))
                    att = int(np.clip(round(held * (rate + RNG.normal(0, 0.06))), 0, held))
                    tot, ot = 4, int(np.clip(np.round(2.6 + 0.9 * engage + RNG.normal(0, 0.9)), 0, 4))
                    late = int(np.clip(np.round(RNG.normal(0.7, 0.6) - 0.3 * engage), 0, tot - ot))
                    subs.append({"code": code, "name": sname, "short": short, "type": "theory",
                                 "current": cur, "previous": prev, "max": 100,
                                 "held": held, "attended": att,
                                 "assignments": {"total": tot, "on_time": ot, "late": late,
                                                 "pending": tot - ot - late}})
                labs = []
                for code, sname, short in lab_subs:
                    cur = float(np.clip(66 + 11 * ability + 3 * engage + RNG.normal(0, 8), 28, 100).round(0))
                    prev = float(np.clip(cur + RNG.normal(0, 6), 20, 100).round(0))
                    held = int(RNG.integers(18, 23))
                    att = int(np.clip(round(held * (rate + RNG.normal(0, 0.05))), 0, held))
                    r = RNG.random()
                    status = "on_time" if r < 0.45 + 0.12 * engage else ("late" if r < 0.8 else "pending")
                    labs.append({"code": code, "name": sname, "short": short, "type": "lab",
                                 "current": cur, "previous": prev, "max": 100,
                                 "held": held, "attended": att,
                                 "record": status,
                                 "days_vs_last": int(np.clip(np.round(RNG.normal(-0.5, 2)), -6, 6))})

                held_t = sum(s["held"] for s in subs + labs)
                att_t = sum(s["attended"] for s in subs + labs)
                pct = round(100 * att_t / held_t, 2)
                avg_cur = float(np.mean([s["current"] for s in subs]))
                avg_prev = float(np.mean([s["previous"] for s in subs]))
                cgpa = round(float(np.clip(avg_cur / 9.5, 4.0, 10.0)), 2)

                students.append({
                    "student_id": student_id, "name": name, "dept": branch, "year": year,
                    "cgpa": cgpa, "avg_marks": round(avg_cur, 1),
                    "backlogs": int(sum(1 for s in subs if s["current"] < 40)),
                    "attendance_pct": pct,
                    "lms_logins_pm": int(np.clip(round(14 + 4 * engage), 1, 30)),
                    "assignment_completion": round(100 * sum(s["assignments"]["on_time"] for s in subs) /
                                                   max(1, sum(s["assignments"]["total"] for s in subs)), 1),
                    "events_attended": int(np.clip(round(3 + 1.6 * engage), 0, 10)),
                    "club_member": int(RNG.random() < 0.35 + 0.1 * engage),
                    "hackathons": int(np.clip(round(1 + 0.8 * engage + RNG.normal(0, 1)), 0, 5)),
                    "certifications": int(np.clip(round(1.5 + 0.5 * engage + RNG.normal(0, 1)), 0, 5)),
                    "aptitude_score": round(float(np.clip(58 + 11 * ability + RNG.normal(0, 8), 15, 100)), 1),
                    "coding_score": round(float(np.clip(58 + 12 * ability + RNG.normal(0, 10), 10, 100)), 1),
                    "mock_interview_score": round(float(np.clip(60 + 8 * engage + RNG.normal(0, 10), 20, 100)), 1),
                    "tech_skill": round(float(np.clip(avg_cur + RNG.normal(0, 6), 10, 100)), 1),
                    "soft_skill": round(float(np.clip(62 + 8 * engage + RNG.normal(0, 8), 20, 100)), 1),
                    "satisfaction_1_5": round(float(np.clip(3.4 + 0.3 * engage + RNG.normal(0, 0.5), 1, 5)), 1),
                    "faculty_feedback_1_5": round(float(np.clip(3.3 + 0.35 * ability + RNG.normal(0, 0.5), 1, 5)), 1),
                })
                detailed.append({
                    "student_id": student_id, "name": name, "branch": branch,
                    "year": year, "section": sec, "roll_no": roll_no,
                    "cgpa": cgpa, "prev_cgpa": round(float(np.clip(avg_prev / 9.5, 4.0, 10.0)), 2),
                    "subjects": subs, "labs": labs,
                    "attendance": {"held": held_t, "attended": att_t,
                                   "absent": held_t - att_t, "pct": pct,
                                   "absent_dates": absent_dates(held_t - att_t)},
                })

pd.DataFrame(students).to_csv(OUT / "students_integrated.csv", index=False)
(OUT / "students_detailed.json").write_text(json.dumps(detailed))

# --- class timetables with timings + periods-per-week ---
timetables = {}
for branch in BRANCHES:
    for year in (1, 2, 3, 4):
        th, lb = subjects_for(year, branch)
        th_names = [n for _, n, _ in th]
        lb_names = [n for _, n, _ in lb]
        for si, sec in enumerate(SECTIONS):
            grid, k, ppw = {}, si * 2 + year, {}
            for d in DAYS:
                periods = []
                for p in range(6):
                    if p == 4 and d in ("Tue", "Thu", "Sat"):
                        c = lb_names[(k + len(periods)) % len(lb_names)] + " (Lab)"
                    else:
                        c = th_names[(k + p) % len(th_names)]
                    periods.append(c)
                    base = c.replace(" (Lab)", "")
                    ppw[base] = ppw.get(base, 0) + 1
                grid[d] = periods
                k += 1
            timetables[f"{branch}-{year}-{sec}"] = {"times": PERIOD_TIMES, "grid": grid,
                                                    "periods_per_week": ppw}
(OUT / "timetables.json").write_text(json.dumps(timetables))
print(f"v3: {len(detailed)} students ({len(BRANCHES)} branches x 4 years x {len(SECTIONS)} sections), {len(timetables)} timetables")
