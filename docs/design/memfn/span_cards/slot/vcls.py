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
#              (c1, c2, cn = three or more). Member count is not the cost: [0-9] (10 members) is two
#              compares, the same as {X,x}.
# Population: every row-1-class window site (census0.row1_class) of every record, per arm; rc compares are
# read from the trace's `runcmp` row, L from the reply's stated run (run_len) or the plan's term (a pinned
# run absent: the plan's consecutive positions of one term); settest from each NONE alternative's span
# positions. Counts are SITES (census0 counts units; the two differ by repeats of one unit).
#   python3 -I vcls.py CENSUS0_PY SWEEP_JSONL > vcls.out
import collections, importlib.util, json, sys

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
    return "c1" if n == 1 else "c2" if n == 2 else "cn"

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
    pop = collections.Counter()
    for line in open(sys.argv[2]):
        rec = json.loads(line)
        for s in rec.get("sites", []):
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
                        c = settest_cls(members(h))
                        if c:
                            pop[(rec["arm"], "settest", c)] += 1
    print("== vcls over %s: verify (form, cls) by the T-CMP / set-test text's boundaries; counts are sites"
          % sys.argv[2].split("/")[-1])
    for (arm, form, cls), n in sorted(pop.items()):
        print("%s\tverify\t%s\t%s\t%d" % (arm, form, cls, n))

main()
