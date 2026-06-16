# Lovable Prompt 5 — Escalation Queue Page

```
Build the Escalation Queue page.

Show cards for every row in 'interventions' where
outcome = 'escalate_to_human', ordered by created_at descending.

Each card:
- Red left border (4px wide, colour #F85149)
- Header: customer_id and customer name (large)
- Week number and relative timestamp on the right
- A "Needs RM Attention" badge — red background, white bold text
- The full rm_briefing text rendered as a readable paragraph
- Two action buttons at the bottom:
    "Mark Reviewed" — grey, secondary
    "Assign to RM"  — green primary

ABOVE the card list, three small filter stats:
- Total pending escalations (count)
- New this week (count where week = current)
- Oldest pending (days since created_at)

EMPTY STATE — when there are no escalations:
Centred green checkmark icon
Large text: "No active escalations"
Below in muted grey:
"The agent resolved all flagged cases autonomously this week."
```
