#!/usr/bin/env python3
"""[FORM-CHAR2] (ii): the fold-class population.  For every unique corpus
`pattern`/`pattern-esc` line (emit_sweep.py's enumeration) plus every pcrec-bench
`bench/*/patterns/*.rx` (read-only), compile at default axes and forced
--engine=vm, read RX_ENGINE / RX_VM_CLS_FOLDS off the artifact, and count the
fold sites (`| 0x20) ==` tests) and the multiplicity of each fold constant.
Usage: fold_census.py --pcrec BIN [--bench DIR] [--jobs N] --out TSV
"""
import argparse, concurrent.futures, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TREE, "scripts"))
import emit_sweep  # noqa
SITE = re.compile(rb"\| 0x20\) == (\d+)\)")
def one(a):
    src, pcrec, pat, eng = a
    ok, art, _ = emit_sweep.compile_stream_c(pcrec, pat, 60, eng)
    if not ok: return None
    m = re.search(rb'#define RX_ENGINE "(\w+)"', art)
    f = re.search(rb"#define RX_VM_CLS_FOLDS (\d+)", art)
    consts = SITE.findall(art)
    mult = {}
    for c in consts: mult[c] = mult.get(c, 0) + 1
    return (src, eng or "default", m.group(1).decode() if m else "?", int(f.group(1)) if f else 0,
            len(consts), max(mult.values()) if mult else 0, len(mult))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pcrec", required=True)
    ap.add_argument("--bench"); ap.add_argument("--jobs", type=int, default=6); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pats = [("corpus", p) for _, _, p in emit_sweep.enumerate_corpus(a.pcrec, TREE, 60)]
    if a.bench:
        for f in sorted(glob.glob(os.path.join(a.bench, "*", "patterns", "*.rx"))):
            pats.append(("bench:" + f.split("/bench/")[1].split("/")[0], open(f, "rb").read().decode("utf-8", "surrogateescape").rstrip("\n")))
    seen = set(); uniq = []
    for s, p in pats:
        if p not in seen: seen.add(p); uniq.append((s, p))
    work = [(s, a.pcrec, p, e) for s, p in uniq for e in (None, "vm")]
    print("unique patterns", len(uniq), file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex, open(a.out, "w", errors="surrogateescape") as out:
        out.write("source\tengine_arm\tengine\tfold_classes\tfold_sites\tmax_mult\tdistinct_consts\tpattern\n")
        for w, r in zip(work, ex.map(one, work)):
            if r: out.write("\t".join(map(str, r)) + "\t" + repr(w[2][:160]) + "\n")
main()
