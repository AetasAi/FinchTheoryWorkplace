#!/usr/bin/env python3
"""
Finch Theory Workplace — Insights index auto-builder.

Scans insights/*.html, extracts metadata, and rebuilds the article grid
in insights.html between markers:

    <!-- AUTO-INSIGHTS-START -->
    ...replaced automatically...
    <!-- AUTO-INSIGHTS-END -->

Articles with a datePublished in the FUTURE are excluded.

Run from repo root:
    py scripts\\build-insights-index.py
"""

import re
import sys
from datetime import date
from pathlib import Path

INSIGHTS_DIR = Path("insights")
INDEX_FILE = Path("insights.html")
START_MARKER = "<!-- AUTO-INSIGHTS-START -->"
END_MARKER = "<!-- AUTO-INSIGHTS-END -->"

CATEGORY_MAP = {
    "retention": "Retention",
    "benefits": "Benefits review",
    "pension": "Benefits review",
    "llp": "Professional practices",
    "professional": "Professional practices",
    "generational": "Workforce performance",
    "financial-wellbeing": "Strategy",
    "wellbeing": "Wellbeing",
    "business": "Business case",
    "strengthening": "Business case",
    "everyday": "Wellbeing",
}

def get_meta(html, name):
    m = re.search(rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else None

def get_og(html, prop):
    m = re.search(rf'<meta\s+property="{re.escape(prop)}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else None

def get_date(html):
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    return date.fromisoformat(m.group(1)) if m else None

def get_title(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m2 = re.search(r'<title>([^<|]+)', html)
    if m2:
        return m2.group(1).strip().replace(' — Finch Theory', '').replace(' - Finch Theory', '')
    return None

def get_standfirst(html):
    m = re.search(r'class="article-standfirst"[^>]*>(.*?)</p>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return get_og(html, 'og:description') or ''

def get_category(slug):
    for key, label in CATEGORY_MAP.items():
        if key in slug.lower():
            return label
    return 'Insights'

def get_date_display(html):
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if m:
        d = date.fromisoformat(m.group(1))
        return f"{d.strftime('%B')} {d.year}"
    return 'June 2026'

def scan_articles(insights_dir):
    today = date.today()
    articles = []

    for path in sorted(insights_dir.glob("*.html")):
        html = path.read_text(encoding="utf-8", errors="replace")

        pub_date = get_date(html)
        if pub_date and pub_date > today:
            print(f"  Skipping (future): {path.name}")
            continue

        title = get_title(html)
        standfirst = get_standfirst(html)[:180]
        category = get_category(path.stem)
        date_display = get_date_display(html)
        slug = path.name

        articles.append({
            "slug": slug,
            "title": title or path.stem,
            "standfirst": standfirst,
            "category": category,
            "date_display": date_display,
            "pub_date": pub_date or today,
        })

    articles.sort(key=lambda a: a["pub_date"], reverse=True)
    return articles

def build_grid(articles):
    if not articles:
        return '<p style="color:var(--ink-muted);padding:2rem 0;">No articles published yet.</p>'
    cards = []
    for a in articles:
        card = f'''      <div class="article-card reveal">
        <span class="article-tag">{a["category"]}</span>
        <p class="article-meta">Matthew Steiner · {a["date_display"]}</p>
        <h3>{a["title"]}</h3>
        <p>{a["standfirst"]}</p>
        <a class="card-link" href="/insights/{a["slug"]}">Read article</a>
      </div>'''
        cards.append(card)
    return "\n\n".join(cards)

def main():
    repo_root = Path(__file__).resolve().parent.parent
    insights_dir = repo_root / INSIGHTS_DIR
    index_path = repo_root / INDEX_FILE

    if not insights_dir.exists():
        sys.stderr.write(f"insights/ not found: {insights_dir}\n")
        return 1
    if not index_path.exists():
        sys.stderr.write(f"insights.html not found: {index_path}\n")
        return 1

    print("Finch Theory Workplace — Insights Index Builder")
    print(f"Scanning: {insights_dir}")

    articles = scan_articles(insights_dir)
    print(f"\nFound {len(articles)} published article(s):")
    for a in articles:
        print(f"  + {a['slug']} — {a['date_display']}")

    grid_html = build_grid(articles)
    index_html = index_path.read_text(encoding="utf-8", errors="replace")

    if START_MARKER not in index_html or END_MARKER not in index_html:
        sys.stderr.write(f"Markers not found in {INDEX_FILE}.\n")
        sys.stderr.write(f"Add these inside the article grid section:\n")
        sys.stderr.write(f"  {START_MARKER}\n  {END_MARKER}\n")
        return 1

    before = index_html[:index_html.index(START_MARKER) + len(START_MARKER)]
    after = index_html[index_html.index(END_MARKER):]
    new_html = before + "\n" + grid_html + "\n    " + after
    index_path.write_text(new_html, encoding="utf-8")

    print(f"\n✓ insights.html updated with {len(articles)} article(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
