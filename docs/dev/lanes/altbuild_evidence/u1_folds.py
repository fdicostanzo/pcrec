"""u1_folds.py BASE_PCREC STAGE_PCREC CASEFOLDING SCRATCH [--jobs N] -- Gates
U1 (fold population) and U3 of docs/design/alt_normal_form.md §5 stage 1
(lane altbuild, 2026-11-06).

THE MODEL shares no code with pcrec: each fold orbit's code points are split
into UTF-8 boxes here (members of one byte length sharing all but the last
byte, contiguous last bytes one range: u8_box's shape for these sets) and
step M of §3.3 runs here (width ascending, last position first, sweeps to a
fixpoint, the adjacency test's rows 1/2 computed, never assumed). For each
class X in `(?i)abcd<X>efgh` -e utf8 it predicts, PER OBSERVABLE:
  run      the stage run EQUALS the run pcrec -e byte (altcls denied) reports
           for the model's merged boxes spelled as a byte pattern (the
           pred.py method: req.c reads that spelling, nothing in the lowering
           or the owner is exercised)
  tables   per machine (forward, reverse, anchored): next-state entries move
           iff the byte ALPHABET partition moves (the coarsest partition of
           0..255 refining every position set of the pattern's byte
           spelling): every machine is minimized and the language is
           unchanged, so a merge reaches the table only through the columns;
           and U3, no machine grows
  ASCII    a class whose members are all <= 0x7F is never lowered: predicted
           a non-mover on every observable
  vmbytes  RX_VM_PROGRAM_BYTES (--engine=vm -fno-cls-kit) moves iff more
           than one box (the seal's `empty` label) or a merge fires
  islands  RX_VM_ALT_ISLANDS falls 1 -> 0 iff the base admits the bare
           class's island and a fold fires; otherwise equal
  rungs    equal (no quantifier in this population)
An unpredicted mover, or a predicted mover that does not move, is printed
with the observable; exit 1 on any."""
import collections, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

def orbits(path):
    g = collections.defaultdict(set)
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line: continue
        f = [x.strip() for x in line.split(";")]
        if f[1] not in ("C", "S"): continue
        s, d = int(f[0], 16), int(f[2], 16)
        g[d] |= {s, d}
    return g

def boxes(cps):
    by = collections.defaultdict(list)
    for e in sorted(chr(c).encode() for c in cps): by[e[:-1]].append(e[-1])
    out = []
    for pre, lasts in sorted(by.items(), key=lambda kv: (len(kv[0]), kv[0])):
        lasts.sort(); run = [lasts[0]]
        for b in lasts[1:] + [None]:
            if b is not None and b == run[-1] + 1: run.append(b); continue
            out.append([{x} for x in pre] + [set(range(run[0], run[-1] + 1))])
            if b is not None: run = [b]
    return out

def merge(br):
    """Step M over boxes (lists of byte sets), declared order."""
    br = [list(b) for b in br]
    def passes(m, j):
        for p in range(min(len(m), len(j))):
            if not (m[p] & j[p]): return True
        return len(m) == len(j)
    while True:
        folds = 0
        for w in sorted({len(b) for b in br}):
            for p in range(w - 1, -1, -1):
                heads, out = [], []
                for b in br:
                    if len(b) != w: out.append(b); continue
                    into = None
                    for hi in range(len(heads) - 1, -1, -1):
                        h = heads[hi]
                        if any(h[i] != b[i] for i in range(w) if i != p): continue
                        ih = next(k for k, x in enumerate(out) if x is h)
                        if not all(passes(m, b) for m in out[ih + 1:]): break
                        into = h
                    if into is not None:
                        into[p] = into[p] | b[p]; folds += 1
                    else:
                        heads.append(b); out.append(b)
                br = out
        if not folds: return br

def partition(atoms):
    """Block count of the coarsest partition of 0..255 refining every atom."""
    sig = {}
    for b in range(256):
        sig.setdefault(tuple(b in a for a in atoms), 0)
    return len(sig)

LETTERS = [{ord(c), ord(c.upper())} for c in "abcdefgh"]

def bx(b): return "\\x%02x" % b
def spell(br):
    def ps(s):
        s = sorted(s)
        return bx(s[0]) if len(s) == 1 else "[" + "".join(bx(b) for b in s) + "]"
    alts = ["".join(ps(p) for p in b) for b in br]
    return alts[0] if len(alts) == 1 else "(?:" + "|".join(alts) + ")"

def run_of(pcrec, enc, pat, extra=()):
    r = subprocess.run(["gnutimeout", "60", pcrec, "-p", "rx", "--emit-facts=" + enc,
                        *extra, "--pattern", pat], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        f = line.split("\t")
        if len(f) > 6 and f[1] == "req_whole_run": return f[6]
    return "?"

def artifact(pcrec, pat, out, extra=()):
    r = subprocess.run(["gnutimeout", "60", pcrec, "-p", "rx", "-e", "utf8", *extra,
                        "-o", out, "--pattern", pat], capture_output=True, text=True)
    if r.returncode: return None
    return open(out, encoding="latin-1").read()

def tables(src):
    t = {}
    for m in re.finditer(r"rx_(\w+?)_next_state\[(\d+)\]", src): t[m.group(1)] = int(m.group(2))
    return t

def stamp(src, name):
    m = re.search(r"#define RX_%s\s+(\S+)" % name, src)
    return m.group(1) if m else None

def one(args):
    base, stage, scratch, t, cps = args
    pat = "(?i)abcd" + chr(t) + "efgh"
    ub = boxes(cps); mb = merge(ub)
    ascii = max(cps) <= 0x7F
    fold = len(mb) < len(ub) and not ascii
    cols = (not ascii and partition(LETTERS + [p for b in ub for p in b]) !=
            partition(LETTERS + [p for b in mb for p in b]))
    o = os.path.join(scratch, "u1_%04x" % t)
    res = []
    # run
    pred = run_of(stage, "byte", "[aA][bB][cC][dD]" + spell(mb) + "[eE][fF][gG][hH]",
                  ("-fno-altcls-merge", "-fno-altcls-factor"))
    got = run_of(stage, "utf8", pat)
    if pred != got: res.append("run predicted %s got %s" % (pred, got))
    # tables, U3
    sb, ss = artifact(base, pat, o + "b.c"), artifact(stage, pat, o + "s.c")
    if sb is None or ss is None:
        res.append("refused base=%s stage=%s" % (sb is None, ss is None))
        return t, cps, ub, mb, res
    tb, ts = tables(sb), tables(ss)
    moved = tb != ts
    if moved != cols: res.append("tables moved=%s columns-moved=%s %s -> %s" % (moved, cols, tb, ts))
    for k in set(tb) & set(ts):
        if ts[k] > tb[k]: res.append("U3 GROWTH %s %d -> %d" % (k, tb[k], ts[k]))
    # VM program bytes, islands, rungs
    vb = artifact(base, pat, o + "vb.c", ("--engine=vm", "-fno-cls-kit"))
    vs = artifact(stage, pat, o + "vs.c", ("--engine=vm", "-fno-cls-kit"))
    pb, ps_ = stamp(vb, "VM_PROGRAM_BYTES"), stamp(vs, "VM_PROGRAM_BYTES")
    if (pb != ps_) != (not ascii and (len(ub) > 1 or fold)):
        res.append("vmbytes %s -> %s boxes=%d fold=%s" % (pb, ps_, len(ub), fold))
    ib, is_ = stamp(vb, "VM_ALT_ISLANDS"), stamp(vs, "VM_ALT_ISLANDS")
    want = "0" if (ib == "1" and fold) else ib
    if is_ != want: res.append("islands %s -> %s fold=%s" % (ib, is_, fold))
    if stamp(vb, "VM_RUNGS") != stamp(vs, "VM_RUNGS"): res.append("rungs moved")
    return t, cps, ub, mb, res

def main():
    base, stage, cf, scratch = sys.argv[1:5]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    os.makedirs(scratch, exist_ok=True)
    g = orbits(cf)
    work = [(base, stage, scratch, t, cps) for t, cps in sorted(g.items())]
    bad = 0; folds = 0; multi = 0
    with ThreadPoolExecutor(jobs) as ex:
        for t, cps, ub, mb, res in ex.map(one, work):
            folds += len(mb) < len(ub); multi += len(ub) > 1
            for r in res:
                bad += 1
                print("U+%04X boxes %d->%d: %s" % (t, len(ub), len(mb), r))
    print("population %d fold classes; %d multi-box; %d with a fold" % (len(g), multi, folds))
    print("U1(folds)+U3 %s (%d findings)" % ("PASS" if not bad and g else "FAIL", bad))
    sys.exit(1 if bad or not g else 0)

main()
