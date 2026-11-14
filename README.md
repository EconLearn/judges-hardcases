# Do jailbreak judges agree with humans on the hard cases?

HarmBench and JailbreakBench each released a validation set in which every item has three human labels and the verdicts of
several automated judges (11 and 4 judges; 902 items in all). This repo splits those items by whether the three humans
agreed and measures each judge on both groups.

Main result (HarmBench classifier): 96% agreement with the human majority where the raters were unanimous, 69% where they
split 2-1. All 15 judges drop on the split items. **The main limitation comes first:** the split items are probably
harder for the human raters too, and three labels cannot measure that. If raters are only 50-77% accurate on contested
items, the drop is explained by label noise alone. The pilot compared judges with a ceiling that assumes every item is
equally hard to grade; all 15 fall below it, but that ceiling is too high for contested items, so this comparison does
not show judge failure. Separating judge error from ambiguous items needs more labels: that is Study 2
(`STUDY2_PLAN.md`).

- `PREREG.md`: the pilot's analysis plan, written before the analysis was run. It was committed together with the results
  (commit `ceac9fa`), so its timing cannot be checked from this repository. Study 2's plan was committed on its own first.
- `STUDY2_PLAN.md`: the plan for fresh, blind ratings of the contested items (sha256 in `STUDY2_PLAN.sha256`).
- `PILOT_REPORT.md`: all results, the negative control, power, and caveats.
- `scripts/analyze.py`, `scripts/posthoc.py`: the analysis. `results/`: their outputs.

Reproduce (Python 3 with numpy and scipy):

    ./fetch_data.sh                      # downloads both public datasets (MIT) and checks their sha256
    python scripts/analyze.py "$PWD"
    python scripts/posthoc.py "$PWD"

Data: HarmBench classifier validation set (github.com/centerforaisafety/HarmBench, data/classifier_val_sets) and the
JailbreakBench judge comparison (huggingface.co/datasets/JailbreakBench/JBB-Behaviors, data/judge-comparison.csv).
The raw data is not redistributed here because it contains harmful model outputs.

Methods feedback on the pilot from Yang Gao (13 Nov 2026) led to the changes listed in `PILOT_REPORT.md` and to the
Study 2 plan.

Licence: MIT.
