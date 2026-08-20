# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A static HTML site (Sherwin Carlquist's plant-science site) with no build system, package manager, or test suite — just hand-written HTML/CSS/JS from the mid-2000s. There is nothing to install, build, lint, or test; "development" means editing HTML/CSS/JS files directly and viewing them in a browser (locally via `file://` or `python3 -m http.server` from inside a site directory).

## Repository structure: two parallel site copies

The repo root contains two near-identical static-site directories, each a full copy of the same site (43 HTML pages, `css/`, `js/`, `images*/`, `menuMain/`, `menuIb/`, `menuWe/`, `pdf*/`):

- **`sherwincarlquist.com/`** — the historical snapshot. Treat as read-only/archival; don't "fix" things here unless explicitly asked to restore missing original assets. Its `pdf/`, `pdf2/`, `pdf4/` directories are gitignored (kept locally, not committed, to avoid repo bloat).
- **`sherwincarlquist.org/`** — the live/working copy. **This is the one to edit.** It's what actually deploys: `.github/workflows/static.yml` publishes this directory to GitHub Pages on every push to `main`. It intentionally excludes most of the large PDFs that `.com` has.

When asked to fix or update site content, edit `sherwincarlquist.org`, not `.com`, unless told otherwise.

## Known site quirks (already fixed once, watch for regressions)

- **Encoding**: GitHub Pages serves all `.html` with an HTTP `Content-Type: text/html; charset=utf-8` header, which overrides any in-page `<meta charset>` tag. All pages in `.org` were originally Windows-1252 bytes mislabeled as `iso-8859-1` — this caused mojibake (garbled quotes/dashes) live, even though the pages looked fine opened locally via `file://` (no HTTP header there, so the meta tag governed). All files have been normalized to real UTF-8 with `<meta charset="utf-8">`. When adding new content with special characters (curly quotes, em dashes, etc.), keep files saved as UTF-8.
- **Legacy JS libraries**: the site uses Prototype.js + script.aculo.us (`js/prototype.js`, `js/scriptaculous.js`, `js/effects.js`) for the Lightbox image popup (`js/lightbox.js`, `css/lightbox.css`), plus hand-rolled Dreamweaver-style `MM_swapImage`/`MM_preloadImages` calls (`js/menu.js`) for the left-nav hover-highlight effect, and a DHTML tooltip library (`js/tooltip.js`, `css/tooltip.css`). These are circa-2005-2008 libraries — don't assume modern JS/DOM APIs are needed or that missing behavior is a "modern browser incompatibility" before checking whether a referenced file is simply missing or misnamed.
- **Missing/misnamed assets are the recurring root cause of "broken feature" reports.** Two examples found so far: (1) `js/scriptaculous.js` was on disk as `scriptaculous.js-load=effects` (a literal filename artifact from however this snapshot was originally saved), so the `<script src="js/scriptaculous.js?load=effects">` tag 404'd and `Effect` (used by the lightbox) was undefined; (2) the menu hover-state images (`menuMain/menuMainDn_*.jpg`, `menuIb/ibMenuDn_*.jpg`, `menuWe/weMenuDn_*.gif`) and the lightbox's `imagesLightbox/loading.gif` / `closelabel.gif` were absent from the repo entirely (in both `.com` and `.org`). When something looks broken, check for a 404'd asset or a misnamed file before assuming the code logic is wrong. The Wayback Machine (web.archive.org, domain `sherwincarlquist.com`) has been a reliable source for recovering original assets that are missing from this repo — query its CDX API (`web.archive.org/cdx/search/cdx?url=sherwincarlquist.com/<path>&output=json&filter=statuscode:200`) and fetch via `https://web.archive.org/web/<timestamp>id_/<original-url>` for the raw file.
- **The contact form** (`contacts-comments.html`) posts to `../cgi-bin/sc.pl`, which does not exist on GitHub Pages (static hosting has no CGI backend). The form is intentionally kept visible with its submit button `disabled` rather than removed.

## Deployment

Pushing to `main` triggers `.github/workflows/static.yml`, which uploads `sherwincarlquist.org` as a Pages artifact and deploys it — no manual build step. Live site: https://britorg.github.io/carlquist_web/.
