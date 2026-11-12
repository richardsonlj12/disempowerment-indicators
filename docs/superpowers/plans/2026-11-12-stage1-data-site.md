# Stage 1 — Data Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the Stage 1 data site: eight indicator pages with live public data, interactive charts, explanatory text and caveats, a summary grid with every reading shown as "Not yet reviewed", a counter-evidence panel, and methodology/archive/about pages — refreshed weekly by GitHub Actions and deployed to GitHub Pages.

**Architecture:** A Python package (`src/indicators/`) fetches each public source, validates it, and writes tidy CSV plus a metadata JSON per series into `data/`. A config folder holds the indicator registry, readings file and hand-curated datasets. A page generator turns the registry plus owner-editable prose into Quarto pages; Quarto's built-in Observable JS renders the charts. The Python side never imports anything from the site, and the site only reads files from `data/` and `config/`.

**Tech Stack:** Python ≥3.12 (local 3.14), pandas, requests, PyYAML, pytest; Quarto ≥1.11 with Observable JS (Observable Plot + Inputs); GitHub Actions; GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-11-09-disempowerment-indicators-design.md` (approved 2026-11-12). Sections 4.4–4.5's threshold and reading logic, the retrospective, and the review-pending GitHub issues belong to Stages 2–3 and are **out of scope** here.

## Global Constraints

- $0: free tools and free data only; no paid APIs.
- **No API keys in Stage 1.** Use keyless endpoints (FRED `fredgraph.csv`, Stack Exchange anonymous quota, Wikimedia with User-Agent). If a source truly needs a key, stop and ask the owner; keys would go only in GitHub Actions Secrets.
- HTTP User-Agent for every request: `disempowerment-indicators/0.1 (+https://github.com/richardsonlj12/disempowerment-indicators)`. Never put the owner's email in requests.
- Avoided sources: OpenSecrets API, EIU, Gallup microdata, ADP, Lightcast, S&P.
- Nothing from `../research/` (the private folder beside the repo) is copied into the repo. Figures are re-verified from primary sources and cited by primary URL.
- Secondary-only figures (marked [S] in research) are never published.
- Readings in Stage 1: every indicator shows **"Not yet reviewed"**. No script produces a reading.
- Exposure-row indicators (E2, G2) use the exposure scale (Low / Rising / Pervasive); all others use the influence scale (Leverage intact / Leverage eroding / Lock-in signals). Both scales also allow "No signal / insufficient data" and "Not yet reviewed".
- Pre-AI trend window for structural series: **2010-01-01 to 2019-12-31**, linear fit. Retrospective start: **2022Q4** (Stage 3; mentioned on pages only).
- Site base path: `https://richardsonlj12.github.io/disempowerment-indicators/`. All links and data URLs relative.
- G2 page: the defense/intelligence exclusion appears in the headline area, in the chart title ("Civilian federal AI use cases"), and in "What it doesn't show".
- Accessible, readable in light and dark mode, usable at phone width.
- Every commit ends with: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Review Focus

1. **A source answers 200 OK with an HTML error page or a changed schema.** Expected: validation rejects it, the last good data stays in place, the series is marked stale, and no garbage is written. → test `test_refresh_keeps_last_good_on_invalid_payload` (Task 9).
2. **One source fails during a scheduled refresh.** Expected: the other sources still update and deploy; the failing series keeps its old data with a "stale since <date>" badge, and a GitHub issue opens (deduplicated by title). → `test_refresh_isolates_source_failure` (Task 9); issue step in Task 12.
3. **Series breaks** (BTOS question change 2025-11-17; Wikimedia bot reclassification). Expected: the chart does not draw a line across the break, and the break is annotated. → `test_series_break_splits_segments` (Task 2) plus the chart's `segment` handling (Task 11).
4. **Rate limit hit partway through** (Stack Exchange anonymous quota of 300/day; Wikimedia limits). Expected: partial results are not saved as if complete; the run resumes incrementally next time from cached months. → `test_stackexchange_partial_quota_not_written` (Task 8).
5. **Base path on GitHub Pages.** Expected: CSV downloads and inter-page links work under `/disempowerment-indicators/`. → link check in the deploy workflow (Task 12), run against the rendered `_site` with that prefix.

---

## File Structure

```
disempowerment-indicators/
  pyproject.toml                      # package + deps + pytest config
  .gitignore
  README.md                           # how to run, preview, review
  REVIEW.md                           # review checklist (spec 7b)
  review/figure-verification.md       # log: each published figure → primary source, checked date
  config/
    indicators.yaml                   # registry: 8 indicators, metadata, series, caveats
    readings.yaml                     # dated readings (Stage 1: all not_yet_reviewed)
    ai_companies.yaml                 # G3 company list, inclusion criteria, changelog
    curated/production_consumption.yaml   # C2 points with citations
    curated/counter_evidence.yaml         # counter-evidence panel items
  content/indicators/<ID>.md          # owner-editable prose per indicator (why, shows/doesn't, what would change)
  src/indicators/
    __init__.py
    http.py                           # get(url, **params) with User-Agent, retries, content-type check
    store.py                          # series files: write/read/validate, metadata, staleness
    registry.py                       # load + validate indicators.yaml and readings.yaml
    trend.py                          # pre-AI linear trend + deviation; rolling change
    curated.py                        # load + validate curated YAML
    sources/fred.py                   # E1 labor share, profit share; G1 US tax components
    sources/dfa.py                    # E3 wealth shares
    sources/btos.py                   # E2 firm AI adoption
    sources/oecd.py                   # G1 OECD revenue structure
    sources/omb.py                    # G2 federal AI use cases
    sources/lda.py                    # G3 lobbying
    sources/stackexchange.py          # C1 Stack Overflow monthly questions
    sources/wikimedia.py              # C1 Wikipedia human pageviews, editors
    refresh.py                        # run all sources, isolate failures, write data/_health.json
    pages.py                          # generate site pages from registry + content
  data/                               # generated: <series_id>.csv, <series_id>.meta.json, _health.json
  site/
    _quarto.yml
    index.qmd  methodology.qmd  archive.qmd  about.qmd
    _indicator_template.qmd           # template rendered by pages.py into indicators/<ID>.qmd
    js/charts.js                      # shared OJS chart helpers
    styles.scss
  tests/
    fixtures/<source>/...             # recorded sample responses
    test_*.py
  .github/workflows/ci.yml            # tests on push/PR
  .github/workflows/refresh-deploy.yml  # weekly refresh + build + deploy
```

---

### Task 1: Project skeleton and local tooling

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `README.md`, `src/indicators/__init__.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: installable package `indicators` (`pip install -e ".[dev]"`); pytest marker `live` for tests that hit the network (excluded by default).

- [ ] **Step 1:** Create a virtual environment in `.venv` with python3 and record the commands in README ("Setup").
- [ ] **Step 2:** Write `pyproject.toml`: name `disempowerment-indicators`, `requires-python = ">=3.12"`, deps `pandas`, `requests`, `pyyaml`; dev extra `pytest`; `[tool.pytest.ini_options]` with `markers = ["live: hits the network"]` and `addopts = "-m 'not live'"`; src layout.
- [ ] **Step 3:** `.gitignore`: `.venv/`, `__pycache__/`, `site/_site/`, `site/.quarto/`, `site/data/`, `site/config/`, `site/indicators/` (generated pages), `.DS_Store`.
- [ ] **Step 4:** Smoke test `test_package_imports` asserting `import indicators` works. Run `pytest -v` → PASS.
- [ ] **Step 5:** Install Quarto ≥1.11 for local preview without admin rights: download the macOS tarball from the official GitHub release, extract under `~/.local/opt/quarto`, symlink `quarto` into `~/.local/bin`. Verify `quarto --version` ≥ 1.11. Document in README ("Preview the site").
- [ ] **Step 6:** Commit `chore: project skeleton`.

---

### Task 2: Series store and metadata contract

**Files:**
- Create: `src/indicators/store.py`, `tests/test_store.py`

**Interfaces:**
- Produces:
  - `SeriesMeta` dataclass: `series_id: str`, `indicator_id: str`, `title: str`, `units: str`, `frequency: Literal["weekly","biweekly","monthly","quarterly","annual","irregular"]`, `source_name: str`, `source_url: str`, `license: str`, `fetched_at: str` (ISO UTC), `data_through: str` (ISO date), `max_lag_days: int`, `breaks: list[dict]` (each `{"date": "YYYY-MM-DD", "note": str}`), `notes: str = ""`.
  - `validate_frame(df: pd.DataFrame) -> None` — requires columns `date` (datetime, unique, ascending) and `value` (float, no NaN); optional `segment` (int). Raises `ValueError` with a specific message.
  - `assign_segments(df, breaks) -> pd.DataFrame` — adds `segment` that increments at each break date.
  - `write_series(df, meta: SeriesMeta, data_dir: Path) -> None` — validates, then writes `<series_id>.csv` (`date,value,segment`) and `<series_id>.meta.json` atomically (temp file + rename).
  - `read_series(series_id, data_dir) -> tuple[pd.DataFrame, SeriesMeta]`.
  - `staleness(meta, today: date) -> int | None` — days past `data_through + max_lag_days`, or `None` if not stale.

- [ ] **Step 1: Tests** in `tests/test_store.py`:
  - `test_write_read_roundtrip` — values and meta survive a round trip.
  - `test_validate_rejects_duplicate_dates`, `test_validate_rejects_nan`, `test_validate_rejects_unsorted`.
  - `test_series_break_splits_segments` — breaks at `2025-11-17` → rows before have `segment == 0`, on/after have `segment == 1`.
  - `test_staleness` — `data_through=2026-06-30`, `max_lag_days=120`, today `2026-11-12` → `15`; today `2026-10-01` → `None`.
  - `test_write_is_atomic_on_invalid` — invalid frame leaves an existing file untouched.
- [ ] **Step 2:** Run `pytest tests/test_store.py -v` → FAIL (module missing).
- [ ] **Step 3:** Implement `store.py` with the interfaces above.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat: series store and metadata contract`.

---

### Task 3: Indicator registry and readings file

**Files:**
- Create: `config/indicators.yaml`, `config/readings.yaml`, `src/indicators/registry.py`, `tests/test_registry.py`

**Interfaces:**
- Produces:
  - `Indicator` dataclass: `id`, `domain` (`economic|government|cultural`), `layer` (`exposure|erosion|lockin`), `scale` (`exposure|influence`), `name`, `short_takeaway`, `attribution` (`strong|moderate|weak`), `attribution_criteria: dict` (keys `directness`, `comparison_group`, `timing`, `confounders`, each a one-line string), `comparison` (`structural|ai_native|curated`), `tier` (`1|2|3`), `series: list[str]` (series IDs), `primary_series: str | None`, `chart_title: str`, `headline_caveat: str | None`, `sources: list[dict]` (`name`, `url`, `license`).
  - `load_registry(path) -> list[Indicator]`, `load_readings(path) -> dict[str, list[Reading]]`.
  - `Reading` dataclass: `indicator_id`, `state` (`not_yet_reviewed|no_signal|low|rising|pervasive|intact|eroding|lockin`), `date: str | None`, `rationale: str | None`, `kind` (`current|retrospective`).
  - `current_reading(readings, indicator_id) -> Reading` — latest `current` reading, else a `not_yet_reviewed` Reading.
- Registry content (exact IDs, layers, scales, comparisons, tiers from spec Sec. 5):
  - E1 labor share — erosion, influence, weak, structural, tier 1; series `labor_share_nfb`, `profit_share`; primary `labor_share_nfb`.
  - E2 firm AI adoption — exposure, exposure scale, strong, ai_native, tier 1; series `btos_ai_use`.
  - E3 wealth concentration — lockin, influence, weak, structural, tier 1; series `wealth_top1`, `wealth_top01`; primary `wealth_top1`.
  - G1 labor-based tax share — erosion, influence, weak, structural, tier 1/2 (store `1`); series `us_labor_tax_share` (primary), `oecd_labor_tax_share_usa`, `oecd_labor_tax_share_avg`.
  - G2 federal AI use cases — exposure, exposure scale, strong, ai_native, tier 2; series `fed_ai_use_cases_total`, `fed_ai_use_cases_high_impact`; `chart_title: "Civilian federal AI use cases"`; `headline_caveat` stating that defense and intelligence uses are largely excluded.
  - G3 AI-company lobbying — lockin, influence, moderate, ai_native, tier 1; series `ai_lobbying_spend`, `ai_lobbying_share`.
  - C1 knowledge commons — erosion, influence, moderate, structural, tier 1; series `so_questions_monthly`, `wiki_user_pageviews_en`, `wiki_active_editors_en`; primary `None` (owner decides between series).
  - C2 production vs consumption — erosion (row placement: erosion), influence, strong, curated, tier 3; series none (curated file).
  - Attribution criteria text drafted from the research report's reasoning; marked `# DRAFT — owner review in Stage 2`.
- `readings.yaml`: one `not_yet_reviewed` entry per indicator, `date: null`.

- [ ] **Step 1: Tests:**
  - `test_registry_has_eight_indicators_with_expected_ids` — `{"E1","E2","E3","G1","G2","G3","C1","C2"}`.
  - `test_exposure_layer_uses_exposure_scale` — for every indicator, `layer == "exposure"` ⇔ `scale == "exposure"`.
  - `test_reading_state_matches_scale` — loading a reading `eroding` for E2 raises `ValueError`.
  - `test_all_readings_not_yet_reviewed_in_stage1`.
  - `test_g2_has_headline_caveat_and_civilian_title`.
  - `test_every_series_id_unique_across_registry`.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Write YAML files and `registry.py`.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat: indicator registry and readings file`.

---

### Task 4: HTTP helper and trend calculations

**Files:**
- Create: `src/indicators/http.py`, `src/indicators/trend.py`, `tests/test_http.py`, `tests/test_trend.py`

**Interfaces:**
- Produces:
  - `get(url: str, params: dict | None = None, expect: Literal["csv","json","any"] = "any", timeout: int = 60) -> requests.Response` — sets the Global Constraints User-Agent; retries 3× with backoff on 429/5xx (honor `Retry-After`); raises `SourceError` if `expect="csv"` or `"json"` and the body looks like HTML (`<html` or `<!doctype` in the first 512 bytes, case-insensitive).
  - `class SourceError(Exception)`.
  - `pre_ai_trend(df, start="2010-01-01", end="2019-12-31") -> pd.DataFrame` — adds `trend` (linear OLS fit on the window, extrapolated over all dates) and `deviation = value - trend`.
  - `rolling_change(df, periods: int) -> pd.Series` — difference over `periods` rows.

- [ ] **Step 1: Tests:** `test_get_sets_user_agent` (mock with `responses` or monkeypatch), `test_get_rejects_html_when_csv_expected`, `test_get_retries_on_429`; `test_pre_ai_trend_exact_on_linear_series` (value = 2·t+1 → deviation all 0), `test_pre_ai_trend_detects_break_after_2022` (add −1.5 after 2023-01-01 → mean deviation after 2023 ≈ −1.5).
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement (add `responses` to dev deps if used). **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat: http helper and trend calculations`.

---

### Task 5: Economic sources — E1, E3, and G1 (US)

**Files:**
- Create: `src/indicators/sources/fred.py`, `src/indicators/sources/dfa.py`, fixtures under `tests/fixtures/fred/`, `tests/fixtures/dfa/`, `tests/test_sources_econ.py`

**Interfaces:**
- Consumes: `http.get`, `store.SeriesMeta`, `store.write_series`.
- Produces: each source module exposes `fetch() -> list[tuple[pd.DataFrame, SeriesMeta]]` (this signature is shared by every source module in Tasks 5–8).
  - `fred.fetch()` returns `labor_share_nfb`, `profit_share`, `us_labor_tax_share`.
  - `dfa.fetch()` returns `wealth_top1`, `wealth_top01`.

- [ ] **Step 1: Choose and verify series (record in `review/figure-verification.md`):**
  - Labor share must be in **percent** (not an index). Prefer FRED `fredgraph.csv?id=<ID>`; if FRED has only an index, use the BLS published labor-share level series instead. The value for 2026Q2 must be **52.8**.
  - Profit share: corporate profits after tax (with IVA and CCAdj) ÷ GDP, both from FRED, in percent.
  - US labor-based tax share: (personal current taxes + contributions for government social insurance) ÷ (total government current tax receipts + contributions for government social insurance), BEA NIPA via FRED, quarterly, percent. Write the formula and series IDs into the meta `notes`.
  - DFA: the Federal Reserve's distributional financial accounts CSV of net worth shares by percentile group (top 1%, top 0.1%), quarterly since 1989.
- [ ] **Step 2: Tests** (offline, fixtures recorded from the real endpoints): `test_labor_share_parses_percent`, `test_tax_share_formula` (hand-computed ratio from fixture rows), `test_dfa_top1_and_top01_parsed`, and `test_meta_fields_complete` (no empty `source_url`/`license`). **Live** tests (`@pytest.mark.live`): `test_live_labor_share_2026q2_is_52_8` (±0.05).
- [ ] **Step 3:** Run → FAIL. **Step 4:** Implement. **Step 5:** Run offline tests → PASS; run `pytest -m live tests/test_sources_econ.py` → PASS.
- [ ] **Step 6:** Commit `feat: FRED and DFA sources (E1, E3, G1-US)`.

---

### Task 6: Adoption and tax-structure sources — E2 and G1 (OECD)

**Files:**
- Create: `src/indicators/sources/btos.py`, `src/indicators/sources/oecd.py`, fixtures, `tests/test_sources_btos_oecd.py`

**Interfaces:**
- Produces: `btos.fetch()` → `btos_ai_use` (percent of US firms reporting AI use, national, biweekly, firm-weighted) with `breaks=[{"date": "2025-11-17", "note": "Question changed from AI use 'in producing goods or services' to 'in any business function'"}]`; `oecd.fetch()` → `oecd_labor_tax_share_usa`, `oecd_labor_tax_share_avg` (annual, (PIT 1100 + SSC 2000) ÷ total tax revenue, percent).

- [ ] **Step 1:** Locate the Census BTOS national time-series download for the AI-use question; record URL and the exact question text per period in meta `notes`. Locate the OECD Revenue Statistics SDMX endpoint.
- [ ] **Step 2: Tests:** `test_btos_break_assigned` (segment increments at 2025-11-17), `test_btos_value_is_percent` (0 ≤ value ≤ 100), `test_oecd_labor_share_formula`; **live:** `test_live_btos_may_2026_near_19_8` (a May-2026 period within 19.3–20.3), `test_live_oecd_avg_2023` ((PIT+SSC) for the OECD average in 2023 = 49.2 ± 0.3).
- [ ] **Step 3:** FAIL → **Step 4:** implement → **Step 5:** PASS (offline and live).
- [ ] **Step 6:** Commit `feat: BTOS and OECD sources (E2, G1-OECD)`.

---

### Task 7: Government sources — G2 and G3

**Files:**
- Create: `src/indicators/sources/omb.py`, `src/indicators/sources/lda.py`, `config/ai_companies.yaml`, fixtures, `tests/test_sources_gov.py`

**Interfaces:**
- Produces: `omb.fetch()` → `fed_ai_use_cases_total`, `fed_ai_use_cases_high_impact` (annual, one row per inventory year), plus a per-agency table written as `data/fed_ai_use_cases_by_agency.csv` (`year,agency,total,high_impact`). `lda.fetch()` → `ai_lobbying_spend` (USD per quarter, summed over `ai_companies.yaml` clients), `ai_lobbying_share` (that ÷ total reported lobbying for the quarter, percent).
- `ai_companies.yaml` schema: `criteria: str`, `companies: [{name, lda_client_names: [str], added: date, reason: str}]`, `changelog: [{date, change}]`. Initial list: frontier-model developers (e.g., OpenAI, Anthropic, Google DeepMind/Alphabet AI-specific registrations, xAI, Meta, Microsoft, Nvidia) — the inclusion criteria text is drafted and marked for owner review.

- [ ] **Step 1:** Confirm the OMB inventory CSV locations for each available year (2023, 2024, 2025) and how "high-impact" (2025) maps to the earlier "rights-/safety-impacting" field; record the mapping and the 2024 baseline choice (1,757 vs 2,133) in meta `notes`. Confirm the LDA.gov API endpoint, pagination and whether a key is required (if required → stop and ask the owner).
- [ ] **Step 2: Tests:** `test_omb_counts_from_fixture`, `test_omb_high_impact_mapping_documented` (meta notes mention the field mapping), `test_lda_sums_only_listed_clients`, `test_lda_share_between_0_and_100`, `test_ai_companies_every_entry_has_reason_and_date`. **Live:** `test_live_omb_2025_total` — assert the count equals what the 2025 repo yields and that it was logged in `review/figure-verification.md` (if it is not 3,611, record the difference there).
- [ ] **Step 3:** FAIL → **Step 4:** implement (LDA: cache per-quarter results in `data/_cache/lda/` so a rerun refetches only the latest two quarters) → **Step 5:** PASS.
- [ ] **Step 6:** Commit `feat: OMB and LDA sources (G2, G3)`.

---

### Task 8: Cultural sources — C1

**Files:**
- Create: `src/indicators/sources/stackexchange.py`, `src/indicators/sources/wikimedia.py`, fixtures, `tests/test_sources_culture.py`

**Interfaces:**
- Produces: `stackexchange.fetch()` → `so_questions_monthly` (count of questions created per calendar month on stackoverflow, 2008-09 onward, via `/2.3/questions` with `filter=total`); `wikimedia.fetch()` → `wiki_user_pageviews_en` (monthly, `agent=user`, 2015-07 onward) and `wiki_active_editors_en` (monthly). Wikimedia meta `breaks` carries the bot-reclassification date (look it up in Wikimedia's own announcement and cite it).

- [ ] **Step 1: Tests:** `test_so_month_bounds` (from/to timestamps cover exactly one calendar month, UTC), `test_stackexchange_partial_quota_not_written` (when the mock returns `quota_remaining: 0` partway through, `fetch` raises `SourceError` and returns no partial frame; already-complete months are kept in `data/_cache/stackexchange/` and the current month is never cached), `test_wikimedia_user_agent_set`, `test_wikimedia_break_assigned`.
- [ ] **Step 2:** FAIL → **Step 3:** implement (only refetch the last two months plus uncached months) → **Step 4:** PASS; live smoke `pytest -m live tests/test_sources_culture.py`.
- [ ] **Step 5:** Commit `feat: Stack Exchange and Wikimedia sources (C1)`.

---

### Task 9: Curated datasets and the refresh runner

**Files:**
- Create: `src/indicators/curated.py`, `config/curated/production_consumption.yaml`, `config/curated/counter_evidence.yaml`, `src/indicators/refresh.py`, `tests/test_curated.py`, `tests/test_refresh.py`

**Interfaces:**
- Produces:
  - Curated item schema: `{id, label, domain, metric, value, unit, date, source_name, source_url, verified: bool, verified_on: date | null, note}`; C2 items also have `side: production|consumption` and `pair: str` (e.g., `music_deezer`).
  - `load_curated(path) -> list[dict]` — validates schema; `published(items)` returns only `verified: true` items.
  - `refresh.run(data_dir: Path, sources: list[module] | None = None, today: date | None = None) -> dict` — calls each source's `fetch()` independently; on exception or validation error, keeps existing files, records `{"status": "failed", "error": str, "since": <first failure date>}`; on success, writes the series and records `{"status": "ok", "data_through": ...}`. Writes `data/_health.json` and returns it. CLI: `python -m indicators.refresh` exits 1 if any source failed (after writing everything else).
- Curated content: C2 pairs (music: Deezer upload share vs. stream share; web articles: Graphite AI share of new articles; news: UMD/Pangram) and counter-evidence items (labor-tax share rising per OECD; AI legislation counts from Stanford AI Index / CSET AGORA / OECD.AI). Each is entered **only after** checking the primary source; anything not verifiable from a primary source stays `verified: false`.

- [ ] **Step 1: Tests:** `test_curated_requires_source_url`, `test_unverified_items_not_published`, `test_c2_pairs_have_both_sides_or_flagged`, `test_refresh_isolates_source_failure` (one fake source raises; another succeeds; health shows one `failed`, one `ok`; the successful series file is written), `test_refresh_keeps_last_good_on_invalid_payload` (an existing good file is unchanged after a source returns an invalid frame), `test_failure_since_date_persists` (a second consecutive failure keeps the first `since` date).
- [ ] **Step 2:** FAIL → **Step 3:** implement and fill the curated YAML with verified entries (log each in `review/figure-verification.md`) → **Step 4:** PASS.
- [ ] **Step 5:** Run `python -m indicators.refresh` for real; commit the resulting `data/` along with the code. Commit `feat: curated datasets and refresh runner`.

---

### Task 10: Indicator prose content

**Files:**
- Create: `content/indicators/E1.md` … `C2.md` (8 files)

**Interfaces:**
- Produces: each file has exactly these level-2 headings, which `pages.py` (Task 11) splits on: `## Why this matters for gradual disempowerment`, `## What it shows`, `## What it doesn't show`, `## What would change our reading`, `## Caveats`. Plus front matter `takeaway:` (one sentence).

- [ ] **Step 1:** Draft prose for each indicator from the spec (Sec. 4.6 guards, Sec. 5 notes) in plain language for journalists and policymakers, with precise terms for researchers. Required content:
  - Economic pages (E1, E2, E3): include the welfare-vs-influence note.
  - E2: include the augmentation-vs-displacement note, the firm-weighted vs employment-weighted contrast, the 2025-11-17 break, and the ~10–11% "don't know" share.
  - G1: state plainly that it currently points away from disempowerment.
  - G2: defense/intelligence exclusion in "What it doesn't show"; self-reported data and definitional changes.
  - C1: the Stack Overflow decline began around 2020, before ChatGPT; the Wikimedia break.
  - Every page: "conditions under which the hypothesized mechanism would operate", not proof.
- [ ] **Step 2:** Every number in the prose traced to a primary source and logged in `review/figure-verification.md`; remove any that can't be.
- [ ] **Step 3:** **Owner review gate:** the owner reads all eight files and approves or edits them (spec 7b, "Indicator page review").
- [ ] **Step 4:** Commit `docs: indicator page prose (owner-reviewed)`.

---

### Task 11: Quarto site, page generator and charts

**Files:**
- Create: `src/indicators/pages.py`, `site/_quarto.yml`, `site/index.qmd`, `site/methodology.qmd`, `site/archive.qmd`, `site/about.qmd`, `site/_indicator_template.qmd`, `site/js/charts.js`, `site/styles.scss`, `tests/test_pages.py`

**Interfaces:**
- Consumes: `load_registry`, `load_readings`, `current_reading`, `read_series`, `staleness`, `load_curated`/`published`, `pre_ai_trend`, the content files.
- Produces: `pages.build(repo_root: Path) -> None` — copies `data/` → `site/data/` and needed `config/` files → `site/config/`, then writes `site/indicators/<ID>.qmd` for all eight indicators from the template. CLI `python -m indicators.pages`. For structural series it also writes `<series_id>_trend.csv` (date, value, trend, deviation, segment) into `site/data/`.

Page requirements:
- **Indicator page** order (spec Sec. 6): headline (reading state badge "Not yet reviewed", attribution badge with the four criteria in a details block, last fetched / data through, "stale since" badge if `staleness` is not None or health is failed, G2 `headline_caveat`), takeaway, "Why this matters", interactive chart, reading history ("No reviewed readings yet — readings begin in Stage 3"), shows / doesn't show box, what would change our reading, method (comparison type, pre-AI window 2010–2019 for structural series, sources with license, series breaks, caveats), CSV download link(s), link to Archive.
- **Chart (`charts.js`, Observable Plot):** timeframe selector with options `All`, `Since 2010`, `Since 2019`, `Since 2022 Q4`; for structural series a view toggle `Level` / `Deviation from 2010–19 trend` (trend shown as a dashed line in Level view); lines drawn per `segment` with a vertical annotated rule at each break; series selector when an indicator has several series; chart title from `chart_title` when set; theme-aware colors; responsive width.
- **Summary (`index.qmd`):** 3×3 grid (rows exposure/erosion/lock-in × economic/government/cultural); each indicator appears in its cell with name, "Not yet reviewed", latest value with units, and attribution badge; empty cells say "No public measure yet"; a note explaining the two scales; a "what the data is telling us" box reading "Readings begin after thresholds are reviewed and frozen (Stage 2–3)"; counter-evidence panel from published curated items; link to the Archive.
- **Methodology:** layers, the two scales, comparison types, the attribution rubric (spec 4.2 text), the staged release, the review procedures summary, critiques taken seriously (Krueger, Millidge, Jedlicka, the authors' own caveats), planned later versions (spec Sec. 8 headings).
- **Archive:** "No snapshots yet; the first retrospective snapshot will appear here in Stage 3."
- **About:** purpose, author (Jeremy Richardson, Ph.D.), how to cite, how to report errors (GitHub issues link).
- `_quarto.yml`: website project, navbar (Summary, Indicators menu of eight, Methodology, Archive, About), `site-url` set to the base path, light + dark themes, `output-dir: _site`.

- [ ] **Step 1: Tests (`tests/test_pages.py`):** `test_build_writes_eight_indicator_pages`, `test_g2_page_contains_caveat_in_headline_and_civilian_title`, `test_stale_badge_rendered_when_stale` (meta with old `data_through`), `test_all_pages_show_not_yet_reviewed`, `test_trend_csv_written_for_structural_series_only`, `test_unverified_curated_items_absent_from_index`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** `python -m indicators.pages && quarto render site` → completes with no errors; `quarto preview site` and check by eye at desktop and phone width, in light and dark mode: every page, every chart control, every CSV link.
- [ ] **Step 6:** Commit `feat: Quarto site, page generator and charts`.

---

### Task 12: CI, scheduled refresh and GitHub Pages deploy

**Files:**
- Create: `.github/workflows/ci.yml`, `.github/workflows/refresh-deploy.yml`, `scripts/link_check.py`, `tests/test_link_check.py`

**Interfaces:**
- Consumes: `python -m indicators.refresh`, `python -m indicators.pages`, `quarto render site`.
- Produces: `link_check.check(site_dir: Path, base_path: str = "/disempowerment-indicators/") -> list[str]` — returns broken internal links and missing files (HTML `href`/`src` and CSV links), resolved as they would be under the base path.

- [ ] **Step 1: Tests:** `test_link_check_flags_missing_csv`, `test_link_check_accepts_relative_links_under_base_path`.
- [ ] **Step 2:** FAIL → implement → PASS.
- [ ] **Step 3:** `ci.yml`: on push and pull request — set up Python 3.12, install, `pytest` (offline only).
- [ ] **Step 4:** `refresh-deploy.yml`: on `schedule` (weekly, Mondays 12:00 UTC), `workflow_dispatch`, and push to `main`. Jobs: (1) refresh — run `python -m indicators.refresh` with `continue-on-error` captured; commit changed `data/` as `github-actions[bot]` with message `data: weekly refresh <date>`; if any source failed, open a GitHub issue titled `Data source failing: <source>` unless an open issue with that exact title exists (use `gh issue list --search` + `gh issue create`). (2) build — `pytest`, `python -m indicators.pages`, set up Quarto ≥1.11, `quarto render site`, `python scripts/link_check.py site/_site` (fails the job on any broken link). (3) deploy — `actions/upload-pages-artifact` + `actions/deploy-pages`. Permissions: `contents: write`, `pages: write`, `id-token: write`, `issues: write`.
- [ ] **Step 5:** **Ask the owner before** enabling GitHub Pages with the "GitHub Actions" source (`gh api -X POST repos/richardsonlj12/disempowerment-indicators/pages -f build_type=workflow`), since that makes the site publicly reachable. Do not deploy until Task 13 is complete.
- [ ] **Step 6:** Commit `ci: tests, weekly refresh and Pages deploy`.

---

### Task 13: Review procedures and Stage 1 release gate

**Files:**
- Create: `REVIEW.md`; finalize `review/figure-verification.md`

**Interfaces:**
- Produces: `REVIEW.md` with the spec 7b checklists — automated checks (what CI enforces), human gates (figure verification, indicator page review, threshold freeze, readings review), independent second check, corrections policy — each as a checkbox list with who does it and when.

- [ ] **Step 1:** Write `REVIEW.md` from spec Sec. 7b.
- [ ] **Step 2:** Confirm every figure that appears in site prose, the curated files or the counter-evidence panel has a row in `review/figure-verification.md`: figure, page, primary-source URL, date checked, checked by.
- [ ] **Step 3: Independent second check:** dispatch a fresh reviewer with no conversation context to read the rendered site (`site/_site`), `content/`, `config/` and `src/`, acting as a skeptical AI-safety researcher; ask for errors, overclaims, one-sided framing, attribution claims beyond the evidence, and broken behavior. Save its findings to `review/stage1-independent-review.md`.
- [ ] **Step 4: Owner gate:** the owner triages the findings; fixes are made; the owner gives explicit go-ahead to publish.
- [ ] **Step 5:** Enable Pages (Task 12 Step 5), push `main`, run the workflow, and confirm the live site at `https://richardsonlj12.github.io/disempowerment-indicators/` serves every page and CSV.
- [ ] **Step 6:** Commit `docs: review procedures and Stage 1 verification log`; tag `v0.1.0-stage1`.
