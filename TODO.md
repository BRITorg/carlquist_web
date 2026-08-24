# TODO

- Low priority: 5 citations on `biography-publications.html` have no match in
  the Carlquist Publications Dataset. Except maybe the reply note, these are
  all expected non-matches since none of them are scientific articles (a
  travel book, a tribute, an award notice, a response note) — the dataset
  simply doesn't cover that kind of content today. Revisit if/when we decide
  to expand the dataset's scope beyond indexed journal articles/books; until
  then these are correctly left unlinked. (The book chapters that were
  previously in this list — "Rapateaceae," "Morphology and anatomy,"
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
    the original paper is cataloged, not this response note; the likeliest
    candidate of the five for an eventual dataset addition since it's the
    closest thing to a scientific article
  - "Philip A. Munz, botanist and friend" (1975, tribute, not a paper)
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

- Decided against Highwire Press `citation_*` meta tags: Google Scholar's own
  inclusion guidelines
  (https://scholar.google.com/intl/en/scholar/inclusion.html) require one
  article per URL — "Place each article and each abstract in a separate HTML
  or PDF file. At this time, we're unable to effectively index multiple
  abstracts on the same webpage" — and the tags "normally apply only to the
  exact page on which they're provided." That's a hard requirement, not a
  style preference, and it would mean a page per publication, which we've
  chosen not to build. The schema.org JSON-LD item above is the path
  forward instead, since it supports multiple entities on one page and
  reuses this site's existing single shared bibliography page.
