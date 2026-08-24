#!/usr/bin/env python3
"""Generate a schema.org JSON-LD block for the publications listed on
biography-publications.html.

EXPLORATORY — this script is a prototype (see TODO.md / the jsonld-publications
branch), not wired into the site yet. It shows what the structured data
would look like if we go ahead with it.

Highwire Press `citation_*` meta tags (what Google Scholar looks for) were
ruled out because Scholar's own inclusion guidelines require one article per
URL and can't index multiple abstracts on one page. JSON-LD doesn't have
that restriction -- a single page can describe many entities in one
`@graph` -- so it's the option that actually fits this site's single shared
bibliography page.

Data sources
------------
- tools/publications/publication-links.json: every citation on the site
  that has a DOI / source / Wikidata match, keyed by either the original
  dead PDF path or an `unlinked-citation:<citation text>` key. Every entry
  has a `wikidata` URL.
- The Carlquist Publications Dataset CSV (not vendored here -- download a
  fresh copy from https://github.com/BRITorg/carlquist_publications_dataset):
  richer per-record metadata (container title, volume, issue, pages,
  authors, editors, publisher, ISSN, type). Joined to publication-links.json
  by Wikidata QID, which is a 1:1 clean match for all 360 current entries.

Usage
-----
    python3 generate_jsonld.py \\
        --links publication-links.json \\
        --dataset-csv /path/to/carlquist_publications.csv \\
        --out jsonld-preview.json \\
        --page-url https://britorg.github.io/carlquist_web/biography-publications.html
"""

import argparse
import csv
import json
import re

QID_RE = re.compile(r"Q\d+")


def parse_author_name(raw):
    """'Carlquist, S.' -> 'Sherwin Carlquist'; 'Raven, Peter H.' -> 'Peter H. Raven'."""
    raw = raw.strip()
    if "," not in raw:
        return raw
    last, first = (p.strip() for p in raw.split(",", 1))
    if last == "Carlquist" and first.rstrip(".") == "S":
        return "Sherwin Carlquist"
    return f"{first} {last}".strip()


def people(raw):
    if not raw:
        return []
    return [
        {"@type": "Person", "name": parse_author_name(name)}
        for name in raw.split(";")
        if name.strip()
    ]


def load_dataset(path):
    by_qid = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qid = row.get("wikidata-id", "").strip()
            if qid:
                by_qid[qid] = row
    return by_qid


def qid_from_url(url):
    m = QID_RE.search(url or "")
    return m.group(0) if m else None


def source_urls(link_entry, row):
    urls = []
    if row.get("DOI"):
        urls.append(f"https://doi.org/{row['DOI']}")
    if row.get("URL"):
        urls.append(row["URL"])
    if link_entry.get("url") and link_entry["url"] not in urls:
        urls.append(link_entry["url"])
    if row.get("wikidata-url"):
        urls.append(row["wikidata-url"])
    elif link_entry.get("wikidata"):
        urls.append(link_entry["wikidata"])
    # de-dupe, preserve order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def build_entry(key, link_entry, row, slug):
    pub_type = row.get("type", "article-journal")
    title = row.get("title") or link_entry.get("title", "")
    authors = people(row.get("author", ""))
    date_published = row.get("issued") or str(row.get("year", link_entry.get("year", "")))
    entry = {
        "@id": f"#{slug}",
        "name": title,
        "author": authors or [{"@type": "Person", "name": "Sherwin Carlquist"}],
        "datePublished": date_published,
        "inLanguage": row.get("language", "en"),
        "sameAs": source_urls(link_entry, row),
    }
    if row.get("DOI"):
        entry["identifier"] = {
            "@type": "PropertyValue",
            "propertyID": "DOI",
            "value": row["DOI"],
        }
    if row.get("page"):
        entry["pagination"] = row["page"]

    if pub_type == "book":
        entry["@type"] = "Book"
        if row.get("publisher"):
            entry["publisher"] = {"@type": "Organization", "name": row["publisher"]}
        if row.get("container-ISBN"):
            entry["isbn"] = row["container-ISBN"]

    elif pub_type == "chapter":
        entry["@type"] = "Chapter"
        book = {"@type": "Book", "name": row.get("container-title", "")}
        editors = people(row.get("editor", ""))
        if editors:
            book["editor"] = editors
        if row.get("publisher"):
            book["publisher"] = {"@type": "Organization", "name": row["publisher"]}
        if row.get("container-ISBN"):
            book["isbn"] = row["container-ISBN"]
        entry["isPartOf"] = book

    else:  # article-journal
        entry["@type"] = "ScholarlyArticle"
        periodical = {"@type": "Periodical", "name": row.get("container-title", "")}
        if row.get("container-ISSN"):
            periodical["issn"] = row["container-ISSN"]
        is_part_of = periodical
        if row.get("volume"):
            volume = {
                "@type": "PublicationVolume",
                "volumeNumber": row["volume"],
                "isPartOf": periodical,
            }
            is_part_of = volume
        if row.get("issue"):
            is_part_of = {
                "@type": "PublicationIssue",
                "issueNumber": row["issue"],
                "isPartOf": is_part_of,
            }
        entry["isPartOf"] = is_part_of

    return entry


def slugify(key, row, index):
    title = row.get("title") or key
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    return f"pub-{index}-{slug}" if slug else f"pub-{index}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--links", default="publication-links.json")
    ap.add_argument("--dataset-csv", required=True)
    ap.add_argument("--out", default="jsonld-preview.json")
    ap.add_argument(
        "--page-html",
        default="../../sherwincarlquist.org/biography-publications.html",
        help="Only emit entries whose Wikidata QID actually appears on this page "
        "(the same citation widget is reused across topic pages, so "
        "publication-links.json has multiple keys per QID; this scopes the "
        "@graph to what's really on the bibliography page).",
    )
    ap.add_argument(
        "--page-url",
        default="https://britorg.github.io/carlquist_web/biography-publications.html",
    )
    args = ap.parse_args()

    links = json.load(open(args.links, encoding="utf-8"))
    by_qid = load_dataset(args.dataset_csv)

    page_html = open(args.page_html, encoding="utf-8").read()
    page_qids = set(re.findall(r"wikidata\.org/wiki/(Q\d+)", page_html))

    graph = []
    unmatched = []
    seen_qids = set()
    for i, (key, link_entry) in enumerate(sorted(links.items())):
        qid = qid_from_url(link_entry.get("wikidata", ""))
        if qid not in page_qids or qid in seen_qids:
            continue
        row = by_qid.get(qid)
        if not row:
            unmatched.append(key)
            continue
        seen_qids.add(qid)
        slug = slugify(key, row, i)
        graph.append(build_entry(key, link_entry, row, slug))

    doc = {
        "@context": "https://schema.org",
        "@graph": graph,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(graph)} entries to {args.out}")
    if unmatched:
        print(f"{len(unmatched)} entries had no dataset match (unexpected):")
        for k in unmatched:
            print(" -", k)


if __name__ == "__main__":
    main()
