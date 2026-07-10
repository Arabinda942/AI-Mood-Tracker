"""
Chart generation for Auro dashboard, rendered with matplotlib
and returned as base64 PNG strings so they can be embedded directly
in HTML/PDF without saving files that need cleanup.
"""
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Neon Night palette: dark panel background baked into every chart so it
# reads consistently whether it's sitting on the dark dashboard or embedded
# in a (light) PDF page.
PANEL = "#10151d"
BLUE = "#3aa0ff"
GREEN = "#35e08a"
RED = "#ff4d6a"
TEXT = "#e8f0f7"
GRID = "#2a3542"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "figure.facecolor": PANEL,
    "axes.facecolor": PANEL,
    "savefig.facecolor": PANEL,
})


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=PANEL)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def mood_trend_chart(logs):
    """Line chart of mood & anxiety over time."""
    if not logs:
        return None
    dates = [datetime.strptime(r["log_date"], "%Y-%m-%d") for r in logs]
    moods = [r["mood_score"] for r in logs]
    anx = [r["anxiety_score"] if r["anxiety_score"] is not None else None for r in logs]

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(dates, moods, color=BLUE, linewidth=2.4, marker="o", markersize=4,
            markerfacecolor=GREEN, markeredgecolor=BLUE, label="Mood")
    if any(a is not None for a in anx):
        ax.plot(dates, anx, color=RED, linewidth=2, linestyle="--", marker="s",
                markersize=3.5, label="Anxiety")

    ax.set_ylim(0, 10.5)
    ax.set_ylabel("Score (1-10)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(frameon=False, loc="upper left", labelcolor=TEXT)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, alpha=0.6, linewidth=0.6)
    ax.set_title("Mood & Anxiety Over Time", fontsize=13, color=BLUE, weight="bold")
    return _fig_to_base64(fig)


def sleep_correlation_chart(logs):
    """Scatter: sleep hours vs mood score."""
    pts = [(r["sleep_hours"], r["mood_score"]) for r in logs if r["sleep_hours"] is not None]
    if len(pts) < 2:
        return None
    xs, ys = zip(*pts)

    fig, ax = plt.subplots(figsize=(5.2, 4))
    ax.scatter(xs, ys, s=70, color=BLUE, alpha=0.85, edgecolor=TEXT, linewidth=0.6)

    # simple trend line
    try:
        import numpy as np
        z = np.polyfit(xs, ys, 1)
        p = np.poly1d(z)
        xline = sorted(xs)
        ax.plot(xline, p(xline), color=GREEN, linewidth=2, linestyle="--")
    except Exception:
        pass

    ax.set_xlabel("Sleep (hours)")
    ax.set_ylabel("Mood score")
    ax.set_ylim(0, 10.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRID, alpha=0.6, linewidth=0.6)
    ax.set_title("Sleep vs. Mood", fontsize=12, color=BLUE, weight="bold")
    return _fig_to_base64(fig)


def exercise_correlation_chart(logs):
    """Scatter: exercise minutes vs mood score."""
    pts = [(r["exercise_minutes"], r["mood_score"]) for r in logs if r["exercise_minutes"] is not None]
    if len(pts) < 2:
        return None
    xs, ys = zip(*pts)

    fig, ax = plt.subplots(figsize=(5.2, 4))
    ax.scatter(xs, ys, s=70, color=GREEN, alpha=0.9, edgecolor=TEXT, linewidth=0.6)

    try:
        import numpy as np
        z = np.polyfit(xs, ys, 1)
        p = np.poly1d(z)
        xline = sorted(xs)
        ax.plot(xline, p(xline), color=RED, linewidth=2, linestyle="--")
    except Exception:
        pass

    ax.set_xlabel("Exercise (minutes)")
    ax.set_ylabel("Mood score")
    ax.set_ylim(0, 10.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRID, alpha=0.6, linewidth=0.6)
    ax.set_title("Exercise vs. Mood", fontsize=12, color=GREEN, weight="bold")
    return _fig_to_base64(fig)


def correlation_stats(logs):
    """Pearson correlation coefficients for sleep/exercise vs mood."""
    import statistics

    def pearson(xs, ys):
        if len(xs) < 2:
            return None
        try:
            return round(statistics.correlation(xs, ys), 2)
        except Exception:
            return None

    sleep_pairs = [(r["sleep_hours"], r["mood_score"]) for r in logs if r["sleep_hours"] is not None]
    ex_pairs = [(r["exercise_minutes"], r["mood_score"]) for r in logs if r["exercise_minutes"] is not None]

    sleep_corr = pearson(*zip(*sleep_pairs)) if len(sleep_pairs) >= 2 else None
    ex_corr = pearson(*zip(*ex_pairs)) if len(ex_pairs) >= 2 else None

    return {"sleep_corr": sleep_corr, "exercise_corr": ex_corr}
