"""
Early Stress Intervention Orchestrator — FastAPI Backend
=========================================================
Hosts:
  - Vapi voice-call webhook (receives transcripts when calls end)
  - Four /demo/* endpoints powering the interactive Lovable demo
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

# CORS open for the Lovable frontend. In production restrict to the
# Lovable preview URL and any published custom domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────
# Lazy clients (created on first request so missing env vars don't crash
# the cold-start health-check)
# ──────────────────────────────────────────────────────────────────────
_sb = None
_groq = None


def supabase():
    global _sb
    if _sb is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise HTTPException(500, "Supabase credentials not configured")
        _sb = create_client(url, key)
    return _sb


def groq_client():
    global _groq
    if _groq is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise HTTPException(500, "Groq API key not configured")
        _groq = Groq(api_key=key)
    return _groq


MODEL = "llama-3.1-8b-instant"


# ──────────────────────────────────────────────────────────────────────
# Agent prompts — kept here as constants so they're easy to tune.
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

YOUR GOAL: a warm wellbeing check-in. Listen for stress signals.
You can offer if appropriate:
- 3-month repayment pause
- Switch to interest-only for 6 months
- Referral to the financial hardship team

CONVERSATION RULES:
- Be warm, human, conversational. Short responses (1-3 sentences)
  like a real phone call.
- Never volunteer the internal context. Never mention "risk score",
  "stress signals", "triage", or anything that sounds like internal data.
- If the customer DIRECTLY asks why you called or what prompted the call,
  you may give a calibrated honest answer like:
  "Our team noticed your account has been showing some patterns we
  sometimes see when customers are facing pressure — like [mention
  1-2 signals in plain English, e.g. 'a few late payments' or
  'savings drawing down quicker than usual']. So I wanted to reach
  out personally and see if there's anything we can help with."
- Translate the technical signals to plain-English equivalents:
    'savings declining 4 weeks'      → "savings drawing down quicker than usual"
    'cc_utilisation high'            → "credit card balance creeping up"
    'days_repayment_late > 0'        → "one of your recent repayments came in late"
    'irregular_income'               → "income deposits look less consistent"
    'stress_ratio > 0.45'            → "repayments are taking a big share of household income"
- If the customer pushes back ("how do you know that?"), acknowledge
  honestly: "We just look at patterns across accounts — nothing private,
  just things that tend to suggest someone might be feeling the pinch.
  I'm here if it would help to talk through options."

Conversation so far:
{history}
{customer_name}: {customer_message}

What does Maya say next? Just her response, no labels."""

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
    """Call Groq with JSON response format and parse the result."""
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
# Pydantic input models for the interactive demo endpoints
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
    # NEW — context from the triage decision
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
# Interactive demo endpoints — the Lovable "Live Demo" page calls these
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
    """Generate a personalised intervention email for the demo customer."""
    first_name = customer.name.split()[0]
    content = llm_json(
        EMAIL_DRAFT_PROMPT.format(first_name=first_name),
        temperature=0.7,
    )
    return {
        "from": "Maya Chen <maya@commbank.com.au>",
        "to": f"{first_name} <demo@example.com>",
        "subject": content["subject"],
        "body": content["body_text"],
    }

@app.post("/demo/voice-turn")
def demo_voice_turn(conv: ConversationTurnInput):
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
    """Run the Summariser agent on a completed demo conversation/email."""
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


@app.post("/demo/summarise-email")
class DraftEmailInput(BaseModel):
    name: str
    annual_income: float
    loan_balance: float
    monthly_repayment: float
    savings_balance: float
    credit_card_balance: float
    credit_card_limit: float
    days_late: int = 0
    irregular_income: bool = False
    # NEW — optional recipient for live sending
    send_to: Optional[str] = None


@app.post("/demo/draft-email")
def demo_draft_email(customer: DraftEmailInput):
    """Generate a personalised intervention email, optionally send it live."""
    first_name = customer.name.split()[0]
    content = llm_json(
        EMAIL_DRAFT_PROMPT.format(first_name=first_name),
        temperature=0.7,
    )

    sent = False
    sent_to = None
    error = None

    if customer.send_to:
        try:
            import sendgrid as _sg
            from sendgrid.helpers.mail import Mail as _Mail
            sg_key = os.getenv("SENDGRID_KEY")
            sg_from = os.getenv("SENDGRID_FROM")
            if sg_key and sg_from:
                sg = _sg.SendGridAPIClient(api_key=sg_key)
                msg = _Mail(
                    from_email=(sg_from, "Maya Chen — CommBank"),
                    to_emails=customer.send_to.strip(),
                    subject=f"[Live Demo] {content['subject']}",
                    plain_text_content=content["body_text"],
                )
                resp = sg.send(msg)
                sent = 200 <= resp.status_code < 300
                sent_to = customer.send_to.strip()
            else:
                error = "SendGrid not configured on the server"
        except Exception as e:
            error = str(e)

    return {
        "from": "Maya Chen <maya@commbank.com.au>",
        "to": sent_to or f"{first_name} <demo@example.com>",
        "subject": content["subject"],
        "body": content["body_text"],
        "sent_live": sent,
        "send_error": error,
    }


# ──────────────────────────────────────────────────────────────────────
# Vapi webhook — receives the end-of-call report and updates Supabase
# ──────────────────────────────────────────────────────────────────────

@app.post("/vapi-webhook")
async def vapi_complete(request: Request):
    """Process a completed Vapi call: summarise the transcript and update DB."""
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
