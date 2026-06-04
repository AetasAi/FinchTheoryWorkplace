#!/usr/bin/env python3
"""Generate sitemap.xml for finchtheory.com.

Walks the repo, classifies each .html file, and writes sitemap.xml.
Run this from the repo root:

    python generate-sitemap.py

Same pattern as the Aetas Wealth script. Edit EXCLUDE_FILES below if you
add new files that shouldn't be in the sitemap (e.g. internal forms,
thank-you pages).
"""
from __future__ import annotations
from datetime import date
from pathlib import Path
import sys

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------

SITE_ROOT = "https://finchtheory.com"
TODAY = date.today().isoformat()

# Folders to skip entirely (won't recurse into these)
EXCLUDE_DIRS = {
    ".git", ".github", "node_modules", "icons", "scripts",
}

# Specific files to skip (matched by filename only, not path)
EXCLUDE_FILES = {
    "404.html",                                  # error page
    "form-thankyou.html",                        # post-form, noindex
    "benefits-review.html",                      # internal data capture
    "google4bf7b0394b6b5986.html",               # Google site verification file
    "charities.html",                            # redirect to charitywellbeing.aetaspartners.com (noindex)
    "introducing-the-aetas-collective.html",     # article retired (Aetas Collective branding removed)
    "article-template.html",                     # internal article template, not real content
}


def _is_audience_page(rel: Path) -> bool:
    """Top audience-targeted pages (highest commercial value)."""
    return rel.parent == Path(".") and rel.name in {
        "limited-companies.html",
        "llps.html",
    }


def _is_tool_or_pricing(rel: Path) -> bool:
    return rel.parent == Path(".") and rel.name in {
        "diagnostic.html",
        "calculator.html",
        "investment.html",   # pricing
    }


def _is_section_hub(rel: Path) -> bool:
    return rel.parent == Path(".") and rel.name in {
        "insights.html",
        "faqs.html",
    }


def _is_funnel_page(rel: Path) -> bool:
    """Conversion/follow-up content (lower priority but still indexable)."""
    return rel.parent == Path(".") and rel.name in {
        "whats-next.html",
        "discovery-briefing.html",
        "initial-conversation-briefing.html",
    }


def _is_legal(rel: Path) -> bool:
    return rel.parent == Path(".") and rel.name in {
        "privacy.html",
        "data-processing-agreement.html",
        "terms.html",
        "complaints.html",
    }


# Classification rules: (predicate, priority, changefreq)
# Evaluated in order; first match wins.
RULES: list[tuple] = [
    # Homepage
    (lambda r: r == Path("index.html"),               1.0, "monthly"),
    # Section hubs (insights, faqs)
    (lambda r: r == Path("insights.html"),            0.8, "weekly"),
    (_is_section_hub,                                 0.7, "monthly"),
    # Insights articles
    (lambda r: r.parent == Path("insights"),          0.7, None),
    # Case studies
    (lambda r: r.parent == Path("case-studies"),      0.7, None),
    # Audience pages
    (_is_audience_page,                               0.9, "monthly"),
    # Tools and pricing
    (_is_tool_or_pricing,                             0.8, "monthly"),
    # Funnel / conversion pages
    (_is_funnel_page,                                 0.6, "monthly"),
    # Legal
    (_is_legal,                                       0.3, "yearly"),
]


# ---------------------------------------------------------------
# WALK + CLASSIFY
# ---------------------------------------------------------------

def classify(rel: Path) -> tuple[float, str | None] | None:
    """Return (priority, changefreq) tuple, or None if file should be excluded."""
    if rel.name in EXCLUDE_FILES:
        return None
    for predicate, priority, changefreq in RULES:
        if predicate(rel):
            return (priority, changefreq)
    return (0.5, None)  # default for any unclassified pages


def find_html(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.html"):
        # Skip excluded dirs
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


def url_for(rel: Path) -> str:
    """Convert a relative file path to a URL."""
    if rel == Path("index.html"):
        return f"{SITE_ROOT}/"
    return f"{SITE_ROOT}/{rel.as_posix()}"


# ---------------------------------------------------------------
# WRITE
# ---------------------------------------------------------------

def write_sitemap(root: Path) -> None:
    files = find_html(root)
    included: list[tuple[Path, float, str | None]] = []
    excluded: list[Path] = []
    fell_through: list[Path] = []

    for path in files:
        rel = path.relative_to(root)
        result = classify(rel)
        if result is None:
            excluded.append(rel)
            continue
        priority, changefreq = result
        included.append((rel, priority, changefreq))
        # Track fall-throughs (default 0.5 with no changefreq)
        if priority == 0.5 and changefreq is None:
            fell_through.append(rel)

    # Sort: homepage first, then by section, then alphabetically
    def sort_key(item: tuple[Path, float, str | None]) -> tuple:
        rel, _, _ = item
        if rel == Path("index.html"):
            return (0, "")
        section_order = {
            "limited-companies.html": 1,
            "llps.html": 1,
            "charities.html": 1,
            "diagnostic.html": 2,
            "calculator.html": 2,
            "investment.html": 2,
            "insights.html": 3,
            "faqs.html": 3,
        }
        if str(rel) in section_order:
            return (section_order[str(rel)], str(rel))
        if rel.parts[0] == "case-studies":
            return (4, str(rel))
        if rel.parts[0] == "insights":
            return (5, str(rel))
        return (6, str(rel))

    included.sort(key=sort_key)

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    last_section = None
    section_labels = {
        0: "Homepage",
        1: "Audience pages",
        2: "Tools and pricing",
        3: "Section hubs",
        4: "Case studies",
        5: "Insights",
        6: "Other",
    }

    for rel, priority, changefreq in included:
        section = sort_key((rel, priority, changefreq))[0]
        if section != last_section:
            lines.append(f"  <!-- {section_labels[section]} -->")
            last_section = section
        lines.append("  <url>")
        lines.append(f"    <loc>{url_for(rel)}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        if changefreq:
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    lines.append("")  # trailing newline

    out_path = root / "sitemap.xml"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    # Report
    print(f"Wrote {out_path}")
    print(f"  Included: {len(included)} URLs")
    print(f"  Excluded: {len(excluded)} files")
    if excluded:
        print()
        print("Excluded files (verify these should really be skipped):")
        for rel in excluded:
            print(f"  - {rel}")
    if fell_through:
        print()
        print(f"WARNING: {len(fell_through)} pages fell through to the default")
        print("priority (0.5). Consider adding a rule for these:")
        for rel in fell_through:
            print(f"  - {rel}")


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    write_sitemap(root)
