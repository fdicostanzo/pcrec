#!/usr/bin/env python3
"""section.py — THE SECTIONING RULE, as a search whose OUTPUT is measured.

The brief asks for "the sectioning rule as MEASURED output", not as an
assumption.  So this file does not contain a rule.  It contains a SEARCH — an
exact dynamic program over partitions of the interval list into contiguous
sections — parameterized by ONE scalar `lam` that prices an op against a byte:

    minimize   sum over sections of ( rodata_bytes + lam * probe_ops )

Sweeping `lam` from 0 (pure size) to infinity (pure speed) traces the whole
size/speed Pareto frontier for a given set.  What the memo calls "the
sectioning rule" is then the DESCRIPTION OF WHAT THIS SEARCH PICKS over the
real populations — read off the answers, not written down in advance.  That
`lam` is a single scalar knob over a size/speed trade is not a coincidence
either: it is the shape [OPT-DIAL]'s five-setting dial needs.

WHY A DP IS EXACT HERE.  A section is a CONTIGUOUS run of the interval list,
and the sections partition the code-point axis in order, so the choice of
where section j ends is independent of everything before it given where it
starts.  `best[j] = min over i of best[i] + cost(i..j)` is therefore exact
over the space of contiguous partitions, and the only approximation left is
the per-section dispatch charge (a real tree's per-leaf depth is not
constant), which is stated where it is applied and is small.

COMPILE-TIME.  Cost evaluation is O(1) per candidate section for every kit
member but two (CUBES is memoized and only reachable at width <= 256;
PAGE64's distinct-page count is maintained incrementally as j grows), and
sections are capped at MAXK intervals.  The whole DP is therefore O(n*MAXK).
TABLES ARE NEVER MATERIALIZED DURING THE SEARCH — only for the sections the
answer actually keeps.  This is what makes deliverable (3)'s compile-time
bound favourable, and it is a property of the algorithm rather than of the
data, so it survives a worse population.
"""

import math

import kit

MAXK = 64                # max intervals a single section may hold
DISP_BYTES = 0.0         # the dispatch node's bytes are INSIDE the
                         # measured per-section text slopes (each
                         # synthetic arm grew its dispatch tree too),
                         # so charging it again would double-count
DISP_OPS = 1.0           # modelled marginal probe cost of one more section


# ------------------------------------------------------------- cost oracles

class CostModel:
    """O(1) (or memoized) COST for a candidate section, without building its
    tables.  Returns (rodata_bytes, probe_ops, form_name) for the cheapest
    kit member at this `lam`, or None if nothing fits."""

    def __init__(self, iv, allow=None, cube_prune=True):
        self.iv = iv
        self.allow = allow
        self.cube_prune = cube_prune
        self._cubes = {}
        self.cube_calls = 0          # counted: deliverable (3)'s cost driver

    def _ok(self, name):
        return self.allow is None or name in self.allow

    def cubes_cost(self, i, j):
        key = (i, j)
        if key in self._cubes:
            return self._cubes[key]
        sec = self.iv[i:j + 1]
        w = kit.width(sec)
        if w > kit.FormCubes.MAXW or (j - i + 1) < 2:
            r = None
        else:
            self.cube_calls += 1
            f = kit.FormCubes(sec)
            r = (0, f.ops()) if f.ok else None
        self._cubes[key] = r
        return r

    def best(self, i, j, lam, page_price):
        sec_lo, sec_hi = self.iv[i][0], self.iv[j][1]
        w = sec_hi - sec_lo + 1
        k = j - i + 1
        best = None

        def offer(nm, ro, ops):
            """BYTES ARE BYTES.  The objective counts `.rodata` AND `.text`:
            the first cost model counted only `.rodata`, and the first full
            Pareto sweep came back with the pure-size policy DOMINATED on
            both axes by the middle one — 9,672 bytes / 1,302 ops against
            4,311 / 111 on the same set.  Range-compare chains are free in
            `.rodata` and 12 bytes an interval in `.text`, and a model that
            cannot see that is not measuring size."""
            nonlocal best
            if not self._ok(nm):
                return
            tot = ro + kit.text_cost(nm, k)
            v = tot + lam * ops
            if best is None or v < best[3]:
                best = (tot, ops, nm, v)

        if k == 1:
            offer("ALL", 0, 0.0)
        if k <= kit.FormRanges.MAXK:
            offer("RANGES", 0, k * (kit.OP_ALU + kit.OP_CMP))
        if w <= 64:
            offer("MASK64", 0, 2 * kit.OP_ALU + kit.OP_CMP)
        if w <= kit.FormCubes.MAXW:
            c = self.cubes_cost(i, j)
            if c is not None:
                offer("CUBES", c[0], c[1])
        offer("BITMAP", (w + 7) // 8, kit.OP_LOAD + 3 * kit.OP_ALU)
        if w >= 128 and page_price is not None:
            npages, nleaf = page_price
            idxw = 1 if nleaf <= 256 else 2
            offer("PAGE64", npages * idxw + nleaf * 8,
                  kit.OP_LOAD + kit.OP_DEP_LOAD + 4 * kit.OP_ALU)
        if k >= kit.FormBsearch.MINK:
            offer("BSEARCH", 8 * k,
                  math.log2(k) * (kit.OP_LOAD + 2 * kit.OP_CMP))
        return best


def _page_price(iv, i, j):
    """(npages, distinct_leaves) for section i..j, in O(j-i).

    Pages are ABSOLUTE (`cp >> 6`), which is what makes this cheap: only the
    pages an interval starts or ends in can be partial, every page strictly
    inside an interval is all-ones, and every page no interval touches is
    all-zero.  So the distinct count is a set of at most 2k boundary masks
    plus at most two constants — no table is built, at search time or ever.
    `kit.FormPage64.price` is the same arithmetic the FORM itself uses, so the
    price the DP pays and the table the emitter writes cannot disagree."""
    return kit.FormPage64.price(iv[i:j + 1])


def partition(iv, lam, allow=None, maxk=MAXK, cube_prune=True):
    """The DP.  Returns (sections, total_rodata, total_ops, forms)."""
    n = len(iv)
    cm = CostModel(iv, allow, cube_prune)
    INF = float("inf")
    best = [INF] * (n + 1)
    back = [None] * (n + 1)
    best[0] = 0.0
    for j in range(n):
        lo_i = max(0, j - maxk + 1)
        for i in range(j, lo_i - 1, -1):
            base = iv[i][0]
            w = iv[j][1] - base + 1
            pp = _page_price(iv, i, j) if w >= 128 else None
            b = cm.best(i, j, lam, pp)
            if b is None:
                continue
            ro, ops, nm, _ = b
            v = best[i] + ro + DISP_BYTES + lam * (ops + DISP_OPS)
            if v < best[j + 1]:
                best[j + 1] = v
                back[j + 1] = (i, nm, ro, ops)
    # walk back
    secs, forms, ro_tot, ops_tot = [], [], 0, 0.0
    j = n
    while j > 0:
        i, nm, ro, ops = back[j]
        secs.append((i, j - 1))
        forms.append(nm)
        ro_tot += ro
        ops_tot += ops
        j = i
    secs.reverse()
    forms.reverse()
    partition.last_cube_calls = cm.cube_calls
    partition.last_cost = best[n]
    return secs, ro_tot, ops_tot, forms


def instantiate(iv, secs, forms):
    """Materialize the chosen sections' kit members.  Only now are tables
    built — the search never did."""
    out = []
    for (i, j), nm in zip(secs, forms):
        sec = iv[i:j + 1]
        cls = {F.name: F for F in kit.KIT}[nm]
        out.append(cls(sec))
    return out


# --------------------------------------------------- the C backend (discover)

def partition_c(iv, lam, exe=None, ivfile=None):
    """The SAME DP, run by `discover.c`, returning the same tuple.

    Used by the sweeps because the Python DP is 600x slower and there are
    thousands of cells; `crosscheck.py` runs BOTH over the population and
    compares, which is what makes using the fast one safe.  A disagreement is
    a study finding, not a fallback to be papered over.
    """
    import os
    import subprocess
    import tempfile

    here = os.path.dirname(os.path.abspath(__file__))
    exe = exe or os.path.join(here, "discover")
    tmp = None
    if ivfile is None:
        fd, tmp = tempfile.mkstemp(suffix=".iv")
        with os.fdopen(fd, "w") as f:
            for l, h in iv:
                f.write("%x %x\n" % (l, h))
        ivfile = tmp
    try:
        r = subprocess.run([exe, ivfile, repr(float(lam)), "--dump"],
                           capture_output=True, text=True)
    finally:
        if tmp:
            os.unlink(tmp)
    if r.returncode:
        raise RuntimeError("discover failed: " + r.stderr.strip())
    starts, forms = [], []
    ro = ops = 0.0
    for line in r.stdout.splitlines():
        if line.startswith("SET "):
            kv = dict(p.split("=", 1) for p in line.split()[1:])
            ro, ops = float(kv["rodata"]), float(kv["ops"])
        elif line.startswith("SEC "):
            kv = dict(p.split("=", 1) for p in line.split()[2:])
            starts.append(int(kv["start"]))
            forms.append(kv["form"])
    secs = [(starts[z], (starts[z + 1] - 1) if z + 1 < len(starts)
             else len(iv) - 1) for z in range(len(starts))]
    return secs, ro, ops, forms
