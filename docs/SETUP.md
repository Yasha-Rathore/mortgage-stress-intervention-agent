# Setup Guide

Step-by-step from zero to running system. Budget about 4–6 hours total.

---

## Step 1 — Sign up for all accounts (30 min)

You need accounts on six services. All free, no credit cards required.

| Service        | URL                          | What to grab                                            |
|---------------|------------------------------|---------------------------------------------------------|
| Groq          | console.groq.com             | API key (starts with `gsk_`)                            |
| Supabase      | supabase.com                 | Project URL + anon key (use **Sydney** region)          |
| SendGrid      | sendgrid.com                 | API key (Full Access) + verified sender email           |
| Vapi.ai       | vapi.ai                      | API key + Phone Number ID (free US trial number)        |
| Railway       | railway.app                  | Free $5 credit, sign in with GitHub                     |
| Lovable       | lovable.dev                  | Free public projects                                    |
| GitHub        | github.com                   | For repo + Actions scheduling                           |

**SendGrid gotcha:** you MUST verify your sender email at Settings → Sender
Authentication. Until you do, all emails fail silently with 401.

---

## Step 2 — Create the Supabase tables (5 min)

Open your Supabase project → SQL Editor → New query. Paste:

```sql
CREATE TABLE customers (
  customer_id TEXT PRIMARY KEY,
  name TEXT, email TEXT, state TEXT,
  annual_income NUMERIC, loan_balance NUMERIC,
  monthly_repayment NUMERIC, savings_balance NUMERIC,
  credit_card_limit NUMERIC, credit_card_balance NUMERIC,
  stress_ratio NUMERIC, risk_tier TEXT,
  intervention_status TEXT DEFAULT 'none',
  email_sent BOOLEAN DEFAULT FALSE,
  email_opened BOOLEAN DEFAULT FALSE,
  email_replied BOOLEAN DEFAULT FALSE,
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE weekly_signals (
  id BIGSERIAL PRIMARY KEY,
  customer_id TEXT,
  week INTEGER,
  savings_balance NUMERIC,
  cc_utilisation NUMERIC,
  days_repayment_late INTEGER,
  irregular_income BOOLEAN,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE interventions (
  id BIGSERIAL PRIMARY KEY,
  customer_id TEXT,
  week INTEGER,
  action TEXT,
  channel TEXT,
  triage_reasoning TEXT,
  email_subject TEXT,
  email_body TEXT,
  sentiment TEXT,
  offer_accepted TEXT,
  outcome TEXT DEFAULT 'pending',
  rm_briefing TEXT,
  new_risk_signals JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE weekly_reports (
  id BIGSERIAL PRIMARY KEY,
  week INTEGER UNIQUE,
  total_interventions INTEGER,
  resolved INTEGER,
  escalated INTEGER,
  email_open_rate NUMERIC,
  acceptance_rate NUMERIC,
  report_text TEXT,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);
```

Click Run. You should see "Success. No rows returned" four times.

---

## Step 3 — Run the Colab notebooks (45 min)

Open the three notebooks from `notebooks/` in Google Colab (File → Upload notebook).

### `01_synthetic_data.ipynb`

Top cell: fill in your Supabase URL and key. Then **Runtime → Run all**.

Output: 500 customers seeded, 4000 weekly signals seeded. Check the Supabase
Table Editor to confirm.

### `02_agents.ipynb`

Top cell: fill in all your API keys. Then run cells one at a time (each cell
tests an agent individually). You'll get one real email in your inbox when
the Email sub-agent cell runs.

### `03_orchestrator.ipynb`

Top cell: same keys. Then run all cells. This runs the full intervention loop
across 80 customers spread over 8 weeks. Takes 3–5 minutes. After it finishes,
your Supabase `interventions` table will have ~60–80 rows, and `weekly_reports`
will have 8 rows.

---

## Step 4 — Deploy the FastAPI backend to Railway (15 min)

1. Push this repository to your own GitHub (see `PUSH_TO_GITHUB.md`).
2. railway.app → New Project → Deploy from GitHub repo → pick your repo.
3. While building → Variables tab → add all the env vars from `.env.example`.
4. Settings → Networking → Generate Domain.
5. Open the URL in your browser — you should see `{"status": "running"}`.
6. Save this URL — it goes into the Lovable Live Demo prompt and into the
   Vapi dashboard as the Server URL.

---

## Step 5 — Build the Lovable dashboard (90 min)

1. lovable.dev → New project.
2. Top-right → Supabase icon → Connect → select your `mortgage-stress-agent`
   project.
3. Open `lovable-prompts/01-base-layout.md` and paste the prompt. Wait for
   Lovable to build.
4. Paste each subsequent prompt one at a time:
   - `02-portfolio-health.md`
   - `03-intervention-feed.md`
   - `04-call-detail-modal.md`
   - `05-escalation-queue.md`
   - `06-weekly-report.md`
   - `07-live-demo-page.md` ← replace `[YOUR_RAILWAY_URL]` first
5. Click Publish. Note the public URL.

---

## Step 6 — Set up GitHub Actions (10 min)

In your GitHub repo:

1. Settings → Secrets and variables → Actions → New repository secret.
2. Add every variable from `.env.example` as a secret with the same name.
3. Go to Actions tab → enable workflows.
4. Run the "Weekly Agent Run" workflow manually once to verify.

The workflow will then run automatically every Monday at 9am AEST.

---

## You're done

Final checklist:

- [ ] Supabase has 500 customers, 4000 signals, ~60+ interventions, 8 reports
- [ ] Railway URL returns `{"status": "running"}`
- [ ] Lovable dashboard shows live data on every page
- [ ] One real email landed in your inbox
- [ ] One real Vapi voice call recorded (US trial number → your phone)
- [ ] GitHub Actions workflow ran manually with success
- [ ] README is updated with your Lovable URL and Loom video link
