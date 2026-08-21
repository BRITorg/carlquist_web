# TODO

- Make links for books: the publication-links widget (see
  `tools/publications/`) currently covers journal articles matched from the
  Carlquist Publications Dataset; the books and book chapters listed on
  `biography-publications.html` (e.g. *Comparative Wood Anatomy*, *Tarweeds
  and Silverswords*) don't yet have equivalent links out to where they can be
  found.

- Add the 3 citations below, found while matching articles that weren't
  originally linked with `[ PDF ]`: the automated matching confused
  near-identical titles (same failure mode as before — see
  `tools/publications/README.md`), so these were excluded from the 41 that
  were added as `[ PDF* ]` widgets. The correct match for each has already
  been looked up:
  - "SEM studies on vessels in ferns. 8. Platyzoma" (1999) — DOI
    `10.1071/bt97120`, Wikidata `Q100711189`.
  - "SEM studies on vessels in ferns. 14. Ceratopteris" (2000) — DOI
    `10.1016/s0304-3770(99)00023-6`, Wikidata `Q139119343`.
  - "SEM studies on vessels in the heterophyllous species of Selaginella"
    (2000) — DOI `10.2307/3088644` (JSTOR), Wikidata `Q139119342`.

- QC needed: 9 citations on `biography-publications.html` had no confident
  match in the Carlquist Publications Dataset at all, mostly because they're
  book chapters, tributes, or notes rather than indexed journal articles —
  worth a manual look in case the dataset just doesn't cover them. One of
  these ("Anatomy of Guayana Mutisieae. Part II") still has its original
  literal dead `<a href="#">PDF</a>` placeholder link, left untouched
  pending this QC:
  - "Anatomy of Guayana Mutisieae. Part II" (1958) — dataset only has Part I
    (1957, different page range)
  - "Terminology of imperforate tracheary elements: a reply" (1986) — only
    the original paper is cataloged, not this response note
  - "Rapateaceae" (1969, chapter in *Anatomy of the Monocotyledons*)
  - "Morphology and anatomy" (1969, chapter in *A Short History of Botany in
    the United States*)
  - "Philip A. Munz, botanist and friend" (1975, tribute, not a paper)
  - "Balanopaceae" (1989, *Flora of Australia* chapter)
  - "Introduction" (1995, *Hawaiian Biogeography* book)
  - "Peter H. Raven—recipient of the 1996 Asa Gray Award" (1997, award
    notice)
  - "Vessels in ferns: structural, ecological, and evolutionary
    significance" (2001)

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
