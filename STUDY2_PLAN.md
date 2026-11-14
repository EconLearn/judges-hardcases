# Study 2 plan: fresh ratings on HarmBench's contested items

Written 2026-11-14, before any Study 2 rating is collected. This file, `study2/select_items.py` and `study2/items.csv` are
committed on their own, in a commit that contains no Study 2 data. Their sha256 values are in `STUDY2_PLAN.sha256`.
Any change after the first rating is collected goes in a "Deviations" section of the Study 2 report, never in this file.

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
