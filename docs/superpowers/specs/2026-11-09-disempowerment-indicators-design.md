# Disempowerment Indicators — Design (v1)

*Drafted 2026-11-09. Status: **approved by owner 2026-11-12**.*

## 1. Intent

A public website that tracks whether society is drifting toward **gradual disempowerment** — the scenario described by Kulveit et al. (2025, [arXiv 2501.16946](https://arxiv.org/abs/2501.16946); [gradual-disempowerment.ai](https://gradual-disempowerment.ai)) in which economies, states and cultures stop depending on human participation (labor, taxes, attention, consent), and so lose the implicit pressure that keeps them serving people. No dramatic takeover; a slow loss of human leverage.

The site turns that argument into **indicators built from free public data**, explains why each was chosen, lets visitors explore the data, and states — as a dated, human-reviewed judgment — what each indicator is telling us now and how that reading has changed since ChatGPT's launch (Q4 2022).

Why it matters: no one has yet published data that operationalizes the paper's proposed metrics (Sec. 6.2). Announced efforts (AI Objectives Institute observatory, a Metaculus-linked index) have released nothing public as of Nov 2026. A careful, transparent tracker is itself a contribution.

### Audience, in priority order
1. **AI-safety researchers** — will scrutinize method, sources, attribution and thresholds.
2. **Journalists** — want the headline finding and a citable chart.
3. **Policymakers** — want what it means and what would change the reading.

Every page therefore leads with the finding and keeps full method one click/scroll away.

## 2. Goals, non-goals, anti-goals

**Goals (v1)**
- A summary page with the scorecard grid, a plain-language "what the data is telling us" statement, and how readings have changed quarter by quarter since Q4 2022.
- One page per indicator: why it matters for disempowerment, interactive chart (switch views and timeframes), current reading with rationale, reading history, method, sources, caveats.
- Data refreshed automatically where sources allow; stale data visibly flagged, and **stale readings** visibly flagged too: when new data arrives after the last review, the reading shows "data updated since review"; when the new data would change the reading, it shows "review pending" (Sec. 4.5).
- A retrospective: quarterly readings from Q4 2022 to now, computed with thresholds fixed *before* being applied to past data.
- Everything reproducible from the public repo.

**Non-goals (v1)**
- Predictions or probabilities.
- A single composite "disempowerment score".
- Non-US coverage beyond what a source provides for free (OECD tax data is international; most others are US).
- User accounts, comments, or any server-side component.

**Anti-goals — failure even if it technically works**
- Attributing movements to AI that the evidence doesn't support (e.g., treating falling democracy scores or the long labor-share decline as AI effects).
- Showing only evidence for disempowerment. Signals pointing the other way must be shown with equal prominence.
- Thresholds tuned after looking at outcomes (hindsight-fitted retrospective). If we look at how labor share moved in 2023–2026 and *then* choose the cut-off for "eroding", we can make the retrospective tell any story we like — consciously or not — and it would look like evidence when it's really our choice. Fixing the thresholds first, with a recorded date and the reasoning behind them (e.g., based on pre-2020 variability), means the retrospective is a genuine test the data could have failed. This is the same logic as pre-registering a study.
- An automated script issuing verdicts in the owner's name.
- Silently serving stale or broken data.
- Committing secrets, or anything from the owner's private research folder, to the public repo.

## 3. Constraints

- **$0 budget.** Free tools and free data only. Public GitHub repo (`richardsonlj12/disempowerment-indicators`), hosted on **GitHub Pages**, refreshed by **GitHub Actions**.
- **Public data only**, with licenses that permit republication. Avoid: OpenSecrets API (closed to new users), EIU, Gallup microdata, ADP, Lightcast, S&P.
- **Secrets** (e.g., FRED API key, Stack Exchange key if used) live only in GitHub Actions Secrets, never in code or commits.
- The owner is learning the workflow; keep the stack small and explain choices.

## 4. How the site interprets data

### 4.1 The scorecard grid
Three **layers** (rows) × three **domains** (columns):

| | Economic | Government | Cultural |
|---|---|---|---|
| **Exposure** — is AI entering the system, and how far? | | | |
| **Erosion** — is the system's dependence on humans falling, and by how much? | | | |
| **Lock-in** — is that dependence becoming hard to restore, and how entrenched is it? | | | |

Every layer asks **whether and to what extent**. Extent is shown two ways: the reading itself is ordered (e.g., low → rising → pervasive), and every reading is displayed with its **magnitude** — the number behind it, in the indicator's own units (e.g., "1.4 pp below 2010–19 trend", "19.8% of firms, +4 pp in 12 months"). Grid cells show readings with magnitudes; they never collapse to a yes/no.

Each indicator sits in one cell. Empty or thin cells are shown honestly as "no public measure yet" (lock-in is mostly unmeasured — say so).

No composite score. Cells are not averaged.

### 4.2 Readings
Readings use **two scales**, because exposure (AI spreading) is not the same as disempowerment (people losing influence). *(Owner decision.)*

**Exposure-row indicators** (E2, G2) use an **exposure scale**:
- **Low**
- **Rising**
- **Pervasive**

**Erosion- and lock-in-row indicators** (E1, E3, G1, G3, C1, C2) use the **influence scale**, recasting the scenarios of the owner's earlier labor-dashboard draft from *welfare* to *influence*:
- **Leverage intact**
- **Leverage eroding**
- **Lock-in signals**

Both scales add **"No signal / insufficient data"** and **"Not yet reviewed"** (data shown, no confirmed reading). The site explains on the summary and methodology pages why the top row of the grid reads on a different scale from the two below it.

Each indicator also carries an **AI-attribution badge** — *strong / moderate / weak* — saying how confidently its movement can be connected to AI rather than other causes.

**How the attribution badge is assigned.** It is a structured judgment, not a calculation, and the site says so. Each indicator is scored against four published criteria:
1. **Directness** — does the series measure AI itself (e.g., firms using AI), or a broad outcome AI is one cause of (e.g., labor share)?
2. **Comparison group** — is there an AI-exposed vs. less-exposed contrast that holds other causes roughly constant?
3. **Timing** — did the change begin or accelerate after generative AI spread (late 2022), rather than continuing an earlier trend?
4. **Known confounders** — how many documented non-AI causes could produce the same movement, and are any of them addressed?

Rule of thumb: **strong** = direct measure, or a comparison group plus timing that fits; **moderate** = timing fits and a plausible mechanism, but no comparison group, or confounders only partly addressed; **weak** = the trend predates generative AI and/or major confounders are unaddressed. Each indicator page shows its score on all four criteria and the reasoning. Badges are drafted in Stage 2 alongside thresholds, reviewed by the owner, and changes are logged on the methodology page.

### 4.3 Two kinds of comparison
- **Slow structural indicators** (decades of history, many causes — e.g., labor share, labor-tax share, Stack Overflow activity): compared against their **pre-generative-AI trend**, fitted over 2010–2019 (after the 2008–09 recession, before COVID distortions). The question: is the series departing from that trend, and how fast?
- **AI-native indicators** (began near zero recently, change month to month — e.g., firm AI adoption, federal AI use cases): compared against **their own recent path** — level, rate of change, and acceleration over rolling 3-, 6- and 12-month windows (or the native frequency where data are annual).

Each indicator's spec states which comparison it uses and its **threshold bands** for the three readings.

### 4.4 Thresholds and the retrospective
- Thresholds are drafted per indicator during the build, reviewed by the owner, then **frozen with a recorded date** before the retrospective is computed. Changes after freezing are logged with reasons (a visible threshold-revision history on the methodology page).
- Measurement window rules (e.g., "rate of change over the latest 4 quarters vs. trend") are fixed per indicator, because the window alone can flip a reading (labor share reads differently over 5 quarters vs. since 2019).
- **Retrospective:** apply the frozen thresholds to each quarter from **Q4 2022** onward, using the **latest revised data** for every indicator. *(Owner decisions below.)*
  - Computed **once**, as a deliberate run, producing proposed readings (~8 indicators × ~16 quarters).
  - The owner **reviews them as a set**: approves the batch, overriding individual readings with a rationale where they disagree. Nothing in the retrospective is published unreviewed.
  - Published as a **dated snapshot** ("computed <date>, thresholds frozen <date>, data as of <date>"). It does **not** recompute when data is revised. A re-run is an explicit owner decision and produces a new dated snapshot; earlier snapshots remain viewable on an **Archive** page, linked from the summary page and from every indicator page.
- The economic starting thresholds draw on the owner's earlier draft, with corrections from research: the "Canaries" gap is cumulative, not year-on-year; labor share is now 52.8% (2026Q2); adoption thresholds must name their measure (firm-weighted vs employment-weighted).

### 4.5 Readings are dated human judgments
- Scripts compute a **proposed** reading from data and thresholds.
- The owner **confirms or overrides** it, with a one-to-three sentence rationale. Only confirmed readings appear as "current".
- Every reading is stored with its date, so the site can show history. Charts update automatically; readings change only on review.
- Retrospective readings are labeled as such ("computed retrospectively on <date> with thresholds frozen <date>") and kept distinct from readings made in real time.
- **Review cadence** *(Claude's call)*: a scheduled **quarterly review** of all current readings. Between reviews, the automation **opens a GitHub issue** whenever a computed proposal differs from the confirmed reading, so changes don't go unnoticed. Each indicator page shows the date of its last review.
- **What happens when data updates automatically** *(clarified at owner's question)*:
  - Every refresh recomputes the proposed reading.
  - **New data period arrives, proposal unchanged** (e.g., a new quarter of labor share that stays within the same band): the page shows "**data updated since review** (data through <date>, last reviewed <date>)". No issue is opened, to avoid weekly noise; it is covered by the quarterly review.
  - **Proposal changes** (crosses a threshold): a GitHub issue opens, and the page shows "**review pending** — new data suggests <proposed reading>", next to the current confirmed reading, until the owner reviews it.
  - **Data revisions** to past periods that change a proposal are treated the same way as a proposal change.
  - **Fetch fails or data goes stale**: CI fails, an issue opens, and the page shows "stale since <date>".

### 4.5a Indicators made of several series *(Claude's call)*
- **C1** (Stack Overflow + Wikipedia), **G1** (US quarterly + OECD annual), **E1** (labor share + profit share): each series gets its own chart and its own computed proposal; each indicator still gets **one** reading.
- When series disagree, the owner decides and the rationale says so. Nothing is averaged automatically.
- **G1:** US quarterly data drives the reading (timely); OECD is the international context. **E1:** labor share alone drives the reading; profit share is shown alongside for context.
- Income and wealth concentration (including AI-linked fortunes) was raised by the owner; see Sec. 8.4 — **pending owner decision on whether it joins v1**.

### 4.6 Standing guards against one-sided reading
- **Counter-evidence panel** on the summary page: signals pointing away from disempowerment (e.g., labor-tax share rising; AI legislation passed; public pushback).
- **Welfare-vs-influence note** on every economic page: people can be better off materially while losing leverage, and vice versa.
- **Augmentation-vs-displacement note** wherever adoption is shown: adoption alone doesn't distinguish empowering from disempowering uses.
- Language: indicators show "conditions under which the hypothesized mechanism would operate", not proof that disempowerment is occurring.

## 5. v1 indicators

Eight indicators chosen because their data is free, refreshable and comparatively simple to process. "Tier" = refresh mode: **1** fully automated API, **2** semi-automated annual/irregular release, **3** curated points entered by hand with citations.

| # | Domain | Indicator | Layer | Attribution | Comparison | Tier | Primary source |
|---|---|---|---|---|---|---|---|
| E1 | Economic | **Labor share of income**, nonfarm business (profit share shown as mirror) | Erosion | Weak | Structural | 1, quarterly | BLS Productivity & Costs via FRED |
| E3 | Economic | **Wealth concentration** — top 1% and top 0.1% share of household wealth | Lock-in proxy | Weak | Structural | 1, quarterly | Federal Reserve Distributional Financial Accounts (DFA) |
| E2 | Economic | **Firm AI adoption** (share of firms using AI) | Exposure | Strong | AI-native | 1, biweekly | Census Business Trends and Outlook Survey (BTOS) |
| G1 | Government | **Labor-based share of tax revenue** (personal income tax + social contributions) | Erosion (core mechanism) | Weak now; central in theory | Structural | 2 annual (OECD); 1 quarterly (US) | OECD Revenue Statistics; US: BEA NIPA / Treasury Fiscal Data |
| G2 | Government | **Federal AI use cases**, total and high-impact per agency | Exposure | Strong | AI-native | 2, annual | OMB federal AI use-case inventories (GitHub CSVs) |
| G3 | Government | **Lobbying by AI companies** (spend and share of total lobbying) | Lock-in proxy | Moderate | AI-native | 1, quarterly | LDA.gov lobbying disclosure API |
| C1 | Cultural | **Human knowledge-commons activity** — Stack Overflow monthly questions; Wikipedia human pageviews (and editors if feasible) | Erosion | Moderate | Structural | 1, monthly | Stack Exchange API; Wikimedia Analytics API |
| C2 | Cultural | **Production vs. consumption** — AI share of what's produced vs. what people actually consume (music; web articles; news) | Exposure → erosion test | Strong, detector-dependent | Curated, no automated reading bands (see notes) | 3, curated | Deezer newsroom; Graphite; UMD/Pangram news study |

Plus the **counter-evidence panel** (not an indicator; no reading): AI legislation counts and other countervailing signals, curated (Tier 3) from Stanford AI Index, CSET AGORA, OECD.AI.

### Indicator notes
- **E1:** Show full 1947– history; post-2022 against 2010–2019 trend. Badge *weak*: the decline predates generative AI by ~20 years. Latest: 52.8% (2026Q2), series low.
- **E3:** *(Added by owner 2026-11-12.)* Concentrated wealth is a lock-in proxy: it converts into political and cultural influence and is hard to reverse (Kulveit's "wealth distribution" metric). Badge *weak*: concentration has risen since the 1980s for many reasons; DFA data begin 1989. Compare post-2022 against the 2010–2019 trend. The page should note that the more AI-specific version — the share of top fortunes tied to AI companies — is planned (Sec. 8.4). Layer placement (lock-in) is Claude's call.
- **E2:** Series break 17 Nov 2025 (question wording changed) — annotate; do not splice silently. Note ~10–11% "don't know". Name the measure (firm-weighted) everywhere; contrast with employment-weighted figures in text.
- **G1:** Currently *rising* — likely reads "leverage intact". Show it prominently; it's the cleanest test of the state-dependence argument and it currently points the other way. OECD data lags ~2 years.
- **G2:** Self-reported; definitions change between years ("rights/safety-impacting" → "high-impact"); 2024 baseline conflicts (1,757 press vs 2,133 repo) — document the choice. **Defense and intelligence AI uses are largely excluded from the inventory — critical caveat** *(owner emphasis)*: state it in the headline area of the page (not only in method notes), in the "what it doesn't show" box, and in the chart title or subtitle (e.g., "Civilian federal AI use cases"), so no reader takes the count as the whole of government AI use. Pair with agency workforce trend only as context (2025 cuts were policy-driven, not AI).
- **G3:** Requires a maintained, versioned list of "AI companies" (with inclusion criteria and change log). LDA migrated from lda.senate.gov in mid-2026 — confirm API access and key rules before building.
- **C1:** Recompute counts from the APIs; don't cite press figures (they conflict). Stack Overflow's decline began ~2020 — show that. Annotate Wikimedia's bot-reclassification break. Identify the client with a User-Agent as Wikimedia requires; respect rate limits.
- **C2:** Curated pairs of points with citations, refreshed by hand. Because the data is sparse and from single platforms/vendor detectors, it gets a reading only by owner judgment, never computed bands. It illustrates the key cultural distinction: AI saturates *production* (~50% of new web articles; >50% of Deezer uploads) while *consumption* stays mostly human (1–3% of Deezer streams).

All latest figures above come from the research report (private research folder) and must be re-checked against primary sources before publication; figures marked secondary there must not be published unverified.

## 6. Pages

1. **Summary (home):** scorecard grid with current readings and badges; "what the data is telling us" statement (owner-written, dated); a quarter-by-quarter view of how readings have changed since Q4 2022 (retrospective clearly labeled); counter-evidence panel; links to each indicator; link to the **Archive**.
2. **Indicator page** (one fixed template):
   - Headline: current reading, badge, date, one-sentence takeaway.
   - "Why this matters for gradual disempowerment".
   - Interactive chart: timeframe selection; alternate views where meaningful (e.g., level vs. deviation from trend; firm-size cuts).
   - Reading history (timeline of readings with rationales).
   - "What it shows / what it doesn't show" box.
   - "What would change our reading".
   - Method: comparison type, window rule, threshold bands, data source(s) with links, license, last fetched, series breaks, caveats.
   - Download the data (CSV).
3. **Methodology:** the framework (layers, readings, badges, comparisons), threshold freeze dates and revision log, retrospective method, critiques the site takes seriously (Krueger, Millidge, Jedlicka, the authors' own caveats), and what's planned for later.
4. **Archive:** all earlier retrospective snapshots, past "what the data is telling us" statements, and superseded threshold versions, each dated. Linked from the summary and every indicator page.
5. **About:** purpose, author, how to cite, how to report errors (GitHub issues).

## 7. Architecture

```
Public sources ──► Python fetch scripts ──► data/ (tidy CSV + metadata) ──► Quarto site ──► GitHub Pages
                  (GitHub Actions, scheduled)       ▲
                                     readings file (owner-reviewed) ┘
```

- **Site:** Quarto (actively maintained; v1.11.x as of Oct 2026). Interactive charts via Quarto's built-in Observable JS (Observable Plot + Inputs) or Plotly — builder's choice, applied consistently.
- **Data scripts:** Python, one per indicator source, **independent of the site generator**. Each writes tidy CSV plus metadata (source URL, license, fetched-at timestamp, data vintage, series-break notes) into a data folder the site reads. Switching site tools later should only mean rewriting page templates.
- **Readings:** a human-edited, version-controlled file of dated readings and rationales. Scripts may write *proposed* readings; only owner-confirmed ones are published as current.
- **Automation:** a scheduled GitHub Actions workflow runs the fetch scripts, commits changed data, rebuilds and deploys. Scheduled workflows in public repos stop after 60 days without repo activity — data commits keep it alive; the builder should confirm.
- **Health checks:** each source has a check that fails loudly in CI and shows a "stale since <date>" badge on the affected page instead of silently serving old data.
- **GitHub Pages base path:** project site at `richardsonlj12.github.io/disempowerment-indicators/`; configure links accordingly.
- **Local preview:** the owner can preview the site locally before pushing (GitHub Pages has no per-change previews).

## 7a. Release stages *(owner decision: staged launch)*

1. **Stage 1 — data site.** All v1 indicator pages with live data, interactive charts, "why this matters", method, sources and caveats. Readings show **"Not yet reviewed"**. Summary page shows the grid structure with indicators placed but unread, plus the counter-evidence panel. Every published figure verified (Sec. 7b) before deploy.
2. **Stage 2 — thresholds.** Draft bands and window rules per indicator; owner reviews and **freezes** them (dated).
3. **Stage 3 — readings.** Compute current proposals and the retrospective; owner reviews as a set; publish confirmed current readings, the retrospective snapshot, reading histories, and the "what the data is telling us" statement.

## 7b. Review procedures *(owner requirement; specifics are Claude's proposal for owner review)*

Nothing reaches the public site without passing the relevant checks. Procedures are written down in the repo (e.g., a `REVIEW.md` checklist) so they're repeatable.

**Automated checks (run in CI on every change and scheduled refresh; a failure blocks deploy):**
- Fetch health: each source responded, returned the expected columns/units, and data isn't older than its expected update lag (otherwise "stale since" badge).
- Sanity checks per series: values within plausible ranges, no unexpected gaps or duplicate dates, series breaks annotated.
- **Spot-check against published figures:** for each indicator, at least one known value from the primary source (e.g., BLS's published 52.8% for 2026Q2) is asserted in a test, so a broken calculation is caught.
- Site builds without errors; links and downloads work.

**Human review gates (owner):**
- **Figure verification** before Stage 1 deploy and whenever text cites a new number: every figure in prose traced to its primary source, with link; secondary-only figures are not published.
- **Indicator page review** before first publication of each page: reasoning, caveats, attribution badge, "what it doesn't show".
- **Threshold freeze** (Stage 2): bands and window rules reviewed and dated.
- **Readings review**: retrospective as a set (Stage 3); current readings quarterly and on automation-opened issues.

**Independent second check:** before each stage goes live, a fresh AI reviewer with no access to our conversation reads the pages, method and code and tries to find errors, overclaims and one-sided framing (acting as a skeptical AI-safety researcher). Its findings are triaged by the owner before release.

**Corrections policy:** errors found after publication are fixed openly with a dated correction note on the affected page; the public can report errors via GitHub issues.

## 8. Later versions

Recorded so they are planned, not lost.

**8.1 Method**
- **First-published ("as of then") comparison** for FRED-covered economic series using **ALFRED** vintages: show what the reading would have been with data as first released vs. latest revised, and where they disagree.

**8.2 Harder indicators from the recommended ten**
- **Young workers in AI-exposed jobs** — Stanford "Canaries" figures (curated) plus an open proxy from CPS microdata (IPUMS or Census API) pooled 6–12 months, exposure quintiles from Eloundou et al. or Felten AIOE, ages 22–25 vs 35–49; label as a rough proxy with wide uncertainty. Latest Stanford figure: ~19% below benchmark (cumulative since late 2022, June 2026 data).
- **Job postings weighted by AI exposure** — Indeed Hiring Lab postings by sector (GitHub, CC BY 4.0) with a hand-built Indeed-sector → SOC crosswalk and exposure weights.
- **AI-written share of scientific papers and peer reviews** — self-computed with Liang et al.'s distributional method on arXiv abstracts and OpenReview reviews (vendor-free).

**8.3 Remaining indicators from the owner's earlier labor-dashboard draft**
- **Recent-graduate unemployment and underemployment** (NY Fed, quarterly; no API).
- **Labor force participation in AI-exposed occupations** (CPS).
- **Real wages in exposed vs non-exposed occupations** (CPS-ORG or ACS for trends; OEWS only for weights — BLS advises against OEWS time series).
- **AI capital investment share** — proxy from BEA information-processing equipment + software + data-center structures as a share of business investment (BEA has no AI category). The St. Louis Fed GDP-contribution claim remains unverified.

**8.4 Other candidates from the research**
- Economic: automation vs augmentation share of AI use (Anthropic Economic Index); AI compute concentration (Epoch AI); wage–productivity gap; corporate profit share as its own indicator.
- **Income and wealth concentration, including AI-linked fortunes** *(owner interest)*. Matches Kulveit's "wealth distribution between AI-heavy and human-centric industries". Options:
  - Top 1% / 0.1% wealth share — Fed Distributional Financial Accounts — **moved into v1 as E3 (owner decision 2026-11-12)**.
  - Top income shares — World Inequality Database (free, annual, CC BY).
  - AI-linked share of top wealth (how much of the richest people's wealth is tied to AI companies) — the most AI-specific version, but the standard sources (Forbes, Bloomberg Billionaires) restrict republication; would need a hand-curated list built from public filings. Harder.
  - AI-company share of total stock-market value — the main index data is paid (S&P); a free version would need building from public filings.
- Government: AI-vendor concentration in federal procurement (USAspending API); AI-generated share of public regulatory comments (regulations.gov API); democratic voice / trust in government as labeled context (OECD Trust Survey, Pew); legislative complexity (no source researched yet — a gap in the paper's own list); AI role in legal processes and security (largely opaque).
- Cultural: AI as information and relationship intermediary (Pew, Reuters Digital News Report, Common Sense Media; Anthropic/OpenAI usage reports); time spent socializing (BLS American Time Use Survey) as context; AI share of news and AI content farms (UMD/Pangram study, NewsGuard); search-to-publisher click-through (Pew); Wikipedia editor activity.
- Cross-cutting: international comparisons where free data allow; Kulveit Sec. 6.2 metrics with no public proxy yet (fraction of corporate decisions made by AI, unsupervised AI spending).

## 9. Left to the builder

- Exact series IDs, API endpoints and query definitions per source (verify each; several access details in the research are unconfirmed).
- Chart library (Observable Plot vs Plotly) and visual design, within: accessible, readable in light and dark mode, works on phones.
- Data file layout and metadata schema; readings file format.
- Draft threshold bands and window rules per indicator, for owner review and freezing.
- Refresh schedule per source (no more frequent than the source updates).
- Test approach for fetch scripts and calculations.

## 10. Calls made by Claude (owner to check)

- v1 set = the seven "simpler" indicators plus E3 (added by owner 2026-11-12) listed in Sec. 5; C2 (production vs consumption) included although curated, because it is simple to build and carries the central cultural distinction.
- Counter-evidence panel ships in v1 though it's not an indicator.
- "No signal / insufficient data" and "Not yet reviewed" added as reading states.
- C2 gets readings only by owner judgment, never computed bands.
- Scripts propose readings; owner confirms (readings file in the repo).
- Multi-series indicators: one reading, owner decides on disagreement; US data drives G1, labor share drives E1 (Sec. 4.5a).
- Quarterly review plus auto-opened GitHub issues when a proposal changes (Sec. 4.5).
- The specific review procedures in Sec. 7b (owner asked for review procedures; the details are proposed).
- G3 (lobbying, lock-in proxy) and C2 use the influence scale.
- Owner's private research folder and earlier draft brief stay out of the public repo; the design references them only in general terms.

*Owner reviewed Sec. 10 on 2026-11-12: approved.*

**Added after owner review (2026-11-12), for owner to check:**
- Readings shown with magnitudes; layer questions now ask "whether and how far" (Sec. 4.1).
- Attribution-badge rubric: four criteria and rule of thumb (Sec. 4.2).
- Data-update behavior: no issue for routine new data; "data updated since review" flag instead; issue + "review pending" only when the proposal changes (Sec. 4.5).
- Archive page (Sec. 6).
- G2 defense/intelligence caveat placed in headline, chart title and "what it doesn't show" (Sec. 5).