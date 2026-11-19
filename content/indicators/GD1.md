---
summary: On average, governments in the OECD (Organisation for Economic Co-operation and Development, a group of mostly wealthy countries) still raise about half of their tax revenue from taxes on people's incomes and social contributions, and that share is slightly above its 2010 level. The US share, which drives the reading, has fallen since 2022.
warning_sign: A falling labor-based share would be consistent with the state depending less on taxing workers. A rising or stable share points the other way.
data_sources:
  - name: "Bureau of Economic Analysis (BEA), national accounts: government receipts, via FRED (Federal Reserve Bank of St. Louis)"
    url: https://fred.stlouisfed.org/series/W055RC1Q027SBEA
  - name: OECD Revenue Statistics
    url: https://data-explorer.oecd.org/?df[ds]=DisseminateFinalDMZ&df[id]=DSD_REV_COMP_OECD%40DF_RSOECD&df[ag]=OECD.CTP.TPS
calculation: The share of tax revenue that comes from taxes on people's incomes plus social insurance contributions. For the United States, quarterly, KEEL computes it from BEA figures; for the OECD average and the United States, annually, it adds two of OECD's published shares.
coverage: United States · quarterly · from 1947; OECD average and United States · annual · from 1965
---

## Why this matters for gradual disempowerment

Gradual disempowerment is the scenario in which economies, states and cultures stop needing people and so stop serving them, without any single dramatic event [(Kulveit et al. 2025)](../sources.qmd#kulveit2025). A state that funds itself by taxing its citizens' work has a reason to keep them productive and to listen to them. A state that funds itself from other sources has less reason to. Political scientists call this the rentier-state pattern: governments funded by resources rather than taxes tend to answer less to their citizens [(Ross 2001)](../sources.qmd#ross2001). It is a common explanation for why governments that live on oil revenue tend to be less accountable.

Kulveit et al. apply the same logic to AI. If AI shifts income from wages toward capital, and tax revenue follows, the state could come to depend less on its citizens. [Drago and Laine (2025)](../sources.qmd#drago2025) make the same comparison in *The Intelligence Curse*: like a state rich in oil, a state whose income comes from AI rather than from people's work may lose its incentive to care about them. [Chooi et al. (2026, 232)](../sources.qmd#chooi2026) propose a related metric: citizen tax revenue relative to AI-derived corporate profits.

This indicator is the most direct public measure we found of that state-dependence argument. It sits in the **Displacement** row, as the core mechanism for the government domain. It is a **lagging** indicator, one that moves late: tax structures change slowly.

**What the data say now.** Across OECD countries, the labor-based share of tax revenue was 48.53 percent in 2010, peaked at 50.54 percent in 2020, and was 49.20 percent in 2023, the latest year with an OECD average.

The US quarterly series drives this indicator's reading. It has fallen since 2022: it averaged 66.85 percent in 2022, a year when federal individual income tax receipts were the highest share of GDP since 1913, partly because of large capital gains realized in 2021 and 2022 [(Congressional Budget Office 2023, 21–24)](../sources.qmd#cbo2023), and was 63.21 percent in the second quarter of 2026 (data as of 17 November 2026). That is inside the range it moved through in 2010 to 2019 (62.30 to 66.88 percent). The reading itself is not yet reviewed.

## What it shows

- **United States, quarterly (drives the reading).** The labor-based share of tax revenue, from the Bureau of Economic Analysis (BEA) national accounts, read through FRED, the Federal Reserve Bank of St. Louis's data service. It covers all levels of government (federal, state and local).
- **United States and OECD average, annual (context).** Taxes on individual incomes plus social security contributions, as a share of total tax revenue, from OECD Revenue Statistics. The OECD data lag two to three years (the OECD average currently runs to 2023, the US figure to 2024).

This is a long-running series. Its baseline is how it behaved in 2010 to 2019. Readings start once the rules are fixed (see the methodology page). Until then the reading shows "Not yet reviewed."

## What it doesn't show

- **It does not measure AI.** Tax law, the business cycle, asset prices and an aging population all move this share.
- **It is labor-based only approximately.** Personal income taxes also fall on interest, dividends and capital gains. A stock-market boom can raise "labor-based" revenue with no change in how much the state depends on workers. Social contributions are tied more closely to wages.
- **It does not show whether governments respond to citizens.** It measures one source of the state's dependence on people. Elections, courts, protest and a free press are other sources, and none of them is measured here.

## What would change our reading

### Alternative explanations

- **A steady share can hide lost leverage.** A state can keep citizens on side through transfer payments even when it no longer depends on their taxes. This is the rentier pattern of buying off citizens with low taxes and patronage [(Ross 2001)](../sources.qmd#ross2001). So a steady labor-based tax share does not guarantee that citizens keep their leverage.
- **A falling share can have other causes.** Tax cuts on income, a weak labor market, an aging population or a boom in corporate profits can all lower the share with no change caused by AI. The share could also fall while citizens keep leverage through other channels.

This is the most direct public measure of state dependence we found, not a guarantee.

### What would raise or lower our confidence

**What would move the reading toward disempowerment:**

- A sustained fall in the US share beyond its 2010 to 2019 range.
- A fall that occurs while corporate and capital-income tax receipts grow faster than wage-based receipts.
- The same fall showing up in the OECD data once those data arrive.

**What would point away from disempowerment:** the US share holding inside or above its 2010 to 2019 range, and the OECD share continuing not to fall.

A later version plans a US-states comparison: states that depend heavily on taxes on extracting oil, gas and coal against states that do not. That would test the rentier logic on US data.

These indicators show whether the conditions for disempowerment are present. They do not show whether it is happening.

## Data and calculation

- **Source and series, United States quarterly.** BEA national accounts, read through FRED: [personal current taxes](../sources.qmd#fred_personal_current_taxes), [contributions for government social insurance](../sources.qmd#fred_social_insurance_contributions), and [government current tax receipts](../sources.qmd#fred_tax_receipts), all for government at every level.
- **Source and series, annual.** [OECD Revenue Statistics, comparative tables](../sources.qmd#oecd_revenue_statistics): taxes on income of individuals and social security contributions, each as a percent of total tax revenue, for the OECD average and for the United States. The OECD average is OECD's own published figure; KEEL does not recompute it. Source: [OECD, Revenue Statistics 2025](../sources.qmd#oecd_revenue_statistics).
- **Units.** Percent of tax revenue.
- **Frequency.** Quarterly (US, at seasonally adjusted annual rates) and annual (OECD).
- **Date range.** US quarterly from the first quarter of 1947; OECD annual from 1965. The OECD average currently runs to 2023 and the OECD figure for the United States to 2024.
- **Formula in plain words.** US quarterly: (personal current taxes + contributions for government social insurance) divided by (government current tax receipts + contributions for government social insurance), times 100. Contributions are added to the bottom of the fraction because BEA does not count them as taxes. OECD annual: the share from taxes on individual incomes plus the share from social security contributions.

## Caveats

- **Two sources, one reading.** The US quarterly series and the OECD annual series use different definitions and do not match exactly. The US series drives the reading. When the two disagree, the author decides and the rationale says so. Nothing is averaged.
- **Revisions.** BEA revises the national accounts, and OECD revises Revenue Statistics. The figures quoted on this page are as of 17 November 2026, and the chart always shows the latest data.
- **The OECD average is the published OECD figure.** KEEL does not recompute it, and its country coverage follows OECD's own definitions.
- **The retrospective is not yet computed.** The retrospective applies the fixed rule to every quarter from the fourth quarter of 2022 onward, to show how readings would have changed since ChatGPT's release. It will be computed once and published as a dated snapshot in Stage 3.

**Feedback.** [Report an error](https://github.com/richardsonlj12/keel/issues/new?template=error-report.md) · [Join the discussion](https://github.com/richardsonlj12/keel/discussions) · [Send private feedback](https://docs.google.com/forms/d/e/1FAIpQLSdJn9K0revpwU1sWM-WPmqlPtw80JVSuR9lIzcPktXqY7e3Tg/viewform)
