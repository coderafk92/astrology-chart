#!/usr/bin/env python3
"""
astro.py — Real astronomical chart calculations for the astrology-chart skill.

Uses Swiss Ephemeris (via kerykeion/pyswisseph) for genuine planetary
positions, house cusps, and aspects. No invented data — every number
here comes from an actual ephemeris calculation, not a language model
guess.

Subcommands:
  natal      Generate a full natal (birth) chart
  transit    Get current/specified-date transiting planets + aspects to a natal chart
  synastry   Compare two natal charts (compatibility / relationship aspects)
  svg        Render a chart wheel as an SVG file

All commands take birth data as flags (year, month, day, hour, minute,
lat, lng, tz). If you don't know precise lat/lng/timezone for a city,
look it up first (web search or known reference data) — this script
does NOT geocode city names, it expects coordinates.

Run with --help on any subcommand for full argument list.
"""

import argparse
import json
import sys
from datetime import datetime, timezone as dt_timezone

from kerykeion import (
    AstrologicalSubjectFactory,
    NatalAspects,
    SynastryAspects,
    RelationshipScoreFactory,
    KerykeionChartSVG,
)


PLANET_KEYS = [
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
    "uranus", "neptune", "pluto", "chiron", "mean_lilith",
    "true_north_lunar_node", "true_south_lunar_node",
]

ANGLE_KEYS = ["ascendant", "descendant", "medium_coeli", "imum_coeli"]

HOUSE_KEYS = [
    "first_house", "second_house", "third_house", "fourth_house",
    "fifth_house", "sixth_house", "seventh_house", "eighth_house",
    "ninth_house", "tenth_house", "eleventh_house", "twelfth_house",
]


def build_subject(args, prefix=""):
    """Build an AstrologicalSubjectModel from parsed CLI args, given an optional
    prefix for person-2 style flags (used by synastry)."""
    def g(field):
        return getattr(args, f"{prefix}{field}")

    return AstrologicalSubjectFactory.from_birth_data(
        name=g("name"),
        year=g("year"),
        month=g("month"),
        day=g("day"),
        hour=g("hour"),
        minute=g("minute"),
        lng=g("lng"),
        lat=g("lat"),
        tz_str=g("tz"),
        city=g("city") or "Unknown",
        nation=g("nation") or "XX",
        online=False,
        houses_system_identifier=g("house_system"),
    )


def point_summary(data, key):
    """Compact representation of a single planet/point/angle."""
    p = data.get(key)
    if p is None:
        return None
    return {
        "name": p["name"],
        "sign": p["sign"],
        "degree_in_sign": round(p["position"], 2),
        "absolute_degree": round(p["abs_pos"], 2),
        "house": p.get("house"),
        "retrograde": p.get("retrograde", False),
    }


def chart_summary(subject):
    data = subject.model_dump()

    planets = {k: point_summary(data, k) for k in PLANET_KEYS if data.get(k)}
    angles = {k: point_summary(data, k) for k in ANGLE_KEYS if data.get(k)}
    houses = {
        k: {"sign": data[k]["sign"], "absolute_degree": round(data[k]["position"] + (0 if False else 0), 2)}
        for k in HOUSE_KEYS if data.get(k)
    }

    aspects_calc = NatalAspects(subject)
    aspects = [
        {
            "point_1": a.p1_name,
            "aspect": a.aspect,
            "point_2": a.p2_name,
            "orb": round(a.orbit, 2),
        }
        for a in aspects_calc.relevant_aspects
    ]

    return {
        "name": data["name"],
        "birth_data": {
            "local_datetime": data["iso_formatted_local_datetime"],
            "utc_datetime": data["iso_formatted_utc_datetime"],
            "city": data["city"],
            "nation": data["nation"],
            "lat": data["lat"],
            "lng": data["lng"],
            "tz_str": data["tz_str"],
        },
        "lunar_phase": data.get("lunar_phase"),
        "planets": planets,
        "angles": angles,
        "houses": houses,
        "aspects": aspects,
    }


def cmd_natal(args):
    subject = build_subject(args)
    result = chart_summary(subject)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_transit(args):
    natal = build_subject(args)

    now = datetime.now(dt_timezone.utc) if not args.t_year else None
    t_year = args.t_year or now.year
    t_month = args.t_month or now.month
    t_day = args.t_day or now.day
    t_hour = args.t_hour if args.t_hour is not None else (now.hour if now else 12)
    t_minute = args.t_minute if args.t_minute is not None else (now.minute if now else 0)

    transiting = AstrologicalSubjectFactory.from_birth_data(
        name="Transit",
        year=t_year, month=t_month, day=t_day, hour=t_hour, minute=t_minute,
        lng=args.lng, lat=args.lat, tz_str=args.tz,
        city=args.city or "Unknown", nation=args.nation or "XX",
        online=False,
    )

    transit_data = transiting.model_dump()
    transit_planets = {k: point_summary(transit_data, k) for k in PLANET_KEYS if transit_data.get(k)}

    # Aspects between transiting planets and natal points
    synastry = SynastryAspects(transiting, natal)
    cross_aspects = [
        {
            "transiting_planet": a.p1_name,
            "aspect": a.aspect,
            "natal_point": a.p2_name,
            "orb": round(a.orbit, 2),
        }
        for a in synastry.relevant_aspects
        if a.orbit <= args.max_orb
    ]

    result = {
        "natal_name": natal.name,
        "transit_datetime_utc": transit_data["iso_formatted_utc_datetime"],
        "transiting_planets": transit_planets,
        "transits_to_natal_chart": cross_aspects,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_synastry(args):
    person1 = build_subject(args, prefix="p1_")
    person2 = build_subject(args, prefix="p2_")

    aspects_calc = SynastryAspects(person1, person2)
    aspects = [
        {
            "person_1_point": a.p1_name,
            "aspect": a.aspect,
            "person_2_point": a.p2_name,
            "orb": round(a.orbit, 2),
        }
        for a in aspects_calc.relevant_aspects
    ]

    score_factory = RelationshipScoreFactory(person1, person2)
    score = score_factory.get_relationship_score()

    result = {
        "person_1": person1.name,
        "person_2": person2.name,
        "relationship_score": {
            "score": score.score_value,
            "description": score.score_description,
            "is_destiny_sign": getattr(score, "is_destiny_sign", None),
        },
        "aspects": aspects,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_svg(args):
    subject = build_subject(args)
    chart = KerykeionChartSVG(
        subject,
        chart_type=args.chart_type,
        new_output_directory=args.output_dir,
    )
    chart.makeSVG()
    print(json.dumps({"status": "ok", "output_dir": args.output_dir}, indent=2))


def add_person_args(parser, prefix="", required=True):
    """prefix is used for the *dest* (e.g. 'p1_'); CLI flags always use hyphens."""
    p = prefix
    flag_p = prefix.replace("_", "-")
    parser.add_argument(f"--{flag_p}name", dest=f"{p}name", required=required, default="Person")
    parser.add_argument(f"--{flag_p}year", dest=f"{p}year", type=int, required=required)
    parser.add_argument(f"--{flag_p}month", dest=f"{p}month", type=int, required=required)
    parser.add_argument(f"--{flag_p}day", dest=f"{p}day", type=int, required=required)
    parser.add_argument(f"--{flag_p}hour", dest=f"{p}hour", type=int, required=required)
    parser.add_argument(f"--{flag_p}minute", dest=f"{p}minute", type=int, default=0)
    parser.add_argument(f"--{flag_p}lat", dest=f"{p}lat", type=float, required=required,
                         help="Latitude in decimal degrees")
    parser.add_argument(f"--{flag_p}lng", dest=f"{p}lng", type=float, required=required,
                         help="Longitude in decimal degrees")
    parser.add_argument(f"--{flag_p}tz", dest=f"{p}tz", required=required,
                         help="IANA timezone string, e.g. Asia/Kolkata")
    parser.add_argument(f"--{flag_p}city", dest=f"{p}city", default=None)
    parser.add_argument(f"--{flag_p}nation", dest=f"{p}nation", default=None)
    parser.add_argument(f"--{flag_p}house-system", dest=f"{p}house_system", default="P",
                         help="House system identifier (P=Placidus, W=Whole Sign, K=Koch, etc). Default Placidus.")


def main():
    parser = argparse.ArgumentParser(description="Real astronomical astrology chart calculations.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_natal = sub.add_parser("natal", help="Generate a full natal chart")
    add_person_args(p_natal)
    p_natal.set_defaults(func=cmd_natal)

    p_transit = sub.add_parser("transit", help="Current/specified-date transits to a natal chart")
    add_person_args(p_transit)
    p_transit.add_argument("--t-year", type=int, default=None, help="Transit year (default: now)")
    p_transit.add_argument("--t-month", type=int, default=None)
    p_transit.add_argument("--t-day", type=int, default=None)
    p_transit.add_argument("--t-hour", type=int, default=None)
    p_transit.add_argument("--t-minute", type=int, default=None)
    p_transit.add_argument("--max-orb", type=float, default=3.0,
                            help="Max orb in degrees to include a transit aspect (default 3.0)")
    p_transit.set_defaults(func=cmd_transit)

    p_syn = sub.add_parser("synastry", help="Compare two natal charts")
    add_person_args(p_syn, prefix="p1_")
    add_person_args(p_syn, prefix="p2_")
    p_syn.set_defaults(func=cmd_synastry)

    p_svg = sub.add_parser("svg", help="Render a chart wheel SVG")
    add_person_args(p_svg)
    p_svg.add_argument("--chart-type", default="Natal", choices=["Natal", "ExternalNatal"])
    p_svg.add_argument("--output-dir", default=".")
    p_svg.set_defaults(func=cmd_svg)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
