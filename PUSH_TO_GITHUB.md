# Push This Project to GitHub

The whole repo is pre-built. You just need to push it. About 10 minutes.

---

## Step 1 — Rotate your old API keys (5 min)

⚠️ **Your previous keys are in your Colab files and the chat history.**
Before pushing this to a public repo, regenerate them:

- **Groq**: console.groq.com/keys → revoke old key → create new
- **SendGrid**: app.sendgrid.com → Settings → API Keys → delete → create new
- **Vapi**: dashboard.vapi.ai/account → revoke → new key
- **Supabase**: Project Settings → API → Reset anon key

Update them in your Colab notebooks and in your Railway env vars.

---

## Step 2 — Create the empty GitHub repo (2 min)

1. github.com → top right `+` icon → **New repository**
2. Repository name: `mortgage-stress-intervention-agent`
3. Description: *"Autonomous multi-agent system for early mortgage stress intervention. Synthetic Australian portfolio, free stack."*
4. **Public**
5. **DO NOT initialise with a README** (we already have one)
6. Click **Create repository**
7. Copy the repo URL — looks like `https://github.com/your-username/mortgage-stress-intervention-agent.git`

---

## Step 3 — Install Git if you haven't (2 min)

**Mac:**
```bash
git --version
```
If prompted, click "Install" for Command Line Tools.

**Windows:**
Download from git-scm.com, install with defaults, restart terminal.

**Configure once:**
```bash
git config --global user.name "Yashasvi Rathore"
git config --global user.email "yashasvirathoreofficial@gmail.com"
```

---

## Step 4 — Push the repo (3 min)

From inside this folder (the unzipped one with all the files):

```bash
git init
git add .
git commit -m "Initial commit: Early Stress Intervention Orchestrator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/mortgage-stress-intervention-agent.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username.

If it asks for credentials:
- **Username**: your GitHub username
- **Password**: a Personal Access Token (NOT your account password)

To get the token:
1. GitHub → top-right avatar → Settings
2. Developer settings (left sidebar, bottom) → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Note: "git push"
5. Expiration: 90 days
6. Scopes: ✅ check `repo`
7. Generate token → copy it (starts with `ghp_`)
8. Paste it as the password

---

## Step 5 — Verify it's there

Refresh your GitHub repo page in the browser. You should see:

```
mortgage-stress-intervention-agent/
├── README.md         ← rendered nicely
├── main.py
├── scheduler.py
├── requirements.txt
├── Procfile
├── railway.json
├── .gitignore
├── .env.example
├── LICENSE
├── .github/workflows/weekly_run.yml
├── docs/
├── notebooks/
└── lovable-prompts/
```

Notice **no `.env`** in the list. That's correct — your secrets stay local.

---

## Step 6 — Deploy to Railway (5 min)

1. railway.app → **New Project** → **Deploy from GitHub repo**
2. Select `mortgage-stress-intervention-agent`
3. Railway starts building automatically. It will fail because env vars aren't set yet — that's expected.
4. Click on the service → **Variables** tab → **Raw Editor**
5. Paste all your real keys (from `.env.example` template, with real values):

```
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=...
GROQ_API_KEY=gsk_...
SENDGRID_KEY=SG....
SENDGRID_FROM=your-verified-sender@example.com
YOUR_EMAIL=your-email@example.com
VAPI_KEY=...
VAPI_PHONE_ID=...
TEST_PHONE=+61...
```

6. Click **Update Variables** → Railway redeploys.
7. **Settings** → **Networking** → **Generate Domain**
8. Open the URL — you should see `{"status": "running"}`
9. Save this URL — you need it for Lovable.

---

## Step 7 — Add GitHub Actions secrets (3 min)

1. Your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

| Secret name      | Value                          |
|------------------|--------------------------------|
| SUPABASE_URL     | your Supabase URL              |
| SUPABASE_KEY     | your anon key                  |
| GROQ_API_KEY     | your Groq key                  |
| SENDGRID_KEY     | your SendGrid key              |
| SENDGRID_FROM    | your verified sender           |
| YOUR_EMAIL       | your email                     |
| VAPI_KEY         | your Vapi key                  |
| VAPI_PHONE_ID    | your Vapi phone UUID           |
| RAILWAY_URL      | your Railway URL               |
| TEST_PHONE       | your phone in E.164            |

3. Go to **Actions** tab → click **Weekly Agent Run** → **Run workflow** → **Run**
4. Wait 1-2 minutes → click the run → check logs for success.

---

## Step 8 — Open the Lovable prompts

Each prompt is in `lovable-prompts/`. Open `07-live-demo-page.md` and
replace `[YOUR_RAILWAY_URL]` with your real Railway URL.

Then paste prompts 1–7 into Lovable one at a time.

---

## You're done!

Final checklist:
- [ ] GitHub repo public and showing the project
- [ ] Railway deployed and returning `{"status":"running"}`
- [ ] GitHub Actions workflow ran successfully at least once
- [ ] Lovable dashboard published and showing data
- [ ] One real email landed in your inbox during testing
- [ ] All Live Demo flows tested (email + voice + escalate)

Add the Lovable URL and a Loom recording to your README and to LinkedIn.

You're ready to interview.
