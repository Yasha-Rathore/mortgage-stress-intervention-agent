# Lovable Prompt 1 — Base Layout

Paste this first. Wait for Lovable to render before moving on.

---

```
Build a dark-themed banking operations console called
"Early Stress Intervention Orchestrator". It's an internal tool
for an Australian bank's credit risk team monitoring a synthetic
mortgage portfolio.

LAYOUT
- Fixed left sidebar (240px wide) with the app name at top
- Five nav items with icons:
    Portfolio Health      (chart icon)
    Intervention Feed     (list icon)
    Escalation Queue      (alert icon)
    Weekly Report         (document icon)
    Live Demo             (play icon)
- Top header bar: title left "Mortgage Stress Intervention System
  — Prototype", small badge right reading
  "Synthetic data · 500 customers · AUS market"
- Main content area changes based on selected nav item

COLOURS (use exactly these)
- Background: #0D1117
- Card backgrounds: #161B22
- Borders: #30363D
- Text primary: #E6EDF3
- Text secondary: #8B949E
- Green (Low risk / success): #3FB950
- Amber (Moderate): #D29922
- Red (Severe / escalate): #F85149
- Blue (info): #58A6FF
- Purple (Call channel): #A371F7
- Teal (Email channel): #39D353

Font: Inter or system-ui sans-serif. Professional, dense,
information-rich like a Bloomberg terminal. No chat interface
anywhere. No emojis in the UI itself.

Connect to Supabase (already linked). Tables: customers,
interventions, weekly_signals, weekly_reports.

Make Portfolio Health the default landing page.
```
