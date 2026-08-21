#!/usr/bin/env python3
"""Match this site's PDF-link citations against the Carlquist Publications
Dataset (https://github.com/BRITorg/carlquist_publications_dataset), to find
each citation's DOI, source URL, and Wikidata record.

Background
----------
sherwincarlquist.org lists ~300 of Carlquist's papers, each originally with
a "[ PDF ]" link to a local file that was never actually included in this
repository (see CLAUDE.md). Those links have since been replaced with an
inline widget that reveals real DOI / source / Wikidata links instead
(see sherwincarlquist.org/js/pdf-widget.js). This script is what produced
that mapping: it scans the site for PDF citations, fuzzy-matches each one
against the dataset's CSV export by year and title, and writes the result
to publication-links.json in this directory.

The matching is intentionally conservative but NOT infallible — text
similarity scoring can be fooled, especially by numbered monograph series
that share almost all of their title text (e.g. "SEM Studies on Vessels in
Ferns. 1. Woodsia obtusa" vs "...6. Woodsia ilvensis"). Always review the
"medium" and "low" confidence entries in the report, and spot-check a
sample of "high" ones, before trusting a fresh run's output. A few matching
errors were found and hand-corrected in the current publication-links.json
after the initial automated pass; see the site's git history for the
"biography-publications.html" fixes on and around the date this file was
first added.

Usage
-----
    python3 match_publications.py \\
        --site-dir ../../sherwincarlquist.org \\
        --dataset-csv /path/to/carlquist_publications.csv \\
        --out publication-links.json \\
        --report match-report.json

Re-running this against future site changes:
    The site no longer contains the original
    `<a href="pdf/....pdf" onclick="return pdfNotAvailable(event);">PDF</a>`
    links this script looks for — they were replaced with the widget markup
    once matched. This script is useful again if: (a) a new page is added
    with a PDF citation in that same legacy dead-link form, before it gets
    converted to a widget, or (b) the dataset is updated (new DOIs found,
    corrected metadata) and you want to re-derive publication-links.json
    from scratch and diff it against the current version to see what
    changed. The dataset CSV is not vendored here — download a fresh copy
    from the dataset repo above so the two don't silently drift apart.
"""

import argparse
import csv
import difflib
import glob
import html
import json
import os
import re
import sys

LINK_RE = re.compile(
    r'<a href="((?:pdf|pdf2|pdf4)/[^"]+\.[Pp][Dd][Ff])"[^>]*'
    r'onclick="return pdfNotAvailable\(event\);"[^>]*>PDF</a>'
)
BOUNDARY_RE = re.compile(r'</?p[ >]|<br\s*/?>', re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
YEAR_RE = re.compile(r"(?:19|20)\d{2}")


def strip_html(s):
    s = TAG_RE.sub(" ", s)
    s = html.unescape(s)
    return WS_RE.sub(" ", s).strip()


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return WS_RE.sub(" ", s).strip()


def extract_links(site_dir):
    """Find every legacy PDF-notice link and its preceding citation text."""
    results = []
    for page in sorted(glob.glob(os.path.join(site_dir, "*.html"))):
        text = open(page, encoding="utf-8").read()
        for m in LINK_RE.finditer(text):
            href = m.group(1)
            head = text[: m.start()]
            boundaries = list(BOUNDARY_RE.finditer(head))
            start = boundaries[-1].end() if boundaries else max(0, m.start() - 300)
            context = strip_html(text[start : m.start()])
            results.append({"page": os.path.basename(page), "href": href, "context": context})

    # A given href can be cited from more than one page; prefer the context
    # from biography-publications.html when available, since it carries the
    # full formatted citation rather than a narrative mention.
    by_href = {}
    for r in results:
        h = r["href"]
        if h not in by_href or r["page"] == "biography-publications.html":
            by_href[h] = r
    return by_href


def slug_from_href(href):
    fname = re.sub(r"\.pdf$", "", os.path.basename(href), flags=re.IGNORECASE)
    fname = re.sub(r"[_-](19|20)\d{2}$", "", fname)
    fname = re.sub(r"^(19|20)\d{2}[_-]", "", fname)
    return re.sub(r"[_-]+", " ", fname)


def leading_year(text):
    m = re.match(r"\s*(19|20)\d{2}", text)
    return int(m.group(0)) if m else None


def prefix_score(query_norm, title_norm):
    qw, tw = query_norm.split(), title_norm.split()
    if not qw:
        return 0.0
    n = 0
    for a, b in zip(qw, tw):
        if a != b:
            break
        n += 1
    return n / len(qw)


def blend_score(query_norm, title_norm):
    """Best-of several similarity signals, chosen to handle both truncated
    filenames (a short prefix of the real title) and dataset titles that
    omit a citation's subtitle (a short prefix of the query)."""
    if not query_norm or not title_norm:
        return 0.0
    seq = difflib.SequenceMatcher(None, query_norm, title_norm).ratio()
    qset = set(query_norm.split())
    tset = set(title_norm.split())
    recall = len(qset & tset) / len(qset) if qset else 0.0
    contains = 1.0 if query_norm in title_norm else 0.0
    return max(seq, recall, prefix_score(query_norm, title_norm), contains)


def load_dataset(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    for row in rows:
        row["_title_norm"] = norm(row["title"])
        try:
            row["_year"] = int(row["year"])
        except (KeyError, ValueError):
            row["_year"] = None
    return rows


def match_all(by_href, dataset_rows):
    report = []
    for href, rec in by_href.items():
        ctx_text = rec["context"]
        href_years = sorted({int(y) for y in YEAR_RE.findall(href)})
        lead_year = leading_year(ctx_text)
        year_candidates = sorted({y for y in (href_years + [lead_year]) if y})

        slug_norm = norm(slug_from_href(href))
        ctx_norm = norm(ctx_text)

        scored = []
        for row in dataset_rows:
            text_score = max(
                blend_score(slug_norm, row["_title_norm"]),
                blend_score(ctx_norm, row["_title_norm"]) if ctx_norm else 0.0,
            )
            if year_candidates and row["_year"] in year_candidates:
                bonus = 0.2
            elif year_candidates and row["_year"] and any(abs(row["_year"] - y) <= 1 for y in year_candidates):
                bonus = 0.05
            else:
                bonus = 0.0
            scored.append((text_score + bonus, text_score, row))
        scored.sort(key=lambda x: -x[0])
        top = scored[:3]

        best_total, best_text, best_row = top[0] if top else (0.0, 0.0, None)
        year_exact = bool(best_row and year_candidates and best_row["_year"] in year_candidates)

        if best_text >= 0.85 and year_exact:
            confidence = "high"
        elif best_text >= 0.7 or (best_text >= 0.55 and year_exact):
            confidence = "medium"
        else:
            confidence = "low"

        report.append(
            {
                "href": href,
                "page": rec["page"],
                "context": ctx_text,
                "confidence": confidence,
                "score": round(best_text, 3),
                "title": best_row["title"] if best_row else None,
                "year": best_row["_year"] if best_row else None,
                "doi": (best_row.get("DOI") or None) if best_row else None,
                "url": (best_row.get("URL") or None) if best_row else None,
                "wikidata": (best_row.get("wikidata-url") or None) if best_row else None,
                "runner_up": [
                    {"score": round(ts, 3), "title": row["title"], "year": row["_year"]}
                    for _, ts, row in top[1:]
                ],
            }
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site-dir", required=True, help="Path to sherwincarlquist.org")
    parser.add_argument("--dataset-csv", required=True, help="Path to carlquist_publications.csv")
    parser.add_argument("--out", default="publication-links.json", help="Where to write the href-keyed mapping")
    parser.add_argument("--report", help="Optional path to write the full match report (with confidence + runner-up) for manual review")
    args = parser.parse_args()

    by_href = extract_links(args.site_dir)
    if not by_href:
        print("No legacy PDF-notice links found under --site-dir. "
              "If the site has already been converted to the widget format, "
              "there is nothing left for this script to match.", file=sys.stderr)

    dataset_rows = load_dataset(args.dataset_csv)
    report = match_all(by_href, dataset_rows)

    from collections import Counter
    print("confidence breakdown:", dict(Counter(r["confidence"] for r in report)), file=sys.stderr)

    if args.report:
        json.dump(report, open(args.report, "w"), indent=1)
        print("wrote", args.report, file=sys.stderr)

    mapping = {}
    for r in report:
        entry = {"title": r["title"], "year": r["year"]}
        if r["doi"]:
            entry["doi"] = r["doi"]
        if r["url"]:
            entry["url"] = r["url"]
        if r["wikidata"]:
            entry["wikidata"] = r["wikidata"]
        mapping[r["href"]] = entry
    json.dump(dict(sorted(mapping.items())), open(args.out, "w"), indent=2, ensure_ascii=False)
    print("wrote", args.out, "with", len(mapping), "entries", file=sys.stderr)


if __name__ == "__main__":
    main()
