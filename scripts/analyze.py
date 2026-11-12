"""Pre-registered pilot (see ../PREREG.md). Usage: python -I analyze.py <pilot_judges_dir>
Reads data/ as data only. Writes results/results.json and prints tables."""
import csv, json, math, sys, hashlib, os
import numpy as np
from scipy.stats import norm

ROOT = sys.argv[1]
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results"); os.makedirs(OUT, exist_ok=True)
SEED = 20261111
B_MAIN = 10_000
N_SIM, B_SIM = 1_000, 1_000

# checksum check
for line in open(os.path.join(DATA, "SHA256SUMS")):
    h, fn = line.split()
    assert hashlib.sha256(open(os.path.join(DATA, fn), "rb").read()).hexdigest() == h, fn


def load_hb():
    d = json.load(open(os.path.join(DATA, "harmbench_text_behaviors_val_set.json")))
    items = [x for v in d.values() for x in v]
    H = np.array([[int(x[f"human_{i}"]) for i in range(3)] for x in items])
    J = {}
    for k in ["cls", "cls_mistral", "llama_guard", "gpt-4-0613", "gpt-4-1106-preview", "mixtral",
              "GPTFuzz", "chatglm", "advbench"]:
        J[k] = np.array([int(x[k]) for x in items])
    J["gpt-3.5-turbo-0613"] = np.array([{"yes": 1, "no": 0}[x["gpt-3.5-turbo-0613"]] for x in items])
    def pair(s):
        k = int(s.split("[[")[1].split("]]")[0]); return int(k == 10)
    J["PAIR_gpt-4-0613"] = np.array([pair(x["PAIR_gpt-4-0613"]) for x in items])
    clusters = np.array([x["behavior_id"] for x in items])
    return H, J, clusters, {}


def load_jbb():
    r = list(csv.DictReader(open(os.path.join(DATA, "jbb_judge_comparison.csv"))))
    H = np.array([[int(x[f"human{i}"]) for i in (1, 2, 3)] for x in r])
    given = np.array([int(x["human_majority"]) for x in r])
    J = {k: np.array([int(x[k]) for x in r]) for k in ["harmbench_cf", "gpt4_cf", "llamaguard2_cf", "llama3_cf"]}
    maj = (H.sum(1) >= 2).astype(int)
    return H, J, None, {"human_majority_mismatches": int((given != maj).sum())}


def wilson(k, n, z=1.959964):
    if n == 0: return (float("nan"),) * 3
    ph = k / n; den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den; h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return ph, c - h, c + h


def p_from_H(H):
    s = H.sum(1); agree = np.where((s == 0) | (s == 3), 1.0, 1 / 3)
    a = agree.mean(); return (1 + math.sqrt(max(2 * a - 1, 0))) / 2, a


def metrics_rows(jud, y, idx):
    """jud,y: arrays; idx: (B, n) indices. returns acc,sens,spec per row."""
    jj, yy = jud[idx], y[idx]; corr = (jj == yy)
    pos = yy.sum(1); neg = yy.shape[1] - pos
    acc = corr.mean(1)
    sens = np.where(pos > 0, (corr & (yy == 1)).sum(1) / np.maximum(pos, 1), np.nan)
    spec = np.where(neg > 0, (corr & (yy == 0)).sum(1) / np.maximum(neg, 1), np.nan)
    return acc, sens, spec


def mde(p1, n1, n2, power=0.8, alpha=0.05):
    za = norm.ppf(1 - alpha / 2)
    def pw(d):
        p2 = p1 - d; se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        return norm.cdf(d / se - za) if se > 0 else 1.0
    if pw(p1) < power: return float("nan")
    lo, hi = 0.0, p1
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if pw(mid) < power else (lo, mid)
    return hi


def analyse(name, H, J, clusters, notes):
    rng = np.random.default_rng(SEED)
    y = (H.sum(1) >= 2).astype(int)
    s = H.sum(1); unan = (s == 0) | (s == 3); split = ~unan
    iu, isp = np.where(unan)[0], np.where(split)[0]
    p, a = p_from_H(H); c = p ** 3 / (p ** 3 + (1 - p) ** 3)
    counts = {"N": int(len(y)), "unan": int(unan.sum()), "split": int(split.sum()),
              "unan_pos": int(y[unan].sum()), "unan_neg": int((1 - y[unan]).sum()),
              "split_pos": int(y[split].sum()), "split_neg": int((1 - y[split]).sum()),
              "pairwise_agreement": a, "p_rater": p, "ceiling_split": p, "ceiling_unan": c}
    # identical-column check
    ks = list(J); ident = [(k1, k2) for i, k1 in enumerate(ks) for k2 in ks[i + 1:] if (J[k1] == J[k2]).all()]
    notes = dict(notes, identical_judge_columns=ident)
    # shared bootstrap indices (stratified)
    bu = iu[rng.integers(0, len(iu), (B_MAIN, len(iu)))]
    bs = isp[rng.integers(0, len(isp), (B_MAIN, len(isp)))]
    # cluster bootstrap (HB only): resample behavior_ids
    if clusters is not None:
        uc = np.unique(clusters); members = [np.where(clusters == k)[0] for k in uc]
        crng = np.random.default_rng(SEED + 1)
        cl_idx = [np.concatenate([members[j] for j in crng.integers(0, len(uc), len(uc))]) for _ in range(2000)]
    res = {}
    for k, jud in J.items():
        corr = jud == y
        r = {}
        for lab, m in [("all", np.ones_like(unan)), ("unan", unan), ("split", split)]:
            r[lab] = {"acc": wilson(int(corr[m].sum()), int(m.sum())),
                      "sens": wilson(int((corr & m & (y == 1)).sum()), int((m & (y == 1)).sum())),
                      "spec": wilson(int((corr & m & (y == 0)).sum()), int((m & (y == 0)).sum()))}
        Au, Su, Pu = metrics_rows(jud, y, bu); As, Ss, Ps = metrics_rows(jud, y, bs)
        diffs = {}
        for met, (u_, s_) in {"acc": (Au, As), "sens": (Su, Ss), "spec": (Pu, Ps)}.items():
            d = s_ - u_; d = d[~np.isnan(d)]
            point = r["split"][met][0] - r["unan"][met][0]
            lo, hi = np.percentile(d, [2.5, 97.5])
            diffs[met] = {"diff": point, "lo": lo, "hi": hi, "flag": bool(lo > 0 or hi < 0)}
        r["diff_split_minus_unan"] = diffs
        # ceiling ratio (stratified bootstrap per prereg; p is constant under stratified resampling)
        ratio = r["split"]["acc"][0] / p
        rr = As / p; lo, hi = np.percentile(rr, [2.5, 97.5])
        r["ceiling_ratio"] = {"ratio": ratio, "lo": lo, "hi": hi, "below_ceiling": bool(hi < 1)}
        # model-based prediction
        u = r["unan"]["acc"][0]; q = (u - (1 - c)) / (2 * c - 1)
        pred = q * p + (1 - q) * (1 - p)
        r["noise_model"] = {"q": q, "pred_split_acc": pred, "obs_minus_pred": r["split"]["acc"][0] - pred,
                            "perfect_judge_expected_drop": c - p}
        # cluster bootstrap of ceiling ratio
        if clusters is not None:
            vals = []
            for idx in cl_idx:
                Hb, yb, jb = H[idx], y[idx], jud[idx]
                sb = Hb.sum(1); spb = (sb == 1) | (sb == 2)
                pb, _ = p_from_H(Hb)
                vals.append((jb[spb] == yb[spb]).mean() / pb)
            lo, hi = np.percentile(vals, [2.5, 97.5])
            r["ceiling_ratio_cluster"] = {"lo": lo, "hi": hi, "below_ceiling": bool(hi < 1)}
        # power
        nu_p, ns_p = counts["unan_pos"], counts["split_pos"]; nu_n, ns_n = counts["unan_neg"], counts["split_neg"]
        r["mde"] = {"sens_at_0.90": mde(0.90, nu_p, ns_p), "sens_at_obs": mde(r["unan"]["sens"][0], nu_p, ns_p),
                    "spec_at_0.90": mde(0.90, nu_n, ns_n), "spec_at_obs": mde(r["unan"]["spec"][0], nu_n, ns_n)}
        # negative control
        acc_all = r["all"]["acc"][0]
        srng = np.random.default_rng(SEED + 7 + list(J).index(k))
        flags = {"acc": 0, "sens": 0, "spec": 0}
        for _ in range(N_SIM):
            sim = np.where(srng.random(len(y)) < acc_all, y, 1 - y)
            su = iu[srng.integers(0, len(iu), (B_SIM, len(iu)))]
            ss = isp[srng.integers(0, len(isp), (B_SIM, len(isp)))]
            a1, s1, p1 = metrics_rows(sim, y, su); a2, s2, p2 = metrics_rows(sim, y, ss)
            for met, d in {"acc": a2 - a1, "sens": s2 - s1, "spec": p2 - p1}.items():
                d = d[~np.isnan(d)]; lo, hi = np.percentile(d, [2.5, 97.5])
                flags[met] += int(lo > 0 or hi < 0)
        r["neg_control_flag_rate"] = {m: v / N_SIM for m, v in flags.items()}
        res[k] = r
        print(name, k, "done", flush=True)
    return {"counts": counts, "notes": notes, "judges": res}


def default(o):
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, np.bool_): return bool(o)
    raise TypeError(type(o))


out = {"HB": analyse("HB", *load_hb()), "JBB": analyse("JBB", *load_jbb())}
json.dump(out, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=default)

for ds, R in out.items():
    print(f"\n== {ds} ==", json.dumps(R["counts"], default=default), R["notes"])
    print(f"{'judge':22s} {'acc_u':>6s} {'acc_s':>6s} {'sens_u':>6s} {'sens_s':>6s} {'spec_u':>6s} {'spec_s':>6s} "
          f"{'dAcc [CI]':>20s} {'dSens [CI]':>20s} {'dSpec [CI]':>20s} {'ratio [CI]':>20s} {'clCI':>12s} {'obs-pred':>8s} {'NC a/se/sp':>14s} {'MDEsens.9':>9s}")
    for k, r in R["judges"].items():
        f = lambda m: f"{r['diff_split_minus_unan'][m]['diff']:+.3f}[{r['diff_split_minus_unan'][m]['lo']:+.2f},{r['diff_split_minus_unan'][m]['hi']:+.2f}]"
        cr = r["ceiling_ratio"]; cl = r.get("ceiling_ratio_cluster")
        nc = r["neg_control_flag_rate"]
        print(f"{k:22s} {r['unan']['acc'][0]:6.3f} {r['split']['acc'][0]:6.3f} {r['unan']['sens'][0]:6.3f} {r['split']['sens'][0]:6.3f} "
              f"{r['unan']['spec'][0]:6.3f} {r['split']['spec'][0]:6.3f} {f('acc'):>20s} {f('sens'):>20s} {f('spec'):>20s} "
              f"{cr['ratio']:.3f}[{cr['lo']:.2f},{cr['hi']:.2f}] "
              f"{(f'[{cl[chr(108)+chr(111)]:.2f},{cl[chr(104)+chr(105)]:.2f}]' if cl else '-'):>12s} "
              f"{r['noise_model']['obs_minus_pred']:+.3f} {nc['acc']:.3f}/{nc['sens']:.3f}/{nc['spec']:.3f} {r['mde']['sens_at_0.90']:.3f}")
