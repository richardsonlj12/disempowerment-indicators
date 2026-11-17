# Source reading notes

Source-reading gate (design Sec. 7b), done 2026-11-17 before the methodology page was drafted. Each source was read from the original. For each one: what it says, what the site relies on, and any limits on how the site may cite it. Figures cited on the site are also logged in `review/figure-verification.md`.

| Source | Read from | Status |
|---|---|---|
| Chooi, Lee & Li (2026) | ACL Anthology PDF, all 10 pages | Read in full |
| Moon & Boudreaux (2026), RAND RR-A4817-1 | RAND PDF, 39 pages (the HTML page blocks scripted requests; the PDF was retrieved through a web fetch and its text extracted) | Read in full (body, limitations, findings and recommendations; appendix mathematics skimmed) |
| Herdağdelen, Joren & Tamkin (2026) | Anthropic Research page and the full paper PDF | Read in full; figures checked against the paper |
| Imas (2026) | Substack post, full text visible (no paywall) | Read in full; quotations checked against the raw page text |

Nothing is listed as unread. The owner also supplied copies of the Chooi et al. and RAND PDFs. Their SHA-1 checksums match the copies retrieved from the public URLs, so both readings are of the published originals.

## Chooi, Lee & Li (2026)

Jay Chooi, Jaeho Lee and Jasmine Li, "Measuring AI-Induced Disempowerment: A Framework and Proposed Metrics", Proceedings of the Workshop on Evaluating Evaluations (EvalEval), ACL 2026, pages 227 to 236. https://aclanthology.org/2026.evaleval-1.36/ (PDF: https://aclanthology.org/2026.evaleval-1.36.pdf)

**What it says.**

- Defines AI-induced disempowerment as "the erosion of humans' ability to meaningfully shape outcomes that affect their lives, where such erosion is caused or substantially mediated by AI systems."
- Grounds the definition in Sen's model of agency. The paper measures agency, which it separates from well-being: a person can be well off and still have little agency. AI use is not disempowering when it expands a party's effective options. Displacement with no erosion and no lock-in counts as adaptation.
- Proposes a three-layer depth model:
  - **Exposure**: AI changes outcomes, by distorting human judgment or displacing human participation.
  - **Erosion**: humans lose the ability to perform tasks without AI. The key transition is from voluntary delegation to involuntary dependence.
  - **Lock-in**: the institutional infrastructure for human agency is dismantled, for example when a profession stops training juniors.
- Adds two axes: domain (economy, state, culture, after Kulveit et al.; epistemic capacity is treated as a mechanism that cuts across all three) and level of analysis (individual, institutional, civilizational).
- Finds that existing measurement "clusters almost entirely at exposure." Treats AI adoption measures as "instrumental indicators" rather than direct measurement goals.
- Proposes six metrics: centaur evaluations; disempowerment perception surveys; AI content saturation and written-output mode collapse; monitoring relative capital flow to and from human labor; human task frontier tracking; and institutional ethnography. For each metric it gives the actors best placed to run it and a feasibility rating.
  - Metric 4 is closest to this site. Its first part is labor cost share, with a difference-in-differences design across AI-exposed and less-exposed sectors. Its second part is citizen tax revenue relative to AI-generated corporate profits. The paper calls both lagging but credible. It notes that labor share has been falling since the 1980s for non-AI reasons and that fiscal data lag one to two years.
- Limitations section:
  - Causal attribution is hard, so most metrics are descriptive or comparative.
  - The jingle fallacy: "disempowerment" at different levels may be different constructs.
  - Leading indicators are hard to validate.
  - Goodhart's law and the political economy of measurement.
  - Fast-moving systems.
  - A warning against premature aggregation into a composite index.

**What the site relies on.**

- The layer names (exposure, erosion, lock-in) for the grid rows.
- The domain columns.
- The agency-versus-welfare distinction, which supports the welfare-vs-influence note.
- The case against a composite score.
- The Goodhart warning, which supports the "diagnostics, not targets" statement.
- Leading and lagging labels.
- The support for comparison designs (Metric 4) as backing for E1, G1 and the C1 contrast.

**Where the site departs from the paper.** The methodology page credits the layers as the site's own adaptation.

1. **Exposure.** The paper's exposure layer means AI already changing outcomes. The site's exposure row means AI entering a system and how far it has gone (firm adoption, E2; depth of use, E3). The paper itself treats adoption as an instrumental indicator, not a measure of exposure in its own sense. So the site's exposure row is closer to the paper's "AI inputs" than to its Layer 1.
2. **Erosion.** The paper's erosion layer is about individual capability: can a person still do the task without AI? The site's erosion row asks something different, following Kulveit et al.: is a system's dependence on human participation falling? Its measures are labor share, the labor-based share of taxes, and activity on human knowledge commons. None of the site's Release 1 indicators measures individual capability loss. This is the largest departure.
3. **Lock-in.** The paper defines lock-in as dismantled institutional infrastructure for human agency. Its examples are expertise pipelines, rising switching costs and legal architectures that presuppose AI. The site's lock-in row asks whether reduced dependence is becoming hard to restore. That is close to the paper. The row is empty in Release 1 because no operational test has been adopted (design Sec. 4.1). The paper's own examples, persistence and switching costs, are among the candidate tests.
4. **Level of analysis.** The site works mostly at the national, aggregate level and does not use the paper's individual / institutional / civilizational axis. The oversight row draws on individual-level experimental evidence (Herdağdelen et al.).
5. **Metrics.** The site implements none of the six metrics as specified. E1 and G1 are simpler national versions of the ideas behind Metric 4: no firm-level SEC data, no exposure-weighted contrast yet, and the labor tax share in place of tax relative to AI profits. The E1 industry comparison planned for Release 2 moves closer to Metric 4.

## Moon & Boudreaux (2026), RAND

Alvin Moon and Benjamin Boudreaux, "A Formal Model of How Artificial Intelligence Erodes Human Agency", RAND Corporation, Research Report RR-A4817-1, April 2026. https://www.rand.org/pubs/research_reports/RRA4817-1.html (DOI 10.7249/RRA4817-1). The HTML page returns HTTP 403 to scripted requests, as the bibliography recorded. The PDF was retrieved and its text extracted.

**What it says.**

- Defines collective agency as the capacity of humans to make decisions about shared resources, institutions and environments.
- Uses social choice theory: a decision process is modeled by its decisive coalitions, the groups whose agreement settles an outcome.
- Proposes three metrics: the distribution of decisive coalitions, minimal coalition size, and the composition of minimal coalitions.
- Formally validates three pathways to agency loss:
  - **Human disenfranchisement**: fewer humans in decision roles.
  - **AI enfranchisement**: AI entities gain decisive power.
  - **AI agenda control**: AI shapes which options reach human decision makers, for example by adding dummy alternatives that split human preferences.
- Identifies a terminal state: a single minimal coalition decisive for all choices. Uses Henry's (1974) definition of an irreversible decision, one that "significantly reduces for a long time the variety of choices that would be possible in the future."
- Argues that even a perfectly aligned AI can erode collective agency by displacing participation, because participation also preserves skills, legitimacy and optionality.
- Stated limits:
  - The scope is narrow: aggregation-type choice tasks only. An individual using a chatbot to inform a personal decision is explicitly out of scope.
  - Participation is modeled as binary, so the model cannot see formal participation that has become hollow. The authors credit Raymond Douglas for this point.
  - Arrow-type axiom problems.
- Recommendations: develop agency evaluations; set minimum human-participation thresholds in high-stakes domains; monitor coalition composition over time; assess whether organizations could restore human decision making.
- Gives no public data series and no empirical estimates.

**What the site relies on.** Background only. No figures are cited.

- The report supports the oversight row's framing: decisions moving from people to AI is the core mechanism, and no public time series measures it.
- Its irreversibility definition is a useful input to the lock-in test the owner must adopt before Release 2. That test could use persistence, or a narrowing of the options people can still choose.
- Its formal-versus-substantive limitation matches the site's caveat that the indicators show conditions under which the mechanism would operate, not proof.

**Departure.** The site does not measure decisive coalitions. No public data exist for them. The methodology page names coalition-composition tracking as a measure the oversight row could use if one appears.

## Herdağdelen, Joren & Tamkin (2026)

Amaç Herdağdelen, Hailey Joren and Alex Tamkin, "How AI agents shape experts' judgment calls", Anthropic Research, 2026-10-27, https://www.anthropic.com/research/agents-judgment-calls. Full paper: "Who's Aligned to Whom? How AI Agents Shape Experts' Research Judgment Calls", https://assets.claude.com/519c17a5d23a794e8b6d50a854048d0b61e0d73a.pdf. Herdağdelen is listed with the Anthropic Fellows Program; Joren and Tamkin with Anthropic.

**What it says (from the paper).**

- **Design.** A randomized trial with a pre-analysis plan registered at osf.io/t3q59. Data collection began before registration; the paper discloses this.
  - Causal-inference practitioners analyzed synthetic observational data with an AI coding agent (Claude Code running Claude Opus 4.8) and delivered a policy recommendation.
  - On four analytical decisions and the final recommendation, a coin flip set which of two defensible options the agent would lean toward. Participants did not know the lean was assigned.
  - 61 participants completed the task. 11 did so without using the agent and form a self-selected no-AI comparison group, which leaves 50 in the sample.
- **Main result.** On the four analytical decisions, participants went with the agent's lean 86% of the time, against 50% by chance. The registered pooled flip rate was 0.72 (95% CI 0.60 to 0.83).
- **The final recommendation.**
  - The registered estimate of the lean's direct effect on the final recommendation was a shift of 0.17 (95% CI minus 0.06 to 0.40, one-sided p 0.069). It is not statistically significant under the registered primary estimator.
  - In an exploratory, in-sample analysis, the four analytical leans alone predicted 82% of recommendations, against a 61% majority baseline.
- **Exploratory findings on how participants saw their own choices.** 77% repeated the agent's talking points when justifying their choices, and 15% mentioned the agent. More than half rated the recommendation as more their own than the agent's.
- **Stated limitations.**
  - An amplified lean: the system prompt told the agent to hold and voice a view.
  - A single task, domain and pinned agent.
  - Average effects only.
- **Proposals.** The authors propose measuring deferral in real work. They note that their own method depended on randomizing the lean, which is not feasible in real work.

**Ruling R10 check.**

| Figure in `config/curated/oversight.yaml` | Paper | Action |
|---|---|---|
| 86% | Confirmed. | Kept. |
| 50 analysts | Confirmed (61 completed; 11 without the agent). | Kept. The note's wording "11 declined the agent" was changed to match the paper. |
| 54% vs 36% rollout | The Anthropic page reports this contrast. The paper does not. The paper's registered estimate of the effect on the recommendation is a 17% shift and not statistically significant. | Removed from the note as a cited figure. The note now says why. |

The per-decision figures on the page (92, 82, 81 and 90 percent) are match rates. The paper reports per-decision flip rates instead (62 to 82 percentage points). The site cites neither.

**What the site relies on.**

- The oversight row's citation: one figure (86%) and the sample size (50).
- The point that deferral can be invisible to the people deferring.
- The authors' own call for a way to measure deferral, which is why the row reads "No public measure yet."

**Limits on citing it.**

- It is a single experiment, not a time series, so it cannot fill the row.
- It is authored at Anthropic, which also publishes E3's data. The site is built with assistance from Claude, and the agent in the study is Claude. The oversight row's citation should state the Anthropic authorship.

## Imas (2026)

Alex Imas (written with Jacob Schaal), "Has AI impacted the labor market yet?", *Ghosts of Electricity* (Substack), 2026-09-29, https://aleximas.substack.com/p/has-ai-impacted-the-labor-market. The post says its current version reflects research available through October 2026.

**What it says.**

- A "now-cast" review of the evidence, mainly on early-career workers.
- Conclusion: the best evidence supports a "narrow claim." AI "may already be affecting the hiring margin for junior white-collar roles most exposed to AI," and that attribution is contested. "Aggregate labor-market disruption has yet to appear in the data."
- Treats remote work and interest-rate exposure as unresolved confounders.
- Reads adoption as broad but shallow so far.
- Names counterforces: "messy" jobs that resist automation, new firms, and a "relational sector," where "human involvement in the role is part of the value," which "may expand as labor flows to existing relational jobs (e.g., healthcare, education)."
- Does not discuss labor share.

**What the site relies on.** The relational-sector idea, as the rival reading for E1. If work moves into relational jobs, labor's share of income could hold steady even while people's bargaining position changes, so a flat labor share is not proof that leverage is intact. The post states the relational-sector idea only briefly. The fuller argument that labor's share could stay stable after AGI is in Imas and Trammell's Dwarkesh Podcast conversation (2026-06-04, listed in the bibliography), which was not part of this reading. Site prose therefore attributes the rival reading to Imas's relational-sector argument without claiming more detail than this post gives.

**Limits on citing it.** The site cites no figures from this post. It reports figures from many studies, and any of them would have to be checked against the study itself before use (design Sec. 7b).

**Reading note.** The post was first read through a summarizing fetch tool. The raw HTML was then downloaded and converted to text, and every quotation above was checked word for word against that text.
