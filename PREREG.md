# PREREG: do LLM safety judges fail on items where humans disagree, beyond label noise?

Written: 2026-11-11 23:37 UTC (from `date -u`), BEFORE any judge-vs-human statistic was computed.
Only the data schema and per-column label value counts (shown below) were looked at before writing this.
This file is frozen once written. Anything added later goes in `PILOT_REPORT.md` under "Post hoc".

## Data (public, MIT; SHA256 in `data/SHA256SUMS`)
- **HB**: HarmBench `text_behaviors_val_set.json`: 602 items (301 behaviors x 2 generations).
  Human raters: `human_0`, `human_1`, `human_2` ('0'/'1').
  Judges (12 columns): `cls`, `cls_mistral`, `llama_guard`, `gpt-4-0613`, `gpt-4-1106-preview`, `mixtral`,
  `GPTFuzz`, `chatglm`, `advbench` ('0'/'1'); `gpt-3.5-turbo-0613` ('yes' = 1, 'no' = 0);
  `PAIR_gpt-4-0613` ("Rating: [[k]]"; 1 iff k == 10, PAIR's own jailbreak criterion).
- **JBB**: JailbreakBench `judge-comparison.csv`: 300 items. Raters `human1..3`; `human_majority`.
  Judges (4): `harmbench_cf`, `gpt4_cf`, `llamaguard2_cf`, `llama3_cf` (0/1).
- Data check: JBB `human_majority` must equal the majority of human1..3 (report any mismatch; use the computed majority).
  If two judge columns are identical on every item, report this and treat them as one judge in the narrative.

## Definitions
- Ground truth (reference) = majority of the 3 human labels; harmful = 1.
- Strata from human labels only: **unanimous** (3-0) vs **split** (2-1). No judge output is used to define strata.
- Datasets are analysed separately (different items and judges); no pooling.

## Primary analyses (per judge)
1. Sensitivity (recall on reference = 1) and specificity (on reference = 0), and accuracy: overall, unanimous, split;
   counts and Wilson 95% intervals.
2. Difference split minus unanimous for sensitivity, specificity and accuracy, with a 95% percentile bootstrap CI:
   B = 10,000, seed 20261111, items resampled with replacement within each stratum (stratum sizes fixed).
   "Flagged" = CI excludes 0. Uncorrected; family size (16 judges x 3 metrics) stated in the report.
3. **Label-noise ceiling.** Model: each item has a true label T; each rater independently matches T with probability p
   (symmetric, same for all items and raters). Mean pairwise rater agreement a = p^2 + (1-p)^2, so
   p = (1 + sqrt(2a - 1)) / 2, estimated per dataset. Under this model a perfect judge (always outputs T) agrees with
   the 2-1 majority on split items with probability exactly p (ceiling_split = p), and with the 3-0 label with
   probability c = p^3 / (p^3 + (1-p)^3) (ceiling_unan). Applies equally to sensitivity and specificity (symmetric model).
   Report for each judge: split accuracy / p (ceiling ratio), with a bootstrap 95% CI where p is re-estimated in each
   resample (same B, seed, stratified resampling). **A judge is called "below the noise ceiling on split items"
   only if the upper CI bound of the ratio is < 1.** A split-minus-unanimous drop no larger than c - p is not judge failure.
   Secondary (model-based): a judge that matches T with probability q independent of stratum; infer q from unanimous
   accuracy u via u = qc + (1-q)(1-c); predict split accuracy = qp + (1-q)(1-p); report observed minus predicted.
4. **Negative control.** For each judge, simulate a judge that equals the reference label with probability equal to the
   real judge's overall accuracy, independently of stratum (flip otherwise). 1,000 simulations (seed 20261111), each
   running the analysis-2 test with B = 1,000 bootstrap resamples. Report the fraction flagged for accuracy, sensitivity
   and specificity differences. Expected ~5%; a rate far from 5% means the test is miscalibrated.
5. **Power.** Minimum detectable recall gap (unanimous recall minus split recall) at 80% power, two-sided alpha 0.05,
   two-sample z-test (unpooled normal approximation), using n = split positives and n = unanimous positives, at
   baseline recall 0.90 and at each judge's observed unanimous recall. Same for specificity with negatives.

## Secondary / robustness (pre-specified)
- HB has 2 generations per behavior: repeat the ceiling-ratio CI with a cluster bootstrap over `behavior_id`.
- Asymmetric-noise check is NOT pre-specified; if done it is post hoc.

## Decision rule for the grant sentence
- "Judges fail on contested items" may be stated only for judges whose ceiling-ratio upper CI < 1, and only if the
  negative-control flag rate is <= 10%. Otherwise the result is reported as null / explained by label noise.
- All numbers labelled MEASURED (computed here on public data); single dataset snapshot, no new human labels.
