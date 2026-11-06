"""u2_fold_keep.py PCREC CASEFOLDING [--jobs N] -- Gate U2 of
docs/design/alt_normal_form.md §5 stage 1 (lane altbuild, 2026-11-06).

THE KEEP RULE, stated here and nowhere else: a simple fold class (CaseFolding
C+S, every member of one fold orbit) KEEPS the run when `(?i)abcd<X>efgh`,
X the orbit's fold target, compiled `-e utf8 --emit-facts=utf8`, reports a
`req_whole_run` of exactly 8 + len(utf8(X)) positions. The count is printed,
and so is its decomposition by SHAPE, the shapes computed from CaseFolding.txt
alone exactly as `docs/dev/lanes/altthink_evidence/shapes2.py` computes them
(no compiler code): the stage-1 prediction is that the kept set is EXACTLY
`ascii` + `exact/allcube<=2/contig` + `exact/allcube<=2/noncontig`
(24 + 489 + 253 = 766 at UCD 16.0.0). Exit 1 on any class kept outside those
shapes or not kept inside them (two-sided), or on an empty population."""
import collections, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

def shapes(path):
    groups = collections.defaultdict(set)
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line: continue
        f = [x.strip() for x in line.split(";")]
        if f[1] not in ("C", "S"): continue
        s, d = int(f[0], 16), int(f[2], 16)
        groups[d] |= {s, d}
    def contiguous(cps):
        cps = sorted(cps); return cps[-1] - cps[0] == len(cps) - 1
    def cube(bs):
        bs = list(bs); k = 0xFF
        for b in bs[1:]: k &= ~(b ^ bs[0])
        return (1 << (8 - bin(k & 0xFF).count("1"))) == len(bs)
    out = {}
    for t, mem in groups.items():
        encs = [chr(x).encode() for x in mem]
        lens = {len(e) for e in encs}
        if lens == {1}: out[t] = "ascii"; continue
        if len(lens) > 1: out[t] = "mixed"; continue
        n = lens.pop()
        pos = [{e[i] for e in encs} for i in range(n)]
        prod = 1
        for p in pos: prod *= len(p)
        exact = prod == len(encs)
        allcube = all(cube(p) for p in pos)
        out[t] = (("exact" if exact else "superset") + "/" +
                  ("allcube<=2" if allcube and all(len(p) <= 2 for p in pos)
                   else ("allcube" if allcube else "noncube")) + "/" +
                  ("contig" if contiguous(mem) else "noncontig"))
    return out

def keeps(pcrec, t):
    x = chr(t)
    r = subprocess.run(["gnutimeout", "60", pcrec, "-p", "rx", "--emit-facts=utf8",
                        "--pattern", "(?i)abcd" + x + "efgh"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        f = line.split("\t")
        if len(f) > 6 and f[1] == "req_whole_run":
            v = f[6].split("/")[0]
            return v != "none" and len(v) // 2 == 8 + len(x.encode())
    return False

def main():
    pcrec, cf = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    sh = shapes(cf)
    with ThreadPoolExecutor(jobs) as ex:
        kept = dict(zip(sh, ex.map(lambda t: keeps(pcrec, t), sh)))
    want = {"ascii", "exact/allcube<=2/contig", "exact/allcube<=2/noncontig"}
    by = collections.Counter(sh[t] for t in sh if kept[t])
    bad = [t for t in sh if kept[t] != (sh[t] in want)]
    print("population %d fold classes" % len(sh))
    for k in sorted(by): print("kept %d %s" % (by[k], k))
    print("U2 keep count %d" % sum(kept.values()))
    for t in sorted(bad)[:40]:
        print("MISMATCH U+%04X shape=%s kept=%s" % (t, sh[t], kept[t]))
    print("U2 %s (%d mismatches)" % ("PASS" if not bad and sh else "FAIL", len(bad)))
    sys.exit(1 if bad or not sh else 0)

main()
