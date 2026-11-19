---
summary: The share of business income paid to workers has been falling for decades, long before generative AI. This page tracks whether that fall speeds up as AI spreads.
warning_sign: A falling labor share would be consistent with workers losing leverage in the economy. A stable or rising share points the other way, though a steady share can still hide lost leverage.
data_sources:
  - name: "Bureau of Labor Statistics (BLS), Productivity and Costs: labor share, nonfarm business sector"
    url: https://data.bls.gov/timeseries/PRS85006174
  - name: "Bureau of Economic Analysis (BEA), corporate profits after tax and gross domestic product, via FRED (Federal Reserve Bank of St. Louis)"
    url: https://fred.stlouisfed.org/series/CPATAX
calculation: The labor share is the part of what nonfarm businesses produce that is paid to workers as wages and benefits, as a percent of output, published by BLS. The profit share, selectable in the chart, is corporate profits after tax divided by gross domestic product.
coverage: United States, nonfarm business sector · quarterly · from 1947
---

## Why this matters for gradual disempowerment

Gradual disempowerment is the scenario in which economies, states and cultures stop needing people and so stop serving them, without any single dramatic event [(Kulveit et al. 2025)](../sources.qmd#kulveit2025). The argument starts from a simple observation: economies serve people partly because they need people's work. Workers who are needed have bargaining power, which KEEL calls leverage. If AI systems can do more of the work, firms need fewer workers, and that source of leverage weakens.

The labor share is the most direct public measure of how much of what businesses produce is paid out to the people who work in them. [Chooi et al. (2026, 232)](../sources.qmd#chooi2026) call labor cost share "the most direct financial measure of human economic participation." If AI substitutes for human work at scale, a falling labor share is one place the change should show up.

This indicator sits in the **Displacement** row: it asks whether the economy's dependence on human labor is falling, and by how much. It is a **lagging** indicator, one that moves late. Income shares move slowly, so it is more likely to confirm a change already under way than to warn of one early.

## What it shows

- **Latest data.** The labor share was 53.0 percent in the third quarter of 2026, the lowest since the series began in 1947. BLS reported its first estimate for the second quarter, 52.8 percent, as the lowest level on record [(U.S. Bureau of Labor Statistics 2026)](../sources.qmd#bls2026). The fall began before ChatGPT's release: the share averaged 56.7 percent in 2021 and was 55.5 percent in the third quarter of 2022.
- **Labor share of income, nonfarm business sector.** Published quarterly by the Bureau of Labor Statistics (BLS), adjusted to remove regular seasonal swings. The chart shows the full history from 1947.
- **Profit share, for context.** Corporate profits after tax as a share of gross domestic product, from the Bureau of Economic Analysis (BEA). It uses a different top and bottom of the fraction, so it is a rough counterpart to the labor share and does not add up to 100 with it. The labor share alone drives this indicator's reading.

This is a long-running series. Its baseline is how it behaved in 2010 to 2019, after the 2008 to 2009 recession and before COVID. The question for a reading is whether the series is departing from that baseline, and how fast. Readings start once the rules are fixed (see the methodology page). Until then the reading shows "Not yet reviewed."

## What it doesn't show

- **It does not measure AI.** The labor share responds to globalization, market concentration, the decline of unions, the mix of industries, the business cycle and more. Chooi, Lee and Li note that labor cost share has been declining since the 1980s for reasons like these.
- **It does not measure leverage directly.** Bargaining power is the thing the argument is about. The labor share is a stand-in for it.
- **It does not measure welfare.** People can be materially better off while losing leverage, and the reverse can also happen. A falling labor share in a fast-growing economy can come with rising real wages. A stable share can come with stagnant ones. KEEL tracks influence and dependence, not material welfare.
- **It covers the nonfarm business sector only.** Government, farms, nonprofit institutions and private households are outside it.

## What would change our reading

### Alternative explanations

- **A flat line can hide lost leverage.** Labor's share could hold steady while work moves into jobs where workers have less bargaining power. Alex Imas and Jacob Schaal describe a "relational sector," where "human involvement in the role is part of the value," that "may expand as labor flows to existing relational jobs (e.g., healthcare, education)" [(Imas and Schaal 2026)](../sources.qmd#imas2026). They present this as a counterforce to AI displacement. KEEL draws a further inference of its own: if labor flows into such jobs as AI takes over other work, labor's share of income could stay roughly flat even if workers end up with less bargaining power. So a flat line is not proof that leverage is intact.
- **A fall can have causes other than AI.** The share has fallen for decades for reasons that have nothing to do with generative AI, and it moves with the business cycle.

### What would raise or lower our confidence

**What would raise our confidence that a change is AI-related:**

- A fall that begins or speeds up after late 2022 and moves away from the baseline by more than the series typically varied in 2010 to 2019 (the exact rule is fixed in Stage 2).
- A faster fall in industries where AI can do much of the work than in industries where it can do little. KEEL plans this comparison for Release 2, using BEA industry data with published AI-exposure scores.

**What would lower it:**

- A fall that tracks the business cycle.
- A fall that is concentrated in industries with little AI exposure.
- A fall that reverses when the economy slows.

These indicators show whether the conditions for disempowerment are present. They do not show whether it is happening.

## Data and calculation

- **Source and series.** The labor share is the [labor share for the nonfarm business sector, as a percent](../sources.qmd#bls_labor_share), from the Bureau of Labor Statistics (BLS) Productivity and Costs program, read directly from BLS.
- **Profit share.** The profit share comes from a different agency, the Bureau of Economic Analysis (BEA). It divides [corporate profits after tax (with inventory valuation and capital consumption adjustments)](../sources.qmd#fred_cpatax) by [gross domestic product](../sources.qmd#fred_gdp), both read through FRED, the Federal Reserve Bank of St. Louis's data service.
- **Units.** Percent of output.
- **Frequency.** Quarterly, adjusted to remove regular seasonal swings.
- **Date range.** From the first quarter of 1947 to the latest published quarter.
- **Formula in plain words.** The labor share is the compensation paid to workers in nonfarm businesses (wages, salaries and benefits, plus an estimate for the self-employed) divided by the current-dollar value of what those businesses produce, as published by BLS. KEEL does not recompute it. The profit share is corporate profits after tax divided by gross domestic product, times 100.

## Caveats

- **BLS revises recent quarters.** For example, BLS first published the labor share for the second quarter of 2026 as 52.8 percent [(U.S. Bureau of Labor Statistics 2026)](../sources.qmd#bls2026). As of 17 November 2026, the same quarter reads 53.3 percent. KEEL uses the latest revised data, so recent values can move after a reading is made. A revision that changes a proposed reading is treated as new data and goes to review. A later version will show readings computed with data as first published alongside the revised data (from the St. Louis Fed's ALFRED archive of past data versions).
- **Quarter-to-quarter movements are noisy.** Readings will use a fixed window and a threshold rule, set in Stage 2, so a single quarter cannot by itself change a reading.
- **The retrospective is not yet computed.** The retrospective applies the fixed rule to every quarter from the fourth quarter of 2022 onward, to show how readings would have changed since ChatGPT's release. It will be computed once and published as a dated snapshot in Stage 3.

**Feedback.** [Report an error](https://github.com/richardsonlj12/keel/issues/new?template=error-report.md) · [Join the discussion](https://github.com/richardsonlj12/keel/discussions) · [Send private feedback](https://docs.google.com/forms/d/e/1FAIpQLSdJn9K0revpwU1sWM-WPmqlPtw80JVSuR9lIzcPktXqY7e3Tg/viewform)
