# Release 1, Stage 1 — Data Site Implementation Plan

> **Note (2026-11-18): indicator codes were renumbered after this plan was written.** Old to new: E2 to EA1, E3 to EA2, E1 to ED1, G1 to GD1, C1 to CD1 (Release 2: E4 to EL1, G2 to GA1, G3 to GL1, C2 to CD2). This plan keeps the old codes as history.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the Release 1 data site: five indicator pages (E1, E2, E3, G1, C1) with live public data, interactive charts, explanatory text and caveats; a summary grid in which every reading shows "Not yet reviewed"; the oversight row; the counter-evidence panel; and methodology, archive and about pages — refreshed weekly by GitHub Actions and deployed to GitHub Pages.

**Architecture:** A Python package (`src/indicators/`) fetches each public source, validates it, and writes tidy CSV plus a metadata JSON per series into `data/`. A `config/` folder holds the indicator registry, the readings file and hand-curated items. A page generator turns the registry plus owner-editable prose into Quarto pages; Quarto's built-in Observable JS renders the charts. The Python side never imports anything from the site, and the site only reads files from `data/` and `config/`.

**Tech Stack:** Python ≥3.12 (local 3.14), pandas, requests, PyYAML, pytest, responses; Quarto ≥1.11 with Observable JS (Observable Plot + Inputs); GitHub Actions; GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-11-09-disempowerment-indicators-design.md` (Revision 2, approved 2026-11-17). **Out of scope here:** the threshold rule, sensitivity tables, proposed readings, the retrospective and review-pending issues (Stages 2–3), and all Release 2 indicators (E4, G2, G3, C2).

## Global Constraints

- $0: free tools and free data only.
- **No API keys in Stage 1.** Use keyless endpoints (FRED `fredgraph.csv`, Stack Exchange anonymous quota, Wikimedia with User-Agent, Hugging Face public files). If a source truly needs a key, stop and ask the owner; keys go only in GitHub Actions Secrets.
- HTTP User-Agent for every request: `keel-indicators/0.1 (+https://github.com/richardsonlj12/keel)`. Never put the owner's email in requests.
- Avoided sources: OpenSecrets API, EIU, Gallup microdata, ADP, Lightcast, S&P.
- Nothing from `../research/` (the private folder beside the repo) is copied into the repo. Figures are re-verified from primary sources and cited by primary URL. Secondary-only figures are never published.
- Stage 1 readings: every indicator shows **"Not yet reviewed"**. No script produces a reading.
- Scales: exposure scale `low | rising | pervasive` for E2, E3; baseline scale `within | above | below | far_above | far_below` for E1, G1, C1; both also allow `no_signal` and `not_yet_reviewed`. Display labels: "Low", "Rising", "Pervasive", "Within baseline", "Above baseline", "Below baseline", "Far above baseline", "Far below baseline", "No signal / insufficient data", "Not yet reviewed".
- Badge name is **"AI-specificity"** (`strong | moderate | weak`), never "attribution".
- Pre-AI baseline period for structural series: **2010-01-01 to 2019-12-31**. Retrospective start (mentioned on pages only): **2022Q4**.
- Lock-in row shows "No public measure yet" in Release 1. The oversight row shows "No public measure yet" with its citation.
- In Markdown prose (pages, docs), write placeholders as `[date]`, never in angle brackets, and avoid paired `~`.
- Site base path: `https://richardsonlj12.github.io/keel/`. All links and data URLs relative.
- Accessible, readable in light and dark mode, usable at phone width.
- Every commit ends with: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Review Focus

1. **A source answers 200 OK with an HTML error page or a changed schema.** Expected: validation rejects it, the last good data stays in place, the series is marked stale, nothing invalid is written. → `test_refresh_keeps_last_good_on_invalid_payload` (Task 8).
2. **One source fails during a scheduled refresh.** Expected: the other sources still update and deploy; the failing series keeps its old data with a "stale since [date]" badge, and a GitHub issue opens (deduplicated by title). → `test_refresh_isolates_source_failure` (Task 8); issue step in Task 11.
3. **Series breaks and schema changes** (BTOS question change 2025-11-17; Wikimedia bot reclassification; Economic Index release schemas). Expected: no line drawn across a break, each break annotated, Economic Index releases harmonized with each mapping documented. → `test_series_break_splits_segments` (Task 2), `test_aei_release_schema_mapping` (Task 6).
4. **Rate limit hit partway through** (Stack Exchange anonymous quota of 300 requests a day across about 1 + N sites). Expected: partial results are not saved as complete; already-complete months are cached and the next run resumes. → `test_stackexchange_partial_quota_not_written` (Task 7).
5. **Base path on GitHub Pages.** Expected: CSV downloads and inter-page links work under `/keel/`. → link check in the deploy workflow (Task 11).

---

## File Structure

```
disempowerment-indicators/
  pyproject.toml  .gitignore  README.md  REVIEW.md
  review/figure-verification.md       # each published figure → primary source, date checked
  review/source-reading-notes.md      # notes from reading Chooi et al., RAND, Herdağdelen et al., Imas
  config/
    indicators.yaml                   # registry: Release 1 indicators + grid layout
    readings.yaml                     # dated readings (Stage 1: all not_yet_reviewed)
    c1_comparison_sites.yaml          # comparison-site criteria and list (owner-approved before fetch)
    curated/counter_evidence.yaml     # counter-evidence panel items + inclusion criteria
    curated/oversight.yaml            # oversight-row citation(s)
  content/indicators/[ID].md          # owner-editable prose per indicator
  content/methodology.md              # owner-reviewed methodology prose
  src/indicators/
    __init__.py  http.py  store.py  registry.py  trend.py  curated.py  refresh.py  pages.py
    sources/fred.py                   # E1 labor share, profit share; G1 US tax share
    sources/btos.py                   # E2 firm AI adoption (with standard errors)
    sources/aei.py                    # E3 Anthropic Economic Index
    sources/oecd.py                   # G1 OECD revenue structure
    sources/stackexchange.py          # C1 Stack Overflow + comparison sites
    sources/wikimedia.py              # C1 Wikipedia
  data/                               # generated: [series_id].csv, [series_id].meta.json, _health.json
  site/
    _quarto.yml  index.qmd  methodology.qmd  archive.qmd  about.qmd
    _indicator_template.qmd           # rendered by pages.py into indicators/[ID].qmd
    js/charts.js  styles.scss
  scripts/link_check.py
  tests/fixtures/...  tests/test_*.py
  .github/workflows/ci.yml  .github/workflows/refresh-deploy.yml
```

---

### Task 1: Project skeleton and local tooling

**Files:** Create `pyproject.toml`, `.gitignore`, `README.md`, `src/indicators/__init__.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: installable package `indicators` (`pip install -e ".[dev]"`); pytest marker `live` for network tests, excluded by default.

- [ ] **Step 1:** Create `.venv` with python3; record setup commands in README ("Setup").
- [ ] **Step 2:** `pyproject.toml`: name `disempowerment-indicators`, `requires-python = ">=3.12"`, deps `pandas`, `requests`, `pyyaml`; dev extra `pytest`, `responses`; pytest `markers = ["live: hits the network"]`, `addopts = "-m 'not live'"`; src layout.
- [ ] **Step 3:** `.gitignore`: `.venv/`, `__pycache__/`, `site/_site/`, `site/.quarto/`, `site/data/`, `site/config/`, `site/indicators/`, `.DS_Store`.
- [ ] **Step 4:** `test_package_imports`; run `pytest -v` → PASS.
- [ ] **Step 5:** Install Quarto ≥1.11 without admin rights: macOS tarball from the official GitHub release into `~/.local/opt/quarto`, symlink `quarto` into `~/.local/bin`; verify `quarto --version`. Document in README ("Preview the site").
- [ ] **Step 6:** Commit `chore: project skeleton`.

---

### Task 2: Series store and metadata contract

**Files:** Create `src/indicators/store.py`, `tests/test_store.py`

**Interfaces:**
- Produces:
  - `SeriesMeta` dataclass: `series_id`, `indicator_id`, `title`, `units`, `frequency` (`weekly|biweekly|monthly|quarterly|annual|irregular`), `source_name`, `source_url`, `license`, `fetched_at` (ISO UTC), `data_through` (ISO date), `max_lag_days: int`, `breaks: list[dict]` (`{"date": "YYYY-MM-DD", "note": str}`), `notes: str = ""`, `role: str = "primary"` (`primary|context|comparison`).
  - `validate_frame(df) -> None`: requires `date` (datetime, unique, ascending) and `value` (float, no NaN); optional `segment` (int), `se` (float ≥ 0, NaN allowed), `group` (str). With `group` present, `date` must be unique within each group. Raises `ValueError` with a specific message.
  - `assign_segments(df, breaks) -> pd.DataFrame`: adds `segment`, incrementing at each break date.
  - `write_series(df, meta, data_dir: Path) -> None`: validates, then writes `[series_id].csv` and `[series_id].meta.json` atomically (temp file + rename).
  - `read_series(series_id, data_dir) -> tuple[pd.DataFrame, SeriesMeta]`.
  - `staleness(meta, today: date) -> int | None`: days past `data_through + max_lag_days`, else `None`.

- [ ] **Step 1: Tests:** `test_write_read_roundtrip`; `test_validate_rejects_duplicate_dates`; `test_validate_allows_same_date_in_different_groups`; `test_validate_rejects_nan_value`; `test_validate_rejects_negative_se`; `test_validate_rejects_unsorted`; `test_series_break_splits_segments` (break `2025-11-17` → before `segment == 0`, on/after `1`); `test_staleness` (`data_through=2026-06-30`, `max_lag_days=120`: today `2026-11-12` → `15`, today `2026-10-01` → `None`); `test_write_is_atomic_on_invalid`.
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat: series store and metadata contract`.

---

### Task 3: Indicator registry, grid layout and readings file

**Files:** Create `config/indicators.yaml`, `config/readings.yaml`, `src/indicators/registry.py`, `tests/test_registry.py`

**Interfaces:**
- Produces:
  - `Indicator` dataclass: `id`, `release: int`, `domain` (`economic|government|cultural`), `layer` (`exposure|erosion|lockin`), `scale` (`exposure|baseline`), `name`, `takeaway`, `specificity` (`strong|moderate|weak`), `specificity_criteria: dict` (keys `directness`, `comparison_group`, `timing`, `confounders`; one line each), `timing` (`leading|lagging`), `direction_assumption: str`, `rival_reading: str`, `comparison` (`structural|ai_native`), `tier: int`, `series: list[str]`, `primary_series: str | None`, `chart_title: str | None`, `headline_caveat: str | None`, `disclosure: str | None`, `sources: list[dict]` (`name`, `url`, `license`).
  - `GridCell`: `layer`, `domain`, `indicator_ids: list[str]`, `empty_label: str` — from `grid:` in the same YAML; plus `oversight: {label, citation_ref}`.
  - `load_registry(path) -> tuple[list[Indicator], list[GridCell], dict]`; `load_readings(path) -> dict[str, list[Reading]]`.
  - `Reading` dataclass: `indicator_id`, `state` (`not_yet_reviewed|no_signal|low|rising|pervasive|within|above|below|far_above|far_below`), `date`, `magnitude: str | None`, `interpretation: str | None`, `rationale: str | None`, `kind` (`current|retrospective`).
  - `current_reading(readings, indicator_id) -> Reading`: latest `current`, else a `not_yet_reviewed` Reading.
  - `STATE_LABELS: dict[str, str]`: display labels from Global Constraints.
- Registry content (spec Sec. 5): E1 (erosion, baseline, weak, lagging, structural, tier 1; series `labor_share_nfb` primary, `profit_share` context); E2 (exposure, exposure, strong, leading, ai_native, tier 1; `btos_ai_use`); E3 (exposure, exposure, strong, leading, ai_native, tier 2; `aei_automation_share` primary, `aei_augmentation_share`; `headline_caveat` "One vendor, one product: Claude usage only"; `disclosure` stating the data is published by Anthropic and the site is built with assistance from Claude); G1 (erosion, baseline, weak, lagging, structural, tier 1; `us_labor_tax_share` primary, `oecd_labor_tax_share_usa` and `oecd_labor_tax_share_avg` context); C1 (erosion, baseline, moderate, leading, structural, tier 1; `so_questions_monthly`, `se_comparison_questions_monthly` (grouped by site), `so_vs_comparison_yoy` primary, `wiki_user_pageviews_en` and `wiki_active_editors_en` context). Direction assumptions and rival readings from spec Sec. 4.6 and 5 notes; specificity criteria drafted, marked `# DRAFT — owner review in Stage 2`.
- Grid: lock-in cells empty with "No public measure yet"; cultural exposure empty with "No public measure yet".
- `readings.yaml`: one `not_yet_reviewed` entry per indicator.

- [ ] **Step 1: Tests:** `test_release1_ids` (`{"E1","E2","E3","G1","C1"}`, all `release == 1`); `test_exposure_layer_uses_exposure_scale` (`layer == "exposure"` ⇔ `scale == "exposure"`); `test_reading_state_matches_scale` (state `below` for E2 raises `ValueError`; `rising` for E1 raises); `test_all_readings_not_yet_reviewed`; `test_every_indicator_has_direction_and_rival_reading`; `test_e3_has_caveat_and_disclosure`; `test_lockin_row_empty_in_release1`; `test_series_ids_unique`; `test_state_labels_cover_all_states`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat: indicator registry, grid and readings file`.

---

### Task 4: HTTP helper and comparison calculations

**Files:** Create `src/indicators/http.py`, `src/indicators/trend.py`, `tests/test_http.py`, `tests/test_trend.py`

**Interfaces:**
- Produces:
  - `get(url, params=None, expect="any", timeout=60) -> requests.Response`: Global Constraints User-Agent; retries 3× with backoff on 429/5xx (honor `Retry-After`); raises `SourceError` when `expect` is `"csv"` or `"json"` and the body starts like HTML (`<html` or `<!doctype` in the first 512 bytes, case-insensitive).
  - `class SourceError(Exception)`.
  - `pre_ai_trend(df, start="2010-01-01", end="2019-12-31") -> pd.DataFrame`: adds `trend` (OLS line on the window, extended over all dates) and `deviation`. **Chart view only**; it is not the threshold rule.
  - `yoy_change(df, periods_per_year: int) -> pd.Series`: change versus the same period a year earlier.
  - `relative_yoy(treated: pd.DataFrame, comparison: pd.DataFrame, periods_per_year: int) -> pd.DataFrame`: per date, treated YoY % change minus the mean comparison YoY % change (a difference-in-differences contrast); columns `date`, `value`.

- [ ] **Step 1: Tests:** `test_get_sets_user_agent`; `test_get_rejects_html_when_csv_expected`; `test_get_retries_on_429`; `test_pre_ai_trend_exact_on_linear_series` (value = 2t + 1 → deviation 0); `test_yoy_change_monthly` (Jan 2024 = 100, Jan 2025 = 80 → −20); `test_relative_yoy` (treated −30%, comparison mean −10% → −20).
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat: http helper and comparison calculations`.

---

### Task 5: FRED and OECD sources — E1 and G1

**Files:** Create `src/indicators/sources/fred.py`, `src/indicators/sources/oecd.py`, fixtures, `tests/test_sources_e1_g1.py`

**Interfaces:**
- Consumes: `http.get`, `store.SeriesMeta`.
- Produces: every source module exposes `fetch() -> list[tuple[pd.DataFrame, SeriesMeta]]` (shared by Tasks 5–7). `fred.fetch()` → `labor_share_nfb`, `profit_share`, `us_labor_tax_share`. `oecd.fetch()` → `oecd_labor_tax_share_usa`, `oecd_labor_tax_share_avg`.

- [ ] **Step 1: Verify series and record them in `review/figure-verification.md`:**
  - Labor share in **percent**, not an index. Prefer FRED `fredgraph.csv?id=[ID]`; if FRED has only an index, use the BLS published labor-share level. 2026Q2 must equal **52.8**.
  - Profit share: corporate profits after tax (with IVA and CCAdj) ÷ GDP, FRED, percent.
  - US labor-based tax share: (personal current taxes + contributions for government social insurance) ÷ (total government current tax receipts + contributions for government social insurance), BEA NIPA via FRED, quarterly, percent; formula and series IDs in meta `notes`.
  - OECD Revenue Statistics via the SDMX endpoint: (PIT 1100 + SSC 2000) ÷ total tax revenue, USA and OECD average, annual.
- [ ] **Step 2: Tests:** offline `test_labor_share_parses_percent`, `test_tax_share_formula` (hand-computed ratio from fixture rows), `test_oecd_labor_share_formula`, `test_meta_fields_complete`; live `test_live_labor_share_2026q2_is_52_8` (±0.05), `test_live_oecd_avg_2023` ((PIT + SSC) share for the OECD average in 2023 = 49.2 ± 0.3).
- [ ] **Step 3:** FAIL → **Step 4:** implement → **Step 5:** offline and live PASS.
- [ ] **Step 6:** Commit `feat: FRED and OECD sources (E1, G1)`.

---

### Task 6: Adoption sources — E2 and E3

**Files:** Create `src/indicators/sources/btos.py`, `src/indicators/sources/aei.py`, fixtures, `tests/test_sources_e2_e3.py`

**Interfaces:**
- Produces: `btos.fetch()` → `btos_ai_use` (percent of US firms reporting AI use, national, biweekly, firm-weighted, with `se` where Census publishes standard errors), `breaks=[{"date": "2025-11-17", "note": "Question changed from AI use 'in producing goods or services' to 'in any business function'"}]`. `aei.fetch()` → `aei_automation_share`, `aei_augmentation_share` (percent of classified Claude conversations, one row per release date, and per month where a release provides monthly aggregates), `frequency="irregular"`.
- `aei.RELEASE_SCHEMAS: dict[str, dict]`: per release, the file path in the Hugging Face dataset and the field mapping to automation / augmentation. Each mapping is listed in meta `notes`, and every schema change becomes a `breaks` entry.

- [ ] **Step 1:** Locate the BTOS national time-series download for the AI-use question, including standard errors; record URL and question text per period in meta `notes`. List the Anthropic Economic Index releases on Hugging Face (`Anthropic/EconomicIndex`), read each README section that defines the automation/augmentation split, and record the mapping and license (CC-BY data per README) in `figure-verification.md`.
- [ ] **Step 2: Tests:** `test_btos_break_assigned`; `test_btos_value_is_percent`; `test_btos_se_nonnegative_when_present`; `test_aei_release_schema_mapping` (each fixture release maps to both shares; unknown schema raises `SourceError` rather than guessing); `test_aei_shares_bounded` (each between 0 and 100; automation + augmentation ≤ 100); live `test_live_btos_may_2026_near_19_8` (a May 2026 period within 19.3–20.3).
- [ ] **Step 3:** FAIL → **Step 4:** implement → **Step 5:** PASS.
- [ ] **Step 6:** Commit `feat: BTOS and Economic Index sources (E2, E3)`.

---

### Task 7: Knowledge-commons sources — C1

**Files:** Create `config/c1_comparison_sites.yaml`, `src/indicators/sources/stackexchange.py`, `src/indicators/sources/wikimedia.py`, fixtures, `tests/test_sources_c1.py`

**Interfaces:**
- `c1_comparison_sites.yaml`: `criteria: str`, `approved_by_owner: bool`, `approved_on: date | null`, `sites: [{api_site_name, reason}]`.
- Produces: `stackexchange.fetch()` → `so_questions_monthly`; `se_comparison_questions_monthly` (one row per site per month, `group` = site); `so_vs_comparison_yoy` (from `trend.relative_yoy`, monthly). `wikimedia.fetch()` → `wiki_user_pageviews_en` (monthly, `agent=user`, 2015-07 onward), `wiki_active_editors_en` (monthly), with the bot-reclassification break cited from Wikimedia's announcement.

- [ ] **Step 1: Owner gate, before any comparison-site data is fetched:** draft the selection criteria (e.g., launched before 2015, at least N questions a month in 2019, subject less likely to be answered by a coding assistant) and a 4–6 site list that meets them; the owner approves; set `approved_by_owner: true` and the date; commit `config: C1 comparison sites (owner-approved)`.
- [ ] **Step 2: Tests:** `test_so_month_bounds` (from/to cover exactly one calendar month, UTC); `test_comparison_requires_owner_approval` (`fetch` raises if `approved_by_owner` is false); `test_stackexchange_partial_quota_not_written` (mock returns `quota_remaining: 0` partway; `fetch` raises `SourceError`; complete months stay cached in `data/_cache/stackexchange/`; the current month is never cached); `test_relative_yoy_written`; `test_wikimedia_user_agent_set`; `test_wikimedia_break_assigned`.
- [ ] **Step 3:** FAIL → **Step 4:** implement (refetch only the last two months plus uncached months) → **Step 5:** PASS; live smoke `pytest -m live tests/test_sources_c1.py`.
- [ ] **Step 6:** Commit `feat: Stack Exchange and Wikimedia sources (C1)`.

---

### Task 8: Curated items and the refresh runner

**Files:** Create `src/indicators/curated.py`, `config/curated/counter_evidence.yaml`, `config/curated/oversight.yaml`, `src/indicators/refresh.py`, `tests/test_curated.py`, `tests/test_refresh.py`

**Interfaces:**
- Curated item schema: `{id, label, domain, metric, value, unit, date, source_name, source_url, verified: bool, verified_on: date | null, note}`. `counter_evidence.yaml` also has top-level `inclusion_criteria: str` (written before items are added) and per-item `kind: policy | welfare | data_signal`.
- `load_curated(path) -> tuple[dict, list[dict]]` (header, items) — validates schema; `published(items)` returns only `verified: true` items.
- `refresh.run(data_dir, sources=None, today=None) -> dict`: calls each source's `fetch()` independently; on exception or validation error keeps existing files and records `{"status": "failed", "error": str, "since": first failure date}`; on success writes and records `{"status": "ok", "data_through": ...}`. Writes `data/_health.json`. CLI `python -m indicators.refresh` exits 1 if any source failed, after writing everything else.
- Content: `inclusion_criteria` from spec Sec. 4.6 (primary sources, dated, welfare-improving signals as well as policy pushback); items such as the rising OECD labor-tax share and AI legislation counts (Stanford AI Index, CSET AGORA, OECD.AI); `oversight.yaml` with the Herdağdelen, Joren & Tamkin (2026) citation and figures taken from the full paper. Each item is entered only after checking its primary source and logged in `figure-verification.md`; anything unverifiable stays `verified: false`.

- [ ] **Step 1: Tests:** `test_curated_requires_source_url`; `test_unverified_items_not_published`; `test_counter_evidence_has_inclusion_criteria`; `test_counter_evidence_includes_welfare_kind` (the file contains at least one item with `kind: welfare`; whether it is published depends on verification); `test_refresh_isolates_source_failure`; `test_refresh_keeps_last_good_on_invalid_payload`; `test_failure_since_date_persists`.
- [ ] **Step 2:** FAIL → **Step 3:** implement and fill curated YAML → **Step 4:** PASS.
- [ ] **Step 5:** Run `python -m indicators.refresh` for real; commit code and resulting `data/`: `feat: curated items and refresh runner`.

---

### Task 9: Source reading and page prose

**Files:** Create `review/source-reading-notes.md`, `content/indicators/E1.md`, `E2.md`, `E3.md`, `G1.md`, `C1.md`, `content/methodology.md`

**Interfaces:**
- Produces: each indicator file has front matter `takeaway:` and exactly these level-2 headings, which `pages.py` splits on: `## Why this matters for gradual disempowerment`, `## What it shows`, `## What it doesn't show`, `## What would change our reading`, `## Caveats`. **Superseded by Batch B (2026-11-17):** front matter is now `summary:`, `warning_sign:`, `data_sources:` (list of `name`, `url`), `calculation:`, `coverage:`; level-2 headings are `## Why this matters for gradual disempowerment`, `## What it shows`, `## What it doesn't show`, `## What would change our reading` (sub-headings `### Warning sign`, `### Alternative explanations`, optional `### What would raise or lower our confidence`), `## Data and calculation`, `## Caveats`. `content/methodology.md` is free-form prose included in `methodology.qmd`.

- [ ] **Step 1: Source reading (spec 7b gate):** read in full and summarize in `review/source-reading-notes.md`: Chooi, Lee & Li (2026); Moon & Boudreaux (2026, RAND); Herdağdelen, Joren & Tamkin (2026); Imas (2026). Note where the site's layers depart from Chooi et al. Anything that can't be retrieved from the original is listed as unread and not relied on.
- [ ] **Step 2: Indicator prose**, plain language with precise terms:
  - Every page: direction assumption and main rival reading in "What would change our reading"; "conditions under which the hypothesized mechanism would operate", not proof.
  - E1, E2, E3: the welfare-vs-influence note. E2, E3: AI-specificity "strong" means it measures AI directly, not that it shows disempowerment.
  - E2: augmentation-vs-displacement note; firm-weighted vs. employment-weighted; the 2025-11-17 break; the "don't know" share.
  - E3: one vendor, one product; product changes as a rival explanation; irregular releases; no pre-AI baseline; the disclosure.
  - G1: states plainly that it currently points away from disempowerment; the rentier co-optation rival reading.
  - C1: the decline began around 2020; the comparison-site design and its limit (AI affects those sites too); the Wikimedia break; AI intermediation as the Wikipedia rival reading.
- [ ] **Step 3: Methodology prose:** layers as our adaptation of Chooi et al.; lock-in row empty and why; oversight row; the two scales and the three-line reading; AI-specificity rubric; comparisons, uncertainty and seasonality; threshold rule and retrospective "coming in Stages 2–3"; critiques (Krueger, Millidge, Jedlicka, the authors' caveats); "diagnostics, not targets"; the named cultural gap; planned later versions (spec Sec. 8 headings).
- [ ] **Step 4:** Every number traced to a primary source and logged in `figure-verification.md`; remove any that can't be.
- [ ] **Step 5: Owner gate:** the owner reviews and approves all prose files.
- [ ] **Step 6:** Commit `docs: indicator and methodology prose (owner-reviewed)`.

---

### Task 9b: Name the project (owner decision)

*(Added 2026-11-17 at the owner's request.)* "The site" is ambiguous in the prose (it can be read as one of the data sources' websites). Before Task 10:

- [ ] **Step 1:** Brainstorm candidate names with the owner, preferably with a memorable acronym; check each for clashes with existing projects and organizations and for domain/repository-name availability.
- [ ] **Step 2: Owner decision** on the name (and whether the repository name changes).
- [ ] **Step 3:** Replace "the site"/"this site" references to the project in content/, the design doc and config display text with the name (keep "website" where it means the web pages generically); use it in the Task 10 site title, navbar and About page.

---

### Task 10: Quarto site, page generator and charts

**Files:** Create `src/indicators/pages.py`, `site/_quarto.yml`, `site/index.qmd`, `site/methodology.qmd`, `site/archive.qmd`, `site/about.qmd`, `site/_indicator_template.qmd`, `site/js/charts.js`, `site/styles.scss`, `tests/test_pages.py`

**Interfaces:**
- Consumes: registry, readings, `current_reading`, `STATE_LABELS`, `read_series`, `staleness`, curated loaders, `pre_ai_trend`, content files.
- Produces: `pages.build(repo_root: Path) -> None` copies `data/` → `site/data/` and needed `config/` files → `site/config/`, writes `site/indicators/[ID].qmd` per Release 1 indicator, and writes `[series_id]_trend.csv` (date, value, trend, deviation, segment) for structural primary series. CLI `python -m indicators.pages`.

Page requirements:
- **Indicator page** (spec Sec. 6): headline in the three-line reading form — state label ("Not yet reviewed"), magnitude line naming the baseline (latest value with units and baseline description), interpretive line with the AI-specificity badge — plus leading/lagging label, last fetched / data through, "stale since [date]" if stale, `headline_caveat` and `disclosure` where set; takeaway; why this matters; chart; reading history ("No reviewed readings yet — readings begin in Stage 3"); shows / doesn't show; what would change our reading; method (comparison type, baseline, AI-specificity scores on the four criteria, sources with license, series breaks, caveats, "Threshold rule and sensitivity table: Stage 2"); CSV links; Archive link.
- **Charts (`charts.js`, Observable Plot):** timeframe selector `All`, `Since 2010`, `Since 2019`, `Since 2022 Q4`; structural series: view toggle `Level` / `Deviation from 2010–19 trend`; C1: views `Stack Overflow vs. comparison sites (YoY)`, `Monthly questions`, `Wikipedia`; lines per `segment` with an annotated rule at each break; `se` drawn as a band where present; series selector for multi-series indicators; theme-aware colors; responsive width.
- **Summary (`index.qmd`):** grid from `GridCell`s (exposure / erosion / lock-in × economic / government / cultural) with each indicator's name, "Not yet reviewed", latest value with units, AI-specificity badge; empty cells say "No public measure yet"; the oversight row spanning all columns with its citation; a note explaining the two scales; a "what the data is telling us" box: "Readings begin after the threshold rule is reviewed and frozen (Stages 2–3)"; counter-evidence panel from published items with its inclusion criteria; Archive link.
- **Methodology:** `content/methodology.md`. **Archive:** "No snapshots yet; the first retrospective snapshot will appear here in Stage 3." **About:** purpose, author (Jeremy Richardson, Ph.D.), how to cite, how to report errors (GitHub issues link), disclosure that the site is built with assistance from Claude (Anthropic).
- `_quarto.yml`: website project; navbar (Summary, Indicators menu of five, Methodology, Archive, About); `site-url` set to the base path; light and dark themes; `output-dir: _site`.

- [ ] **Step 1: Tests:** `test_build_writes_release1_pages_only` (exactly E1, E2, E3, G1, C1); `test_reading_rendered_in_three_lines`; `test_e3_page_has_caveat_and_disclosure`; `test_stale_badge_rendered_when_stale`; `test_all_pages_show_not_yet_reviewed`; `test_trend_csv_for_structural_only`; `test_index_lockin_row_says_no_public_measure`; `test_index_has_oversight_row_with_citation`; `test_unverified_curated_items_absent`; `test_about_has_claude_disclosure`; `test_no_angle_bracket_placeholders_in_generated_qmd`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** `python -m indicators.pages && quarto render site` completes without errors; `quarto preview site` and check by eye at desktop and phone width, light and dark: every page, chart control and CSV link.
- [ ] **Step 6:** Commit `feat: Quarto site, page generator and charts`.

---

### Task 10b: Owner revises the page summary tables (owner gate)

*(Added 2026-11-17 at the owner's request.)* Once Task 10 renders the pages locally, the owner revises the text of each indicator page's top summary table (summary, warning sign, data sources, calculation, coverage) before anything is published.

- [ ] **Step 1:** Render the site locally (`quarto preview site`) and give the owner the list of pages to review.
- [ ] **Step 2: Owner gate:** the owner edits the front-matter fields in content/indicators/[ID].md (or comments in ALL CAPS for Claude to apply).
- [ ] **Step 3:** Apply comments; re-run the page tests and the figure check for any new numbers; commit `docs: owner revisions to page summary tables`.

*(Added 2026-11-18.)* The summary page no longer carries a "What the data are telling us" box in Stage 1; in Stage 3 it gets back a dated "What the data are telling us" statement once readings exist.

---

### Task 11: CI, scheduled refresh and GitHub Pages deploy

**Files:** Create `.github/workflows/ci.yml`, `.github/workflows/refresh-deploy.yml`, `scripts/link_check.py`, `tests/test_link_check.py`

**Interfaces:**
- Produces: `link_check.check(site_dir: Path, base_path: str = "/keel/") -> list[str]` — broken internal links and missing files (HTML `href`/`src`, CSV links), resolved as under the base path.

- [ ] **Step 1: Tests:** `test_link_check_flags_missing_csv`; `test_link_check_accepts_relative_links_under_base_path`. FAIL → implement → PASS.
- [ ] **Step 2:** `ci.yml`: on push and pull request — Python 3.12, install, `pytest` (offline).
- [ ] **Step 3:** `refresh-deploy.yml`: on `schedule` (weekly, Mondays 12:00 UTC), `workflow_dispatch`, and push to `main`. Jobs: (1) refresh — `python -m indicators.refresh`, capture failure without stopping; commit changed `data/` as `github-actions[bot]` with `data: weekly refresh [date]`; for each failed source, open an issue titled `Data source failing: [source]` unless an open issue with that title exists (`gh issue list --search` then `gh issue create`). (2) build — `pytest`, `python -m indicators.pages`, Quarto ≥1.11, `quarto render site`, `python scripts/link_check.py site/_site` (fails on any broken link). (3) deploy — `actions/upload-pages-artifact`, `actions/deploy-pages`. Permissions: `contents: write`, `pages: write`, `id-token: write`, `issues: write`.
- [ ] **Step 4:** **Ask the owner before** enabling GitHub Pages with the Actions source (`gh api -X POST repos/richardsonlj12/keel/pages -f build_type=workflow`); it makes the site public. Do not deploy until Task 12 is complete.
- [ ] **Step 5:** Commit `ci: tests, weekly refresh and Pages deploy`.

---

### Task 12: Review procedures and Release 1 Stage 1 gate

**Files:** Create `REVIEW.md`; finalize `review/figure-verification.md`

**Interfaces:**
- Produces: `REVIEW.md` with spec Sec. 7b as checklists — automated checks (what CI enforces), human gates (source reading, figure verification, indicator page review, threshold-rule freeze, readings review), independent second check, corrections policy — each with who and when.

- [ ] **Step 1:** Write `REVIEW.md`.
- [ ] **Step 2:** Confirm every figure in site prose, curated files and the counter-evidence panel has a row in `figure-verification.md`: figure, page, primary-source URL, date checked, checked by.
- [ ] **Step 3: Independent second check:** a fresh reviewer with no conversation context reads the rendered site, `content/`, `config/` and `src/` as a skeptical AI-safety researcher, looking for errors, overclaims, one-sided framing, causal language in readings, attribution beyond the evidence, and broken behavior. Findings saved to `review/stage1-independent-review.md`.
- [ ] **Step 4: Owner gate:** the owner triages findings; fixes are made; the owner gives explicit go-ahead to publish.
- [ ] **Step 5:** Enable Pages (Task 11 Step 4), push `main`, run the workflow, confirm the live site serves every page and CSV.
- [ ] **Step 6:** Commit `docs: review procedures and verification log`; tag `v0.1.0-release1-stage1`.
