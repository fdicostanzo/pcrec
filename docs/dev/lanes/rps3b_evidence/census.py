"""census.py HARNESS TREE BENCH_DIR [--jobs N] -- [RUN-POS-SET] stage 3 step 0's
COUNTED LISTING (manager ruling 2026-11-13: a listing in the report, NOT a gate;
lane rps3b). Population and its reading are p2_census.py's (altbuild_evidence/):
every corpus pattern block and every bench pattern, compiled `--features all
--emit-facts` by build/pcrec-harness under four lever sets: default, the stage-3
domain (`run-pos-sets`), `rr_alt` row 1 (`alt-union-run`), and both. Each compile's
`req_whole_run` value is compared with the default's; a mover is counted by kind:
new (none -> a run), moved (a run -> another), lost (a run -> none), refused
(the compile is refused: today's kit, K-1, the run Part D lifts), plus the
default's own refusals. NOT INDEPENDENT: the run comes from pcrec's own walk
under its levers (the memo's independent model is OWED, see the report)."""
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

CONFIGS = [("default", []), ("sets", ["--harness=run-pos-sets"]),
           ("alt", ["--harness=alt-union-run"]),
           ("sets+alt", ["--harness=run-pos-sets", "--harness=alt-union-run"])]

def one(args):
    pcrec, (where, pat, flags, enc) = args
    inl = "".join(x for x in flags if x in "msx")
    if inl: pat = b"(?" + inl.encode() + b")" + pat
    out = []
    for _, lv in CONFIGS:
        argv = [pcrec, "-p", "rx", "-e", enc, "--features", "all", "--emit-facts=" + enc] + lv
        if "i" in flags: argv.append("-i")
        try:
            r = subprocess.run(argv + ["--pattern", pat], capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            out.append("TIMEOUT"); continue
        if r.returncode:
            e = r.stderr.decode("utf-8", "replace")
            out.append("KIT-REFUSED" if "memfn kit refused" in e else "REFUSED"); continue
        v = "NO-ROW"
        for line in r.stdout.decode("utf-8", "replace").splitlines():
            c = line.split("\t")
            if len(c) > 7 and c[1] == "req_whole_run": v = c[6]; break
        out.append(v)
    return where, pat, enc, out

def kind(d, v):
    if v in ("KIT-REFUSED", "REFUSED", "TIMEOUT", "NO-ROW"): return v.lower()
    if d == v: return None
    if d == "none": return "new"
    if v == "none": return "lost"
    return "moved"

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    pcrec, tree, broot = a
    pats = corpus(pcrec, tree) + bench(broot)
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, [(pcrec, p) for p in pats]))
    print("population: %d patterns (%d corpus, %d bench), %d compiles" % (
        len(res), sum(1 for r in res if not r[0].startswith("bench/")),
        sum(1 for r in res if r[0].startswith("bench/")), 4 * len(res)))
    dflt = collections.Counter(r[3][0] if r[3][0] in ("KIT-REFUSED", "REFUSED", "TIMEOUT", "NO-ROW")
                               else ("run" if r[3][0] != "none" else "none") for r in res)
    print("default: " + ", ".join("%s %d" % kv for kv in sorted(dflt.items())))
    for ci, (name, _) in enumerate(CONFIGS[1:], 1):
        cnt = collections.Counter()
        for where, pat, enc, out in res:
            if out[0] in ("KIT-REFUSED", "REFUSED", "TIMEOUT", "NO-ROW"): continue
            k = kind(out[0], out[ci])
            if k: cnt[(enc, "bench" if where.startswith("bench/") else "corpus", k)] += 1
        tot = sum(cnt.values())
        print("\n== %s: %d movers vs default" % (name, tot))
        for k, n in sorted(cnt.items()):
            print("  %-5s %-6s %-12s %d" % (k + (n,)))
    print("\n== bench movers (every config), pattern: default -> sets -> alt -> sets+alt")
    for where, pat, enc, out in res:
        if where.startswith("bench/") and len(set(out)) > 1:
            print("  %s\t%s\t%s" % (where, pat.decode("utf-8", "replace")[:60], " -> ".join(out)))
    print("\n== rule (1) movers (alt vs default, and sets+alt vs sets), corpus and bench")
    for where, pat, enc, out in res:
        if out[1] != out[3] or out[0] != out[2]:
            print("  %s\t%s\t%s" % (where, pat.decode("utf-8", "replace")[:60], " -> ".join(out)))

main()
