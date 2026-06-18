#!/usr/bin/env python3
"""
predict.py — Rule-based daily prediction engine.

Reads transit JSON from astro.py transit and applies astrological
timing rules to produce a scored daily forecast without needing the
Anthropic API. Works offline, instant.

Usage:
  python3 scripts/astro.py transit [...] | python3 scripts/predict.py

Outputs a structured JSON with:
  - day_score: overall day rating (0-100)
  - category: EXCELLENT / GOOD / NEUTRAL / CAUTION / DIFFICULT
  - areas: per-life-area scores and notes
  - do_today: list of recommended actions
  - avoid_today: list of things to avoid
  - best_window: best time of day based on Moon
  - active_transits: condensed list of what's active
"""

import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# ── Rule tables ───────────────────────────────────────────────────────────────

# (transiting_planet, aspect, natal_planet_or_point) → (area, modifier, note)
# areas: work, relationships, health, money, general
# modifier: +2 strong positive, +1 mild positive, 0 neutral, -1 mild caution, -2 strong caution

RULES: List[Tuple[str, str, str, str, int, str]] = [
    # planet, aspect, natal_point, area, score_delta, note
    # SUN transits
    ("Sun", "conjunction", "Sun",          "work",          2, "Peak self-expression day — initiate, lead, be visible"),
    ("Sun", "conjunction", "Moon",         "relationships", 1, "Emotions and identity aligned — good for personal conversations"),
    ("Sun", "conjunction", "Saturn",       "work",         -1, "Discipline demanded — avoid shortcuts, do the serious work"),
    ("Sun", "conjunction", "Mars",         "health",       -1, "High energy but accident-prone — channel it, don't rush"),
    ("Sun", "trine",       "Jupiter",      "work",          2, "Excellent for expansion, recognition, and outreach"),
    ("Sun", "trine",       "Venus",        "relationships", 2, "Great for social connection, charm, creative work"),
    ("Sun", "square",      "Saturn",       "work",         -2, "Obstacles and delays — plan, don't force"),
    ("Sun", "square",      "Mars",         "health",       -1, "Conflict energy — stay measured, avoid confrontations"),
    ("Sun", "opposition",  "Saturn",       "work",         -2, "Tension with authority or structure — lay low, be patient"),

    # MOON transits (fast-moving, day-level detail)
    ("Moon", "conjunction", "Venus",       "relationships", 2, "Warm, receptive energy — great for dates, social plans"),
    ("Moon", "conjunction", "Jupiter",     "general",       2, "Optimistic mood, good for new starts and meetings"),
    ("Moon", "conjunction", "Saturn",      "general",      -1, "Heaviness, solitude — good for focused solitary work"),
    ("Moon", "conjunction", "Mars",        "health",       -1, "Irritability, impulsive reactions — breathe before responding"),
    ("Moon", "conjunction", "Pluto",       "relationships",-1, "Emotional intensity — avoid power struggles"),
    ("Moon", "trine",       "Sun",         "general",       2, "Emotional clarity and flow — trust instincts today"),
    ("Moon", "trine",       "Venus",       "relationships", 2, "Easy social flow, good for any heart-centred activity"),
    ("Moon", "trine",       "Jupiter",     "money",         1, "Optimism supports financial decisions — research today"),
    ("Moon", "square",      "Saturn",      "general",      -1, "Emotional blocks — not the day for sensitive conversations"),
    ("Moon", "square",      "Mars",        "health",       -1, "Reactive energy — schedule demanding physical work, not meetings"),
    ("Moon", "opposition",  "Moon",        "general",      -1, "Full Moon energy — emotions amplified, sleep may be disrupted"),

    # MERCURY transits
    ("Mercury", "conjunction", "Mercury",  "work",          1, "Sharp thinking — great for writing, negotiations, learning"),
    ("Mercury", "conjunction", "Mars",     "work",          1, "Direct communication — good for assertive conversations"),
    ("Mercury", "conjunction", "Saturn",   "work",         -1, "Mental caution — re-check everything, avoid signing contracts"),
    ("Mercury", "trine",       "Jupiter",  "work",          2, "Excellent for big-picture thinking, presentations, deals"),
    ("Mercury", "square",      "Neptune",  "work",         -1, "Confusion risk — clarify before acting, re-read emails"),
    ("Mercury", "square",      "Saturn",   "work",         -2, "Communication blocks — avoid major negotiations today"),
    ("Mercury", "opposition",  "Mercury",  "work",         -1, "Mercury opposition — miscommunication possible, double-check"),

    # VENUS transits
    ("Venus", "conjunction", "Venus",      "relationships", 2, "Your most magnetic day — lean into love and creativity"),
    ("Venus", "conjunction", "Jupiter",    "money",         2, "Financial luck and social charm aligned — act on it"),
    ("Venus", "conjunction", "Mars",       "relationships", 2, "Attraction and passion elevated — romantic energy high"),
    ("Venus", "conjunction", "Saturn",     "relationships",-1, "Relationship tests or seriousness — have the real conversation"),
    ("Venus", "trine",       "Mars",       "relationships", 2, "Creative and romantic energy flows — collaborate, connect"),
    ("Venus", "square",      "Mars",       "relationships",-1, "Tension in relationships — avoid ultimatums"),
    ("Venus", "square",      "Pluto",      "relationships",-2, "Obsessive or controlling energy in relationships — pull back"),
    ("Venus", "opposition",  "Venus",      "relationships",-1, "Relationship friction — needs vs others' needs in conflict"),

    # MARS transits
    ("Mars", "conjunction",  "Sun",        "work",          2, "Drive and ambition surge — take decisive action"),
    ("Mars", "conjunction",  "Jupiter",    "work",          2, "Excellent for bold moves, leadership, and ambition"),
    ("Mars", "conjunction",  "Saturn",     "work",         -1, "Frustration with obstacles — be patient, work systematically"),
    ("Mars", "conjunction",  "Pluto",      "work",          1, "Intense focus available — deep work, transformation possible"),
    ("Mars", "trine",        "Sun",        "health",        2, "Physical energy peak — exercise, sports, active projects"),
    ("Mars", "square",       "Sun",        "health",       -2, "Conflict and frustration — avoid ego battles, stay grounded"),
    ("Mars", "square",       "Mars",       "health",       -1, "Accident-prone, hot-tempered — slow down physically"),
    ("Mars", "opposition",   "Mars",       "general",      -2, "Energy clash — major conflicts possible, choose battles wisely"),

    # JUPITER transits
    ("Jupiter", "conjunction", "Sun",      "work",          2, "Expansion, recognition, opportunity — a major lucky window"),
    ("Jupiter", "conjunction", "Jupiter",  "general",       2, "Jupiter return — great year marker, growth and blessings"),
    ("Jupiter", "conjunction", "Venus",    "money",         2, "Financial and romantic luck aligned — invest, connect"),
    ("Jupiter", "trine",       "Sun",      "work",          2, "Smooth expansion — excellent for applications, launches"),
    ("Jupiter", "trine",       "Moon",     "relationships", 2, "Emotional generosity — social life and wellbeing flourish"),
    ("Jupiter", "square",      "Sun",      "work",         -1, "Overconfidence risk — excellent energy but temper the enthusiasm"),

    # SATURN transits
    ("Saturn", "conjunction", "Sun",       "work",         -2, "Saturn return or major test — restructure, not expand"),
    ("Saturn", "conjunction", "Moon",      "general",      -1, "Emotional heaviness — self-care, boundaries, solitude"),
    ("Saturn", "trine",       "Sun",       "work",          2, "Hard work rewarded — long-term projects pay off now"),
    ("Saturn", "trine",       "Saturn",    "work",          1, "Stability and structure — good for planning and building"),
    ("Saturn", "square",      "Sun",       "work",         -2, "Major resistance — don't quit, but reassess the approach"),
    ("Saturn", "square",      "Moon",      "general",      -2, "Emotional isolation — be gentle with self, don't isolate"),
    ("Saturn", "opposition",  "Sun",       "work",         -1, "Others impose limits — negotiate, adapt, stay patient"),

    # URANUS transits
    ("Uranus", "conjunction", "Sun",       "work",          1, "Sudden changes and breakthroughs — stay flexible, embrace change"),
    ("Uranus", "conjunction", "Moon",      "general",      -1, "Emotional disruption — unexpected events in personal life"),
    ("Uranus", "trine",       "Sun",       "work",          2, "Brilliant innovations and breakthroughs — experiment boldly"),
    ("Uranus", "square",      "Sun",       "work",         -1, "Disruption and instability — avoid major commitments"),
    ("Uranus", "square",      "Moon",      "general",      -1, "Unpredictable emotions — ground yourself before big decisions"),

    # NEPTUNE transits
    ("Neptune", "trine",    "Venus",       "relationships", 1, "Spiritual and creative connection — art, music, romance"),
    ("Neptune", "conjunction", "Sun",      "work",         -1, "Confusion and idealism — verify facts, avoid escapism"),
    ("Neptune", "square",   "Mercury",     "work",         -2, "Serious confusion risk — postpone important decisions/contracts"),
    ("Neptune", "square",   "Sun",         "work",         -1, "Identity fog — journaling and meditation help, avoid big launches"),

    # PLUTO transits
    ("Pluto", "trine",     "Sun",          "work",          2, "Deep transformation energy — powerful period for reinvention"),
    ("Pluto", "conjunction", "Sun",        "work",          1, "Life-changing period — deep change is happening, work with it"),
    ("Pluto", "square",    "Sun",          "work",         -2, "Power struggles and forced change — avoid control battles"),
    ("Pluto", "square",    "Moon",         "general",      -2, "Emotional upheaval — therapy, journaling, not suppression"),
    ("Pluto", "opposition", "Sun",         "work",         -1, "Confrontations with power — integrity is your shield"),
]

# Build lookup dict
RULE_LOOKUP: Dict[Tuple[str,str,str], List[Tuple[str,int,str]]] = {}
for planet, aspect, natal, area, delta, note in RULES:
    key = (planet, aspect, natal)
    RULE_LOOKUP.setdefault(key, []).append((area, delta, note))


AREA_LABELS = {
    "work":          "Work & Ambition",
    "relationships": "Relationships",
    "health":        "Health & Energy",
    "money":         "Money & Resources",
    "general":       "Overall Energy",
}

SCORE_EMOJI = {
    "work": "💼",
    "relationships": "❤️",
    "health": "⚡",
    "money": "💰",
    "general": "🌟",
}

# Moon sign → best window suggestion
MOON_WINDOWS = {
    "Ari": "Morning (high physical energy) is best for action; evenings may be restless.",
    "Tau": "Midday onwards — slow mornings, productive afternoons.",
    "Gem": "Morning communication is sharp; afternoon for research.",
    "Can": "Evenings for personal matters; mornings for routine.",
    "Leo": "Morning and early afternoon peak — take center stage.",
    "Vir": "Morning detail work; afternoon analysis and organisation.",
    "Lib": "Late morning for negotiations and meetings; avoid rushing.",
    "Sco": "Afternoon and evening for deep work and serious conversations.",
    "Sag": "Full-day energy but best momentum in the morning.",
    "Cap": "Morning for ambitious tasks; schedule discipline early.",
    "Aqu": "Afternoon for creative and collaborative work.",
    "Pis": "Early morning or late evening — avoid important decisions at peak hours.",
}


def score_to_category(score: int) -> str:
    if score >= 70: return "EXCELLENT"
    if score >= 55: return "GOOD"
    if score >= 40: return "NEUTRAL"
    if score >= 25: return "CAUTION"
    return "DIFFICULT"


def score_to_emoji(score: int) -> str:
    if score >= 70: return "🟢"
    if score >= 55: return "🟢"
    if score >= 40: return "🟡"
    if score >= 25: return "🟡"
    return "🔴"


def main():
    data = json.load(sys.stdin)

    transits      = data.get("transits_to_natal_chart", [])
    t_planets     = data.get("transiting_planets", {})
    transit_dt    = data.get("transit_datetime_utc", "")
    natal_name    = data.get("natal_name", "You")

    # Area accumulators: base 50
    area_scores = {"work": 50, "relationships": 50, "health": 50, "money": 50, "general": 50}
    area_notes: Dict[str, List[str]] = {k: [] for k in area_scores}
    active_transits = []

    for t in transits:
        planet   = t.get("transiting_planet", "")
        aspect   = t.get("aspect", "")
        natal_pt = t.get("natal_point", "")
        orb      = t.get("orb", 99)

        # orb weight: tighter = stronger effect
        orb_weight = 1.5 if orb < 1 else (1.2 if orb < 2 else 1.0)

        matched = RULE_LOOKUP.get((planet, aspect, natal_pt))
        if matched:
            for (area, delta, note) in matched:
                weighted_delta = round(delta * orb_weight * 10)
                area_scores[area] = max(0, min(100, area_scores[area] + weighted_delta))
                area_notes[area].append(note)
                active_transits.append({
                    "transit": f"{planet} {aspect} natal {natal_pt}",
                    "orb": orb,
                    "area": AREA_LABELS[area],
                    "note": note,
                })

    # Clamp all scores 0-100
    for k in area_scores:
        area_scores[k] = max(0, min(100, area_scores[k]))

    overall_score = round(sum(area_scores.values()) / len(area_scores))

    # Best window from Moon sign
    moon = t_planets.get("moon", {})
    moon_sign = moon.get("sign", "")
    best_window = MOON_WINDOWS.get(moon_sign, "Check the Moon's position for timing guidance.")

    # Do / Avoid from top positive/negative notes
    all_notes_with_delta = []
    for t in transits:
        planet   = t.get("transiting_planet", "")
        aspect   = t.get("aspect", "")
        natal_pt = t.get("natal_point", "")
        matched = RULE_LOOKUP.get((planet, aspect, natal_pt))
        if matched:
            for (area, delta, note) in matched:
                all_notes_with_delta.append((delta, note))

    sorted_notes = sorted(all_notes_with_delta, key=lambda x: x[0], reverse=True)
    do_today    = list(dict.fromkeys(n for d, n in sorted_notes if d > 0))[:4]
    avoid_today = list(dict.fromkeys(n for d, n in sorted_notes if d < 0))[:4]

    # Build output
    result = {
        "name":          natal_name,
        "date":          transit_dt[:10] if transit_dt else "today",
        "overall_score": overall_score,
        "category":      score_to_category(overall_score),
        "emoji":         score_to_emoji(overall_score),
        "moon_in":       f"{moon_sign} {moon.get('degree_in_sign', 0):.1f}°" if moon_sign else "unknown",
        "areas": {
            k: {
                "label":    AREA_LABELS[k],
                "emoji":    SCORE_EMOJI[k],
                "score":    area_scores[k],
                "rating":   score_to_emoji(area_scores[k]),
                "notes":    area_notes[k][:3],
            }
            for k in area_scores
        },
        "do_today":       do_today,
        "avoid_today":    avoid_today,
        "best_window":    best_window,
        "active_transits_count": len(active_transits),
        "active_transits": sorted(active_transits, key=lambda x: x["orb"])[:10],
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
