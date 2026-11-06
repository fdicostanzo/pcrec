"""p2_census.py PCREC TREE BENCH_DIR [--jobs N] -- Stage 2p's group-count
census (docs/design/alt_normal_form.md §3.4 "Bound", r4 RDY-6a: the census
runs BEFORE the limits.def row lands, so the row never holds a presumed
value; lane altbuild, 2026-11-06).

Run on a build whose group bound is a CENSUS-ONLY 4096 (never committed).
Population: every corpus pattern block (TREE/tests/**/*.rxt via `pcrec
--list-source`, at its block's or file head's encoding, `byte` where none)
and every BENCH_DIR/*/patterns/*.rx line (`utf8` under bench/utf8, `byte`
elsewhere), compiled `--features all --emit-facts`. Prints the distribution
of `req_pieces`' group count (declines by reason), the maximum, and the
patterns at the top of the distribution."""
import collections, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

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
            line = open(os.path.join(d, f), "rb").read().split(b"\n")[0]
            if line:
                pats.append(("bench/%s/%s" % (sub, f), line, "", "utf8" if sub == "utf8" else "byte"))
    return pats

def one(args):
    pcrec, (where, pat, flags, enc) = args
    inl = "".join(x for x in flags if x in "msx")
    if inl: pat = b"(?" + inl.encode() + b")" + pat
    argv = [pcrec, "-p", "rx", "-e", enc, "--features", "all", "--emit-facts=" + enc]
    if "i" in flags: argv.append("-i")
    try:
        r = subprocess.run(argv + ["--pattern", pat], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return where, pat, "TIMEOUT"
    if r.returncode: return where, pat, "REFUSED"
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        c = line.split("\t")
        if len(c) > 7 and c[1] == "req_pieces":
            if c[7]: return where, pat, c[7]
            return where, pat, "groups=%d" % (c[6].count("|") + 1)
    return where, pat, "NO-ROW"

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    pcrec, tree, broot = a
    pats = corpus(pcrec, tree) + bench(broot)
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, [(pcrec, p) for p in pats]))
    dist = collections.Counter(r[2] for r in res)
    print("population: %d compiles" % len(res))
    for k, n in sorted(dist.items(), key=lambda kv: (not kv[0].startswith("groups="), kv[0])):
        print("  %-28s %d" % (k, n))
    g = [(int(r[2][7:]), r) for r in res if r[2].startswith("groups=")]
    g.sort(key=lambda x: -x[0])
    print("max groups: %d" % (g[0][0] if g else 0))
    for n, r in g[:15]:
        print("  %d\t%s\t%s" % (n, r[0], r[1].decode("utf-8", "replace")[:80]))
    bad = dist.get("NO-ROW", 0) + dist.get("TIMEOUT", 0)
    if bad or dist.get("REFUSED", 0) * 5 > len(res):
        print("p2 census: FAIL (a row is missing, a compile timed out, or over a fifth refused)")
        sys.exit(1)
    print("p2 census: PASS")

main()
