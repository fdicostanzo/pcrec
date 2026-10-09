#!/usr/bin/env python3
"""walk_survey: the BENCH population -- every pcrec-bench pattern export
(bench/<set>/patterns/*.rx) x every regime the set declares x the subjects
that regime sees (the loader's rule, pcrecbench/subbench.py subjects_for():
`match` = every short-manifest subject, `search_short` = the short subjects
<= [subjects] short_search_max_bytes (default 256), `throughput` = the
throughput manifest, driven find-all). Compiled the way the bench's
pcrec-auto testee does (--features all; -e utf8 on the utf8 set), as
docs/dev/optloop/revend/census.py did.

    pop_bench.py BENCHCOPY > work/pop_bench.tsv

BENCHCOPY is a `git archive` of pcrec-bench (bench/ pcrecbench/) with its
generators run IN THE COPY (pcrec-bench itself is read-only to this study).
Rows: pid set enc icase pattern_hex regime subjects(comma-joined paths).
"""
import glob, os, sys, tomllib

root = os.path.abspath(sys.argv[1])
print("pid\tset\tenc\ticase\tpattern_hex\tregime\tsubjects")
for toml in sorted(glob.glob(os.path.join(root, "bench", "*", "subbench.toml"))):
    d = os.path.dirname(toml); st = os.path.basename(d)
    cfg = tomllib.load(open(toml, "rb"))
    regimes = list(cfg["regimes"])
    sub = cfg.get("subjects", {})
    smax = int(sub.get("short_search_max_bytes", 256))

    def manifest(name, subdir):
        p = os.path.join(d, name)
        if not os.path.exists(p):
            return []
        out = []
        for ln in open(p).read().split("\n")[1:]:
            f = ln.split("\t")
            if len(f) >= 2 and f[0]:
                out.append((f[0], int(f[1]), os.path.join(d, subdir, f[0] + ".bin")))
        return out
    short = manifest(sub.get("manifest", "manifest.tsv"), "subjects")
    thr = manifest("manifest_throughput.tsv", "throughput")
    cells = {"match": short, "search_short": [s for s in short if s[1] <= smax],
             "throughput": thr}
    enc = "utf8" if st == "utf8" else "byte"
    for p in sorted(glob.glob(os.path.join(d, "patterns", "*.rx"))):
        b = open(p, "rb").read().rstrip(b"\n")
        if not b or b"\x00" in b:
            continue
        pid = "%s/%s" % (st, os.path.basename(p)[:-3])
        for r in regimes:
            subs = [s[2] for s in cells[r] if os.path.exists(s[2])]
            if subs:
                print("%s\t%s\t%s\t0\t%s\t%s\t%s" % (pid, st, enc, b.hex(), r, ",".join(subs)))
