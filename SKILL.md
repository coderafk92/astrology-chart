---
name: astrology-chart
description: Generate real, astronomically-calculated natal (birth) charts, planetary transits, and synastry/compatibility readings using Swiss Ephemeris data — not invented or guessed placements. Use this skill whenever the user asks for their birth chart, natal chart, zodiac sign placements, "what's my rising sign," daily/current transits, horoscope grounded in real planetary positions, relationship/compatibility astrology between two people, or wants an SVG chart wheel image. Always use this skill instead of generating astrology content from memory — planetary positions, houses, and aspects must come from the scripts here, never guessed.
---

# Astrology Chart

Real astrology, not LLM guesswork. This skill wraps a genuine Swiss Ephemeris
calculation engine (via the `kerykeion` Python library) so every planetary
position, house cusp, and aspect is astronomically accurate — the same class
of calculation professional astrology software uses. Claude's job is to
collect clean birth data, run the script, and then write the actual
interpretation in natural language.

**Never invent zodiac placements, house positions, or aspects from memory.**
Always run the script and read real numbers back before writing any
interpretation. If you skip the script and guess, the chart will almost
certainly be astronomically wrong.

## When to use this

- "What's my birth chart / natal chart?"
- "What's my rising sign / moon sign?"
- "What are today's transits for me?"
- "Are we compatible?" / synastry / relationship astrology between two people
- "Draw/show my chart wheel"
- Any astrology request where real planetary positions matter (as opposed to
  generic "Geminis are..." personality-type content, which doesn't need this
  skill)

## Step 1: Collect birth data

You need, for each person:
- Date of birth (year, month, day)
- Time of birth (hour, minute — 24h format). If the user doesn't know their
  exact birth time, ask once; if they truly don't know, you can proceed with
  12:00 noon but **explicitly tell them** the Ascendant, houses, and Moon
  position may be inaccurate (the Moon moves ~12-13°/day, houses depend
  entirely on exact time).
- Birth location (city, country)

**You need latitude, longitude, and an IANA timezone string for the birth
location** (e.g. `Asia/Kolkata`, `America/New_York`). The script does not
geocode city names. If you don't already know the coordinates and timezone
for the city:
- Use your own knowledge for well-known cities (most capitals and major
  cities you can place confidently)
- Otherwise, web_search for "[city] latitude longitude timezone"
- Use the timezone that was *in effect at the time of birth* if it's a
  historical date with DST or zone changes — mention this caveat if relevant

Never fabricate coordinates. A few degrees of longitude error can shift the
houses meaningfully; get this right or tell the user you're approximating.

## Step 2: Run the script

All commands are run from this skill's directory:

```bash
python3 scripts/astro.py natal \
  --name "Aakash" --year 2002 --month 8 --day 20 --hour 9 --minute 15 \
  --lat 18.5204 --lng 73.8567 --tz "Asia/Kolkata" --city "Pune" --nation "IN"
```

This prints JSON: every planet's sign/degree/house, the four angles
(Ascendant, Descendant, MC, IC), all 12 house cusps, lunar phase, and every
notable aspect between points. **Read this JSON before writing anything** —
it is the ground truth for the chart.

### Other commands

**Current/specified-date transits against a natal chart:**
```bash
python3 scripts/astro.py transit \
  --name "Aakash" --year 2002 --month 8 --day 20 --hour 9 --minute 15 \
  --lat 18.5204 --lng 73.8567 --tz "Asia/Kolkata" \
  [--t-year 2026 --t-month 6 --t-day 17]   # omit to use right now
```
Omit `--t-*` flags entirely to get transits for the current moment. Add
`--max-orb 2` to tighten/loosen which aspects count as "active" (default 3°).

**Synastry / compatibility between two people:**
```bash
python3 scripts/astro.py synastry \
  --p1-name "Aakash" --p1-year 2002 --p1-month 8 --p1-day 20 --p1-hour 9 --p1-minute 15 \
  --p1-lat 18.5204 --p1-lng 73.8567 --p1-tz "Asia/Kolkata" \
  --p2-name "Partner" --p2-year 2001 --p2-month 3 --p2-day 5 --p2-hour 18 --p2-minute 0 \
  --p2-lat 19.0760 --p2-lng 72.8777 --p2-tz "Asia/Kolkata"
```
Returns a numeric relationship score (Ciro Discepolo method — 0-5 Minimal up
to 30+ Rare Exceptional) plus every cross-chart aspect. Use both: the score
as a headline, the aspects to explain *why*.

**SVG chart wheel image:**
```bash
python3 scripts/astro.py svg \
  --name "Aakash" --year 2002 --month 8 --day 20 --hour 9 --minute 15 \
  --lat 18.5204 --lng 73.8567 --tz "Asia/Kolkata" \
  --output-dir /mnt/user-data/outputs
```
Produces `[Name] - Natal Chart.svg` — a real chart wheel with zodiac ring,
house divisions, planet glyphs, and an aspect grid. Present this to the user
via the file tools/`present_files` so they can view or download it. (It
renders correctly in any browser/artifact viewer; some basic SVG→PNG
converters that don't support CSS variables will render it incorrectly — that
is a converter limitation, not a problem with the file.)

Run `python3 scripts/astro.py <command> --help` for the full flag list,
including the `--house-system` flag (default `P` = Placidus; also supports
`W` = Whole Sign, `K` = Koch, and others).

## Step 3: Write the interpretation

Once you have real data from the script, write the actual reading. Read
`references/interpretation_guide.md` before writing — it has the
sign/house/aspect meanings and, more importantly, guidance on writing
psychologically grounded readings rather than generic horoscope-column filler.

General principles:
- Lead with the placements that matter most: Sun, Moon, Ascendant first, then
  notable tight-orb aspects (under ~3°), then the rest as supporting detail.
- Tie placements to psychology and behavior patterns, not vague mysticism —
  this lands better and is more honest about what astrology actually offers
  as a self-reflection framework.
- Be specific to *this* chart. Avoid copy-paste sign descriptions that would
  apply to anyone with that placement; reference the actual house, aspect,
  and degree context the script returned.
- For transits: explain what's currently "activated" in their natal chart
  and what that tends to correspond with, rather than predicting fixed
  outcomes.
- Keep appropriate epistemic framing — present this as a reflective/symbolic
  framework, not deterministic fact, especially if the user seems to be
  treating it as literal prediction for major life decisions.

## Notes

- All calculations use Tropical zodiac and Placidus houses by default
  (industry-standard Western astrology). Sidereal/Vedic (Lahiri ayanamsa) is
  supported by the underlying library if a user specifically wants Vedic
  charts — ask before assuming.
- The engine computes Sun through Pluto, Chiron, mean Lilith, and the lunar
  nodes. It does not include asteroids beyond Chiron unless extended.
- Dependencies: `kerykeion` (installs `pyswisseph` under the hood, which
  bundles its own ephemeris data — no internet needed at runtime).
