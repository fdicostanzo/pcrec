#!/usr/bin/env python3
"""[M6.6.1] §2 axis C -- CAPTURES INSIDE A LOOKAROUND, and the budget cells.

§3's emitted code has to decide, per lookaround polarity, whether it takes a
CAPTURE SNAPSHOT and whether it restores one. That decision is a semantics
question with four separate answers, and the design is wrong if it gives one
answer to all four. Measured here rather than reasoned:

  C1  POSITIVE lookaround that SUCCEEDS -- are its captures retained?
  C2  NEGATIVE lookaround that FAILS (i.e. the assertion SUCCEEDS) -- are the
      captures its body wrote on the way discarded?
  C3  POSITIVE lookaround that FAILS -- the case the design's first draft is
      most likely to get wrong, because the whole enclosing alternative fails
      and a reader concludes nothing observable survives. It is observable
      when the lookaround sits inside an alternation whose OTHER branch
      matches, which is the shape this axis uses throughout.
  C4  A lookaround under a QUANTIFIER, where the body runs more than once.

  C5  Also here because it belongs to the same emitted decision: what a
      lookaround does to \\K, to \\G, and to the reported match START.

  C6  The BUDGET cells (D42.6): does a lookaround body's work show up as
      catastrophic backtracking, i.e. is there a shape whose cost is
      unbounded inside the assertion? Measured against libpcre2's own match
      limit rather than asserted, because §3.8's step-charge claim is exactly
      the claim a panel will ask for a witness for.
"""
import ctypes
import importlib.util
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "la_oracle", os.path.join(_HERE, "la_oracle.py"))
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)


def show(v):
    if v == "ERR":
        return "ERR"
    if v is None:
        return "nomatch"
    span, groups = v
    g = " ".join("_" if x is None else "(%d,%d)" % x for x in groups)
    return "(%d,%d)%s" % (span[0], span[1], (" g:" + g) if g else "")


def row(pat, subj, note=""):
    print("%-34s %-10s | %-26s | %-26s | %s" %
          (pat, repr(subj), show(la.search(pat, subj)),
           show(la.pyre_search(pat, subj)), note))


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)
    print("%-34s %-10s | %-26s | %-26s | %s" %
          ("pattern", "subject", "libpcre2 10.46", "python3 re", "note"))


print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")

hdr("C1 -- POSITIVE lookaround that SUCCEEDS: captures RETAINED?")
row(r"(?=(a))a", "a", "positive lookahead, body captured 'a'")
row(r"(?=(a)(b))ab", "ab", "two groups inside")
row(r"(?<=(a))b", "ab", "positive LOOKBEHIND's capture")
row(r"(?<=(a)(b))c", "abc", "two groups inside a lookbehind")
row(r"(?=(a|b))\w", "b", "which alternative the group holds")
row(r"a(?=(b))b", "ab", "capture then the same text consumed after")
row(r"(?=(?:x)?(a))a", "a", "an optional that did not participate")

hdr("C2 -- NEGATIVE lookaround whose ASSERTION SUCCEEDS: captures DISCARDED?")
row(r"(?!(a))b", "b", "body failed outright: nothing was written")
row(r"(?!(a)x)ab", "ab", "body captured 'a' THEN failed on x -- retained?")
row(r"(?<!(a)x)b", "axb", "  ... the lookbehind mirror (assertion FAILS here)")
row(r"(?<!(z)x)b", "axb", "  ... assertion SUCCEEDS, body wrote nothing")
row(r"(?!(a)x)(a)", "ab", "a SECOND group outside, to prove the answer is read")
row(r"(?!(?:(a)|(b))z)\w", "az", "which of two inner groups, if either")

hdr("C3 -- POSITIVE lookaround that FAILS AFTER PARTIALLY CAPTURING")
print("# The observable shape: the failing lookaround is in a branch whose")
print("# SIBLING matches, so the search continues and the group is readable.")
row(r"(?:(?=(a)x)y|(a))", "ab", "lookahead captures 'a', fails on x; branch 2 matches")
row(r"(?:(?=(a)x)y|.)", "ab", "same, sibling consumes anything")
row(r"(?:(?<=(a)x)y|(b))", "axb", "lookbehind mirror")
row(r"(?:(?=(a))x|(a))", "ab", "lookahead SUCCEEDS then the follow fails")
row(r"(?=(a))x|(a)", "ab", "same without the group wrapper")
row(r"(?:(?=(a)|(b))x|\w)", "ab", "two inner alternatives, follow fails")

hdr("C4 -- A LOOKAROUND UNDER A QUANTIFIER")
row(r"^(?=(a))*a$", "a", "star over a positive lookahead with a capture")
row(r"^(?=(a))+a$", "a", "plus")
row(r"^(?=(a)){2}a$", "a", "exact 2")
row(r"^(?:(?=(a)))*a$", "a", "wrapped in a non-capturing group")
row(r"^(?=(a))*b$", "b", "the body never succeeds: how many iterations?")
row(r"^(?!(a))*b$", "b", "star over a NEGATIVE lookahead")
row(r"^(?<=(a))*", "a", "star over a lookbehind at pos 0")
row(r"a(?<=(a))*b", "ab", "  ... mid-pattern")
print()
print("# THE EMPTY-ITERATION QUESTION. A lookaround is zero-width, so `*` over")
print("# one can never make progress. Does PCRE2 loop forever, iterate once,")
print("# or refuse? Timed, because 'it did not hang' is the measurement:")
for pat, subj in [(r"^(?=a)*a$", "a"), (r"^(?:(?=a))*a$", "a"),
                  (r"^(?:(?=a)|b)*a$", "a"), (r"^(?:(?!x))*a$", "a"),
                  (r"^(?:(?=(a)))*a$", "a")]:
    t0 = time.time()
    r = la.search(pat, subj)
    dt = time.time() - t0
    print("    %-26s %-6s -> %-20s in %.4f s" % (pat, repr(subj), show(r), dt))

hdr("C5 -- \\K, \\G and the reported MATCH START")
row(r"a\Kb", "ab", "\\K outside any lookaround, the control")
print("    (?<=\\Ka)x / (?=a\\K)x etc are COMPILE ERRORS -- see probe_lookbehind_length.py B1")
print()
print("# PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK: does the runtime expose the knob,")
print("# and what does it do? Measured, because err 199's own text names it.")
_lib = la._lib
if hasattr(_lib, "pcre2_set_compile_extra_options_8"):
    _lib.pcre2_compile_context_create_8.restype = ctypes.c_void_p
    _lib.pcre2_compile_context_create_8.argtypes = [ctypes.c_void_p]
    _lib.pcre2_compile_context_free_8.restype = None
    _lib.pcre2_compile_context_free_8.argtypes = [ctypes.c_void_p]
    _lib.pcre2_set_compile_extra_options_8.restype = ctypes.c_int
    _lib.pcre2_set_compile_extra_options_8.argtypes = [ctypes.c_void_p,
                                                       ctypes.c_uint32]

    def with_extra(pat, bits):
        cc = _lib.pcre2_compile_context_create_8(None)
        try:
            _lib.pcre2_set_compile_extra_options_8(cc, bits)
            b = pat.encode("latin-1")
            ec = ctypes.c_int(0)
            eo = ctypes.c_size_t(0)
            code = _lib.pcre2_compile_8(b, len(b), 0, ctypes.byref(ec),
                                        ctypes.byref(eo), cc)
            if code:
                _lib.pcre2_code_free_8(code)
                return "ok"
            return "err %d (%s)" % (ec.value, la.pcre2._errmsg(ec.value))
        finally:
            _lib.pcre2_compile_context_free_8(cc)

    # THE BIT IS DERIVED BY SWEEP, NOT QUOTED -- and this is the SECOND
    # constant in this lane where the value a reader would take from the
    # documentation's list order is wrong on this build. The first draft used
    # 0x00008000 and the behavioural guard below reported "this block
    # measured nothing", which is the only reason the error was caught. A
    # sweep of all 32 bits finds EXACTLY ONE that turns `(?=a\K)x` from
    # err 199 into ok.
    hits = [i for i in range(32)
            if with_extra(r"(?=a\K)x", 1 << i) == "ok"]
    print("    bits that enable \\K in a lookaround: %s"
          % ([hex(1 << i) for i in hits] or "NONE"))
    if len(hits) != 1:
        print("    !! not exactly one bit -- this block measured nothing")
    else:
        BSK = 1 << hits[0]
        print("    (?=a\\K)x   extra=0       -> %s" % with_extra(r"(?=a\K)x", 0))
        print("    (?=a\\K)x   extra=%#x    -> %s" % (BSK, with_extra(r"(?=a\K)x", BSK)))
        print("    (?<=\\Ka)x  extra=%#x    -> %s" % (BSK, with_extra(r"(?<=\Ka)x", BSK)))
        print("    (?<=a*)x   extra=%#x    -> %s" % (BSK, with_extra(r"(?<=a*)x", BSK)))
        print("               ^ CONTROL: an UNRELATED lookbehind error must survive,")
        print("                 or the bit is disabling checks wholesale rather than this one")
        print("    a\\Kb       extra=%#x    -> %s" % (BSK, with_extra(r"a\Kb", BSK)))
        print("               ^ CONTROL: plain \\K, which was already legal, still is")
        print("    the documentation-order guess 0x8000 -> %s"
              % with_extra(r"(?=a\K)x", 0x8000))
else:
    print("    no pcre2_set_compile_extra_options_8 in this runtime")
print()
print("# \\G inside a lookaround (the assertions module's own construct):")
for pat, subj, sp in [(r"(?=\Ga)a", "aa", 0), (r"(?=\Ga)a", "aa", 1),
                      (r"(?<=\Ga)b", "ab", 0)]:
    print("    %-14s subj=%-6s sp=%d -> %s" %
          (pat, repr(subj), sp, show(la.search(pat, subj, sp))))

hdr("C6 -- BUDGET: is there unbounded work INSIDE a lookaround body?")
print("# D42.6 asks whether a lookaround body's steps must be counted. If a")
print("# body can burn unbounded work while the assertion as a whole is")
print("# zero-width, then a budget that does not count them is not a budget.")
print("#")
print("# THE FIRST VERSION OF THIS AXIS WAS VACUOUS and the reason is worth")
print("# more than the axis. It used `(?=(a+)+c)x` on 'a'*n + 'b' and measured")
print("# 0.0000 s at every n -- not because the body is cheap but because")
print("# PCRE2's own START OPTIMIZATION sees a REQUIRED CODE UNIT ('x') that")
print("# the subject does not contain and never runs the match at all. A probe")
print("# whose subject cannot reach the construct reports a confident zero.")
print("# Both arms are kept below so the vacuity is visible rather than fixed")
print("# away -- and the same optimization is a fact §5's prefilter section")
print("# needs, since it is PCRE2 doing exactly what a prefilter does.")
print()
print("%-24s %-6s | %-28s | %s" % ("pattern", "n", "libpcre2", "seconds"))
def timed(pat, subj):
    t0 = time.time()
    try:
        r = show(la.search(pat, subj))
    except Exception as e:                                  # noqa: BLE001
        r = "MATCH-LIMIT/ERR: %s" % str(e)[:34]
    return r, time.time() - t0

for pat in [r"^(a+)+$", r"^(?=(a+)+$)", r"^(a|a)+$", r"^(?=(a|a)+$)",
            r"^(?=(a+)+$)x", r"^(?!(a+)+$)y"]:
    for n in (16, 20, 24):
        r, dt = timed(pat, "a" * n + "b")
        print("%-24s n=%-4d | %-28s | %.4f" % (pat, n, r, dt))
print()
print("# READ THIS AS: `^(?=(a+)+$)` costs the SAME as `^(a+)+$` at every n and")
print("# reaches libpcre2's own match limit (error -47) at the same n. The work")
print("# a lookaround body does is real, is unbounded in the subject, and is")
print("# metered by PCRE2 through the same counter as everything else. The")
print("# `x`-suffixed row is the vacuity control and reads 0.0000 throughout.")
