#!/usr/bin/env python3
"""
interpret.py — Claude-powered interpretation of real chart data.

Reads JSON output from astro.py (natal, transit, or synastry) and calls
the Anthropic API to generate a real written reading grounded in the
actual planetary positions and aspects.

Usage:
  # Natal reading
  python3 scripts/astro.py natal [...] | python3 scripts/interpret.py natal

  # Transit reading
  python3 scripts/astro.py transit [...] | python3 scripts/interpret.py transit

  # Synastry reading
  python3 scripts/astro.py synastry [...] | python3 scripts/interpret.py synastry

  # Daily prediction (do/don't)
  python3 scripts/astro.py transit [...] | python3 scripts/interpret.py daily

Reads chart JSON from stdin, writes markdown interpretation to stdout.

Requires ANTHROPIC_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


API_URL = "https://api.anthropic.com/v1/messages"
MODEL   = "claude-sonnet-4-6"


def call_claude(system_prompt: str, user_content: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "model": MODEL,
        "max_tokens": 1800,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            return body["content"][0]["text"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


# ── System prompts ────────────────────────────────────────────────────────────

NATAL_SYSTEM = """You are an experienced psychological astrologer writing a
natal chart interpretation. The chart data you receive is astronomically
accurate — real Swiss Ephemeris calculations, not guessed positions.

Write a personal, insightful reading structured as:

1. **The Core Trinity** — Sun, Moon, Ascendant together as one unified
   picture of the person's nature. 3-4 sentences.

2. **Defining Aspects** — Pick the 3-4 tightest-orb aspects (lowest orbit
   values) and explain what each tension or harmony actually feels like in
   daily life. Be specific to this chart, not generic.

3. **Life Themes** — Note any notable planetary concentrations (sign/house
   stelliums, dominant element/quality) and what area of life they channel
   energy toward.

4. **A Reflection** — One closing observation that ties the chart together.
   Something the person can actually use.

Tone: psychologically grounded, direct, warm. Not fortune-telling, not
generic horoscope content. Every sentence should feel like it was written
for *this* chart specifically. Use the actual sign names, house numbers, and
aspect names from the data."""

TRANSIT_SYSTEM = """You are an astrologer writing a personalized transit
forecast. You have both a natal chart and the current sky's planetary
positions, plus the aspects currently transiting planets are making to
the natal chart.

Write a forecast structured as:

1. **Current Sky Summary** — What the major transiting planets are doing
   right now (1-2 sentences each for slow movers: Jupiter, Saturn, Uranus,
   Neptune, Pluto).

2. **Active Transits to Your Chart** — Go through the transiting aspects
   list. Focus on tight-orb aspects (under 2°) first — these are the live,
   active themes right now. Explain what each means in plain language.

3. **Do / Don't This Period** — Based on the active transits, give 3 clear
   action items: what to lean into, what to avoid, what to be aware of.

Tone: practical, grounding. This should read like advice from a trusted
astrologer, not a vague magazine horoscope. Use real planet and aspect names."""

SYNASTRY_SYSTEM = """You are an astrologer writing a relationship
compatibility reading based on real synastry data.

Structure:
1. **The Connection at a Glance** — Lead with the relationship score and
   its category. Describe the overall quality of the connection in 2-3
   sentences.

2. **Where You Flow** — Pick the 3-4 harmonious cross-aspects (trines,
   sextiles, conjunctions to benefics) and explain the ease or resonance
   they create.

3. **Where You Friction** — Pick the 2-3 challenging aspects (squares,
   oppositions) and explain the growth edge they represent. Frame as
   opportunity, not doom.

4. **The Core Dynamic** — Sun-Moon, Venus-Mars, any Ascendant aspects:
   what's the emotional and attraction chemistry?

5. **One Honest Observation** — Something real about this connection that
   both people should know.

Tone: honest, balanced, not rose-tinted. Real compatibility readings
name both gifts and challenges."""

DAILY_SYSTEM = """You are an astrologer creating a practical daily
prediction based on real transit data.

Output a daily briefing with:

## Today's Astrology — [extract the transit date from the data]

**Overall Energy:** One sentence — what's the vibe of the day.

**Your 4 Life Areas:**
- 🟢/🟡/🔴 **Work & Ambition** — what's activated, what to do/avoid
- 🟢/🟡/🔴 **Relationships** — same
- 🟢/🟡/🔴 **Health & Energy** — same
- 🟢/🟡/🔴 **Money & Resources** — same

(🟢 = favorable, 🟡 = neutral/mixed, 🔴 = caution)

**Do today:** 2-3 concrete actions aligned with the sky
**Avoid today:** 2-3 specific things to sidestep
**Best window:** Based on the Moon's position, suggest the best part of
the day for important actions.

Keep it under 300 words. Make it feel like a real personalized briefing,
not a generic horoscope."""


# ── Main ──────────────────────────────────────────────────────────────────────

def summarize_natal(data: dict) -> str:
    """Compact the natal JSON to avoid burning too many tokens."""
    planets = data.get("planets", {})
    angles  = data.get("angles", {})
    aspects = sorted(data.get("aspects", []), key=lambda a: a.get("orb", 99))

    lines = [f"# Natal Chart — {data['name']}",
             f"Born: {data['birth_data']['local_datetime']}, "
             f"{data['birth_data']['city']}, {data['birth_data']['nation']}",
             ""]

    lines.append("## Planets")
    for k, p in planets.items():
        retro = " (R)" if p.get("retrograde") else ""
        lines.append(f"  {p['name']}: {p['sign']} {p['degree_in_sign']:.1f}° "
                     f"— {p.get('house','').replace('_',' ')}{retro}")

    lines.append("\n## Angles")
    for k, a in angles.items():
        lines.append(f"  {a['name']}: {a['sign']} {a['degree_in_sign']:.1f}°")

    lines.append(f"\n## Aspects (top 15 by orb)")
    for a in aspects[:15]:
        lines.append(f"  {a['point_1']} {a['aspect']} {a['point_2']} — orb {a['orb']}°")

    lp = data.get("lunar_phase", {})
    if lp:
        lines.append(f"\nLunar phase: {lp.get('moon_phase_name','')} {lp.get('moon_emoji','')}")

    return "\n".join(lines)


def summarize_transit(data: dict) -> str:
    t_planets = data.get("transiting_planets", {})
    aspects   = sorted(data.get("transits_to_natal_chart", []),
                       key=lambda a: a.get("orb", 99))

    lines = [f"# Transit Report — {data['natal_name']}",
             f"Transit datetime (UTC): {data['transit_datetime_utc']}", ""]

    lines.append("## Current Sky (transiting planets)")
    for k, p in t_planets.items():
        retro = " (R)" if p.get("retrograde") else ""
        lines.append(f"  {p['name']}: {p['sign']} {p['degree_in_sign']:.1f}°{retro}")

    lines.append(f"\n## Active Transits to Natal Chart (all under requested orb)")
    for a in aspects:
        lines.append(f"  Transit {a['transiting_planet']} {a['aspect']} "
                     f"natal {a['natal_point']} — orb {a['orb']}°")

    return "\n".join(lines)


def summarize_synastry(data: dict) -> str:
    aspects = sorted(data.get("aspects", []), key=lambda a: a.get("orb", 99))
    score   = data.get("relationship_score", {})

    lines = [f"# Synastry — {data['person_1']} & {data['person_2']}",
             f"Relationship score: {score.get('score')} "
             f"({score.get('description')}, "
             f"destiny sign: {score.get('is_destiny_sign')})",
             "",
             "## Cross-chart Aspects (top 20 by orb)"]
    for a in aspects[:20]:
        lines.append(f"  {data['person_1']} {a['person_1_point']} "
                     f"{a['aspect']} "
                     f"{data['person_2']} {a['person_2_point']} — orb {a['orb']}°")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Pipe astro.py JSON through Claude for a written interpretation.")
    parser.add_argument("mode", choices=["natal", "transit", "synastry", "daily"],
                        help="natal | transit | synastry | daily")
    args = parser.parse_args()

    raw = json.load(sys.stdin)

    if args.mode == "natal":
        content = summarize_natal(raw)
        result  = call_claude(NATAL_SYSTEM, content)

    elif args.mode == "transit":
        content = summarize_transit(raw)
        result  = call_claude(TRANSIT_SYSTEM, content)

    elif args.mode == "daily":
        content = summarize_transit(raw)
        result  = call_claude(DAILY_SYSTEM, content)

    elif args.mode == "synastry":
        content = summarize_synastry(raw)
        result  = call_claude(SYNASTRY_SYSTEM, content)

    print(result)


if __name__ == "__main__":
    main()
