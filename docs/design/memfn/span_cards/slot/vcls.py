# span_cards/slot/vcls.py — the VERIFY cost classes of the census's (form, cls) pairs, read off the kit's own
# T-CMP rows (memfn/src/runcmp.c) and set test (memfn/src/generic.c kit_set_test), over census0's J0 sweep.
#
# census0.out's `cls` vocabulary (rc: run length <= 8 "short" / "long"; settest: member count set1/set2/setN)
# is S2b's reading, not the text's. The text's real boundaries:
#   rc-words   the masked run's WORD COUNT D(L) = ceil(L / W), W = rc_width(L) (8 at L >= 8, 4 at L >= 4,
#              else 2): one load + mask + compare per word, joined by &&. Classes w1 (L in {2,4,8}),
#              w2 (L in {3,5,6,7,9..16}), w3 (L 17..24). "<= 8" put L 3 (two words) with L 8 (one).
#   rc-memcmp  gcc's constant memcmp: one load at L in {1,2,4,8} (class l1), a vector compare at L >= 16
#              (lv), a 2-4 piece chain elsewhere (lc, reached only under MF_D_RUN_OVERLAP).
#   rc-overlap two overlapping words at L in {3,5-7,9-15} (class o2).  rc-bytes: one test per position (bL).
#   settest    kit_set_test's COMPARE count: one per singleton or edge-touching range, two per inner range
#              (c1, c2, cn = three to seven, cn+ = more than seven: UNMEASURED, R-38 Part D D3). Member count is not the cost: [0-9] (10 members) is two
#              compares, the same as {X,x}.
# Population: every row-1-class window site (census0.row1_class) of every record, per arm; rc compares are
# read from the trace's `runcmp` row, L from the reply's stated run (run_len) or the plan's term (a pinned
# run absent: the plan's consecutive positions of one term); settest from each NONE alternative's span
# positions. Counts are SITES (census0 counts units; the two differ by repeats of one unit). R-38 Part D (D3): every
# site's derived run parts too, from their `run_part_terms` records (census0's ONE parser, `runpart_pop`): each
# multi-member SET term (settest, cls), the RUN term (rc-<row>, cls), a scan-less part (every-pos, -).
# LOWERING SHAPES (r9 EMIT-3, [rev1.3 r9fc-FIX-5]): a two-compare set test is classed by what gcc 15.2 -O2
# -march=x86-64 -mtune=generic (the declared target, §2.7) lowers it to, never by its spelling. `alu1`: ONE ALU op
# and ONE compare, i.e. any pair of singletons one bit apart ({X,x} `andl $-33; cmpb`, and {@,`} the same) or an
# inner range ([0-9] `subl $48; cmpb $9`), and the complement of one byte ([^x], one `cmpb`: at most one ALU op and
# one compare, S2e); `cmp2`: anything else (a pair differing in more than one bit, an edge range with one more),
# two compares. `shape` lines split class c2 by them, and the timed instance must be the
# majority shape (link.py), else its row is a lower bound.
# STAMPED (r9 SLOT-9): the header names the sweep's sha-256 and the commit census0 states it was swept at, so
# the plan's verify keys are reproducible from the tree plus that sweep.
#   python3 -I vcls.py CENSUS0_PY SWEEP_JSONL SOURCE_COMMIT > vcls.out
import collections, hashlib, importlib.util, json, sys

def load(path):
    spec = importlib.util.spec_from_file_location("census0", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def members(h):
    b = bytes.fromhex(h)
    return [i for i in range(256) if (b[i >> 3] >> (i & 7)) & 1]

def settest_cls(ms):
    if len(ms) == 256:
        return None
    rg = []
    for x in sorted(ms):
        if rg and x == rg[-1][1] + 1:
            rg[-1][1] = x
        else:
            rg.append([x, x])
    n = sum(1 if (lo == hi or lo == 0 or hi == 255) else 2 for lo, hi in rg)
    # R-38 Part D (part_d.md §5.1 D3 [r1pd F20]): cn is 3 to 7 compares (the measured `\w` instance's range);
    # above 7 is cn+, UNMEASURED, never priced by cn's row. census0.py's settest_cls holds the same bounds.
    return "c1" if n == 1 else "c2" if n == 2 else "cn" if n <= 7 else "cn+"

def shape(ms):
    """the lowering shape of a TWO-compare set test (members ms): `alu1` (one ALU op + one compare: a single-bit
    pair or an inner range) or `cmp2` (two compares); None for any other compare count"""
    rg = []
    for x in sorted(ms):
        if rg and x == rg[-1][1] + 1:
            rg[-1][1] = x
        else:
            rg.append([x, x])
    if sum(1 if (lo == hi or lo == 0 or hi == 255) else 2 for lo, hi in rg) != 2:
        return None
    if len(rg) == 2 and rg[0][0] == 0 and rg[1][1] == 255 and rg[1][0] == rg[0][1] + 2:
        return "alu1"       # [^x], every byte but one: gcc lowers it to ONE cmpb (S2e, ruled FIX-5)
    if len(rg) == 2 and all(lo == hi for lo, hi in rg):
        return "alu1" if bin(rg[0][0] ^ rg[1][0]).count("1") == 1 else "cmp2"
    return "alu1" if len(rg) == 1 else "cmp2"

def words(L):
    w = 8 if L >= 8 else 4 if L >= 4 else 2
    return -(-L // w)

def rc_cls(row, L):
    if row == "words":
        return "w%d" % words(L)
    if row == "memcmp":
        return "l1" if L in (1, 2, 4, 8) else "lv" if L >= 16 else "lc"
    if row == "overlap":
        return "o2"
    return "b%d" % L

def plan_run_len(wr):
    # the longest stretch of consecutive plan offsets sharing one term: the run the compare reads
    best, cur, prev = 0, 0, None
    for off, term in wr.get("plan", []):
        if prev and term == prev[1] and off == prev[0] + 1:
            cur += 1
        else:
            cur = 1
        prev = (off, term)
        best = max(best, cur)
    return best

def main():
    c0 = load(sys.argv[1])
    pop, shp = collections.Counter(), collections.Counter()
    for line in open(sys.argv[2]):
        rec = json.loads(line)
        for s in rec.get("sites", []):
            for k in c0.runpart_pop(s):
                pop[(rec["arm"],) + k] += 1
            alts = s.get("alts")
            if not alts or not any(c0.row1_class(a) for a in alts):
                continue
            wr = s.get("wr", {})
            L = wr.get("run_len", 0) if wr.get("run_stated") else plan_run_len(wr)
            for tb, row in s.get("trace", {}).get("ends", []):
                if tb == "runcmp" and row not in (None, "none", "-"):
                    pop[(rec["arm"], "rc-" + row, rc_cls(row, L))] += 1
            for a in alts:
                if a["entry"] != 1:
                    continue
                for sp in a["spans"]:
                    for h in sp["sets"]:
                        ms = members(h)
                        c = settest_cls(ms)
                        if c:
                            pop[(rec["arm"], "settest", c)] += 1
                        if c == "c2":
                            shp[(rec["arm"], "settest", "c2." + shape(ms))] += 1
    sha = hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()
    print("== vcls over %s (sha256 %s, swept at %s): verify (form, cls) by the T-CMP / set-test text's boundaries;"
          " counts are sites" % (sys.argv[2].split("/")[-1], sha, sys.argv[3]))
    for (arm, form, cls), n in sorted(pop.items()):
        print("%s\tverify\t%s\t%s\t%d" % (arm, form, cls, n))
    for (arm, form, cls), n in sorted(shp.items()):
        print("%s\tshape\t%s\t%s\t%d" % (arm, form, cls, n))

if __name__ == "__main__":
    main()
