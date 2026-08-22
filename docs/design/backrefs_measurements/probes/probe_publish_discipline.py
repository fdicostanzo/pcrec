"""probe_publish_discipline.py -- MEASURED, libpcre2 vs BOTH emitted models.

R32 finding E1, and this lane's answer to it. §3.2 at commit 4cd461f
claimed "a slot is UNSET iff no live path wrote it", making the two-slot
UNSET test total and a self-reference safe with no parser rejection. That
is FALSE while a group is RE-ENTERED: `src/gen/emit_vm.c:3813-3835` writes
slot[2k] when control traverses the group's OPENING position and
slot[2k+1] at the CLOSING one, so on iteration n > 1 the start belongs to
iteration n and the end to iteration n-1. Neither is UNSET. The compare
then runs on a span that is not a capture.

THIS PROBE IS THE ARM-VS-ARM FORM OF THAT. `simvm.py` (the R32 critic
r32eng's simulator, adopted with a `publish` axis) runs the SAME AST, the
SAME search order and the SAME trail discipline in two publication modes:

  publish='open'   the model §3.2 described and emit_vm.c implements today
  publish='close'  the correction -- the opening position goes to a
                   per-group PENDING slot and the (start, end) PAIR is
                   published together at close

Both arms come from ONE simulator, so any infidelity to the real emitter
cancels between them and what remains is the publication discipline alone.
libpcre2 10.46 is the third arm and the oracle of record (D26).

THREE THINGS IT REPORTS, and the third is why this is not merely a
correctness question:

  1. DIVERGENCES per model against libpcre2, over the whole population.
  2. The REVERSED-SPAN count -- cells where ref_s > ref_e, each of which
     is `ref_e - ref_s` underflowing a size_t in EMITTED code and reading
     out of bounds. A wrong answer is a bug; this one is a memory-safety
     defect in a matcher someone else compiles.
  3. A POSITIVE CONTROL: the backref-FREE arm of the population must
     agree in BOTH models, because publication discipline is unobservable
     without a backreference (at match completion every group is closed).
     If that column is not 0/0 the two modes differ somewhere they must
     not, and the byte-identity claim of §11.3 is in question.
"""
import itertools
import sys

import br_oracle as O
import simvm

# Patterns that RE-ENTER a group while a reference to it is live -- the E1
# class. Written out rather than generated, because each one is a distinct
# shape of re-entry and a generator would bury that.
REENTRY = [
    r"(a|b\1)+",            r"^(a|b\1)+$",         r"^(?:(a|b\1))+$",
    r"^(?:(a|b\1)y)+",      r"^(?:(a|b\1)y)+$",    r"(a|b\1)*",
    r"^(?:(a|b\1)|y)+$",    r"((a)|b\2)+",         r"^((a)|b\2)+$",
    r"(?:(a\1?)y)+",        r"^(?:(a\1?)y)+$",     r"((ab|b)\1?)+",
    r"^(?:(a|bb)\1?y)+$",   r"(\1a|b)+",           r"^(\1a|b)+$",
    r"^(?:(\1a|b)y)+$",     r"((a)\2?|b)+",        r"^(?:(a|b)\1?)+$",
]
# The SAME shapes with the backreference removed -- the positive control.
CONTROL = [
    r"(a|b)+",              r"^(a|b)+$",           r"^(?:(a|b))+$",
    r"^(?:(a|b)y)+",        r"^(?:(a|b)y)+$",      r"(a|b)*",
    r"^(?:(a|b)|y)+$",      r"((a)|b)+",           r"^((a)|b)+$",
    r"(?:(a)y)+",           r"^(?:(a)y)+$",        r"((ab|b))+",
    r"^(?:(a|bb)y)+$",      r"(a|b)+",             r"^(a|b)+$",
    r"^(?:(a|b)y)+$",       r"((a))+",             r"^(?:(a|b))+$",
]
# Ordinary backref shapes with NO re-entry -- these must already agree in
# both models, and they are what makes a "36 divergences" headline mean
# "36 in one class" rather than "36 out of who knows".
PLAIN = [
    r"^(a)\1$",             r"^(a*)b\1$",          r"^(a|b)\1$",
    r"^(a)?\1$",            r"^(\w)\1+$",          r"(\w)\1",
    r"^(a)\1*$",            r"^()\1\1$",           r"^(a?)\1{2}$",
    r"^(?:(a)|b)\1$",       r"^(a)(b)\2\1$",       r"^(?:(a|b)\1)+$",
]
ALPHA = "aby"


def subjects(maxlen=4):
    out = [""]
    for L in range(1, maxlen + 1):
        out += ["".join(t) for t in itertools.product(ALPHA, repeat=L)]
    return out


def pcre2(pat, subj, ncap):
    """libpcre2's answer, PADDED to `ncap` groups.

    `pcre2_match` returns rc = the number of ovector PAIRS it filled, and
    that count STOPS at the highest group that participated -- so a pattern
    whose trailing groups are unset comes back with a SHORTER tuple, not
    with None entries. Comparing that raw against the simulator's
    fixed-width tuple reports a shape mismatch as a semantic divergence:
    this probe's own first run called `(a|b)*` on "" a divergence in BOTH
    models and in the CONTROL arm, which is exactly the column that exists
    to be zero. Padding is the fix, and it is applied to the ORACLE side
    only -- the model is never adjusted to agree."""
    if O.compile_err(pat):
        return "ERR"
    r = O.compile(pat).search(subj)
    if r is None:
        return None
    g = tuple(r[1])
    if len(g) < ncap:
        g = g + (None,) * (ncap - len(g))
    return (tuple(r[0]), g)


def model(pat, subj, publish):
    try:
        res, oob = simvm.run(pat, subj, publish=publish)
    except Exception as e:                                # noqa: BLE001
        return "SIMERR:%s" % e, "no"
    if res is None:
        return None, oob
    return (tuple(res[0]), tuple(res[1])), oob


def sweep(pats, subs, label):
    rows = 0
    diff = {"open": 0, "close": 0}
    oob = {"open": 0, "close": 0}
    examples = {"open": [], "close": []}
    for pat in pats:
        if O.compile_err(pat):
            print("  SKIP (libpcre2 refuses): %s" % pat)
            continue
        ncap = simvm.parse(pat)[1]
        for subj in subs:
            want = pcre2(pat, subj, ncap)
            rows += 1
            for pub in ("open", "close"):
                got, ob = model(pat, subj, pub)
                if ob != "no":
                    oob[pub] += 1
                if got != want:
                    diff[pub] += 1
                    if len(examples[pub]) < 4:
                        examples[pub].append((pat, subj, want, got))
    print("  %-28s cells=%d" % (label, rows))
    for pub in ("open", "close"):
        print("    publish=%-6s divergences=%-5d reversed-span cells=%d"
              % (pub, diff[pub], oob[pub]))
        for e in examples[pub]:
            print("        %-22s %-7s libpcre2=%s model=%s"
                  % (e[0], repr(e[1]), e[2], e[3]))
    return rows, diff, oob


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    subs = subjects()
    print("libpcre2 %s ; simulator simvm.py (R32/r32eng, publish axis added)"
          % O.version())
    print("alphabet %r, subjects |s| <= 4 plus the empty string = %d subjects"
          % (ALPHA, len(subs)))
    print()

    print("A. THE RE-ENTRY CLASS (E1's population)")
    n1, d1, o1 = sweep(REENTRY, subs, "re-entry shapes")
    print()
    print("B. ORDINARY BACKREFS, no re-entry")
    n2, d2, o2 = sweep(PLAIN, subs, "plain backref shapes")
    print()
    print("C. POSITIVE CONTROL -- the same shapes with NO backreference")
    print("   Publication discipline is UNOBSERVABLE without a backref (at")
    print("   match completion every group is closed), so both models must")
    print("   agree here. A non-zero column refutes that and puts §11.3's")
    print("   byte-identity claim in question.")
    n3, d3, o3 = sweep(CONTROL, subs, "backref-free control")

    total = n1 + n2 + n3
    print()
    print("SUMMARY")
    print("  cells                              : %d" % total)
    print("  publish=open   divergences         : %d  (reversed-span: %d)"
          % (d1["open"] + d2["open"] + d3["open"],
             o1["open"] + o2["open"] + o3["open"]))
    print("  publish=close  divergences         : %d  (reversed-span: %d)"
          % (d1["close"] + d2["close"] + d3["close"],
             o1["close"] + o2["close"] + o3["close"]))
    print("  control-arm divergences (must be 0): open=%d close=%d"
          % (d3["open"], d3["close"]))
    if total == 0:
        print("REFUSING to report agreement: no cells ran")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
