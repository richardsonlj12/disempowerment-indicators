# KEEL review procedures

Nothing reaches the public site without passing the checks below. This page is the repeatable checklist for the design's Section 7b. "The owner" is the author of KEEL (Jeremy Richardson). Each item says who does it and when.

Release 1 Stage 1 is the data site. Readings stay at "Not yet reviewed" until Stage 3.

## 1. Automated checks

These run without a person. They are listed as they exist today, not as hoped for.

**On every push to `main` and every pull request** (`.github/workflows/ci.yml`):

- [ ] Run `pytest` on Python 3.12. This is the offline suite: tests that use saved fixtures, with no network.
- Who: GitHub Actions. When: every change.

**On every push to `main`, every Monday at 12:00 UTC and on a manual run** (`.github/workflows/refresh-deploy.yml`):

- [ ] Refresh every source (scheduled and manual runs only). Each source runs on its own, so one failure does not stop the others. The runner checks each result before writing it: the `date` and `value` columns exist, dates are real and in order with no duplicates, and no value is missing. It writes `data/_health.json`.
- [ ] Run `pytest` again on the refreshed data.
- [ ] Build the indicator pages (`python -m indicators.pages`) and render the site with Quarto.
- [ ] Run `scripts/link_check.py` on the built site. It fails on any broken internal link or download, and on any link that is not relative.
- [ ] Deploy to GitHub Pages only if every earlier step passed. A failed build blocks deploy.
- Who: GitHub Actions. When: every push to `main` and every week.

**Stale data.** Each series records the date its data run through and how late new data may be. When a series is later than that, the built page shows a "stale since" badge. The badge does not block deploy.

**Pytest markers.** `pyproject.toml` excludes two markers from the default run, and CI never runs them:

- `live` tests use the network. They include the spot checks against published values (for example the BLS labor share for 2026Q2). Run them by hand with `.venv/bin/pytest -m live` after changing a fetcher and before a release.
- `release_gate` tests block a release, not development. They check that the feedback form link is filled in, that no `[DRAFT FOR OWNER]` passage remains, that every Sources link resolves, and that every internal link lands with its target just below the top bar on a desktop and a phone screen (`scripts/anchor_check.py`, in Chrome; needs `pip install -e '.[dev,browser]'` and a full build with `quarto render` first; about 6 minutes). Run them by hand before a release with `.venv/bin/pytest -m release_gate`. The Sources link test also has the `live` marker, so run both together when needed: `.venv/bin/pytest -m "live and release_gate"`.
- Who: the person cutting the release. When: before every release.

**Sources page link check** (`src/indicators/bibliography.py`):

- [ ] Run `.venv/bin/python -m indicators.bibliography check-links`. It requests every URL and DOI in `references/keel.json` with a browser-like User-Agent and writes `review/sources-link-check.md`. A link is OK, broken, or "owner browser check" (the site refuses scripts, so the status is not known).
- [ ] The owner opens each "owner browser check" link in a browser. The links already confirmed are listed in `OWNER_BROWSER_CHECKED` in `bibliography.py`, each with the date. The `release_gate` link test passes a blocked URL only if it is in that list. Add a URL there only after opening it.
- Who: the person cutting the release runs it; the owner does the browser checks. When: before every release and when a source is added.

## 2. Human gates

Each gate is the owner's decision. Claude may prepare the material and log what it checked, but does not approve a gate.

**Source reading** (before the methodology page was written; repeat for any new source)

- [ ] Read the full paper or report from the original, not a summary. Required for Chooi, Lee and Li (2026) and Moon and Boudreaux (2026).
- [ ] Check the Herdağdelen, Joren and Tamkin (2026) paper, and Imas and Schaal's post, before citing them.
- [ ] Record what each source says, what KEEL relies on and any limit on how to cite it, in `review/source-reading-notes.md`.
- Who: the owner, with Claude preparing notes. When: before a source is cited.

**Figure verification** (before Stage 1 deploy, and whenever text cites a new number)

- [ ] Trace every figure in prose, curated files, the counter-evidence panel and `config/indicators.yaml` text to its primary source, and log it in `review/figure-verification.md` with the link, the date checked and who checked.
- [ ] Do not publish a figure that has only a secondary source.
- [ ] Mark a value that an agency may revise with the date it was read.
- Who: Claude or the owner; the owner approves. When: before deploy and with each new number.

**Indicator page review** (before the first publication of each page)

- [ ] Read the reasoning, caveats, AI link, warning sign, alternative explanations and "What it doesn't show".
- [ ] Check that the closing line is present and that no sentence says more than the data show.
- Who: the owner. When: before each page is first published.

**Threshold-rule freeze** (Stage 2)

- [ ] Review the rule, the windows and the sensitivity table, then fix them with a date, before any reading is computed.
- Who: the owner. When: Stage 2.

**Readings review** (Stage 3)

- [ ] Review the retrospective as a set before anything is published.
- [ ] After that, review current readings every quarter, and whenever an automated issue asks for it.
- Who: the owner. When: Stage 3, then quarterly.

## 3. Independent second check

- [ ] Before each stage goes live, a fresh AI reviewer with no access to the project conversation reads the rendered site, `content/`, `config/` and `src/` as a skeptical AI-safety researcher.
- [ ] It looks for errors, overclaims, one-sided framing, causal language in readings, attribution beyond the evidence and broken behavior.
- [ ] Findings are saved in `review/stage1-independent-review.md` (one file per stage).
- [ ] The owner triages every finding, fixes are made, and the owner gives an explicit go-ahead to publish.
- Who: a fresh reviewer, then the owner. When: before each stage goes live.

## 4. Corrections policy

- [ ] Fix an error found after publication openly. Put a dated correction note on the affected page.
- [ ] Log the correction in `review/figure-verification.md` if a figure changed.
- [ ] Anyone can report an error through GitHub Issues (the error-report template) and give feedback in GitHub Discussions or the feedback form.
- Who: the owner decides and approves; Claude may draft. When: as soon as an error is confirmed.

## 5. Operational notes

- **The weekly refresh commits to `main` as `github-actions[bot]` every week, by design.** The commit keeps the "Data last fetched" dates on the site truthful. Do not turn on branch protection that requires pull requests for `main`: it would block the bot's push and break the refresh job.
- **Failed sources open an issue.** When a source fails, the refresh opens one GitHub issue titled "Data source failing: [source]". If an open issue with that title already exists, it opens no second one. A failed source does not stop the build: the site deploys with the last good data for that source, and the stale badge appears once the data are late.
- **Only one run at a time.** The refresh and deploy workflow allows one run at once, so two runs never race to commit `data/`.

## 6. Files in `review/`

| File | What it records |
|---|---|
| `sources-verification.md` | Each entry in `references/keel.json` checked against its original: authors, title, dates, identifiers. |
| `sources-link-check.md` | The result of the Sources page link check: each URL, its status and notes, and the links the owner must open in a browser. Rewritten by `python -m indicators.bibliography check-links`. |
| `citation-sweep.md` | A sweep of every page for factual claims that had no citation, and what was done about each. |
| `source-reading-notes.md` | The source-reading gate: what each key source says, what KEEL relies on and the limits on citing it. |
| `figure-verification.md` | Every figure on the site traced to its primary source, with link, date checked and who checked. |
| `cd1-comparison-site-selection.md` | The pre-registered rules and screening for the CD1 comparison sites, and the owner's approval. |

## 7. Versions and edits

Decided by the owner, 2026-11-19. The version number counts what has been published. Releases and stages are names from the project plan; each stage ships as a version, and the version keeps counting between stages.

| What goes live | Version |
|---|---|
| Release 1, Stage 1 (launch) | v0.1.0 |
| A batch of wording fixes, or a correction | v0.1.1, v0.1.2 … |
| Release 1, Stage 2 (reading rules fixed) | v0.2.0 |
| Release 1, Stage 3 (first readings published) | v1.0.0 |
| Release 2 (new indicators) | v1.1.0 |

- **0.x means in development, with no readings yet.** v1.0.0 marks Stage 3, when the site first says what the data mean. After 1.0, new capability raises the middle number and fixes raise the last.
- **The weekly data refresh is not a version.** The bot commits it, and "Data last fetched" on each page records it.
- **Every push the owner approves is tagged** (for example `v0.1.1`), with short release notes on GitHub that list each change. A tag marks exactly which text and code were live, so it is a safe point to return to. Data commits fall between tags by design.
- **Where a change is recorded:**

| Change | Version | Git history and release notes | Dated note on the page | Revision log (Methodology) |
|---|---|---|---|---|
| Polish: a typo, clearer wording, layout | last number | yes | no | no |
| Correction: a wrong figure, or a claim that said more than the data | last number | yes | **yes** (section 4) | no |
| A change to a fixed rule, window or AI link rating | middle number | yes | no | **yes** |
| New capability: a stage, an indicator, a chart view | middle number (1.0 for Stage 3) | yes | no | no |

- **How an edit goes live:** the owner asks for a change (or edits `content/`); Claude shows it in the local preview; the owner approves; Claude commits, tags and pushes; the site redeploys automatically within minutes. Small edits can be batched into one version.
