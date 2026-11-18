This page explains how the site turns public data into indicators, and how it will turn indicators into readings. A **reading** is the site's label for what an indicator's data is doing, such as "Rising" or "Within baseline." For now the site shows data only. Every indicator's reading says "Not yet reviewed," because readings start once the rules that produce them are fixed in advance and dated (see "Releases and stages" below).

## The framework

The site tracks the scenario that Kulveit et al. (2025) call **gradual disempowerment** ([Kulveit et al., "Gradual Disempowerment," arXiv 2501.16946](https://arxiv.org/abs/2501.16946)). Economies, states and cultures stay roughly aligned with human interests partly because they need human participation: people's work, taxes, compliance and attention. As AI systems replace that participation, the incentive for firms and governments to serve people could weaken gradually, with no single dramatic event. The site's author has written a short introduction to the argument ([Richardson, "No Robot Uprising Required"](https://richardsonlj.substack.com/p/no-robot-uprising-required)).

The site uses one word for this throughout: **leverage**, the bargaining power people have because systems need their work, taxes or attention.

These indicators show whether the conditions for disempowerment are present. They do not show that it is happening.

### Releases and stages

The site is built in steps. **Releases** decide which indicators are on the site. **Stages** decide how far each release has gone.

**Releases.**

- **Release 1 (now):** labor share of income (E1), firm AI adoption (E2), how AI is used (E3), the labor-based share of tax revenue (G1), human knowledge-commons activity (C1), the oversight row and the counter-evidence panel.
- **Release 2:** wealth concentration (E4), federal AI use cases (G2), AI-interest political influence (G3), AI's share of cultural production versus consumption (C2), and a written definition of lock-in.

**Stages.** Each release goes through three stages.

1. **Stage 1, the data site (now).** Charts, sources and explanations, with every reading shown as "Not yet reviewed."
2. **Stage 2, the threshold rule.** A mechanical rule for turning data into readings is written, reviewed, fixed in advance and dated, before any reading is made. This works like pre-registering a study.
3. **Stage 3, readings and the retrospective.** The fixed rule produces current readings. It is also applied once to every quarter since late 2022, and the result is published as a dated **retrospective**: a look back at how the readings would have changed since ChatGPT's release.

### Rows, domains and the grid

The scorecard is a grid. Its columns are three **domains**: economic, government and cultural, following Kulveit et al. Its rows are three **layers**:

- **Adoption:** is AI entering the system, and how far?
- **Displacement:** is the system's dependence on human participation falling, and by how much?
- **Lock-in:** is that dependence becoming hard to restore, and how entrenched is it?

A fourth row, **human deferral and oversight**, runs across all three domains. It asks whether people are deferring to AI's judgment.

**The rows are inspired by Chooi, Lee and Li (2026).** Their paper, ["Measuring AI-Induced Disempowerment: A Framework and Proposed Metrics"](https://aclanthology.org/2026.evaleval-1.36/), proposes three layers that they call exposure, erosion and lock-in. Our grid owes its structure to theirs, but our rows ask different questions, so we use different names for the first two. The table shows how they line up.

| This site's row | Chooi, Lee and Li's term | How they relate |
|---|---|---|
| **Adoption:** AI entering a system (E2, E3) | Adoption measures, which they treat as outside their three layers | The paper says adoption measures like these are not direct measures of disempowerment but "might serve as instrumental indicators" of it. We agree, and the adoption row's pages say so. |
| **Displacement:** a whole system depending less on human participation (E1, G1, C1) | **Exposure:** AI already changing outcomes, by distorting human judgment or displacing human participation | Our row covers the displacement half of their exposure layer, measured for whole economies, states and knowledge communities. This follows Kulveit et al. The paper treats displacement alone, without erosion or lock-in, as adaptation rather than disempowerment. |
| Not measured | **Erosion:** individuals losing the ability to do a task without AI | None of the site's indicators measures individual capability. This is the largest gap between the site and the paper. |
| **Lock-in:** reduced dependence becoming hard to restore (empty for now) | **Lock-in:** the institutional infrastructure for human agency dismantled, for example a profession that no longer trains juniors | Close to the paper's meaning. |

We also do not use the paper's second axis, level of analysis (individual, institutional, civilizational). Our indicators are national totals. The paper's own warning applies: "disempowerment" at different levels may be different things sharing a name.

**No composite score.** Each indicator gets its own reading, and cells are never averaged. Chooi, Lee and Li give reasons we share:

- How to weight indicators is not understood.
- A composite can hide a failure in one domain.

### Why the lock-in row is empty

Concentrated wealth or political influence is not by itself evidence that reduced human dependence is hard to reverse. Before anything is placed in the lock-in row, the author will adopt a written, operational test for lock-in. Candidate tests:

- **Persistence:** a departure from baseline that does not reverse after shocks over a stated number of periods.
- **Rising switching costs:** a growing capacity of groups that profit from AI to block a return to human decision making.

Rising switching costs is one of the lock-in signs Chooi, Lee and Li list. Persistence is the site's own proposal. If no test is adopted, the row will be renamed "Concentration of influence" rather than overclaim. Until then, every lock-in cell reads "No public measure yet."

### The oversight row

The mechanism at the center of the gradual disempowerment argument is decisions moving from people to AI. No public time series measures this. The oversight row therefore reads "No public measure yet" and cites the only current evidence we know of: an experiment by Herdağdelen, Joren and Tamkin (2026), ["How AI agents shape experts' judgment calls"](https://www.anthropic.com/research/agents-judgment-calls).

**The study.** Professional analysts worked on a data analysis with an AI coding agent. On four analytical decisions, a coin flip set which option the agent was set to favor. Across those decisions, the 50 analysts in the study went with the agent's favored option 86 percent of the time, against 50 percent by chance. Many repeated the agent's arguments when explaining their choices without crediting it.

**Its limits.** It is one experiment, in one task, with one agent, and the authors list these limits themselves. The agent in the study was Claude. The study is authored at Anthropic, which also publishes the data behind E3 and makes Claude. It is not a time series and cannot fill the row.

Moon and Boudreaux (2026, RAND Corporation) propose a formal way to track the same mechanism in ["A Formal Model of How Artificial Intelligence Erodes Human Agency"](https://www.rand.org/pubs/research_reports/RRA4817-1.html): the number and makeup of the groups whose agreement decides an outcome, and whether AI is entering those groups or shaping the options they see. If a public, repeatable measure of deferral appears, it will fill this row.

## Readings

### Leading and lagging

Each indicator is labeled **leading** or **lagging**. A leading indicator is likely to move early, before any effect is entrenched; adoption and activity measures are examples. A lagging indicator is likely to move only after a change is well under way; income and tax shares are examples. Most long-running series lag.

### Two sets of labels

Adoption-row indicators (E2 and E3) use three labels: **Low, Rising, Pervasive**.

Displacement-row and lock-in-row indicators (E1, G1 and C1) use five labels, each measured against a baseline:

- Within baseline
- Above baseline
- Below baseline
- Far above baseline
- Far below baseline

Both sets also allow "No signal / insufficient data" and "Not yet reviewed." Every reading names its baseline in the line under it. "Above" and "below" describe direction only. Whether a move is a warning sign depends on the indicator, and each page says which way counts.

### How readings will work

Every reading will appear as three lines:

1. **The reading.** What the data is doing, using the labels above.
2. **The magnitude.** The number behind the reading, in the indicator's own units, naming the baseline it is measured against.
3. **The interpretation.** What the movement would mean if AI were driving it, written from the indicator's warning sign. It always carries the AI link rating.

A reading says what the data did. It does not say why.

*Illustrative example only. No such reading has been made, and the bracketed values are placeholders:*

> **E1 Labor share: Below baseline**
>
> [x] points below its 2010 to 2019 baseline, over the latest [n] quarters
>
> *If AI-driven, consistent with workers losing leverage · AI link: weak*

### Readings are dated human judgments

Each reading goes through these steps:

1. A script computes a **proposed** reading from the data and the rule fixed in advance.
2. Jeremy Richardson, the site's author, confirms or overrides it, with a short rationale. Only confirmed readings appear as current.
3. Every reading is stored with its date, so each indicator page can show its history.

Charts update automatically. Readings change only on review.

**Review cadence.** All readings are reviewed quarterly. Between reviews, the page flags any gap between the data and the last review:

- **"Data updated since review"** when new data arrives and the proposed reading is unchanged.
- **"Review pending"** when the new data would change the reading.

### The AI link rating

Every interpretation carries an **AI link** rating: strong, moderate or weak. It says how clearly a movement in the series can be connected to AI rather than to other causes. It is a judgment made against four written criteria:

1. **Does it measure AI itself?** Or does it measure a broad outcome that AI is one cause of?
2. **Is there a comparison group?** That is, a less AI-exposed group that holds other causes roughly constant.
3. **Does the timing fit?** Did the change begin or speed up after generative AI spread in late 2022, rather than continue an earlier trend?
4. **Other possible causes.** How many documented causes other than AI (confounders) could produce the same movement, and are any of them addressed?

The rule of thumb:

- **Strong:** a direct measure of AI, or a comparison group plus timing that fits.
- **Moderate:** timing fits and there is a plausible mechanism, but no comparison group, or other causes only partly addressed.
- **Weak:** the trend predates generative AI, or major other causes are unaddressed.

"Strong" means the series measures AI directly (E2, E3). It is not strong evidence of harm, and it does not mean the indicator shows disempowerment. The current ratings are drafts. They will be reviewed in Stage 2, and any later change will be logged on this page.

## Comparisons

### Two kinds of baseline

**Long-running series** (E1, G1, C1) have decades of history and many causes. Their baseline is how the series behaved in **2010 to 2019**, after the 2008 to 2009 recession and before COVID. This page and the indicator pages call it the 2010 to 2019 baseline. The question is whether the series is departing from its baseline, and how fast.

**Series that measure AI use directly** (E2, E3) have only a few years of history and no pre-AI period, and can change quickly. E2 began near zero. E3 is a share of AI conversations, so it has no zero point to start from. Their baseline is their **own recent path**: level, rate of change and whether that rate is speeding up, averaged over the last 3, 6 and 12 months, or at the series' own frequency where data are less frequent.

### Comparison groups

A comparison group can separate an AI-related change from other causes. C1 has one. Stack Overflow is compared with four non-programming Stack Exchange sites, the **comparison sites**, chosen under criteria fixed before any post-2019 counts were viewed. The main measure is a **relative-activity index**: Stack Overflow's questions over the past 12 months relative to the comparison sites', set to 100 for 2019. Because AI affects the comparison sites too, the index measures relative change and likely understates any AI effect. It is not a causal estimate.

**Leave-one-out band.** The index is also recomputed four times, each time leaving out one comparison site. The chart shows the range of those four results as a band, so a reader can see whether the result depends on any single site.

E1 will gain an industry comparison in Release 2: labor share in industries where AI can do much of the work, against industries where it can do little, using published exposure scores.

### Uncertainty and seasonality

- Where a source publishes standard errors (a measure of how much an estimate would vary from sample to sample), the chart shows them as bands. The Census Bureau's Business Trends and Outlook Survey (BTOS), used for E2, is one. The threshold rule will use them.
- Monthly series with seasonal patterns (Stack Exchange, Wikipedia) are compared over 12-month periods or year over year.
- A move inside a series' normal noise never counts as crossing a threshold.

### Breaks, markers and revisions

- **Series breaks.** When a source changes its definition or method so that values before and after are not comparable, the chart marks the date and does not join the two parts. Examples: the change to the Census AI question on 17 November 2025 (E2), Wikimedia's improved bot detection in 2025 (C1), and changes in the Anthropic Economic Index release format (E3).
- **Chart markers.** Dated events that may matter for reading a chart are marked without splitting the line. Examples: ChatGPT's release on 30 November 2022 (every chart), GitHub Copilot's launch and Stack Overflow policy events (C1), and the Census question wording that began on 19 October 2026 (E2).
- **Revisions.** Official statistics are revised. The site uses the latest revised data. A revision that would change a reading is treated like new data and goes to review.

## Thresholds and the retrospective (coming in Stages 2 and 3)

**The rule comes first.** In Stage 2, a mechanical rule for each kind of comparison will be written, reviewed, fixed in advance and dated. The bands for each indicator then follow from the rule. They are not hand-picked after looking at the data. The author and the AI assistant that built the site have already seen the 2023 to 2026 data, so fixing hand-picked thresholds would not be enough.

**The candidate rule for long-running series** compares the change over an indicator's window with the spread of same-length changes in 2010 to 2019:

| Change over the window, against the 2010 to 2019 spread | Reading |
|---|---|
| Within one standard deviation | Within baseline |
| Between one and two standard deviations | Above or below baseline |
| Beyond two standard deviations | Far above or far below baseline |

A matching rule will be written for the adoption labels. The exact rules are a Stage 2 decision.

**Windows are part of the rule.** The window (for example, "change over the latest four quarters") can flip a reading on its own, so it is fixed for each indicator along with the rule.

**Sensitivity.** Each indicator page will show what the reading would be under reasonable alternatives:

- other windows
- another baseline period, such as 2015 to 2019
- narrower and wider bands

Where a reading flips under a reasonable alternative, the page will say so.

**Revision log.** Any change to a rule after it is fixed will be logged here, with the date and the reason.

**Retrospective.** In Stage 3, the fixed rule will be applied once to every quarter from the **fourth quarter of 2022**, when ChatGPT was released, to the present, using the latest revised data. The author reviews the results as a set. The retrospective will then be published as a dated snapshot ("computed [date], rule fixed [date], data as of [date]"). It does not recompute when data are revised. A re-run is a deliberate decision that produces a new snapshot, and earlier snapshots stay on the Archive page.

## Standing guards against one-sided reading

### The counter-evidence panel

The summary page carries a panel of signals pointing away from disempowerment, held to the same standard as the indicators. The inclusion criteria were written before any items were added. An item is included only if it meets all four:

1. **Primary source.** It comes from a primary source (the statistical agency, legislature or authors who produced the figure), which we opened and checked, with a link.
2. **Dated.** It is dated, with the period it covers stated.
3. **Measured.** It is a measured value or a counted event, not an opinion or a press paraphrase.
4. **Points away.** It points away from disempowerment in one of two ways:
   - policy pushback: governments or institutions acting to keep human control, such as AI laws passed
   - data that move the opposite way to what the disempowerment scenario predicts

Material welfare, such as rising incomes, is not counted. Welfare is not agency: people can be better off while losing influence (see below).

**Items are kept even if they are small or later reverse.** An item whose figure cannot be verified stays in the project's records, marked unverified with the reason, and is not published.

**No claim that AI caused it.** Inclusion says nothing about whether AI caused the signal.

### Warning signs and alternative explanations

Every indicator page states two things:

- **Warning sign:** which way a movement would be consistent with people losing leverage.
- **Alternative explanations:** the most plausible other explanations of the same data, including a reassuring movement that hides displacement and an alarming one with a cause other than AI.

These indicators show whether the conditions for disempowerment are present. They do not show that it is happening.

### Welfare and influence are different things

People can be better off materially while losing influence, and the reverse. Chooi, Lee and Li make the same distinction between well-being and agency. Every economic page notes it. A rising real income is good news, but it is not evidence that leverage is intact, so it is not counted in the counter-evidence panel.

### Diagnostics, not targets

These indicators are diagnostics. The site does not recommend that any policy aim to move one of these numbers. When a measure becomes a target, it stops being a good measure (Goodhart's law). Chooi, Lee and Li give the same warning about disempowerment metrics.

### The cultural gap

C1 measures activity on knowledge sites. It does not measure human capacity, attention or reliance on AI. The cultural column has no adoption indicator yet, and its displacement indicator counts activity, which is several steps removed from people's capacity to shape their culture.

The next candidate is survey data on how far people use AI as a go-between for information and relationships, such as Pew Research Center surveys and the Reuters Institute Digital News Report.

## Critiques we take seriously

**David Krueger (2025)**, a coauthor of the gradual disempowerment paper, warns that many proposed metrics do not separate empowering uses of AI from disempowering ones. Heavy AI use can look like progress while people lose real agency. The site responds in three ways:

- It keeps adoption (E2, E3) apart from displacement.
- It adds a note on augmentation versus replacement (AI helping people work, against AI doing the work instead of them) wherever adoption is shown.
- It names deferral, whether people simply approve AI's decisions, as the row with no public measure.

**Beren Millidge (2025)** argues that gradual disempowerment might not be so bad. Most people already have little individual influence over large systems. AI governance could be better than human governance. Capital income and transfers could sustain living standards. He calls the outcome highly uncertain. His argument is why every economic page separates welfare from influence: material gains are real, but they answer a different question.

**P. O. Jedlicka (2026)** argues that gradual disempowerment scenarios do not explain how societies actually respond, and assume that technology dictates outcomes. In Jedlicka's view they underrate people acting together and social conflict: people organize, push back and change the rules as a technology spreads. This is the main reason for the site's rule that signals pointing the other way, including policy pushback, are shown with equal prominence.

**The authors' own caveats.**

- Kulveit et al. concede that some outcomes of the scenario are ambiguous. For example, an AI-run state could bring large benefits.
- Chooi, Lee and Li say that showing what caused a change is hard throughout, that most metrics in this area can only describe and compare, and that leading indicators are hard to validate before the outcomes they predict have happened.

The site's indicators are descriptive in exactly this sense.

## What comes later

**Release 2** adds four indicators:

- **Wealth concentration (E4).**
- **Federal AI use cases (G2).**
- **AI-interest political influence (G3):** lobbying by groups that profit from AI.
- **AI's share of cultural production versus consumption (C2):** how much of what is made is AI-generated, against how much of what people actually read, watch or hear.

E4 and G3 are placed in the lock-in row only if a lock-in test is adopted.

Later versions are planned under four headings:

- **Method.**
  - Readings computed with data as first published, alongside revised data (from the Federal Reserve Bank of St. Louis's ALFRED archive of past data versions).
  - The E1 industry comparison.
  - A test on US states of the rentier logic for G1: states funded by oil, gas and coal taxes, which may answer less to their residents, against states that are not.
  - A measure of deferral for the oversight row, if one becomes available.
- **Harder indicators of AI's effect on work and research.**
  - Young workers in AI-exposed jobs.
  - Job postings weighted by AI exposure.
  - The AI-written share of scientific papers and peer reviews.
- **More labor-market indicators.**
  - Recent-graduate unemployment.
  - Participation in AI-exposed occupations.
  - Real wages in exposed versus less-exposed occupations.
  - An AI capital-investment share.
- **Other candidates from the research.** These include:
  - How far people read information and relate to others through AI, the next cultural candidate.
  - Income and wealth concentration tied to AI companies.
  - AI-vendor concentration in federal procurement.
  - AI-generated public regulatory comments.
  - International comparisons where free data allow.

## Sources and disclosure

The framework comes from [Kulveit et al. (2025)](https://arxiv.org/abs/2501.16946). These four sources were read in full before this page was written (the RAND report's mathematical appendix skimmed):

- [Chooi, Lee and Li (2026), "Measuring AI-Induced Disempowerment: A Framework and Proposed Metrics"](https://aclanthology.org/2026.evaleval-1.36/)
- [Moon and Boudreaux (2026), "A Formal Model of How Artificial Intelligence Erodes Human Agency," RAND Corporation](https://www.rand.org/pubs/research_reports/RRA4817-1.html)
- [Herdağdelen, Joren and Tamkin (2026), "How AI agents shape experts' judgment calls"](https://www.anthropic.com/research/agents-judgment-calls)
- [Imas and Schaal (2026), "Has AI impacted the labor market yet?"](https://aleximas.substack.com/p/has-ai-impacted-the-labor-market)

Every figure on the site is checked against its primary source before publication.

This site is built with assistance from Claude (Anthropic). One indicator (E3) uses data published by Anthropic, and the oversight row cites research authored at Anthropic.
