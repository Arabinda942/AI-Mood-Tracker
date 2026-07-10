# Auro — Mental Health Mood Tracker (Rajbari Edition)

A daily mood tracker styled after the old zamindar-bari (Rajbari) houses of Bengal —
deep maroon walls, antique gold trim, jali lattice patterns, serif type.

## Stack
- **Backend:** Flask + SQLite
- **Charts:** matplotlib (mood trend, sleep/exercise correlation, rendered server-side as PNG)
- **PDFs:** reportlab (welcome letter on signup, therapist report export)
- **Frontend:** server-rendered HTML/CSS/vanilla JS (no separate Node/React build needed —
  kept to one coherent stack so it runs with just `python app.py`)

## Setup
```bash
pip install -r requirements.txt
python app.py
```
Visit http://localhost:5050

## Features
- Register with phone, name, age, sex, email, location → receive a "Welcome to Auro" PDF
- Daily mood + anxiety sliders, sleep hours, exercise minutes, notes
- Dashboard: streak counter, average mood, mood/anxiety trend chart,
  sleep-vs-mood and exercise-vs-mood correlation charts with Pearson r
- CBT exercises: thought record, gratitude, cognitive reframe, grounding —
  saved and shown in history
- One-click therapist report PDF export (summary stats + charts + recent CBT entries)

## Notes
- Passwords are hashed with Werkzeug's `generate_password_hash`.
- `data/auro.db` and `data/generated/*.pdf` are created automatically on first run.
- Not a replacement for professional care — includes a crisis-care disclaimer in the welcome PDF.

## Deploying on Render (fixes the "Internal Server Error" on /dashboard)
That error happened because Render's free-tier disk is **ephemeral** — every
redeploy/restart wipes `data/auro.db`, but your browser keeps its old login
cookie. The app used to crash trying to load a user that no longer existed.
Fixed: `login_required` now checks the user still exists and safely bounces
back to the login page instead of crashing.

Two more things worth doing on Render for a smoother deploy:
1. This repo now includes a `Procfile` (`web: gunicorn app:app`) and `gunicorn`
   is in `requirements.txt`, so Render's Python service will run it correctly.
2. Set an environment variable `AURO_SECRET` in the Render dashboard to a fixed
   random string. Otherwise sessions still work fine, but it's good practice
   for production.
3. If you want mood history to **survive redeploys**, attach a Render
   **persistent disk** and point `DB_PATH` (in `database.py`) at a path on it —
   right now the SQLite file lives inside the app folder, which resets on deploy.

## UI
Rebuilt as a dark "Neon Night" theme — deep charcoal background, glass panels,
glowing blue / green / red accents on stats, charts, and buttons. All class
names in the templates stayed the same, so only `static/css/style.css` and the
chart colors in `utils/charts.py` changed.


## Want a React/Node version instead?
This build uses Flask + vanilla JS for simplicity (one server, one language for backend logic).
If you'd like a React frontend talking to this same Flask API (which already exposes
`/api/mood_logs`), let me know and I can scaffold that as a second frontend.
