#!/usr/bin/env python3
"""G5 preregistered eval (draft): exact McNemar + bootstrap macro-F1. Inputs are private prediction
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


def load(p):
    return {r["record_id"]: r for r in (json.loads(l) for l in open(p) if l.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--tuned", required=True)
    ap.add_argument("--baseline", action="append", default=[], help="name=path")
    ap.add_argument("--final", action="store_true", help="the single preregistered run")
    a = ap.parse_args()
    gold = load(a.gold); tuned = load(a.tuned)
    ids = sorted(gold)
    rep = {"n": len(ids), "final": a.final, "tuned_acc": sum(tuned[i]["pred"] == gold[i]["gold"] for i in ids) / len(ids)}
    for spec in a.baseline:
        name, path = spec.split("=", 1); base = load(path)
        b = sum(1 for i in ids if tuned[i]["pred"] == gold[i]["gold"] and base[i]["pred"] != gold[i]["gold"])
        c = sum(1 for i in ids if tuned[i]["pred"] != gold[i]["gold"] and base[i]["pred"] == gold[i]["gold"])
        rep[name] = {"b": b, "c": c, "p_exact": mcnemar_exact(b, c)}
    pairs = [(gold[i]["gold"], tuned[i]["pred"]) for i in ids]
    rng = random.Random(7)
    boots = sorted(macro_f1([rng.choice(pairs) for _ in pairs]) for _ in range(10000))
    rep["macro_f1"] = macro_f1(pairs); rep["macro_f1_ci95"] = [boots[249], boots[9749]]
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
