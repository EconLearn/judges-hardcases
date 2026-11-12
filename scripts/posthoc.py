"""POST HOC (not pre-registered). Usage: python -I posthoc.py <pilot_judges_dir>
(1) Unstratified item bootstrap of split-accuracy / p, p re-estimated per resample
    (the prereg's stratified bootstrap holds p fixed, so its 're-estimate p' step was a no-op).
(2) Break-even rater accuracy on split items = upper 95% bound of the judge's split accuracy:
    if raters are no more accurate than this on contested items (heterogeneous difficulty), a perfect
    judge would score no higher, so the drop would be within label noise.
(3) Share of judge errors on split items: by construction every split-item error agrees with the 1 minority rater."""
import sys, os, json, csv, math
import numpy as np
ROOT = sys.argv[1]; DATA = os.path.join(ROOT, "data")
R = json.load(open(os.path.join(ROOT, "results", "results.json")))
def hb():
    d = json.load(open(os.path.join(DATA, "harmbench_text_behaviors_val_set.json"))); it = [x for v in d.values() for x in v]
    H = np.array([[int(x[f"human_{i}"]) for i in range(3)] for x in it])
    J = {k: np.array([int(x[k]) for x in it]) for k in ["cls","cls_mistral","llama_guard","gpt-4-0613","gpt-4-1106-preview","mixtral","GPTFuzz","chatglm","advbench"]}
    J["gpt-3.5-turbo-0613"] = np.array([{"yes":1,"no":0}[x["gpt-3.5-turbo-0613"]] for x in it])
    J["PAIR_gpt-4-0613"] = np.array([int(int(x["PAIR_gpt-4-0613"].split("[[")[1].split("]]")[0]) == 10) for x in it])
    return H, J
def jbb():
    r = list(csv.DictReader(open(os.path.join(DATA, "jbb_judge_comparison.csv"))))
    H = np.array([[int(x[f"human{i}"]) for i in (1,2,3)] for x in r])
    return H, {k: np.array([int(x[k]) for x in r]) for k in ["harmbench_cf","gpt4_cf","llamaguard2_cf","llama3_cf"]}
out = {}
for name, (H, J) in {"HB": hb(), "JBB": jbb()}.items():
    rng = np.random.default_rng(20261112); N = len(H)
    idx = rng.integers(0, N, (10000, N)); Hb = H[idx]; s = Hb.sum(2); y = (s >= 2)
    sp = (s == 1) | (s == 2); agree = np.where(sp, 1/3, 1.0).mean(1); p = (1 + np.sqrt(np.clip(2*agree-1, 0, None)))/2
    print(f"\n{name}: p bootstrap 95% CI [{np.percentile(p,2.5):.3f},{np.percentile(p,97.5):.3f}]")
    out[name] = {}
    for k, j in J.items():
        jb = j[idx]; acc_s = ((jb == y) & sp).sum(1) / sp.sum(1); rr = acc_s / p
        lo, hi = np.percentile(rr, [2.5, 97.5]); be = R[name]["judges"][k]["split"]["acc"][2]
        out[name][k] = {"ratio_unstrat_lo": lo, "ratio_unstrat_hi": hi, "break_even_split_rater_acc": be}
        print(f"  {k:20s} ratio CI(unstrat) [{lo:.2f},{hi:.2f}]  break-even split rater acc {be:.3f}")
json.dump(out, open(os.path.join(ROOT, "results", "posthoc.json"), "w"), indent=1, default=float)
