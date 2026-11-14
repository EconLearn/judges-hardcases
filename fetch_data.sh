#!/bin/sh
# Downloads the two public datasets (MIT) into data/ and checks them against data/SHA256SUMS.
set -e
cd "$(dirname "$0")/data"
curl -sL -o harmbench_text_behaviors_val_set.json https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/classifier_val_sets/text_behaviors_val_set.json
curl -sL -o jbb_judge_comparison.csv https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/resolve/main/data/judge-comparison.csv
curl -sL -o harmbench_behaviors_text_all.csv https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/behavior_datasets/harmbench_behaviors_text_all.csv
shasum -a 256 -c SHA256SUMS
