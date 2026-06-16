# Lovable Prompt 3 — Intervention Feed Page

```
Build the Intervention Feed page.

Show a scrollable vertical list of cards from the Supabase
'interventions' table, ordered by created_at descending,
limited to 20 most recent.

EACH CARD layout:
- Top row:
    customer_id on left (font-mono, e.g. "CBA-00247")
    week number next to it
    relative timestamp on right (e.g. "2 hours ago")
- Channel badge on top-right of card:
    EMAIL  = teal #39D353 background, white bold text
    CALL   = purple #A371F7 background
    ESCALATE = red #F85149 background
- Outcome badge below channel badge:
    pending = grey
    resolved = green
    follow_up = amber
    escalate_to_human = red
- For EMAIL channel cards:
    show the email_subject in italic grey text below the badges
- For CALL channel cards:
    show two small pill tags next to each other:
      one with sentiment value (e.g. "concerned")
      one with offer_accepted value (e.g. "repayment_pause")
- One line of triage_reasoning in muted grey text underneath

EXPANDER — bottom of each card has an
"Agent reasoning ▸" expandable section that reveals a
dark terminal-style panel inside the card showing:
- Full triage_reasoning text
- For CALL: new_risk_signals array as bullet list
- For EMAIL: full email_body
- For ESCALATE: full rm_briefing

For CALL cards specifically, also add a
"View call detail ↗" link in the bottom-right corner that
opens a modal (built in the next prompt).

ABOVE THE LIST:
- A search input filtering cards by customer_id substring
- Filter buttons: All | Email | Call | Escalate

Each card has a subtle hover state — 1px brighter border.
```
