"""
Early Stress Intervention Orchestrator — FastAPI Backend
=========================================================
Hosts:
  - Vapi voice-call webhook (receives transcripts when calls end)
  - Five /demo/* endpoints powering the interactive Lovable demo
  - Health-check at /

Deployed on Railway. Connects to Supabase for persistence and Groq for the
LLM agents. All keys are read from environment variables — never commit
real values.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ──────────────────────────────────────────────────────────────────────
# App + middleware
# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Early Stress Intervention Orchestrator",
    description="Autonomous multi-agent backend for mortgage stress intervention",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────
# Lazy clients
# ──────────────────────────────────────────────────────────────────────
_sb = None
_groq = None


def supabase():
    global _sb
    if _sb is None:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_KEY", "").strip()
        if not url or not key:
            raise HTTPException(500, "Supabase credentials not configured")
        _sb = create_client(url, key)
    return _sb


def groq_client():
    global _groq
    if _groq is None:
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            raise HTTPException(500, "Groq API key not configured")
        _groq = Groq(api_key=key)
    return _groq


MODEL = "llama-3.1-8b-instant"


# ──────────────────────────────────────────────────────────────────────
# Agent prompts
# ──────────────────────────────────────────────────────────────────────

TRIAGE_PROMPT = """You are a credit risk analyst at an Australian bank.
Assess this customer and decide on an action.

Customer profile:
{customer}

Behavioural signals (latest first):
{signals}

Respond ONLY in valid JSON:
{{
  "stress_assessment": "low | moderate | high | critical",
  "key_signals": ["2-3 signals driving your view"],
  "reasoning": "2 sentences explaining your conclusion",
  "action": "MONITOR | EMAIL | CALL | ESCALATE",
  "action_rationale": "why this action and not another",
  "urgency": "routine | soon | immediate"
}}

Rules:
- MONITOR for most customers showing borderline signals.
- EMAIL for moderate stress with early warning patterns.
- CALL for high/critical stress requiring a human-style conversation.
- ESCALATE only when default risk is imminent or RM intervention is required.
"""

EMAIL_DRAFT_PROMPT = """Write a warm email from CommBank to {first_name}.

Context: this customer may be under some financial pressure but doesn't know
the bank has noticed. The purpose of the email is to gently offer a free home
loan health check with a specialist.

Rules:
- Subject line: short, curiosity-driven, never alarming.
- Body: 3 short paragraphs. Warm and human, not corporate.
- Never mention risk, stress, arrears, or internal bank data.
- End with two clear options: "Book a call" or "I'm fine, no thanks".
- Sign off as: Maya Chen, Home Loan Specialist, CommBank.

Respond in JSON: {{"subject": "...", "body_text": "..."}}
"""


VOICE_TURN_PROMPT = """You are Maya, a home loan specialist at Commonwealth Bank,
on a phone call with {customer_name}.

INTERNAL CONTEXT (do not share unless the customer specifically asks
why you called):
- Customer risk tier: {risk_tier}
- Triage signals that flagged this customer: {key_signals}
- Bank's internal reasoning: {reasoning}

YOUR GOAL: a warm wellbeing check-in. Move the conversation forward
toward understanding how the customer is going financially. Listen
for stress signals. Where appropriate, offer:
- 3-month repayment pause
- Switch to interest-only for 6 months
- Referral to the financial hardship team

CONVERSATION DYNAMICS — VERY IMPORTANT:
- You are the one driving the conversation. Don't just respond to
  the customer — gently steer toward your goal.
- If the customer's reply is short or non-substantive (e.g. "Hi",
  "Yeah", "OK", "Hello"), DON'T just respond with another pleasantry.
  Move forward with a specific question. For example:
  - User: "Hi Maya" → You: "Hey {customer_name}! How have things
    been with you lately? Are you finding the repayments comfortable
    on the loan?"
  - User: "Yeah okay" → You: "Good to hear. Can I ask — has anything
    changed for you in the last few months — work, family, anything
    like that?"
  - User: "What's this about?" → You explain calibratedly (see below).
- Always end your response with either a question OR an offer.
  Never end with a statement that closes the topic.
- Keep responses SHORT — 1-2 sentences max. Real phone calls are
  back-and-forth, not monologues.

CONVERSATION RULES:
- Be warm, human, conversational. Use {customer_name}'s first name
  occasionally (not every sentence).
- Never volunteer the internal context. Never mention "risk score",
  "stress signals", "triage", "flagged", or anything that sounds
  like internal data.

IF THE CUSTOMER ASKS WHY YOU'RE CALLING:
Give a calibrated honest answer translating the technical signals
to plain English. Example:
  "Our team noticed your account has been showing some patterns we
  sometimes see when people are feeling a bit of pressure — like
  [1-2 signals in plain English: 'a few late payments' / 'savings
  drawing down quicker than usual' / 'credit card balance creeping
  up' / 'income deposits a bit irregular']. So I wanted to reach
  out personally and see if there's anything we can help with."

Plain-English translations:
  'savings declining'          → "savings drawing down quicker than usual"
  'cc_utilisation high'        → "credit card balance creeping up"
  'days_repayment_late > 0'    → "a recent repayment came in late"
  'irregular_income'           → "income deposits a bit less consistent"
  'stress_ratio > 0.45'        → "repayments are taking a big share of household income"

IF THE CUSTOMER ASKS "ARE YOU A REAL PERSON?":
Answer honestly: "I'm an AI assistant from CommBank, but I can put
you through to a human specialist if you'd prefer. Either way I can
walk you through the options if that's helpful."

IF THE CUSTOMER PUSHES BACK ("how do you know that?"):
"We just look at patterns across accounts — nothing private, just
things that tend to suggest someone might be feeling the pinch.
I'm here if it would help to talk through options."

Conversation so far:
{history}
{customer_name}: {customer_message}

What does Maya say next? Just her response. Keep it short.
Always end with a question or an offer."""

SUMMARISE_PROMPT = """You are a credit risk analyst reviewing a {channel} interaction.
Customer: {name}, risk tier: {risk_tier}

Content:
{transcript}

Respond ONLY in valid JSON:
{{
  "sentiment": "positive | neutral | concerned | distressed",
  "engaged": true or false,
  "reasons_disclosed": ["any reasons customer mentioned"],
  "offer_accepted": "none | repayment_pause | interest_only | hardship_referral | booked_call",
  "outcome": "resolved | monitor | follow_up | escalate_to_human",
  "new_risk_signals": ["new signals learned"],
  "updated_stress_assessment": "low | moderate | high | critical",
  "next_action": "what should happen in next triage cycle",
  "rm_briefing": "one paragraph for human RM if escalating, else null"
}}"""


def llm_json(prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
    """Call Groq with JSON response format."""
    resp = groq_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return json.loads(resp.choices[0].message.content)


def llm_text(prompt: str, temperature: float = 0.7) -> str:
    """Call Groq for free-form text output."""
    resp = groq_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


# ──────────────────────────────────────────────────────────────────────
# Pydantic input models
# ──────────────────────────────────────────────────────────────────────

class CustomerInput(BaseModel):
    name: str
    annual_income: float
    loan_balance: float
    monthly_repayment: float
    savings_balance: float
    credit_card_balance: float
    credit_card_limit: float
    days_late: int = 0
    irregular_income: bool = False
    # Optional recipient for live email send
    send_to: Optional[str] = None


class EmailReplyInput(BaseModel):
    customer_name: str
    risk_tier: str
    email_subject: str
    email_body: str
    customer_reply: str


class ConversationTurnInput(BaseModel):
    customer_name: str
    risk_tier: str
    customer_message: str
    conversation_history: List[Dict[str, str]] = []
    key_signals: List[str] = []
    triage_reasoning: str = ""


class TranscriptInput(BaseModel):
    customer_name: str
    risk_tier: str
    conversation: List[Dict[str, str]]


# ──────────────────────────────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Early Stress Intervention Orchestrator",
        "version": "1.0.0",
    }


# ──────────────────────────────────────────────────────────────────────
# Demo endpoints
# ──────────────────────────────────────────────────────────────────────

@app.post("/demo/triage")
def demo_triage(customer: CustomerInput):
    """Run the Triage Agent against a user-built customer profile."""
    annual_repayment = customer.monthly_repayment * 12
    stress_ratio = annual_repayment / customer.annual_income if customer.annual_income else 0

    if stress_ratio > 0.45:
        risk_tier = "Severe"
    elif stress_ratio > 0.30:
        risk_tier = "Moderate"
    else:
        risk_tier = "Low"

    customer_obj = customer.model_dump()
    customer_obj.update({
        "customer_id": "DEMO-LIVE",
        "stress_ratio": round(stress_ratio, 3),
        "risk_tier": risk_tier,
    })

    cc_util = (
        customer.credit_card_balance / customer.credit_card_limit
        if customer.credit_card_limit else 0
    )
    signals = [{
        "week": 1,
        "savings_balance": customer.savings_balance,
        "cc_utilisation": round(cc_util, 3),
        "days_repayment_late": customer.days_late,
        "irregular_income": customer.irregular_income,
    }]

    triage = llm_json(TRIAGE_PROMPT.format(
        customer=json.dumps(customer_obj, indent=2),
        signals=json.dumps(signals, indent=2),
    ))

    return {
        "customer": customer_obj,
        "stress_ratio": round(stress_ratio, 3),
        "risk_tier": risk_tier,
        "cc_utilisation": round(cc_util, 3),
        "triage": triage,
    }


@app.post("/demo/draft-email")
def demo_draft_email(customer: CustomerInput):
    """Generate a personalised email and optionally send it live via SendGrid."""
    first_name = customer.name.split()[0]
    content = llm_json(
        EMAIL_DRAFT_PROMPT.format(first_name=first_name),
        temperature=0.7,
    )

    sent = False
    sent_to_addr = None
    error = None

    print(f"[demo/draft-email] send_to received: {customer.send_to!r}", flush=True)

    if customer.send_to:
        try:
            import sendgrid as _sg
            from sendgrid.helpers.mail import Mail as _Mail
            sg_key = os.getenv("SENDGRID_KEY", "").strip()
            sg_from = os.getenv("SENDGRID_FROM", "").strip()
            if sg_key and sg_from:
                recipient = customer.send_to.strip()
                sg = _sg.SendGridAPIClient(api_key=sg_key)
                msg = _Mail(
                    from_email=(sg_from, "Maya Chen — CommBank"),
                    to_emails=recipient,
                    subject=f"[Live Demo] {content['subject']}",
                    plain_text_content=content["body_text"],
                )
                resp = sg.send(msg)
                sent = 200 <= resp.status_code < 300
                sent_to_addr = recipient
                print(f"[demo/draft-email] SendGrid status: {resp.status_code}", flush=True)
            else:
                error = "SendGrid not configured on server"
                print(f"[demo/draft-email] error: {error}", flush=True)
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}"
            print(f"[demo/draft-email] exception: {error}", flush=True)

    return {
        "from": "Maya Chen <maya@commbank.com.au>",
        "to": f"{first_name} <{sent_to_addr}>" if sent_to_addr else f"{first_name} <demo@example.com>",
        "subject": content["subject"],
        "body": content["body_text"],
        "sent_live": sent,
        "send_error": error,
    }


@app.post("/demo/summarise-email")
def demo_summarise_email(e: EmailReplyInput):
    """Summarise an email + customer-reply exchange."""
    transcript = (
        f"--- Bank email ---\n"
        f"Subject: {e.email_subject}\n\n{e.email_body}\n\n"
        f"--- Customer reply ---\n{e.customer_reply}"
    )
    summary = llm_json(SUMMARISE_PROMPT.format(
        channel="email",
        name=e.customer_name,
        risk_tier=e.risk_tier,
        transcript=transcript,
    ))
    return summary


@app.post("/demo/voice-turn")
def demo_voice_turn(conv: ConversationTurnInput):
    """Get Maya's next response in the simulated voice conversation."""
    history_text = "\n".join(
        f"{'Maya' if m.get('role') == 'maya' else conv.customer_name}: {m.get('text', '')}"
        for m in conv.conversation_history
    )

    if not conv.customer_message and not conv.conversation_history:
        first_name = conv.customer_name.split()[0]
        return {
            "maya_response": (
                f"Hi {first_name}, it's Maya from CommBank. "
                "How are you going? Just wanted to do a quick check-in — "
                "is now an okay time?"
            )
        }

    response = llm_text(
        VOICE_TURN_PROMPT.format(
            customer_name=conv.customer_name,
            risk_tier=conv.risk_tier,
            key_signals=", ".join(conv.key_signals) if conv.key_signals else "(none provided)",
            reasoning=conv.triage_reasoning or "(none provided)",
            history=history_text,
            customer_message=conv.customer_message,
        ),
        temperature=0.7,
    )
    return {"maya_response": response}


@app.post("/demo/summarise")
def demo_summarise(t: TranscriptInput):
    """Run the Summariser agent on a completed voice conversation."""
    transcript = "\n".join(
        f"{'Maya' if m.get('role') == 'maya' else t.customer_name}: {m.get('text', '')}"
        for m in t.conversation
    )
    summary = llm_json(SUMMARISE_PROMPT.format(
        channel="voice call",
        name=t.customer_name,
        risk_tier=t.risk_tier,
        transcript=transcript,
    ))
    return summary


# ──────────────────────────────────────────────────────────────────────
# Vapi webhook
# ──────────────────────────────────────────────────────────────────────

@app.post("/vapi-webhook")
async def vapi_complete(request: Request):
    """Process a completed Vapi call."""
    data = await request.json()
    message = data.get("message", {})
    if message.get("type") != "end-of-call-report":
        return {"status": "ignored", "reason": "not end-of-call"}

    transcript = message.get("transcript", "")
    customer_id = message.get("call", {}).get("metadata", {}).get("customer_id")
    if not customer_id:
        return {"status": "ignored", "reason": "no customer_id in metadata"}

    sb = supabase()
    customer = (
        sb.table("customers").select("*").eq("customer_id", customer_id)
        .single().execute().data
    )

    summary = llm_json(SUMMARISE_PROMPT.format(
        channel="voice call",
        name=customer["name"],
        risk_tier=customer["risk_tier"],
        transcript=transcript,
    ))

    sb.table("interventions").update({
        "outcome": summary.get("outcome"),
        "sentiment": summary.get("sentiment"),
        "offer_accepted": summary.get("offer_accepted"),
        "rm_briefing": summary.get("rm_briefing"),
        "new_risk_signals": summary.get("new_risk_signals"),
    }).eq("customer_id", customer_id).eq("channel", "voice").execute()

    return {"status": "processed", "outcome": summary.get("outcome")}
