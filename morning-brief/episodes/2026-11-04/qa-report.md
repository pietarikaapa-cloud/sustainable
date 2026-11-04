# QA report: Morning Signal, 2026-11-04

Fact-checker: independent QA agent. Method: direct fetches are blocked in this container, so every story was checked with extended web searches on its headline, key facts and URL (domain-restricted searches where the URL did not surface at first). Window: 48h for news, 7 days for research.

## Story fact-check

| id | verdict | issue | suggested correction |
|---|---|---|---|
| ai-1 | PASS | URL confirmed (CNBC 2026-11-04). Hinojosa projected win, campaign moratorium, CoreWeave about -7% overnight (on Robinhood), Wells Fargo 27% of planned US data-centre gigawatts: all supported. Overlaps with sus-1 (midterms and data centres). | Script: say "projected" winner, and call the moratorium a campaign pledge, not a policy. Merge with sus-1 or cross-refer to it. |
| ai-2 | PASS | URL confirmed (TechCrunch 2026-11-02). Amended S-1/A wording, RSP threshold, "considering updates" to RSP, and "no model has crossed the threshold" are all supported. TechCrunch also notes an S-1 is partly marketing, and "imminently" carries no date. | Do not say Anthropic "has built" or "is about to release" a self-improving AI. It is a risk-factor disclosure about future models, and no timeline is given. |
| ai-3 | PASS | URL confirmed (CNBC 2026-11-02). About $17B Q3 revenue, $33.24B nine-month revenue and $895.4B commitments ("substantially all" compute/infrastructure) are supported. | Script: the commitments run over many years (most out to 2031–2045). They are not spending to date. Do not cite loss figures: secondary sources disagree on them. |
| ai-4 | PASS | URL confirmed (TechCrunch 2026-11-02). $115B is enterprise value. Equity value is lower (Bloomberg ~$102.6B; TechCrunch ~$80B). 4.5 shares per share. All-stock. Close expected in the first half of 2028. | Script: say "about $115 billion including debt", never "$115 billion in cash". Both stocks fell on the news. |
| ai-5 | PASS | URL confirmed (Axios 2026-11-02). Grid Protectors Program and backlash framing are supported. The Georgia pilot is up to 1 GW of curtailment. | None. Voluntary pledge, with terms negotiated per utility. Do not call it binding. |
| ai-6 | PASS | URL confirmed (CNBC 2026-11-03). Investment "could exceed" £20B (~$27B), Brookfield's estimate including chips. Over 1GW in three phases; phase 1 conditional; Drax shares up 8%. All supported. | Script: "could exceed", not "will invest". Phase 1 alone is about £2.5B and still needs approvals and a tenant. |
| ai-7 | PASS | URL confirmed (WaPo 2026-11-03). The underlying six-chatbot test (WaPo 2026-10-24) is described accurately. | None. |
| ai-8 | PASS | URL confirmed (CNBC 2026-11-02). Four agreements, ADNOC + Inception42, Machine-Readable Government, Mubadala, and a "reported" round of up to $20B are all supported. | Script: deal values were not disclosed. |
| ai-9 | PASS | URL confirmed (openai.com). Dated 2026-10-29, inside the 7-day research window. The described content matches coverage. | None. It is OpenAI describing its own system, and nobody outside has tested it. |
| ai-10 | PASS | arXiv 2611.03946 confirmed. Title, the 100-minute pilot with 12 researchers in 3 teams, the concepts and the caveat all match. | None. It is a small pilot or position paper, so do not call it a "study proving" anything. |
| media-1 | PASS | URL confirmed (TheWrap). Suits filed 2026-11-02 in Manhattan federal court. Over 30B pages, the unblockable crawler, paywall bypass, the named customers, and C&D letters in Aug 2025 and Apr 2026 are all supported. Already framed as allegations. | Script: the AI firms named are Brave's customers, not defendants. Keep "allege". |
| media-2 | PASS | URL confirmed (Dataconomy 2026-11-03). AG Szpunar opinion of 2026-11-03 in C-250/25: non-binding, and the court usually follows such opinions. Note: the official press release says the AG recommended the training questions be declared inadmissible. Reuters-based coverage, including Dataconomy, says he called training permitted under the TDM exception. | Script: keep "non-binding". On training, safer wording is "the adviser signalled training is generally covered by the data-mining exception." |
| media-3 | FIX (minor) | Content verified: Human Consent Foundation brief (~Oct 30), CAA and MAC co-signers, Hathaway/Midler/Madonna, separate WME brief. Axios story confirmed at www.axios.com. Stored URL lacked "www.". | **Applied:** URL normalised to `https://www.axios.com/2026/11/03/hollywood-new-york-times-openai-microsoft`. |
| media-4 | PASS | URL confirmed (Deadline). Small US English-language TV test, "test kitchen", mood themes with clips, no chat box, model not disclosed. All supported. | None. |
| media-5 | PASS | URL confirmed (gov.ca.gov 2026-11-02). $750M to at least $1B, sunset extended 10 years (to 2040), 5% bump for two or more productions, $100M for independents (up from $26M), above-the-line costs, federal credit call. All match the release and coverage. FilmLA shows production still down. | Script: it is a proposal and needs the legislature. Do not say "California raised" the credit. |
| media-6 | PASS | URL confirmed (Campaign). Closed Nov 2 after CFIUS clearance. FTC conditions over five years. AI growth engine with Epsilon. Sadoun's "very welcome" quote. All supported. Price is ~$2.2B (some outlets say $2.17B). | None. |
| media-7 | FIX | URL confirmed (Seoul Economic Daily 2026-11-04), but the global "11,000 job cuts" tally is single-sourced and not tied to a named tracker. A BigGo summary of the same report says 10,000. The headline presented that number as established fact. Krafton and Nexon details are supported. | **Applied:** headline now "Korean game studios hire for AI skills amid industry layoffs". Summary attributes the ~11,000 figure to the paper and flags it as unverified. Confidence lowered to `low`. |
| sus-1 | FIX | URL confirmed (Inside Climate News 2026-11-04). Supported: Dems take both chambers, majority of governorships, energy costs and data centres as issues, Castor. But these are election-night projections (ABC/AP) and races were still being counted. Strong overlap with ai-1. | **Applied:** headline now "Democrats projected to win Congress…". Summary adds "these are network projections and some races were still being counted." Script: merge with ai-1 or keep one data-centre angle only. |
| sus-2 | PASS | URL confirmed (Climate Home 2026-11-02). COP31 runs 9–20 Nov at Antalya Expo Center. Türkiye hosts, Australia presides over negotiations. Leaders' summit 11–12 Nov. Electrification pledge launch on Energy Day, 10 Nov. Five days from today to 9 Nov is correct. | Script: the pledge is voluntary (electricity at 35% of final energy by 2035). Critics note it does not require clean power. |
| sus-3 | PASS | URL confirmed (ICN 2026-11-02). Over 80% renewables target for new hub data centres and East Data West Computing (2022) are supported. | Script: 80% is a target. The Oxford Institute for Energy Studies questions how far it is being met in practice. |
| sus-4 | PASS | URL confirmed (ICN 2026-11-03; live headline "EPA Pulls the Plug on Regulating Air Pollution…"). EPA won't finalise estimating methods and will end the agreement. ~14,000 farms / ~2,600 AFOs, dairy and pork groups welcoming it, and no methane coverage are all supported. The EPA announcement was ~Oct 30 and ICN's story is within the window. | Script: EPA says Clean Air Act implementation is unchanged. Frame "rollback" as critics' view. |
| sus-5 | PASS | URL confirmed (ICN 2026-11-03). Nature Communications, CU Boulder, 133,200–449,100 (avg ~300,000) structures damaged or destroyed 2024–2060, near-tripling, vulnerability, eastern rise. All supported. | Script: "damaged or destroyed", under a no-new-adaptation scenario. |
| sus-6 | PASS | URL confirmed (ICN 2026-11-02). Greenpeace-commissioned Cerulogy modelling: 30% reported vs 0.6% actual. The UCLA GWP20/GWP100 paper is supported but is separate work and does not assess GWP*. | Script: say it is a Greenpeace-commissioned report, and do not imply UCLA backed the GWP* critique. |
| sus-7 | PASS | URL confirmed (Trellis). 82% vs ~3 in 4, 96% vs 73%, commissioners, and the practitioner-risk caveat all match the ECIU release. Note: Trellis piece is written by Futerra's CEO (a report commissioner). | Script: mention it is a report by Futerra/ECIU/CBI Economics, not independent research. |
| sus-8 | PASS | URL confirmed (Climate Home 2026-11-03). Summit was Oct 29–30 (Montréal). Alliance for the Future, minerals, grids, storage, infrastructure protection, EIB framework, LNG feasibility study. All supported. | Script: the LNG piece is only a feasibility study, and no investment was announced. |

### Duplicates and overlaps across desks
- **ai-1 and sus-1:** same event (midterm results and data-centre politics). Merge into one segment, or have sus-1 cover only the climate-policy outlook.
- **AI energy cluster:** ai-3 (compute commitments), ai-5 (OpenAI grid pledge), ai-6 (Drax), sus-3 (China renewables) and sus-2 (electrification). These are distinct stories but share a theme. Avoid repeating "AI's energy footprint" lines in each.
- **Publisher vs AI cluster:** media-1 (Brave), media-2 (Gemini AG opinion), media-3 (NYT v OpenAI amicus) and ai-7 (chatbot voter guides). Distinct stories. Frame them together if needed, but do not conflate the cases.

## Summary

- 25 stories checked: **22 PASS, 3 FIX, 0 DROP**. Every URL surfaced in search results as the described article, and all are within the window. ai-9 is research dated 2026-10-29, inside 7 days.
- Special-attention items: ai-2 and ai-3 (Anthropic S-1/A) are accurate as written. ai-4 is $115B *enterprise value*, all-stock. ai-6's $27B is "could exceed £20B", converted. media-5's figures match the governor's release. media-7's 11,000 figure is weakly sourced and has been hedged. sus-1 needs "projected" and has been hedged. sus-2's dates and location are correct.

### Changes applied to JSON
1. `stories-sustainability.json` sus-1: the headline now says "Democrats projected to win Congress in midterms shaped by energy bills and data centres". The summary appends a note that these are network projections and that some races were still being counted.
2. `stories-media.json` media-7: the headline is now "Korean game studios hire for AI skills amid industry layoffs". The first summary sentence is rewritten to attribute the ~11,000 figure to Seoul Economic Daily and flag it as unverified (another summary says 10,000). Confidence is now `medium` → `low`.
3. `stories-media.json` media-3: URL normalised to `https://www.axios.com/...`.

All three JSON files validate. Note: the files were re-serialised with 2-space indentation.

### Script writer: do not say
- That Anthropic "has" or "is about to release" self-improving AI. Say the filing warns future models *could* meet its threshold, that no model has crossed it, and give no date.
- "$895 billion spent". These are multi-year commitments.
- "Marvell pays $115 billion in cash". It is ~$115B enterprise value, all-stock.
- "Brookfield will invest $27 billion". It "could exceed" £20B, and phase 1 is conditional.
- "Democrats won the Senate/House" as final results. Say "projected".
- "Hinojosa will ban data centres". A moratorium was a campaign pledge.
- "California raised its film tax credit to $1B". It is a proposal only.
- "The EU court ruled against Google". It is a non-binding Advocate General opinion.
- "Brave infringed copyright" or "Anthropic/Perplexity were sued". These are allegations against Brave only.
- "Game industry has cut 11,000 jobs" as fact. Attribute it to the Seoul Economic Daily, or omit it.
- That UCLA researchers backed the Greenpeace GWP* critique.
- That the COP31 electrification pledge commits countries to clean power. It does not.
