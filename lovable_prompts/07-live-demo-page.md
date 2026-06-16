# Lovable Prompt 7 — Live Demo Page

**⚠️ Before pasting:** Replace `[YOUR_RAILWAY_URL]` with your actual
Railway URL (e.g. `https://agent-backend-production-abc.up.railway.app`).

```
Build the Live Demo page — the interactive demo where the user
drives the agent themselves.

LAYOUT — two columns side by side, each ~50% width.

═══ LEFT COLUMN — "Build a Customer" panel ═══

Header: "Build a Customer Profile"
Subtext: "Adjust parameters below. The agent will assess in real time."

Form fields (vertical stack, each with current value shown):
- Name (text input, default "Sarah Chen")
- Annual income ($) — slider $45k–$250k, default $78k
- Loan balance ($) — slider $200k–$1.5M, default $620k
- Monthly repayment ($) — slider $1,500–$8,000, default $4,200
- Savings balance ($) — slider $0–$80k, default $8,400
- Credit card balance ($) — slider $0–$20k, default $7,200
- Credit card limit ($) — dropdown: 5000, 8000, 10000, 15000, 20000
- Days late on repayment — slider 0–14, default 3
- Irregular income — toggle switch, default ON

Below the form, a large button:
"▶ Run Triage Agent"

When clicked, POST the form data as JSON to:
[YOUR_RAILWAY_URL]/demo/triage

Show a loading spinner labelled "Agent reasoning..." while waiting.

═══ RIGHT COLUMN — "Agent Decision" panel ═══

Empty state:
"Configure a customer and click Run Triage Agent"

After triage completes, show:

1. Computed Metrics card:
   - Stress Ratio: large number (e.g. 0.52)
   - CC Utilisation: %
   - Risk Tier: coloured badge (Low/Moderate/Severe)

2. Triage Decision card with these fields:
   - Stress Assessment: pill badge
     (low/moderate/high/critical with matching colour)
   - Action: large coloured badge —
       MONITOR (grey)
       EMAIL (teal #39D353)
       CALL (purple #A371F7)
       ESCALATE (red #F85149)
   - Urgency: pill badge
   - Reasoning: full paragraph
   - Key Signals: bullet list
   - Action Rationale: italic grey paragraph

3. Conditional "Execute Action" button below the decision:
   - If action = EMAIL: button "✉ Draft Email"
   - If action = CALL: button "📞 Start Voice Conversation"
   - If action = ESCALATE: button "🚨 View RM Briefing"
   - If action = MONITOR: disabled, text "No action needed"

═══ EMAIL FLOW ═══
When "Draft Email" is clicked:
POST the customer data to [YOUR_RAILWAY_URL]/demo/draft-email

Display the generated email in a styled email-preview card:
- From: Maya Chen <maya@commbank.com.au>
- To: [customer first name] <demo@example.com>
- Subject: [from response]
- Body: [from response, paragraphs]

Below the email, add:
- Header: "Simulate Customer Reply"
- A textarea where the user can type a reply
  Placeholder: "Type what the customer would reply..."
- Button "📊 Run Summariser"

When the button is clicked, POST to
[YOUR_RAILWAY_URL]/demo/summarise-email with:
{
  customer_name, risk_tier,
  email_subject, email_body, customer_reply
}

Display the response in a structured "Extracted Intelligence"
card showing:
  Sentiment, Engaged, Reasons Disclosed, Offer Accepted,
  Outcome, Next Action

═══ CALL FLOW ═══
When "Start Voice Conversation" is clicked:
Open a chat-style interface inline on the right column.

First, POST to [YOUR_RAILWAY_URL]/demo/voice-turn with:
{
  customer_name, risk_tier,
  customer_message: "",
  conversation_history: []
}
to get Maya's opening line. Display as a Maya bubble.

Then a chat input at the bottom where the user types a
"customer response." On submit:
- Add the user's message as a customer bubble
- POST again to /demo/voice-turn with updated history
- Display Maya's response as another bubble

After 3+ exchanges OR a "End Call & Summarise" button is clicked:
- POST the full conversation to /demo/summarise with:
  {
    customer_name, risk_tier,
    conversation: [{role: 'maya'/'customer', text: ...}, ...]
  }
- Display the extracted intelligence card

Maya bubbles: teal #39D353 tinted, left-aligned
Customer bubbles: grey #21262D, right-aligned

═══ ESCALATE FLOW ═══
When "View RM Briefing" is clicked:
Display a red-bordered card with the action_rationale from
the triage response, labelled "Briefing for Relationship Manager".

═══ STYLING ═══
Match the rest of the app — dark theme, same colour palette.
Add a subtle "Powered by Groq Llama 3.3 70B" footnote under
each agent response.

The Railway URL throughout: [YOUR_RAILWAY_URL]
```
