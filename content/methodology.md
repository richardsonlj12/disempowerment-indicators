This page explains how the site turns public data into indicators, and how it will turn indicators into readings. In Release 1, Stage 1, the site shows data only. Every indicator's reading says "Not yet reviewed," because the rules that produce readings are written and frozen in Stage 2 before any reading is made.

## The framework

The site tracks the scenario Kulveit et al. (2025) call **gradual disempowerment**. Economies, states and cultures stay roughly aligned with human interests partly because they need human participation: people's work, taxes, compliance and attention. As AI systems replace that participation, the pressure that keeps these systems serving people could weaken, with no single dramatic event.

### Layers, domains and the grid

The scorecard is a grid. Its columns are three **domains**: economic, government and cultural, following Kulveit et al. Its rows are three **layers**:

- **Exposure:** is AI entering the system, and how far?
- **Erosion:** is the system's dependence on humans falling, and by how much?
- **Lock-in:** is that dependence becoming hard to restore, and how entrenched is it?

A fourth row, **human deferral / oversight**, runs across all three domains.

**The layers are our adaptation of Chooi, Lee and Li (2026).** Their paper, "Measuring AI-Induced Disempowerment: A Framework and Proposed Metrics," proposes the exposure, erosion and lock-in sequence. We use their names, but our definitions differ, and we say where:

- **Exposure.** In the paper, exposure means AI already changing outcomes, by distorting human judgment or displacing human participation. On this site, the exposure row measures AI entering a system: how many firms use it (E2), and how deeply one product is used (E3). The paper treats adoption measures like these as useful instruments rather than direct measures of disempowerment. We agree, and the exposure row's indicators say so.
- **Erosion.** In the paper, erosion is the loss of individual capability: a person can no longer do a task without AI. On this site, the erosion row asks whether a whole system's dependence on human participation is falling. Examples are labor's share of income (E1), the share of taxes raised from workers (G1) and activity on human knowledge commons (C1). This follows Kulveit et al. more than Chooi et al., and it is the largest difference. None of the site's current indicators measures individual capability.
- **Lock-in.** In the paper, lock-in means the institutional infrastructure for human agency has been dismantled, for example a profession that no longer trains juniors. On this site, lock-in asks whether reduced dependence is becoming hard to restore. That is close to the paper's meaning. The row is empty for now (see below).

We also do not use the paper's second axis, level of analysis (individual, institutional, civilizational). Our indicators are national aggregates. The paper's own warning applies: "disempowerment" at different levels may be different things sharing a name.

**No composite score.** Each indicator gets its own reading, and cells are never averaged. Chooi, Lee and Li give reasons we share:

- How to weight indicators is not understood.
- A composite can hide a failure in one domain.

### Why the lock-in row is empty

Concentrated wealth or political influence is not by itself evidence that reduced human dependence is hard to reverse. Before anything is placed in the lock-in row, the project owner will adopt a written, operational test for lock-in. Candidate tests:

- **Persistence:** a departure from baseline that does not revert after shocks over a stated number of periods.
- **Rising switching costs:** a growing capacity of AI-interest actors to block a return to human decision making.

Both echo examples Chooi, Lee and Li give. If no test is adopted, the row will be renamed (for example, "concentration of influence") rather than overclaim. Until then, every lock-in cell reads "No public measure yet."

### The oversight row

The mechanism at the center of the gradual disempowerment argument is decisions moving from people to AI. No public time series measures this. The oversight row therefore reads "No public measure yet" and cites the only current evidence we know of: an experiment by Herdağdelen, Joren and Tamkin (2026).

**The study.** Professional analysts worked on a data analysis with an AI coding agent. On four analytical decisions, a coin flip set which way the agent leaned. Across those decisions, the 50 analysts in the study went with the agent's lean 86 percent of the time, against 50 percent by chance. Many repeated the agent's arguments when explaining their choices without crediting it.

**Its limits.** It is one experiment, in one task, with one agent, and the authors list these limits themselves. It is authored at Anthropic, which also publishes the data behind E3. It is not a time series and cannot fill the row.

Moon and Boudreaux (2026, RAND) propose a formal way to track the same mechanism: the number and makeup of the groups whose agreement decides an outcome, and whether AI is entering those groups or shaping the options they see. If a public, repeatable measure of deferral appears, it will fill this row.

## Readings

### Two scales

Exposure-row indicators (E2, E3) use the **exposure scale**: Low, Rising, Pervasive.

Erosion-row and lock-in-row indicators (E1, G1, C1) use the **baseline scale**:

- Within baseline
- Above baseline
- Below baseline
- Far above baseline
- Far below baseline

Both scales also allow "No signal / insufficient data" and "Not yet reviewed." Every reading names its baseline in the line under it, so no reader has to look it up.

### How readings will work

Every reading will appear as three lines:

1. **The reading.** What the data is doing, on the indicator's scale.
2. **The magnitude.** The number behind the reading, in the indicator's own units, naming the baseline it is measured against.
3. **The interpretation.** What the movement would mean if AI were driving it, written from the indicator's direction assumption. It always carries the AI-specificity badge.

Readings describe what the data is doing, and the third line interprets it, so a reading never implies a cause on its own.

*Illustrative example only. No such reading has been made, and the bracketed values are placeholders:*

> **E1 Labor share: Below baseline**
> [x] points below its 2010 to 2019 pattern, over the latest [n] quarters
> *If AI-driven, consistent with eroding human leverage · AI-specificity: weak*

### Readings are dated human judgments

Each reading goes through these steps:

1. A script computes a **proposed** reading from the data and the frozen rule.
2. The project owner confirms or overrides it, with a short rationale. Only confirmed readings appear as current.
3. Every reading is stored with its date, so each indicator page can show its history.

Charts update automatically. Readings change only on review.

**Review cadence.** All readings are reviewed quarterly. Between reviews, the page flags any gap between the data and the last review:

- **"Data updated since review"** when new data arrives and the proposed reading is unchanged.
- **"Review pending"** when the new data would change the reading.

### The AI-specificity badge

Every interpretation carries an **AI-specificity** badge: strong, moderate or weak. It says how confidently a movement in the series can be connected to AI rather than other causes. It is a structured judgment, not a calculation. Each indicator is scored on four criteria:

1. **Directness.** Does the series measure AI itself, or a broad outcome that AI is one cause of?
2. **Comparison group.** Is there an AI-exposed versus less-exposed contrast that holds other causes roughly constant?
3. **Timing.** Did the change begin or speed up after generative AI spread in late 2022, rather than continue an earlier trend?
4. **Known confounders.** How many documented non-AI causes could produce the same movement, and are any of them addressed?

The rule of thumb:

- **Strong:** a direct measure of AI, or a comparison group plus timing that fits.
- **Moderate:** timing fits and there is a plausible mechanism, but no comparison group, or confounders only partly addressed.
- **Weak:** the trend predates generative AI, or major confounders are unaddressed.

"Strong" for an indicator that measures AI directly (E2, E3) means only that. It does not mean the indicator shows disempowerment. The current badges are drafts. They will be reviewed in Stage 2, and any later change will be logged on this page.

## Comparisons

### Two kinds of baseline

**Slow structural indicators** (E1, G1, C1) have decades of history and many causes. Their baseline is the series' own **pattern in 2010 to 2019**, after the 2008 to 2009 recession and before COVID. The question is whether the series is departing from that pattern, and how fast.

**AI-native indicators** (E2, E3) began recently, near zero, and change month to month. Their baseline is their **own recent path**: level, rate of change and whether that rate is speeding up, over rolling 3-, 6- and 12-month windows, or at the native frequency where data are less frequent.

### Comparison groups

A comparison group can separate an AI-related change from other causes. C1 has one. Stack Overflow is compared with four non-programming Stack Exchange sites, chosen under criteria fixed before any post-2019 counts were viewed. Because AI affects the comparison sites too, the contrast measures relative change and likely understates any AI effect.

**Planned for Stage 2:** a leave-one-out robustness check. The C1 contrast will be recomputed four times, each time leaving out one comparison site, to show whether the result depends on any single site.

E1 will gain an industry comparison in Release 2: labor share in more versus less AI-exposed industries.

### Uncertainty and seasonality

- Where a source publishes standard errors (Census BTOS, for E2), the chart shows them as bands. The threshold rule will use them.
- Monthly series with seasonal patterns (Stack Exchange, Wikipedia) are compared year over year.
- A move inside a series' normal noise never counts as crossing a threshold.

### Breaks and revisions

- **Series breaks.** When a source changes its definition or method, the chart marks the date and the series is not spliced silently. Examples: the change to the Census AI question on 17 November 2025 (E2), Wikimedia's bot reclassification in 2025 (C1), and changes in the Anthropic Economic Index release format (E3).
- **Revisions.** Official statistics are revised. The site uses the latest revised data. A revision that would change a reading is treated like new data and goes to review.

## Thresholds and the retrospective (coming in Stages 2 and 3)

**Rule first.** In Stage 2, a mechanical rule for each kind of comparison will be written, reviewed and frozen with a recorded date. The bands for each indicator then fall out of the rule. They are not hand-picked after looking at the data. The project owner and the builder have already seen the 2023 to 2026 data, so freezing hand-picked thresholds would not be enough. This works like pre-registering a study.

**The candidate rule for structural series** compares the change over an indicator's window with the spread of same-length changes in 2010 to 2019:

| Change over the window, against the 2010 to 2019 spread | Reading |
|---|---|
| Within one standard deviation | Within baseline |
| Between one and two standard deviations | Above or below baseline |
| Beyond two standard deviations | Far above or far below baseline |

A matching rule will be written for the exposure scale. The exact rules are a Stage 2 decision.

**Windows are part of the rule.** The window (for example, "change over the latest four quarters") can flip a reading on its own, so it is fixed per indicator when the rule is frozen.

**Sensitivity.** Each indicator page will show what the reading would be under reasonable alternatives:

- other windows
- another baseline period, such as 2015 to 2019
- narrower and wider bands

Where a reading flips under a reasonable alternative, the page will say so.

**Revision log.** Any change to a frozen rule will be logged here, with the date and the reason.

**Retrospective.** In Stage 3, the frozen rule will be applied once to every quarter from the **fourth quarter of 2022**, when ChatGPT was released, to the present, using the latest revised data. The project owner reviews the results as a set. The retrospective will then be published as a dated snapshot ("computed [date], rule frozen [date], data as of [date]"). It does not recompute when data are revised. A re-run is a deliberate decision that produces a new snapshot, and earlier snapshots stay on the Archive page.

## Standing guards against one-sided reading

### The counter-evidence panel

The summary page carries a panel of signals pointing away from disempowerment, held to the same standard as the indicators. The inclusion criteria were written before any items were added. An item is included only if it meets all four:

1. **Primary source.** It comes from a primary source (the statistical agency, legislature or authors who produced the figure), which we opened and checked, with a link.
2. **Dated.** It is dated, with the period it covers stated.
3. **Measured.** It is a measured value or a counted event, not an opinion or a press paraphrase.
4. **Points away.** It points away from disempowerment in one of three ways:
   - a welfare signal: people materially better off
   - a policy pushback: governments or institutions acting to keep human control
   - a data signal that moves against the hypothesized mechanism

**Items stay.** Items are not removed because they are small or later reverse. An item whose figure cannot be verified stays in the project's records, marked unverified with the reason, and is not published.

**No AI attribution.** Inclusion says nothing about whether AI caused the signal.

### Direction assumptions and rival readings

Every indicator page states two things:

- **Its direction assumption:** which way a movement would be consistent with eroding human leverage.
- **Its main rival reading:** the most plausible way the same data could arise without disempowerment.

Each indicator shows conditions under which the hypothesized mechanism would operate. None of them is proof that disempowerment is happening.

### Welfare and influence are different things

People can be better off materially while losing influence, and the reverse. Chooi, Lee and Li make the same distinction between well-being and agency. Every economic page notes it. A rising real income is a welfare signal and appears in the counter-evidence panel. It is not evidence that leverage is intact.

### Diagnostics, not targets

These indicators are diagnostics. The site does not recommend that any policy aim to move one of these numbers. A measure that becomes a target loses its value as a signal (Goodhart's law). Chooi, Lee and Li give the same warning about disempowerment metrics.

### The cultural gap

C1 measures activity on knowledge sites. It does not measure human capacity, attention or reliance on AI. The cultural column has no exposure indicator yet, and its erosion indicator counts activity, which is several steps removed from people's capacity to shape their culture.

The next candidate is survey data on AI as an intermediary for information and relationships, such as Pew Research Center surveys and the Reuters Institute Digital News Report.

## Critiques we take seriously

**David Krueger (2025)**, a coauthor of the gradual disempowerment paper, warns that many proposed metrics do not separate empowering uses of AI from disempowering ones. Heavy AI use can look like progress while people lose real agency. The site responds in three ways:

- It keeps exposure (E2, E3) apart from erosion.
- It adds an augmentation-versus-displacement note wherever adoption is shown.
- It names deferral, the thing Krueger suggests testing, as the row with no public measure.

**Beren Millidge (2025)** argues that gradual disempowerment might not be so bad. Most people already have little individual influence over large systems. AI governance could be better than human governance. Capital income and transfers could sustain living standards. He calls the outcome highly uncertain. His argument is why every economic page separates welfare from influence, and why the counter-evidence panel includes welfare signals.

**P. O. Jedlicka (2026)** argues that gradual disempowerment scenarios are under-specified sociologically and lean on technological determinism. In his view they underrate collective agency and social conflict: people organize, push back and change the rules as a technology spreads. This is the main reason the site shows signals pointing the other way with equal prominence, including policy pushback.

**The authors' own caveats.**

- Kulveit et al. concede that some outcomes of the scenario are ambiguous. For example, an AI-run state could bring large benefits.
- Chooi, Lee and Li say causal attribution is hard throughout, that most metrics in this area can only describe and compare, and that leading indicators are hard to validate before the outcomes they predict have happened.

The site's indicators are descriptive in exactly this sense.

## What comes later

**Release 2** adds four indicators:

- **Wealth concentration (E4).**
- **Federal AI use cases (G2).**
- **AI-interest political influence (G3).**
- **AI's share of cultural production versus consumption (C2).**

E4 and G3 are placed in the lock-in row only if a lock-in test is adopted.

Later versions are planned under four headings:

- **Method.**
  - Readings computed with data as first published, alongside revised data (ALFRED vintages).
  - The E1 industry comparison.
  - A US-states test of the rentier logic for G1.
  - A measure of deferral for the oversight row, if one becomes available.
- **Harder indicators from the recommended ten.**
  - Young workers in AI-exposed jobs.
  - Job postings weighted by AI exposure.
  - The AI-written share of scientific papers and peer reviews.
- **Remaining indicators from the owner's earlier labor-dashboard draft.**
  - Recent-graduate unemployment.
  - Participation in AI-exposed occupations.
  - Real wages in exposed versus less-exposed occupations.
  - An AI capital-investment share.
- **Other candidates from the research.** These include:
  - AI as an information and relationship intermediary, the next cultural candidate.
  - Income and wealth concentration tied to AI companies.
  - AI-vendor concentration in federal procurement.
  - AI-generated public regulatory comments.
  - International comparisons where free data allow.

## Sources and disclosure

The full papers behind the framework were read before this page was written:

- Chooi, Lee and Li (2026)
- Moon and Boudreaux (2026)
- Herdağdelen, Joren and Tamkin (2026)
- Imas (2026)

Every figure on the site is checked against its primary source before publication.

This site is built with assistance from Claude (Anthropic). One indicator (E3) uses data published by Anthropic, and the oversight row cites research authored at Anthropic.
