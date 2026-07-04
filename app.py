import csv
import io
import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for

from matcher import find_matches
from schemes_data import SCHEMES

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

DB_PATH = os.path.join(app.instance_path, "leads.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Puducherry", "Chandigarh", "Other",
]


def get_db():
    if "db" not in g:
        os.makedirs(app.instance_path, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(app.instance_path, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            state TEXT,
            scheme_id TEXT,
            scheme_name TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", states=STATES)


@app.route("/results", methods=["POST"])
def results():
    form = request.form
    profile = {
        "age": int(form.get("age", 0) or 0),
        "gender": form.get("gender", ""),
        "state": form.get("state", ""),
        "area_type": form.get("area_type", ""),
        "annual_income": int(form.get("annual_income", 0) or 0),
        "occupation": form.get("occupation", ""),
        "social_category": form.get("social_category", ""),
        "is_bpl": form.get("is_bpl") == "yes",
        "is_disabled": form.get("is_disabled") == "yes",
        "is_student": form.get("is_student") == "yes",
        "is_widow": form.get("is_widow") == "yes",
        "has_daughter_under_10": form.get("has_daughter_under_10") == "yes",
        "is_business_owner": form.get("is_business_owner") == "yes",
        "owns_pucca_house": form.get("owns_pucca_house") == "yes",
    }
    matches = find_matches(profile)
    session["state"] = profile["state"]
    return render_template("results.html", matches=matches, profile=profile)


@app.route("/lead/<scheme_id>", methods=["GET", "POST"])
def lead(scheme_id):
    scheme = next((s for s in SCHEMES if s["id"] == scheme_id), None)
    if scheme is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        state = request.form.get("state", "").strip()

        if name and phone:
            db = get_db()
            db.execute(
                "INSERT INTO leads (name, phone, state, scheme_id, scheme_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (name, phone, state, scheme["id"], scheme["name"], datetime.utcnow().isoformat()),
            )
            db.commit()
            return render_template("thank_you.html", scheme=scheme)

    return render_template("lead_form.html", scheme=scheme, states=STATES, prefill_state=session.get("state", ""))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_leads"))
        error = "Incorrect password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/leads")
@admin_required
def admin_leads():
    db = get_db()
    rows = db.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    return render_template("admin_leads.html", leads=rows)


@app.route("/admin/leads.csv")
@admin_required
def admin_leads_csv():
    db = get_db()
    rows = db.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "phone", "state", "scheme_id", "scheme_name", "created_at"])
    for row in rows:
        writer.writerow([row["id"], row["name"], row["phone"], row["state"], row["scheme_id"], row["scheme_name"], row["created_at"]])
    return output.getvalue(), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=leads.csv",
    }


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5051)
