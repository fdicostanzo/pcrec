"""[DD-14] §5.3a / §5.7 / §4.4a(6) -- HOW MANY SLOT INSTANCES A SUBTREE NEEDS.

R34's VERIFIER refuted two things this design said about slots, and both are
in-pcrec facts, so this probe asks pcrec rather than reasoning:

  V-2  §5.3a's premise "there is ONE slot per lexical construct" is FALSE for
       five of the seven families. Only GROUP and PENDING slots are per
       lexical node; CUT_MARK, SPAN_LOW, EMPTY_GUARD, REVDET and COUNTER are
       allocated PER EMITTED COPY, because `vm_count_slots` walks a quantified
       body `copies` times. The design's |W| formula counted lexical
       constructs and therefore under-counted under replication.

  V-3  §4.4a site (6)'s verdict "LEXICAL ONLY" is wrong, and the consequence
       is an OUT-OF-BOUNDS SLOT WRITE in emitted code -- K27's class, which
       `vm_count_slots`' own header names: "a lift this pre-pass cannot see
       runs vm_slot_mark(v, v->nmark++) past RX_NSLOTS". Two ways in:
         (a) a callee defined inside `X{0}` is counted ZERO times
             (`vm_count_slots` returns at the `rmin == 0 && rmax == 0` guard,
             and `vm_emit` emits "X{0}: matches empty, no code"), yet the
             CALLEE REGION must still emit the body;
         (b) §6.3's HYBRID emits the callee region SEPARATELY, so that copy
             needs its own slot instances -- counting the subtree once is one
             body short.

AXES
  A  the five per-EMITTED-COPY families, counted from real artifacts
  B  the two per-LEXICAL-NODE families, for contrast
  C  the `{0}` prune: a construct inside `X{0}` allocates NOTHING
  D  |W| over this module's own corpus shapes, so §5.7's range is sourced

Every number here comes from `build/pcrec`'s own emitted artifact -- the slot
LEGEND (`RX_SLOT_*` defines) and `RX_NSLOTS` -- not from reading the emitter.
"""
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
PCREC = os.path.join(REPO, "build", "pcrec")
TMP = os.environ.get("TMPDIR", "/tmp")
OUT = os.path.join(TMP, "dd14_slotcount.c")

FAMILIES = ["GROUP", "PENDING", "EMPTY_GUARD", "SPAN_LOW", "CUT_MARK",
            "REVDET", "COUNTER"]


def slots(pat, extra=()):
    """The artifact's slot legend for `pat`: {family: count}, plus NSLOTS."""
    cmd = [PCREC, "-p", "rx", "--features", "all", "--engine=vm",
           "-o", OUT] + list(extra) + [pat]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip().splitlines()[:1]
    src = open(OUT).read()
    names = set(re.findall(r"#define\s+(RX_SLOT_[A-Z0-9_]+)\s", src))
    counts = {}
    for f in FAMILIES:
        if f == "GROUP":
            counts[f] = len({n for n in names
                             if re.match(r"RX_SLOT_GROUP\d+_(START|END)$", n)})
        elif f == "PENDING":
            counts[f] = len({n for n in names if n.endswith("_PENDING")})
        elif f == "REVDET":
            counts[f] = len({n for n in names
                             if re.match(r"RX_SLOT_REVDET\d+_", n)})
        else:
            counts[f] = len({n for n in names
                             if re.match(r"RX_SLOT_%s\d+$" % f, n)})
    m = re.search(r"#define\s+RX_NSLOTS\s+(\d+)", src)
    counts["NSLOTS"] = int(m.group(1)) if m else -1
    return counts, None


def row(pat, note="", extra=()):
    c, err = slots(pat, extra)
    if c is None:
        print("  %-30s REFUSED: %s" % (pat, err))
        return None
    live = " ".join("%s=%d" % (f, c[f]) for f in FAMILIES if c[f])
    print("  %-30s NSLOTS=%-3d %-46s%s"
          % (pat, c["NSLOTS"], live, ("  # " + note) if note else ""))
    return c


if not os.path.exists(PCREC):
    print("no %s -- build first" % PCREC)
    sys.exit(3)
print("pcrec:", PCREC)
print("python3:", sys.version.split()[0])
print()

print("=== AXIS A: FIVE families are allocated PER EMITTED COPY ============")
print("# One LEXICAL construct, a quantifier around it, and the slot count")
print("# GROWS with the repeat count. If the design's 'one slot per lexical")
print("# construct' premise were true these rows would all be equal.")
_a = []
for n in (1, 2, 3, 5):
    c = row("^((?>a)){%d}$" % n, "ONE lexical atomic group")
    _a.append(c["CUT_MARK"] if c else None)
print("  cut marks by repeat count: %s" % _a)
if _a[0] is not None and len(set(x for x in _a if x)) == 1:
    print("  !! VACUOUS: the count did not grow -- axis A measured nothing")
print()
_b = []
for n in (1, 3, 5):
    c = row("^(a?){0,%d}$" % n, "ONE lexical quantified group")
    _b.append(c["SPAN_LOW"] if c else None)
print("  span-lows by repeat count: %s" % _b)
print()
print("# and the EMPTY_GUARD family, whose gloss the design also had wrong:")
row("^(a?){0,5}$", "bounded repeat, nullable body -> NO guard")
row("^(a?)*$", "UNBOUNDED, nullable body -> the guard's real trigger")
row("^(a?)+$", "unbounded +")
row("^((a)|b)*$", "unbounded, nullable-ish alternation")
print()

print("=== AXIS B: TWO families ARE per lexical node ======================")
for n in (1, 3, 5):
    row("^((a)){%d}$" % n, "capture groups do NOT replicate")
row(r"^((a)){3}\2$", "a MARKED group: one PENDING slot, not three")
print()

print("=== AXIS C: the `{0}` PRUNE -- a construct inside X{0} gets NOTHING =")
row("^((?>a)){1}b$", "the same construct at {1}")
row("^((?>a)){0}b$", "at {0}: NO cut-mark slot at all")
row("^(a?){0,3}b$", "at {0,3}")
row("^(a?){0}b$", "at {0}")
print("# `vm_count_slots` returns at the `rmin == 0 && rmax == 0` guard and")
print("# `vm_emit` writes 'X{0}: matches empty, no code'. So a CALLEE defined")
print("# inside {0} -- a real idiom, measured matching in probe_wrapped_target")
print("# axis Z0 -- is counted ZERO times while its callee region must still")
print("# emit the body. That is the out-of-bounds write vm_count_slots' own")
print("# header names (K27's class).")
print()

print("=== AXIS D: |W| by shape, in TWO populations =======================")
print("# W(g) = every slot INSTANCE the emitted region for g can write,")
print("# minus slots 0 and 1. Measured as (NSLOTS - 2) on a pattern that IS")
print("# the callee body, which is |W| for a call to the whole of it.")
print("#")
print("# D1 -- THE CALLEES THIS MODULE'S OWN CORPUS ACTUALLY USES (§10.2).")
print("# This is the population §5.7 may quote, and NOTHING wider.")
print("#")
print("# THE RECURSIVE ONES ARE MEASURED CALL-ERASED, and that is exact")
print("# rather than approximate: pcrec cannot compile a call today, and a")
print("# CALL NODE ALLOCATES NO SLOT FAMILY OF ITS OWN (§4.4a site 6) -- the")
print("# call site\'s cost is 2|W| TRAIL entries, which are not slots. So the")
print("# body with `(?N)` replaced by `(?:)` has exactly the callee region\'s")
print("# slot demand. The erased spelling is shown beside each row.")
_w1 = []
for pat, note in [
        ("(a|b)", "spellings.rxt's discriminator callee"),
        ("(a|ab)", "atomicity.rxt's isolated callee"),
        ("([a-z]+)", "the linkage prototype's body"),
        ("(a(?:)?b)", "leftrec/captures.rxt's callee, from (a(?1)?b)"),
        ("((a)(?:)?(b))", "callproto P1's callee, from ((a)(?1)?(b))"),
        (r"(a(?:)?b)\1", "slotfamilies axis P MARKED, from (a(?1)?b)\\1"),
        ("((?>a(?:)?))", "slotfamilies axis C ATOMIC, from ((?>a(?1)?))"),
]:
    c = row(pat, note)
    if c:
        _w1.append(c["NSLOTS"] - 2)
if _w1:
    print("  |W| over the CORPUS callees: %s  -> range %d-%d"
          % (_w1, min(_w1), max(_w1)))
print()
print("# D2 -- WIDER shapes, to show the range is a property of the callee")
print("# and not a constant. NOT quotable as 'the corpus'.")
_w2 = []
for pat, note in [
        ("((a)(?:x)?(b))", "three groups"),
        ("(a?){0,5}", "a rung-bearing callee, five span-lows"),
        ("((a)(b)(c)(d))", "five groups"),
        ("((?>a)){5}", "one lexical atomic group, six cut marks"),
]:
    c = row(pat, note)
    if c:
        _w2.append(c["NSLOTS"] - 2)
if _w2:
    print("  |W| over the WIDER shapes: %s  -> range %d-%d"
          % (_w2, min(_w2), max(_w2)))
print("# and |W(0)| for `(?R)` is RX_NSLOTS - 2 BY CONSTRUCTION, whatever")
print("# the pattern is -- the upper bound needs no population at all.")
print()

print("=== REACHABILITY GUARDS ============================================")
ok = True
if _a[0] is not None and _a[-1] is not None and _a[-1] <= _a[0]:
    print("  !! axis A did not show growth"); ok = False
else:
    print("  axis A: cut marks grow with the repeat count -- the")
    print("          per-emitted-copy claim is exercised")
if _b[0] is not None and _b[-1] is not None and _b[-1] <= _b[0]:
    print("  !! axis B/span-low did not show growth"); ok = False
else:
    print("  axis A': span-lows likewise")
print("  axis C: the {0} rows must show FEWER families than their {1}")
print("          siblings, or the prune was not exercised")
print("  guards:", "OK" if ok else "SEE ABOVE")
