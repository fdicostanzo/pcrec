"""u4_census.py BASE_PCREC STAGE_PCREC TREE BENCH_UTF8_DIR OUT [--jobs N] --
Gate U4's island and rung census of docs/design/alt_normal_form.md §5 stage 1
(lane altbuild, 2026-11-06; manager ruling R1 in altbuild_rulings.md).

POPULATION: every utf8 pattern block of the corpus (`pcrec --list-source`
over TREE/tests/**/*.rxt, the block's `encoding` or its file head's) and
every `BENCH_UTF8_DIR/*.rx` line. Each is compiled `-e utf8 --features all`
on four axes: {--engine=vm, auto} x {default, -fno-cls-kit}, by BASE and by
STAGE, and `RX_VM_ALT_ISLANDS` and `RX_VM_RUNGS` are read off the artifact
(`-` where the artifact has none: a DFA artifact, or a refusal, kept apart).

THE CLAIM, two-sided: an island or rung that moves base -> stage is a
D186 choice cell of the stage's merge, and every one is RESTORED by bit 10:
the same compile on STAGE with `-fno-altcls-merge` reads the base value. A
mover bit 10 does not restore is UNRESTORED (a finding: the stage moved it
by something other than the merge). The family column is a reading aid,
not a model: `bare` = the pattern has no `|` (U1's bare-class islands /
the rung flips), `alt` = it has one (R1's size-knee family or a bare class
inside a larger pattern) -- the report reads each `alt` cell by hand.
Output: OUT/u4_movers.tsv and a summary on stdout; exit 1 on any UNRESTORED
mover or any refusal that differs base vs stage."""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

AXES = [("vm", ["--engine=vm"]), ("vm-nokit", ["--engine=vm", "-fno-cls-kit"]),
        ("auto", []), ("auto-nokit", ["-fno-cls-kit"])]
STAMP = re.compile(rb'^#define RX_VM_(ALT_ISLANDS|RUNGS) (\S+)', re.M)

def unesc(s):
    out, i = bytearray(), 0
    b = s.encode("utf-8", "surrogateescape")
    while i < len(b):
        if b[i] == 0x5c and i + 1 < len(b):
            c = chr(b[i + 1])
            if c == "x": out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
            out.append({"t": 9, "n": 10, "r": 13, "\\": 92}.get(c, b[i + 1])); i += 2; continue
        out.append(b[i]); i += 1
    return bytes(out)

def corpus(pcrec, tree):
    pats = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in sorted(fs):
            if not f.endswith(".rxt"): continue
            p = os.path.join(d, f)
            r = subprocess.run([pcrec, "--list-source", p], capture_output=True, timeout=60)
            if r.returncode: continue
            head_enc, seen_pat = "", False
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#"): continue
                c = line.split("\t")
                if len(c) < 10: continue
                if c[0] == "encoding" and not seen_pat: head_enc = c[3]
                if c[0] not in ("pattern", "pattern-esc"): continue
                seen_pat = True
                if (c[8] or head_enc) != "utf8": continue
                pats.append((os.path.relpath(p, tree) + ":" + c[1], unesc(c[4]), c[5]))
    return pats

def bench(d):
    pats = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".rx"): continue
        for i, line in enumerate(open(os.path.join(d, f), "rb").read().split(b"\n")):
            if line: pats.append(("bench/utf8/" + f + ":" + str(i + 1), line, ""))
    return pats

def compile_(pcrec, pat, flags, extra):
    inl = "".join(x for x in flags if x in "msx")
    if inl: pat = b"(?" + inl.encode() + b")" + pat
    argv = [pcrec, "-p", "rx", "-e", "utf8", "--features", "all", "-o", "/dev/stdout"]
    if "i" in flags: argv.append("-i")
    argv += extra + ["--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode: return "REFUSED"
    st = dict((k.decode(), v.decode()) for k, v in STAMP.findall(r.stdout))
    return "%s/%s" % (st.get("ALT_ISLANDS", "-"), st.get("RUNGS", "-"))

def cell(args):
    base, stage, (where, pat, flags), (ax, extra) = args
    b = compile_(base, pat, flags, extra)
    s = compile_(stage, pat, flags, extra)
    d = compile_(stage, pat, flags, extra + ["-fno-altcls-merge"]) if b != s else s
    return where, pat, ax, b, s, d

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    base, stage, tree, bdir, out = a
    pats = corpus(stage, tree) + bench(bdir)
    tasks = [(base, stage, p, ax) for p in pats for ax in AXES]
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(cell, tasks))
    bad = 0; movers = []
    for where, pat, ax, b, s, d in res:
        if b == s: continue
        if "REFUSED" in (b, s) or "TIMEOUT" in (b, s):
            verdict = "REFUSAL-MOVED"; bad += 1
        elif d == b:
            verdict = "restored-by-bit10"
        else:
            verdict = "UNRESTORED"; bad += 1
        fam = "alt" if b"|" in pat else "bare"
        movers.append((where, pat.decode("utf-8", "replace"), ax, b, s, d, fam, verdict))
    with open(os.path.join(out, "u4_movers.tsv"), "w") as f:
        f.write("where\tpattern\taxis\tbase isl/rungs\tstage\tstage -fno-altcls-merge\tfamily\tverdict\n")
        for m in movers: f.write("\t".join(m) + "\n")
    print("population: %d utf8 patterns (%d corpus, %d bench) x %d axes = %d cells"
          % (len(pats), len(pats) - len(bench(bdir)), len(bench(bdir)), len(AXES), len(res)))
    print("refused on both builds: %d cells" % sum(1 for r in res if r[3] == r[4] == "REFUSED"))
    print("movers: %d (restored by bit 10: %d; findings: %d)"
          % (len(movers), sum(1 for m in movers if m[7] == "restored-by-bit10"), bad))
    for m in movers: print("\t".join(m))
    print("U4 census: %s" % ("FAIL" if bad else "PASS"))
    sys.exit(1 if bad else 0)

main()
