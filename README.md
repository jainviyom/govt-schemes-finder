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
