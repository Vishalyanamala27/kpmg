# Student Success Score — Methodology Note

## 1. What the score is
A transparent **0–100 weighted composite** over 7 normalised pillars. Every student's
score decomposes exactly into pillar contributions (`weight × sub-score`), so any
score can be explained without black-box ML — a deliberate choice for faculty trust.

## 2. Indicators & normalisation (all mapped to 0–100)
| Pillar (weight) | Inputs & combination |
|---|---|
| Academics **30%** | CGPA normalised `(cgpa−4.5)/5.5×100` (55%) + avg marks (25%) + backlog penalty `100 − 22×backlogs` (20%) |
| Attendance **15%** | Overall attendance % directly |
| LMS Activity **15%** | Logins/month ÷25×100 (45%) + assignment completion % (55%) |
| Placement Readiness **15%** | Aptitude (35%) + coding (40%) + mock interviews (25%) |
| Engagement **10%** | Events÷8 (35%) + club membership (15%) + hackathons÷3 (25%) + certifications÷4 (25%) |
| Skills **10%** | Technical (60%) + soft skills (40%) |
| Feedback **5%** | Satisfaction (50%) + faculty feedback (50%), 1–5 → 0–100 |

`Success Score = Σ weight × sub-score` → e.g. Academics 70 contributes `0.30×70 = 21.0 pts`.

## 3. Risk identification (two lenses + escalation)
- **Academic-risk points:** CGPA<6.0, backlogs≥2, attendance<55%, assignments<45%, academic sub<45.
- **Placement-risk points:** aptitude<45, coding<45, mock<45, placement sub<45.
- Mapping: **Critical** = 3+ points or sub<30; **At-Risk** = 2 points or sub<45; **Watch** = 1 point or sub<55; else **Safe**.
- **Overall risk** = worse of the two lenses; escalated to At-Risk if score<45, Critical if score<32.
- Current cohort (n=500, mean 58.4): Safe 192 · Watch 153 · At-Risk 67 · Critical 88 → **~31% need intervention**.

## 4. Segmentation (rule-based, action-linked)
- **All-Round Stars** (≥75, n=32) → peer mentors, advanced projects.
- **Academic Strong, Placement-Weak** (n=15) → highest-ROI bootcamp target.
- **Placement-Ready Grinders** (n=36) → remedial academics, protect placement edge.
- **Disengaged Potentials** (n=118) → clubs, certifications, hackathons.
- **Steady Climbers** (n=167) → maintain with light-touch nudges.
- **At-Risk Strugglers** (n=132) → counsellor + structured plan within 7 days.

## 5. Limitations & next steps
Synthetic demo data; weights are expert-set, not fitted. With real longitudinal data:
fit weights via logistic regression on graduation/placement outcomes, validate with
cross-validation, add trend (attendance delta) and early-semester prediction.
