"""
scheduler.py — Standalone weekly orchestrator
==============================================
Called by GitHub Actions every Monday at 09:00 AEST. Runs the full
agentic loop: reads at-risk customers, triages each, dispatches to the
chosen channel, summarises responses, and writes the weekly report.

All credentials come from environment variables.
"""

import os
import json
import datetime
import random
import time

from groq import Groq
from supabase import create_client
import sendgrid
from sendgrid.helpers.mail import Mail
import requests

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

SUPABASE_URL  = os.environ["SUPABASE_URL"]
SUPABASE_KEY  = os.environ["SUPABASE_KEY"]
GROQ_API_KEY  = os.environ["GROQ_API_KEY"]
SENDGRID_KEY  = os.environ.get("SENDGRID_KEY", "")
SENDGRID_FROM = os.environ.get("SENDGRID_FROM", "")
YOUR_EMAIL    = os.environ.get("YOUR_EMAIL", "")
VAPI_KEY      = os.environ.get("VAPI_KEY", "")
VAPI_PHONE_ID = os.environ.get("VAPI_PHONE_ID", "")
TEST_PHONE    = os.environ.get("TEST_PHONE", "")
RAILWAY_URL   = os.environ.get("RAILWAY_URL", "")

MODEL = "llama-3.3-70b-versatile"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)


# ──────────────────────────────────────────────────────────────────────
# Agents
# ──────────────────────────────────────────────────────────────────────

def triage_customer(customer, signals):
    prompt = f"""You are a credit risk analyst at an Australian bank.
Assess this customer and decide on an action.

Customer: {json.dumps(customer, indent=2, default=str)}
Last 4 weeks signals: {json.dumps(signals[-4:], indent=2, default=str)}

Respond ONLY in valid JSON:
{{
  "stress_assessment": "low | moderate | high | critical",
  "key_signals": ["2-3 signals driving your view"],
  "reasoning": "2 sentences explaining your conclusion",
  "action": "MONITOR | EMAIL | CALL | ESCALATE",
  "action_rationale": "why this action and not another",
  "urgency": "routine | soon | immediate"
}}

Rules: MONITOR for most customers. EMAIL for moderate stress with
early warning signs. CALL for high/critical only. ESCALATE only for
imminent default risk."""

    resp = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(resp.choices[0].message.content)


def send_email_intervention(customer, triage):
    first = customer['name'].split()[0]
    draft = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""Write a warm email from CommBank to {first}.
Offer a free home loan health check call. Under 200 words.
Sign as Maya Chen, Home Loan Specialist.
Return JSON: {{"subject": "...", "body_text": "..."}}"""}],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    content = json.loads(draft.choices[0].message.content)

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_KEY)
    msg = Mail(
        from_email=SENDGRID_FROM,
        to_emails=YOUR_EMAIL,
        subject=f"[{customer['customer_id']}] {content['subject']}",
        plain_text_content=content['body_text']
    )
    sg.send(msg)

    return {"subject": content['subject'], "body": content['body_text']}


def generate_mock_transcript(customer):
    first = customer['name'].split()[0]
    prompt = f"""Generate a realistic 2-minute phone call between Maya
(CommBank specialist) and {first}. Maya offers help with mortgage stress.
Customer discloses a real-life reason (reduced hours, medical, family).
End with a clear outcome. Natural Australian speech patterns."""

    resp = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return resp.choices[0].message.content


def summarise_interaction(transcript, customer, channel):
    prompt = f"""You are a credit risk analyst reviewing a {channel} interaction.
Customer: {customer['name']}, risk tier: {customer['risk_tier']}

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
  "next_action": "what happens next",
  "rm_briefing": "paragraph for RM if escalating, else null"
}}"""

    resp = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(resp.choices[0].message.content)


def generate_weekly_report(week, interventions):
    resolved = sum(1 for i in interventions if i.get('outcome') == 'resolved')
    escalated = sum(1 for i in interventions if i.get('outcome') == 'escalate_to_human')
    emails = sum(1 for i in interventions if i.get('channel') == 'email')
    calls = sum(1 for i in interventions if i.get('channel') == 'voice')
    accepted = sum(1 for i in interventions if i.get('offer_accepted', 'none') != 'none')

    prompt = f"""Write a weekly credit risk executive briefing memo.

Week {week} data:
- Total interventions: {len(interventions)}
- Email: {emails} | Voice: {calls}
- Resolved: {resolved} | Escalated: {escalated}
- Acceptance: {accepted}/{len(interventions)}

Three paragraphs, CBA credit risk memo style:
1. Portfolio summary
2. Effectiveness
3. Focus areas for next week"""

    resp = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content


# ──────────────────────────────────────────────────────────────────────
# Main orchestration loop
# ──────────────────────────────────────────────────────────────────────

def main():
    week = datetime.date.today().isocalendar()[1]
    print(f"=== Week {week} agent run ===")

    customers = (
        sb.table('customers').select('*')
        .in_('risk_tier', ['Moderate', 'Severe'])
        .execute().data
    )
    print(f"Triaging {len(customers)} at-risk customers")

    log = []
    for customer in customers:
        signals = (
            sb.table('weekly_signals').select('*')
            .eq('customer_id', customer['customer_id'])
            .order('week', desc=True).limit(4).execute().data
        )

        try:
            triage = triage_customer(customer, signals)
        except Exception as e:
            print(f"  [WARN] triage failed for {customer['customer_id']}: {e}")
            continue

        action = triage['action']
        if action == 'MONITOR':
            continue

        row = {
            'customer_id': customer['customer_id'],
            'week': week,
            'action': action,
            'triage_reasoning': triage['reasoning'],
            'outcome': 'pending'
        }

        try:
            if action == 'EMAIL':
                r = send_email_intervention(customer, triage)
                row['channel'] = 'email'
                row['email_subject'] = r['subject']
                row['email_body'] = r['body']

            elif action == 'CALL':
                # Mock transcript path (Vapi free tier limit)
                transcript = generate_mock_transcript(customer)
                summary = summarise_interaction(transcript, customer, 'voice call')
                row['channel'] = 'voice'
                row['sentiment'] = summary['sentiment']
                row['offer_accepted'] = summary['offer_accepted']
                row['outcome'] = summary['outcome']
                row['new_risk_signals'] = summary['new_risk_signals']
                row['rm_briefing'] = summary.get('rm_briefing')

            elif action == 'ESCALATE':
                row['channel'] = 'escalation'
                row['outcome'] = 'escalate_to_human'
                row['rm_briefing'] = triage.get('action_rationale', '')

            sb.table('interventions').insert(row).execute()
            log.append(row)
            print(f"  Wk{week} {customer['customer_id']} -> {action}")
        except Exception as e:
            print(f"  [WARN] {action} failed: {e}")
            continue

        time.sleep(0.3)

    report = generate_weekly_report(week, log)
    sb.table('weekly_reports').upsert({
        'week': week,
        'total_interventions': len(log),
        'resolved': sum(1 for i in log if i.get('outcome') == 'resolved'),
        'escalated': sum(1 for i in log if i.get('outcome') == 'escalate_to_human'),
        'acceptance_rate': (
            sum(1 for i in log if i.get('offer_accepted', 'none') != 'none')
            / max(1, len(log))
        ),
        'report_text': report
    }).execute()

    print(f"\n[OK] Week {week}: {len(log)} interventions logged.")


if __name__ == "__main__":
    main()
