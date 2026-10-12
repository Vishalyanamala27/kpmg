"""Student Success Score + Risk + Segmentation + Explainability.
Deterministic, documented, no ML library needed (transparent weighted model).
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path

BASE = Path(__file__).parent
DF = pd.read_csv(BASE / "data" / "students_integrated.csv")

# ---- Normalisation helpers (all -> 0..100) ----
def norm_cgpa(x): return ((x - 4.5) / (10 - 4.5) * 100).clip(0, 100)
def backlog_penalty(b): return (100 - b * 22).clip(0, 100)  # 0 bl=100, 2 bl=56, 4+=12
def norm_logins(x): return ((x / 25) * 100).clip(0, 100)
def norm_events(x): return ((x / 8) * 100).clip(0, 100)
def norm_certs(x): return ((x / 4) * 100).clip(0, 100)
def norm_hack(x): return ((x / 3) * 100).clip(0, 100)
def norm_1_5(x): return ((x - 1) / 4 * 100).clip(0, 100)

# ---- Sub-scores (0..100) ----
df = DF.copy()
df["academic_sub"] = (0.55 * norm_cgpa(df["cgpa"]) + 0.25 * df["avg_marks"] + 0.20 * backlog_penalty(df["backlogs"])).round(1)
df["attendance_sub"] = df["attendance_pct"]
df["lms_sub"] = (0.45 * norm_logins(df["lms_logins_pm"]) + 0.55 * df["assignment_completion"]).round(1)
df["engagement_sub"] = (0.35 * norm_events(df["events_attended"]) + 0.15 * df["club_member"] * 100
                        + 0.25 * norm_hack(df["hackathons"]) + 0.25 * norm_certs(df["certifications"])).round(1)
df["placement_sub"] = (0.35 * df["aptitude_score"] + 0.40 * df["coding_score"] + 0.25 * df["mock_interview_score"]).round(1)
df["skills_sub"] = (0.6 * df["tech_skill"] + 0.4 * df["soft_skill"]).round(1)
df["feedback_sub"] = (0.5 * norm_1_5(df["satisfaction_1_5"]) + 0.5 * norm_1_5(df["faculty_feedback_1_5"])).round(1)

# ---- Final Success Score weights (documented) ----
W = {"academic_sub": 0.30, "attendance_sub": 0.15, "lms_sub": 0.15,
     "engagement_sub": 0.10, "placement_sub": 0.15, "skills_sub": 0.10, "feedback_sub": 0.05}
df["success_score"] = sum(df[k] * w for k, w in W.items()).round(1)

# ---- Risk flags ----
academic_risk_pts = ((df["cgpa"] < 6.0).astype(int) + (df["backlogs"] >= 2).astype(int)
                     + (df["attendance_pct"] < 55).astype(int) + (df["assignment_completion"] < 45).astype(int)
                     + (df["academic_sub"] < 45).astype(int))
placement_risk_pts = ((df["aptitude_score"] < 45).astype(int) + (df["coding_score"] < 45).astype(int)
                      + (df["mock_interview_score"] < 45).astype(int) + (df["placement_sub"] < 45).astype(int))

def acad_label(p, sub):
    if p >= 3 or sub < 30: return "Critical"
    if p == 2 or sub < 45: return "At-Risk"
    if p == 1 or sub < 55: return "Watch"
    return "Safe"
def place_label(p, sub):
    if p >= 3 or sub < 30: return "Critical"
    if p == 2 or sub < 45: return "At-Risk"
    if p == 1 or sub < 55: return "Watch"
    return "Safe"

df["academic_risk"] = [acad_label(p, s) for p, s in zip(academic_risk_pts, df["academic_sub"])]
df["placement_risk"] = [place_label(p, s) for p, s in zip(placement_risk_pts, df["placement_sub"])]

order = {"Safe": 0, "Watch": 1, "At-Risk": 2, "Critical": 3}
overall = [max(a, b, key=lambda x: order[x]) for a, b in zip(df["academic_risk"], df["placement_risk"])]
# low success score escalates
overall = ["At-Risk" if (s < 45 and order[o] < 2) else ("Critical" if s < 32 else o) for s, o in zip(df["success_score"], overall)]
df["overall_risk"] = overall

# ---- Segmentation (rule-based, actionable) ----
def segment(r):
    if r["success_score"] >= 75: return "All-Round Stars"
    if r["academic_sub"] >= 65 and r["placement_sub"] < 55: return "Academic Strong, Placement-Weak"
    if r["academic_sub"] < 55 and r["placement_sub"] >= 60: return "Placement-Ready Grinders"
    if r["engagement_sub"] < 35 and r["academic_sub"] >= 55: return "Disengaged Potentials"
    if r["overall_risk"] in ("At-Risk", "Critical"): return "At-Risk Strugglers"
    return "Steady Climbers"
df["segment"] = df.apply(segment, axis=1)

# ---- Explainability: weighted contributions (points of 100) ----
SUB_LABELS = {"academic_sub": "Academics (30%)", "attendance_sub": "Attendance (15%)",
              "lms_sub": "LMS Activity (15%)", "engagement_sub": "Engagement (10%)",
              "placement_sub": "Placement Readiness (15%)", "skills_sub": "Skills (10%)",
              "feedback_sub": "Feedback (5%)"}
contrib_cols = {}
for k, w in W.items():
    df[f"contrib_{k}"] = (df[k] * w).round(1)

def top_drivers(r, n=3):
    items = sorted(((SUB_LABELS[k], r[f"contrib_{k}"], r[k]) for k in W), key=lambda x: -x[1])[:n]
    return [{"factor": k, "points": float(p), "subscore": float(s)} for k, p, s in items]

def risk_factors(r):
    f = []
    if r["cgpa"] < 6.5: f.append(f"Low CGPA ({r['cgpa']})")
    if r["backlogs"] >= 2: f.append(f"{int(r['backlogs'])} active backlogs")
    if r["attendance_pct"] < 60: f.append(f"Low attendance ({r['attendance_pct']}%)")
    if r["assignment_completion"] < 50: f.append(f"Low assignment completion ({r['assignment_completion']}%)")
    if r["aptitude_score"] < 50: f.append(f"Weak aptitude ({r['aptitude_score']})")
    if r["coding_score"] < 50: f.append(f"Weak coding ({r['coding_score']})")
    if r["mock_interview_score"] < 50: f.append(f"Weak interviews ({r['mock_interview_score']})")
    if r["engagement_sub"] < 35: f.append("Low campus engagement")
    return f[:4]

def recommend(r):
    rec = []
    if r["backlogs"] >= 1 or r["cgpa"] < 6.5: rec.append("Assign remedial tutoring + backlog clearance plan")
    if r["attendance_pct"] < 65: rec.append("Counsellor check-in: attendance mentorship")
    if r["assignment_completion"] < 60: rec.append("LMS nudge: weekly assignment reminders")
    if r["coding_score"] < 55 or r["aptitude_score"] < 55: rec.append("Enrol in placement bootcamp (aptitude + coding)")
    if r["mock_interview_score"] < 55: rec.append("Schedule 2 mock interviews with feedback")
    if r["engagement_sub"] < 35: rec.append("Recommend 1 club + 1 certification to boost engagement")
    if not rec: rec.append("Nominate for peer-mentor / advanced projects")
    return rec[:3]

df["top_drivers"] = df.apply(lambda r: json.dumps(top_drivers(r)), axis=1)
df["risk_factors"] = df.apply(lambda r: json.dumps(risk_factors(r)), axis=1)
df["recommendations"] = df.apply(lambda r: json.dumps(recommend(r)), axis=1)

df.to_csv(BASE / "data" / "students_scored.csv", index=False)

summary = {
    "n": len(df),
    "mean_score": round(df.success_score.mean(), 1),
    "risk_counts": df.overall_risk.value_counts().to_dict(),
    "segment_counts": df.segment.value_counts().to_dict(),
    "dept_mean": df.groupby("dept").success_score.mean().round(1).to_dict(),
    "weights": {SUB_LABELS[k]: v for k, v in W.items()},
}
(BASE / "data" / "insights.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
print("Saved data/students_scored.csv")
