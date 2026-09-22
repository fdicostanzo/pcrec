#!/usr/bin/env python3
"""[ONE-PASS REACH CENSUS] M-A's driver: three populations in, reach out.

Populations are exactly `captures_via_dfa_survey.md` §3.6's table:
  hybrid17     the 17 capture-forced `hybrid` capability rows (§1.5), read
               from `../capsurvey_census.tsv` rather than re-derived.
  corpus       every `pattern`/`pattern-esc` line of every shipped `.rxt`.
  corpus_utf8  the same under `-e utf8`.

The survey asks for the reach AMONG CAPTURE-BEARING PATTERNS, so every
figure is reported twice: over the whole population and over the rows with
`ncap >= 1`, which is the one the decision rule is stated against.

Environment: PCREC PROBE BENCH CORPUS OUT
"""
import os, sys, subprocess, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reqpos_census import dec_field, corpus_pop        # one decoder, one home

E = os.environ

def bench_capability():
    import glob
    out = {}
    for p in sorted(glob.glob(os.path.join(E["BENCH"], "bench", "capability",
                                           "patterns", "*.rx"))):
        b = open(p, "rb").read()
        while b.endswith(b"\n"): b = b[:-1]
        out[os.path.basename(p)[:-3]] = b
    return out

def hybrid17():
    rows, caps = [], bench_capability()
    tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "capsurvey_census.tsv")
    for ln in open(tsv):
        f = ln.rstrip("\n").split("\t")
        if len(f) < 4 or f[0] == "name": continue
        if f[3] == '"hybrid"' and "capture group" in f[2]:
            if f[0] in caps: rows.append((f[0], caps[f[0]]))
    return rows

def run(rows, args):
    inp = "".join("%s\t%s\n" % (i, p.hex()) for i, p in rows)
    r = subprocess.run([E["PROBE"]] + args, input=inp.encode(),
                       capture_output=True, timeout=1800)
    if r.returncode != 0: sys.exit("probe failed: " + r.stderr.decode()[:400])
    out, hdr = [], None
    for ln in r.stdout.decode().rstrip("\n").split("\n"):
        f = ln.split("\t")
        if hdr is None: hdr = f; continue
        out.append(dict(zip(hdr, f)))
    return out

def summarise(name, recs):
    ok = [r for r in recs if r["status"] == "ok"]
    capb = [r for r in ok if int(r["ncap"]) >= 1]
    def frac(rows, key="onepass"):
        n = len(rows)
        k = sum(1 for r in rows if r[key] == "1")
        return k, n, (100.0 * k / n if n else 0.0)
    why = collections.Counter(r["why"] for r in ok if r["onepass"] == "0")
    a, b, c = frac(ok); d, e, f = frac(capb)
    g, h, i = frac(capb, "capped")
    anch = sum(1 for r in capb if r["anchored"] == "1" and r["onepass"] == "1")
    return dict(population=name, probed=len(recs), refused=len(recs) - len(ok),
                ok=b, onepass=a, reach_pct=round(c, 2),
                capture_bearing=e, capture_onepass=d, capture_reach_pct=round(f, 2),
                capped_onepass=g, capped_reach_pct=round(i, 2),
                capture_onepass_and_leading_anchor=anch,
                not_onepass_why=dict(why))

def main():
    out = {}
    h, cp = hybrid17(), corpus_pop()
    runs = {"hybrid17": run(h, []), "corpus": run(cp, []),
            "corpus_utf8": run(cp, ["-e", "utf8"]),
            "corpus_nofactor": run(cp, ["-no-factor"])}
    names = {"hybrid17": "hybrid17 (capture-forced hybrid capability rows)",
             "corpus": "corpus, --features all, byte",
             "corpus_utf8": "corpus, --features all, -e utf8",
             "corpus_nofactor": "corpus, byte, altcls merge+factor DENIED"
                                " (the precedents' criterion)"}
    for k in runs: out[k] = summarise(names[k], runs[k])
    json.dump(out, open(os.path.join(E["OUT"], "onepass_summary.json"), "w"), indent=1)
    # the committed per-row table, for the corpus arms
    with open(os.path.join(E["OUT"], "onepass_census.tsv"), "w") as o:
        o.write("# [ONE-PASS REACH CENSUS] captures_via_dfa_survey.md §3.6 M-A\n"
                "# (lane c2prep, 2026-09-22).  Produced by c2/onepass_census.py\n"
                "# driving c2/onepass_probe.c.  `why` is `kind` for a lookaround,\n"
                "# backreference or subroutine call, `ambiguous` otherwise.\n")
        o.write("pop\tid\tstatus\tncap\tnodes\tonepass\twhy\tanchored\tcapped\n")
        for pop in ("hybrid17", "corpus", "corpus_utf8"):
            rows = runs[pop]
            for r in rows:
                o.write("\t".join([pop] + [r[k] for k in
                        ("id","status","ncap","nodes","onepass","why","anchored","capped")]) + "\n")
    for k, v in out.items():
        print(json.dumps(v, indent=1))

if __name__ == "__main__":
    main()
