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
- The same dataset's carlquist_authors.csv and carlquist_journals.csv:
  separate reconciled tables mapping each as-cited author/editor name and
  each journal title to its own Wikidata item, letting Person and
  Periodical entities carry a `sameAs` link too (not just the publication
  itself). Journal coverage is 100% for the entries in this graph; author
  coverage is partial -- 22 as-cited names (mostly one-off editors of edited
  volumes) have no reconciled Wikidata match and fall back to a plain name.

Usage
-----
    python3 generate_jsonld.py \\
        --links publication-links.json \\
        --dataset-csv /path/to/carlquist_publications.csv \\
        --authors-csv /path/to/carlquist_authors.csv \\
        --journals-csv /path/to/carlquist_journals.csv \\
        --out jsonld-preview.json \\
        --page-url https://britorg.github.io/carlquist_web/biography-publications.html

If --authors-csv / --journals-csv are omitted, they're looked for as
sibling files next to --dataset-csv (the dataset repo's normal layout).
"""

import argparse
import csv
import json
import os
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


def people(raw, author_wikidata):
    if not raw:
        return []
    out = []
    for name in raw.split(";"):
        name = name.strip()
        if not name:
            continue
        person = {"@type": "Person", "name": parse_author_name(name)}
        wd = author_wikidata.get(name)
        if wd:
            person["sameAs"] = wd
        out.append(person)
    return out


def load_dataset(path):
    by_qid = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qid = row.get("wikidata-id", "").strip()
            if qid:
                by_qid[qid] = row
    return by_qid


def load_author_wikidata(path):
    by_cited_name = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cited = row.get("author-as-cited", "").strip()
            wd = row.get("wikidata-url", "").strip()
            if cited and wd:
                by_cited_name[cited] = wd
    return by_cited_name


def load_journal_wikidata(path):
    by_title = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row.get("journal-title", "").strip()
            wd = row.get("wikidata-url", "").strip()
            if title and wd:
                by_title[title] = wd
    return by_title


def qid_from_url(url):
    m = QID_RE.search(url or "")
    return m.group(0) if m else None


def full_date(raw):
    """Pad a partial/date-only value to a full ISO 8601 datetime with a
    timezone. schema.org's Date type accepts 'YYYY', 'YYYY-MM', or a bare
    'YYYY-MM-DD' with no time component, but Google's Rich Results Test
    flags anything short of a full datetime+timezone as "Invalid datetime
    value" / "missing a timezone" on datePublished (confirmed by testing
    against the live tool -- see the jsonld-publications branch history).
    None of these are real publication timestamps, so pad with a synthetic
    UTC midnight: '1958' -> '1958-01-01T00:00:00+00:00'."""
    raw = (raw or "").strip()
    parts = raw.split("-")
    if len(parts) == 1:
        date = f"{raw}-01-01"
    elif len(parts) == 2:
        date = f"{raw}-01"
    else:
        date = raw
    return f"{date}T00:00:00+00:00"


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


def build_entry(key, link_entry, row, slug, author_wikidata, journal_wikidata):
    pub_type = row.get("type", "article-journal")
    title = row.get("title") or link_entry.get("title", "")
    authors = people(row.get("author", ""), author_wikidata)
    date_published = full_date(
        row.get("issued") or str(row.get("year", link_entry.get("year", "")))
    )
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
    if pub_type == "book":
        entry["@type"] = "Book"
        # schema.org's `pagination` domain is Article, not Book/CreativeWork --
        # a book's `page` value here is a whole-book page count, not a range
        # within a container, so it maps to `numberOfPages` instead.
        if row.get("page"):
            entry["numberOfPages"] = row["page"]
        if row.get("publisher"):
            entry["publisher"] = {"@type": "Organization", "name": row["publisher"]}
        if row.get("container-ISBN"):
            entry["isbn"] = row["container-ISBN"]

    elif pub_type == "chapter":
        entry["@type"] = "Chapter"
        if row.get("page"):
            entry["pagination"] = row["page"]
        book = {"@type": "Book", "name": row.get("container-title", "")}
        editors = people(row.get("editor", ""), author_wikidata)
        if editors:
            book["editor"] = editors
        if row.get("publisher"):
            book["publisher"] = {"@type": "Organization", "name": row["publisher"]}
        if row.get("container-ISBN"):
            book["isbn"] = row["container-ISBN"]
        entry["isPartOf"] = book

    else:  # article-journal
        entry["@type"] = "ScholarlyArticle"
        if row.get("page"):
            entry["pagination"] = row["page"]
        journal_title = row.get("container-title", "")
        periodical = {"@type": "Periodical", "name": journal_title}
        if row.get("container-ISSN"):
            periodical["issn"] = row["container-ISSN"]
        journal_wd = journal_wikidata.get(journal_title)
        if journal_wd:
            periodical["sameAs"] = journal_wd
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
    ap.add_argument(
        "--authors-csv",
        default=None,
        help="Defaults to carlquist_authors.csv next to --dataset-csv.",
    )
    ap.add_argument(
        "--journals-csv",
        default=None,
        help="Defaults to carlquist_journals.csv next to --dataset-csv.",
    )
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

    dataset_dir = os.path.dirname(args.dataset_csv)
    authors_csv = args.authors_csv or os.path.join(dataset_dir, "carlquist_authors.csv")
    journals_csv = args.journals_csv or os.path.join(dataset_dir, "carlquist_journals.csv")
    author_wikidata = load_author_wikidata(authors_csv)
    journal_wikidata = load_journal_wikidata(journals_csv)

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
        graph.append(build_entry(key, link_entry, row, slug, author_wikidata, journal_wikidata))

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
