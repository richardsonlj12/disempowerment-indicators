# KEEL Stage 1: independent review

Reviewer: independent second checker (Claude, Opus 5.5), 18 November 2026. I rebuilt the site (`python -m indicators.pages` and `quarto render site`, both clean). Then I read every generated page, `content/`, `config/`, `site/js/` and the published CSVs, recomputed the headline figures from those CSVs, and spot-checked primary sources online. I did not test the site in a browser, so I have not checked dark mode, phone width or keyboard use directly.

## Verdict

**Close to publishable. Fix one Critical item and about eight Important ones first.** The prose is unusually careful about causation, and the figures I checked match their CSVs and sources. The problems are mostly about consistency and balance. GD1's text and GD1's own chart point in opposite directions. The pages offer an interpretation where the data are reassuring (GD1) but not where they are alarming (ED1, at a record low). The counter-evidence panel and the oversight row each show the more favourable number from their source.

## Findings

1. **Critical. GD1: the text says one thing and the page's own baseline chart says the opposite.**
   *Where:* `indicators/GD1.html`, in the Summary row and "What the data say now" (`site/indicators/GD1.qmd` summary table), against the "Deviation from 2010–19 trend" chart view and `site/data/us_labor_tax_share_trend.csv`.
   *What is wrong:* The summary table says the baseline is "against its 2010 to 2019 trend". The text then judges the US share against the 2010–19 *range* (62.30 to 66.88) and concludes "this indicator does not point toward disempowerment".
   *Evidence:* Against the trend the page names, the latest US value (63.21, 2026 Q2) is **−7.0 points** off a trend extended to 70.2. The standard deviation of the 2010–19 deviations is 0.54, so the gap is about 13 of them. That trend rises steeply because 2010 was a post-recession low. A reader who switches to the deviation view sees a dramatic fall, while the prose next to it says there is nothing to see.
   *Fix:* Choose one baseline concept and use it in the summary row, the text and the chart. If the extended linear trend is kept as a view, say on GD1 that the 2010–19 slope reflects recovery from the recession and should not be extended. Or drop the deviation view for GD1 until Stage 2 fixes the rule. Do not state a conclusion that the page's own chart contradicts.

2. **Important. The pages interpret reassuring data but stay silent on alarming data.**
   *Where:* GD1 Summary and "What the data say now" ("On the evidence so far, this indicator does not point toward disempowerment"), compared with ED1 (`site/indicators/ED1.qmd`), which has no "what the data say now" section.
   *What is wrong:* Every reading is "Not yet reviewed", yet GD1 effectively gives one, and it is the reassuring one. ED1 gives none, although its latest value is the lowest in the series' history.
   *Evidence:* In `labor_share_nfb.csv`, 53.0 in 2026 Q3 is the series minimum since 1947. It sits 3.65 points below the 2010–19 trend, against a baseline standard deviation of 0.47. BLS's own headline, which the ED1 caveat cites only for the revision figure, is "Labor share at its lowest level, 52.8 percent, in second quarter 2026", described as "the lowest level ever recorded" (bls.gov TED, 15 September 2026; I confirmed this by fetching it).
   *Fix:* Treat both pages the same way. Either remove the interpretive verdict from GD1, or add a matching "What the data say now" to ED1. That section should say the labor share is at a record low. It should also say the fall from about 56.9 in 2021 began before ChatGPT (−1.0 points by 2022 Q3), alongside post-pandemic profit margins, which are also near a high in `profit_share.csv`.

3. **Important. Three different "baseline" ideas are in use.**
   *Where:* `methodology.html` "Reading labels" and "The threshold rule"; summary tables ("against its 2010 to 2019 trend"); GD1 text ("range"); `charts.js:166–173` (straight-line trend fitted to 2010–19 and extended).
   *What is wrong:* The candidate rule compares changes over a window with the spread of same-length changes. The charts show deviation from an extended linear trend. GD1's prose uses the range of levels. These can give opposite answers (finding 1).
   *Fix:* Before publishing, change the summary-table wording to something neutral ("compared with its 2010 to 2019 behaviour"). Add a sentence to the methodology page saying the deviation view is not the rule and can mislead where the baseline period begins at a cyclical low. The chart note already says the first half of this.

4. **Important. The first counter-evidence item does not meet the panel's own criterion 4.**
   *Where:* `index.html` Counter-evidence; `config/curated/counter_evidence.yaml` (`oecd_labor_tax_share`).
   *What is wrong:* "Labor-based taxes remain about half of OECD tax revenue" is a *level*. Criterion 4 asks for "data that move the opposite way to what the disempowerment scenario predicts".
   *Evidence:* The OECD average fell from 50.54 (2020) to 49.20 (2023). It is "up" only against a 2010 starting point (48.53), and it dipped below that in 2011, 2016 and 2022. The same data also already appear as context on GD1, so they are counted twice. The label also hides GD1's own caveat that personal income tax includes tax on capital income.
   *Fix:* Remove the item, or restate it honestly ("no sustained fall since 2010; down 1.3 points since the 2020 peak") and explain why a level meets the criterion. Don't count GD1's context series as separate counter-evidence.

5. **Important. The AI-law count is presented as "policy pushback" without its caveat.**
   *Where:* `index.html` Counter-evidence; `counter_evidence.yaml` (`ai_legislation_counts`).
   *What is wrong:* The panel defines pushback as "governments or institutions acting to keep human control". A count of "AI-related" enacted bills includes laws that promote or fund AI.
   *Evidence:* The curated note itself says the count "says nothing about whether they restrain AI or how well they are enforced". That note is not shown on the page.
   *Fix:* Show the note's caveat on the panel. Better, count only laws that restrict AI or require human oversight.

6. **Important. The oversight row reports the most striking figure from the study and leaves out its weaker main result and a key design choice.**
   *Where:* `index.html` oversight cell; `methodology.html` "Oversight"; `config/curated/oversight.yaml`.
   *What is wrong and the evidence:* The page cites 86 percent agreement with the agent's lean. Two things are missing.
     - The authors "deliberately strengthened the agents' lean". I confirmed this on the Anthropic page.
     - The effect on the final recommendation was much weaker: 54 percent against 36 percent, a 17-point gap. The curated note says the paper's registered estimate of this effect is not statistically significant.
   The 11 analysts who chose not to use the agent were excluded. The wording "Share of four analytical choices where…" also misdescribes the figure. It is the share of analyst-decisions, not of four choices.
   *Fix:* Add one sentence on each limit. Reword the metric as "Share of analysts' decisions (four per analyst, 50 analysts) that matched the agent's randomly assigned lean".

7. **Important. CD1 is published without its main measure, and its claims about Stack Overflow have no published data behind them.**
   *Where:* `indicators/CD1.html`; home grid CD1 cell ("Latest value not yet available").
   *What is wrong:*
     - The default chart view, the chart title and the "Calculation" row all describe the Stack Overflow index. That index and all its views are `available: false`, so the first thing a reader sees is "Data still being collected".
     - The page makes historical claims with no data published to support them: "peaked in the mid-2010s and fell through the late 2010s… after a rise in 2020, the fall steepened in 2021 and 2022". The Method section then says "Stack Overflow declined from about 2020", which contradicts that.
     - "criteria fixed before any post-2019 counts were requested or viewed" (`methodology.html` "Comparison groups") sits awkwardly next to the authors' detailed knowledge of Stack Overflow's post-2019 path.
   *Fix:* Hold CD1 back, or make Wikipedia the default view and put a clear "Stack Overflow index: coming" notice first. Make the timing claims agree with each other. Narrow the pre-registration claim to "post-2019 counts for the candidate comparison sites".

8. **Important. "AI link: Strong" will be misread on the home grid, especially for EA2.**
   *Where:* `index.html` grid (EA1 and EA2 badges); `methodology.html` "The AI link rating".
   *What is wrong:* A coloured "Strong" badge next to "48.6 percent automation" reads as strong evidence. The pages do say otherwise, but only further in.
   *Evidence:* The EA2 data have seven points in four segments, come from one vendor, have no comparison group, and the page itself says vendor product changes can move them. The methodology's own definition of Strong includes "a comparison group plus timing that fits".
   *Fix:* For the Adoption row, use a different label such as "Measures AI directly", or rate EA2 Moderate because of the single-vendor and product-change confounds.

9. **Important. The EA2 chart is under owner review; my view:**
   *Where:* `indicators/EA2.html`; `site/indicators/EA2.qmd` keelSpec; `charts.js` multi view.
   *Problems:*
     - **Two mirror-image lines.** Automation and augmentation always sum to 100, so plotting both doubles the ink without adding information.
     - **Narrow y-axis.** The automatic domain of roughly 42 to 58 makes swings of a few points look large.
     - **Too little data to compare.** There are seven points in four segments separated by breaks. Segment 2 is a single isolated dot. Almost no comparison within a segment is possible, so readings like "Rising" cannot yet be supported.
     - **Points sit on the wrong dates.**
       - Most points are plotted at the *release* date, not the date of the sample. The Feb 2026 sample is plotted at 24 March and the Aug 2025 sample at 15 September.
       - The April and May 2026 points sit at month start.
       - So the spacing on the time axis misrepresents when the data were collected.
     - **Misleading "as of" date.** "48.6 percent (1 May 2026)" and "data through 1 May 2026" refer to the whole month of May.
   *Fix:* Plot automation share only, as dots placed at the sample's midpoint. Use a fixed axis such as 30 to 70 or 0 to 100, with a 50 percent reference line. Label points with their sample window. Write "May 2026" rather than a single day.

10. **Important. EA2 overclaims in its summary.**
    *Where:* EA2 Summary row: "It is the only free public data on how AI is used".
    *What is wrong:* OpenAI's "How People Use ChatGPT" (Chatterji et al. 2025, NBER) publishes a comparable usage split (Asking, Doing, Expressing). Surveys such as Pew's also report how people use AI.
    *Fix:* Write "the only regularly released free public series that classifies AI conversations as automation or augmentation" and name the OpenAI study as a one-off comparison.

11. **Minor. EA1: the wording records may contradict "The examples given did not change".**
    *Where:* EA1 "The series break on 17 November 2025"; `site/data/btos_ai_use.meta.json` notes.
    *Evidence:* The metadata quotes different examples for the two wordings: "machine learning, natural language processing…" against "SI-powered data analysis; generative SI for marketing…". So the examples changed either in November 2025 or in October 2026. If October 2026, the "only the term changed" description of the marker is incomplete too.
    *Fix:* Check against the 3 December 2025 Census notice and the V5 instrument, then reword. I could not read the PDF text to check this myself.

12. **Minor. EA1 and EA2 chart specs carry CD1's site labels.**
    *Where:* `groupLabels` in the EA1, EA2 and other page specs ("diy", "travel", "rpg", "scifi").
    *What is wrong:* These are harmless leftovers, but the global map could mislabel any future group key that happens to match.
    *Fix:* Emit `groupLabels` only on CD1.

13. **Minor. The retrospective boilerplate says "every quarter" on every page.**
    *Where:* the CD1 and EA1 caveats and the methodology.
    *What is wrong:* CD1 is monthly, EA1 every two weeks, and EA2 irregular.
    *Fix:* Say "every period" or name each indicator's own frequency.

14. **Minor. ED1 says the profit share is "shown alongside", but it is not.**
    *Where:* ED1 "What it shows".
    *What is wrong:* In the Level view (`charts.js:161`) the profit share is a separate choice in a dropdown, not drawn on the same chart.
    *Fix:* Say "selectable in the chart".

15. **Minor. GD1's 2022 comparison point is a capital-gains peak.**
    *Where:* GD1 "What the data say now".
    *What is wrong:* "Fallen since 2022: averaged 66.85" starts from a year inflated by tax on 2021 capital gains, so part of the fall is a return to normal.
    *Fix:* Add one clause saying so.

16. **Minor. One sentence in the methodology reads as causal.**
    *Where:* `methodology.html` "What KEEL measures": "As AI systems replace that participation…"
    *Fix:* "If AI systems replace…"

17. **Minor. Charts are hard to use without sight or a mouse.**
    *Where:* `charts.js:224–253`.
    *What is wrong:* The chart markers are numbered only and explained in a list below. Hover tips need a pointer. There is no table of the values on the page, only the CSV.
    *Fix:* Add a collapsible table of the latest values or the plotted points. I have not checked dark mode, phone width or keyboard focus in a browser; someone should do that by hand before launch.

18. **Minor. The canonical site URL is not live yet.**
    *Where:* `https://richardsonlj12.github.io/keel/`, used in `_quarto.yml` and the citation on the About page.
    *Evidence:* It returns 404 today. The GitHub repo URL returns 200.
    *Fix:* Confirm after deployment that the issue template and Discussions links work.

## What is done well

- **Careful causal language throughout.** Every page separates "consistent with" from "caused by". Each has a substantive "What it doesn't show" and alternative explanations that cut both ways ("a flat line can hide lost leverage"; "a falling share can mislead too").
- **Breaks and caveats are handled honestly.**
  - The EA1 November 2025 break is shown as separate segments, with the gap from the funding lapse left visible.
  - The Census "Super Intelligence" relabel is documented with before-and-after figures, and the page explains why it is a marker rather than a break.
  - EA2's choice of denominator is reconciled explicitly with Anthropic's headline numbers.
- **Figures match their sources.** Everything I recomputed matched the published CSVs: 24.2/24.6 (EA1), 22.8/44.1 by firm size, 51.07 against about 49, 66.85, 62.30–66.88, 48.53/50.54/49.20, and the BLS 52.8 to 53.3 revision. The Imas and Schaal quotation is exact, and the Herdağdelen 86 percent figure and sample size are correct.
- **Conflict of interest disclosed.** The Anthropic/Claude interest is disclosed prominently on EA2, on the methodology page and on About.
- **Critics given real space.** Krueger, Millidge and Jedlicka are represented substantively. "Welfare is not influence" is applied consistently.
- **Pre-commitment structure.** The design (readings blank until a dated rule, sensitivity tables, a retrospective as a dated snapshot) is a strong guard against fitting the rule to the data, provided the fixes above make the Stage 1 prose follow the same discipline.
- **No broken links.** All internal links and anchors resolve; I checked with a script over `_site/`.
