---
summary: A growing share of US firms say they use AI. This measures adoption, how far AI is entering firms, counting every firm equally. It does not by itself show that anyone has lost leverage.
warning_sign: Rising adoption would show AI spreading through firms. By itself it does not show that people have lost leverage.
data_sources:
  - name: Census Bureau, Business Trends and Outlook Survey (BTOS)
    url: https://www.census.gov/hfp/btos
calculation: The share of US firms answering "Yes" when asked whether they used AI in the last two weeks, counting every firm equally (firm-weighted), as estimated by the Census Bureau. A second view shows the same share within seven firm-size classes.
coverage: United States · every two weeks · from September 2023
---

## Why this matters for gradual disempowerment

Gradual disempowerment is the scenario in which economies, states and cultures stop needing people and so stop serving them, without any single dramatic event [(Kulveit et al. 2025)](../sources.qmd#kulveit2025). Before AI can reduce the economy's dependence on human work, firms have to adopt it. This indicator tracks that first step: the share of US businesses that report using AI. It sits in the **Adoption** row of the grid, which asks whether AI is entering a system and how far it has gone.

Adoption is a precondition for the mechanism Kulveit et al. describe. It is not evidence of the mechanism itself. Rising adoption is equally consistent with AI making workers more productive and more valuable, and with AI replacing them. This indicator cannot tell those apart. It is a **leading** indicator, one that moves early: adoption should move before any effect on labor's share of income or on tax revenue does.

## What it shows

- **The share of US firms answering "Yes" when asked whether they used AI in the last two weeks.** From the Census Bureau's Business Trends and Outlook Survey (BTOS), national, all sectors.
- **Census standard errors**, shown as bands on the chart. A standard error is a measure of how much an estimate would vary from sample to sample. Each estimate is dated by the end of its two-week collection period.
- **By firm size.** A second view shows the same share within seven size classes, from firms with 1 to 4 employees to firms with 250 or more. Census publishes these from the November 2025 question onward. Larger firms report using AI more often: in the period ending 1 November 2026, 22.8 percent of firms with 1 to 4 employees said "Yes," against 44.1 percent of firms with 250 or more.

**Firm-weighted.** Every firm counts once, whatever its size, so a five-person shop and a large employer weigh the same. An employment-weighted measure, which counts firms by how many people they employ, answers a different question (what share of workers are at firms that use AI) and can give a very different number. KEEL labels this series "firm-weighted" wherever it appears.

**Why firm-weighted.** KEEL uses the firm-weighted share for three reasons, and accepts one limitation:

1. **It is the official national estimate.** The BTOS national estimate is firm-weighted. It is the official, free series, published every two weeks with standard errors, and KEEL can track it automatically. Measures weighted by employment, or drawn from other surveys, report substantially higher adoption than the firm-weighted Census figure. A Federal Reserve Board note compares the two kinds of measure [(Allen 2026)](../sources.qmd#allen2026). They answer different questions, so neither is wrong.
2. **It measures breadth.** Counting each firm once shows how widely AI has spread across separate businesses, which is the question the Adoption row asks.
3. **The firm-size view fills part of the gap.** It shows how adoption differs between small and large firms.

**The limitation.** Because larger firms adopt more, the firm-weighted share understates how many workers encounter AI at work.

**The series break on 17 November 2025.** Census changed the question after testing it with respondents:

- **Through early October 2025**, firms were asked whether they used AI "in producing goods or services."
- **From the collection that began on 17 November 2025**, they are asked whether they used it "in any of its business functions." The examples given did not change.

Census's testing found that some businesses answered "No" even though they used AI, for example in hiring, accounting, project management or research and development, because those uses were not directly connected to "producing goods or services." The broader question counts more uses as AI use, so the two segments are not comparable. Census saw a shift in the level of the series with the new wording and started a new time series because of it [(U.S. Census Bureau 2025)](../sources.qmd#census2025). The chart shows them as separate segments and does not join them. There are no estimates for the weeks between the last old-wording period and the first new-wording period.

**The wording marker on 19 October 2026.** Beginning with the collection of 19 October 2026, Census changed the term in the question to "Super Intelligence or SI (formerly referred to as Artificial Intelligence or AI)" and replaced the examples with new ones, such as "SI-powered data analysis" and "generative SI for marketing, product design, or coding" [(U.S. Census Bureau 2026)](../sources.qmd#census2026). Census cites Executive Order 14434 for the change ([U.S. Census Bureau, n.d.](../sources.qmd#census_btos); [Exec. Order No. 14,434](../sources.qmd#eo14434)). Respondents saw the new wording. In that first period:

- the "Do not know" share rose from 9.6 to 13.9 percent, and the "No" share fell from 65.8 to 61.9 percent
- the "Yes" share was essentially unchanged, at 24.2 percent against 24.6 percent in the period before
- the standard error of the "Yes" share rose from 0.27 to 0.61 percentage points

The same period also started a new version of the questionnaire, so these changes cannot be traced to the wording alone. KEEL marks the date on the chart but does not treat it as a series break. It will revisit that decision once more periods are published.

**"Do not know."** A sizeable share of firms answer "Do not know." Across the periods from the November 2025 change through mid-October 2026, that share ranged from 9.1 to 11.2 percent. It was 13.9 percent in the first period asked with the new wording (as published on 17 November 2026). KEEL shows the "Yes" share. A shift between "Do not know" and "Yes" can move the series without any change in actual use.

This series measures AI use directly and has no history before AI. Its baseline is its own recent path: its level, how fast it is changing, and whether that pace is speeding up, averaged over the last 3, 6 and 12 months. Readings will use the labels Low, Rising and Pervasive, and start once the rules are fixed (see the methodology page). Until then the reading shows "Not yet reviewed."

## What it doesn't show

- **It does not show disempowerment.** A change in the series is a change in AI use. It is not evidence of harm, and it does not show lost leverage.
- **It does not show how AI is used.** A firm that uses AI to help its staff (augmentation) and a firm that uses it to do the work instead of its staff (replacement) both answer "Yes." Adoption that augments workers may strengthen their position. Adoption that replaces them may weaken it. KEEL's next indicator, how AI is used (EA2), is the nearest public data on a related split, and it covers one vendor's product.
- **It does not show how much AI a firm uses.** A firm that tried one tool once and a firm that runs core operations on AI count the same.
- **It does not measure welfare.** Wider AI use may raise output and incomes while shifting who has influence, or the reverse. This series speaks to neither.

## What would change our reading

### Alternative explanations

- **Shallow or helpful use.** Adoption may be shallow or experimental, and may help workers rather than replace them. If adoption keeps rising while the displacement indicators (ED1, labor share; GD1, labor-based tax share) hold steady, that explanation becomes more likely. Adoption that rises alongside displacement signals would be consistent with the disempowerment scenario. It would still not prove it.
- **Changes in how firms answer.** A move between "Do not know" and "Yes," or a change in the question, can shift the series with no change in actual use.

These indicators show whether the conditions for disempowerment are present. They do not show whether it is happening.

## Data and calculation

- **Source and series.** [Census Bureau, Business Trends and Outlook Survey](../sources.qmd#census_btos), question 7 ("In the last two weeks, did this business use..."), answer "Yes." Periods from September 2023 to early October 2025 come from Census's AI core questions file. Periods from November 2025 onward come from the national estimates file, and the firm-size view from the employment size class file. All are linked from the BTOS data downloads page.
- **Units.** Percent of firms. Standard errors are in percentage points.
- **Frequency.** Every two weeks. Each estimate is dated by the last day of its collection period.
- **Date range.** From the period ending 24 September 2023 to the latest published period. Census published no estimates for collections from 6 October to 16 November 2025, during a federal funding lapse. The firm-size view starts in November 2025.
- **Formula in plain words.** Census's own estimate of the share of firms answering "Yes," with each firm counted once. KEEL does not recompute it. The two question wordings are kept as separate segments.

## Caveats

- **Self-reported.** Answers come from one respondent per firm, who may not know every use of AI in the business. Survey response rates and the "Do not know" share both affect the estimate.
- **Two-week reference window.** The question asks about the last two weeks, so occasional use can be missed in one period and counted in the next.
- **The 17 November 2025 break.** A reading that spans the break treats the two segments separately. Part or all of any jump at the break comes from the new wording.
- **US only, and firms only.** The series says nothing about government or household use of AI.
