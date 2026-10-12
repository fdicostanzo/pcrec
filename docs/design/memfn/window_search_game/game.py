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
    """Per-subject-byte scan cost, kit-internal and UNMEASURED (D149 label):
    memchr of one byte 1, a class of <=3 bytes 1.5 (memchr2/3), a larger
    class 4 (table loop), a pair +0.5 over its dearer anchor's form."""
    def one(m):
        n = SP.popc(m)
        return 1.0 if n == 1 else (1.5 if n <= 3 else 4.0)
    if len(f.anchors) == 1:
        return one(f.classes[f.anchors[0]])
    return max(one(f.classes[a]) for a in f.anchors) + 0.5


VERIFY_PER_STOP = 2.0        # UNMEASURED: per-stop span verify + re-entry


# ---- consumers: what the contract does NOT carry ---------------------------
CONSUMERS = {
    # name: (per-candidate fixed cost, per-window-byte cost, per-start cost)
    "none": (0.0, 0.0, 0.0),          # D161 as written: no consumer price
    "dfa": (20.0, 1.0, 0.0),          # forward DFA from the window beginning
    "vm": (40.0, 0.0, 60.0),          # anchored attempt per possible start
}


def consumer_cost(f, consumer):
    c_cand, c_byte, c_start = CONSUMERS[consumer]
    return c_cand + c_byte * (f.mb + f.L) + c_start * (f.ov + 1)


def expected_cost(f, consumer):
    """Expected cost per subject byte under the prior's independence model."""
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


POLICIES = [
    ("P1-rare-pos", pol_rare_pos),
    ("P2-rare-span", pol_rare_span),
    ("P3-pair", pol_pair),
    ("P4-selfprice", pol_selfprice),
    ("P5-dfa", pol_window("dfa")),
    ("P5-vm", pol_window("vm")),
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
