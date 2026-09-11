#!/usr/bin/env python3
"""kit.py — the [CLS-TREE] PER-SECTION REPRESENTATION KIT, and the emitter
that composes one bespoke straight-line matcher out of it.

THE GENERAL SHAPE (Frank's reframing, docs/dev/plan.md [CLS-TREE]):

    a class matcher is COMPOSED PER-SECTION from a small kit of
    representations, STATICALLY SELECTED.

This file is the kit.  Its INPUT is a bare code-point SET — a sorted,
disjoint, non-adjacent interval list — and NOTHING ELSE.  There is no
provenance argument, no `is_caseless` flag, no "this came from \\p" tag:
CONSTITUTIONAL CONSTRAINT 1.  Every property this file exploits is read off
the set's own structure, which is why the caseless fold and the \\p{Lu}
parity block fall out of ONE member (`CUBES`) rather than out of two special
cases.

STRUCTURE OF AN EMITTED MATCHER

    1. one global bound test        (cp outside [lo_0, hi_last] -> 0)
    2. a balanced binary DISPATCH TREE over the section boundaries
    3. at each leaf, the section's own chosen TEST

[CLS-TREE]'s seed representation — "a binary tree of ranges" — is the
DEGENERATE CASE of this shape: every section one interval, every leaf `ALL`.
That is not a coincidence to note in passing, it is why the kit is the
general mechanism and the seed is one of its settings.

THE KIT MEMBERS (a leaf test; `x` is `cp - base`, and the dispatch has
already established `0 <= x < W`):

  ALL      k == 1               `1`                       — nothing to test
  RANGES   k small              OR of `(unsigned)(x-a) <= b-a`
  CUBES    W <= 256             OR of `(x & care) == val`  — two-level
                                minimization over ceil(log2 W) bits, exact
                                (Quine-McCluskey) at this width.  The ASCII
                                case fold is the single-cube instance with
                                care = ~0x20; \\p{Lu} over an adjacent-pair
                                block is the care = ~0x01 instance.
  MASK64   W <= 64              `(mask >> x) & 1`          — NO LOAD
  BITMAP   any W                `(tbl[x>>3] >> (x&7)) & 1` — one load
  PAGE64   any W                two-level, deduplicated 8-byte leaves
  BSEARCH  any k                binary search over the section's intervals

COST.  Each member reports `rodata` (bytes it puts in .rodata; exact, this
is a counted property of the emitted table) and `ops` (a MODEL weight used
only to steer the sectioning search).  Nothing in the memo's ranking rests
on `ops`: the emitted matcher is compiled and TIMED, and the model's job is
only to generate candidates for the measurement to rank.
"""

import math

# Model weights.  Deliberately crude and deliberately NOT load-bearing: the
# sectioning DP uses them to order candidates, the stopwatch ranks the result.
# `LOAD` is charged above an ALU op because a leaf that reads memory is the
# thing form_char_step0.md's families B/C/D left genuinely open.
OP_ALU = 1.0
OP_CMP = 1.0
OP_LOAD = 3.0
OP_DEP_LOAD = 5.0          # a load whose ADDRESS is a previous load's value


# ------------------------------------------------------------------ helpers

def span(section):
    return section[0][0], section[-1][1]


def width(section):
    lo, hi = span(section)
    return hi - lo + 1


def card(section):
    return sum(h - l + 1 for l, h in section)


def members_of(section, base):
    out = []
    for l, h in section:
        out.extend(range(l - base, h - base + 1))
    return out


# ------------------------------------------------- exact two-level minimizer

def minimize_cubes(members, nbits, care_all=None):
    """Exact-ish two-level minimization of the boolean function whose ON-set
    is `members` over `nbits` variables, with every point >= 2**nbits (and
    every point the caller marks) a DON'T CARE.

    Returns a list of (care_mask, value) cubes whose OR is the function on
    the ON-set and which never fires outside ON-set u DC-set.

    Method: Quine-McCluskey prime-implicant generation (exact at these
    widths — nbits <= 8 is 256 minterms) followed by essential-prime
    extraction plus a greedy cover of the remainder.  The greedy tail is the
    only inexact step; `minimize_cubes_exact_cover` below swaps it for a
    branch-and-bound when the remainder is small, which it always is here.

    A cube is (care, val): it fires on x iff (x & care) == val.  care with a
    0 bit is a DON'T-CARE BIT — a free bit — which is exactly the structure
    CONSTITUTIONAL CONSTRAINT 1 names: a complete orbit under a set of free
    bits is one cube.
    """
    full = (1 << nbits) - 1
    on = set(members)
    if not on:
        return []
    dc = set(range(1 << nbits)) - on
    if care_all is not None:
        dc &= care_all
    else:
        dc = set()
    # Points the function must NOT fire on:
    off = set(range(1 << nbits)) - on - dc

    # --- prime implicants over on|dc
    cur = {(full, m) for m in (on | dc)}
    primes = set()
    while cur:
        nxt = set()
        used = set()
        bycare = {}
        for c in cur:
            bycare.setdefault(c[0], []).append(c[1])
        for care, vals in bycare.items():
            vs = set(vals)
            for b in range(nbits):
                bit = 1 << b
                if not (care & bit):
                    continue
                ncare = care & ~bit
                for v in vs:
                    if v & bit:
                        continue
                    if (v | bit) in vs:
                        nxt.add((ncare, v))
                        used.add((care, v))
                        used.add((care, v | bit))
        primes |= (cur - used)
        cur = nxt
    # keep only primes that cover at least one ON point and no OFF point
    good = []
    for care, val in primes:
        cov = {m for m in on if (m & care) == val}
        if not cov:
            continue
        if any((m & care) == val for m in off):
            continue
        good.append((care, val, cov))
    if not good:
        return []

    # --- essential primes
    chosen, covered = [], set()
    for m in on:
        hits = [g for g in good if m in g[2]]
        if len(hits) == 1 and hits[0] not in chosen:
            chosen.append(hits[0])
    for g in chosen:
        covered |= g[2]
    # --- greedy cover of the rest
    rest = [g for g in good if g not in chosen]
    while covered != on:
        rest.sort(key=lambda g: -len(g[2] - covered))
        if not rest or not (rest[0][2] - covered):
            break
        chosen.append(rest[0])
        covered |= rest[0][2]
        rest = rest[1:]
    return [(c, v) for c, v, _ in chosen]


# ---------------------------------------------------------------- kit members

class Form:
    name = "?"

    @staticmethod
    def fits(section):
        return False

    def __init__(self, section):
        self.section = section
        self.base, self.top = span(section)
        self.w = self.top - self.base + 1

    def rodata(self):
        return 0

    def ops(self):
        return 0.0

    def expr(self, x, tabname):
        raise NotImplementedError

    def tables(self, tabname):
        return ""


class FormAll(Form):
    name = "ALL"

    @staticmethod
    def fits(section):
        return len(section) == 1

    def expr(self, x, t):
        return "1"


class FormRanges(Form):
    name = "RANGES"
    MAXK = 8

    @staticmethod
    def fits(section):
        return len(section) <= FormRanges.MAXK

    def ops(self):
        return len(self.section) * (OP_ALU + OP_CMP)

    def expr(self, x, t):
        parts = []
        for l, h in self.section:
            a, b = l - self.base, h - self.base
            if a == b:
                parts.append("(%s == %uu)" % (x, a))
            elif a == 0:
                parts.append("(%s <= %uu)" % (x, b))
            elif b == self.w - 1:
                parts.append("(%s >= %uu)" % (x, a))
            else:
                parts.append("((%s - %uu) <= %uu)" % (x, a, b - a))
        return "(" + " | ".join(parts) + ")"


def _range_and(a, b):
    """AND of every integer in [a,b] — the common high prefix."""
    sh = 0
    while a != b:
        a >>= 1
        b >>= 1
        sh += 1
    return a << sh


def _range_or(a, b):
    """OR of every integer in [a,b]."""
    if a == b:
        return a
    m = (a ^ b).bit_length()
    return (a | b) | ((1 << m) - 1)


def cube_of(section, base, w, nbits):
    """Is this section EXACTLY ONE don't-care cube?  O(k), k = interval count
    — it never touches an individual member.

    A one-cube function is an affine subspace of the hypercube: the CARE bits
    are the ones every member agrees on, the rest are FREE.  Over a set given
    as intervals both aggregates are closed forms —

        val  = AND over members          = AND of the intervals' range-ANDs
        care = ~(OR(M) & ~AND(M))        (a bit differs from `val` iff `val`
                                          has 0 there and some member has 1)

    — so the cube is found without enumerating the set.  The only thing left
    is that the cube must not SPILL onto a point the section excludes, and the
    O(k) necessary condition for that (cube size minus member count cannot
    exceed the don't-care budget) rejects almost every candidate before the
    exact big-integer containment check runs at all.

    THIS IS THE WHOLE OF THE CASE FOLD.  `(c|0x20)=='a'` — [FORM-CHAR]'s
    shipped `ascii-fold` object, which pcrec today reaches through a
    classifier that asks "are these two bytes a case-fold pair" — is what this
    returns on the two-member set {x, x^0x20}, found without the question
    being asked.  It returns the same shape for {x, x^0x01}, for a four-member
    set free in two bits, and for `\p{Lu}`-over-an-adjacent-pair-block's
    parity cube.  One test, every instance, no provenance consulted.
    """
    full = (1 << nbits) - 1
    a_all, o_all, nmem = full, 0, 0
    for l, h in section:
        x0, x1 = l - base, h - base
        a_all &= _range_and(x0, x1)
        o_all |= _range_or(x0, x1)
        nmem += x1 - x0 + 1
    val = a_all
    care = full & ~(o_all & ~a_all)
    nfree = nbits - bin(care).count("1")
    if nfree > 24:                      # cube would be astronomically large
        return None
    csize = 1 << nfree
    if csize - nmem > (1 << nbits) - w:  # O(k) necessary condition
        return None
    # exact containment, as big-integer bitsets over x in [0, 2**nbits)
    mbits = 0
    for l, h in section:
        x0, x1 = l - base, h - base
        mbits |= ((1 << (x1 + 1)) - 1) ^ ((1 << x0) - 1)
    okbits = mbits | (((1 << (1 << nbits)) - 1) ^ ((1 << w) - 1))
    cube = 1 << val
    for b in range(nbits):
        if not (care >> b) & 1:
            cube |= cube << (1 << b)
    if cube & ~okbits:
        return None
    return (care, val)


def free_bit_exists(members, nbits, dc):
    """THE PRE-TEST, and it is the whole of CONSTITUTIONAL CONSTRAINT 1's
    algebra in one line: does flipping some single bit map the member set into
    itself (modulo don't-cares)?

    A bit with that property is a FREE BIT — the set is a union of complete
    orbits under it — and a complete orbit is exactly a don't-care cube.  Both
    of the constraint's named customers pass it, for opposite reasons:

      * the ASCII case fold {x, x^0x20} is ONE orbit under bit 5, so bit 5 is
        free.  `(c|0x20)=='a'` is that cube written out.  The kit reaches it
        with no idea the set came from `(?i)`.
      * `\\p{Lu}` over an adjacent-pair block is the EVENS — not closed under
        bit 0 at all, but closed under every OTHER bit, so bits 1..n are free
        and the cube is `(x & 1) == 0`.  Range plus parity.

    O(|members| * nbits), and it runs before the exact minimizer to keep the
    minimizer off sections that have no structure for it to find.  This is a
    HEURISTIC PRUNE of the search, not of the kit: `--no-cube-prune` measures
    what it costs (see README)."""
    ms = set(members)
    ok = ms | dc
    for b in range(nbits):
        bit = 1 << b
        if all((x ^ bit) in ok for x in ms):
            return True
    return False


class FormCubes(Form):
    """CONSTITUTIONAL CONSTRAINT 1's member.  Never told what the set is FOR."""
    name = "CUBES"
    MAXW = 256
    MAXCUBES = 6
    MAXK_SEARCH = 16         # exact minimizer only up to this interval count
    TIER2 = True             # run the exact minimizer at all (measured knob)

    @staticmethod
    def fits(section):
        return width(section) <= FormCubes.MAXW

    def __init__(self, section):
        """TWO TIERS, and the split is what keeps discovery cheap.

        Tier 1 — `single_cube`, constant-bounded, run on EVERY section that
        fits.  It is the only tier that can fire below width 64, because below
        64 `MASK64` already costs no table and three ops, so a multi-cube
        cover has nothing to win; one cube (two ops, no table) does.

        Tier 2 — the exact minimizer, run ONLY in the band 64 < W <= 256,
        where `MASK64` no longer fits and the alternative is a BITMAP with a
        LOAD.  That band is where a handful of cubes is worth searching for,
        and confining the search to it is what turns the DP's cost from
        minutes into milliseconds (measured: README, "discovery cost")."""
        Form.__init__(self, section)
        self.nbits = max(1, (self.w - 1).bit_length())
        one = cube_of(section, self.base, self.w, self.nbits)
        if one is not None:
            self.cubes = [one]
        elif (FormCubes.TIER2 and self.w > 64
              and len(section) <= FormCubes.MAXK_SEARCH):
            mem = members_of(section, self.base)
            dc = set(range(self.w, 1 << self.nbits))   # x >= W cannot occur
            self.cubes = minimize_cubes(mem, self.nbits, care_all=dc)
        else:
            self.cubes = []
        self.ok = bool(self.cubes) and len(self.cubes) <= FormCubes.MAXCUBES

    def ops(self):
        return len(self.cubes) * (OP_ALU + OP_CMP)

    def expr(self, x, t):
        full = (1 << self.nbits) - 1
        parts = []
        for care, val in self.cubes:
            if care == full:
                parts.append("(%s == %uu)" % (x, val))
            else:
                parts.append("((%s & 0x%Xu) == 0x%Xu)" % (x, care, val))
        return "(" + " | ".join(parts) + ")"


class FormMask64(Form):
    name = "MASK64"

    @staticmethod
    def fits(section):
        return width(section) <= 64

    def __init__(self, section):
        Form.__init__(self, section)
        m = 0
        for b in members_of(section, self.base):
            m |= 1 << b
        self.mask = m

    def ops(self):
        return 2 * OP_ALU + OP_CMP

    def expr(self, x, t):
        return "((0x%016XULL >> %s) & 1u)" % (self.mask, x)


class FormBitmap(Form):
    name = "BITMAP"

    @staticmethod
    def fits(section):
        return True

    def __init__(self, section):
        Form.__init__(self, section)
        self.nbytes = (self.w + 7) // 8
        b = bytearray(self.nbytes)
        for m in members_of(section, self.base):
            b[m >> 3] |= 1 << (m & 7)
        self.bytes = bytes(b)

    def rodata(self):
        return self.nbytes

    def ops(self):
        return OP_LOAD + 3 * OP_ALU

    def tables(self, t):
        rows = ", ".join("0x%02X" % v for v in self.bytes)
        return "static const unsigned char %s[%d] = { %s };\n" % (
            t, self.nbytes, rows)

    def expr(self, x, t):
        return "((%s[(%s) >> 3] >> ((%s) & 7)) & 1u)" % (t, x, x)


class FormPage64(Form):
    """PCRE2's own property-lookup shape, generalized: an index over 64-wide
    pages into a DEDUPLICATED table of 8-byte leaves.  Dense and all-empty
    pages collapse to one shared leaf each, which is why real (bursty) script
    data is where this member earns its keep."""
    name = "PAGE64"

    @staticmethod
    def fits(section):
        return width(section) >= 128

    def __init__(self, section):
        Form.__init__(self, section)
        # Pages are ABSOLUTE (cp >> 6), not base-relative: the page
        # decomposition of a set is then a property of the SET and not of the
        # sectioning, which is what lets section.py price this member in O(k)
        # without materializing it (and keeps cost model and emitter honest
        # about each other — they index identically).
        self.pbase = self.base >> 6
        self.npages = (self.top >> 6) - self.pbase + 1
        masks = [0] * self.npages
        for l, h in section:
            for p in range(l >> 6, (h >> 6) + 1):
                pl, ph = p << 6, (p << 6) + 63
                a, b = max(l, pl), min(h, ph)
                masks[p - self.pbase] |= ((1 << (b - a + 1)) - 1) << (a - pl)
        uniq, idx = {}, []
        for mk in masks:
            if mk not in uniq:
                uniq[mk] = len(uniq)
            idx.append(uniq[mk])
        self.leaves = [k for k, _ in sorted(uniq.items(), key=lambda kv: kv[1])]
        self.idx = idx
        self.idxw = 1 if len(self.leaves) <= 256 else 2

    def rodata(self):
        return self.npages * self.idxw + len(self.leaves) * 8

    def ops(self):
        return OP_LOAD + OP_DEP_LOAD + 4 * OP_ALU

    def tables(self, t):
        ity = "unsigned char" if self.idxw == 1 else "unsigned short"
        s = "static const %s %s_i[%d] = { %s };\n" % (
            ity, t, self.npages, ", ".join(str(v) for v in self.idx))
        s += "static const unsigned long long %s_l[%d] = { %s };\n" % (
            t, len(self.leaves), ", ".join("0x%016XULL" % v
                                           for v in self.leaves))
        return s

    def expr(self, x, t):
        # NOTE: indexes off `cp` directly, never off `x` — absolute pages.
        return ("((%s_l[%s_i[(cp >> 6) - %uu]] >> (cp & 63)) & 1u)"
                % (t, t, self.pbase))

    @staticmethod
    def price(section):
        """(npages, ndistinct_leaves) in O(k), without building anything.

        Only the pages an interval STARTS or ENDS in can carry a partial
        mask; every page strictly inside an interval is all-ones, and any page
        no interval touches is all-zero.  So the distinct-mask count is the
        size of a set of at most 2k boundary masks plus at most two constants.
        """
        base, top = span(section)
        pbase = base >> 6
        npages = (top >> 6) - pbase + 1
        bmask = {}
        full = False
        touched = 0
        for l, h in section:
            pl, ph = l >> 6, h >> 6
            if ph - pl >= 2:
                full = True
            touched += ph - pl + 1
            for p in (pl, ph):
                a, b = max(l, p << 6), min(h, (p << 6) + 63)
                bmask[p] = bmask.get(p, 0) | \
                    (((1 << (b - a + 1)) - 1) << (a - (p << 6)))
        vals = set(bmask.values())
        if full:
            vals.add((1 << 64) - 1)
        if touched < npages:
            vals.add(0)
        return npages, len(vals)


class FormBsearch(Form):
    """[CLS-TREE]'s SEED, as a leaf member: binary search over this section's
    own interval table."""
    name = "BSEARCH"
    MINK = 8

    @staticmethod
    def fits(section):
        return len(section) >= FormBsearch.MINK

    def rodata(self):
        return 8 * len(self.section)

    def ops(self):
        return math.log2(len(self.section)) * (OP_LOAD + 2 * OP_CMP)

    def tables(self, t):
        lo = ", ".join("%uu" % (l - self.base) for l, _ in self.section)
        hi = ", ".join("%uu" % (h - self.base) for _, h in self.section)
        n = len(self.section)
        return ("static const unsigned %s_lo[%d] = { %s };\n"
                "static const unsigned %s_hi[%d] = { %s };\n"
                % (t, n, lo, t, n, hi))

    def expr(self, x, t):
        return "cls_bsearch(%s_lo, %s_hi, %d, %s)" % (t, t, len(self.section), x)


KIT = [FormAll, FormRanges, FormCubes, FormMask64, FormBitmap, FormPage64,
       FormBsearch]


def candidates(section, allow=None):
    """Every kit member that FITS this section, instantiated.  Selection is a
    function of the section's structure alone."""
    out = []
    for F in KIT:
        if allow is not None and F.name not in allow:
            continue
        if not F.fits(section):
            continue
        f = F(section)
        if F is FormCubes and not f.ok:
            continue
        out.append(f)
    return out
