"""
Auro — Insights & Lifestyle Plan
Rule-based (deterministic, no external calls) narrative analysis of a
person's mood logs, plus a generic evidence-informed weekly routine
template lightly adjusted to their own averages. Intentionally avoids
prescriptive numbers (calories, macros, medication, exact dosages) —
this is a general-wellness scaffold, not clinical or dietary advice.
"""


def _trend_direction(logs):
    """Compare the first half of entries to the second half to describe
    a rough direction. Returns one of: 'improving', 'declining', 'steady',
    or None if there isn't enough data to say anything meaningful."""
    if len(logs) < 4:
        return None
    mid = len(logs) // 2
    first_half = logs[:mid]
    second_half = logs[mid:]
    avg1 = sum(r["mood_score"] for r in first_half) / len(first_half)
    avg2 = sum(r["mood_score"] for r in second_half) / len(second_half)
    diff = avg2 - avg1
    if diff >= 0.75:
        return "improving"
    if diff <= -0.75:
        return "declining"
    return "steady"


def build_graph_analysis(logs, stats):
    """Returns a list of short narrative paragraphs (strings) interpreting
    the mood/sleep/exercise/anxiety data — the kind of plain-language
    summary that makes the charts easier to read at a glance."""
    if not logs:
        return ["No entries yet — once a few days are logged, this section will "
                "summarize the trend in plain language."]

    paragraphs = []

    avg_mood = sum(r["mood_score"] for r in logs) / len(logs)
    anx_vals = [r["anxiety_score"] for r in logs if r["anxiety_score"] is not None]
    sleep_vals = [r["sleep_hours"] for r in logs if r["sleep_hours"] is not None]
    ex_vals = [r["exercise_minutes"] for r in logs if r["exercise_minutes"] is not None]

    direction = _trend_direction(logs)
    if direction == "improving":
        paragraphs.append(
            f"Mood has been trending upward across the {len(logs)} logged day(s), "
            f"with the more recent entries sitting noticeably higher than the earlier ones."
        )
    elif direction == "declining":
        paragraphs.append(
            f"Mood has been trending downward across the {len(logs)} logged day(s), "
            f"with the more recent entries sitting lower than the earlier ones. "
            f"That kind of stretch is worth flagging to a doctor or therapist if it continues."
        )
    elif direction == "steady":
        paragraphs.append(
            f"Mood has stayed fairly steady across the {len(logs)} logged day(s), "
            f"averaging around {avg_mood:.1f} out of 10, without a strong upward or downward trend."
        )
    else:
        paragraphs.append(
            f"Average mood across the logged entries so far is {avg_mood:.1f} out of 10. "
            f"A few more days of logging will make it possible to describe a trend here."
        )

    if anx_vals:
        avg_anx = sum(anx_vals) / len(anx_vals)
        if avg_anx >= 7:
            paragraphs.append(
                f"Anxiety has been running high, averaging {avg_anx:.1f} out of 10 across logged days. "
                f"Sustained anxiety at this level is a reasonable thing to bring up with a professional."
            )
        elif avg_anx >= 4:
            paragraphs.append(f"Anxiety has averaged {avg_anx:.1f} out of 10 — moderate, and worth keeping an eye on.")
        else:
            paragraphs.append(f"Anxiety has averaged {avg_anx:.1f} out of 10 — relatively low across logged days.")

    if sleep_vals:
        avg_sleep = sum(sleep_vals) / len(sleep_vals)
        if avg_sleep < 6:
            paragraphs.append(
                f"Average sleep has been {avg_sleep:.1f} hours a night, below the generally "
                f"recommended 7–9 hours for adults. Short sleep is one of the more common, "
                f"and more fixable, contributors to low mood and high anxiety."
            )
        else:
            paragraphs.append(f"Average sleep has been {avg_sleep:.1f} hours a night, within a healthy range.")

    if stats.get("sleep_corr") is not None:
        r = stats["sleep_corr"]
        if r >= 0.3:
            paragraphs.append(f"There's a positive relationship between sleep and mood in this data (r = {r}) — nights with more sleep tend to line up with better mood days.")
        elif r <= -0.3:
            paragraphs.append(f"There's an inverse relationship between sleep and mood in this data (r = {r}), which is unusual and may be worth discussing with a professional.")

    if ex_vals:
        avg_ex = sum(ex_vals) / len(ex_vals)
        paragraphs.append(f"Average logged exercise has been {avg_ex:.0f} minutes a day.")

    if stats.get("exercise_corr") is not None:
        r = stats["exercise_corr"]
        if r >= 0.3:
            paragraphs.append(f"Exercise shows a positive relationship with mood in this data (r = {r}) — more active days tend to line up with better mood.")

    return paragraphs


def build_lifestyle_plan(logs):
    """Returns a dict describing a generic weekday/weekend routine, meal
    structure, exercise plan, and engagement activities — lightly adjusted
    based on the person's own averages (e.g. suggesting an earlier wind-down
    if their average sleep is low). No calorie counts, macros, or specific
    diet prescriptions — general structure only."""

    sleep_vals = [r["sleep_hours"] for r in logs if r["sleep_hours"] is not None] if logs else []
    avg_sleep = sum(sleep_vals) / len(sleep_vals) if sleep_vals else None

    ex_vals = [r["exercise_minutes"] for r in logs if r["exercise_minutes"] is not None] if logs else []
    avg_ex = sum(ex_vals) / len(ex_vals) if ex_vals else None

    wind_down_note = (
        "Sleep has been running low in your logs — try moving wind-down 30–45 minutes earlier "
        "for a week and see if mood/anxiety shift."
        if avg_sleep is not None and avg_sleep < 6
        else "Keep a consistent wind-down time, even on weekends."
    )

    exercise_note = (
        "Start small — even 10–15 minutes of walking most days is a reasonable place to begin."
        if avg_ex is not None and avg_ex < 15
        else "Current activity level looks reasonable — focus on consistency over intensity."
    )

    weekday_routine = [
        ("6:30–7:00 AM", "Wake, natural light, water before coffee/tea"),
        ("7:00–7:30 AM", "Breakfast — protein + something whole-grain or fruit"),
        ("7:30–9:00 AM", "Morning routine / commute / focused work block"),
        ("9:00 AM–1:00 PM", "Work block, with one 5–10 min break each hour"),
        ("1:00–1:45 PM", "Lunch, away from the desk/screen if possible"),
        ("1:45–5:30 PM", "Work block; a short walk or stretch mid-afternoon"),
        ("5:30–6:15 PM", "Exercise — walk, gym, sport, or home workout"),
        ("6:15–6:45 PM", "Wind down from work — shower, change, no email"),
        ("6:45–7:30 PM", "Dinner, lighter than lunch, 2–3 hrs before bed"),
        ("7:30–9:30 PM", "Personal time — hobby, family/friends, low-key activity"),
        ("9:30–10:30 PM", "Wind-down — dim lights, no screens, reading/journaling"),
        ("10:30–11:00 PM", "Sleep"),
    ]

    weekend_routine = [
        ("8:00–8:30 AM", "Wake without an alarm if possible — same general window as weekdays"),
        ("8:30–9:30 AM", "Slow breakfast, no rush"),
        ("9:30–12:00 PM", "Errands, chores, or a project — something with visible progress"),
        ("12:00–1:00 PM", "Lunch"),
        ("1:00–4:00 PM", "Longer activity block — outdoors, social plans, a hobby, exercise"),
        ("4:00–6:00 PM", "Downtime — rest, light reading, a show, a nap if needed"),
        ("6:00–7:00 PM", "Dinner with others if possible"),
        ("7:00–9:30 PM", "Social time, hobby, or a low-pressure creative activity"),
        ("9:30–11:00 PM", "Wind-down, similar to weekdays — try not to let this drift too late"),
    ]

    eating_structure = [
        "Aim for three main meals plus 1–2 small snacks, spaced roughly 3–4 hours apart, "
        "rather than skipping meals and over-eating later.",
        "Build each main meal around a protein source, a vegetable or fruit, and a whole-grain "
        "or starchy carb — the classic balanced-plate structure, not a specific diet.",
        "Keep a consistent breakfast time — it anchors appetite and energy for the rest of the day.",
        "Hydrate through the day; a glass of water on waking and one with each meal is a simple habit to start.",
        "Keep dinner lighter and earlier where possible — 2–3 hours before bed tends to help sleep quality.",
        "This is a general structure, not a diet plan — a dietitian is the right person for calorie or macro targets.",
    ]

    exercise_plan = [
        exercise_note,
        "3–4 days/week: 20–30 min of moderate cardio (brisk walk, cycling, swimming, or a sport).",
        "2 days/week: basic strength work (bodyweight — squats, push-ups, rows — or light weights).",
        "Daily: a few minutes of stretching or mobility, especially after long sitting.",
        "One full rest day a week is part of the plan, not a failure of it.",
    ]

    engagement_activities = [
        "One creative or hands-on hobby a week (music, drawing, cooking, writing, building something).",
        "Regular contact with at least one friend or family member outside of work/study.",
        "A short daily reflection — even 3 lines in a journal, or the CBT thought-record already in Auro.",
        "Time outdoors most days, even 10 minutes — daylight exposure genuinely helps mood regulation.",
        "One low-stakes 'just for fun' activity a week with no productivity goal attached.",
    ]

    return {
        "wind_down_note": wind_down_note,
        "weekday_routine": weekday_routine,
        "weekend_routine": weekend_routine,
        "eating_structure": eating_structure,
        "exercise_plan": exercise_plan,
        "engagement_activities": engagement_activities,
    }
