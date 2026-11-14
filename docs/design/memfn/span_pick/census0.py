#!/usr/bin/env python3
"""span_pick stage 2, unit S2b: the step-0 census (span_cards.md rev 1.1 §7), the ONE kit-side pricer of
span_pick's formula. It REPLACES smp20.py (smp20 is census0 on one site) and generalizes it to every window
site of R-33's sweep.

    python3 -I census0.py control WITNESS.out PRIOR.list -- NAME=BUNDLE.list ...   > smp20.out
    python3 -I census0.py sweep SWEEP.jsonl [-o census0.out] [--note TEXT]
    python3 -I census0.py forecast SWEEP.jsonl --measures SET.tsv [--swept-at COMMIT] [-o census0_cards.out]

CONTROL: smp20 `(?i)x/1234` priced with the note's formula (§The pick: no `streams` factor, byte(m) = the
method's cost per subject byte over all its streams) under ONE rate model per compile (D186 add. 2): a BLIND
compile prices under P, the default prior for its encoding, alone; a WITH-DATA compile under the named bundle
alone. WITNESS.out is witness.sh's output (its default-arm and DEF-deny lines are TODAY's picks, the
incumbents); each .list is `pcrec --list-analysis NAME [-I DIR]` output (its `#section freq` rows).
The output is `smp20.out` byte for byte (the golden, committed) PLUS ONE appended line: P's BLIND argmin over
the same 3,536-point grid the with-data bundles are counted on (span_pick.md: "P's argmin is '/' at 3,381").

SWEEP: the same pricer over every window site of R-33's raw sweep (collect.py's JSONL; the byte rates are the
sweep's `.rates.json`, digest a322116b1b87f9f6 = P). Each candidate (alternative x core position x method) is
priced under P at the CORNERS of smp20's grid (k = byte(PAIR)/byte(memchr) 1.00 and 12.00; hit(memchr) h1 5
and 40; hit(PAIR) 1x and 8x h1) and the BAND-0 argmin is compared with the incumbent READ FROM THE TRACE
(wr = the kit's phase-1 reply: alternative and stop offset; `trace.fdroute`/`ends` = the method). Output (1):
movers by class; output (2): the card population for row-1-class sites (a NONE alternative whose core
position 0 is a two-member set): methods, verify (form, cls) pairs, consumer kinds x entry facts.

What this does NOT compute (span_pick review B5, kept): the band (no card has a noise, so the real rule keeps
the incumbent at every point: the pick printed is what it would choose once noise exists and is smaller than
the printed gap); TIE rows among qualifiers within band; KEY/M (the incumbents are READ, never recomputed);
Horspool lines (R14c: D-hors incumbents stay UNPRICED); memchr-back (no card); SIMD-form cards; the PARKED
alternative's reseed obligation at a non-first stop. T-FIND's admission of a method on a site's facts is the
kit's: the sweep mode admits every method by member count (memchr for 1, PAIR for 2, the walk for any), an
ASSUMPTION; the control admits smp20's (memchr for 1, PAIR for 2).

Constants are STAND-INS, none measured for these methods: byte(memchr) 0.06 = plan_cost.def C_MEMCHR (Zen 1);
byte(PAIR) = k x byte(memchr), k 2 = two memchr streams (ASSUMPTION, t588tri (a)); byte(walk) 1.16 =
plan_cost.def C_BITMAP (MEASURED, Zen 1; sweep mode only); hit 20 c per candidate returned (R-33's H_HIT
ASSUMPTION, not a plan_cost.def row; the walk's hit is h1); cmp 2.5 = C_VERIFY at pass 0 (cmp(form, pass)
flat); enter 20 = C_ENTER. The sweep's verify (form, cls) CLASSES (run length short <= 8 / long, set size
1/2/N) are census0's reading for S2c's cell list, not a measured vocabulary. Exact rationals, rounded half
away from zero once at the end (measure_sets §1.7).

BOUNDARIES (control) are EXACT, not swept: every price is linear in k and in hit(PAIR), so the k (and the
hit(PAIR)) at which {X,x} and the cheapest one-member stop cost the same is solved in rationals at each point
of the stated hit grid (review B1: a region quoted from a sweep must state its grid).
"""
import collections
import json
import sys
from fractions import Fraction as Q

PPM = 10**6
BM = Q(6, 100)                                       # byte(memchr), per subject byte
BW = Q(116, 100)                                     # byte(walk), sweep mode only
CMP, ENTER = Q(5, 2), Q(20)
FULL = frozenset(range(256))

# smp20's site: the six core positions of `(?i)x/1234` as byte sets (offsets 0..5)
PAT = [frozenset(b"xX"), frozenset(b"/"), frozenset(b"1"), frozenset(b"2"), frozenset(b"3"), frozenset(b"4")]
ARMS = {"default": list(range(6)), "DEF": list(range(1, 6))}
WARM = {"default": "[default]", "DEF": "[--memfn=no-window-search,no-window-skip]"}


# ---------------------------------------------------------------- the pricer (shared by both modes)

def mass(model, s):
    return Q(sum(model.get(b, 0) for b in s))


def price(model, sets, stop, k=Q(2), hit_pair=Q(20), hit_one=Q(20), method=None, others=None):
    """The note's price of the plan that stops at sets[stop] by `method` (default: by member count, 2 =
    PAIR, else memchr), verifying `others` (default: every other position), per 1e6 subject bytes.
    k = byte(PAIR) / byte(memchr); hit_pair, hit_one = hit(PAIR), hit(memchr or walk)."""
    s = sets[stop]
    method = method or ("pair" if len(s) == 2 else "memchr")
    byte, hit = {"pair": (BM * k, hit_pair), "memchr": (BM, hit_one), "walk": (BW, hit_one)}[method]
    m = mass(model, s)
    if others is None:
        others = [j for j in range(len(sets)) if j != stop]
    ms = sorted(mass(model, sets[j]) for j in others)                    # ascending mass
    ver, pr = Q(0), Q(1)
    for mo in ms:
        ver += CMP * pr
        pr *= mo / PPM
    return byte * PPM + m * (hit + ver) + m * pr * ENTER


def rnd(x):
    return int(x + Q(1, 2)) if x >= 0 else -int(-x + Q(1, 2))


# ---------------------------------------------------------------- control: smp20's site and its witness

def rates(path):
    r, on = {}, False
    for line in open(path):
        if line.startswith("#section"):
            on = line.strip() == "#section freq"
            continue
        if on and not line.startswith("#") and line.strip():
            k, _c, ppm = line.split()[:3]
            r[int(k, 16)] = int(ppm)
    return r


def incumbents(path):
    """{(arm, source): offset or None}: the stop set each compile's memchr calls search, READ from the
    `memchr on:` field of witness.sh's line (the witness's trace of today's pick)."""
    out = {}
    for line in open(path):
        for arm, tag in WARM.items():
            if not line.startswith(tag + " "):
                continue
            src = line[len(tag):].split()[0]
            stops = set(line.split("memchr on:")[1].split("RX_FINDINGS")[0].replace("'", "").split())
            hit = [i for i, s in enumerate(PAT) if set(chr(c) for c in s) == stops]
            out[(arm, src)] = hit[0] if hit else None
    return out


def name(stop):
    return "?" if stop is None else "@%d {%s}" % (stop, ",".join(chr(c) for c in sorted(PAT[stop])))


def px(model, c, **kw):
    return price(model, PAT, c, **kw)


def pick(model, arm, inc, **kw):
    """(pick, qualifiers, prices): the cheapest candidate cheaper than the incumbent, else the incumbent."""
    p = {c: px(model, c, **kw) for c in ARMS[arm]}
    q = [c for c in ARMS[arm] if c != inc and p[c] < p[inc]]
    return (min(q, key=lambda c: (p[c], c)) if q else inc), q, p


def control(args):
    cut = args.index("--") if "--" in args else len(args)
    inc = incumbents(args[0])
    P = rates(args[1])
    data = [(a.split("=", 1)[0], rates(a.split("=", 1)[1])) for a in args[cut + 1:]]
    sources = [("blind", "P", P)] + [(n, "B:" + n, d) for n, d in data]

    for hp in (Q(20), Q(40)):
        print("== prices, byte(PAIR) 0.12 (k 2), hit(PAIR) %s, hit(memchr) 20" % hp)
        for _s, mn, md in sources:
            row = [(rnd(px(md, i, hit_pair=hp)), i) for i in range(len(PAT))]
            print("%-10s %s  least %s" % (mn, "  ".join("%s %d" % (name(i), v) for v, i in row),
                                          name(min(row)[1])))
        print("-- the pick per rate source and arm (incumbent = today's compiled pick, WITNESS.out)")
        for src, mn, md in sources:
            for arm in ARMS:
                i = inc.get((arm, src))
                if i is None:
                    print("%-10s %-7s incumbent not one modelled stop (WITNESS.out); not priced" % (mn, arm))
                    continue
                c, q, p = pick(md, arm, i, hit_pair=hp)
                gap = "" if c == i else "  gap %d (%.3fx)" % (rnd(p[i] - p[c]), float(p[i] / p[c]))
                print("%-10s %-7s incumbent %s %d -> pick %s %d  qualifiers %s%s" % (
                    mn, arm, name(i), rnd(p[i]), name(c), rnd(p[c]),
                    ",".join(name(x) for x in q) or "none", gap))

    print("== blind (P), default arm: EXACT boundary of {X,x} vs P's cheapest one-member stop")
    print("   grid: hit(memchr) h1 in 5,10,20,40; hit(PAIR) = 1,2,4,8 x h1; k = byte(PAIR)/byte(memchr) solved")
    for h1 in (Q(5), Q(10), Q(20), Q(40)):
        one = min(range(1, 6), key=lambda c: (px(P, c, hit_one=h1), c))
        po = px(P, one, hit_one=h1)
        cells = []
        for mult in (1, 2, 4, 8):
            rest = px(P, 0, k=Q(0), hit_pair=h1 * mult, hit_one=h1)  # {X,x} without its byte term
            ks = (po - rest) / (BM * PPM)
            cells.append("hit(PAIR) %s: %s" % (h1 * mult, "k* %.4f" % float(ks) if ks >= 1
                                               else "departs at every k >= 1 (k* %.4f)" % float(ks)))
        m = mass(P, PAT[0])
        rest_h = px(P, 0, k=Q(2), hit_pair=Q(0), hit_one=h1)
        hs = (po - rest_h) / m
        at2 = ("departs iff hit(PAIR) > %.3f (%.3fx h1)" % (float(hs), float(hs / h1)) if hs > 0
               else "departs at every hit(PAIR)")
        print("h1 %-3s cheapest one-member %s %d; {X,x} kept for k < k*, departs above: %s; at k 2 %s"
              % (h1, name(one), rnd(po), "; ".join(cells), at2))

    print("== blind (P), DEF arm: P's cheapest one-member stop per hit(memchr) (k, hit(PAIR) do not enter)")
    print("   " + "; ".join("h1 %s: %s" % (h1, name(min(range(1, 6), key=lambda c: (px(P, c, hit_one=h1), c))))
                          for h1 in (Q(5), Q(10), Q(20), Q(40))))

    def grid_argmins(d):
        seen = {}
        for h1 in (Q(5), Q(10), Q(20), Q(40)):
            for mult in (1, 2, 4, 8):
                for kk in range(100, 1201, 5):
                    b = min(range(6), key=lambda c: (px(d, c, k=Q(kk, 100), hit_pair=h1 * mult,
                                                        hit_one=h1), c))
                    seen[b] = seen.get(b, 0) + 1
        return seen

    for n, d in data:
        print("== with data %s: B's cheapest stop over the grid (h1 5..40, hit(PAIR) 1-8 x h1, k 1.00-12.00 by 0.05)" % n)
        print("   " + "; ".join("%s at %d points" % (name(b), v) for b, v in sorted(grid_argmins(d).items())))
    # the ONE appended golden line (span_cards.md §7): P's blind argmin over the same grid
    seen = grid_argmins(P)
    print("== blind P: argmin over the grid (h1 5..40, hit(PAIR) 1-8 x h1, k 1.00-12.00 by 0.05), %d points: %s"
          % (sum(seen.values()), "; ".join("%s at %d points" % (name(b), v) for b, v in sorted(seen.items()))))


# ---------------------------------------------------------------- sweep: every window site of R-33

ENTRY = {0: "UNSTATED", 1: "NONE", 2: "PARKED", 3: "RESEED"}
METHOD_OF_ROW = {                                    # r33_sim/sim.py's table: the row -> the method it renders
    "D1": "memchr", "D1w": "memchr", "PAIR": "pair", "R7w": "walk", "fn-memchr": "memchr", "fn-pair": "pair",
    "pf_memchr": "memchr", "pf_memchr_bounded": "memchr", "pf_walk": "walk", "pf_walk_bounded": "walk",
    "D1c": "memchr-back", "pf_memchr_back": "memchr-back",
}
CORNERS = [(Q(kk), Q(h1), Q(h1 * mu)) for kk in (1, 12) for h1 in (5, 40) for mu in (1, 8)]
METHODS_BY_K = {1: ("memchr", "walk"), 2: ("pair", "walk")}


def setbits(hexs):
    b = bytes.fromhex(hexs)
    return frozenset(x for x in range(256) if b[x >> 3] >> (x & 7) & 1)


def merge(alt):
    """offset -> {set, core, yset, yes, ycore}: the AND of every covering span's set (window.c `merge`)."""
    pos = {}
    for sp in alt["spans"]:
        for j, h in enumerate(sp["sets"]):
            off = sp["start"] + j
            st = setbits(h)
            p = pos.setdefault(off, {"set": FULL, "core": False, "yset": FULL, "yes": False, "ycore": False})
            p["set"] = p["set"] & st
            incore = sp["core_lo"] <= j < sp["core_lo"] + sp["core_len"]
            p["core"] |= incore
            if sp["verify"] == 1:                    # MF_VERIFY_YES
                p["yes"] = True
                p["yset"] = p["yset"] & st
                p["ycore"] |= incore
    return pos


def alt_domain(alt):
    """(positions, readable): the candidate positions (core, not full, non-empty; a PARKED alternative
    reads only its verify-YES facts) as {off: set}, and the sets of every readable position."""
    pos = merge(alt)
    parked = alt["entry"] == 2
    sk, ck = ("yset", "ycore") if parked else ("set", "core")
    read = {o: p[sk] for o, p in pos.items() if (p["yes"] or not parked) and p[sk] != FULL and p[sk]}
    cand = {o: p[sk] for o, p in pos.items() if (p["yes"] or not parked) and p[ck] and p[sk] != FULL and p[sk]}
    return cand, read


def row1_class(alt):
    """A NONE alternative whose core position 0 (the first core offset) is a two-member set."""
    if alt["entry"] != 1:
        return False
    core = [o for o, p in merge(alt).items() if p["core"]]
    return bool(core) and len(merge(alt)[min(core)]["set"]) == 2


def today_method(site, part_ix=None):
    """(frame, method, row): TODAY's method, read from the trace (r33_sim/sim.py today_method)."""
    t = site["trace"]
    tab = collections.defaultdict(list)
    for tb, ch in t["ends"]:
        if ch not in (None, "none", "-"):
            tab[tb].append(ch)
    frame = tab["wfE"][0] if tab["wfE"] else "?"
    if part_ix is not None:
        fns = tab["fn"]
        return frame, (METHOD_OF_ROW.get(fns[part_ix], fns[part_ix]) if part_ix < len(fns) else "unobserved"), "fn"
    if "D-hors" in tab["wfD"]:
        return frame, "hors", "D-hors"
    if t["fdroute"]:
        return frame, METHOD_OF_ROW.get(t["fdroute"], t["fdroute"]), t["fdroute"]
    if frame == "E-func":
        fns = tab["fn"]
        return frame, (METHOD_OF_ROW.get(fns[0], fns[0]) if fns else "loop"), (fns[0] if fns else "-")
    return frame, ("loop" if frame == "E-find" else "generic"), "-"


def units(rec):
    for si, s in enumerate(rec["sites"]):
        deleg = s.get("deleg", "?")
        if s.get("alts"):
            _f, meth, _r = today_method(s)
            yield {"kind": deleg, "alts": s["alts"], "wr": s["wr"], "method": meth, "site": s,
                   "runcmp": [ch for tb, ch in s["trace"]["ends"] if tb == "runcmp"]}
        for line in s.get("trace", {}).get("parts", []):   # D3's NEW population branch: one unit per record
            yield {"kind": deleg + ":runpart", "alts": [], "wr": {}, "method": "-", "site": s, "runcmp": [],
                   "record": run_part_record(line)}
        pi = 0
        for p in s.get("preds", []):
            if "part" in p:
                _f, meth, _r = today_method(s, pi)
                yield {"kind": deleg + ":part", "alts": p["part"]["alts"], "wr": p["wr"], "method": meth,
                       "site": s, "runcmp": []}
                pi += 1


def desc(k, method):
    return "k%d/%s" % (k, method)


def clslen(n):
    return "short" if n <= 8 else "long"


def clsset(k):
    return "set%s" % (k if k <= 2 else "N")


def sweep(path, outpath, note=""):
    rates_all = json.load(open(path + ".rates.json"))
    models = {}
    C = collections.defaultdict(collections.Counter)         # arm -> counter
    classes = collections.defaultdict(collections.Counter)   # (arm, row1flag) -> class -> units
    pop = collections.defaultdict(collections.Counter)       # arm -> population key -> row-1 units
    nrec = 0
    for line in open(path):
        rec = json.loads(line)
        nrec += 1
        if rec.get("rc") != 0:
            continue
        arm = "DEF" if rec.get("arm") == "DEF" else "RTE"
        for u in units(rec):
            c = C[arm]
            if u["kind"].endswith(":runpart"):         # a derived run part: verify classes only (vcls fold)
                c["run part units (deleg:runpart)"] += 1
                continue
            rid = u["site"].get("rate")
            if rid not in models:
                models[rid] = dict(enumerate(rates_all[rid]["rate"]))
            model = models[rid]
            c["window units"] += 1
            r1 = any(row1_class(a) for a in u["alts"])
            c["row-1-class units"] += r1
            # candidates
            cands = []                                         # (alt, off, method, sets, others)
            for ai, alt in enumerate(u["alts"]):
                cand, read = alt_domain(alt)
                for off, s in sorted(cand.items()):
                    sets = {o: v for o, v in read.items()}
                    others = [o for o in sets if o != off]
                    for m in METHODS_BY_K.get(len(s), ("walk",)):
                        cands.append((ai, off, m, sets, others))
            wr = u["wr"]
            if wr.get("rc") != 0 or not wr.get("has_stop"):
                c["incumbent unpriced: no stop"] += 1
                continue
            im = u["method"]
            if im not in ("memchr", "pair", "walk"):
                c["incumbent unpriced: " + im] += 1
                continue
            ia, io = wr["alt"], wr["stop"]
            alt = u["alts"][ia]
            cand, read = alt_domain(alt)
            if io not in cand or cand[io] != setbits(wr["stop_set"]):
                c["incumbent unpriced: stop not a candidate position (inconsistent)"] += 1
                continue
            if (im == "memchr" and len(cand[io]) != 1) or (im == "pair" and len(cand[io]) != 2):
                c["incumbent unpriced: method/set size mismatch"] += 1
                continue
            c["incumbent priced"] += 1
            if r1:
                c["row-1-class incumbent priced"] += 1
            moved, cls_here = 0, collections.Counter()
            for kk, h1, hp in CORNERS:
                def pr(ai_, off_, m_, sets_, others_):
                    idx = sorted(sets_)
                    pos = {o: i for i, o in enumerate(idx)}
                    return price(model, [sets_[o] for o in idx], pos[off_], k=kk, hit_pair=hp, hit_one=h1,
                                 method=m_, others=[pos[o] for o in others_])
                ip = pr(ia, io, im, read, [o for o in read if o != io])
                best = None
                for (ai_, off_, m_, sets_, others_) in cands:
                    if (ai_, off_, m_) == (ia, io, im):
                        continue
                    p = pr(ai_, off_, m_, sets_, others_)
                    if p < ip and (best is None or (p, ai_, off_, m_) < best[0]):
                        best = ((p, ai_, off_, m_), sets_)
                if best:
                    moved += 1
                    _p, ai_, off_, m_ = best[0]
                    tgt = u["alts"][ai_]
                    cls_here[desc(len(alt_domain(tgt)[0][off_]), m_) + " (alt %s)" % ENTRY[tgt["entry"]]] += 1
            c["units moving at >=1 corner"] += moved > 0
            c["units moving at all %d corners" % len(CORNERS)] += moved == len(CORNERS)
            if r1:
                c["row-1-class units moving at >=1 corner"] += moved > 0
            for cl in cls_here:
                classes[(arm, r1)][desc(len(cand[io]), im) + " -> " + cl] += 1
            # output (2): the card population, row-1-class units
            if r1:
                for m_ in sorted({x[2] for x in cands if u["alts"][x[0]]["entry"] == 1}):
                    pop[arm]["method " + m_] += 1
                pop[arm]["method (incumbent) " + im] += 1
                kinds = {u["site"].get("site_kind", 0)}
                ents = sorted({ENTRY[a["entry"]] for a in u["alts"]})
                for kd in kinds:
                    for e in ents:
                        pop[arm]["enter kind=%s deleg=%s entry=%s" % (kd, u["kind"], e)] += 1
                rl = wr.get("run_len", 0) if wr.get("run_stated") else 0
                for rc in u["runcmp"]:
                    if rc not in (None, "none", "-"):
                        pop[arm]["verify rc-%s cls=%s" % (rc, clslen(rl))] += 1
                for ai_ in {x[0] for x in cands}:
                    if u["alts"][ai_]["entry"] != 1:
                        continue
                    cd, rd = alt_domain(u["alts"][ai_])
                    for off_, s in sorted(rd.items()):
                        pop[arm]["verify settest cls=%s" % clsset(len(s))] += 1
    out = []
    w = out.append
    w("== census0 (step 0, span_cards.md §7) over %s (%d records)%s; byte rates P digest a322116b1b87f9f6; corners "
      "k {1,12} x h1 {5,40} x hit(PAIR) {1x,8x h1}; BAND-0 argmin vs the incumbent read from the trace"
      % (path.split("/")[-1], nrec, " [" + note + "]" if note else ""))
    w("== (1) movers by class; units are window sites (and window-stating FUNC parts), RTE = default compile, "
      "DEF = the --memfn=no-window-search,no-window-skip recompile")
    for arm in ("RTE", "DEF"):
        for k, v in sorted(C[arm].items()):
            w("%-3s %-62s %6d" % (arm, k, v))
        for r1 in (True, False):
            for cl, v in sorted(classes[(arm, r1)].items()):
                w("%-3s mover class %s: %-72s %6d" % (arm, "ROW-1" if r1 else "other", cl, v))
    w("== (2) the card population: row-1-class units (a NONE alternative whose core position 0 is a two-member "
      "set); counts are units")
    for arm in ("RTE", "DEF"):
        for k, v in sorted(pop[arm].items()):
            w("%-3s %-72s %6d" % (arm, k, v))
    text = "\n".join(out) + "\n"
    if outpath:
        open(outpath, "w").write(text)
    else:
        sys.stdout.write(text)


# ---------------------------------------------------------------- forecast: the measured cards (S2f)
# `forecast SWEEP.jsonl --measures SET.tsv [--swept-at COMMIT] [-o census0_cards.out]` prices the same window sites
# with a measurement set's CARDS in place of the stand-ins, and folds in vcls's verify classes (r9-SLOT-9).
# The cards are read from the set's `#section rows` (the file `measure_store/<id>/<rev>/set.tsv`, the form
# `pcrec --measures=FILE` reads; DEFAULTS `idk` names it), unit `walkbytes` (the scalar walk's per-byte cost = 1):
#   byte(m)   kit.find_byte.{libc,pair,walk}        value / 1e6 per subject byte (memchr = libc)
#   hit(m)    kit.find_hit.<form>.random.<one|alt>.<gap>   per candidate returned; RANDOM landing (the floor's
#             rows), the gap (hit density) 256 and 1024 each a POINT; PAIR reads `alt` (x and X alternate), the
#             others `one`
#   cmp       kit.verify_cmp.settest.<c1|c2|cn>.{p0,p50}  cmp(p) = p0 + (p50 - p0) x min(p, 1-p) / 0.5
#   enter     kit.enter.<site_kind>.NONE                 per pass; only NONE-entry alternatives are priced
# The price is linear in the cards, so the band of a comparison is the quadrature sum of (coef_a - coef_b) x noise
# (span_pick.md "The band of a comparison"); a mover BEYOND BAND departs by more than Z_BAND x that band
# (Z_BAND 3.0, UNMEASURED DEFAULT, span_cards §6). Not priced (counted as such): a unit whose incumbent or a
# candidate is not a NONE alternative, a method with no card (walk-back), a site kind with no enter card, a unit
# whose incumbent is not memchr/pair/walk. Run-compare rows (rc-*) are not priced: verify is per position, as
# in the stand-in sweep. A fused-compare bound row (value 0) is a LOWER BOUND on its cost.
Z_BAND = Q(3)
CARD_GAPS = (256, 1024)
BYTE_CARD = {"memchr": "kit.find_byte.libc", "pair": "kit.find_byte.pair", "walk": "kit.find_byte.walk"}
HIT_CARD = {"memchr": "kit.find_hit.libc.random.one.%d", "pair": "kit.find_hit.pair.random.alt.%d",
            "walk": "kit.find_hit.walk.random.one.%d"}


def load_cards(path):
    """(header dict, {key: (value, noise)}) in walkbytes (value_e6 / 1e6) from a set file's header and rows sections"""
    hdr, cards, sec = {}, {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("#section"):
            sec = line.split()[1]
        elif not line or line.startswith("#"):
            continue
        elif sec == "header":
            k, _, v = line.partition("\t")
            hdr[k] = v
        elif sec == "rows":
            f = line.split("\t")
            cards[f[0]] = (Q(int(f[2]), 10**6), Q(int(f[4]), 10**6))
    return hdr, cards


def class_measure(form, arg):
    """HOUSE-16's class measure of a verify form's class, read off the text's boundaries (vcls.py's, folded here):
    settest -> the COMPARE count of the member set `arg` (a list of byte values): one per singleton or edge-touching
    range, two per inner range; None for the full set. rc-words -> the word count of a run of length `arg`."""
    if form == "rc-words":
        w = 8 if arg >= 8 else 4 if arg >= 4 else 2
        return -(-arg // w)
    if len(arg) == 256:
        return None
    rg = []
    for x in sorted(arg):
        if rg and x == rg[-1][1] + 1:
            rg[-1][1] = x
        else:
            rg.append([x, x])
    return sum(1 if (lo == hi or lo == 0 or hi == 255) else 2 for lo, hi in rg), rg


def settest_cls(ms):
    """the set test's class by its COMPARE count (R-38 Part D, part_d.md §5.1 D3 [r1pd F20]): c1, c2, cn = 3 to 7
    compares (the measured `\\w` instance's range), cn+ above 7, UNMEASURED: never priced by cn's 7-compare row.
    vcls.py holds the SAME bounds (two copies, changed in one commit; census0_cards.out's data lines equal vcls.out's)"""
    r = class_measure("settest", ms)
    if r is None:
        return None
    return "c1" if r[0] == 1 else "c2" if r[0] == 2 else "cn" if r[0] <= 7 else "cn+"


# ---------------------------------------------------------------- the derived run part's record (R-38 Part D D3)
# The kit's trace build prints ONE `MFTRACE run_part_terms` record per derived run part, on the define path
# (window.c run_part_terms; part_d.md §5.1 D3):
#   MFTRACE run_part_terms art=A site=S part=I hint=H terms=OFF:KIND:VAL,...
# KIND RUN (VAL its run_len) or SET (VAL the 32-byte set in hex); `hint` the RUN term's index, `-` scan-less.
# THE ONE PARSER of the record: census0's population branch (`deleg:runpart`), vcls_lines' verify classes,
# vcls.py, and G2's check of the record (memfn/tests/g2/run_part_census.py) all read it here.
def run_part_record(line):
    """one record line -> {"art", "site", "part", "hint" (None scan-less), "terms": [(off, "RUN", run_len) |
    (off, "SET", members)]}; None for any other line"""
    f = line.split()
    if len(f) < 3 or f[0] != "MFTRACE" or f[1] != "run_part_terms":
        return None
    kv = dict(x.split("=", 1) for x in f[2:] if "=" in x)
    terms = []
    for t in kv.get("terms", "").split(","):
        if not t:
            continue
        off, kind, val = t.split(":", 2)
        terms.append((int(off), kind, int(val) if kind == "RUN" else sorted(setbits(val))))
    return {"art": int(kv["art"]), "site": int(kv["site"]), "part": int(kv["part"]),
            "hint": None if kv.get("hint") == "-" else int(kv["hint"]), "terms": terms}


def spelled(ms):
    """a position the kit's RUN term can spell (T, K): one member, or two members one bit apart (a cube)"""
    return len(ms) == 1 or (len(ms) == 2 and bin(ms[0] ^ ms[1]).count("1") == 1)


def run_part_classes(rec, runcmp=None):
    """the record's verify (form, cls) pairs: every multi-member SET term (settest, settest_cls), the RUN term
    (rc-<row>, its class; `runcmp` the run compare's chosen row, the term unclassed where none is read), a
    scan-less part (every-pos, -)"""
    out = []
    for off, kind, val in rec["terms"]:
        if kind == "SET" and len(val) > 1:
            c = settest_cls(val)
            if c:
                out.append(("settest", c))
        elif kind == "RUN" and runcmp not in (None, "none", "-"):
            out.append(("rc-" + runcmp, rc_cls(runcmp, val)))
    if rec["hint"] is None:
        out.append(("every-pos", "-"))
    return out


def run_part_unspelled(rec):
    """the record's SET terms whose set the kit's RUN term cannot spell (G2's check's census quantity)"""
    return sum(1 for off, kind, val in rec["terms"] if kind == "SET" and not spelled(val))


def settest_shape(ms):
    """the lowering shape of a TWO-compare set test: `alu1` (a single-bit pair, an inner range, or [^x]) or `cmp2`"""
    r = class_measure("settest", ms)
    if r is None or r[0] != 2:
        return None
    rg = r[1]
    if len(rg) == 2 and rg[0][0] == 0 and rg[1][1] == 255 and rg[1][0] == rg[0][1] + 2:
        return "alu1"
    if len(rg) == 2 and all(lo == hi for lo, hi in rg):
        return "alu1" if bin(rg[0][0] ^ rg[1][0]).count("1") == 1 else "cmp2"
    return "alu1" if len(rg) == 1 else "cmp2"


def rc_cls(row, L):
    if row == "words":
        return "w%d" % class_measure("rc-words", L)
    if row == "memcmp":
        return "l1" if L in (1, 2, 4, 8) else "lv" if L >= 16 else "lc"
    return "o2" if row == "overlap" else "b%d" % L


def plan_run_len(wr):
    best, cur, prev = 0, 0, None
    for off, term in wr.get("plan", []):
        cur = cur + 1 if prev and term == prev[1] and off == prev[0] + 1 else 1
        prev = (off, term)
        best = max(best, cur)
    return best


def runpart_pop(s):
    """a site's derived run parts' verify (form, cls) pairs, from its `run_part_terms` records (collect.py keeps
    them raw in `trace.parts`); the run compare's row is the site's first chosen `runcmp` row"""
    rc = next((ch for tb, ch in s.get("trace", {}).get("ends", []) if tb == "runcmp" and ch not in (None, "none", "-")),
              None)
    for line in s.get("trace", {}).get("parts", []):
        yield from run_part_classes(run_part_record(line), rc)


def vcls_lines(path, swept_at):
    """vcls.py's census folded in: verify (form, cls) counts per arm over every row-1-class window SITE, the
    c2 lowering shapes, stamped with the sweep's sha-256 and commit (r9-SLOT-9). The data lines are vcls.out's,
    byte for byte (the job compares)."""
    import hashlib
    pop, shp = collections.Counter(), collections.Counter()
    for line in open(path):
        rec = json.loads(line)
        for s in rec.get("sites", []):
            for k in runpart_pop(s):
                pop[(rec["arm"],) + k] += 1
            alts = s.get("alts")
            if not alts or not any(row1_class(a) for a in alts):
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
                        ms = sorted(setbits(h))
                        c = settest_cls(ms)
                        if c:
                            pop[(rec["arm"], "settest", c)] += 1
                        if c == "c2":
                            shp[(rec["arm"], "settest", "c2." + settest_shape(ms))] += 1
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    out = ["== (3) vcls fold over %s (sha256 %s, swept at %s): verify (form, cls) by the T-CMP / set-test text's "
           "boundaries; counts are SITES (lines below are vcls.out's data lines)" % (path.split("/")[-1], sha, swept_at)]
    for tab in (pop, shp):
        for (arm, form, cls), n in sorted(tab.items()):
            out.append("%s\t%s\t%s\t%s\t%d" % (arm, "verify" if tab is pop else "shape", form, cls, n))
    return out


def mcoefs(cards, model, sets, stop, method, kind, gap, others):
    """(coefficients {card key: coef}, missing key or None): the plan's price as a linear form in the cards, per
    1e6 subject bytes; the verify term as in `price` with cmp(p) interpolated between the card's two pass rates"""
    co = collections.defaultdict(Q)
    bkey, hkey = BYTE_CARD[method], HIT_CARD[method] % gap
    m = mass(model, sets[stop])
    co[bkey] += PPM
    co[hkey] += m
    pr = Q(1)
    for mo, j in sorted((mass(model, sets[j]), j) for j in others):
        cl = settest_cls(sorted(sets[j]))
        p = mo / PPM
        w = min(p, 1 - p) / Q(1, 2)
        co["kit.verify_cmp.settest.%s.p0" % cl] += m * pr * (1 - w)
        co["kit.verify_cmp.settest.%s.p50" % cl] += m * pr * w
        pr *= p
    co["kit.enter.%d.NONE" % kind] += m * pr
    miss = next((k for k in co if k not in cards), None)
    return co, miss


def mprice(co, cards):
    return sum(c * cards[k][0] for k, c in co.items())


def mgap(ca, cb, cards):
    """(price a - price b, band^2): the band of the comparison, quadrature over the cards (exact squares)"""
    keys = set(ca) | set(cb)
    return (sum((ca.get(k, 0) - cb.get(k, 0)) * cards[k][0] for k in keys),
            sum(((ca.get(k, 0) - cb.get(k, 0)) * cards[k][1]) ** 2 for k in keys))


def forecast(path, setpath, outpath, swept_at):
    hdr, cards = load_cards(setpath)
    rates_all = json.load(open(path + ".rates.json"))
    models = {}
    C = collections.defaultdict(collections.Counter)         # (arm, gap) -> counter
    classes = collections.defaultdict(collections.Counter)   # (arm, gap, r1) -> class -> units [BAND-0]
    beyond = collections.defaultdict(collections.Counter)    # (arm, gap, r1) -> class -> units beyond band
    smp20 = None
    nrec = 0
    for line in open(path):
        rec = json.loads(line)
        nrec += 1
        if rec.get("rc") != 0:
            continue
        arm = "DEF" if rec.get("arm") == "DEF" else "RTE"
        for u in units(rec):
            if u["kind"].endswith(":runpart"):         # a derived run part: verify classes only (vcls fold)
                for gap in CARD_GAPS:
                    C[(arm, gap)]["run part units (deleg:runpart)"] += 1
                continue
            rid = u["site"].get("rate")
            if rid not in models:
                models[rid] = dict(enumerate(rates_all[rid]["rate"]))
            model = models[rid]
            kind = u["site"].get("site_kind", 0)
            r1 = any(row1_class(a) for a in u["alts"])
            wr, im = u["wr"], u["method"]
            why = None
            if wr.get("rc") != 0 or not wr.get("has_stop"):
                why = "no stop"
            elif im not in ("memchr", "pair", "walk"):
                why = "incumbent method " + im
            elif ("kit.enter.%d.NONE" % kind) not in cards:
                why = "no enter card for site kind %d" % kind
            if why is None:
                ia, io = wr["alt"], wr["stop"]
                alt = u["alts"][ia]
                cand, read = alt_domain(alt)
                if alt["entry"] != 1:
                    why = "incumbent alternative entry %s (no enter card)" % ENTRY[alt["entry"]]
                elif io not in cand or cand[io] != setbits(wr["stop_set"]) or \
                        (im == "memchr" and len(cand[io]) != 1) or (im == "pair" and len(cand[io]) != 2):
                    why = "incumbent not a consistent candidate"
            for gap in CARD_GAPS:
                c = C[(arm, gap)]
                c["window units"] += 1
                c["row-1-class units"] += r1
                if why:
                    c["unpriced: " + why] += 1
                    continue
                cands = []
                for ai, a in enumerate(u["alts"]):
                    if a["entry"] != 1:
                        continue
                    cd, rd = alt_domain(a)
                    for off, s in sorted(cd.items()):
                        for m_ in METHODS_BY_K.get(len(s), ("walk",)):
                            cands.append((ai, off, m_, rd))
                ico, miss = mcoefs(cards, model, read, io, im, kind, gap, [o for o in read if o != io])
                if miss:
                    c["unpriced: no card " + miss] += 1
                    continue
                ip = mprice(ico, cards)
                best = None
                for ai, off, m_, rd in cands:
                    if (ai, off, m_) == (ia, io, im):
                        continue
                    co, miss = mcoefs(cards, model, rd, off, m_, kind, gap, [o for o in rd if o != off])
                    if miss:
                        c["candidate unpriced: no card " + miss] += 1
                        continue
                    p = mprice(co, cards)
                    if p < ip and (best is None or (p, ai, off, m_) < best[0]):
                        best = ((p, ai, off, m_), co, rd)
                c["priced"] += 1
                c["row-1-class priced"] += r1
                if not best:
                    continue
                (p, ai, off, m_), co, rd = best
                cl = "%s -> %s" % (desc(len(cand[io]), im), desc(len(alt_domain(u["alts"][ai])[0][off]), m_))
                d, b2 = mgap(ico, co, cards)
                c["movers (BAND-0)"] += 1
                c["row-1-class movers (BAND-0)"] += r1
                classes[(arm, gap, r1)][cl] += 1
                if d * d > Z_BAND ** 2 * b2:
                    c["movers beyond band (z 3)"] += 1
                    c["row-1-class movers beyond band (z 3)"] += r1
                    beyond[(arm, gap, r1)][cl] += 1
            if smp20 is None and rec.get("src") == "s588" and rec.get("id") == "smp20" and arm == "RTE" and u["alts"]:
                smp20 = (u, model, kind)
    out = []
    w = out.append
    w("== census0 forecast (S2f, span_cards.md §7, §9) over %s (%d records), the cards of %s@%s (values_digest %s, "
      "method %s, tier %s, box %s)" % (path.split("/")[-1], nrec, hdr.get("id"), hdr.get("rev"), hdr.get("values_digest"),
                                       hdr.get("method"), hdr.get("tier"), hdr.get("box")))
    w("== cards read from the set's rows (unit walkbytes): " + "; ".join(
        "%s %s" % (k, "%.6f" % float(cards[k][0])) for k in sorted(BYTE_CARD.values())))
    w("== k measured = byte(pair)/byte(memchr) = %.4f; points: hit gap %s, random landing (PAIR: alt split)"
      % (float(cards[BYTE_CARD["pair"]][0] / cards[BYTE_CARD["memchr"]][0]), ",".join(map(str, CARD_GAPS))))
    w("== a mover is the BAND-0 argmin cheaper than the incumbent at the point; BEYOND BAND = cheaper by more than "
      "z 3.0 (UNMEASURED DEFAULT) x the quadrature band of the card noises; units are window sites as in census0.out")
    for line in vcls_lines(path, swept_at):
        w(line)
    w("== (4) movers at the measured card point; RTE = default compile, DEF = the no-window-search,no-window-skip "
      "recompile")
    for arm in ("RTE", "DEF"):
        for gap in CARD_GAPS:
            for k, v in sorted(C[(arm, gap)].items()):
                w("%-3s gap %-4d %-72s %6d" % (arm, gap, k, v))
    w("== (5) row 1's forecast mover list: ROW-1 class units (a NONE alternative whose core position 0 is a "
      "two-member set), by class and arm; 'other' = every other unit")
    for arm in ("RTE", "DEF"):
        for gap in CARD_GAPS:
            for r1 in (True, False):
                for cl, v in sorted(classes[(arm, gap, r1)].items()):
                    w("%-3s gap %-4d mover class %s: %-44s BAND-0 %6d  beyond band %6d" % (
                        arm, gap, "ROW-1" if r1 else "other", cl, v, beyond[(arm, gap, r1)][cl]))
    w("== (6) the watched witness: smp20 `(?i)x/1234`, blind (P), default arm; is the measured card point above or "
      "below k*?")
    u, model, kind = smp20
    alt = u["alts"][0]
    cand, read = alt_domain(alt)
    sets = [read[o] for o in sorted(read)]
    stops = sorted(read)
    pos = {o: i for i, o in enumerate(stops)}
    BP, BL = cards[BYTE_CARD["pair"]][0], cards[BYTE_CARD["memchr"]][0]
    # control of the reading: the stand-in k* at h1 20, hit(PAIR) 1x h1 from THIS sweep's P model (span_pick: 2.146)
    one = min(range(1, 6), key=lambda c: (price(model, PAT, c, hit_one=Q(20)), c))
    ks = (price(model, PAT, one, hit_one=Q(20)) - price(model, PAT, 0, k=Q(0), hit_pair=Q(20))) / (BM * PPM)
    w("   stand-in k* at h1 20, hit(PAIR) 1x h1 (this sweep's P model, %s; span_pick.md: 2.146): %.4f"
      % (u["site"].get("rate"), float(ks)))
    for gap in CARD_GAPS:
        pr_ = {}
        for o in stops:
            m_ = "pair" if len(read[o]) == 2 else "memchr" if len(read[o]) == 1 else "walk"
            co, miss = mcoefs(cards, model, [read[x] for x in stops], pos[o], m_, kind, gap,
                              [pos[x] for x in stops if x != o])
            pr_[o] = (co, miss, m_)
        if any(v[1] for v in pr_.values()):
            w("   gap %d: a card is missing: %s" % (gap, sorted({v[1] for v in pr_.values() if v[1]})))
            continue
        pp = {o: mprice(v[0], cards) for o, v in pr_.items()}
        names = {o: name(o) if o < 6 else "@%d" % o for o in stops}
        w("   gap %d: prices (walkbytes per 1e6 bytes, enter kind %d): %s" % (gap, kind, "  ".join(
            "%s %s %.0f" % (names[o], pr_[o][2], float(pp[o])) for o in stops)))
        ones = [o for o in stops if len(read[o]) == 1]
        o1 = min(ones, key=lambda o: (pp[o], o))
        co0 = pr_[stops[0]][0]
        rest = pp[stops[0]] - co0[BYTE_CARD["pair"]] * BP
        kstar = (pp[o1] - rest) / (co0[BYTE_CARD["pair"]] * BL)    # byte coef is PPM for both
        kmeas = BP / BL
        d, b2 = mgap(co0, pr_[o1][0], cards)
        w("   gap %d: cheapest one-member stop %s %.0f; {X,x} PAIR %.0f; k* %.4f; k measured %.4f; "
          "the measured card point is %s k*; {X,x} minus %s = %+.0f, band (1 sigma) %.0f, %s"
          % (gap, names[o1], float(pp[o1]), float(pp[stops[0]]), float(kstar), float(kmeas),
             "ABOVE" if kmeas > kstar else "BELOW", names[o1], float(d), float(b2) ** 0.5,
             "beyond band (z 3)" if d * d > Z_BAND ** 2 * b2 else "within band (z 3)"))
    text = "\n".join(out) + "\n"
    if outpath:
        open(outpath, "w").write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "control":
        control(sys.argv[2:])
    elif len(sys.argv) > 2 and sys.argv[1] == "sweep":
        a = sys.argv[2:]
        sweep(a[0], a[a.index("-o") + 1] if "-o" in a else None, a[a.index("--note") + 1] if "--note" in a else "")
    elif len(sys.argv) > 2 and sys.argv[1] == "forecast":
        a = sys.argv[2:]
        forecast(a[0], a[a.index("--measures") + 1], a[a.index("-o") + 1] if "-o" in a else None,
                 a[a.index("--swept-at") + 1] if "--swept-at" in a else "?")
    else:
        sys.exit(__doc__)
