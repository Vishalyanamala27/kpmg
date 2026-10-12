"""Synthetic multi-source student data generator.
Simulates 7 disconnected campus systems, then integrates them.
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N = 500
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

depts = ["CSE", "ECE", "ME", "BBA"]
years = [1, 2, 3, 4]
students = [f"STU{str(i+1).zfill(3)}" for i in range(N)]
names_pool = ["Aarav","Diya","Arjun","Ananya","Vivaan","Ishita","Kabir","Meera","Rohan","Sneha",
              "Aditya","Priya","Karan","Neha","Rahul","Pooja","Sahil","Riya","Manav","Tanvi"]
surnames = ["Sharma","Patel","Reddy","Iyer","Khan","Gupta","Nair","Singh","Das","Kulkarni"]

def pick_name(rng):
    return f"{rng.choice(names_pool)} {rng.choice(surnames)}"

dept = RNG.choice(depts, N, p=[0.4, 0.25, 0.2, 0.15])
year = RNG.choice(years, N, p=[0.25, 0.25, 0.25, 0.25])
# latent ability drives correlations (realistic)
ability = RNG.normal(0, 1, N)
engagement_trait = RNG.normal(0, 1, N)

# --- Academic system ---
cgpa = np.clip(7.0 + 1.1 * ability + RNG.normal(0, 0.5, N), 4.5, 10.0).round(2)
avg_marks = np.clip(cgpa * 9.2 + RNG.normal(0, 3, N), 30, 98).round(1)
backlogs = np.array([RNG.poisson(max(0.1, 1.6 - 0.55 * (c - 6))) if c < 8 else (1 if RNG.random() < 0.06 else 0) for c in cgpa])
backlogs = np.clip(backlogs, 0, 5)

# --- Attendance system ---
attendance = np.clip(72 + 8 * ability + 4 * engagement_trait + RNG.normal(0, 8, N), 28, 99).round(1)

# --- LMS system ---
lms_logins_pm = np.clip(np.round(14 + 4 * engagement_trait + 2 * ability + RNG.normal(0, 4, N)), 1, 32).astype(int)
assign_completion = np.clip(70 + 9 * ability + 5 * engagement_trait + RNG.normal(0, 9, N), 15, 100).round(1)

# --- Engagement system ---
events = np.clip(np.round(np.maximum(0, 3 + 1.6 * engagement_trait + RNG.normal(0, 1.5, N))), 0, 12).astype(int)
clubs = (RNG.random(N) < (0.35 + 0.15 * engagement_trait.clip(-1, 2))).astype(int)
hackathons = np.clip(np.round(np.maximum(0, 1 + 0.8 * engagement_trait + RNG.normal(0, 1, N))), 0, 6).astype(int)
certs = np.clip(np.round(np.maximum(0, 1.5 + 0.7 * (ability + engagement_trait) / 2 + RNG.normal(0, 1, N))), 0, 6).astype(int)

# --- Placement cell ---
aptitude = np.clip(58 + 11 * ability + RNG.normal(0, 8, N), 15, 100).round(1)
coding = np.clip(55 + 12 * ability + (dept == "CSE") * 6 + RNG.normal(0, 10, N), 10, 100).round(1)
mock_interviews = np.clip(60 + 8 * engagement_trait + 4 * ability + RNG.normal(0, 10, N), 20, 100).round(1)

# --- Skills assessments ---
tech_skill = np.clip(0.6 * coding + 0.4 * avg_marks + RNG.normal(0, 6, N), 10, 100).round(1)
soft_skill = np.clip(62 + 8 * engagement_trait + RNG.normal(0, 8, N), 20, 100).round(1)

# --- Feedback system ---
satisfaction = np.clip(np.round(3.4 + 0.3 * engagement_trait + RNG.normal(0, 0.6, N), 1), 1, 5)
faculty_feedback = np.clip(np.round(3.3 + 0.35 * ability + RNG.normal(0, 0.6, N), 1), 1, 5)

df = pd.DataFrame({
    "student_id": students,
    "name": [pick_name(RNG) for _ in range(N)],
    "dept": dept, "year": year,
    "cgpa": cgpa, "avg_marks": avg_marks, "backlogs": backlogs,
    "attendance_pct": attendance,
    "lms_logins_pm": lms_logins_pm, "assignment_completion": assign_completion,
    "events_attended": events, "club_member": clubs, "hackathons": hackathons, "certifications": certs,
    "aptitude_score": aptitude, "coding_score": coding, "mock_interview_score": mock_interviews,
    "tech_skill": tech_skill, "soft_skill": soft_skill,
    "satisfaction_1_5": satisfaction, "faculty_feedback_1_5": faculty_feedback,
})

# Simulate messy disconnected sources: save per-source raw files too
df[["student_id","cgpa","avg_marks","backlogs"]].to_csv(OUT / "raw_academic.csv", index=False)
df[["student_id","attendance_pct"]].to_csv(OUT / "raw_attendance.csv", index=False)
df[["student_id","lms_logins_pm","assignment_completion"]].to_csv(OUT / "raw_lms.csv", index=False)
df[["student_id","events_attended","club_member","hackathons","certifications"]].to_csv(OUT / "raw_engagement.csv", index=False)
df[["student_id","aptitude_score","coding_score","mock_interview_score"]].to_csv(OUT / "raw_placement.csv", index=False)
df[["student_id","tech_skill","soft_skill"]].to_csv(OUT / "raw_skills.csv", index=False)
df[["student_id","satisfaction_1_5","faculty_feedback_1_5"]].to_csv(OUT / "raw_feedback.csv", index=False)
df.to_csv(OUT / "students_integrated.csv", index=False)
print(f"Generated {len(df)} students -> data/students_integrated.csv + 7 raw source files")
print(df.describe().round(2).to_string())
