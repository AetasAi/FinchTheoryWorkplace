#!/usr/bin/env python3
"""
Finch Theory Workplace — Article scheduler.

Assigns publication dates to articles in insights/.
Run from repo root:
    py scripts\\schedule-articles.py
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path

START_FROM = date(2026, 6, 6)
ARTICLE_ORDER = [
    "why-financial-wellbeing-is-a-business-issue.html",
    "financial-wellbeing-in-the-workplace.html",
    "strengthening-your-team-through-financial-wellbeing.html",
    "when-everyday-life-stops-talking-back.html",
    "the-true-cost-of-replacing-an-employee.html",
    "what-a-pension-review-actually-finds.html",
    "financial-wellbeing-for-llps-and-professional-practices.html",
    "generational-financial-pressure-what-sme-employers-need-to-know.html",
]
SCHEDULE = {}
PUBLISH_DAYS = [1, 3]  # Tue/Thu
POSTS_DIR = Path("insights")

def format_display(d):
    return f"{d.day} {d.strftime('%B')} {d.year}"

def next_publish_day(start, publish_days):
    d = start
    while d.weekday() not in publish_days:
        d += timedelta(days=1)
    return d

def generate_dates(start, count, publish_days):
    dates, d = [], next_publish_day(start, publish_days)
    for _ in range(count):
        dates.append(d)
        d = next_publish_day(d + timedelta(days=1), publish_days)
    return dates

def update_dates(path, target_date):
    html = path.read_text(encoding="utf-8", errors="replace")
    original = html
    target_iso = target_date.isoformat()
    target_full = f"{target_iso}T08:00:00+00:00"
    msgs = []

    json_pat = re.compile(r'("datePublished"\s*:\s*")([^"]+)(")')
    m = json_pat.search(html)
    if m and m.group(2)[:10] != target_iso:
        html = json_pat.sub(f'\\g<1>{target_full}\\g<3>', html, count=1)
        msgs.append(f"JSON-LD: {m.group(2)[:10]} → {target_iso}")

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True, msgs
    return False, []

def main():
    repo_root = Path(__file__).resolve().parent.parent
    posts_dir = repo_root / POSTS_DIR
    if not posts_dir.exists():
        sys.stderr.write(f"insights/ not found\n")
        return 1

    print("Finch Theory Workplace — Article Scheduler")
    seq_dates = generate_dates(START_FROM, len(ARTICLE_ORDER), PUBLISH_DAYS)
    schedule = {fn: d for fn, d in zip(ARTICLE_ORDER, seq_dates)}
    schedule.update({fn: date.fromisoformat(d) for fn, d in SCHEDULE.items()})

    print(f"{'Filename':<60} {'Date':<20} {'Status'}")
    print("-" * 90)
    for fn, target in sorted(schedule.items(), key=lambda x: x[1]):
        path = posts_dir / fn
        if not path.exists():
            print(f"{fn:<60} {format_display(target):<20} FILE NOT FOUND")
            continue
        changed, msgs = update_dates(path, target)
        print(f"{fn:<60} {format_display(target):<20} {'Updated: ' + '; '.join(msgs) if changed else 'No change'}")
    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
