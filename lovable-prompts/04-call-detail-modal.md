# Lovable Prompt 4 — Call Detail Modal

```
For every CALL channel card in the Intervention Feed,
the "View call detail ↗" link in the bottom-right opens a
modal dialog (close on Escape or click outside).

MODAL LAYOUT — dark theme matching the rest of the app,
720px wide, centred with backdrop blur:

HEADER:
- Customer name (large) and customer_id (small grey)
- Week number underneath
- Close X in top right

SUBHEADER STRIP:
"Voice Intervention · Maya · CommBank"
followed by a metadata row:
Duration "~2 min" · Status "Completed" · Processed [timestamp]

SECTION 1 — "Call Recording"
A play button labelled "▶ Listen to call" with a static audio
waveform graphic below it. No real audio playback.
Subtitle: "Recording available for compliance review"

SECTION 2 — "Conversation Transcript"
Render as a chat thread between "Maya (CommBank)" and the
customer's first name. Generate a 4-6 turn realistic
conversation using the new_risk_signals and triage_reasoning
fields as context (use generic placeholder if missing).

Bubble styling:
- Maya bubbles: left-aligned, teal #39D353 tinted background
- Customer bubbles: right-aligned, grey #21262D background
- Show timestamps next to each message

SECTION 3 — "Agent Extracted Intelligence"
Render as a two-column key/value table:
  Sentiment:           [sentiment field]
  Engagement Level:    derived (high if engaged=true)
  Reasons Disclosed:   [new_risk_signals as comma list]
  Offer Made:          derived from triage_reasoning context
  Offer Accepted:      [offer_accepted field]
  Outcome:             [outcome field]
  Recommended Next:    [rm_briefing or default text]

FOOTER STRIP (muted grey):
"Processed by Summariser sub-agent · Groq Llama 3.3 70B ·
1.2s latency · Customer risk profile auto-updated"
```
