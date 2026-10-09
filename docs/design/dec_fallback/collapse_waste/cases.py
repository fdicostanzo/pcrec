#!/usr/bin/env python3
"""docs/design/dec_fallback/collapse_waste/cases.py -- the compiles whose
attempt COUNT the lane changed, read off attempt_hist.py's two census TSVs
per variant (PARENT_DIR/probe/census_<v>.tsv vs CHILD_DIR's), written as
timing.py's CASES_TSV (variant, json argv) on stdout; the per-variant count
of (parent attempts -> child attempts) on stderr.

usage: cases.py PARENT_DIR CHILD_DIR VARIANT[,VARIANT...]
"""
import ast, collections, json, os, sys


def load(d, v):
    out = {}
    for line in open(os.path.join(d, "probe", f"census_{v}.tsv"), encoding="utf-8", errors="replace"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 4:
            continue
        key = ast.literal_eval(f[1])
        att = sum(1 for p in ast.literal_eval(f[3]) if p.startswith("att="))
        out[key] = (f[0], att)
    return out


def argv_of(key):
    pat, flags, feats, enc, eng = key
    a = []
    if "i" in flags: a.append("-i")
    if "u" in flags: a.append("--ucp")
    if feats: a += ["--features", feats]
    if enc: a += ["-e", enc]
    if eng: a.append("--engine=" + eng)
    return a + ["--pattern-esc", "--pattern", "\"" + pat.replace("\"", "\\\"") + "\""]


for v in sys.argv[3].split(","):
    p, c = load(sys.argv[1], v), load(sys.argv[2], v)
    shift = collections.Counter()
    for k in sorted(p, key=repr):
        if k in c and p[k][1] != c[k][1]:
            shift[(p[k][1], c[k][1], p[k][0], c[k][0])] += 1
            print(f"{v}\t{json.dumps(argv_of(k))}")
    print(v, dict(shift), file=sys.stderr)
