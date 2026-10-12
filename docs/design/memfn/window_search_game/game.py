#!/usr/bin/env python3
"""game.py -- the KIT POLICIES and the COUNTING simulator (lane wingame).

Every policy reads ONLY D161's inputs -- the span list (classes, move-back,
overshoot) and the frequency table -- plus, where a policy needs something the
contract does not carry, an EXPLICIT parameter named in its signature
(`consumer`, `form_price`). Nothing here reads a clock: every consequence is a
COUNT over the subject's bytes.

THE FORM. A window search the kit could build is
    (span, anchors, verify)
anchors = 1 or 2 positions inside the span the scan tests (a memchr / class
scan / packed pair), verify = the whole span tested at each stop. A STOP is a
subject position where every anchor class holds; a SURVIVOR a stop where the
whole span holds. Each survivor hands the consumer a WINDOW
    [span_start - move_back, span_start + len)
and up to overshoot + 1 possible match beginnings inside it.

THE COUNTS (per form, per subject):
    stops       positions the scan stops at (kit work beyond the scan)
    surv        stops that pass the span verify (consumer invocations)
    win_bytes   sum over survivors of move_back + len (bytes a forward DFA
                re-steps from the window beginning to confirm the span)
    win_union   the same windows' union (a consumer that never re-steps)
    starts      sum over survivors of overshoot + 1 (anchored attempts a
                backtracker would make)
"""
import numpy as np

import spans as SP


# ---- the frequency table (D161 input 2) ----------------------------------
def load_prior(path):
    """tests/findings/default_ppm.tsv: `byte<TAB>ppm`, 256 rows."""
    p = np.zeros(256)
    for ln in open(path):
        b, v = ln.split()
        p[int(b)] = int(v)
    return p / p.sum()


def prior_from_subject(buf):
    c = np.bincount(np.frombuffer(buf, np.uint8), minlength=256).astype(float)
    return (c + 0.5) / (c.sum() + 128.0)


def pc(prior, m):
    return float(sum(prior[b] for b in SP.bytes_of(m)))


# ---- candidate forms ------------------------------------------------------
class Form:
    __slots__ = ("si", "anchors", "classes", "mb", "ov", "kind", "est_stop", "est_surv")

    def __init__(self, si, anchors, classes, mb, ov, kind, prior):
        self.si, self.anchors, self.classes = si, anchors, classes
        self.mb, self.ov, self.kind = mb, ov, kind
        self.est_stop = 1.0
        for a in anchors:
            self.est_stop *= pc(prior, classes[a])
        self.est_surv = 1.0
        for c in classes:
            self.est_surv *= pc(prior, c)

    @property
    def L(self):
        return len(self.classes)

    def desc(self):
        cl = "".join(SP.fmt_class(c) for c in self.classes)
        return "%s#%d{%s}@a=%s,mb=%s,ov=%s" % (self.kind, self.si, cl,
                                               ",".join(map(str, self.anchors)),
                                               self.mb, self.ov)


def bounded_spans(sp):
    return [(i, s) for i, s in enumerate(sp) if s["move_back"] is not None]


def forms_of(sp, prior, pairs=True):
    """Every single-anchor and (optionally) two-anchor form over every
    BOUNDED span. Unbounded spans are not expressible under D161."""
    out = []
    for i, s in bounded_spans(sp):
        cl = s["classes"]
        for a in range(len(cl)):
            if SP.popc(cl[a]) == 256:
                continue
            out.append(Form(i, [a], cl, s["move_back"], s["overshoot"], "one", prior))
        if pairs and len(cl) >= 2:
            idx = sorted((pc(prior, cl[a]), a) for a in range(len(cl))
                         if SP.popc(cl[a]) < 256)[:6]
            for x in range(len(idx)):
                for y in range(x + 1, len(idx)):
                    a, b = sorted((idx[x][1], idx[y][1]))
                    out.append(Form(i, [a, b], cl, s["move_back"], s["overshoot"], "pair", prior))
    return out


# ---- form prices: the KIT's own knowledge (not a contract input) -----------
def scan_price(f):
    """Per-subject-byte scan cost in units of ONE DFA TRANSITION STEP,
    kit-internal and UNMEASURED (D149 label). Order of magnitude only: the
    bench's floor-byte row puts a memchr-class pass near 0.017 ns/B while a
    table-driven DFA step costs tens of times that, so memchr of one byte
    0.03, of <= 3 bytes (memchr2/3) 0.06, a larger class (a table loop, close
    to a DFA step) 0.7, a pair +0.03 over its dearer anchor's form."""
    def one(m):
        n = SP.popc(m)
        return 0.03 if n == 1 else (0.06 if n <= 3 else 0.7)
    if len(f.anchors) == 1:
        return one(f.classes[f.anchors[0]])
    return max(one(f.classes[a]) for a in f.anchors) + 0.03


VERIFY_PER_STOP = 10.0       # UNMEASURED: per-stop span verify + scan re-entry


# ---- consumers: what the contract does NOT carry ---------------------------
CONSUMERS = {
    # name: (per-candidate fixed cost, per-window-byte cost, per-start cost)
    "none": (0.0, 0.0, 0.0),          # D161 as written: no consumer price
    "dfa": (20.0, 1.0, 0.0),          # forward DFA from the window beginning
    "vm": (40.0, 0.0, 60.0),          # anchored attempt per possible start
    # all in units of one DFA transition step; UNMEASURED (D149), chosen only
    # to have the right SHAPE (bytes against starts) and order of magnitude
}


def consumer_cost(f, consumer):
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return c_cand + c_byte * (f.mb + f.L) + c_start * (f.ov + 1)


def expected_cost(f, consumer):
    """Expected cost per subject byte under the prior's independence model."""
    if isinstance(f, Plan):
        return plan_cost(f, consumer)
    return scan_price(f) + f.est_stop * VERIFY_PER_STOP + f.est_surv * consumer_cost(f, consumer)


# ---- the policies ---------------------------------------------------------
def _argmin(forms, key):
    best = None
    for f in forms:
        k = key(f)
        if best is None or k < best[0]:
            best = (k, f)
    return best[1] if best else None


def pol_rare_pos(sp, prior):
    """P1: the single rarest POSITION anywhere; verify its span."""
    return _argmin([f for f in forms_of(sp, prior, False)],
                   lambda f: (f.est_stop, f.mb, -f.L))


def pol_rare_span(sp, prior):
    """P2: the span with the smallest joint (independence) rate; scan its
    rarest position."""
    fs = forms_of(sp, prior, False)
    return _argmin(fs, lambda f: (f.est_surv, f.est_stop, f.mb))


def pol_pair(sp, prior):
    """P3: the two rarest positions of one span at their fixed distance
    (packed pair); falls back to P1 on one-position spans."""
    fs = forms_of(sp, prior, True)
    return _argmin(fs, lambda f: (f.est_stop, f.est_surv, f.mb))


SELF_DECLINE = 0.25   # UNMEASURED (D149): P4 declines a form stopping on >25% of bytes


def pol_selfprice(sp, prior):
    """P4: the kit prices its own forms (scan + verify) and nothing
    downstream -- the most a kit can do with D161's inputs alone. Its
    decline is a kit-own constant, because "is the search worth it" needs
    the cost of NOT searching, which is the consumer's."""
    fs = forms_of(sp, prior, True)
    f = _argmin(fs, lambda f: (expected_cost(f, "none"), f.mb))
    if f is not None and f.est_stop > SELF_DECLINE:
        return "decline"
    return f


def baseline_cost(consumer):
    """Per-byte cost of NO window search: the consumer meets every byte
    (a DFA steps it; a VM attempts a start there)."""
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return c_byte + c_start


def pol_window(consumer):
    """P5(consumer): P4 plus the downstream price of each survivor, which
    needs `consumer` -- a fact D161 does not carry -- and a decline against
    the consumer's own no-search cost, which needs it too."""
    def p(sp, prior):
        fs = forms_of(sp, prior, True)
        f = _argmin(fs, lambda f: (expected_cost(f, consumer), f.mb))
        if f is not None and expected_cost(f, consumer) >= baseline_cost(consumer) + 1.0:
            return "decline"
        return f
    p.__name__ = "pol_window_" + consumer
    return p


# ---- [wingame2] P6 `refine`: scan a RARE span B, locate span A locally -----
# Frank's policy (2026-10-11, "minimize overshoot"): span A is the best window
# (smallest overshoot) but has no rare target; span B has one. Scan for B; at
# each B hit bound where A must lie from the two spans' (move-back, overshoot)
# and run a LOCAL class search for A over that bounded region; A's hit fixes
# the window with A's own small overshoot. Where the gap is unbounded the
# fallback is a forward search for A's class (a plain Form over A).
#
# THE ONE FACT P6 NEEDS BEYOND D161's inputs is the per-span LENGTH (already a
# span's classes) -- nothing else: with omin = move_back - overshoot, the
# relative distance of two spans, A before B, is
#       start(B) - start(A)  in  [omin_B - omin_A,  move_back_B - move_back_A]
# and its uncertainty is overshoot_B - overshoot_A. (The LOOSE bound a reader
# would write treating both spans as independent against the match start has
# uncertainty overshoot_A + overshoot_B.) Both are computed; `loose` is the
# sensitivity row.
LOCAL_FLOOR = 0.0   # no UNMEASURED constant is added by P6 itself: it reuses
                    # scan_price (per tested start, one class test), VERIFY_PER_STOP
                    # and CONSUMERS.


def omin_of(s):
    return s["move_back"] - s["overshoot"]


def region_of(sa, sb, loose=False):
    """Interval [dlo, dhi] of start(A) - start(B), from move-back/overshoot
    and the span lengths only; None when not derivable (a span unbounded, or
    the spans' order cannot be fixed)."""
    if sa["move_back"] is None or sb["move_back"] is None:
        return None
    amin, bmin = omin_of(sa), omin_of(sb)
    if loose:
        return (amin - sb["move_back"], sa["move_back"] - bmin)
    la, lb = len(sa["classes"]), len(sb["classes"])
    if bmin >= amin + la:                      # A before B
        return (sa["move_back"] - sb["move_back"], amin - bmin)
    if amin >= bmin + lb:                      # B before A
        return (amin - bmin, sa["move_back"] - sb["move_back"])
    return None


class Plan:
    """Scan form fB for span B; at each B survivor search A's class over the
    bounded region [dlo, dhi] (relative to B's start)."""
    def __init__(self, ia, ib, sa, sb, fA, fB, reg, loose):
        self.ia, self.ib, self.sa, self.sb, self.fA, self.fB = ia, ib, sa, sb, fA, fB
        self.dlo, self.dhi = reg
        self.loose = loose
        self.est_stop, self.est_surv = fB.est_stop, fB.est_surv
        self.kind = "local-loose" if loose else "local"

    @property
    def width(self):
        return self.dhi - self.dlo

    def desc(self):
        return "%s:A#%d{%s}mb=%d,ov=%d<-B#%d{%s}@a=%s,d=[%d,%d]" % (
            self.kind, self.ia, "".join(SP.fmt_class(c) for c in self.sa["classes"]),
            self.fA.mb, self.fA.ov, self.ib,
            "".join(SP.fmt_class(c) for c in self.sb["classes"]),
            ",".join(map(str, self.fB.anchors)), self.dlo, self.dhi)


def local_price(fA):
    """Per tested start of A: one class test of A's rarest position (the
    same scan_price table), then the verify only on its hits."""
    return scan_price(fA)


def a_form(sa, ia, prior):
    cl = sa["classes"]
    cand = [(pc(prior, cl[k]), k) for k in range(len(cl)) if SP.popc(cl[k]) < 256]
    if not cand:
        return None
    k = min(cand)[1]
    return Form(ia, [k], cl, sa["move_back"], sa["overshoot"], "one", prior)


def plans_of(sp, prior, loose=False):
    """Every (A, B) plan over ordered pairs of BOUNDED spans with a derivable
    region. B's scan form is its best form by (stop rate, survivor rate)."""
    out = []
    for ia, sa in bounded_spans(sp):
        fA = a_form(sa, ia, prior)
        if fA is None:
            continue
        for ib, sb in bounded_spans(sp):
            if ib == ia:
                continue
            reg = region_of(sa, sb, loose)
            if reg is None:
                continue
            fbs = [f for f in forms_of([sb], prior, True)]
            if not fbs:
                continue
            fB = min(fbs, key=lambda f: (f.est_stop, f.est_surv))
            fB.si = ib
            out.append(Plan(ia, ib, sa, sb, fA, fB, reg, loose))
    return out


def plan_cost(p, consumer):
    """Expected cost per subject byte, same independence model as P5."""
    w = p.width
    hits = (w + 1) * p.fA.est_surv
    return (scan_price(p.fB) + p.fB.est_stop * VERIFY_PER_STOP
            + p.fB.est_surv * ((w + 1) * local_price(p.fA)
                               + hits * consumer_cost(p.fA, consumer)))


def pol_refine(consumer):
    """P6(consumer): P5's candidates plus every local plan; same decline
    rule. The fallback for an unbounded gap is P5's own form over A (a
    forward search for A's class), which is already among the candidates."""
    def p(sp, prior):
        cands = list(forms_of(sp, prior, True)) + plans_of(sp, prior)
        f = _argmin(cands, lambda f: (expected_cost(f, consumer),
                                      0 if isinstance(f, Form) else 1))
        if f is not None and expected_cost(f, consumer) >= baseline_cost(consumer) + 1.0:
            return "decline"
        return f
    p.__name__ = "pol_refine_" + consumer
    return p


def refine_pair(sp, prior):
    """Frank's setting, structurally: A = the bounded span with the smallest
    (overshoot, move-back); B = the other span whose rarest position is
    rarest, required rarer than A's. -> (ia, ib) or None."""
    b = bounded_spans(sp)
    if not b or len(sp) < 2:
        return None
    ia = min(b, key=lambda t: (t[1]["overshoot"], t[1]["move_back"], -len(t[1]["classes"])))[0]

    def rate(s):
        return min(pc(prior, c) for c in s["classes"])
    others = [(rate(s), i) for i, s in enumerate(sp) if i != ia]
    if not others:
        return None
    rb, ib = min(others)
    if rb >= rate(sp[ia]):
        return None
    return ia, ib


def rare_pos(s, prior):
    """(rate, index) of a span's rarest single position."""
    return min((pc(prior, c), k) for k, c in enumerate(s["classes"]))


def best_form_of(sp, i, prior, consumer):
    """Best Form over one bounded span by the consumer-priced expected cost
    (no decline): the forward search for that span's class."""
    fs = [f for f in forms_of(sp, prior, True) if f.si == i]
    return _argmin(fs, lambda f: (expected_cost(f, consumer), f.mb)) if fs else None


POLICIES = [
    ("P1-rare-pos", pol_rare_pos),
    ("P2-rare-span", pol_rare_span),
    ("P3-pair", pol_pair),
    ("P4-selfprice", pol_selfprice),
    ("P5-dfa", pol_window("dfa")),
    ("P5-vm", pol_window("vm")),
    ("P6-dfa", pol_refine("dfa")),
    ("P6-vm", pol_refine("vm")),
]


# ---- the simulator ----------------------------------------------------------
def lut(m):
    a = np.zeros(256, bool)
    a[SP.bytes_of(m)] = True
    return a


def simulate(f, S):
    """COUNTS for form f over subject S (np.uint8 array)."""
    n = len(S)
    L = f.L
    if n < L:
        return dict(stops=0, surv=0, win_bytes=0, win_union=0, starts=0)
    m = n - L + 1
    pos = [lut(c)[S][k:k + m] for k, c in enumerate(f.classes)]
    stop = np.ones(m, bool)
    for a in f.anchors:
        stop &= pos[a]
    surv = stop.copy()
    for k in range(L):
        if k not in f.anchors:
            surv &= pos[k]
    idx = np.nonzero(surv)[0]
    lo = np.maximum(idx - f.mb, 0)
    hi = idx + L
    wb = int((hi - lo).sum())
    # union of [lo, hi)
    un = 0
    end = -1
    for a, b in zip(lo.tolist(), hi.tolist()):
        if b <= end:
            continue
        un += b - max(a, end)
        end = b
    return dict(stops=int(stop.sum()), surv=int(len(idx)), win_bytes=wb,
                win_union=un, starts=int(len(idx)) * (f.ov + 1))


def work(c, f, consumer, n):
    """The P5 objective's own unit applied to MEASURED counts (not rates)."""
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return (scan_price(f) * n + VERIFY_PER_STOP * c["stops"]
            + c["surv"] * c_cand + c_byte * c["win_bytes"] + c_start * c["starts"])


# ---- [wingame2] simulating a Plan, and the presence gate --------------------
def _masks(f, S):
    """(stop, surv) boolean arrays over start positions for form f."""
    n, L = len(S), f.L
    m = n - L + 1
    pos = [lut(c)[S][k:k + m] for k, c in enumerate(f.classes)]
    stop = np.ones(m, bool)
    for a in f.anchors:
        stop &= pos[a]
    surv = stop.copy()
    for k in range(L):
        if k not in f.anchors:
            surv &= pos[k]
    return stop, surv


def _window_counts(idx, mb, L, ov):
    lo = np.maximum(idx - mb, 0)
    hi = idx + L
    un, end = 0, -1
    for a, b in zip(lo.tolist(), hi.tolist()):
        if b <= end:
            continue
        un += b - max(a, end)
        end = b
    return dict(surv=int(len(idx)), win_bytes=int((hi - lo).sum()), win_union=un,
                starts=int(len(idx)) * (ov + 1))


def simulate_plan(p, S):
    """COUNTS for Plan p over subject S. stops = B stops; bsurv = B
    survivors (each opens one local search); local_pos = start positions
    tested; pairs = (B survivor, A hit) pairs; surv = DISTINCT A hits (the
    consumer's windows; the kit hands each A window over once)."""
    n = len(S)
    LA, LB = p.fA.L, p.fB.L
    if n < max(LA, LB):
        return dict(stops=0, bsurv=0, local_pos=0, pairs=0, surv=0, win_bytes=0,
                    win_union=0, starts=0)
    bst, bsv = _masks(p.fB, S)
    _, asv = _masks(Form(0, [0], p.fA.classes, 0, 0, "one", np.ones(256) / 256), S)
    mA = len(asv)
    idxB = np.nonzero(bsv)[0]
    lo = np.clip(idxB + p.dlo, 0, mA)
    hi = np.clip(idxB + p.dhi + 1, 0, mA)
    ok = hi > lo
    lo, hi = lo[ok], hi[ok]
    cs = np.concatenate(([0], np.cumsum(asv)))
    pairs = int((cs[hi] - cs[lo]).sum())
    diff = np.zeros(mA + 1, np.int64)
    np.add.at(diff, lo, 1)
    np.add.at(diff, hi, -1)
    covered = np.cumsum(diff[:mA]) > 0
    idxA = np.nonzero(asv & covered)[0]
    c = _window_counts(idxA, p.fA.mb, LA, p.fA.ov)
    c.update(stops=int(bst.sum()), bsurv=int(len(idxB)), local_pos=int((hi - lo).sum()),
             pairs=pairs)
    # MERGED hand-over: one window per B survivor that has an A hit, from the
    # first hit's window beginning to the last hit's end (counted per B
    # survivor; overlapping windows of neighbouring survivors are not merged)
    allA = np.nonzero(asv)[0]
    a0 = np.searchsorted(allA, lo, side="left")
    a1 = np.searchsorted(allA, hi, side="left")
    has = a1 > a0
    first, last = allA[a0[has]], allA[a1[has] - 1]
    c.update(mcand=int(has.sum()),
             mbytes=int((last + LA - np.maximum(first - p.fA.mb, 0)).sum()),
             mstarts=int((a1 - a0)[has].sum()) * (p.fA.ov + 1))
    return c


def simulate_any(f, S):
    if isinstance(f, Plan):
        return simulate_plan(f, S)
    return simulate(f, S)


def work_any(c, f, consumer, n):
    if isinstance(f, Plan):
        c_cand, c_byte, c_start = CONSUMERS[consumer]
        return (scan_price(f.fB) * n + VERIFY_PER_STOP * c["stops"]
                + local_price(f.fA) * c["local_pos"] + c["surv"] * c_cand
                + c_byte * c["win_bytes"] + c_start * c["starts"])
    return work(c, f, consumer, n)


def work_merge(c, p, consumer, n):
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return (scan_price(p.fB) * n + VERIFY_PER_STOP * c["stops"]
            + local_price(p.fA) * c["local_pos"] + c["mcand"] * c_cand
            + c_byte * c["mbytes"] + c_start * c["mstarts"])


def simulate_gate(f, S, gmask, goff):
    """Forward search for form f's span, with a PRESENCE GATE: a candidate
    start s is dropped (and the scan ends) when no byte of class gmask lies
    at or after s + goff. Returns counts plus `scan_n` (the bytes the forward
    scan covers) and `gate_n` (bytes the gate's own scan covers, <= n)."""
    n = len(S)
    L = f.L
    g = np.nonzero(lut(gmask)[S])[0]
    last = int(g[-1]) if len(g) else -1
    stop, surv = _masks(f, S)
    m = len(stop)
    cut = max(0, min(m, last - goff + 1))
    stop_g, surv_g = stop[:cut], surv[:cut]
    idx = np.nonzero(surv_g)[0]
    c = _window_counts(idx, f.mb, L, f.ov)
    c.update(stops=int(stop_g.sum()), scan_n=min(n, cut + L - 1 if cut else 0), gate_n=n,
             last=last)
    return c


def work_gate(c, f, consumer, gprice):
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return (gprice * c["gate_n"] + scan_price(f) * c["scan_n"] + VERIFY_PER_STOP * c["stops"]
            + c["surv"] * c_cand + c_byte * c["win_bytes"] + c_start * c["starts"])
