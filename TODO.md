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

- Decided against Highwire Press `citation_*` meta tags: Google Scholar's own
  inclusion guidelines
  (https://scholar.google.com/intl/en/scholar/inclusion.html) require one
  article per URL — "Place each article and each abstract in a separate HTML
  or PDF file. At this time, we're unable to effectively index multiple
  abstracts on the same webpage" — and the tags "normally apply only to the
  exact page on which they're provided." That's a hard requirement, not a
  style preference, and it would mean a page per publication, which we've
  chosen not to build. schema.org JSON-LD (now added to
  `biography-publications.html`, see `tools/publications/generate_jsonld.py`)
  was the path taken instead, since it supports multiple entities on one
  page and reuses this site's existing single shared bibliography page.

- Check out how the site looks and works on a mobile device. The markup
  predates responsive design (hand-rolled Dreamweaver-era layout, fixed-width
  tables/menus), so this needs an actual look rather than an assumption —
  worth checking things like the left-nav hover menu (which relies on mouse
  hover, not touch), the lightbox popups, and whether the fixed-width layout
  causes horizontal scrolling or illegibly small text on a phone screen.
