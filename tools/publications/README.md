# Publication link mapping

`publication-links.json` records, for every disabled `[ PDF ]` link that used
to appear on sherwincarlquist.org, which publication in the
[Carlquist Publications Dataset](https://github.com/BRITorg/carlquist_publications_dataset)
it corresponds to. It's keyed by the original local PDF path the site used to
link to (e.g. `pdf2/1960_Anatomy_of_Xyridaceae_1960.PDF`) — those paths never
pointed to a real file, but they're still useful as a stable identifier for
"which citation is this."

This mapping is the source data behind the DOI / source / Wikidata links
shown in each PDF widget on the live site (see
`sherwincarlquist.org/js/pdf-widget.js`) — those links are baked directly into
the site's HTML, so this file isn't loaded by the site itself. It's kept here
so the mapping can be audited, corrected, or extended later without having to
redo the matching from scratch.

`match_publications.py` is the script that produced it: it scans the site's
HTML for PDF citations and fuzzy-matches each one against a CSV export of the
dataset by year and title. See the script's docstring (`--help`) for usage
and for what re-running it later would and wouldn't do, given the site no
longer contains the original dead-link markup it looks for.

A first automated pass matched 300/304 entries with high or medium
confidence and 0 with low confidence, but a handful of matches were still
wrong — mostly citations from Carlquist's numbered monograph series (e.g.
"SEM Studies on Vessels in Ferns. 1. ..." vs "...6. ...") where the shared
title text fooled the similarity scoring despite the series number in the
citation and the number in the matched title disagreeing. Four such errors
were found by manually cross-checking every matched title's site citation
text and are already corrected in `publication-links.json`. If you re-run
the matcher, diff its output against the current file rather than trusting
it blindly, and pay particular attention to numbered-series titles.
