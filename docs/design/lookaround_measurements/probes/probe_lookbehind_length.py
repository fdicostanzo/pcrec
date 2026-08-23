#!/usr/bin/env python3
"""[M6.6.1] §2 axis B -- THE LOOKBEHIND LENGTH RULE, cell by cell on 10.46.

The charter asks for this rule "as PCRE2 10.46 actually implements it". It is
not what the PCRE2 documentation's summary sentence suggests and it is not
what python `re` does, so every cell here is a measurement.

FOUR SEPARATE QUESTIONS, deliberately not run together, because collapsing
them is how a design ends up with one rule where PCRE2 has three:

  B1  WHICH BODIES COMPILE -- fixed, per-branch-fixed-but-different,
      bounded-variable, unbounded -- with the ERROR NUMBER for the ones that
      do not (the number is the fact; D26 tier 3 makes the wording not one).
  B2  THE PREFERENCE ORDER when more than one back-step could succeed. This
      is the question the design's capture semantics rest on, and the answer
      has TWO levels that disagree with each other: top-level BRANCHES are
      tried in WRITTEN ORDER, and within one branch the STEP-BACK LENGTH is
      tried LONGEST FIRST regardless of how the alternation inside it is
      written. A design that implemented "alternatives in written order" at
      both levels would be right about the first and wrong about the second.
  B3  THE max_varlookbehind CAP -- a property of the COMPILE CONTEXT, not of
      the construct, so its DEFAULT is bisected here rather than quoted.
  B4  PCRE2_INFO_MAXLOOKBEHIND, the number the compiled pattern publishes.
      §3's back-step and §5's prefilter both need exactly this quantity, so
      what PCRE2 computes for a composite body is a fact worth having.
"""
import importlib.util
import os
import sys

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


def errcell(pat):
    e = la.compile_err(pat)
    return "ok" if e is None else "err %d (%s)" % (e[0], e[2])


def pyerrcell(pat):
    c, err = la.pyre(pat)
    return "ok" if err is None else err.split(":")[-1].strip()


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")

# ---------------------------------------------------------------------------
hdr("B1 -- WHICH LOOKBEHIND BODIES COMPILE (default compile context)")
print("%-30s | %-6s | %-46s | %s" %
      ("lookbehind body", "maxlb", "libpcre2 10.46", "python3 re"))
print("-" * 118)
B1 = [
    # --- fixed, single length
    (r"(?<=a)x",              "one character"),
    (r"(?<=abc)x",            "three characters, fixed"),
    (r"(?<=\w)x",             "a class"),
    (r"(?<=[abc][def])x",     "two classes"),
    (r"(?<=a{3})x",           "an EXACT count -- still fixed"),
    (r"(?<=(?:ab){2})x",      "an exact count over a group"),
    # --- alternatives of the SAME fixed length
    (r"(?<=ab|cd)x",          "two branches, same length"),
    (r"(?<=(ab|cd))x",        "  ... inside a capture"),
    # --- alternatives of DIFFERENT fixed lengths (the charter's cell)
    (r"(?<=a|bc)x",           "two branches, DIFFERENT fixed lengths"),
    (r"(?<=(a|bc))x",         "  ... inside a capture: ONE branch, variable"),
    (r"(?<=a|bc|def)x",       "three branches, three lengths"),
    # --- nested groups
    (r"(?<=(?:a)(?:b))x",     "nested non-capturing, fixed"),
    (r"(?<=(a)(b))x",         "two captures, fixed"),
    (r"(?<=(?:a|bc)d)x",      "a variable group followed by a fixed byte"),
    (r"(?<=((a|bc)d))x",      "  ... all inside one capture"),
    # --- quantifiers inside
    (r"(?<=a{2,3})x",         "BOUNDED variable"),
    (r"(?<=a{0,3})x",         "bounded variable including zero"),
    (r"(?<=a?)x",             "the ? quantifier"),
    (r"(?<=a*)x",             "UNBOUNDED"),
    (r"(?<=a+)x",             "UNBOUNDED"),
    (r"(?<=a{2,})x",          "UNBOUNDED with a floor"),
    (r"(?<=a*?)x",            "unbounded lazy"),
    (r"(?<=a*+)x",            "unbounded possessive"),
    (r"(?<=(?>a*))x",         "unbounded inside an atomic group"),
    # --- a backreference inside
    (r"(a)(?<=\1)x",          "a backreference of a FIXED-width group"),
    (r"(a|bc)(?<=\1)x",       "a backreference of a VARIABLE-width group"),
    (r"(a)(?<=b\1)x",         "backref plus a literal"),
    # --- other lookarounds inside
    (r"(?<=(?=a)a)x",         "a LOOKAHEAD inside a lookbehind"),
    (r"(?<=(?<=a)b)x",        "a LOOKBEHIND inside a lookbehind"),
    (r"(?<=a(?!b))x",         "a negative lookahead inside"),
    (r"(?=(?<=a)b)x",         "a LOOKBEHIND inside a lookahead"),
    (r"(?=(?<=a*)b)x",        "an UNBOUNDED lookbehind inside a lookahead"),
    # --- \K
    (r"(?<=\Ka)x",            "\\K inside a lookbehind"),
    (r"(?=a\K)x",             "\\K inside a lookahead"),
    (r"(?!a\K)x",             "\\K inside a NEGATIVE lookahead"),
    (r"(?<!\Ka)x",            "\\K inside a negative lookbehind"),
    (r"a\Kb",                 "\\K OUTSIDE any lookaround, as the control"),
    # --- the negative forms take the same rule?
    (r"(?<!a|bc)x",           "NEGATIVE, different fixed lengths"),
    (r"(?<!a*)x",             "NEGATIVE, unbounded"),
    (r"(?<*a|bc)x",           "NON-ATOMIC, different fixed lengths"),
    (r"(?<*a*)x",             "NON-ATOMIC, unbounded"),
]
for pat, note in B1:
    mlb = la.maxlookbehind(pat)
    print("%-30s | %-6s | %-46s | %s" %
          (pat, "-" if mlb is None else mlb, errcell(pat), pyerrcell(pat)))
print()
print("# the same rows again with the NOTE, so the table above stays narrow:")
for pat, note in B1:
    print("    %-30s %s" % (pat, note))

# ---------------------------------------------------------------------------
hdr("B2 -- THE PREFERENCE ORDER when more than one back-step could succeed")
print("The design's capture semantics rest entirely on this. TWO LEVELS, and")
print("they do NOT follow the same rule.")
print()
print("--- level 1: TOP-LEVEL BRANCHES are tried in WRITTEN ORDER ---")
print("%-30s %-8s | %-30s | verdict" % ("pattern", "subject", "libpcre2"))
for pat, subj, verdict in [
    (r"(?<=(a)|(aa))c", "aac", "branch 1 (shorter, written first) WINS"),
    (r"(?<=(aa)|(a))c", "aac", "branch 1 (longer, written first) WINS"),
    (r"(?<=(a)|(aa)|(aaa))c", "aaac", "branch 1 wins over both longer ones"),
    (r"(?<=(aaa)|(aa)|(a))c", "aaac", "branch 1 wins again"),
]:
    print("%-30s %-8s | %-30s | %s" % (pat, repr(subj), show(la.search(pat, subj)), verdict))
print()
print("--- level 2: WITHIN one branch the STEP-BACK LENGTH is tried LONGEST")
print("    FIRST, and the alternation's own written order does NOT decide it ---")
print("%-30s %-8s | %-30s | verdict" % ("pattern", "subject", "libpcre2"))
for pat, subj, verdict in [
    (r"(?<=(a|aa|aaa))c", "aaac", "longest (3) wins though written LAST"),
    (r"(?<=(aaa|aa|a))c", "aaac", "longest (3) wins, written first"),
    (r"(?<=(a|aa))c", "aac", "longest (2) wins though written last"),
    (r"(?<=(x|aa|a))c", "aac", "longest VIABLE (2) wins; 3 is not viable"),
    (r"(?<=(a|ba))c", "bac", "longest (2) wins though written last"),
    (r"(?<=(a|ba))c", "xac", "only length 1 is viable there"),
    (r"(?<=(a{1,3}))c", "aaac", "a bounded quantifier: longest first"),
    (r"(?<=(a|aa)(b|bb))c", "abbc", "composite: the SUM is what varies"),
]:
    print("%-30s %-8s | %-30s | %s" % (pat, repr(subj), show(la.search(pat, subj)), verdict))
print()
print("--- the LOOKAHEAD's own preference, for comparison: ordinary")
print("    leftmost-first alternation, since there is no length to choose ---")
for pat, subj in [(r"(?=(a|ab))ab", "ab"), (r"(?=(ab|a))ab", "ab"),
                  (r"(?=(a|aa))aa", "aa"), (r"(?=(aa|a))aa", "aa")]:
    print("%-30s %-8s | %-30s" % (pat, repr(subj), show(la.search(pat, subj))))

# ---------------------------------------------------------------------------
hdr("B3 -- THE max_varlookbehind CAP: a property of the COMPILE CONTEXT")
print("Bisected, not quoted. `(?<=a{1,N})x` needs a back-step of N.")
lo, hi = 0, 1
while hi < 1 << 20:
    if la.compile_err(r"(?<=a{1,%d})x" % hi) is not None:
        break
    lo, hi = hi, hi * 2
else:
    hi = None
if hi is None:
    print("DEFAULT CAP: no refusal found up to 2^20 -- not a cap this probe can find")
else:
    a, b = lo, hi
    while b - a > 1:
        m = (a + b) // 2
        if la.compile_err(r"(?<=a{1,%d})x" % m) is None:
            a = m
        else:
            b = m
    print("DEFAULT CAP (bisected): largest accepted variable back-step = %d" % a)
    print("  `(?<=a{1,%d})x` -> %s" % (a, errcell(r"(?<=a{1,%d})x" % a)))
    print("  `(?<=a{1,%d})x` -> %s" % (b, errcell(r"(?<=a{1,%d})x" % b)))
print()
print("# the SAME pattern under an EXPLICIT cap, proving the cap is contextual")
print("%-22s | %-12s | %s" % ("pattern", "cap", "libpcre2"))
for n in (0, 1, 2, 3, 4, 5, 16, 255, 256, 65535):
    e = la.compile_err_mvlb(r"(?<=a{1,4})x", n)
    print("%-22s | cap=%-8d | %s" % (r"(?<=a{1,4})x", n,
                                     "ok" if e is None else "err %d (%s)" % (e[0], e[2])))
print()
print("# a FIXED-length lookbehind is NOT subject to the cap at all:")
for n in (1, 2):
    e = la.compile_err_mvlb(r"(?<=aaaaaaaaaa)x", n)
    print("%-22s | cap=%-8d | %s" % (r"(?<=a{10})x-as-literal", n,
                                     "ok" if e is None else "err %d (%s)" % (e[0], e[2])))
print("# and the FIXED bound that does exist -- bisect a plain literal body:")
lo, hi = 1, 2
while hi < 1 << 22:
    if la.compile_err("(?<=" + "a" * hi + ")x") is not None:
        break
    lo, hi = hi, hi * 2
else:
    hi = None
if hi is None:
    print("  no fixed-length refusal found up to 2^22 characters")
else:
    a, b = lo, hi
    while b - a > 1:
        m = (a + b) // 2
        if la.compile_err("(?<=" + "a" * m + ")x") is None:
            a = m
        else:
            b = m
    print("  largest accepted FIXED back-step = %d; %d -> %s"
          % (a, b, errcell("(?<=" + "a" * b + ")x")))

# ---------------------------------------------------------------------------
hdr("B4 -- PCRE2_INFO_MAXLOOKBEHIND for composite bodies")
print("The quantity §3's back-step and §5's prefilter both need.")
print("%-36s | %s" % ("pattern", "maxlookbehind (characters)"))
for pat in [r"abc", r"(?<=a)x", r"(?<=abc)x", r"(?<=a|bc)x", r"(?<=(a|bc))x",
            r"(?<=a{2,5})x", r"(?<=(a|aa)(b|bb))x", r"(?<=a)(?<=bc)x",
            r"(?<=a)x|(?<=bcd)y", r"(?<!abcd)x", r"(?=(?<=abc)d)x",
            r"\babc", r"(?m)^abc", r"a\Kb"]:
    print("%-36s | %s" % (pat, la.maxlookbehind(pat)))

# ---------------------------------------------------------------------------
hdr("B5 -- AT SUBJECT START: what a lookbehind does with too little subject")
print("%-24s %-10s %-4s | %-22s | %s" %
      ("pattern", "subject", "sp", "libpcre2", "python re"))
for pat, subj, sp in [
    (r"(?<=a)b", "b", 0), (r"(?<=a)b", "ab", 0), (r"(?<=a)b", "ab", 1),
    (r"(?<!a)b", "b", 0), (r"(?<!a)b", "ab", 0),
    (r"(?<=a|bc)x", "cx", 0), (r"(?<=a|bc)x", "acx", 0),
    (r"(?<=abc)x", "bcx", 0),
    # startpos: the assertion sees the subject BEFORE startpos in PCRE2
    (r"(?<=a)b", "ab", 1),
    (r"(?<!a)b", "ab", 1),
]:
    print("%-24s %-10s %-4d | %-22s | %s" %
          (pat, repr(subj), sp, show(la.search(pat, subj, sp)),
           show(la.pyre_search(pat, subj, sp))))
print()
print("# THE STARTPOS CELL, stated on its own because it is a CONTRACT question")
print("# for pcrec's rx_search (docs/spec/match_api.md) rather than a syntax one:")
print("# does a lookbehind read subject bytes BEFORE the start offset?")
for pat, subj, sp in [(r"(?<=a)b", "ab", 1), (r"(?<!a)b", "ab", 1),
                      (r"(?<=a)b", "xb", 1), (r"(?<!a)b", "xb", 1)]:
    print("    %-12s subj=%-6s startpos=%d -> pcre2 %-12s python %s"
          % (pat, repr(subj), sp, show(la.search(pat, subj, sp)),
             show(la.pyre_search(pat, subj, sp))))
