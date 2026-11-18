# Disempowerment Indicators — Design (v1)

*Drafted 2026-11-09. Approved by owner 2026-11-12. **Revision 2, 2026-11-12:** incorporates an independent review and the owner's decisions on it (see Sec. 11). Revision 2 approved by owner 2026-11-17. **Revision 3, 2026-11-17:** terminology and page changes from the owner's review of the Stage 1 prose (see Sec. 11, Revision 3).*

## 1. Intent

A public website that tracks whether society is drifting toward **gradual disempowerment** — the scenario described by Kulveit et al. (2025, [arXiv 2501.16946](https://arxiv.org/abs/2501.16946); [gradual-disempowerment.ai](https://gradual-disempowerment.ai)) in which economies, states and cultures stop depending on human participation (labor, taxes, attention, consent), and so lose the implicit pressure that keeps them serving people. No dramatic takeover; a slow loss of human leverage.

The site turns that argument into **indicators built from free public data**, explains why each was chosen, lets visitors explore the data, and states — as a dated, human-reviewed judgment — what each indicator is telling us now and how that reading has changed since ChatGPT's launch (Q4 2022).

Why it matters: no one has yet published data that operationalizes the paper's proposed metrics (Sec. 6.2). Announced efforts (AI Objectives Institute observatory, a Metaculus-linked index) have released nothing public as of Nov 2026. A careful, transparent tracker is itself a contribution.

The site is built to **iterate**: a small, defensible first release, then additions (Sec. 7a, Sec. 8).

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
- A retrospective: quarterly readings from Q4 2022 to now, computed with a threshold **rule** fixed *before* being applied (Sec. 4.4).
- Everything reproducible from the public repo.

**Non-goals (v1)**
- Predictions or probabilities.
- A single composite "disempowerment score".
- Non-US coverage beyond what a source provides for free (OECD tax data is international; most others are US).
- User accounts, comments, or any server-side component.
- Recommending that any indicator be targeted or optimized by policy (Sec. 4.6).

**Anti-goals — failure even if it technically works**
- Attributing movements to AI that the evidence doesn't support (e.g., treating falling democracy scores or the long labor-share decline as AI effects).
- Reading labels that imply cause: a reading describes what the data is doing; interpretation is separate and always carries the AI link rating (Sec. 4.2).
- Showing only evidence for disempowerment. Signals pointing the other way must be shown with equal prominence.
- Thresholds tuned after looking at outcomes (hindsight-fitted retrospective). If we look at how labor share moved in 2023–2026 and *then* choose the cut-off, we can make the retrospective tell any story we like — consciously or not — and it would look like evidence when it's really our choice. Because the owner and the builder have already seen the 2023–26 data, freezing hand-picked thresholds is not enough: the **rule** that generates the bands is fixed first, the bands fall out of it, and a sensitivity table shows what alternative rules would have said (Sec. 4.4). This is the same logic as pre-registering a study.
- Treating movement inside a series' noise as a signal.
- An automated script issuing verdicts in the owner's name.
- Silently serving stale or broken data.
- Committing secrets, or anything from the owner's private research folder, to the public repo.

## 3. Constraints

- **$0 budget.** Free tools and free data only. Public GitHub repo (`richardsonlj12/disempowerment-indicators`), hosted on **GitHub Pages**, refreshed by **GitHub Actions**.
- **Public data only**, with licenses that permit republication. Avoid: OpenSecrets API (closed to new users), EIU, Gallup microdata, ADP, Lightcast, S&P.
- **Secrets** (e.g., FRED API key, Stack Exchange key if used) live only in GitHub Actions Secrets, never in code or commits.
- The owner is learning the workflow; keep the stack small and explain choices.
- **Disclosure:** the site is built with assistance from Claude (Anthropic), and one indicator (E3) uses Anthropic data. The About page and the E3 page say so.

## 4. How the site interprets data

### 4.1 The scorecard grid
Three **layers** (rows) × three **domains** (columns), plus one cross-cutting row:

| | Economic | Government | Cultural |
|---|---|---|---|
| **Adoption** — is AI entering the system, and how far? | | | |
| **Displacement** — is the system's dependence on human participation falling, and by how much? | | | |
| **Lock-in** — is that dependence becoming hard to restore, and how entrenched is it? | | | |
| **Across all domains: human deferral and oversight** — are people deferring to AI's judgment? | spans all three columns | | |

Every layer asks **whether and to what extent**. Extent is shown two ways: the reading itself is ordered, and every reading is displayed with its **magnitude** — the number behind it, in the indicator's own units, naming its baseline (e.g., "1.4 points below its 2010–19 trend", "19.8% of firms; +4 points in 12 months, faster than its recent pace"). Grid cells show readings with magnitudes and AI link ratings together, everywhere; they never collapse to a yes/no.

Each indicator sits in one cell. Empty or thin cells are shown honestly as "no public measure yet".

No composite score. Cells are not averaged.

**The rows are inspired by Chooi, Lee & Li (2026)** ([ACL Anthology](https://aclanthology.org/2026.evaleval-1.36/)), whose layers are exposure, erosion and lock-in. *(Revision 3, owner decision.)* The site's rows ask different questions, so the first two are renamed, and the methodology page carries a crosswalk table and credits the paper as the inspiration:
- **Adoption** (E2, E3) ≈ what the paper treats as adoption measures that "might serve as instrumental indicators" of disempowerment, outside its three layers.
- **Displacement** (E1, G1, C1) ≈ the displacement half of the paper's **exposure** layer (AI displacing human participation), measured for whole systems, following Kulveit et al.
- The paper's **erosion** layer (individual capability loss) is not measured by the site.
- **Lock-in** ≈ the paper's lock-in.

Internal layer keys in config and code stay `exposure`, `erosion`, `lockin`; `registry.layer_label()` gives the display names.

**Lock-in needs an operational definition before anything is placed in that row.** Concentration of wealth or political influence (E4, G3) is not by itself evidence that reduced human dependence is hard to reverse. Before Release 2 places E4 or G3 in the lock-in row, an operational test is written and owner-approved — candidates: *persistence* (a departure from baseline that does not revert after shocks over a stated number of periods) and *rising switching costs* (growing capacity of AI-interest actors to block reversal). If no test is adopted, the row is renamed **"Concentration of influence"** rather than overclaiming. Until then the lock-in row reads "no public measure yet". *(Owner to decide before Release 2.)*

**Human deferral and oversight** is the paper's core mechanism — decisions moving from humans to AI — and has no public time series. Release 1 shows this row as "no public measure yet", citing the only current evidence: Herdağdelen, Joren & Tamkin (2026), "How AI agents shape experts' judgment calls" (Anthropic Research). Figures are taken from the full paper before citing.

### 4.2 Readings
Readings describe **what the data is doing**, not what it means. Interpretation sits in a separate line that always carries the AI link rating. *(Owner decision.)*

**Adoption-row indicators** (E2, E3, G2) use the **exposure scale** (displayed as the labels Low / Rising / Pervasive; the internal scale key stays `exposure`):
- **Low**
- **Rising**
- **Pervasive**

**Displacement- and lock-in-row indicators** (E1, G1, C1; Release 2: E4, G3, C2) use the **baseline scale** *(owner decision; replaces "leverage intact / eroding / lock-in signals")*:
- **Within baseline**
- **Above baseline**
- **Below baseline**
- **Far above baseline**
- **Far below baseline**

"Baseline" is defined per comparison type (Sec. 4.3) and is **named in the line under every reading**, so no reader has to click to find out what it means.

Both scales add **"No signal / insufficient data"** and **"Not yet reviewed"** (data shown, no confirmed reading).

Every reading is displayed as three lines:

> **E1 Labor share: Below baseline**
> 1.4 points below its 2010–19 trend
> *If AI-driven, consistent with workers losing leverage · AI link: weak*

> **G1 Worker tax share: Above baseline**
> *Points away from disempowerment: the state's reliance on taxing workers is rising · AI link: weak*

> **E2 Firm AI adoption: Rising**
> 19.8% of firms; +4 points in 12 months, faster than its recent pace
> *Adoption only; doesn't by itself show lost leverage · AI link: strong*

(Example figures are illustrative until verified and computed.)

Each indicator states its **warning sign** *(renamed from "direction assumption" in Revision 3)*: which direction of movement would be consistent with people losing leverage, so that the interpretive line can be written mechanically. Leverage is defined once on the methodology page: the bargaining power people have because systems need their work, taxes or attention.

**Leading or lagging.** Each indicator is labeled *leading* (likely to move early) or *lagging* (likely to show damage only after it is entrenched). Most long-running series lag.

**AI link** — *strong / moderate / weak* — *(renamed from "AI-attribution badge", then from "AI-specificity" in Revision 3; config field `ai_link`)* says how confidently a series' movement can be connected to AI rather than other causes. "Strong" for a series that *is* about AI (E2, E3, G2) means only that it measures AI directly; it does **not** mean strong evidence of harm or that it shows disempowerment. Every indicator page says so where the rating first appears.

**How the AI link is assigned.** It is a structured judgment, not a calculation, and the site says so. Each indicator is scored against four published criteria:
1. **Directness** — does the series measure AI itself (e.g., firms using AI), or a broad outcome AI is one cause of (e.g., labor share)?
2. **Comparison group** — is there an AI-exposed vs. less-exposed contrast that holds other causes roughly constant?
3. **Timing** — did the change begin or accelerate after generative AI spread (late 2022), rather than continuing an earlier trend?
4. **Known confounders** — how many documented non-AI causes could produce the same movement, and are any of them addressed?

Rule of thumb: **strong** = direct measure, or a comparison group plus timing that fits; **moderate** = timing fits and a plausible mechanism, but no comparison group, or confounders only partly addressed; **weak** = the trend predates generative AI and/or major confounders are unaddressed. Each indicator page shows its score on all four criteria and the reasoning. Badges are drafted in Stage 2 alongside thresholds, reviewed by the owner, and changes are logged on the methodology page. Adding a comparison group (Sec. 5, C1) can honestly raise a badge.

### 4.3 Two kinds of comparison
- **Long-running series** (decades of history, many causes — e.g., labor share, labor-tax share, Stack Overflow activity): the baseline is the series' **pre-generative-AI pattern, 2010–2019** (after the 2008–09 recession, before COVID distortions). The question: is the series departing from that pattern, and how fast?
- **Series that measure AI use directly** (began near zero recently, change month to month — e.g., firm AI adoption, federal AI use cases, the Economic Index): the baseline is **their own recent path** — level, rate of change, and acceleration over rolling 3-, 6- and 12-month windows (or the native frequency where data are annual).

**Uncertainty and seasonality.**
- Where a source publishes standard errors (e.g., Census BTOS), show them as bands on the chart and use them in the threshold rule.
- Monthly series with seasonal patterns (Stack Overflow, Wikipedia) are compared year-over-year or seasonally adjusted, stated per indicator.
- A move inside a series' noise band never counts as crossing a threshold.

### 4.4 Thresholds and the retrospective
- **Rule first.** In Stage 2, a **mechanical rule** for each comparison type is written, reviewed by the owner and **frozen with a recorded date**; the bands for each indicator then fall out of the rule rather than being hand-picked. Candidate rule for structural series: compare the change over the indicator's window with the spread of same-length changes in 2010–2019, with "Within baseline" inside ±1 standard deviation, "Above/Below" between 1 and 2, and "Far above/below" beyond 2. This avoids extrapolating a 2010–19 straight line seven or more years forward, which the review cautioned against; deviation from the 2010–19 trend remains available as a chart view. A matching rule is written for the exposure scale. *(The exact rule is a Stage 2 decision.)*
- **Window rules** (e.g., "change over the latest 4 quarters") are fixed per indicator as part of the rule, because the window alone can flip a reading.
- **Sensitivity table.** Each indicator page and the methodology page show the reading under reasonable alternatives — other windows, other baseline periods (e.g., 2015–19), narrower and wider bands. Where a reading flips under a reasonable alternative, the page says so.
- Changes after freezing are logged with reasons (a visible threshold-revision history on the methodology page).
- Adoption measures always name what they measure (firm-weighted vs. employment-weighted).
- **Retrospective:** apply the frozen rule to each quarter from **Q4 2022** onward, using the **latest revised data** for every indicator. *(Owner decisions below.)*
  - Computed **once**, as a deliberate run, producing proposed readings (about 5 Release 1 indicators × about 16 quarters).
  - The owner **reviews them as a set**: approves the batch, overriding individual readings with a rationale where they disagree. Nothing in the retrospective is published unreviewed.
  - Published as a **dated snapshot** ("computed [date], rule frozen [date], data as of [date]"). It does **not** recompute when data is revised. A re-run is an explicit owner decision and produces a new dated snapshot; earlier snapshots remain viewable on an **Archive** page, linked from the summary page and from every indicator page.

### 4.5 Readings are dated human judgments
- Scripts compute a **proposed** reading from data and the frozen rule.
- The owner **confirms or overrides** it, with a one-to-three sentence rationale. Only confirmed readings appear as "current".
- Every reading is stored with its date, so the site can show history. Charts update automatically; readings change only on review.
- Retrospective readings are labeled as such ("computed retrospectively on [date] with rule frozen [date]") and kept distinct from readings made in real time.
- **Review cadence:** a scheduled **quarterly review** of all current readings. Between reviews, the automation **opens a GitHub issue** whenever a computed proposal differs from the confirmed reading. Each indicator page shows the date of its last review.
- **What happens when data updates automatically:**
  - Every refresh recomputes the proposed reading.
  - **New data period arrives, proposal unchanged:** the page shows "**data updated since review** (data through [date], last reviewed [date])". No issue is opened; it is covered by the quarterly review.
  - **Proposal changes** (crosses a threshold): a GitHub issue opens, and the page shows "**review pending** — new data suggests [proposed reading]", next to the current confirmed reading, until the owner reviews it.
  - **Data revisions** to past periods that change a proposal are treated the same way as a proposal change.
  - **Fetch fails or data goes stale:** CI fails, an issue opens, and the page shows "stale since [date]".

### 4.5a Indicators made of several series
- **C1** (Stack Overflow + comparison sites + Wikipedia), **G1** (US quarterly + OECD annual), **E1** (labor share + profit share): each series gets its own chart and its own computed proposal; each indicator still gets **one** reading.
- When series disagree, the owner decides and the rationale says so. Nothing is averaged automatically.
- **G1:** US quarterly data drives the reading (timely); OECD is the international context. **E1:** labor share alone drives the reading; profit share is shown alongside for context. **C1:** the Stack Overflow relative-activity index (against the four comparison sites) drives the reading; Wikipedia is shown alongside.

### 4.6 Standing guards against one-sided reading
- **Counter-evidence panel** on the summary page: signals pointing away from disempowerment, **held to the same standard as the indicators** — sourced from primary sources, dated, and selected by inclusion criteria written in advance. It includes policy pushback and data moving against the mechanism (e.g., labor-tax share not falling; AI legislation passed). *(Revision 3, owner decision:)* material welfare signals are **not** included, because welfare is not agency: people can be better off while losing influence. US real median household income may appear only as labeled context, never as counter-evidence.
- **Warning sign** and **Alternative explanations** on every indicator page, as sub-headings of "What would change our reading" *(renamed in Revision 3)*. Alternative explanations are the most plausible other explanations of the same data, including a reassuring movement that hides displacement and an alarming one with a cause other than AI. Examples: E1 — labor share could hold steady while work shifts into low-leverage sectors (Imas and Schaal's "relational sector" argument), so a flat line is not proof that leverage is intact. G1 — a state can co-opt citizens through transfers (the rentier pattern), so G1 is the most direct public measure of state dependence, not a guarantee. C1 — falling Wikipedia pageviews may reflect AI *intermediation* (people still consume its content, through chatbots) rather than human disengagement.
- **Welfare-vs-influence note** on every economic page: people can be better off materially while losing leverage, and vice versa.
- **Augmentation-versus-replacement note** wherever adoption is shown *(renamed in Revision 3 so it does not collide with the Displacement row)*; E3 turns this note into data.
- **Diagnostics, not targets:** the methodology page states that the site does not recommend optimizing any series; policy aimed at moving one number would break its value as a signal (Goodhart's law).
- **The cultural gap is named:** C1 and C2 measure content and activity, not human capacity, attention or reliance. The methodology page says so and names AI-as-intermediary survey data (Pew, Reuters Institute Digital News Report) as the next candidate.
- Language *(Revision 3)*: every page carries "These indicators show whether the conditions for disempowerment are present. They do not show that it is happening."

## 5. v1 indicators

**Release 1** ships five indicators plus the oversight row and the counter-evidence panel. **Release 2** adds four more (Sec. 7a). "Tier" = refresh mode: **1** fully automated API, **2** semi-automated annual/irregular release, **3** curated points entered by hand with citations.

| #   | Release | Domain     | Indicator                                                                                                                                                             | Row                          | AI link                     | Comparison                        | Tier                              | Primary source                                          |
| --- | ------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | --------------------------- | --------------------------------- | --------------------------------- | ------------------------------------------------------- |
| E1  | 1       | Economic   | **Labor share of income**, nonfarm business (profit share shown as mirror)                                                                                            | Displacement                 | Weak                        | Structural                        | 1, quarterly                      | BLS Productivity & Costs via FRED                       |
| E2  | 1       | Economic   | **Firm AI adoption** (share of firms using AI)                                                                                                                        | Adoption                     | Strong                      | AI-native                         | 1, biweekly                       | Census Business Trends and Outlook Survey (BTOS)        |
| E3  | 1       | Economic   | **How AI is used: automation vs. augmentation**                                                                                                                       | Adoption                     | Strong (one vendor)         | AI-native                         | 2, irregular                      | Anthropic Economic Index (Hugging Face)                 |
| G1  | 1       | Government | **Labor-based share of tax revenue** (personal income tax + social contributions)                                                                                     | Displacement (core mechanism) | Weak now; central in theory | Structural                        | 1 quarterly (US); 2 annual (OECD) | US: BEA NIPA via FRED; OECD Revenue Statistics          |
| C1  | 1       | Cultural   | **Human knowledge-commons activity** — Stack Overflow monthly questions vs. non-programming Stack Exchange sites; Wikipedia human pageviews (and editors if feasible) | Displacement                 | Moderate                    | Structural, with comparison group | 1, monthly                        | Stack Exchange API; Wikimedia Analytics API             |
| —   | 1       | All        | **Human deferral and oversight** — no public measure yet                                                                                                              | Cross-cutting                | —                           | —                                 | 3, curated citation               | Herdağdelen, Joren & Tamkin (2026)                      |
| E4  | 2       | Economic   | **Wealth concentration** — top 1% and top 0.1% share of household wealth                                                                                              | Lock-in (pending definition) | Weak                        | Structural                        | 1, quarterly                      | Federal Reserve Distributional Financial Accounts (DFA) |
| G2  | 2       | Government | **Federal AI use cases**, total and high-impact per agency                                                                                                            | Adoption                     | Strong                      | AI-native                         | 2, annual                         | OMB federal AI use-case inventories (GitHub)            |
| G3  | 2       | Government | **AI-interest political influence** (lobbying)                                                                                                                        | Lock-in (pending definition) | Moderate                    | AI-native                         | 1, quarterly                      | LDA.gov lobbying disclosure API                         |
| C2  | 2       | Cultural   | **Production vs. consumption** — AI share of what's produced vs. what people actually consume (music; web articles; news)                                             | Displacement                 | Strong, detector-dependent  | Curated, no computed bands        | 3, curated                        | Deezer newsroom; Graphite; UMD/Pangram news study       |

Plus the **counter-evidence panel** (not an indicator; no reading), curated (Tier 3) to the standard in Sec. 4.6.

### Indicator notes
- **E1 Labor share of income:** Show full 1947– history. AI link *weak*: the decline predates generative AI by about 20 years. Lagging. Alternative explanation: the relational-sector argument (Sec. 4.6). Latest: 52.8% (2026Q2), series low (verify before publishing).
- **E2 Firm AI adoption:** Series break 17 Nov 2025: the question broadened from "in producing goods or services" to "in any of its business functions"; the AI term and the examples did not change. Annotate; do not splice silently. Show BTOS standard errors. Name the measure (firm-weighted) everywhere. Leading. *(Revision 3, owner decisions:)*
  - **Why firm-weighted** is explained on the page: (1) the BTOS national estimate is firm-weighted, the official free biweekly series with standard errors that can be tracked automatically; measures weighted by employment, or drawn from other surveys, report substantially higher adoption (cited qualitatively from a Federal Reserve Board note; no specific figure is quoted because its weighting is described inconsistently across sources); (2) firm-weighting measures breadth across separate businesses, which fits the Adoption row; (3) limitation: it understates how many workers encounter AI, because larger firms adopt more.
  - **By firm size view:** Census publishes the same estimate for seven employment size classes from the November 2025 question onward (series `btos_ai_use_by_size`).
  - **19 October 2026 wording:** from that collection the question says "Super Intelligence or SI (formerly referred to as Artificial Intelligence or AI)" (Census cites Executive Order 14434). Respondents saw the new wording. In that first period "Do not know" rose from 9.6 to 13.9 percent and "No" fell, while "Yes" was essentially unchanged (24.6 to 24.2 percent) and the standard error rose (0.27 to 0.61); the same period started a new questionnaire version. It is **not a series break**; it is a labeled chart marker, to be revisited at Stage 2 once more periods are published. "Do not know" ranged 9.1–11.2 percent from November 2025 through mid-October 2026. Neutral tone.
- **E3 How AI is used: automation vs. augmentation:** *(Owner decision 2026-11-12.)* The only free public data on *how* AI is used — the share of tasks handed over entirely (automation) vs. done together (augmentation), among conversations **categorized** into one of five patterns *(Revision 3: "categorized", not "classified")*; the nearest public proxy for Kulveit's suggested metric, the fraction of major corporate decisions made primarily by AI systems, but **not** that measure. Placed in the Adoption row as how much of the work is handed to AI. Caveats stated prominently on the page: **one vendor, one product** (Claude; users are not a representative sample of AI users; "a minority of AI use" removed in Revision 3 for lack of a primary source); first release window December 2024 – January 2025 (confirmed); a rising automation share may reflect Anthropic's own product changes (e.g., agentic tools) rather than society delegating more; releases are irregular and schemas change, so releases are harmonized and changes documented; no pre-AI baseline exists. **Conflict-of-interest disclosure:** the data is published by Anthropic, and the site is built with assistance from Claude. Leading.
- **G1 Labor-based share of tax revenue:** *(Corrected 2026-11-17 from verified data; earlier wording said "rising".)* The OECD average has not fallen (48.5% in 2010, peak 50.5% in 2020, 49.2% in 2023). The US quarterly series, which drives the reading, fell from an average of 66.9% in 2022 to 63.2% in 2026Q2 but remains inside its 2010–19 range (62.3–66.9%). Overall the evidence does not currently point toward disempowerment; the US decline is worth watching. Show it prominently; it's the most direct public measure of the state-dependence argument. Alternative explanation: rentier co-optation (Sec. 4.6); the page also cites *The Intelligence Curse* (Drago & Laine 2025). The OECD share is slightly above its 2010 level (it dipped below in some years). OECD data lag two to three years (OECD average to 2023, US to 2024). Lagging.
- **C1 Human knowledge-commons activity:** Recompute counts from the APIs; don't cite press figures (they conflict). Stack Overflow's yearly question count peaked in 2016 and began falling in 2017, rose briefly in 2020, then fell more steeply from 2021–22 *(corrected 2026-11-17 from verified data; earlier wording said the decline began about 2020)* — show that. **Comparison group:** a set of non-programming Stack Exchange sites, chosen by criteria written in advance (e.g., long history, high volume, low expected AI substitutability) and fixed before results are viewed; the Stack Overflow vs. comparison-site comparison addresses the pre-ChatGPT decline. Caveat: AI affects the comparison sites too, so the measure is *relative* change. Annotate Wikimedia's bot-reclassification break (the improved classification exists only from March 2025; earlier months were not reprocessed). Identify the client with a User-Agent as Wikimedia requires; respect rate limits. Alternative explanation for Wikipedia: people reading its content through AI (Sec. 4.6). Leading.
  - *(Revision 3, owner decisions.)* **Only four comparison sites** (Home Improvement, Travel, Role-playing Games, Science Fiction & Fantasy), approved 2026-11-17.
  - **Main measure: a relative-activity index** — Stack Overflow's 12-month question total relative to the geometric mean of the four comparison sites' 12-month totals, 2019 average = 100 (`so_relative_index`, from June 2012). Second headline: **change since November 2022** (`so_change_since_chatgpt`). A **leave-one-out band** (`so_relative_index_loo_min/max`) shows the range when each comparison site is dropped in turn. The year-over-year gap (`so_vs_comparison_yoy`) is kept as an alternative view. The page calls it a relative-activity index, **not a causal estimate**: Stack Overflow diverged from the comparison sites before ChatGPT.
  - **Chart markers:** Copilot technical preview 29 June 2021; Copilot general availability 21 June 2022; ChatGPT 30 November 2022; Stack Overflow's ban on AI-generated answers 5 December 2022; moderator strike 5 June 2023. Copilot shows that "before AI" is not clean for programmers.
  - **Deletion caveat:** counts exclude deleted questions; deletion rates differ by site and accumulate with age, so older months are undercounted; the effect on the index is unknown and likely understates Stack Overflow's decline. Every download is archived so deletions can be measured later.
  - Stage 2 and later items are in Sec. 8.1.
- **E4 Wealth concentration (Release 2):** Concentrated wealth converts into political and cultural influence (Kulveit's "wealth distribution" metric). AI link *weak*: concentration has risen since the 1980s for many reasons; DFA data begin 1989. Lock-in placement depends on the lock-in definition (Sec. 4.1). The page notes that the AI-specific version — the share of top fortunes tied to AI companies — is planned (Sec. 8).
- **G2 Federal AI use cases (Release 2):** Self-reported; definitions change between years ("rights/safety-impacting" → "high-impact"); 2024 baseline conflicts (1,757 press vs 2,133 repo) — document the choice. **Defense and intelligence AI uses are largely excluded — critical caveat** *(owner emphasis)*: stated in the headline area, in the "what it doesn't show" box, and in the chart title ("Civilian federal AI use cases"). Pair with agency workforce trend only as context (2025 cuts were policy-driven, not AI). Official source: github.com/ombegov.
- **G3 AI-interest political influence (Release 2):** Framed as "AI-interest political influence". Most big-tech lobbying is not about AI, so report **both** (a) spending by a maintained, versioned list of AI companies (inclusion criteria and change log) and (b) filings whose LDA issue text mentions AI. LDA migrated from lda.senate.gov in mid-2026 — confirm API access and key rules before building. Lock-in placement depends on the lock-in definition.
- **C2 Production vs. consumption (Release 2):** Curated pairs of points with citations, refreshed by hand; reading by owner judgment only, never computed bands. Name source conflicts: Graphite and Pangram sell AI detectors (Pangram co-authored the UMD news study); state each detector's published false-positive rate or that none is published, and note the vendor interest in "What it doesn't show". It illustrates the key cultural distinction: AI saturates *production* (about 50% of new web articles; >50% of Deezer uploads) while *consumption* stays mostly human (1–3% of Deezer streams).

All latest figures above come from the research report (private research folder) and must be re-checked against primary sources before publication; figures marked secondary there must not be published unverified.

## 6. Pages

1. **Summary (home):** scorecard grid with current readings, magnitudes and AI link ratings; the cross-cutting oversight row; "what the data is telling us" statement (owner-written, dated); a quarter-by-quarter view of how readings have changed since Q4 2022 (retrospective clearly labeled); counter-evidence panel; links to each indicator; link to the **Archive**.
2. **Indicator page** (one fixed template):
   - Headline: current reading in the three-line form (Sec. 4.2), date, leading/lagging label, one-sentence summary (front matter `summary:`, renamed from `takeaway:` in Revision 3).
   - **Summary table at the top** *(Revision 3)*: warning sign, data sources (name and link), calculation (one or two plain sentences), coverage (geography · frequency · first date), from front matter `warning_sign`, `data_sources` (list of name/url), `calculation`, `coverage`; plus current reading, grid row, AI link, leading/lagging and "data through", filled automatically from config and data.
   - "Why this matters for gradual disempowerment".
   - Interactive chart: timeframe selection; alternate views where meaningful (e.g., level vs. deviation from 2010–19 trend; comparison group; firm-size cuts); uncertainty bands where published.
   - Reading history (timeline of readings with rationales).
   - "What it shows / what it doesn't show" box.
   - "What would change our reading", with sub-headings "Warning sign" and "Alternative explanations" (and optionally "What would raise or lower our confidence").
   - **"Data and calculation"** *(Revision 3)*: source and series, units, frequency, date range, and the formula in plain words.
   - Method: comparison type, baseline, window rule, threshold rule and resulting bands, sensitivity table, AI link scores on the four criteria, data source(s) with links, license, last fetched, series breaks, caveats.
   - Download the data (CSV).
3. **Methodology:** the framework (rows inspired by Chooi et al., with a crosswalk table; releases and stages defined; the lock-in definition or its absence; the oversight row; scales; AI link rubric; comparisons; uncertainty), the frozen threshold rule and revision log, retrospective method, sensitivity approach, critiques the site takes seriously (Krueger, Millidge, Jedlicka, the authors' own caveats), the "diagnostics, not targets" statement, the named cultural gap, and what's planned for later.
4. **Archive:** all earlier retrospective snapshots, past "what the data is telling us" statements, and superseded threshold rules, each dated. Linked from the summary and every indicator page.
5. **About:** purpose, author, how to cite, how to report errors (GitHub issues), and the disclosure that the site is built with assistance from Claude (Anthropic).

## 7. Architecture

```
Public sources ──► Python fetch scripts ──► data/ (tidy CSV + metadata) ──► Quarto site ──► GitHub Pages
                  (GitHub Actions, scheduled)       ▲
                                     readings file (owner-reviewed) ┘
```

- **Site:** Quarto (actively maintained; v1.11.x as of Oct 2026). Interactive charts via Quarto's built-in Observable JS (Observable Plot + Inputs) or Plotly — builder's choice, applied consistently.
- **Data scripts:** Python, one per indicator source, **independent of the site generator**. Each writes tidy CSV plus metadata (source URL, license, fetched-at timestamp, data vintage, series-break notes, standard errors where published) into a data folder the site reads. Switching site tools later should only mean rewriting page templates.
- **Readings:** a human-edited, version-controlled file of dated readings and rationales. Scripts may write *proposed* readings; only owner-confirmed ones are published as current.
- **Automation:** a scheduled GitHub Actions workflow runs the fetch scripts, commits changed data, rebuilds and deploys. Scheduled workflows in public repos stop after 60 days without repo activity — data commits keep it alive; the builder should confirm.
- **Health checks:** each source has a check that fails loudly in CI and shows a "stale since [date]" badge on the affected page instead of silently serving old data.
- **GitHub Pages base path:** project site at `richardsonlj12.github.io/disempowerment-indicators/`; configure links accordingly.
- **Local preview:** the owner can preview the site locally before pushing (GitHub Pages has no per-change previews).

## 7a. Releases and stages

Two dimensions: **releases** decide *which indicators* are on the site; **stages** decide *how far* each release has gone through the review gates.

**Releases** *(owner decision 2026-11-12)*
- **Release 1:** E1, E2, E3, G1, C1 (with the Stack Exchange comparison group), the oversight row ("no public measure yet"), and the counter-evidence panel. Every domain has an indicator; the lock-in row reads "no public measure yet".
- **Release 2:** E4, G2, G3, C2; the E1 comparison by industry (Sec. 8); and the lock-in definition (Sec. 4.1), which must be settled before E4 or G3 are placed in that row.

**Stages** (each release passes through all three; a Release 2 indicator goes through them on its own when added)
1. **Stage 1 — data site.** Indicator pages with live data, interactive charts, "why this matters", method, sources and caveats. Readings show **"Not yet reviewed"**. Summary page shows the grid structure with indicators placed but unread, plus the counter-evidence panel. Every published figure verified (Sec. 7b) before deploy.
2. **Stage 2 — threshold rule.** Draft the mechanical rule per comparison type and the window rule per indicator; compute the sensitivity table; draft AI link scores; owner reviews and **freezes** them (dated).
3. **Stage 3 — readings.** Compute current proposals and the retrospective; owner reviews as a set; publish confirmed current readings, the retrospective snapshot, reading histories, and the "what the data is telling us" statement.

## 7b. Review procedures *(owner requirement; specifics are Claude's proposal, approved 2026-11-12)*

Nothing reaches the public site without passing the relevant checks. Procedures are written down in the repo (a `REVIEW.md` checklist) so they're repeatable.

**Automated checks (run in CI on every change and scheduled refresh; a failure blocks deploy):**
- Fetch health: each source responded, returned the expected columns/units, and data isn't older than its expected update lag (otherwise "stale since" badge).
- Sanity checks per series: values within plausible ranges, no unexpected gaps or duplicate dates, series breaks annotated.
- **Spot-check against published figures:** for each indicator, at least one known value from the primary source (e.g., BLS's published 52.8% for 2026Q2) is asserted in a test, so a broken calculation is caught.
- Site builds without errors; links and downloads work.

**Human review gates (owner):**
- **Source reading** before the methodology page is written: the full Chooi, Lee & Li (2026) paper and the RAND report (Moon & Boudreaux 2026) are read from the original; Herdağdelen, Joren & Tamkin (2026) and Imas and Schaal's work are checked before being cited.
- **Figure verification** before Stage 1 deploy and whenever text cites a new number: every figure in prose traced to its primary source, with link; secondary-only figures are not published.
- **Indicator page review** before first publication of each page: reasoning, caveats, AI link, warning sign and alternative explanations, "what it doesn't show".
- **Threshold-rule freeze** (Stage 2): rule, windows and sensitivity table reviewed and dated.
- **Readings review**: retrospective as a set (Stage 3); current readings quarterly and on automation-opened issues.

**Independent second check:** before each stage goes live, a fresh AI reviewer with no access to our conversation reads the pages, method and code and tries to find errors, overclaims and one-sided framing (acting as a skeptical AI-safety researcher). Its findings are triaged by the owner before release.

**Corrections policy:** errors found after publication are fixed openly with a dated correction note on the affected page; the public can report errors via GitHub issues.

## 8. Later versions

Recorded so they are planned, not lost. Release 2 indicators are in Sec. 5 and 7a.

**8.1 Method**
- **First-published ("as of then") comparison** for FRED-covered economic series using **ALFRED** vintages: show what the reading would have been with data as first released vs. latest revised, and where they disagree.
- **E1 comparison by industry** (Release 2): labor share in more vs. less AI-exposed industries, from BEA GDP-by-industry compensation and value added, with industry exposure weights (e.g., Felten AIOE by industry).
- **G1 US-states rentier analog:** states heavily dependent on severance taxes (e.g., WV, WY, AK, ND) vs. others, from the Census Annual Survey of State Government Tax Collections.
- **Measuring deferral:** if a public, repeatable measure of human deferral to AI appears, it fills the oversight row.
- **C1, Stage 2** *(Revision 3)*: a placebo "normal divergence" range (how far sites drift apart for ordinary reasons); thresholds applied to calendar-year values of the index; a test of whether the index's slope changed after late 2022.
- **C1, later** *(Revision 3)*: an event study around the marked dates; a wider comparison pool; a correction for deleted questions using the archived downloads.

**8.2 Harder indicators from the recommended ten**
- **Young workers in AI-exposed jobs** — Stanford "Canaries" figures (curated) plus an open proxy from CPS microdata (IPUMS or Census API) pooled 6–12 months, exposure quintiles from Eloundou et al. or Felten AIOE, ages 22–25 vs 35–49; label as a rough proxy with wide uncertainty. Latest Stanford figure: about 19% below benchmark (cumulative since late 2022, June 2026 data).
- **Job postings weighted by AI exposure** — Indeed Hiring Lab postings by sector (GitHub, CC BY 4.0) with a hand-built Indeed-sector → SOC crosswalk and exposure weights.
- **AI-written share of scientific papers and peer reviews** — self-computed with Liang et al.'s distributional method on arXiv abstracts and OpenReview reviews (vendor-free).

**8.3 Remaining indicators from the owner's earlier labor-dashboard draft**
- **Recent-graduate unemployment and underemployment** (NY Fed, quarterly; no API).
- **Labor force participation in AI-exposed occupations** (CPS).
- **Real wages in exposed vs non-exposed occupations** (CPS-ORG or ACS for trends; OEWS only for weights — BLS advises against OEWS time series).
- **AI capital investment share** — proxy from BEA information-processing equipment + software + data-center structures as a share of business investment (BEA has no AI category). The St. Louis Fed GDP-contribution claim remains unverified.

**8.4 Other candidates from the research**
- Economic: AI compute concentration (Epoch AI); wage–productivity gap; corporate profit share as its own indicator.
- **Income and wealth concentration, including AI-linked fortunes** *(owner interest)*. Matches Kulveit's "wealth distribution between AI-heavy and human-centric industries". Options:
  - Top 1% / 0.1% wealth share — Fed DFA — **E4, Release 2**.
  - Top income shares — World Inequality Database (free, annual, CC BY).
  - AI-linked share of top wealth (how much of the richest people's wealth is tied to AI companies) — the most AI-specific version, but the standard sources (Forbes, Bloomberg Billionaires) restrict republication; would need a hand-curated list built from public filings. Harder.
  - AI-company share of total stock-market value — the main index data is paid (S&P); a free version would need building from public filings.
- Government: AI-vendor concentration in federal procurement (USAspending API); AI-generated share of public regulatory comments (regulations.gov API); democratic voice / trust in government as labeled context (OECD Trust Survey, Pew); legislative complexity (no source researched yet — a gap in the paper's own list); AI role in legal processes and security (largely opaque).
- Cultural: **AI as information and relationship intermediary** (Pew, Reuters Digital News Report, Common Sense Media; Anthropic/OpenAI usage reports) — **the next cultural candidate**, and the likely first cultural exposure indicator; time spent socializing (BLS American Time Use Survey) as context; AI share of news and AI content farms (UMD/Pangram study, NewsGuard); search-to-publisher click-through (Pew); Wikipedia editor activity.
- Cross-cutting: international comparisons where free data allow; Kulveit Sec. 6.2 metrics with no public proxy yet (fraction of corporate decisions made by AI, unsupervised AI spending).

## 9. Left to the builder

- Exact series IDs, API endpoints and query definitions per source (verify each; several access details in the research are unconfirmed).
- Chart library (Observable Plot vs Plotly) and visual design, within: accessible, readable in light and dark mode, works on phones.
- Data file layout and metadata schema; readings file format.
- Drafts for Stage 2: the threshold rule per comparison type, window rules, sensitivity alternatives and AI link scores — all for owner review and freezing.
- The draft comparison-site selection criteria for C1, for owner review before results are viewed.
- How E3's releases are harmonized across schema changes (documented on the page).
- Refresh schedule per source (no more frequent than the source updates).
- Test approach for fetch scripts and calculations.

## 10. Calls made by Claude (owner to check)

- v1 set = the seven "simpler" indicators plus wealth concentration (added by owner 2026-11-12); C2 (production vs consumption) included although curated, because it is simple to build and carries the central cultural distinction. *(Superseded by the Release 1 / Release 2 split, Sec. 7a.)*
- Counter-evidence panel ships in v1 though it's not an indicator.
- "No signal / insufficient data" and "Not yet reviewed" added as reading states.
- C2 gets readings only by owner judgment, never computed bands.
- Scripts propose readings; owner confirms (readings file in the repo).
- Multi-series indicators: one reading, owner decides on disagreement; US data drives G1, labor share drives E1 (Sec. 4.5a).
- Quarterly review plus auto-opened GitHub issues when a proposal changes (Sec. 4.5).
- The specific review procedures in Sec. 7b (owner asked for review procedures; the details are proposed).
- Owner's private research folder and earlier draft brief stay out of the public repo; the design references them only in general terms.

*Owner reviewed Sec. 10 on 2026-11-12: approved.*

**Added after owner review (2026-11-12), approved:**
- Readings shown with magnitudes; layer questions ask "whether and how far" (Sec. 4.1).
- AI-specificity rubric: four criteria and rule of thumb (Sec. 4.2).
- Data-update behavior: no issue for routine new data; "data updated since review" flag instead; issue + "review pending" only when the proposal changes (Sec. 4.5).
- Archive page (Sec. 6).
- G2 defense/intelligence caveat placed in headline, chart title and "what it doesn't show" (Sec. 5).

## 11. Revision 2 (2026-11-12): independent review and owner decisions

An independent review of the design (kept in the owner's private research folder) made twelve recommendations and a scope note. Outcome:

**Owner decisions**
- **Anthropic Economic Index added as E3** (exposure row, one-vendor caveat, conflict-of-interest disclosure); wealth concentration renumbered **E4**.
- **Readings describe the data, not its meaning:** the baseline scale (Within / Above / Below / Far above / Far below baseline) replaces "leverage intact / eroding / lock-in signals"; the baseline is named under every reading; a separate interpretive line carries the AI-specificity badge. The exposure scale is unchanged.
- **Release 1 / Release 2 split** (Sec. 7a).

**Adopted as recommended (Claude's call, for owner check)**
- Lock-in must be operationally defined before anything is placed in that row; the layers are credited as our adaptation of Chooi et al., whose full paper is read first (Sec. 4.1).
- Direction assumption and main rival reading for each indicator (Sec. 4.2, 4.6).
- Leading/lagging label (Sec. 4.2).
- Badge renamed "AI-specificity"; "strong" for E2, E3, G2 explained as "measures AI directly" (Sec. 4.2).
- Stack Exchange comparison group for C1 in Release 1; E1 by-industry comparison in Release 2; G1 states analog later (Sec. 5, 8.1).
- Oversight row with "no public measure yet" (Sec. 4.1).
- Cultural gap named; AI-as-intermediary surveys as the next candidate (Sec. 4.6, 8.4).
- Mechanical threshold rule, frozen before bands are computed, plus a sensitivity table; window-change comparison preferred over long straight-line extrapolation (Sec. 4.4).
- Uncertainty bands and seasonality handling; moves inside noise never cross a threshold (Sec. 4.3).
- G3 reframed as "AI-interest political influence", classified by company list and by filing issue text (Sec. 5).
- C2 detector-vendor conflicts and false-positive rates named (Sec. 5).
- Counter-evidence panel held to the indicators' standard, including welfare-improving signals (Sec. 4.6).
- "Diagnostics, not targets" statement (Sec. 4.6).
- Disclosure that the site is built with assistance from Claude (Sec. 3, 6).

**Open for the owner**
- The lock-in definition (before Release 2).
- The exact threshold rule (Stage 2).

## 11a. Revision 3 (2026-11-17): owner review of the Stage 1 prose

The owner reviewed the Release 1 pages and methodology on 2026-11-17, with a jargon review and an independent figure check. Owner decisions:

- **Row names:** Exposure → **Adoption**; Erosion → **Displacement**; Lock-in unchanged (fallback name "Concentration of influence" if no lock-in test is adopted). The methodology page gets a crosswalk table to Chooi, Lee & Li and credits them as the inspiration (Sec. 4.1). Internal keys are unchanged.
- **Badge:** "AI-specificity" → **AI link** (strong / moderate / weak); each page explains that "strong" means the series measures AI directly, not strong evidence of harm (Sec. 4.2).
- **Page vocabulary:** "direction assumption" → **Warning sign**; "main rival reading" → **Alternative explanations** (Sec. 4.2, 4.6); "augmentation versus displacement" → **augmentation versus replacement** (Sec. 4.6); front matter `takeaway:` → `summary:`.
- **Counter-evidence:** welfare signals removed (welfare is not agency); the panel holds policy pushback and data moving against the mechanism. The AI legislation item is verified and published (Sec. 4.6).
- **Indicator pages:** a summary table at the top and a new "Data and calculation" section (Sec. 6).
- **Plain language:** Stage and Release defined once on the methodology page; "structural" → long-running series; "AI-native" → measures AI use directly; "frozen rule" → rule fixed in advance and dated; "the project owner" → the author (Jeremy Richardson); "leverage" defined once; "baseline" and "retrospective" kept, with a gloss; no raw series IDs in page prose; standard closing line on every page.
- **C1:** relative-activity index as the main measure, with change since November 2022, a leave-one-out band, the year-over-year gap as an alternative view, five chart markers, the deletion caveat and download archive; only four comparison sites (Sec. 5; Stage 2 and later items in Sec. 8.1).
- **E2:** firm-weighted rationale and the by-firm-size view; the 19 October 2026 "Super Intelligence or SI" wording is a labeled chart marker, **not a series break**, to be revisited at Stage 2; dates of the 17 November 2025 change corrected (Sec. 5).
- **E3:** "categorized", not "classified"; the Kulveit metric paraphrased correctly; the unsourced "minority of AI use" claim removed (Sec. 5).
- **G1:** cites *The Intelligence Curse*; OECD lag "two to three years"; OECD share "slightly above its 2010 level" (Sec. 5).
- **BTOS revisit rule:** the 19 October 2026 wording marker is converted to a series break only if the "Yes" share shows a level jump after 2 to 3 more periods.
- **Median income:** may appear only as context, not as counter-evidence.
- **Internal keys vs public terms:** "structural", "ai_native", "exposure", "erosion", "lockin", "baseline scale" and similar remain as internal keys in code and config; public text (pages, methodology, chart labels) uses the new terms.
- **Single source of truth for page prose:** each indicator's summary, warning sign and alternative explanations live only in `content/indicators/[ID].md` (front matter and sub-headings); `config/indicators.yaml` no longer carries `summary`, `warning_sign` or `alternative_explanations`.
- **Oversight row name:** stays "Human deferral and oversight" everywhere (methodology, `config/curated/oversight.yaml`, `config/indicators.yaml` `oversight.row_label`).

Sec. 10 and Sec. 11 above are kept as history; their older terms (exposure/erosion rows, AI-specificity, direction assumption, rival reading, welfare signals) describe earlier revisions.
