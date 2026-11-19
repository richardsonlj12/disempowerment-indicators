# Missing-citation sweep (Sources batch, Part 2)

Owner requirement: read every page and list each factual claim that rests on a source but carried no citation; add the citation (and a verified Sources entry when the work was not listed). Done on 2026-11-18 over the summary page (generated text, `content/summary-about-indicators.md`, `config/curated/*.yaml`), `content/methodology.md`, the five indicator pages (`content/indicators/*.md` and their generated summary tables and Method sections), `site/about.qmd` and `site/archive.qmd`. Every new Sources entry is logged in `review/sources-verification.md` ("Added in Part 2"). Citations follow Chicago author-date, 18th edition (rules in `references/README.md`) and link to the entry's anchor on the Sources page.

Outcomes: **added** (citation added; new entry if marked *new*), **converted** (an existing direct link replaced by a citation), **covered** (the claim sits in the same paragraph or section as a citation of the same work), **data** (a figure from the indicator's own data; the data source is cited in the summary table, the Method section and now in "Data and calculation"), **none needed** (no outside source: definitions, KEEL's own method or plans), **not added** (listed for the owner).

Summary: 16 direct source links replaced (11 converted to citations, 5 removed with the methodology's source list); links to Sources entries now in the hand-written pages: methodology 18, EA1 7, EA2 12, ED1 7, GD1 8, CD1 11 (including 8 data-source links in "Data and calculation"), plus 3 on the generated summary page and, on each indicator page, the generated data-source, Method-section and chart-marker links; 13 new verified entries; 4 claims not cited (owner decisions below).

## Summary page

| Claim | Outcome |
|---|---|
| Oversight row: Herdağdelen, Joren and Tamkin study, 50 analysts, 86 percent | converted: "[(Herdağdelen et al. 2026a)]" (generated from `oversight.yaml`, `source_key`) |
| Counter-evidence: OECD labor-based share 49.2 percent | converted: name linked to the `oecd_revenue_statistics` entry (the SDMX data request stays in the YAML) |
| Counter-evidence: 25 US national AI bills 2016–2025, 150 state bills in 2025 | converted: "[(Sajadieh et al. 2026, 341, 343)]" (pages re-read in the chapter PDF) |
| Grid values (24.2 percent, 48.6 percent, 53.0 percent, 63.2 percent) | data |
| Reading labels and inclusion criteria | none needed |

## Methodology

| Claim | Outcome |
|---|---|
| The scenario Kulveit et al. call gradual disempowerment | converted: "[Kulveit et al. (2025)]" (narrative) |
| KEEL's author's introduction | converted: "[(Richardson 2026)]" |
| Domains "following Kulveit et al." | added: "[Kulveit et al. (2025)]" |
| Rows inspired by Chooi, Lee and Li | converted: "[Chooi et al. (2026)]" (18th ed.: three authors take "et al." in citations; the prose names "Chooi, Lee and Li" elsewhere are unchanged) |
| Quotation "might serve as instrumental indicators" | added: "[(Chooi et al. 2026, 228)]" (page from the PDF) |
| Callout table and following paragraphs on the paper's layers, levels of analysis, composite scores, switching costs, well-being and agency, Goodhart warning, caveats | covered (Chooi et al. 2026 cited at the start of the section) |
| Oversight experiment (Herdağdelen, Joren and Tamkin) | converted: "[Herdağdelen et al. (2026a)]" |
| Moon and Boudreaux's formal model (RAND) | converted: "[Moon and Boudreaux (2026)]" |
| Census AI question change on 17 November 2025 | added: "[(U.S. Census Bureau 2025)]" |
| Wikimedia's improved bot detection in 2025 | added: "[(Miller 2025)]" |
| Changes in the Anthropic Economic Index release format | data (the dataset's data documentation; cited on EA2) |
| ChatGPT released 30 November 2022 | added: "[(OpenAI 2022)]" *new* |
| GitHub Copilot launch; Stack Overflow policy events | added: "([Friedman 2021]; [Dohmke 2022]; [Makyen 2022])" *new* (three entries) |
| Census wording from 19 October 2026 | added: "[(U.S. Census Bureau 2026)]" *new* |
| The two Census changes compared (level shift; "Yes" share unchanged) | covered (cited in the bullets just above) and data |
| BTOS publishes standard errors | data (cited on EA1) |
| Krueger, Millidge, Jedlicka critiques | converted: linked "David Krueger (2025)", "Beren Millidge (2025)", "P. O. Jedlicka (2026)" |
| "Kulveit et al. concede ..." | added: "[Kulveit et al. (2025)]" |
| Goodhart's law ("When a measure becomes a target ...") | **not added**: a common saying; no source verified in this batch (owner decision below) |
| Pew Research Center surveys, Reuters Institute Digital News Report (as future candidates) | none needed (named as candidates, no claim made about them) |
| ALFRED archive of past data versions | none needed (names a data service KEEL plans to use) |
| "Sources and disclosure" list | replaced by one sentence linking the Sources page (the list and the `<!-- SOURCES -->` comment removed; disclosure, closing line and feedback pointer kept) |

## EA1

| Claim | Outcome |
|---|---|
| Gradual disempowerment definition | converted: "(Kulveit et al., 2025)" to "[(Kulveit et al. 2025)]" |
| Federal Reserve Board note comparing measures; employment-weighted measures report higher adoption | converted: "[(Allen 2026)]" |
| Census testing found businesses answered "No"; level shift; new series | converted: "[(U.S. Census Bureau 2025)]" |
| New term "Super Intelligence or SI ..." from 19 October 2026 | added: "[(U.S. Census Bureau 2026)]" *new* |
| Census cites Executive Order 14434 | added: "([U.S. Census Bureau, n.d.]; [Exec. Order No. 14,434])" *new* (`census_btos`, whose page sentence the owner confirmed in a browser on 2026-11-17; `eo14434`, verified in the Federal Register) |
| Firm-size shares, "Do not know" shares, standard errors | data |
| No estimates for 6 October to 16 November 2025 during a federal funding lapse | data (Census data dictionary; `review/figure-verification.md`); "Data and calculation" now links the BTOS entry |

## EA2

| Claim | Outcome |
|---|---|
| Gradual disempowerment definition | converted |
| Kulveit et al. suggest tracking the fraction of corporate decisions made by AI | covered (cited in the sentence before) |
| Sample sizes: 10 February 2025 | added: "[(Handa et al. 2025, app. E)]" |
| 27 March 2025 | added: "[(Anthropic 2025)]" *new* |
| 15 September 2025 | added: "[(Appel et al. 2025)]" *new* |
| 15 January 2026 | added: "[(Appel et al. 2026)]" *new* |
| 24 March 2026 | added: "[(Massenkoff et al. 2026a)]" *new* |
| 26 June 2026, daily sampling | added: "[(Massenkoff et al. 2026b)]" *new* |
| September 2025 report puts automation at about 49 percent | added: "[(Appel et al. 2025)]" |
| 51.1 percent over classified conversations | data |
| Breaks (layout, plans, calendar months, Cowork) | data (release data documentation); "Data and calculation" links the dataset entry |
| Brynjolfsson, Chandar and Chen findings | converted: "[(Brynjolfsson et al. 2026, sec. 2.5, fig. 5, table 3)]" |
| First release covers 16 to 23 December 2024 | converted: "[(Handa et al. 2025, app. E)]" |
| January 2026 report describes Free, Pro and Max | added: "[(Appel et al. 2026)]" |
| Inline "Disclosure" paragraph | removed (owner decision; the generated Disclosure callout now carries both sentences) |

## ED1

| Claim | Outcome |
|---|---|
| Gradual disempowerment definition | converted |
| Quotation "the most direct financial measure of human economic participation" | converted: "[Chooi et al. (2026, 232)]" |
| Labor cost share declining since the 1980s (Chooi, Lee and Li note) | covered (same section; p. 232) |
| Imas and Schaal's "relational sector" quotations | added: "[(Imas and Schaal 2026)]" (previously uncited on this page) |
| BLS first published 2026 Q2 as 52.8 percent | added: "[(U.S. Bureau of Labor Statistics 2026)]" *new* (`bls2026`, the TED article) |
| 53.3 percent as of 17 November 2026 | data |
| FRED carries only an index version of the labor share (2017 = 100) | **not added**: a statement about FRED's holdings; FRED blocks scripted requests and no FRED page was verified in this batch (owner decision below) |
| Self-employed estimate in BLS compensation | data (BLS concepts page, logged in `review/figure-verification.md`; not a cited work) |
| Data series | "Data and calculation" now links `bls_labor_share`, `fred_cpatax`, `fred_gdp` |

## GD1

| Claim | Outcome |
|---|---|
| Gradual disempowerment definition | converted |
| "Political scientists call this the rentier-state pattern ... governments funded by resources rather than taxes tend to answer less to their citizens" | **not added**: rests on the political-science literature (for example work on the "rentier effect"); no work verified in this batch (owner decision below) |
| Kulveit et al. apply the same logic to AI | covered (cited in the paragraph before) |
| Drago and Laine, *The Intelligence Curse* | converted: "[Drago and Laine (2025)]" |
| Chooi, Lee and Li propose a related metric | converted: "[Chooi et al. (2026, 232)]" |
| OECD and US figures (48.53, 50.54, 49.20; 66.85, 63.21; 62.30 to 66.88) | data |
| "Co-optation" (rentier pattern of buying off citizens) | **not added**: same literature as above (owner decision) |
| "Source: OECD, Revenue Statistics 2025." | converted: linked to the `oecd_revenue_statistics` entry (the data KEEL reads); the *Revenue Statistics 2025* publication itself is not a separate entry |
| Data series | "Data and calculation" links the three FRED entries and the OECD entry |

## CD1

| Claim | Outcome |
|---|---|
| Gradual disempowerment definition | converted |
| Copilot technical preview 29 June 2021; generally available 21 June 2022 | added: "[(Friedman 2021)]", "[(Dohmke 2022)]" *new* |
| Chart markers (five dates) | added: one citation per marker *new* (`openai2022`, `makyen2022`, `stackoverflow2023` and the two GitHub posts); the generated Method section cites the same entries |
| "Normal" is Stack Exchange's term for a site that has left beta | data (Stack Exchange API site records; `review/cd1-comparison-site-selection.md`); the API entry is linked in "Data and calculation" |
| Wikimedia's human-traffic classification; bot accounts | data (Wikimedia Analytics API; linked) |
| Bot-detection change from March 2025; roughly 8 percent decline | converted: "[(Miller 2025)]" |
| Stack Overflow's decline began before ChatGPT | data |

## About and Archive

| Claim | Outcome |
|---|---|
| About: purpose, author, how to cite, feedback, disclosure | none needed (no claim rests on an outside work; the Substack and LinkedIn links are the author's own pages, not cited works) |
| Archive | none needed |

## Owner decisions

The four claims below stay uncited until the owner decides (fix round 1 instruction). The independent reviewer suggested sources, recorded here and not yet verified or added:

1. Goodhart's law (methodology): reviewer's suggestion: Chooi et al. 2026, p. 234 (which cites Goodhart 1984), or Strathern 1997 for the "measure becomes a target" wording.
2. Rentier-state pattern (GD1, line 15) and co-optation (GD1, line 48): reviewer's suggestion: Kulveit et al. 2025, sec. 4.1, which discusses rentier states (citing Beblawi and Luciani 1987) and loyalty secured through distribution.
3. FRED index version of the labor share (ED1): reviewer's suggestion: FRED series PRS85006173 (index, 2017 = 100), as a data-source entry.
4. "OECD, Revenue Statistics 2025" (GD1): keep linked to the dataset entry, or add the publication as its own reference entry.
