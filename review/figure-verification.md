# Figure verification

Every figure that appears on the site is re-checked against its primary source and logged here. Secondary-only figures are never published.

| figure | where used | primary-source URL | date checked | checked by |
|---|---|---|---|---|
| Labor share, nonfarm business, 2026Q2, two vintages: 52.8 first published (per the BLS TED article); 53.3 current per PRS85006174 as of 2026-11-17 (revised; 2026Q1 54.0, 2026Q3 53.0). The site uses the latest revised data, so 53.3. | E1 chart and tests | https://api.bls.gov/publicAPI/v1/timeseries/data/PRS85006174?startyear=2026&endyear=2026 (BLS series PRS85006174, labor share in percent; page: https://www.bls.gov/lpc/) | 2026-11-17 | Task 5 implementer (script, BLS API v1) |
| Labor share series ID choice: PRS85006174 (percent level). FRED has only the index PRS85006173 (2017=100), so FRED cannot supply the percent level. | E1 | https://api.bls.gov/publicAPI/v1/timeseries/data/PRS85006173 (index, for comparison) | 2026-11-17 | Task 5 implementer |
| Profit share = CPATAX / GDP x 100; 2026Q2 = 3877.434 / 32563.030 = 11.91 percent | E1 context | https://fred.stlouisfed.org/series/CPATAX and https://fred.stlouisfed.org/series/GDP | 2026-11-17 | Task 5 implementer |
| US labor-based tax share = (W055RC1Q027SBEA personal current taxes + W782RC1Q027SBEA contributions for government social insurance) / (W054RC1Q027SBEA government current tax receipts + W782RC1Q027SBEA) x 100; 2025Q3 = 64.27 percent | G1 primary | https://fred.stlouisfed.org/series/W055RC1Q027SBEA , https://fred.stlouisfed.org/series/W782RC1Q027SBEA , https://fred.stlouisfed.org/series/W054RC1Q027SBEA | 2026-11-17 | Task 5 implementer |
| OECD average, 2023, (PIT 1100 + SSC 2000) share of total tax revenue = 23.736 + 25.463 = 49.20 percent (plan: 49.2 +/- 0.3; OK) | G1 context | https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_REV_COMP_OECD@DF_RSOECD,2.0/OECD_REP.TAX_REV.S13.T_1100+T_2000._T.PT_OTR_SECTOR.A?startPeriod=2023&endPeriod=2023 (explorer: https://data-explorer.oecd.org/?df[ds]=DisseminateFinalDMZ&df[id]=DSD_REV_COMP_OECD%40DF_RSOECD&df[ag]=OECD.CTP.TPS) | 2026-11-17 | Task 5 implementer (script, OECD SDMX) |
| OECD United States, 2023: PIT 39.968 + SSC 23.506 = 63.47 percent (USA data through 2024; OECD average through 2023) | G1 context | same OECD dataflow, key USA.TAX_REV.S13.T_1100+T_2000._T.PT_OTR_SECTOR.A | 2026-11-17 | Task 5 implementer |

Notes:

- The bls.gov and oecd.org web pages return 403 to scripted requests, so those page URLs were not opened by script; the API endpoints were. A human should open https://www.bls.gov/lpc/ and the OECD terms page once and confirm the license wording before launch.
- The OECD average (OECD_REP) is used as published; the percentage categories are the dataset's own.
