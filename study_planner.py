"""Study planner: per-student gap analysis, improvement feed, weekly study
timetable. Merges detailed records + success scores into dashboard/data.js
(window.STUDENTS detailed, window.TIMETABLES class schedules).
"""
import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
detailed = json.loads((BASE / "data" / "students_detailed.json").read_text())
timetables = json.loads((BASE / "data" / "timetables.json").read_text())
scored = pd.read_csv(BASE / "data" / "students_scored.csv").set_index("student_id").to_dict("index")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SLOTS = ["5:00 - 7:00 PM", "7:30 - 9:30 PM"]
WEEK_HRS = 12


def plan_student(d):
    subs = sorted(d["subjects"], key=lambda s: s["current"])
    weak = [s for s in subs if s["current"] < 60][:2] or subs[:1]
    strong = sorted(d["subjects"], key=lambda s: -s["current"])[:2]
    gap = round(strong[0]["current"] - weak[0]["current"], 0)

    # hour allocation: weak subjects get the lion's share
    alloc, rest = {}, [s["name"] for s in subs if s not in weak]
    each_weak = round(WEEK_HRS * 0.55 / len(weak), 1)
    for s in weak:
        alloc[s["name"]] = each_weak
    each_rest = round(WEEK_HRS * 0.30 / max(1, len(rest)), 1)
    for name in rest:
        alloc[name] = each_rest
    alloc["Revision + previous papers"] = round(WEEK_HRS - sum(alloc.values()), 1)

    # weekly timetable: weak subjects appear 2x, Sunday = revision + rest
    rotation = [w["name"] for w in weak] * 2 + rest + ["Revision"]
    table, i = {}, 0
    for day in DAYS:
        table[day] = [rotation[i % len(rotation)], rotation[(i + 1) % len(rotation)]]
        i += 2

    tips = [
        f"Shift ~{each_weak} hrs/week to {weak[0]['name']} (currently {weak[0]['current']:.0f}) "
        f"using solved examples + previous papers; protect {strong[0]['name']} ({strong[0]['current']:.0f}) with 1 revision slot.",
    ]
    pending = [l["name"] for l in d["labs"] if l["record"] == "pending"]
    if pending:
        tips.append(f"Finish pending {', '.join(pending)} record(s) by Friday — records carry internal marks.")
    if d["attendance"]["pct"] < 75:
        tips.append(f"Attendance {d['attendance']['pct']}% ({d['attendance']['absent']} absents) is below 75% — "
                    "attend the next 10 classes in a row to rebuild the buffer.")
    for s in subs:
        if s["assignments"]["pending"]:
            tips.append(f"{s['assignments']['pending']} {s['name']} assignment(s) still pending — submit before the lab hour.")
            break
    summary = (f"{d['name']} scored {strong[0]['current']:.0f} in {strong[0]['name']} but "
               f"{weak[0]['current']:.0f} in {weak[0]['name']} — a {gap:.0f}-mark gap. "
               f"Moving ~{each_weak} hrs/week into {weak[0]['name']} problem practice can lift it past 60 in 3 weeks.")
    return {"summary": summary, "weak": [w["name"] for w in weak],
            "strong": [s["name"] for s in strong], "hours": alloc,
            "timetable": table, "tips": tips[:4]}


def improvements(d):
    """Improvement feed: marks deltas, record timeliness, attendance, CGPA."""
    feed = []
    subs = sorted(d["subjects"], key=lambda s: s["current"] - s["previous"], reverse=True)
    best, worst = subs[0], subs[-1]
    if best["current"] - best["previous"] >= 1:
        feed.append({"tone": "good",
                     "text": f"+{best['current'] - best['previous']:.0f} marks in {best['name']} vs last test ({best['previous']:.0f} to {best['current']:.0f})"})
    if worst["current"] - worst["previous"] <= -5:
        feed.append({"tone": "warn",
                     "text": f"{worst['current'] - worst['previous']:.0f} marks in {worst['name']} vs last test — flagged in this week's plan"})
    for lab in d["labs"]:
        dv = lab["days_vs_last"]
        if lab["record"] == "on_time" and dv <= 0:
            feed.append({"tone": "good",
                         "text": f"{lab['name']} record submitted on time ({abs(dv)} day(s) earlier than last time)"})
        elif lab["record"] == "on_time":
            feed.append({"tone": "good", "text": f"{lab['name']} record submitted on time"})
        elif lab["record"] == "late":
            feed.append({"tone": "warn", "text": f"{lab['name']} record submitted late — target on-time next cycle"})
        else:
            feed.append({"tone": "warn", "text": f"{lab['name']} record still pending"})
    ot = sum(s["assignments"]["on_time"] for s in d["subjects"])
    tot = sum(s["assignments"]["total"] for s in d["subjects"])
    feed.append({"tone": "good" if ot / tot >= 0.7 else "warn",
                 "text": f"Assignments: {ot}/{tot} on time ({100 * ot / tot:.0f}%)"})
    att = d["attendance"]
    feed.append({"tone": "good" if att["pct"] >= 75 else "warn",
                 "text": f"Attendance {att['pct']}% — {att['absent']} absent(s) of {att['held']} classes this semester"})
    delta = round(d["cgpa"] - d["prev_cgpa"], 2)
    feed.append({"tone": "good" if delta >= 0 else "warn",
                 "text": f"CGPA {d['cgpa']} ({'+' if delta >= 0 else ''}{delta} vs last semester)"})
    return feed


out = []
for d in detailed:
    s = scored.get(d["student_id"], {})
    d["success_score"] = round(float(s.get("success_score", 0)), 1)
    d["overall_risk"] = s.get("overall_risk", "Watch")
    d["skills"] = {"tech": s.get("tech_skill"), "soft": s.get("soft_skill"),
                   "aptitude": s.get("aptitude_score"), "coding": s.get("coding_score"),
                   "mock": s.get("mock_interview_score")}
    d["plan"] = plan_student(d)
    d["feed"] = improvements(d)
    out.append(d)

out.sort(key=lambda d: (d["year"], d["section"], d["roll_no"]))
js = ("window.STUDENTS = " + json.dumps(out) + ";\n"
      "window.TIMETABLES = " + json.dumps(timetables) + ";\n")
(BASE / "dashboard" / "data.js").write_text(js)
print(f"planner: {len(out)} students + {len(timetables)} timetables -> dashboard/data.js ({len(js)//1024} KB)")
wk = [s for s in out if s["overall_risk"] in ("At-Risk", "Critical")]
print(f"at-risk/critical: {len(wk)} | avg CGPA: {sum(s['cgpa'] for s in out)/len(out):.2f}")
