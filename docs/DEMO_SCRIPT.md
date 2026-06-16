# Interview Demo Script

How to demo this project in a 5-minute interview slot. Tested wording
included for every step.

---

## The 30-second pitch (memorise this verbatim)

> *"I built an autonomous credit stress intervention agent that monitors a
> synthetic portfolio of 500 Australian mortgage customers. It identifies
> early stress signals — declining savings, high credit utilisation, late
> repayments — and autonomously decides whether to monitor, send a
> personalised email, place an outbound AI voice call, or escalate to a
> human relationship manager. After every interaction it extracts
> structured intelligence and updates the customer's risk profile. It runs
> weekly on GitHub Actions with zero human involvement. The entire stack
> is free."*

That's the answer to "tell me about a recent project." Anything more is
asked-for, not volunteered.

---

## The 5-minute structured demo

### Opening (30 sec)
Pull up the Lovable dashboard. Don't explain the system yet.

> *"Quick demo — this is the operations console a credit risk team would
> use. Let me walk you through it."*

### Portfolio Health (45 sec)
Land on Portfolio Health. Point at the stat cards.

> *"500 synthetic customers. The risk tiers use APRA's serviceability
> bands — over 30% of income to mortgage is moderate stress, over 45% is
> severe. About a third of this synthetic portfolio sits in severe right
> now, which actually matches what's happening in the real Australian
> market this year."*

Show the line chart trending up.

> *"Interventions have ramped from week 1 to week 8 because the
> simulated signals worsen over time — same as a real cohort would after
> a rate-rise cycle."*

### Intervention Feed (60 sec)
Click through. Show the channel badges.

> *"Every action the agent has taken in the last 8 weeks. Each card shows
> what the agent decided, why it decided it, and what happened. Email
> interventions, voice calls, escalations."*

Click an expandable "Agent reasoning" panel.

> *"This is the audit trail. The agent doesn't just decide — it explains.
> 'Severe stress band, savings declining 4 weeks, credit card maxed out.'
> Every decision in this system is auditable, which is the regulatory
> table-stakes for autonomous AI in banking."*

Click a CALL card and open the modal.

> *"Voice call. Here's the full transcript, and here's what the
> Summariser extracted — sentiment, the reasons the customer disclosed,
> whether they accepted an offer. This last bit is the most valuable
> output of the system. Banks currently can't get this at scale because
> it's manually coded by humans after every call. Doing it with an LLM
> unlocks portfolio-level analytics."*

### Escalation Queue (30 sec)
Show 2-3 escalations.

> *"These are the cases the agent decided needed a human. Each one comes
> with an agent-written briefing so the RM walks into the conversation
> already knowing the situation."*

### Weekly Report (30 sec)
Show the latest week.

> *"This memo is generated autonomously every Monday morning, no human
> authored it. CBA-style credit risk memo format. The data is computed
> deterministically from Supabase to avoid hallucination — only the
> language is LLM-generated."*

### Live Demo (90 sec) — THE MONEY MOMENT
Click Live Demo. Slide it over to the interviewer.

> *"Your turn. Build a customer however you want — push the sliders.
> Let's see what the agent does."*

Watch them drag sliders. Wait for them to click "Run Triage Agent."

When the triage decision appears, watch their face. If they go EMAIL,
click through and let them type a reply. If they go CALL, let them have a
chat with Maya.

After the Summariser runs:

> *"Every output you just saw is real model inference. Nothing scripted.
> The agent made all those decisions in front of you."*

### Close (15 sec)
> *"Whole thing runs on a free stack — Groq for the LLM, Supabase in
> Sydney, SendGrid, Vapi, Lovable, GitHub Actions. Total monthly cost is
> zero. The architecture is in the GitHub repo if you want to look later."*

---

## Common questions and the answers

**Q: How does this compare to what we already do?**
> "Where I'd guess banks are today — monthly batch flagging, manual
> outbound calls, generic scripts. Where this prototype lands — same-week
> intervention, personalised contact, structured conversation
> intelligence. The agentic part is the orchestration: deciding per-customer
> whether to email, call, or escalate based on reasoning over signals, not
> fixed rules."

**Q: What about regulatory and compliance?**
> "Three big considerations. One, the audit trail — every agent decision
> has a recorded reasoning chain. Two, content controls — the email
> prompts explicitly forbid promises and end with fixed CTAs. Three, human
> escalation — for the first 90 days in production I'd recommend every
> CALL action gets human approval before dialling. The agent does the
> triage, a human authorises the action."

**Q: How accurate is the LLM at triaging?**
> "On the synthetic data it routes about 70% of moderate-and-severe
> customers to MONITOR, 20% to EMAIL, 8% to CALL, 2% to ESCALATE. The
> distribution feels right but I don't have ground truth to measure
> accuracy formally. In production this would be A/B tested against a
> control cohort handled by the current process."

**Q: Why Groq specifically?**
> "Latency mostly. Llama 3.3 70B on Groq runs at 500+ tokens/second
> which means each triage decision returns in under a second.
> Cost-effective too — free tier covers 14,400 requests a day, easily
> enough for a 500-customer cohort. In production I'd add OpenAI as a
> fallback."

**Q: Did you build this in production?**
> "Production-equivalent. Real LLM calls, real Supabase database, real
> outbound emails via SendGrid, real Vapi voice integration. Customer
> data is synthetic and the Vapi free tier limits voice calls to US
> numbers, so for the demo voice interventions use Groq-generated mock
> transcripts processed by the real Summariser. Everything else is live."

**Q: How long did it take?**
> "About three weeks of evenings and weekends. The agents themselves
> took two days. The bulk of the time was the dashboard and the
> interactive demo page."

**Q: What would you do differently next time?**
> "Two things. First, build the dashboard before the agents — I built
> backend-first and ended up rebuilding parts of it. Second, add real
> outcome data into the loop. Right now the agent makes a decision but
> doesn't learn from whether the decision worked. Next iteration would
> feed intervention outcomes back into the Triage prompt as few-shot
> examples."

---

## What NOT to say

- Don't apologise for the synthetic data. It's a deliberate design choice.
- Don't apologise for the US Vapi number. Frame it as a free-tier
  constraint, not a flaw.
- Don't oversell. Banks know what's hard about this. Calibrated humility
  lands better than confidence.
- Don't mention Twilio, that didn't work for you, etc. Tell the clean
  story of what you ended up with.

---

## The follow-up email

Send 24 hours after the interview:

> Subject: Mortgage Stress Orchestrator — live link and code
>
> Hi [name],
>
> Thanks for the chat today. Three things to follow up on:
>
> 1. Live dashboard: [Lovable URL]
> 2. GitHub repo with full architecture: [GitHub URL]
> 3. 90-second walkthrough recording: [Loom URL]
>
> Happy to dig into any part of it in more detail. If it'd be useful, I'm
> also happy to spend 30 minutes mapping how this approach would specifically
> apply to [BANK NAME]'s home loan portfolio.
>
> Yashasvi
