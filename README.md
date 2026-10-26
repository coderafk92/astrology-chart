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
<!--
╔══════════════════════════════════════════════════════════════╗
║                 ASTROLOGY CHART README                      ║
║          Celestial • Zodiac • Cosmic Observatory            ║
╚══════════════════════════════════════════════════════════════╝

Replace repository links if your project lives elsewhere.
Animated graphics load from external SVG services.
-->

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:090B1A,35:30204F,70:76549B,100:C6A76A&height=250&section=header&text=ASTROLOGY%20CHART&fontSize=48&fontColor=F6E8C8&animation=fadeIn&fontAlignY=36&desc=THE%20ART%20OF%20READING%20THE%20COSMOS&descAlignY=58&descSize=15" />

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Cormorant+Garamond&weight=600&size=24&duration=3200&pause=1000&color=C6A76A&center=true&vCenter=true&width=760&lines=Every+Birth+Chart+Tells+a+Story+%E2%9C%A8;Real+Planetary+Positions.+Meaningful+Interpretations.+%F0%9F%8C%99;Natal+Charts+%E2%80%A2+Transits+%E2%80%A2+Synastry;Astronomical+Calculations%2C+Not+AI+Guesswork+%E2%9C%A6" alt="Animated celestial introduction" />

<br/>

### ☽ &nbsp; WHERE ASTRONOMY MEETS ASTROLOGY &nbsp; ☾

**Real celestial calculations. Thoughtful interpretations. One cosmic toolkit.**

<br/>

[![GitHub](https://img.shields.io/badge/BUILT%20BY-coderafk92-C6A76A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/coderafk92)
[![Python](https://img.shields.io/badge/POWERED%20BY-PYTHON-76549B?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/LICENSE-MIT-C6A76A?style=for-the-badge)](#-license)
[![Astrology](https://img.shields.io/badge/COSMIC%20TOOLS-NATAL%20%7C%20TRANSITS%20%7C%20SYNASTRY-30204F?style=for-the-badge)](#-the-cosmic-toolkit)

<br/>

*✦ An astrology skill for Claude Code and Claude.ai ✦*

</div>

---

<div align="center">

## ✧ THE STARS PROVIDE THE DATA. THE STORY BEGINS WITH YOU. ✧

*A birth chart deserves more than a beautiful guess.*

</div>

## ☽ Overview

**Astrology Chart** is a Claude skill that generates natal charts, planetary transits, synastry charts, and astrological chart wheels using actual astronomical calculations.

Instead of asking a language model to guess planetary placements, this project gives Claude a calculation engine to retrieve the underlying chart data first.

Powered by [Kerykeion](https://github.com/g-battaglia/kerykeion) and Swiss Ephemeris-based calculations, the skill combines computational precision with natural-language interpretation.

### ✦ The philosophy

Traditional AI-generated astrology can sound convincing while getting the underlying planetary placements wrong.

Astrology Chart takes a different approach:

**Calculate first. Interpret second.**

Planetary positions, house cusps, and aspects come from the calculation engine. Claude then uses those results to explain the chart in accessible language.

No invented planetary placements. No dependence on an LLM remembering astronomical tables. Just calculated data followed by interpretation.

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Georgia&size=19&duration=3000&pause=900&color=C6A76A&center=true&vCenter=true&width=700&lines=Calculate+the+Heavens+%E2%9C%A6;Understand+the+Chart+%E2%98%BD;Interpret+the+Cosmic+Patterns+%E2%98%BE" alt="The celestial workflow"/>

</div>

---

## ✧ The Cosmic Toolkit

<table>
<tr>
<td width="50%" valign="top">

<div align="center">

### ☉ NATAL CHARTS

**Your personal celestial map**

</div>

Generate natal charts from a birth date, birth time, and geographic location.

Explore:

- Sun, Moon, and planetary placements
- Zodiac signs and planetary degrees
- Ascendant and house placements
- Planetary aspects
- Structured chart data for interpretation

*Every placement is based on calculated chart data.*

</td>
<td width="50%" valign="top">

<div align="center">

### ☽ PLANETARY TRANSITS

**The moving sky**

</div>

Calculate planetary transits for the present or a selected date and compare them with a natal chart.

Explore:

- Current or historical planetary positions
- Transiting planets and natal placements
- Relevant aspects between transit and natal planets
- Structured results for interpretation

*Choose the date. Calculate the sky. Explore the symbolism.*

</td>
</tr>
<tr>
<td width="50%" valign="top">

<div align="center">

### ♡ SYNASTRY

**Two charts. One comparison.**

</div>

Compare two natal charts to explore astrological compatibility and inter-chart aspects.

Features include:

- Two-person chart comparison
- Planet-to-planet aspects
- Relationship-oriented interpretation
- A numeric compatibility score, as implemented by the calculation script

*Astrological compatibility is interpretive, not a scientifically validated measure of relationship success.*

</td>
<td width="50%" valign="top">

<div align="center">

### ✧ CHART WHEELS

**See the celestial geometry**

</div>

Generate real SVG chart wheels from calculated astronomical data.

Includes visual representations of:

- The zodiac wheel
- Planetary placements
- Astrological houses
- Planetary aspects

*Actual chart data, rendered as a visual map—not an AI-generated illustration.*

</td>
</tr>
</table>

---

## ☾ How the Magic Works

<div align="center">

```text
                    ✧ YOUR BIRTH DETAILS ✧
                              |
                              ▼
                   ┌────────────────────┐
                   │  ASTROLOGY SKILL   │
                   │      SKILL.md      │
                   └────────────────────┘
                              |
                              ▼
                   ┌────────────────────┐
                   │  ASTRO CALCULATION │
                   │      SCRIPT        │
                   └────────────────────┘
                              |
                              ▼
                   ┌────────────────────┐
                   │ KERYKEION /        │
                   │ EPHEMERIS ENGINE   │
                   └────────────────────┘
                              |
                              ▼
                   ✦ CALCULATED DATA ✦
                              |
                              ▼
                   ┌────────────────────┐
                   │  CLAUDE'S ANALYSIS │
                   │  & INTERPRETATION  │
                   └────────────────────┘
                              |
                              ▼
                   ☽ YOUR CHART READING ☾
```

</div>

### The four-step process

**01 — Provide the details.**  
Supply a birth date, birth time, and location, or the relevant information for a transit or synastry calculation.

**02 — Calculate the chart.**  
Claude follows the skill instructions and invokes the Python script to obtain the requested chart data.

**03 — Retrieve actual placements.**  
The calculation engine returns planetary positions, house cusps, aspects, and other supported information.

**04 — Interpret the results.**  
Claude uses the returned data to construct a readable astrological interpretation.

The key distinction: **the model generates the interpretation, not the underlying astronomical numbers.**

---

## ✧ Example: A Natal Chart Reading

<div align="center">

### ☉ YOUR CELESTIAL BLUEPRINT ☽

*A conversation with Claude*

</div>

**You:**

> What's my birth chart? Born June 15, 2000, at 2:30 PM in Pune, India.

Claude obtains the location's coordinates and timezone, then runs the calculation script:

```bash
python3 scripts/astro.py natal \
  --name "You" \
  --year 2000 \
  --month 6 \
  --day 15 \
  --hour 14 \
  --minute 30 \
  --lat 18.5204 \
  --lng 73.8567 \
  --tz "Asia/Kolkata"
```

The script calculates the planetary placements, houses, and aspects for the supplied birth details.

Claude then interprets the **actual returned results**, explaining the Sun, Moon, Ascendant, house placements, and aspects without inventing positions.

<sub>Example input shown for demonstration. The final reading must use the script's actual output.</sub>

---

## ☼ Designed for Ground-Truth Data

Many language models can produce convincing astrological language without accurately calculating a chart.

Astrology Chart separates these tasks.

<table>
<tr>
<th align="center">Without Calculation</th>
<th align="center">With Astrology Chart</th>
</tr>
<tr>
<td valign="top">

- ❌ Placements may be guessed
- ❌ Degrees may be inaccurate
- ❌ Houses may be inconsistent
- ❌ Aspects may be invented

</td>
<td valign="top">

- ✦ Positions computed by a calculation engine
- ✦ House cusps calculated from chart inputs
- ✦ Aspects derived from chart data
- ✦ Interpretations grounded in returned results

</td>
</tr>
</table>

**The goal is to reduce fabricated chart data by calculating first and interpreting second.**

Astronomical calculation accuracy and astrological interpretation are separate things: correct planetary positions do not establish that astrology can scientifically predict personality or events.

---

## ☽ Installation

### ✦ Option I — Claude Code

Install the skill in your personal Claude Code skills directory.

```bash
git clone https://github.com/coderafk92/astrology-chart.git \
  ~/.claude/skills/astrology-chart
```

Enter the project directory:

```bash
cd ~/.claude/skills/astrology-chart
```

Install the Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

The skill's instructions are located in:

```text
~/.claude/skills/astrology-chart/SKILL.md
```

> Replace the repository URL if your project is published under a different account or repository name.

### ✦ Option II — Claude.ai or Another Compatible Setup

Clone the repository somewhere convenient, then follow the skill installation process supported by your Claude environment.

You can also inspect `SKILL.md` directly to understand how the skill uses the calculation script.

For an environment that does not automatically install the Python dependencies, install them explicitly and verify that the script can run before requesting a reading.

---

## ✧ The CLI: The Observatory at Your Fingertips

You don't need Claude to run the calculation engine.

The Python script provides a command-line interface for supported chart calculations and SVG generation.

### ☉ Natal chart

```bash
python3 scripts/astro.py natal --help
```

### ☽ Planetary transits

```bash
python3 scripts/astro.py transit --help
```

### ♡ Synastry

```bash
python3 scripts/astro.py synastry --help
```

### ✧ SVG chart wheels

```bash
python3 scripts/astro.py svg --help
```

Use `--help` to discover the arguments supported by your installed version.

---

## 🌌 Project Architecture

```text
astrology-chart/
│
├── SKILL.md
│   └── Instructions Claude follows
│
├── scripts/
│   └── astro.py
│       └── Natal, transit, synastry, and SVG CLI
│
├── references/
│   └── interpretation_guide.md
│       └── Signs, houses, aspects, and interpretation guidance
│
├── examples/
│   └── Sample chart output
│
└── requirements.txt
    └── Python dependencies
```

### ✦ Separation of responsibilities

| Component | Purpose |
|---|---|
| `SKILL.md` | Tells Claude when and how to use the calculation tools |
| `astro.py` | Exposes the chart-calculation and SVG workflows |
| `interpretation_guide.md` | Provides interpretive reference material |
| `examples/` | Demonstrates expected output formats |
| `requirements.txt` | Lists the Python dependencies |

This structure keeps the astronomical calculations, instructions, and interpretive guidance separate.

---

## ☽ Accuracy, Timezones & Limitations

Birth charts depend on more than a calendar date.

Accurate results require appropriate handling of:

- **Birth time:** The Ascendant and houses can change significantly with time.
- **Location:** Geographic coordinates affect local chart calculations.
- **Timezone:** The supplied civil time must be converted correctly.
- **Ephemeris data:** Planetary positions depend on the underlying astronomical calculation resources.
- **Calculation settings:** House systems and other settings can affect the resulting chart.

If the birth time is unknown or approximate, that uncertainty should be reflected in the reading—particularly for the Ascendant and houses.

The skill provides astronomical inputs for astrological interpretation. It does not establish astrology as a scientifically validated predictive method.

---

## ⚖️ License

The repository's code is licensed under the **MIT License**, subject to the actual contents of the project's `LICENSE` file.

Its dependencies have their own licensing terms:

- **Kerykeion:** Review the project's current license and distribution requirements.
- **Swiss Ephemeris / pyswisseph:** Review the applicable licensing terms for the exact versions and configuration you use.

Depending on the dependency and use case, separate license requirements may apply, particularly for commercial distribution.

**Do not assume that the repository's MIT license automatically covers every dependency.** Review the upstream licenses before redistributing the project or using it commercially.

---

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=0:30204F,50:76549B,100:C6A76A&height=2&section=header" />

## ☾ THE COSMOS HAS A STORY. LET'S READ IT RESPONSIBLY. ☽

*Real calculations. Thoughtful interpretations. A little celestial wonder.*

<br/>

<a href="https://github.com/coderafk92">
<img src="https://img.shields.io/badge/DEVELOPER-coderafk92-C6A76A?style=for-the-badge&logo=github&logoColor=white" alt="GitHub developer"/>
</a>

<a href="https://github.com/coderafk92/astrology-chart">
<img src="https://img.shields.io/badge/EXPLORE%20THE%20SOURCE-30204F?style=for-the-badge&logo=github&logoColor=white" alt="Explore repository"/>
</a>

<br/><br/>

<img src="https://readme-typing-svg.demolab.com?font=Georgia&size=18&duration=3200&pause=1100&color=C6A76A&center=true&vCenter=true&width=700&lines=As+Above%2C+So+We+Explore.+%E2%9C%A6;Every+Chart+Begins+With+Calculated+Data.+%E2%98%BD;May+Your+Curiosity+Never+Stop.+%E2%9C%A8" alt="Celestial closing message"/>

<br/>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:090B1A,35:30204F,70:76549B,100:C6A76A&height=150&section=footer" />

<sub>✦ Crafted with curiosity by <a href="https://github.com/coderafk92">coderafk92</a> ✦</sub>

</div>
