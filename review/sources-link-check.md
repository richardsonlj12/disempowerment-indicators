# Sources link check

Every URL and DOI in `references/keel.json`, requested on 2026-11-18 with a browser-like User-Agent, following redirects (`python -m indicators.bibliography check-links`). "Owner browser check" means the site refused or did not answer a scripted request; the owner must open it in a browser.

Summary: OK: 28 · owner browser check: 6 · broken: 0

| key | URL | status | HTTP | notes |
|---|---|---|---|---|
| allen2026 | <https://doi.org/10.17016/2380-7172.4032> | OK | 200 | redirected to https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html |
| allen2026 | <https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html> | OK | 200 |  |
| brynjolfsson2026 | <https://digitaleconomy.stanford.edu/app/uploads/2026/08/Canaries_August2026.pdf> | OK | 200 |  |
| census2025 | <https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf> | OK | 200 |  |
| chooi2026 | <https://doi.org/10.18653/v1/2026.evaleval-1.36> | OK | 200 | redirected to https://aclanthology.org/2026.evaleval-1.36/ |
| chooi2026 | <https://aclanthology.org/2026.evaleval-1.36/> | OK | 200 |  |
| drago2025 | <https://intelligence-curse.ai/> | OK | 200 |  |
| handa2025 | <https://doi.org/10.48550/arXiv.2503.04761> | OK | 200 | redirected to https://arxiv.org/abs/2503.04761 |
| handa2025 | <https://arxiv.org/abs/2503.04761> | OK | 200 |  |
| herdagdelen2026a | <https://www.anthropic.com/research/agents-judgment-calls> | OK | 200 |  |
| herdagdelen2026b | <https://assets.claude.com/519c17a5d23a794e8b6d50a854048d0b61e0d73a.pdf> | OK | 200 |  |
| imas2026 | <https://aleximas.substack.com/p/has-ai-impacted-the-labor-market> | OK | 200 |  |
| jedlicka2026 | <https://doi.org/10.48550/arXiv.2608.03904> | OK | 200 | redirected to https://arxiv.org/abs/2608.03904 |
| jedlicka2026 | <https://arxiv.org/abs/2608.03904> | OK | 200 |  |
| krueger2025 | <https://www.lesswrong.com/posts/hP2Pms2acPW6eeD6B/a-few-quick-thoughts-on-measuring-disempowerment> | OK | 200 |  |
| kulveit2025 | <https://doi.org/10.48550/arXiv.2501.16946> | OK | 200 | redirected to https://arxiv.org/abs/2501.16946 |
| kulveit2025 | <https://arxiv.org/abs/2501.16946> | OK | 200 |  |
| millidge2025 | <https://www.beren.io/2025-11-23-Gradual-Disempowerment-Might-Not-Be-So-Bad/> | OK | 200 |  |
| miller2025 | <https://diff.wikimedia.org/2025/10/17/new-user-trends-on-wikipedia/> | OK | 200 |  |
| moon2026 | <https://doi.org/10.7249/RRA4817-1> | OK | 200 | redirected to https://www.rand.org/pubs/research_reports/RRA4817-1.html |
| moon2026 | <https://www.rand.org/pubs/research_reports/RRA4817-1.html> | OK | 200 |  |
| richardson2026 | <https://richardsonlj.substack.com/p/no-robot-uprising-required> | OK | 200 |  |
| sajadieh2026 | <https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_8_policy_and_governance.pdf> | OK | 200 |  |
| anthropic_economic_index | <https://huggingface.co/datasets/Anthropic/EconomicIndex> | OK | 200 |  |
| bls_labor_share | <https://www.bls.gov/productivity/home.htm> | owner browser check | 403 | blocked or unavailable to scripts |
| census_btos | <https://www.census.gov/hfp/btos> | OK | 200 | redirected to https://www.census.gov/hfp/btos/ |
| fred_cpatax | <https://fred.stlouisfed.org/series/CPATAX> | owner browser check | - | ReadTimeout |
| fred_gdp | <https://fred.stlouisfed.org/series/GDP> | owner browser check | - | ReadTimeout |
| fred_personal_current_taxes | <https://fred.stlouisfed.org/series/W055RC1Q027SBEA> | owner browser check | - | ReadTimeout |
| fred_social_insurance_contributions | <https://fred.stlouisfed.org/series/W782RC1Q027SBEA> | owner browser check | - | ReadTimeout |
| fred_tax_receipts | <https://fred.stlouisfed.org/series/W054RC1Q027SBEA> | owner browser check | - | ReadTimeout |
| oecd_revenue_statistics | <https://data-explorer.oecd.org/?df[ds]=DisseminateFinalDMZ&df[id]=DSD_REV_COMP_OECD%40DF_RSOECD&df[ag]=OECD.CTP.TPS> | OK | 200 | redirected to https://data-explorer.oecd.org/?df%5Bds%5D=DisseminateFinalDMZ&df%5Bid%5D=DSD_REV_COMP_OECD%40DF_RSOECD&df%5Bag%5D=OECD.CTP.TPS |
| stackexchange_api | <https://api.stackexchange.com/docs/questions> | OK | 200 |  |
| wikimedia_analytics_api | <https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/> | OK | 200 |  |
