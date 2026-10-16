#!/usr/bin/env python3
"""G5 preregistered eval (draft): term-level paired bootstrap (primary, per G5_PREREG_EVAL.md 2026-10-16) +
exact McNemar (descriptive) + bootstrap macro-F1. Inputs are private prediction
JSONL files keyed by record_id ({"record_id","pred"}) plus a gold JSONL ({"record_id","gold","family"})."""
import argparse, json, random
from math import comb


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def macro_f1(pairs):
    labels = {g for g, _ in pairs} | {p for _, p in pairs}
    f = []
    for l in labels:
        tp = sum(1 for g, p in pairs if g == l and p == l)
        fp = sum(1 for g, p in pairs if g != l and p == l)
        fn = sum(1 for g, p in pairs if g == l and p != l)
        f.append(0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return sum(f) / len(f) if f else 0.0


def holm(pvals):
    """Holm step-down adjusted p-values (dict name -> p)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1]); m = len(items); out = {}; run = 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p)); out[k] = run
    return out


def term_bootstrap(ids, gold, tuned, base, n=10000, seed=7, key="family"):
    """Resample test terms (clusters) with replacement; all rows of a term move together.
    Returns accuracy diff (tuned - base), 95% CI, two-sided bootstrap p, number of clusters."""
    clusters = {}
    for i in ids:
        clusters.setdefault(gold[i].get(key) or i, []).append(i)
    names = sorted(clusters)
    stats = {c: (sum(tuned[i]["pred"] == gold[i]["gold"] for i in clusters[c]),
                 sum(base[i]["pred"] == gold[i]["gold"] for i in clusters[c]), len(clusters[c])) for c in names}
    def diff(sample):
        t = sum(stats[c][0] for c in sample); b = sum(stats[c][1] for c in sample); m = sum(stats[c][2] for c in sample)
        return (t - b) / m if m else 0.0
    obs = diff(names); rng = random.Random(seed)
    boots = sorted(diff([rng.choice(names) for _ in names]) for _ in range(n))
    lo, hi = boots[int(0.025 * n)], boots[int(0.975 * n) - 1]
    p = min(1.0, 2 * min(sum(d <= 0 for d in boots), sum(d >= 0 for d in boots)) / n)
    return {"acc_diff": obs, "ci95": [lo, hi], "p_boot": p, "n_terms": len(names)}


def load(p):
    return {r["record_id"]: r for r in (json.loads(l) for l in open(p) if l.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--tuned", required=True)
    ap.add_argument("--baseline", action="append", default=[], help="name=path")
    ap.add_argument("--final", action="store_true", help="the single preregistered run")
    a = ap.parse_args()
    if not a.final:
        raise SystemExit("refusing to read test gold without --final (preregistered single run)")
    gold = load(a.gold); tuned = load(a.tuned)
    ids = sorted(gold)
    rep = {"n": len(ids), "final": a.final, "tuned_acc": sum(tuned[i]["pred"] == gold[i]["gold"] for i in ids) / len(ids)}
    for spec in a.baseline:
        name, path = spec.split("=", 1); base = load(path)
        b = sum(1 for i in ids if tuned[i]["pred"] == gold[i]["gold"] and base[i]["pred"] != gold[i]["gold"])
        c = sum(1 for i in ids if tuned[i]["pred"] != gold[i]["gold"] and base[i]["pred"] == gold[i]["gold"])
        rep[name] = {"term_bootstrap": term_bootstrap(ids, gold, tuned, base),
                     "mcnemar_descriptive": {"b": b, "c": c, "p_exact": mcnemar_exact(b, c)}}
    adj = holm({k: v["term_bootstrap"]["p_boot"] for k, v in rep.items() if isinstance(v, dict)})
    for k, p in adj.items():
        rep[k]["p_holm"] = p; rep[k]["significant_0.05"] = p < 0.05
    pairs = [(gold[i]["gold"], tuned[i]["pred"]) for i in ids]
    rng = random.Random(7)
    boots = sorted(macro_f1([rng.choice(pairs) for _ in pairs]) for _ in range(10000))
    rep["macro_f1"] = macro_f1(pairs); rep["macro_f1_ci95"] = [boots[249], boots[9749]]
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
