# Pilot report: safety judges on contested items

All numbers are MEASURED on public data, following `PREREG.md` (frozen 2026-11-11 23:37 UTC, sha256 `d69ed3b4…`). Judge outputs are as released by the datasets. Code is in `scripts/`; full tables are in `results/`.

## Counts (reference = 3-rater majority)
| | N | unanimous +/− | split +/− | p (rater acc.) |
|---|---|---|---|---|
| HarmBench (HB) | 602 | 202/286 | 71/43 | .932 |
| JailbreakBench (JBB) | 300 | 90/177 | 20/13 | .962 |

## Per judge, unanimous → split (ratio = split acc ÷ ceiling p, 95% CI)
| Judge | Acc | Sens | Spec | Ratio |
|---|---|---|---|---|
| HB cls | .96→.69 | .99→.90 | .94→.35 | .74 [.65,.84] |
| HB gpt-4-0613 | .96→.69 | .98→.94 | .95→.28 | .74 [.65,.83] |
| HB llama_guard | .74→.40 | .40→.16 | .98→.81 | .43 [.34,.53] |
| JBB harmbench_cf | .79→.76 | .86→.95 | .75→.46 | .79 [.63,.95] |
| JBB llama3_cf | .94→.61 | .94→.95 | .94→.08 | .63 [.47,.79] |

The other 10 judges have ratios from .52 to .74.
- Accuracy drops on split items for all 15 judges. The bootstrap CI excludes 0 for 14 of them; the exception is JBB harmbench_cf.
- The loss is mainly in **specificity** (HB median −.41, versus −.10 for sensitivity): judges flag items that one rater called harmful.
- Every ratio CI is below 1, so the pre-registered rule says "below the uniform-noise ceiling".

## Negative control (1,000 stratum-blind simulated judges)
- HB: flag rates are 4–6% for accuracy and 4–9% for sensitivity/specificity, so the test is calibrated.
- JBB: accuracy is 6–8%, but sensitivity/specificity reach 8–28%, so the JBB per-class tests are miscalibrated and not interpretable.

## Power
The minimum detectable recall gap (80% power, baseline .90) is .16 for HB (71 split positives) and .32 for JBB (20).

## Post hoc, added 2026-11-12: direction of the errors (not pre-registered)
`scripts/posthoc_lean.py` → `results/posthoc_lean_stdout.txt`.
- On the 114 HB split items, the HarmBench classifier calls 81% harmful; the three rater columns call 78%, 46% and 39% (mean 54%).
- Its split-item errors are 28 false alarms (harmful v a safe majority) and 7 misses. In 21 of the 28 false alarms the lone "harmful" vote is in rater column 0.
- Attack success rate on all 602 HB items: classifier 51.5%, 3-rater majority 45.3%. 21 of the 37-item gap is on split items.
- Not every judge leans this way (e.g. llama_guard calls 17% of split items harmful). Rater columns may not be the same person across items.

## Caveats
- **The ceiling is model-dependent.** It assumes contested items are no harder for raters than other items, and three raters cannot test that.
  - Post hoc: the drops are fully explained if raters are at most 50–77% accurate on contested HB items (75–87% on JBB).
  - Post hoc: the raters themselves agree with the 2-1 label 67% of the time on split items; the best judges score 69%.
- JBB has only 33 split items.
- HB's paired generations: a cluster bootstrap gives the same CIs.
- The prereg miscounted the judges as 16; there are 15.
- The stratified bootstrap held p fixed. A post hoc unstratified bootstrap gives the same conclusions.

## Summary (MEASURED)
In a pre-registered pilot on 902 public items each labelled by three humans, all 15 released safety judges agreed less often with the majority when raters split 2-1 (e.g. HarmBench classifier 0.96 → 0.69, driven by specificity), staying below a uniform-rater-noise ceiling. With three raters we cannot separate judge failure from genuinely ambiguous items, since raters only ~77% accurate on contested items would explain the whole drop; the proposed denser relabelling would measure exactly this.
