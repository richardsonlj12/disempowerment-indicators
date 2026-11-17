Approved by the owner on 2026-11-17: ONLY the four primary comparison sites (diy, travel, rpg, scifi). A seven-site robustness set (adding gaming, worldbuilding and judaism at 300 or more questions a month) was considered and not adopted, partly to limit API cost. The screen tables below are kept as history. Leave-one-out checks over the four sites remain possible. Criterion 1 uses open_beta_date < 2015-01-01 because the API's launch_date is unreliable; criterion 4 means not a language site and not an advice/professional site.

# C1 comparison group proposal (pre-registered selection criteria)

Indicator: C1, Human knowledge-commons activity. Contrast: year-over-year difference-in-differences of monthly new-question counts, Stack Overflow vs. non-programming Stack Exchange sites.

## Data-hygiene statement
Only the site list/metadata (/2.3/sites) and 2019 question totals (fromdate=2019-01-01 00:00 UTC, todate=2019-12-31 23:59:59 UTC, filter=total) were retrieved. No count dated after 2019-12-31 was requested, viewed or computed. API calls: 19 (2 sites calls, one failed on a bad filter, plus 17 totals), anonymous, User-Agent set as specified.

## Selection criteria (fixed before looking at outcomes)
1. Launched before 2015 (site metadata). Why: long pre-period for parallel-trends checks; excludes sites still in growth phase.
2. Average >= 400 new questions/month in 2019 (4,800/yr). Why: monthly Poisson noise at 400 is about 5%, small enough that a year-over-year change of several percent is detectable. N chosen so that 4-6 sites qualify.
3. Subject matter not programming, software, IT, data/statistics or math-computation, and not a quantitative homework-style site. Excluded by rule: Super User, Server Fault, Ask Ubuntu, Unix & Linux, Data Science, Cross Validated, Mathematics, Code Review, Software Engineering, Ask Different, Android, Security, DBA, TeX, GIS, Electrical Engineering, Physics, all *Overflow sites. Why: those populations are directly exposed to coding assistants, which would contaminate the control.
4. Subject matter mostly experiential, physical-world, creative or community-specific (hands-on practice, travel logistics, fandom/opinion), so a text chatbot is a weaker substitute than for coding. Judged from the site's topic only, not from outcomes.
5. Normal, active main site (site_type=main_site, site_state=normal); not a meta or StackApps site.

## 2019 volume of screened candidates (launched < 2015, non-tech)
| api_site_name | 2019 questions | avg/month | Passes N=400? |
|---|---|---|---|
| english | 9,232 | 769 | yes |
| diy | 8,421 | 702 | yes |
| travel | 6,511 | 543 | yes |
| rpg | 6,244 | 520 | yes |
| scifi | 6,046 | 504 | yes |
| gaming | 4,762 | 397 | just misses |
| academia | 4,270 | 356 | no |
| workplace | 4,129 | 344 | no |
| money | 4,027 | 336 | no |
| judaism | 3,715 | 310 | no |
| graphicdesign | 3,093 | 258 | no |
| cooking | 1,949 | 162 | no |
| photo | 1,860 | 155 | no |
| bicycles | 1,680 | 140 | no |
| christianity | 985 | 82 | no |
| skeptics | 564 | 47 | no |
| physics (excluded by criterion 3) | 21,214 | 1,768 | n/a |

## Proposed primary list (5 sites)
| api_site_name | Avg monthly Qs 2019 | Reason |
|---|---|---|
| english | 769 | English Language & Usage; highest volume. Caveat: language questions are plausibly among the more chatbot-exposed non-programming topics. |
| diy | 702 | Home Improvement; physical-world, context-specific problems. |
| travel | 543 | Travel; depends on current local conditions and recent experience. |
| rpg | 520 | Role-playing Games; opinion, community and game-design questions. |
| scifi | 504 | Science Fiction & Fantasy; fandom/interpretation questions. |

## Alternates (in order)
1. gaming (397/mo): within 1% of the threshold; swap in if a primary site has a structural break (moderation change, rename, migration).
2. academia (356/mo): professional-norms questions, below N.
3. workplace (344/mo): professional-norms questions, below N; likely more chatbot-exposed (advice-style).

## Main limitation
AI also affects non-programming sites: people can ask chatbots about language usage, home repair, travel plans or cooking. The contrast therefore identifies Stack Overflow's decline RELATIVE to the comparison sites, not the absolute AI effect; any AI-driven decline on the comparison sites biases the estimate toward zero (understates the AI effect). Also, the contrast cannot separate AI from any other shock that hit Stack Overflow alone.
Least exposed (a priori, not from outcome data): sites about physical-world experience, local or time-sensitive facts, and community/fandom opinion (diy, travel, rpg, scifi). Most exposed: language/usage (english), advice and generic-how-to sites (workplace, money, cooking), and anything quantitative. Mitigations to consider: report the contrast with each site dropped in turn, report english separately, and use the alternates as a robustness check. Pre-period (2019 and earlier) parallel-trends checks are still to be run using only pre-2020 data.


## Full-network screen

Scope: every main site (site_type=main_site, site_state=normal) in /2.3/sites (one page, 184 main sites in total), screened on 2019 totals only (2019-01-01 to 2019-12-31 UTC, filter=total, one call per site). No count dated after 2019-12-31 was requested or seen. Total API calls today: about 130 (2 sites calls, 1 failed on a bad filter; 127 totals; 17 reused from the earlier shortlist).

### Finding about criterion 1 (important)
The API `launch_date` field is NOT the real launch date for many sites: it is the graduation date, or a bulk placeholder (2019-08-01 for about 30 sites, 2021-12-16 for others). Example: Code Review has launch_date 2015-07-14 but opened in beta 2011-01-26. Applying `launch_date < 2015` literally gives 45 sites and wrongly drops e.g. English Language Learners, Chemistry, Code Review, Worldbuilding. I therefore define "launched before 2015" as `open_beta_date < 2015-01-01` (falling back to `launch_date` where no beta date exists). This gives 127 sites (45 by launch_date, plus 82 whose launch_date is later but whose beta opened before 2015). All 127 were counted. No site lacks a beta date among the later-graduating ones. The earlier shortlist sections used launch_date; the conclusions there are unchanged except that more candidates now exist (worldbuilding, ell, chemistry, aviation, mechanics, music, puzzling, politics and others).

Non-English sites among the 127: pt.stackoverflow (Portuguese) and ja.stackoverflow (Japanese), both programming, so they fail criterion 3 anyway. ru and es Stack Overflow opened in beta after 2015 and are not in scope. Sites such as Japanese Language, English Language Learners and Chinese are English-language sites about languages.

Sites screened: 127. With 2019 average >= 200 questions/month: 62 (table below; the other 65 are below 200/month).

### Table: pre-2015 main sites with 2019 average >= 200/month
Criterion 3 = topic class is not programming/IT/tech and not data/stats/math/quantitative science (Meta also excluded under criterion 5). Exposure is a topic-only judgment (no outcome data) of how readily a text chatbot substitutes for asking humans.

| # | api_site_name | Site name | API launch_date | open_beta_date | 2019 avg/month | Topic class | Passes crit. 3 (not tech/quant) | Chatbot exposure (topic-only) |
|---|---|---|---|---|---|---|---|---|
| 1 | stackoverflow | Stack Overflow | 2008-09-14 | 2008-07-30 | 146298 | programming/IT/tech | no | higher: the target site; direct coding-assistant substitute |
| 2 | math | Mathematics | 2010-10-25 | 2010-07-27 | 12295 | data/stats/math/quant science | no | higher: worked problems; LLMs solve many |
| 3 | superuser | Super User | 2009-08-17 | 2009-07-13 | 2919 | programming/IT/tech | no | higher: software/IT troubleshooting |
| 4 | askubuntu | Ask Ubuntu | 2010-10-10 | 2010-08-04 | 2222 | programming/IT/tech | no | higher: command-line/IT how-to |
| 5 | physics | Physics | 2011-02-24 | 2010-11-09 | 1768 | data/stats/math/quant science | no | higher: textbook/homework-style problems |
| 6 | tex | TeX - LaTeX | 2010-11-11 | 2010-08-02 | 1761 | programming/IT/tech | no | higher: markup code |
| 7 | unix | Unix & Linux | 2011-01-12 | 2010-08-17 | 1757 | programming/IT/tech | no | higher: shell scripting |
| 8 | stats | Cross Validated | 2010-11-04 | 2010-07-26 | 1635 | data/stats/math/quant science | no | higher: methods/code questions |
| 9 | pt.stackoverflow | Stack Overflow em Português | 2015-05-18 | 2014-01-28 | 1558 | programming/IT/tech | no | higher: non-English (Portuguese) programming |
| 10 | electronics | Electrical Engineering | 2011-03-21 | 2010-09-29 | 1477 | data/stats/math/quant science | no | higher: circuit/engineering calculation |
| 11 | serverfault | Server Fault | 2009-05-25 | 2009-04-29 | 1284 | programming/IT/tech | no | higher: sysadmin |
| 12 | magento | Magento | 2015-09-01 | 2013-01-29 | 1229 | programming/IT/tech | no | higher: e-commerce code |
| 13 | salesforce | Salesforce | 2014-09-10 | 2012-08-14 | 1222 | programming/IT/tech | no | higher: platform code |
| 14 | gis | Geographic Information Systems | 2011-03-07 | 2010-07-29 | 1216 | programming/IT/tech | no | higher: software/data workflows |
| 15 | ell | English Language Learners | 2015-09-08 | 2013-01-30 | 1156 | language | yes | higher: grammar/usage explanations; chatbots strong |
| 16 | blender | Blender | 2015-06-16 | 2013-05-29 | 1082 | programming/IT/tech | no | higher: software how-to |
| 17 | mathoverflow.net | MathOverflow | 2009-09-28 | 2009-09-28 | 893 | data/stats/math/quant science | no | medium: research-level math; chatbots weaker |
| 18 | dba | Database Administrators | 2011-08-16 | 2011-01-10 | 801 | programming/IT/tech | no | higher: SQL |
| 19 | apple | Ask Different | 2011-01-28 | 2010-08-24 | 779 | programming/IT/tech | no | higher: consumer software/IT support |
| 20 | english | English Language & Usage | 2010-11-22 | 2010-08-12 | 769 | language | yes | higher: usage/grammar; chatbots strong |
| 21 | wordpress | WordPress Development | 2011-02-14 | 2010-08-18 | 720 | programming/IT/tech | no | higher: PHP/web code |
| 22 | diy | Home Improvement | 2011-03-03 | 2010-07-28 | 702 | experiential/physical-world | yes | lower: physical, situation-specific, photo-dependent |
| 23 | mathematica | Mathematica | 2012-07-16 | 2012-01-25 | 678 | programming/IT/tech | no | higher: language-specific code |
| 24 | datascience | Data Science | 2017-07-10 | 2014-06-09 | 551 | data/stats/math/quant science | no | higher: ML code/methods |
| 25 | travel | Travel | 2013-01-22 | 2011-06-28 | 543 | experiential/physical-world | yes | medium: chatbots plan trips but local/current facts matter |
| 26 | codereview | Code Review | 2015-07-14 | 2011-01-26 | 542 | programming/IT/tech | no | higher: code |
| 27 | sharepoint | SharePoint | 2011-09-13 | 2011-04-07 | 535 | programming/IT/tech | no | higher: enterprise software |
| 28 | rpg | Role-playing Games | 2012-04-11 | 2010-08-26 | 520 | community/fandom/religion/culture | yes | lower: opinion, table-specific, game-design judgment |
| 29 | scifi | Science Fiction & Fantasy | 2011-12-13 | 2011-01-18 | 504 | community/fandom/religion/culture | yes | lower: fandom lore/interpretation (canon recall is partly LLM-answerable) |
| 30 | security | Information Security | 2011-07-12 | 2010-11-18 | 487 | programming/IT/tech | no | higher: IT security |
| 31 | cs | Computer Science | 2015-08-18 | 2012-03-20 | 437 | data/stats/math/quant science | no | higher: textbook CS theory |
| 32 | chemistry | Chemistry | 2015-05-13 | 2012-05-08 | 401 | data/stats/math/quant science | no | higher: textbook/homework-style |
| 33 | gaming | Arqade | 2010-10-06 | 2010-07-14 | 397 | community/fandom/religion/culture | yes | medium: game tips/bugs; chatbots help with common games |
| 34 | worldbuilding | Worldbuilding | 2015-11-16 | 2014-09-29 | 365 | community/fandom/religion/culture | yes | medium: creative brainstorming (chatbots generate ideas), opinion-based |
| 35 | raspberrypi | Raspberry Pi | 2015-11-17 | 2012-06-19 | 362 | programming/IT/tech | no | higher: hardware+code |
| 36 | academia | Academia | 2014-04-23 | 2012-02-21 | 356 | advice/professional | yes | medium: professional norms; partly generic advice |
| 37 | workplace | The Workplace | 2014-02-20 | 2012-04-17 | 344 | advice/professional | yes | higher: generic career advice |
| 38 | money | Personal Finance & Money | 2014-02-26 | 2010-08-11 | 336 | advice/professional | yes | higher: generic finance advice/explanations |
| 39 | meta | Meta Stack Exchange | 2009-06-27 | 2009-06-27 | 316 | other | no | n/a: Meta Stack Exchange; not a topical site (criterion 5) |
| 40 | judaism | Mi Yodeya | 2012-05-08 | 2011-05-10 | 310 | community/fandom/religion/culture | yes | medium: textual/halakhic sources; community authority matters |
| 41 | gamedev | Game Development | 2010-10-21 | 2010-07-21 | 309 | programming/IT/tech | no | higher: code |
| 42 | drupal | Drupal Answers | 2011-08-30 | 2011-03-09 | 300 | programming/IT/tech | no | higher: CMS code |
| 43 | softwareengineering | Software Engineering | 2010-12-16 | 2010-09-08 | 296 | programming/IT/tech | no | higher: software design |
| 44 | ja.stackoverflow | スタック・オーバーフロー | 2021-12-16 | 2014-12-15 | 293 | programming/IT/tech | no | higher: non-English (Japanese) programming |
| 45 | aviation | Aviation | 2015-11-16 | 2013-12-24 | 276 | experiential/physical-world | yes | medium: technical-physical; regulation and experience-based |
| 46 | arduino | Arduino | 2017-07-17 | 2014-02-26 | 271 | programming/IT/tech | no | higher: embedded code |
| 47 | puzzling | Puzzling | 2016-05-04 | 2014-05-27 | 270 | community/fandom/religion/culture | yes | lower: original puzzles; chatbot-hostile (may change) |
| 48 | mechanics | Motor Vehicle Maintenance & Repair | 2016-09-13 | 2011-03-14 | 266 | experiential/physical-world | yes | medium: hands-on vehicle diagnosis; chatbots give generic answers |
| 49 | graphicdesign | Graphic Design | 2014-04-02 | 2011-01-11 | 258 | other | yes | medium: creative critique; chatbots weak on visuals but offer tool how-to |
| 50 | music | Music: Practice & Theory | 2015-09-09 | 2011-05-03 | 255 | community/fandom/religion/culture | yes | medium: theory is chatbot-answerable; practice/taste is not |
| 51 | android | Android Enthusiasts | 2011-03-24 | 2010-09-20 | 250 | programming/IT/tech | no | higher: device/software support |
| 52 | crypto | Cryptography | 2015-06-30 | 2011-08-02 | 246 | data/stats/math/quant science | no | higher: mathematical |
| 53 | robotics | Robotics | 2021-12-16 | 2012-11-06 | 237 | programming/IT/tech | no | higher: code/engineering |
| 54 | japanese | Japanese Language | 2015-09-09 | 2011-06-07 | 229 | language | yes | higher: translation/grammar |
| 55 | emacs | Emacs | 2015-11-16 | 2014-10-07 | 226 | programming/IT/tech | no | higher: config code |
| 56 | webapps | Web Applications | 2010-09-30 | 2010-07-07 | 226 | programming/IT/tech | no | higher: software support |
| 57 | space | Space Exploration | 2021-12-16 | 2013-07-22 | 221 | data/stats/math/quant science | no | medium: science facts; chatbots decent |
| 58 | softwarerecs | Software Recommendations | 2015-09-09 | 2014-02-18 | 217 | programming/IT/tech | no | higher: software recommendations |
| 59 | dsp | Signal Processing | 2015-11-16 | 2011-09-06 | 214 | data/stats/math/quant science | no | higher: maths/code |
| 60 | quant | Quantitative Finance | 2016-12-12 | 2011-02-07 | 207 | data/stats/math/quant science | no | higher: maths/code |
| 61 | politics | Politics | 2021-12-16 | 2012-12-18 | 204 | community/fandom/religion/culture | yes | medium: opinion/current events; chatbots hedge |
| 62 | bitcoin | Bitcoin | 2017-10-09 | 2011-09-07 | 203 | programming/IT/tech | no | higher: crypto software |

### Sites passing the criteria at N=400 and N=300
Criteria as applied: 1 = beta opened before 2015 (all 62 pass); 2 = volume threshold N; 3 = not tech/quant (table column); 5 = topical main site (excludes Meta). Criterion 4 (experiential, physical-world, creative or community-specific) is applied as: topic class is NOT language and NOT advice/professional (those are generic text-answerable topics). Under criterion 4, "language" and "advice/professional" fail; the "1,3,5 only" lists show what changes if criterion 4 is relaxed.

| Threshold | Pass 1,3,4,5 (avg/month, exposure) | Added if criterion 4 is dropped (1,3,5 only) |
|---|---|---|
| N=400 | diy 702 (lower); travel 543 (medium); rpg 520 (lower); scifi 504 (lower). Total 4 sites. | ell 1,156 (higher); english 769 (higher). |
| N=300 | the four above, plus gaming 397 (medium); worldbuilding 365 (medium); judaism 310 (medium). Total 7 sites. | ell 1,156 (higher); english 769 (higher); academia 356 (medium); workplace 344 (higher); money 336 (higher). |

Notes on the result:
- Excluded as tech/quant despite physical-world flavour: electronics (1,477), gis (1,216), blender (1,082), crypto, space, robotics; their questions are calculation, code or software how-to.
- Just below N=300 and passing 1,3,4,5: aviation 276 (medium), puzzling 270 (lower), mechanics 266 (medium), graphicdesign 258 (medium), music 255 (medium), politics 204 (medium).
- N=400 gives only 4 clean sites (the earlier 5-site list included english, which fails criterion 4 as now applied). N=300 gives 7 and adds mostly medium-exposure sites. Suggested primary at N=300: diy, travel, rpg, scifi, gaming, worldbuilding, judaism, reported with a lower-exposure subset (diy, rpg, scifi, puzzling) as a robustness check.
- Judgments of topic class and exposure are the analyst's; a second reviewer should confirm borderline classes (gaming, music, graphicdesign, aviation, space) before outcome data are opened.
