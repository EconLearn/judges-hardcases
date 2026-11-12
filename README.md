# Do jailbreak judges agree with humans on the hard cases?

HarmBench and JailbreakBench each released a validation set in which every item has three human labels and the verdicts of
several automated judges (11 and 4 judges; 902 items in all). This repo splits those items by whether the three humans
agreed and measures each judge on both groups.

Main result (HarmBench classifier): 96% agreement with the human majority where the raters were unanimous, 69% where they
split 2-1. If raters made independent random mistakes at the rate their overall agreement implies, a perfect judge would
still match the majority about 93% of the time on the split items. All 15 judges fall below that line, mostly by calling
outputs harmful that the majority judged safe. Three labels per item cannot tell judge error from genuinely ambiguous
items; that needs more labels.

- `PREREG.md`: the analysis plan, written before any results (sha256 in `PREREG.sha256`).
- `PILOT_REPORT.md`: all results, the negative control, power, and caveats.
- `scripts/analyze.py`, `scripts/posthoc.py`: the analysis. `results/`: their outputs.

Reproduce (Python 3 with numpy and scipy):

    ./fetch_data.sh                      # downloads both public datasets (MIT) and checks their sha256
    python scripts/analyze.py "$PWD"
    python scripts/posthoc.py "$PWD"

Data: HarmBench classifier validation set (github.com/centerforaisafety/HarmBench, data/classifier_val_sets) and the
JailbreakBench judge comparison (huggingface.co/datasets/JailbreakBench/JBB-Behaviors, data/judge-comparison.csv).
The raw data is not redistributed here because it contains harmful model outputs.

Licence: MIT.
