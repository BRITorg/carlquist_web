# TODO

- QC needed: 5 citations on `biography-publications.html` had no confident
  match in the Carlquist Publications Dataset at all, mostly because they're
  tributes or notes rather than indexed journal articles — worth a manual
  look in case the dataset just doesn't cover them. (The book chapters that
  were previously in this list — "Rapateaceae," "Morphology and anatomy,"
  "Balanopaceae," and "Introduction" — all turned out to be in the dataset
  after all; they just weren't picked up by the earlier fuzzy-match pass,
  likely because their short, generic titles collided with other dataset
  entries. They were matched by hand instead and now have `[ PDF* ]`
  widgets, same as the books.)
  - "Japanese Festivals" (1965, with Helen Bauer) — a popular travel book,
    not a botanical work; not in the Carlquist Publications Dataset or
    Wikidata (unlike the 7 other books listed under "Books" on
    `biography-publications.html`, which all matched and now have
    `[ PDF* ]` widgets)
  - "Terminology of imperforate tracheary elements: a reply" (1986) — only
    the original paper is cataloged, not this response note
  - "Philip A. Munz, botanist and friend" (1975, tribute, not a paper)
  - "Peter H. Raven—recipient of the 1996 Asa Gray Award" (1997, award
    notice)
  - "Vessels in ferns: structural, ecological, and evolutionary
    significance" (2001)

- Upstream "Anatomy of Guayana Mutisieae. Part II" (1958, Mem. N. Y. Bot.
  Gard. 10:157-184) to the
  [Carlquist Publications Dataset](https://github.com/BRITorg/carlquist_publications_dataset)
  and to Wikidata: this is the root cause of why the site's now-fixed dead
  `<a href="#">PDF</a>` link for it had no automated match — the dataset
  only has Part I (1957), and Wikidata has no item for Part II either. This
  is the real fix; everything else is a stopgap around the gap in those two
  sources. In the meantime the site's widget for it points straight at
  `https://www.biodiversitylibrary.org/part/324546` (BHL item 150908, Mem.
  N.Y. Bot. Gard. v.10, pages 157-184) as a manually-identified stand-in;
  see the `unlinked-citation:1958. Anatomy of Guayana Mutisieae. Part II...`
  entry in `tools/publications/publication-links.json` for how that match
  was made. Once the record exists upstream in both places, re-run
  `match_publications.py` so this citation gets picked up the same
  automated way as the rest and the manual `publication-links.json` entry
  and its widget (including the eventual Wikidata link) can be replaced
  with the normal generated ones.

- Add schema.org JSON-LD structured data for the publications on
  `biography-publications.html` (a `ScholarlyArticle` entry per citation,
  with `identifier` for the DOI, `sameAs` for the Wikidata record,
  `datePublished`, `author`, and `isPartOf` for the journal). This is the
  format search engines actually parse for rich results and knowledge-graph
  linking, and unlike Highwire `citation_*` meta tags it isn't limited to
  one entity per page, so it fits this site's single shared bibliography
  page. All the underlying data already exists in
  `tools/publications/publication-links.json`.

- Add a `sitemap.xml` to help search engines discover and crawl all pages
  on the site — a small, general, all-upside addition independent of the
  publication-specific work above.

- Explore using Highwire Press `citation_*` meta tags (what Google Scholar
  specifically looks for) for the publications. These are page-level and
  designed for one work per page, which doesn't fit dumping them onto the
  existing shared `biography-publications.html` list — so this would mean
  creating a separate dedicated citations page (or one page per
  publication), linked from the site as its own resource, while leaving the
  original bibliography page unchanged.
