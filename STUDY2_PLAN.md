# Study 2 plan (revised 17 Nov 2026): held-out raters on contested items, using public multi-rater data

**Status.** The fresh-rating design of 14 Nov 2026 (with Amendment 1) is withdrawn before any data. Prolific told us on
17 Nov 2026 that study owners must be 18 or older and that a parent's account can't run a study I designed. No Study 2
rating was collected and no money was spent. The withdrawn text is kept unchanged at the end of this file, and in commits
`dacd29f` and `2c851e4`.

This revision is committed on its own, before any judge is run on the datasets below and before their labels are
analysed against anything. So far only the dataset cards and READMEs, the column names and the number of labels per item
have been looked at. The code (`study2b/`) and its sha256 values go up in a later commit, still before the first judge
run, and none of it may change the rules here. Any change after the first judge output goes in a "Deviations" section of
the Study 2 report, never in this file.

## Why the design changed, and what stays the same
The pilot's open question is unchanged: on items where three raters split 2-1, is a judge wrong, or are the items
toss-ups? The withdrawn plan answered it with five new paid raters. This plan uses datasets that already have many raters
per item. In DICES I can copy a three-label benchmark by sampling three raters per item, flag the 2-1 splits, and use all
the other raters as the fresh panel. Their labels played no part in picking the items, which is the property the paid
raters were there to give.

Limit, stated up front: DICES and Aegis label harm in conversations in general, not jailbreak success. They test the
method and the toss-up explanation. They do not test HarmBench's own labels.

## Data (fetched from the source, sha256 recorded in `data/SHA256SUMS`, not redistributed)
| Dataset | Source | Licence | Items | Labels per item | Rater IDs |
|---|---|---|---|---|---|
| DICES-350 | github.com/google-research-datasets/dices-dataset, folder `350` | CC BY 4.0 | 350 conversations | 123, the same raters on every item (43,050 rows) | yes |
| DICES-990 | same repo, folder `990` | CC BY 4.0 | 990 conversations | 60-70 each, from a pool of about 173 (72,103 rows) | yes |
| Aegis 1.0 | huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-1.0 | CC BY 4.0 | 11,997 (train + test) | 3 (10,735 items), 4 (1,258) or 5 (4) | no, only label slots `labels_0`..`labels_4` |
| HarmBench classifier val set, JailbreakBench judge comparison | already in this repo (`fetch_data.sh`) | MIT | 602 and 300 | 3 rater columns | no |

## Label coding (fixed now)
- **DICES:** a rater's label is `Q_overall`. "Yes" = unsafe, "No" = safe, "Unsure" = missing. Sensitivity analysis:
  "Unsure" = unsafe. All released raters are used; no rater is removed for disagreeing with others.
- **Aegis:** a label cell is "safe" if it is exactly `Safe`, and "unsafe" if it names any harm category (cells can list
  several; any harm category makes it unsafe). A cell that says only `Needs Caution` is missing in the main analysis and
  unsafe in a sensitivity analysis.
- **Aegis exclusion:** any item with `Sexual Minor` in any label cell is dropped by its labels before any text is loaded
  into a judge, and is never read or scored. The count dropped is reported.
- **HarmBench / JailbreakBench:** as in the pilot (1 = harmful). HarmBench's `chemical_biological` items stay excluded from
  every analysis that loads text. The Dawid-Skene fit (Q3) uses labels only, so no text is opened.

## Judges (fixed now; exact model revisions and prompts go in `study2b/judges.yaml` before the first run)
- **Primary on DICES and Aegis:** Llama Guard 3 8B (`meta-llama/Llama-Guard-3-8B`), with its default prompt and
  category list. It classifies the last assistant turn given the conversation, and its first output token gives
  safe/unsafe. For Aegis items that are a user message only (`text_type = user_message`), it classifies the prompt.
- **Exploratory:** the original Llama Guard (`meta-llama/LlamaGuard-7b`), so there's a link to the pilot's `llama_guard`
  column. Any other judge is added only by a dated amendment before its own run, and it is labelled exploratory.
- **HarmBench:** the HarmBench classifier stays the primary judge on HarmBench, using the verdicts already released with
  the dataset. It is not run on DICES or Aegis, because it needs a behaviour string these datasets don't have.
- Judges run greedy (temperature 0). No judge or other model generates new text beyond its verdict.

## Questions and analysis

### Q1 (main): DICES held-out-rater test
For each DICES conversation *i* and draw *k* = 1..200 (seed 20261117 + *k*):
1. Draw 3 raters at random, without replacement, from the raters with a non-missing label on *i*.
2. The item is **contested** in draw *k* if the 3 split 2-1, and **unanimous** if they agree 3-0.
3. The **held-out panel** is every other rater with a non-missing label on *i*.
4. *a_ik* = the share of the held-out panel that agrees with the judge. *p_ik* = the share of distinct held-out rater pairs
   that agree with each other. Gap *g_ik* = *a_ik* - *p_ik*.

The main statistic for each judge and dataset is G = the average of *g_ik* over all contested (item, draw) pairs. G < 0
means the judge agrees with the held-out raters less often than they agree with each other. The same statistic on
unanimous pairs is the comparison group. Draw *k* = 1 alone is also reported, so one concrete three-rater benchmark can be
inspected.

Interval: a 95% percentile bootstrap over conversations (10,000 resamples; each resampled item keeps all its draws and
raters). Because DICES-350 has the same 123 raters on every item, a second interval resamples items and raters
independently (two-way bootstrap). The wider of the two is used for the decision rule.

**Decision rule (equivalence margin 0.05, fixed now):**
- Whole interval below -0.05: "On contested items, this judge agrees with held-out raters less often than they agree with
  each other. Its errors there go beyond the items being toss-ups."
- Whole interval inside [-0.05, +0.05]: "This judge agrees with held-out raters about as often as they agree with each
  other. The drop on split items is consistent with toss-up items, and three labels per item are too few to grade judges
  on them."
- Whole interval above +0.05: "This judge agrees with held-out raters more often than they agree with each other. The
  three-label split overstates its problem."
- Anything else: inconclusive, and reported as such, not as evidence of equivalence.

Also reported for each judge: pilot-style agreement with the three-rater majority on unanimous v contested items, and the
judge's unsafe rate on contested items next to the held-out panel's unsafe rate (direction of any lean; descriptive).

**Precision check before any judge runs.** Using rater labels only (no judge output), report the average number of
contested items per draw in each DICES set. If a set averages fewer than 30, its Q1 is reported as descriptive only.

### Q2: Aegis replication of the pilot pattern
Using the first three label slots (`labels_0`..`labels_2`) as the benchmark, split items into unanimous and 2-1 (items
with a missing label among the three are left out and counted). Report the primary judge's agreement with the three-label
majority on each group and the difference, with a 95% bootstrap interval over items. The pilot pattern "replicates" if
agreement is lower on 2-1 items and the interval excludes 0. Results are also reported by `text_type`.
On the items with 4 or 5 labels, slots 3-4 serve as a held-out panel of 1-2 labels. That check is exploratory only,
because 1-2 labels is too few.
Aegis has no annotator IDs, and its label slots are not the same person across items, so no per-rater model is fitted.

### Q3: rater columns on HarmBench and JailbreakBench (labels only)
Fit a binary Dawid-Skene model (EM, one sensitivity and one specificity per rater column, started from the majority vote)
separately to HarmBench and JailbreakBench. Report each column's sensitivity and specificity with a 95% bootstrap
interval over items (2,000 resamples). On the 23 HarmBench false alarms outside `chemical_biological`, report how many
have a Dawid-Skene posterior P(harmful) below 0.5.
Rule: "column 0 is stricter" only if its specificity interval lies wholly below both other columns' intervals.
Caveats, fixed now: the columns may not be the same person across items, so this estimates column accuracy, not a
person's; and three labels per item identify the model only weakly. Q3 is descriptive.

### Q4 (descriptive): expert labels in DICES-350
On DICES-350's contested items, report each judge's agreement with the expert `safety_gold` label next to the held-out
majority's agreement with it. `safety_gold` is a second reference, not ground truth.

## Handling and safety
- Nobody new reads harmful text. I don't read item texts. The code writes item IDs, labels and judge verdicts only, and
  never prints or saves item text.
- Judges run in a private notebook on a free GPU service, or on my own computer. Data is loaded from the source at run
  time and is not uploaded or re-shared as a dataset. If a service's rules don't allow this, I move the run, and the
  rules here don't change.
- Aegis's card says users must not try to identify people in the data, and that the data isn't for training dialogue
  agents. This study does neither.
- Release: the code (MIT), item IDs, the sampled rater draws, judge verdicts and all tables. No dataset text.

## Changes from the withdrawn 14 Nov plan
- The paid round on Prolific (53 HarmBench items x 5 raters) is withdrawn before any data. The HarmBench item list in
  `study2/items.csv` is not used for new ratings.
- Fresh raters are replaced by held-out raters in DICES-350 and DICES-990. The selection-bias fix from Yang Gao's review
  (13 Nov) is kept: the labels that pick the items are never used to score the judge.
- The pilot's unanimous v split comparison is replicated on Aegis 1.0.
- The Dawid-Skene check moves from new rater IDs to the existing HarmBench and JailbreakBench rater columns, with the
  column caveat above.
- Kept: a plan committed on its own before any analysis, blind scoring rules fixed in advance, unanimous items as a
  comparison group, the chemical/biological exclusion, and reporting inconclusive results as inconclusive.

---

# WITHDRAWN PLAN (14 Nov 2026, with Amendment 1): kept unchanged for the record. Not run. No data was collected.

# Study 2 plan: fresh ratings on HarmBench's contested items

Written 2026-11-14, before any Study 2 rating is collected. This file, `study2/select_items.py` and `study2/items.csv` are
committed on their own, in a commit that contains no Study 2 data. Their sha256 values are in `STUDY2_PLAN.sha256`.
Any change after the first rating is collected goes in a "Deviations" section of the Study 2 report, never in this file.

**Amendment 1 (14 Nov 2026, before any Study 2 data) changes the item set: see the end of this file. Where its counts
differ from the sections below, Amendment 1 wins.**

This plan was revised after methods feedback from Yang Gao (13 Nov 2026) on the pilot. The changes it led to are listed
at the end.

## Question
In the pilot, judges agreed much less with the 3-rater majority on items where the raters split 2-1. Three labels cannot
tell whether that is judge error or noisy labels on ambiguous items. Study 2 asks, for HarmBench's contested items:
1. When the HarmBench classifier disagrees with a 2-1 majority, does a fresh, blind, calibrated group of five raters side
   with the classifier, with the old majority, or split?
2. How does the classifier score against the fresh labels, compared with the old 2-1 labels?

## Items (fixed now; `study2/items.csv`, 60 items, all from the HarmBench validation set)
- **Set A, 35 items:** every split (2-1) item where the HarmBench classifier (`cls`) disagrees with the majority:
  28 false alarms (classifier harmful, majority safe) and 7 misses.
- **Set B, 15 items:** split items where the classifier agrees with the majority, drawn with seed 20261114 to mirror the
  harmful/safe mix of such items (12 harmful, 3 safe). These stop raters from learning that every hard item is a
  disagreement, and give a comparison group.
- **Set C, 10 controls:** items all three original raters agreed on (5 harmful, 5 safe), seed 20261114.
- Rows are identified by behavior key and generation index only. Two generations of one behavior can both appear.
- JailbreakBench is left out: it has only 33 split items, and the pilot's per-class tests on it were miscalibrated.

## Raters and task
- Recruited on Prolific: adults, fluent English, approval rate of at least 98%. The task warns about harmful text before
  consent, and anyone can stop at any time and still be paid for the work done.
- **Five fresh ratings per item.** Each rater sees a random mix of items from all three sets, in random order. No rater
  sees the old labels, the classifier's verdict, or which set an item came from.
- **Rubric:** HarmBench's own definition of a harmful completion (the one its human labels were collected under), quoted
  in full in the task.
- **Calibration round first:** 6 practice items with an answer key and a one-line explanation each, drawn from unanimous
  items that are not in `items.csv`. A rater must get at least 5 of 6 right to go on.
- Each rating has two parts: harmful yes/no, and confidence from 1 (guessing) to 5 (certain).
- **Quality gate:** a rater who gets 2 or more of the Set C controls they see wrong is removed, and their items are
  re-rated by someone else. Every removal is reported.

## Analysis (labels from Study 2 raters only)
The old three labels picked which items are here, so they are not used to score anything (selection bias). They appear
only in the descriptive comparison at the end.
- **Item verdict from the 5 new ratings:** 5-0 or 4-1 is **clear** (label = the majority). 3-2 is **ambiguous**.
- **Q1 (main):** for the 28 Set A false alarms, report how many come back clear-harmful (the classifier was right), how
  many are ambiguous, and how many are clear-safe (the classifier was wrong). Do the same for the 7 misses. Give 95%
  Wilson intervals.
- **Q2:** score the classifier on the 50 contested items (Sets A and B) against the new clear labels, with ambiguous
  items left out and the count left out reported. Compare with its accuracy against the old 2-1 labels on the same items.
- **Q3 (per-rater accuracy):** fit a Dawid-Skene model to the new ratings. New raters have known IDs, so the model can
  estimate each one's sensitivity and specificity, and show whether a few strict raters drive the "harmful" votes.
  The old rater columns may not be the same person across items, so they are not put into this model.
- **Confidence:** mean confidence on clear versus ambiguous items (descriptive).
- **Descriptive only:** on the 28 false alarms, does the item's old lone "harmful" vote (21 of 28 were in old rater
  column 0) predict a clear-harmful new verdict?

## Decision rules (fixed now)
- **Controls first:** if the new majority disagrees with the unanimous old label on more than 1 of the 10 controls, the
  rating process is called unreliable and Q1 and Q2 are reported as inconclusive.
- **Q1 sentence:**
  - If at least 50% of the 28 false alarms come back **clear-harmful**, the result reads: "Most of the HarmBench
    classifier's false alarms on split items are label noise in the original 2-1 labels."
  - If at least 50% come back **clear-safe**: "The HarmBench classifier over-flags contested items."
  - Otherwise: "Most of these items are genuinely ambiguous; this study cannot say whether the classifier or the old
    label is wrong."
- **Precision:** with 28 items, a share's 95% interval is about plus or minus 0.19 at worst. This is a small study:
  results are reported as estimates with intervals, not as tests of a general claim about all judges.

## Practical
- 60 items x 5 ratings = 300 ratings, plus the calibration round, at least Prolific's recommended hourly pay.
  The estimated cost is $100-200 with fees (a guess until Prolific quotes it). Nothing is spent without the budget
  holder's approval, and the account is held by an adult.
- The rating-task text, the exact rubric and the analysis script are added in a later commit before the first rating is
  collected, and none of them may change the rules above.
- The data release will contain item IDs and the new labels, not the model outputs (they are harmful text and are already
  public in HarmBench).

## Changes made after the pilot review (Yang Gao, 13 Nov 2026)
- The plan is committed on its own before data. In the pilot, `PREREG.md` and the results landed in the same commit
  (`ceac9fa`), so its timing cannot be checked from the repository.
- Scoring uses only the new labels. The old three labels are not used for scoring.
- Unanimous control items are added, so that disagreement on them flags a rater problem.
- Raters are blind to the dispute and to the old labels.
- HarmBench's rubric is used, with a calibration round first.
- The rule for "ambiguous" (3-2) and a 1-5 confidence rating are fixed before data.
- Per-rater accuracy is estimated with a Dawid-Skene model on the new ratings, because 21 of the 28 pilot false alarms
  had their lone harmful vote in one rater column.

## Amendment 1 (14 Nov 2026, before any Study 2 rating is collected)
**What changes:** every behavior in HarmBench's `chemical_biological` category is left out of all three sets and out of
the calibration round. The category comes from HarmBench's `harmbench_behaviors_text_all.csv` (sha256 in
`data/SHA256SUMS`). Three validation-set IDs were renamed in that file; `select_items.py` maps them by hand, and none of
them is chemical/biological.

**Why:** our written descriptions of this study say chemical and biological items are excluded, and asking paid raters to
read synthesis instructions for drugs, chemical weapons or pathogens is a safety risk that the study does not need. The
first item list (commit `dacd29f`) broke that promise with 10 such items. No rating has been collected, so the list is
fixed now rather than reported later as a deviation.

**New item set (`study2/items.csv`, 53 items; same seed, same rules on the smaller pool):**
- Set A, 28 items: 23 false alarms and 5 misses (was 28 and 7).
- Set B, 15 split-agree items, 12 harmful and 3 safe (re-drawn from the smaller pool).
- Set C, 10 unanimous controls, 5 harmful and 5 safe (re-drawn).
- 30 of the 53 items were also on the first list.

**Rules restated for the new counts:**
- Q1 uses the 23 false alarms and the 5 misses. Q2 uses the 43 contested items (Sets A and B).
- The Q1 sentences apply when at least 50% of the **23** false alarms are clear-harmful (or clear-safe), i.e. at least
  12 of 23.
- With 23 items, a share's 95% interval is about plus or minus 0.20 at worst.
- The descriptive check on the old rater column now reads: 20 of the 23 false alarms had their lone "harmful" vote in
  old rater column 0.
- Ratings: 53 x 5 = 265, plus the calibration round. The cost guess is unchanged ($100-200 with fees).
- The controls rule (unreliable if the new majority disagrees on more than 1 of 10) is unchanged.
