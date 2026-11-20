#!/usr/bin/env python3
"""l3feat2: two-sided compare of a BASE and a FEATURE build over the census
population (census_l1.population: every .rxt pattern of the base tree + the
bench file). Per distinct text: the byte-encoding facts req_whole_run,
req_landmark_maxoff, req_byte, run_pin, and the stamps REQ_WHY, REQ_HANDOFF,
REQ_RUN, REQ_BYTE, DFA_SCAN, DFA_PREFILTER, VM_PREFILTER at the default
engine and at --engine=vm; plus the .c text with the abi number masked.
usage: cmp_l3.py BASEBIN FEATBIN BASETREE BENCHFILE OUTDIR [--jobs N]"""
import concurrent.futures as cf, importlib.util, os, re, subprocess, sys

L1P = "/home/pcrec/projects/pcrec/worktrees/l3feat/docs/dev/lanes/l1build_evidence/census_l1.py"
sp = importlib.util.spec_from_file_location("census_l1", L1P)
L1 = importlib.util.module_from_spec(sp); sp.loader.exec_module(L1)
FACTS = ("req_whole_run", "req_landmark_maxoff", "req_byte", "run_pin")
STAMPS = ("REQ_WHY", "REQ_HANDOFF", "REQ_RUN", "REQ_BYTE", "DFA_SCAN", "DFA_PREFILTER", "VM_PREFILTER")
ABI = re.compile(rb"\b1(09|10)\b")


def facts(b, pat):
    try:
        r = subprocess.run([b, "-p", "rx", "--features", "all", "--emit-facts=byte", "--pattern", pat],
                           capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode:
        return "REFUSED"
    d = {}; sec = None
    for ln in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if ln.startswith("#section "): sec = ln.split()[1]; continue
        if ln.startswith("#") or sec != "facts": continue
        x = ln.split("\t")
        if x[0] == "byte" and x[1] in FACTS: d[x[1]] = x[6]
    return tuple(d.get(f) for f in FACTS)


def cfile(b, pat, eng, out):
    a = [b, "-p", "rx", "--features", "all", "--pattern", pat, "-o", out]
    if eng: a.insert(1, "--engine=vm")
    try:
        r = subprocess.run(a, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None
    if r.returncode:
        return "REFUSED", None
    t = open(out, "rb").read(); os.unlink(out)
    st = tuple((re.search(rb'#define\s+RX_%s\s+"([^"]*)"' % k.encode(), t) or [None, b"-"])[1].decode("latin-1")
               for k in STAMPS)
    return st, ABI.sub(b"ABI", t)


def one(a):
    base, feat, pat, tmp = a
    rec = {"pat": pat}
    rec["fb"], rec["ff"] = facts(base, pat), facts(feat, pat)
    for eng in ("", "vm"):
        o = os.path.join(tmp, "%d_%x.c" % (os.getpid(), abs(hash((pat, eng, os.urandom(4))))))
        sb, cb = cfile(base, pat, eng, o)
        sf, cf_ = cfile(feat, pat, eng, o)
        rec["s" + eng] = (sb, sf)
        rec["c" + eng] = cb == cf_
    return rec


def main():
    a = sys.argv[1:]; jobs = 12
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    base, feat, tree, bench, out = a
    os.makedirs(out, exist_ok=True); tmp = os.path.join(out, "tmp"); os.makedirs(tmp, exist_ok=True)
    pop = L1.population(base, tree, bench)
    seen = {}
    for src, pat in pop: seen.setdefault(pat, []).append(src)
    with cf.ThreadPoolExecutor(jobs) as ex:
        recs = list(ex.map(one, [(base, feat, p, tmp) for p in seen]))
    fm = [r for r in recs if r["fb"] != r["ff"]]
    sm = [r for r in recs if r["s"][0] != r["s"][1] or r["svm"][0] != r["svm"][1]]
    cm = [r for r in recs if not (r["c"] and r["cvm"])]
    def src(r):
        s = seen[r["pat"]]
        return ("bench" if any(x.startswith("bench:") for x in s) else "corpus") + ":" + s[0]
    with open(os.path.join(out, "movers.tsv"), "w") as f:
        f.write("kind\tsrc\tpattern\tbase\tfeat\n")
        for r in fm: f.write("facts\t%s\t%s\t%s\t%s\n" % (src(r), L1.esc(r["pat"]), r["fb"], r["ff"]))
        for r in sm:
            for e in ("", "vm"):
                if r["s" + e][0] != r["s" + e][1]:
                    f.write("stamps%s\t%s\t%s\t%s\t%s\n" % (e and "-vm", src(r), L1.esc(r["pat"]), r["s" + e][0], r["s" + e][1]))
        for r in cm:
            f.write("ctext\t%s\t%s\tdefault-identical=%s\tvm-identical=%s\n" % (src(r), L1.esc(r["pat"]), r["c"], r["cvm"]))
    print("population rows %d (corpus %d, bench %d), distinct texts %d" % (
        len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")), sum(1 for s, _ in pop if s.startswith("bench:")), len(seen)))
    print("fact movers (req_whole_run/req_landmark_maxoff/req_byte/run_pin, byte): %d" % len(fm))
    print("stamp movers (default or vm): %d" % len(sm))
    print(".c text movers (abi number masked): %d" % len(cm))
    print("non-lookbehind texts among any mover: %d" % sum(1 for r in {id(x): x for x in fm + sm + cm}.values() if b"(?<=" not in r["pat"]))


if __name__ == "__main__":
    main()
