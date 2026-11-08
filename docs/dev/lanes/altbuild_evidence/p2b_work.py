"""p2b_work.py PCREC TREE BENCH_DIR [--jobs N] -- Stage 2b's work census
(docs/design/alt_normal_form.md §3.3 r7 SIM-3 (b)/(c), §5 2b Gates: the
owner's work bound is a limits row whose value this census sets, no
presumed value; lane altbuild, 2026-11-06).

Run on a CENSUS-ONLY build (never committed): `PCREC_MAX_ALTNF_WORK`
unbounded and `pcrec_altnf` printing `ALTNF_WORK <work> <caller> <n>` to
stderr per call (caller `altcls`, rules {M,P,S}, or `lower`, {M}).
Population: every corpus pattern block (TREE/tests/**/*.rxt via `pcrec
--list-source`, at its encoding, `byte` where none) and every
BENCH_DIR/*/patterns/*.rx pattern (whole file less one trailing newline;
`utf8` under bench/utf8), compiled `--features all -e ENC -o -` on the
default route. Prints per caller the call count, the distribution's
quantiles, the maximum and the top patterns."""
import collections, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
            head_enc, seen = "", False
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#"): continue
                c = line.split("\t")
                if len(c) < 10: continue
                if c[0] == "encoding" and not seen: head_enc = c[3]
                if c[0] not in ("pattern", "pattern-esc"): continue
                seen = True
                enc = c[8] or head_enc or "byte"
                if enc not in ("byte", "utf8"): continue
                pats.append((os.path.relpath(p, tree) + ":" + c[1], unesc(c[4]), c[5], enc))
    return pats

def bench(root):
    pats = []
    for sub in sorted(os.listdir(root)):
        d = os.path.join(root, sub, "patterns")
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".rx"): continue
            b = open(os.path.join(d, f), "rb").read()
            if b.endswith(b"\n"): b = b[:-1]
            if b:
                pats.append(("bench/%s/%s" % (sub, f), b, "", "utf8" if sub == "utf8" else "byte"))
    return pats

def one(args):
    pcrec, (where, pat, flags, enc) = args
    inl = "".join(x for x in flags if x in "msx")
    if inl: pat = b"(?" + inl.encode() + b")" + pat
    argv = [pcrec, "-p", "rx", "-e", enc, "--features", "all", "-o", "-"]
    if "i" in flags: argv.append("-i")
    try:
        r = subprocess.run(argv + ["--pattern", pat], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return where, pat, None, "TIMEOUT"
    calls = []
    for line in r.stderr.decode("utf-8", "replace").splitlines():
        c = line.split("\t")
        if c[0] == "ALTNF_WORK": calls.append((int(c[1]), c[2], int(c[3])))
    return where, pat, calls, "ok" if r.returncode == 0 else "refused"

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    pcrec, tree, broot = a
    pats = corpus(pcrec, tree) + bench(broot)
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, [(pcrec, p) for p in pats]))
    st = collections.Counter(r[3] for r in res)
    print("population: %d compiles (%s)" % (len(res), ", ".join("%s %d" % kv for kv in sorted(st.items()))))
    for caller in ("altcls", "lower"):
        ws = sorted(((w, n, r[0], r[1]) for r in res if r[2] for (w, c, n) in r[2] if c == caller),
                    key=lambda x: -x[0])
        if not ws: print("%s: no calls" % caller); continue
        vals = sorted(x[0] for x in ws)
        q = lambda f: vals[min(len(vals) - 1, int(f * len(vals)))]
        print("%s: %d calls; work p50 %d p99 %d p99.9 %d max %d" % (caller, len(vals), q(.5), q(.99), q(.999), vals[-1]))
        for w, n, where, pat in ws[:8]:
            print("  %d\tbranches=%d\t%s\t%s" % (w, n, where, pat.decode("utf-8", "replace")[:70]))
    bad = st.get("TIMEOUT", 0)
    if bad or not any(r[2] for r in res):
        print("p2b work census: FAIL (a timeout, or no call printed: not a census build)")
        sys.exit(1)
    print("p2b work census: PASS")

main()
