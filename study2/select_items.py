"""Study 2 item selection (fixed BEFORE any new rating is collected). Usage: python -I study2/select_items.py <repo_dir>
Writes study2/items.csv: one row per item to be re-rated, identified by HarmBench behavior key + generation index.
No model output text is written (the data contains harmful text; raters see it only inside the rating task)."""
import sys, os, json, random, csv
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
d = json.load(open(os.path.join(ROOT, "data", "harmbench_text_behaviors_val_set.json")))
H = ("human_0", "human_1", "human_2")
# Amendment 1 (before any data): leave out HarmBench's chemical_biological behaviors entirely (category from
# data/harmbench_behaviors_text_all.csv, sha256 in data/SHA256SUMS).
cat = {r["BehaviorID"]: r["SemanticCategory"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "harmbench_behaviors_text_all.csv")))}
# Three validation-set IDs were renamed in the later category file; their categories, checked by hand against it:
cat.update({"chop_shops_los_angeles_locating": "illegal",           # = los_angeles_chop_shops_list
            "ddos_code_obfuscation": "cybercrime_intrusion",        # = ddos_code_obfuscation_tools_1/2
            "password_pin_coercion_dialogue": "not_in_file"})       # no match; a coercion dialogue, not chem/bio
assert all(k in cat for k in d), "behavior missing from the HarmBench category file"
EXCLUDE = {"chemical_biological"}
n_all = sum(len(v) for v in d.values())
items = [(k, i, r) for k, v in sorted(d.items()) if cat[k] not in EXCLUDE for i, r in enumerate(v)]
votes = lambda r: sum(int(r[c]) for c in H)
maj = lambda r: int(votes(r) >= 2)
rng = random.Random(20261114)
split = [x for x in items if 0 < votes(x[2]) < 3]
fa = [x for x in split if int(x[2]["cls"]) == 1 and maj(x[2]) == 0]     # classifier harmful, 2-1 majority safe
mi = [x for x in split if int(x[2]["cls"]) == 0 and maj(x[2]) == 1]     # classifier safe, 2-1 majority harmful
agree = [x for x in split if int(x[2]["cls"]) == maj(x[2])]
agree_h = [x for x in agree if maj(x[2]) == 1]; agree_s = [x for x in agree if maj(x[2]) == 0]
nb = 15; nbh = round(nb * len(agree_h) / len(agree))                    # mirror the harmful/safe mix of agree items
setB = rng.sample(agree_h, nbh) + rng.sample(agree_s, nb - nbh)
unan_h = [x for x in items if votes(x[2]) == 3]; unan_s = [x for x in items if votes(x[2]) == 0]
ctrl = rng.sample(unan_h, 5) + rng.sample(unan_s, 5)
rows = ([("A_false_alarm", x) for x in fa] + [("A_miss", x) for x in mi] + [("B_split_agree", x) for x in setB]
        + [("C_control_unanimous", x) for x in ctrl])
with open(os.path.join(ROOT, "study2", "items.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["set", "behavior_key", "generation_index", "old_votes_harmful_of_3", "classifier_cls"])
    for s, (k, i, r) in rows: w.writerow([s, k, i, votes(r), r["cls"]])
print(f"generations {n_all}, after excluding {sorted(EXCLUDE)}: {len(items)}")
print(f"split {len(split)}: false alarms {len(fa)}, misses {len(mi)}, agree {len(agree)} ({len(agree_h)} harmful)")
print(f"selected: A {len(fa)+len(mi)}, B {len(setB)} ({nbh} harmful), C {len(ctrl)}; total {len(rows)}")
