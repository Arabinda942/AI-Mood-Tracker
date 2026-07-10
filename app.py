"""
Auro — Mental Health Mood Tracker
Flask backend.
"""
import os
from datetime import datetime, date
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_file, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
from utils import charts, pdf_gen

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "data", "generated")
os.makedirs(OUT_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("AURO_SECRET", "rajbari-auro-dev-secret-change-me")

db.init_db()


# ---------- helpers ----------
def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


CBT_LIBRARY = [
    {
        "type": "thought_record",
        "title": "Thought Record",
        "blurb": "Catch an automatic thought, weigh the evidence, and write a more balanced one."
    },
    {
        "type": "gratitude",
        "title": "Three Good Things",
        "blurb": "Note three things — however small — that went well today, and why."
    },
    {
        "type": "reframe",
        "title": "Cognitive Reframe",
        "blurb": "Take a harsh self-judgement and rewrite it the way you'd speak to a friend."
    },
    {
        "type": "grounding",
        "title": "5-4-3-2-1 Grounding",
        "blurb": "Anchor into the present using five senses when anxiety spikes."
    },
]


# ---------- auth ----------
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        age = request.form.get("age", "").strip()
        sex = request.form.get("sex", "").strip()
        email = request.form.get("email", "").strip()
        location = request.form.get("location", "").strip()
        password = request.form.get("password", "")

        if not name or not phone or not password:
            flash("Name, phone number, and password are required.")
            return redirect(url_for("register"))

        if db.get_user_by_phone(phone):
            flash("An account with this phone number already exists. Please log in.")
            return redirect(url_for("login"))

        user_id = db.create_user(
            name, phone,
            int(age) if age.isdigit() else None,
            sex, email, location,
            generate_password_hash(password)
        )

        # Generate the welcome PDF
        pdf_path = os.path.join(OUT_DIR, f"auro_welcome_{user_id}.pdf")
        pdf_gen.generate_welcome_pdf(name, phone, age, sex, email, location, pdf_path)

        session["user_id"] = user_id
        session["welcome_pdf"] = pdf_path
        return redirect(url_for("welcome"))

    return render_template("register.html")


@app.route("/welcome")
@login_required
def welcome():
    user = db.get_user_by_id(session["user_id"])
    return render_template("welcome.html", user=user)


@app.route("/welcome/download")
@login_required
def welcome_download():
    pdf_path = session.get("welcome_pdf") or os.path.join(OUT_DIR, f"auro_welcome_{session['user_id']}.pdf")
    if not os.path.exists(pdf_path):
        user = db.get_user_by_id(session["user_id"])
        pdf_gen.generate_welcome_pdf(user["name"], user["phone"], user["age"], user["sex"],
                                      user["email"], user["location"], pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name="Welcome_to_Auro.pdf")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_phone(phone)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Phone number or password is incorrect.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- dashboard ----------
@app.route("/dashboard")
@login_required
def dashboard():
    user = db.get_user_by_id(session["user_id"])
    logs = db.get_mood_logs(user["id"])
    today = date.today().isoformat()
    today_log = next((r for r in logs if r["log_date"] == today), None)

    trend_chart = charts.mood_trend_chart(logs)
    sleep_chart = charts.sleep_correlation_chart(logs)
    exercise_chart = charts.exercise_correlation_chart(logs)
    stats = charts.correlation_stats(logs)

    streak = 0
    log_dates = {r["log_date"] for r in logs}
    from datetime import timedelta
    d = date.today()
    while d.isoformat() in log_dates:
        streak += 1
        d -= timedelta(days=1)

    avg_mood = round(sum(r["mood_score"] for r in logs) / len(logs), 1) if logs else None

    return render_template(
        "dashboard.html",
        user=user,
        logs=list(reversed(logs)),
        today=today,
        today_log=today_log,
        trend_chart=trend_chart,
        sleep_chart=sleep_chart,
        exercise_chart=exercise_chart,
        stats=stats,
        streak=streak,
        avg_mood=avg_mood,
        total_entries=len(logs),
    )


@app.route("/log_mood", methods=["POST"])
@login_required
def log_mood():
    user_id = session["user_id"]
    log_date = request.form.get("log_date") or date.today().isoformat()
    mood_score = int(request.form.get("mood_score", 5))
    anxiety_score = request.form.get("anxiety_score")
    anxiety_score = int(anxiety_score) if anxiety_score else None
    sleep_hours = request.form.get("sleep_hours")
    sleep_hours = float(sleep_hours) if sleep_hours else None
    exercise_minutes = request.form.get("exercise_minutes")
    exercise_minutes = int(exercise_minutes) if exercise_minutes else None
    notes = request.form.get("notes", "").strip()

    db.upsert_mood_log(user_id, log_date, mood_score, anxiety_score, sleep_hours, exercise_minutes, notes)
    return redirect(url_for("dashboard"))


# ---------- CBT ----------
@app.route("/cbt")
@login_required
def cbt():
    user_id = session["user_id"]
    entries = db.get_cbt_entries(user_id)
    return render_template("cbt.html", library=CBT_LIBRARY, entries=entries)


@app.route("/cbt/save", methods=["POST"])
@login_required
def cbt_save():
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date") or date.today().isoformat()
    exercise_type = request.form.get("exercise_type", "thought_record")
    situation = request.form.get("situation", "")
    automatic_thought = request.form.get("automatic_thought", "")
    evidence_for = request.form.get("evidence_for", "")
    evidence_against = request.form.get("evidence_against", "")
    balanced_thought = request.form.get("balanced_thought", "")
    mood_before = request.form.get("mood_before")
    mood_after = request.form.get("mood_after")

    db.add_cbt_entry(
        user_id, entry_date, exercise_type, situation, automatic_thought,
        evidence_for, evidence_against, balanced_thought,
        int(mood_before) if mood_before else None,
        int(mood_after) if mood_after else None,
    )
    return redirect(url_for("cbt"))


# ---------- therapist report ----------
@app.route("/report/download")
@login_required
def report_download():
    user = db.get_user_by_id(session["user_id"])
    logs = db.get_mood_logs(user["id"], limit=365)
    cbt_entries = db.get_cbt_entries(user["id"], limit=20)

    chart_data = {
        "trend": charts.mood_trend_chart(logs),
        "sleep": charts.sleep_correlation_chart(logs),
        "exercise": charts.exercise_correlation_chart(logs),
    }
    stats = charts.correlation_stats(logs)

    out_path = os.path.join(OUT_DIR, f"auro_therapist_report_{user['id']}.pdf")
    pdf_gen.generate_therapist_report_pdf(user, logs, cbt_entries, chart_data, stats, out_path)
    return send_file(out_path, as_attachment=True, download_name=f"Auro_Therapist_Report_{user['name'].replace(' ', '_')}.pdf")


# ---------- API (for JS charts / live refresh) ----------
@app.route("/api/mood_logs")
@login_required
def api_mood_logs():
    logs = db.get_mood_logs(session["user_id"])
    return jsonify([dict(r) for r in logs])


if __name__ == "__main__":
    # use_reloader=False avoids "signal only works in main thread" errors that
    # occur when the dev server is launched from certain IDEs/debuggers where
    # Flask's auto-reloader isn't running in the main interpreter thread.
    app.run(debug=True, port=5050, use_reloader=False)
