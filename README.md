# astrology-chart

A Claude Code / Claude.ai skill that generates **real, astronomically
calculated** natal charts, transits, and synastry — not LLM-guessed zodiac
content.

Under the hood it's Swiss Ephemeris-grade calculation (via
[kerykeion](https://github.com/g-battaglia/kerykeion)), the same class of
engine professional astrology software uses. Every planet position, house
cusp, and aspect comes from real orbital math, computed offline, no API
keys, no internet required at runtime.

Claude reads the skill, calls the script for ground-truth numbers, then
writes the actual interpretation — combining real data with language
generation instead of either pure hallucination or a static lookup table.

## Why this exists

Ask any LLM for "my birth chart" today and it will, by default, confidently
invent planetary placements. They're plausible-sounding and almost always
wrong. This skill fixes that by giving Claude an actual ephemeris to query
before it writes a single word of interpretation.

## What it does

- **Natal charts** — full planet/house/aspect breakdown for a birth date,
  time, and location
- **Transits** — what's currently (or on any date) activating a natal chart
- **Synastry** — compatibility between two charts, including a numeric
  relationship score
- **Chart wheels** — real SVG chart wheel images, not generated illustrations

## Install

As a Claude Code skill:
```bash
git clone https://github.com/<your-username>/astrology-chart.git ~/.claude/skills/astrology-chart
cd ~/.claude/skills/astrology-chart
pip install -r requirements.txt
```

Or just clone it anywhere and point Claude at the `SKILL.md`.

## Example

```
You: What's my birth chart? Born June 15 2000, 2:30pm, Pune, India.
```
Claude looks up Pune's coordinates/timezone, runs:
```bash
python3 scripts/astro.py natal --name "You" --year 2000 --month 6 --day 15 \
  --hour 14 --minute 30 --lat 18.5204 --lng 73.8567 --tz "Asia/Kolkata"
```
...and writes a real reading from the actual returned Sun/Moon/Ascendant/
aspect data — Gemini Sun in the 9th house, Sagittarius Moon, Libra Rising,
etc., not a guess.

## Structure

```
astrology-chart/
├── SKILL.md                          # what Claude reads to use this skill
├── scripts/astro.py                  # natal / transit / synastry / svg CLI
├── references/interpretation_guide.md # sign/house/aspect meanings, writing guidance
├── examples/                         # sample output
└── requirements.txt
```

## CLI directly

You don't need Claude to use this — it's a normal CLI:

```bash
python3 scripts/astro.py natal --help
python3 scripts/astro.py transit --help
python3 scripts/astro.py synastry --help
python3 scripts/astro.py svg --help
```

## License

MIT for this repo's code. `kerykeion`/`pyswisseph` carry their own licenses
(AGPL-3.0 / Swiss Ephemeris license) — see their respective repos for terms,
especially around commercial use of the ephemeris data.
