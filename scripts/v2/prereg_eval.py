#!/usr/bin/env python3
"""G5 preregistered eval (draft): term-level paired bootstrap (primary, per G5_PREREG_EVAL.md 2026-10-16) +
exact McNemar (descriptive) + bootstrap macro-F1.
--final verifies the frozen test manifest sha and the locked threshold-config sha, scores only manifest ids,
and takes an exclusive run-once lock so a second --final run refuses. Inputs are private prediction
JSONL files keyed by record_id ({"record_id","pred"} and/or {"record_id","margin"}; margin = logp(SLANG)-logp(OTHER), labelled with the
locked threshold) plus a gold JSONL ({"record_id","gold","family"})."""
import argparse, json, random, hashlib, os

MANIFEST_SHA = "a03c8619ba91a0f3d3edb43a358adbb5a6fcc83fe462442b6cb66e94be8296b6"
THRESHOLD_CFG_SHA = "d0ecacbb0a1dd820f97dc88d9177b4ffde65a8da7b411dffed573eb6a5883e61"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
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
    ap.add_argument("--manifest", help="frozen test_manifest.txt (sha must be MANIFEST_SHA)")
    ap.add_argument("--threshold-config", help="locked decision-threshold config (sha must be THRESHOLD_CFG_SHA)")
    ap.add_argument("--lock", help="run-once lock file; created exclusively, a second --final run refuses")
    a = ap.parse_args()
    if not a.final:
        raise SystemExit("refusing to read test gold without --final (preregistered single run)")
    if not (a.manifest and a.threshold_config and a.lock):
        raise SystemExit("--final requires --manifest, --threshold-config and --lock")
    if sha(a.manifest) != MANIFEST_SHA:
        raise SystemExit("frozen manifest sha mismatch")
    if sha(a.threshold_config) != THRESHOLD_CFG_SHA:
        raise SystemExit("threshold config sha mismatch")
    try:
        fd = os.open(a.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    except FileExistsError:
        raise SystemExit(f"refusing second --final run: lock {a.lock} exists")
    os.write(fd, json.dumps({"tuned": a.tuned, "tuned_sha": sha(a.tuned)}).encode()); os.close(fd)
    manifest = [l.strip() for l in open(a.manifest) if l.strip()]
    gold = {i: r for i, r in load(a.gold).items() if i in set(manifest)}; tuned = load(a.tuned)
    thr = json.load(open(a.threshold_config))["threshold"]
    for r in tuned.values():  # apply the locked threshold when margins are supplied
        if "margin" in r:
            p = "SLANG_SENSE" if r["margin"] > thr else "OTHER_SENSE"
            if "pred" in r and r["pred"] != p:
                raise SystemExit(f"pred disagrees with locked threshold for {r['record_id']}")
            r["pred"] = p
    if len(gold) != len(manifest) or any(i not in tuned for i in manifest):
        raise SystemExit("gold/predictions do not cover the frozen manifest exactly")
    ids = sorted(gold)
    rep = {"n": len(ids), "final": a.final, "manifest_sha": MANIFEST_SHA, "threshold_cfg_sha": THRESHOLD_CFG_SHA, "threshold": thr, "tuned_acc": sum(tuned[i]["pred"] == gold[i]["gold"] for i in ids) / len(ids)}
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
