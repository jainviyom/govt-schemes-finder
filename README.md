# Yojana Checker — "Which government schemes am I eligible for?"

A simple Flask web app for India: users answer a short form (age, income, state,
occupation, category, etc.) and get a list of central government schemes they
likely qualify for, with a link to the official portal for each.

## How it makes money

**Lead generation**: on the results page, every matched scheme has a "Get help
applying" button. Users who click it leave their name, phone, and state. Those
leads are stored in a local SQLite database (`instance/leads.db`) and can be
viewed/exported at `/admin/leads` (password-protected). You sell/refer these
leads to CSC (Common Service Centre) operators, CA firms, or scheme consultants
who charge people to help fill out and file applications — a well-established
model in India. This keeps the tool itself free, which maximizes usage and
therefore lead volume.

Two easy additions if you want a second revenue stream later:
- Google AdSense banner in `base.html` (works well once you have organic traffic).
- A "priority processing" affiliate link to partner CSC/agent services per scheme.

## Running locally

```bash
cd /Users/Viyom/projects/govt-schemes-finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit http://127.0.0.1:5050

Admin leads dashboard: http://127.0.0.1:5050/admin/leads
(default password `changeme` — set a real one via the `ADMIN_PASSWORD`
environment variable before deploying).

## Project structure

```
app.py              Flask routes, lead storage, admin dashboard
schemes_data.py      The scheme database + eligibility criteria
matcher.py           Rule engine that matches a user profile to schemes
templates/           Jinja2 HTML templates
static/css/          Styling
instance/leads.db    SQLite DB of leads (created automatically, gitignored)
```

## Adding or editing schemes

Edit the `SCHEMES` list in `schemes_data.py`. Each entry has a `criteria`
dict — supported keys are documented via `matcher.py`. No template changes
needed; the results page renders whatever matches.

## Deploying to Render

This repo includes a `render.yaml` Blueprint so Render can provision the
service automatically:

1. Go to [render.com](https://render.com) and sign in (GitHub login is easiest).
2. **New +** → **Blueprint** → connect the `govt-schemes-finder` GitHub repo.
3. Render reads `render.yaml` and proposes one web service. It auto-generates
   `SECRET_KEY`; you'll be prompted to type in a value for `ADMIN_PASSWORD`
   (pick a real one, not `changeme`).
4. Click **Apply** / **Create**. First build takes a couple of minutes; the
   free tier will spin down after 15 minutes of inactivity and take ~30-60s
   to wake back up on the next request.
5. Every push to `main` auto-redeploys.

**Important — leads database persistence**: the free tier's disk is
ephemeral, so `instance/leads.db` (where captured leads live) is wiped on
every redeploy or restart. That's fine for testing, but since leads are the
whole monetization model here, before relying on this for real leads either:
- upgrade the web service to a paid instance type and attach a Render
  **persistent disk** mounted at `instance/`, or
- swap SQLite for Render's managed Postgres (bigger change: swap the
  `sqlite3` calls in `app.py` for `psycopg2`/`SQLAlchemy` and a
  `DATABASE_URL` env var).

## Before going live

- Set a strong `SECRET_KEY` and `ADMIN_PASSWORD` as environment variables.
- Double-check every scheme's eligibility rules and `apply_url` against the
  current official source — scheme rules and income thresholds change.
- Add a privacy policy page describing how phone numbers/leads are used and
  shared with consultants (needed for user trust and for AdSense approval).
- Consider adding Hindi/regional-language labels — most of this audience will
  prefer their own language, and it meaningfully increases reach in India.
- Deploy on Render, Railway, PythonAnywhere, or a small VPS. SQLite is fine at
  low-to-moderate lead volume; move to Postgres if it grows.
