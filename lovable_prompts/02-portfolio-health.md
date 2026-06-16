# Lovable Prompt 2 — Portfolio Health Page

```
Build out the Portfolio Health page (the default landing page).

TOP ROW — four large stat cards pulling from the Supabase
'customers' table, grouped by risk_tier:
1. Total Customers — count all rows
2. Severe Risk — count where risk_tier='Severe', red accent
3. Moderate Risk — count where risk_tier='Moderate', amber accent
4. Low Risk — count where risk_tier='Low', green accent

Each card: big number, label, and a small grey percentage of
total underneath.

MIDDLE ROW — two charts side by side:
- Left: line chart "Weekly Interventions" — count from
  'interventions' table grouped by week. X-axis: week number.
  Y-axis: count. Smooth line, green colour.
- Right: donut chart of risk tier split. Use green/amber/red
  colours matching the stat cards.

BOTTOM ROW — five smaller metric tiles:
- Autonomous Resolution Rate:
    count where outcome='resolved' / total interventions, as %
- Offer Acceptance Rate:
    count where offer_accepted != 'none' / total, as %
- Active Escalations:
    count where outcome='escalate_to_human'
- Emails Sent This Week:
    count where channel='email' for the most recent week
- Calls Placed This Week:
    count where channel='voice' for the most recent week

Auto-refresh data every 30 seconds.

Add a subtle "Live · auto-refreshing" indicator with a pulsing
green dot in the top right of the page.
```
