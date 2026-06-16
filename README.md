# Early Stress Intervention Orchestrator

> **An autonomous multi-agent system that monitors a synthetic portfolio of
> 500 Australian mortgage customers, identifies early stress signals, runs
> outbound email and AI voice interventions without human involvement,
> extracts structured intelligence from every conversation, and publishes
> weekly executive credit-risk reports.**
>
> Built end-to-end on a free stack. Designed as a prototype of what
> Australian banks are actively building with agentic AI today.

[![Made with Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3%2070B-orange)](https://groq.com)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20Sydney-3FCF8E)](https://supabase.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![Lovable](https://img.shields.io/badge/Frontend-Lovable-7C3AED)](https://lovable.dev)
[![Cost](https://img.shields.io/badge/Infra%20Cost-%240-3FB950)](#stack)

---

## The problem

Australian banks hold roughly **$2.2 trillion in home loans**. Their biggest
operational pain point is not knowing *which* customers are stressed — internal
data shows that. The pain is **what to do about it at scale and how fast**.

When a customer is showing early stress signals (declining savings, rising
credit card utilisation, late repayments, irregular income), the bank has
roughly a **6–12 week window** to intervene before the case escalates into
formal hardship. Hardship cases cost **$3,000–8,000 each** to manage. Loan
defaults are catastrophic.

The current process is monthly batch flagging followed by manual outbound
calls from human collections teams using generic scripts. It is slow,
inconsistent, and the interventions are not personalised.

**This system prototypes the autonomous alternative.**

---

## What it does

Every Monday at 9am AEST, GitHub Actions wakes the system. It:

1. **Reads** all 500 synthetic customers and the last 8 weeks of their
   behavioural signals from Supabase.
2. **Triages** each moderate-or-severe risk customer through the Triage Agent
   (Groq Llama 3.3 70B), which reasons over six signal types and decides
   between four actions: `MONITOR`, `EMAIL`, `CALL`, `ESCALATE`.
3. **Acts** autonomously based on that decision:
   - `EMAIL` → drafts a warm personalised email and sends it via SendGrid
   - `CALL` → places an outbound AI voice call via Vapi.ai
   - `ESCALATE` → writes a one-paragraph briefing for a human RM
4. **Summarises** every reply and call transcript through the Summariser
   Agent, extracting sentiment, reasons disclosed, offers accepted, and new
   risk signals — then updates the customer's risk profile.
5. **Reports** by generating an autonomous executive credit-risk memo in CBA
   style, posted to the dashboard and available to subscribers.

A Lovable dashboard renders all of this live, with a Live Demo page that
lets anyone build a customer profile and run the full agent loop interactively.

---

## Architecture

```
                    GitHub Actions (cron — Mondays 9am AEST)
                                    │
                                    ▼
                            Orchestrator (scheduler.py)
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
         Supabase (Sydney)              Triage Agent (Groq LLM)
         · customers                   reasons over signals,
         · weekly_signals              returns structured JSON
         · interventions                       │
         · weekly_reports          ┌───────────┴───────────────┐
                                   │           │               │
                                  EMAIL       CALL          ESCALATE
                                   │           │               │
                                   ▼           ▼               ▼
                              SendGrid     Vapi.ai          RM queue
                                   │           │
                                   ▼           ▼
                            Customer    Customer  ← outbound
                            replies     converses
                                   │           │
                                   ▼           ▼
                              Summariser Agent (Groq LLM)
                              extracts structured intelligence
                                          │
                                          ▼
                                  Supabase update
                                          │
                                          ▼
                              Reporter Agent (Groq LLM)
                              weekly executive memo
                                          │
                                          ▼
                                Lovable dashboard
                                · Portfolio Health
                                · Intervention Feed
                                · Escalation Queue
                                · Weekly Report
                                · Live Demo (you drive it)
```

---

## The Live Demo page

The Lovable dashboard includes an interactive Live Demo where the viewer can:

1. **Build a customer** using sliders (income, loan size, savings, late days,
   irregular income, etc).
2. **Run the Triage Agent** and watch the reasoning, stress assessment, and
   decided action populate live.
3. **Trigger the chosen channel** —
   - For email: see the generated email, type a reply, watch the Summariser
     extract structured intelligence
   - For voice: hold a live chat-style conversation with Maya, end it, and
     watch the Summariser run on the full transcript
4. **See the agent's decision logic** appear step by step — no scripted demo,
   real model output every time.

This is the most-engaged moment in any interview demo of this project.

---

## Stack

Everything used here is free. Total infrastructure cost: **$0**.

| Component                  | Tool                    | Free tier                  |
|---------------------------|-------------------------|----------------------------|
| Data notebooks             | Google Colab            | Unlimited                  |
| LLM (all 4 agents)         | Groq (Llama 3.3 70B)    | 14,400 requests / day      |
| Transcription              | Groq Whisper large-v3   | Included                   |
| Database                   | Supabase (ap-southeast-2) | 500 MB, 2 free projects  |
| Backend webhooks + demo    | FastAPI on Railway      | $5 starter credit          |
| Email outreach             | SendGrid                | 100 emails / day forever   |
| AI voice calls             | Vapi.ai                 | $10 trial credit           |
| Dashboard                  | Lovable                 | Public projects free       |
| Scheduling                 | GitHub Actions          | 2,000 minutes / month      |
| Demo recording             | Loom                    | 25 videos free             |

---

## Repository layout

```
mortgage-stress-intervention-agent/
├── README.md                      ← you are here
├── main.py                        ← FastAPI backend (Vapi webhook + demo endpoints)
├── requirements.txt
├── Procfile                       ← Railway start command
├── railway.json                   ← Railway build config
├── .env.example                   ← env-var template
├── .gitignore
├── LICENSE                        ← MIT
├── docs/
│   ├── ARCHITECTURE.md           ← detailed component design
│   ├── DEMO_SCRIPT.md            ← what to say in an interview demo
│   └── SETUP.md                  ← step-by-step setup instructions
├── notebooks/
│   ├── 01_synthetic_data.ipynb   ← generates 500 customers + 8 weeks of signals
│   ├── 02_agents.ipynb           ← all 4 agents, individually testable
│   └── 03_orchestrator.ipynb     ← the full Monday-morning loop
└── lovable-prompts/
    ├── 01-base-layout.md
    ├── 02-portfolio-health.md
    ├── 03-intervention-feed.md
    ├── 04-call-detail-modal.md
    ├── 05-escalation-queue.md
    ├── 06-weekly-report.md
    └── 07-live-demo-page.md
```

---

## Getting it running

See [`docs/SETUP.md`](docs/SETUP.md) for the full step-by-step. The short version:

1. Sign up for Groq, Supabase (Sydney region), SendGrid, Vapi.ai, Railway, and Lovable.
2. Copy `.env.example` to `.env` and fill in your keys.
3. Run the three Colab notebooks in order to seed Supabase.
4. Deploy this repo to Railway (auto-detects FastAPI from the Procfile).
5. Open Lovable, connect Supabase, paste the seven prompts from `lovable-prompts/`.
6. Set the GitHub Actions workflow with your secrets (see `docs/SETUP.md`).

End-to-end setup time: about 4–6 hours.

---

## Agents

| Agent                  | Role                                              | Model              |
|-----------------------|---------------------------------------------------|--------------------|
| **Triage**             | Reasons over 6 signal types, picks action         | Llama 3.3 70B      |
| **Email sub-agent**    | Drafts personalised email, sends via SendGrid     | Llama 3.3 70B      |
| **Voice sub-agent**    | Holds live conversation, listens for stress       | Llama 3.3 70B      |
| **Summariser**         | Extracts structured intelligence from transcripts | Llama 3.3 70B      |
| **Reporter**           | Writes autonomous weekly credit-risk memo         | Llama 3.3 70B      |

All five agents share the same model on Groq's free tier. Total LLM cost
over an 8-week simulated run: **$0**.

---

## Synthetic data

500 customers generated with the [Faker library](https://faker.readthedocs.io)
using realistic Australian distributions:

- Annual income: normal(95k, 28k) clipped to $45k–$250k (from ABS 2021 Census)
- Loan balance: normal($620k, $180k) clipped to $200k–$1.5M
- Interest rate: uniform(5.89% — 6.99%) — current Australian variable rate range
- State distribution: NSW 32%, VIC 26%, QLD 20%, WA 11%, SA 11%

The **stress ratio** (annual repayment ÷ annual income) follows
[APRA's serviceability guidance](https://www.apra.gov.au):
- `≤ 0.30` → Low risk
- `0.30 – 0.45` → Moderate
- `> 0.45` → Severe

8 weeks of weekly signals are generated per customer with realistic
drift — stressed customers show gradually declining savings, rising credit
card utilisation, and intermittent late repayments.

---

## Why this matters

This system is a direct prototype of what banks are trying to build with
agentic AI right now. Specifically:

- **Customer Assist programs** at CBA, NAB, ANZ, Westpac are all moving toward
  earlier, more personalised intervention. Manual processes don't scale.
- **Conversation intelligence** at the bank level — extracting sentiment,
  reasons disclosed, offer acceptance — currently relies on human-coded post-
  call notes. Doing this with an LLM at scale unlocks portfolio-level analytics.
- **Autonomous decisioning with human escalation** is the design pattern
  regulators favour. The escalation queue here is auditable: every decision
  the agent makes has a recorded reasoning trail.

---

## Limitations / honest notes

- **Voice calls are demonstrated, not run at scale.** Vapi's free tier only
  permits outbound calls to US numbers. The voice sub-agent is fully wired
  up — a working call is recorded in `docs/DEMO_SCRIPT.md` — but the bulk
  intervention runs use Groq-generated mock transcripts so the dashboard
  can show realistic voice-intervention data without burning credits.
- **All customer data is synthetic.** No real customer information is used.
- **The dashboard reads but does not write** to Supabase — Row Level Security
  is intentionally permissive for the demo. In production every read would
  require an authenticated `credit_risk_analyst` role.
- **Sender identity is verified per SendGrid** — in production the bank's
  CLI would be authenticated end-to-end.

---

## Author

**Yashasvi Rathore**
AI Product Manager · Data, SaaS & GenAI Platforms
Based in Melbourne, Australia · Full work rights, no sponsorship required

[LinkedIn](https://linkedin.com/in/yashasvi-rathore-aus) ·
[Email](mailto:yashasvirathoreofficial@gmail.com)

---

## License

[MIT](LICENSE)
