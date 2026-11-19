---
summary: In conversations with one AI product, Claude, this tracks how often people hand a task over entirely (automation) versus work on it together with the AI (augmentation). It is free, public, released a few times a year, and covers one vendor.
warning_sign: A rising automation share would be consistent with tasks moving from people to AI.
data_sources:
  - name: Anthropic Economic Index (Hugging Face)
    url: https://huggingface.co/datasets/Anthropic/EconomicIndex
calculation: Of the Claude.ai conversations that fit one of five ways of working with the AI, the percent in each pattern. The automation share is the two automation patterns added together; the augmentation share is the other three, so the two add up to 100. Conversations that fit no pattern, a few percent, are left out and shown in the data table. Anthropic sorts the conversations into patterns; KEEL rescales the shares so the five add to 100, adds them into the two totals, and charts all five over time.
coverage: Worldwide (Claude.ai users) · irregular releases · from a December 2024 sample
---

## Why this matters for gradual disempowerment

Gradual disempowerment is the scenario in which economies, states and cultures stop needing people and so stop serving them, without any single dramatic event [(Kulveit et al. 2025)](../sources.qmd#kulveit2025). The argument turns on decisions and tasks moving from people to AI. Among the metrics worth developing, Kulveit et al. suggest tracking the fraction of major corporate decisions made primarily by AI systems. No public data measures anything like that across society.

The Anthropic Economic Index is the nearest public proxy. It sorts conversations with Claude by how people work with the AI:

- **Automation**: the AI is asked to complete a task with little involvement from the person. Anthropic's "directive" and "feedback loop" patterns.
- **Augmentation**: the person and the AI work on it together. Anthropic's "validation," "task iteration" and "learning" patterns.

This indicator sits in the **Adoption** row, as a measure of how much of the work is handed to AI. Firm AI adoption (EA1) asks whether firms use AI at all. EA2 asks, for one product, how much of the work is handed over. It is a **leading** indicator, one that moves early.

## What it shows

- **How Claude.ai conversations that fit one of the five patterns split among them**, worldwide. The chart shows one bar per sample, placed at the date the conversations were sampled, not the date of the release. The two automation patterns are stacked at the bottom of each bar and the three augmentation patterns above them, so the number above each bar is the automation share.
- **The data come from the Anthropic Economic Index releases on Hugging Face.** These appear at irregular intervals. Each release is converted to the same five shares, and every change in how a release is built is recorded as a break in the data (below).
- **How many conversations each release analyzed.** Anthropic's reports give these sample sizes for its Claude.ai analyses:
  - 10 February 2025: 1 million conversations [(Handa et al. 2025, app. E)](../sources.qmd#handa2025).
  - 27 March 2025: 1 million conversations [(Anthropic 2025)](../sources.qmd#anthropic2025).
  - 15 September 2025: 1 million conversations [(Appel et al. 2025)](../sources.qmd#appel2025).
  - 15 January 2026: 1 million conversations [(Appel et al. 2026)](../sources.qmd#appel2026).
  - 24 March 2026: 1 million conversations sampled from Claude.ai and Anthropic's API; the report does not say how many came from Claude.ai [(Massenkoff et al. 2026a)](../sources.qmd#massenkoff2026a).
  - 26 June 2026: not reported. Anthropic says it now samples a slice of conversations every day [(Massenkoff et al. 2026b)](../sources.qmd#massenkoff2026b).

**The denominator.** Some conversations do not fit any of the five patterns, and Anthropic labels them "none" or "not classified." KEEL leaves those out, so the automation and augmentation shares always add up to 100. Some of Anthropic's report headlines count every conversation in the denominator, including those that fit no pattern. For example, the September 2025 report puts automation at about 49 percent of Claude.ai conversations [(Appel et al. 2025)](../sources.qmd#appel2025). Counting only the conversations that fit one of the five patterns, the same release gives 51.1 percent. Both are correct for their own denominators. KEEL uses the second version so that a change in how many conversations fit no pattern does not move the series.

**Breaks in the data: the method groups.** Anthropic has changed how it builds and publishes these data several times. Each change is a break, and the samples between two breaks form a method group, labelled A to D on the chart. Samples in the same group were built the same way and can be compared. A difference between groups may come from the change in method rather than from a change in how people use Claude.

- **Group A: releases of 10 February and 27 March 2025.** Anthropic's first two reports. Each published a summary table of the share of conversations in each pattern, and KEEL reads that table. The conversations come from Claude.ai Free and Pro plans: one week in December 2024, 16 to 23 December [(Handa et al. 2025, app. E)](../sources.qmd#handa2025), and the 11 days after Claude 3.7 Sonnet was launched, which Anthropic dates to February and March 2025 [(Anthropic 2025)](../sources.qmd#anthropic2025).
- **Group B: releases of 15 September 2025 and 15 January 2026.** From September 2025 Anthropic published the underlying data, broken down by country and other dimensions, instead of summary tables. KEEL computes the shares from the worldwide pattern rows. Each release covers one week of Free and Pro conversations: 4 to 11 August 2025 and 13 to 20 November 2025. Because the calculation changed, groups A and B should not be compared directly. The rise from 43 to 51 percent automation falls exactly at this break.
- **Group C: release of 24 March 2026.** The same layout as group B, but the Claude.ai data now include the Max plan as well as Free and Pro. The population of users changed. One week, 5 to 12 February 2026 [(Massenkoff et al. 2026a)](../sources.qmd#massenkoff2026a). It is the only sample in its group.
- **Group D: release of 26 June 2026, covering April and May 2026.** Anthropic now samples conversations every day and publishes whole calendar months, with its own automation and augmentation totals [(Massenkoff et al. 2026b)](../sources.qmd#massenkoff2026b). KEEL computes the shares from the five patterns and checks them against those totals. The Claude.ai data now also include Cowork, Anthropic's product for carrying out multi-step tasks. Cowork is built to need less back-and-forth, so including it may raise the automation share by itself.

This series measures AI use directly and has no history before AI. Its baseline is its own recent path, at the frequency the releases allow. Readings will use the labels Low, Rising and Pervasive, and start once the rules are fixed (see the methodology page). Until then the reading shows "Not yet reviewed."

## What it doesn't show

- **It does not show AI use across society.** This is **one vendor, one product**: conversations on Claude.ai. Its users are not a representative sample of people who use AI. Use through Anthropic's API and through other companies' products is not included. Releases analyze large samples of conversations (see "What it shows"). A large sample reduces noise, but it does not make one product's users representative of all AI users.
- **It does not show disempowerment.** A change in the series is a change in how AI is used. It is not evidence of harm, and it does not show lost leverage. A task handed to AI may free a person for work they value more.
- **It does not measure decisions.** Automation here means a task completed with little back-and-forth in a conversation. It does not show who made the decision the task served, or whether a person reviewed the result.
- **It does not separate handing over more from a change in tasks.** The overall share can rise because people hand the same tasks over more fully, or because they bring Claude more of the kinds of tasks that suit automation. Only the first is closer to people handing over work, and this series cannot tell the two apart.
- **It has no pre-AI baseline.** The series begins with a sample from 16 to 23 December 2024. There is no earlier period to compare it with, so timing cannot serve as evidence here.
- **It does not measure welfare.** People who automate more of their tasks may be better off, worse off, or neither. This series tracks how work is shared with AI. It says nothing about who gains from that.

## What would change our reading

### Alternative explanations

- **Anthropic's own product changes.** A rising automation share may reflect changes to Anthropic's products rather than society handing over more work. Tools that carry out multi-step tasks on their own, such as Cowork, are built to need less back-and-forth. Adding them to the data, or more people adopting them, can raise the automation share with no change in how willing people are to hand over work.
- **Changes in who uses Claude.** A change in the user population, such as the March 2026 plan widening, can do the same.
- **A falling share can mislead too.** A falling automation share in this one product says little if people are handing work to other AI products instead.

### What would raise or lower our confidence

**What would raise our confidence that a change reflects people handing over more work:**

- A rise in automation that holds within a stable population and product mix, between releases with no break.
- A similar rise in usage data from other AI providers, if any is published.

- Independent labor-market evidence linking automation, measured with this same data at the level of occupations (EA2 charts only the overall share), to where young workers' employment fell. One study points this way, with limits: Brynjolfsson, Chandar and Chen find that employment of US workers aged 22 to 25 fell most in occupations whose tasks had the highest share of automation in Claude conversations. In occupations with the highest share of augmentation, employment was flat or rising. The authors call their findings descriptive, not estimates of what AI caused. The pattern weakens when they control for education, some of the trends began before generative AI, and it is stronger in their payroll data than in national survey data [(Brynjolfsson et al. 2026, sec. 2.5, fig. 5, table 3)](../sources.qmd#brynjolfsson2026).

**What would lower it:**

- A rise that appears only at a product launch or a change in coverage.
- A rise that reverses in the next release.

These indicators show whether the conditions for disempowerment are present. They do not show whether it is happening.

## Data and calculation

- **Source and series.** [Anthropic Economic Index](../sources.qmd#anthropic_economic_index), published on Hugging Face. KEEL reads the worldwide Claude.ai rows of each release. Files covering Anthropic's API are a different population and are not used.
- **Units.** Percent of the Claude.ai conversations that fit one of the five patterns.
- **Frequency.** Irregular, one bar per sample, dated by the window in which the conversations were sampled. The June 2026 release gives separate figures for April and May 2026.
- **Date range.** Six releases so far. The first release, dated 10 February 2025, covers a sample from 16 to 23 December 2024 [(Handa et al. 2025, app. E)](../sources.qmd#handa2025). The latest figures cover May 2026.
- **Formula in plain words.** Each pattern's share = that pattern divided by (directive + feedback loop + validation + task iteration + learning), times 100, so the five add to 100. Automation share = directive + feedback loop. Augmentation share = validation + task iteration + learning = 100 minus the automation share. Conversations labeled "none" or "not classified" are left out. How each release's files are converted to these shares is recorded in the data's notes.

## Caveats

- **Conflict of interest.** Anthropic publishes the data and has a commercial interest in how its products are perceived. KEEL is built with assistance from Claude. KEEL uses the published data as released and documents every choice it makes in converting it.
- **Irregular releases.** Releases arrive months apart, and the gaps between them differ. Readings compare releases, whatever the time between them.
- **Changing file formats.** Each release has been structured differently. Any future change in layout will be added as a break.
- **Plans covered in January 2026.** Anthropic's January 2026 report describes its sample as Free, Pro and Max conversations [(Appel et al. 2026)](../sources.qmd#appel2026), but the release's data documentation says Free and Pro. KEEL follows the data documentation, so the plan change is marked at the 24 March 2026 release.
- **Patterns assigned automatically.** Anthropic sorts conversations into patterns automatically, using its own methods. A change in those methods could move the shares. The breaks list records only the changes the releases document.
