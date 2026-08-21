# Sherwin Carlquist — Plant Discoveries (Web Archive)

This repository is a preserved copy of **sherwincarlquist.com**, the personal
website of botanist Sherwin Carlquist, showcasing his research on plant
discoveries, island biology, wood anatomy, and floral morphology.

**Live site:** https://britorg.github.io/carlquist_web/

## About this archive

The original site was mirrored with `wget` on **July 2, 2020**, prior to the
launch of an NSF-funded project on Carlquist's work. That backup is the basis
for this repository, which is now published via GitHub Pages so the content
remains publicly accessible.

This git repository contains two primary directories:

[sherwincarlquist.com](sherwincarlquist.com/) - this directory contains the site contents as of 2020-07-02 with some exceptions. PDFs of journal articles from the original site are not included in this repository.
[sherwincarlquist.org](sherwincarlquist.org/) - this directory contains the original content with minor changes to improve readibility and to augment some information. This version of the content is published to the live site (link above) using GitHub Pages.

The site covers topics including:

- Island biology
- Tarweeds & silverswords
- Floral anatomy
- Ecological and systematic wood anatomy
- Wood evolution
- Fern & monocot xylem
- Leaf anatomy
- Gnetales
- Biography & publications
- Recent work

## Status

This is a static archive of the original site as it existed in 2020. Content,
images, and links are preserved as captured; some assets or external links
from the original site may no longer resolve.

## Changes made to the .org version

Since the original 2020 mirror, `sherwincarlquist.org` has received the
following fixes to make it work correctly as a static site on GitHub Pages
(`sherwincarlquist.com` is left untouched as the historical snapshot):

- **Character encoding**: GitHub Pages serves HTML with an HTTP
  `charset=utf-8` header that overrides the pages' own charset meta tag. The
  underlying file bytes were Windows-1252 (mislabeled as ISO-8859-1), which
  caused smart quotes and em-dashes to render as garbled text online. 23 HTML
  files and `js/tooltip.js` were converted to real UTF-8 and their meta tags
  updated to match.
- **Home page image lightbox**: The Lightbox popup used by the home page's
  image slideshow was broken because `js/scriptaculous.js` had been saved to
  disk under the wrong filename, so the script 404'd. The file was renamed
  correctly and the missing `js/effects.js` and lightbox loading/close-icon
  images were restored from the Wayback Machine archive of the original
  live site.
- **Contact form**: `contacts-comments.html` posts to a CGI script that
  doesn't exist under GitHub Pages' static hosting. Rather than removing the
  form, its submit button was disabled so the fields remain visible.
- **Publication PDF links**: Carlquist originally linked directly to PDF files 
  hosted on his site, but none of these publication PDFs are hosted in this
  repository, so each `[ PDF ]` link is now
  an inline disclosure widget: activating it (by click or keyboard) expands
  to "PDF may be available at these external sources" followed by real DOI,
  source, and/or Wikidata links, matched against the
  [Carlquist Publications Dataset](https://github.com/BRITorg/carlquist_publications_dataset).
  This dataset contains articles that were listed by Carlquist on his site, but not linked so these
  links have been added to the bibliography page with `[ PDF* ]` and a note clarifying
  that Carlquist did not originally link these files. 
  These links are written directly into the static HTML so they're crawlable by search engines and accessible to
  screen readers by default — `js/pdf-widget.js` only adds the collapse/expand
  behavior on top. The mapping from each PDF link to its matched publication
  is kept in `tools/publications/` for future auditing.
- **Left-nav hover-highlight menus**: The hover-highlight images for the
  left-side navigation menus (main, island biology, wood evolution) were
  missing from the repo, so hovering a menu item showed a broken-image icon.
  The main menu's images were recovered from the Wayback Machine; the island
  biology and wood evolution submenu images don't exist in any archive, so
  they were synthesized by applying the same brightness reduction used by
  the recovered main-menu images to their existing normal-state counterparts.

## About The Sherwin Carlquist Extended Specimen Network

This site and web archive are preserved and shared as part of a collaborative project to link and preserve Carlquist's specimens, field images, publications, and archival materials. Details about this project and further Carlquist resources are available at https://britorg.github.io/carlquist_esn/. 