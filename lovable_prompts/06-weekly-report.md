# Lovable Prompt 6 — Weekly Report Page

```
Build the Weekly Report page.

At the top, fetch the most recent row from the Supabase
'weekly_reports' table (highest week number).

PAGE HEADER:
"Week [N] Executive Briefing"
Small label underneath in italic muted grey:
"Autonomous Report — generated Monday 9am AEST ·
No human authored this"

STAT TILES ROW — 5 tiles:
- Total Interventions: total_interventions
- Resolved Autonomously: resolved
- Escalated to Human: escalated
- Email Interventions:
    count from interventions table where channel='email'
    AND week = this row's week
- Acceptance Rate: acceptance_rate as %

MAIN CONTENT SECTION:
Render the report_text field as formatted paragraphs with
generous line spacing (line-height 1.8). Use a serif font here
(Georgia, Garamond, or similar) to make it feel like a real
executive memo. Add subtle paragraph numbers (1, 2, 3) in the
margin.

TOP RIGHT of report section:
"Download as PDF" button (no actual PDF generation — just
a styled button for now).

ABOVE THE REPORT:
"Past Reports" dropdown listing all weeks present in
weekly_reports table. Switching weeks reloads the data and
report_text.

FOOTER STRIP (muted grey at bottom):
"Sources: Supabase · Groq Llama 3.3 70B · SendGrid · Vapi.ai ·
GitHub Actions · Generated [generated_at formatted as
'9 Jun 2025, 9:03 AEST']"
```
