#!/usr/bin/env python3
"""[M6.6.1] §2 axis A -- EVERY LOOKAROUND SPELLING, and what it actually IS.

Two oracles per row: libpcre2 10.46 (the source of truth, D26) and python3
`re` (which the .rxt harness uses for the base tier, and which §7's goal-facts
list projects out of these same cells rather than re-running).

THE DISCRIMINATOR RULE, taken from backrefs_design.md §2 and from
registry.c:692's own record: a construct that merely COMPILES proves nothing
about what it is. Every row therefore carries a subject on which the answer
distinguishes this construct from its neighbours -- direction (does it look
forward or back), polarity (does it assert or refute), width (does it consume)
and ATOMICITY (does it retry its own alternation for the benefit of what
follows). The atomicity discriminator is registry.c:702-704's own, reproduced
here rather than cited:

    (?=(a|ab))\\1$      NO MATCH on "abab"   <- atomic: keeps its first success
    (?*(a|ab))\\1$      matches [2,4)        <- non-atomic: retries
    (*napla:(a|ab))\\1$ matches [2,4)        <- same construct, verb spelling

Run: probe_spellings.py
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


def pc(pat, subj, start=0):
    return show(la.search(pat, subj, start))


def py(pat, subj, start=0):
    return show(la.pyre_search(pat, subj, start))


def errcell(pat):
    e = la.compile_err(pat)
    if e is None:
        return "ok"
    return "err %d @%d (%s)" % e


def pyerrcell(pat):
    c, err = la.pyre(pat)
    return "ok" if err is None else err


def hdr(t):
    print()
    print("=" * 72)
    print(t)
    print("=" * 72)


print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")

# ---------------------------------------------------------------------------
hdr("AXIS A1 -- COMPILE STATUS of every spelling, both oracles")
print("%-40s | %-28s | %s" % ("spelling", "libpcre2 10.46", "python3 re"))
print("-" * 100)
SPELLINGS = [
    # the four (? forms
    r"(?=a)b", r"(?!a)b", r"(?<=a)b", r"(?<!a)b",
    # the two (? non-atomic forms
    r"(?*a)b", r"(?<*a)b",
    # the alpha verb spellings, short
    r"(*pla:a)b", r"(*nla:a)b", r"(*plb:a)b", r"(*nlb:a)b",
    r"(*napla:a)b", r"(*naplb:a)b",
    # the alpha verb spellings, long
    r"(*positive_lookahead:a)b", r"(*negative_lookahead:a)b",
    r"(*positive_lookbehind:a)b", r"(*negative_lookbehind:a)b",
    r"(*non_atomic_positive_lookahead:a)b",
    r"(*non_atomic_positive_lookbehind:a)b",
    # forms PCRE2 does NOT have, as controls: a non-atomic NEGATIVE lookaround
    r"(*nanla:a)b", r"(*nanlb:a)b", r"(?<!*a)b",
    # the degenerate bodies
    r"(?=)", r"(?!)", r"(?<=)", r"(?<!)",
    r"a(?=)b", r"a(?!)b", r"a(?<=)b", r"a(?<!)b",
]
for p in SPELLINGS:
    print("%-40s | %-28s | %s" % (p, errcell(p), pyerrcell(p)))

# ---------------------------------------------------------------------------
hdr("AXIS A2 -- THE DISCRIMINATORS: what each spelling actually DOES")
print("Each block gives the answer on subjects chosen so that a WRONG reading")
print("of the construct gives a different answer.")

DISC = [
    ("DIRECTION + POLARITY, on one alphabet", [
        (r"(?=a)\w", "ab", "positive lookahead: asserts 'a' next, consumes it"),
        (r"(?=a)\w", "ba", "  ... at offset 1"),
        (r"(?!a)\w", "ab", "negative lookahead: refuses 'a' here"),
        (r"(?!a)\w", "ba", "  ..."),
        (r"(?<=a)\w", "ab", "positive lookbehind: 'a' BEHIND the cursor"),
        (r"(?<=a)\w", "ba", "  ..."),
        (r"(?<!a)\w", "ab", "negative lookbehind"),
        (r"(?<!a)\w", "ba", "  ..."),
    ]),
    ("ZERO WIDTH: the assertion consumes nothing", [
        (r"^(?=a)a$", "a", "lookahead then the same byte: matches"),
        (r"^(?=a).$", "a", "  ... and `.` is what consumes it"),
        (r"^(?=aa)a$", "a", "body longer than the subject: fails"),
        (r"^a(?<=a)$", "a", "lookbehind at end-of-subject over the byte just read"),
    ]),
    ("ATOMICITY -- registry.c:702-704's own discriminator, reproduced", [
        (r"(?=(a|ab))\1$", "abab", "ATOMIC lookahead: keeps its FIRST success"),
        (r"(?*(a|ab))\1$", "abab", "NON-ATOMIC (? spelling: retries"),
        (r"(*napla:(a|ab))\1$", "abab", "NON-ATOMIC verb spelling: same construct"),
        (r"(*pla:(a|ab))\1$", "abab", "ATOMIC verb spelling: same as (?=)"),
    ]),
    ("ATOMICITY of the LOOKBEHIND pair", [
        (r"^(?<*(a|ba))\1", "ba", "non-atomic lookbehind, at pos 0 (vacuous)"),
        (r"(?<*(a|ba))c", "bac", "non-atomic positive lookbehind"),
        (r"(?<=(a|ba))c", "bac", "atomic positive lookbehind, same body"),
        (r"(*naplb:(a|ba))c", "bac", "verb spelling of the non-atomic one"),
    ]),
    ("VERB vs (? SPELLING equivalence, one cell each", [
        (r"(*pla:a)\w", "ab", "(*pla:) == (?=)"),
        (r"(?=a)\w", "ab", ""),
        (r"(*nlb:a)\w", "ba", "(*nlb:) == (?<!)"),
        (r"(?<!a)\w", "ba", ""),
    ]),
]
for title, rows in DISC:
    print()
    print("--- " + title + " " + "-" * max(0, 60 - len(title)))
    print("%-26s %-8s | %-22s | %-22s | note" %
          ("pattern", "subject", "libpcre2", "python re"))
    for pat, subj, note in rows:
        print("%-26s %-8s | %-22s | %-22s | %s" %
              (pat, repr(subj), pc(pat, subj), py(pat, subj), note))

# ---------------------------------------------------------------------------
hdr("AXIS A3 -- THE DEGENERATE BODIES, on real subjects")
print("%-16s %-8s | %-18s | %-18s" % ("pattern", "subject", "libpcre2", "python re"))
for pat, subj in [(r"a(?=)b", "ab"), (r"a(?!)b", "ab"),
                  (r"a(?<=)b", "ab"), (r"a(?<!)b", "ab"),
                  (r"(?=)", ""), (r"(?!)", ""), (r"(?=)a", "a"),
                  (r"a(?!)|ab", "ab"),
                  (r"(?:(?!))|a", "a")]:
    print("%-16s %-8s | %-18s | %-18s" % (pat, repr(subj), pc(pat, subj), py(pat, subj)))

# ---------------------------------------------------------------------------
hdr("AXIS A4 -- QUANTIFIED LOOKAROUND")
print("PCRE2 accepts a quantifier on a lookaround; python3 `re` DOES NOT.")
print("The interesting cell is the EMPTY-ITERATION rule: a lookaround is")
print("zero-width, so a `*` over one can never make progress.")
print()
print("%-22s | %-26s | %-26s" % ("pattern", "libpcre2 compile", "python compile"))
QUANT = [r"(?=a)*", r"(?=a)+", r"(?=a)?", r"(?=a){2}", r"(?=a){0,3}",
         r"(?!a)?", r"(?!a)*", r"(?<=a)*", r"(?<!a)+",
         r"(?:(?=a))*", r"(?:(?=a))+", r"(?:(?!a))*",
         r"(?=a)*+", r"(?=(a))*"]
for p in QUANT:
    print("%-22s | %-26s | %-26s" % (p, errcell(p), pyerrcell(p)))
print()
print("%-24s %-8s | %-24s | %-24s" % ("pattern", "subject", "libpcre2", "python re"))
for pat, subj in [(r"^(?=a)*a$", "a"), (r"^(?=a)+a$", "a"),
                  (r"^(?:(?=a))*a$", "a"), (r"^(?:(?=a))*b$", "b"),
                  (r"^(?=a){2}a$", "a"), (r"^(?!b)*a$", "a"),
                  (r"^(?=(a))*a$", "a"), (r"^(?=(a))+a$", "a"),
                  (r"^(?:(?=(a)))*a$", "a")]:
    print("%-24s %-8s | %-24s | %-24s" % (pat, repr(subj), pc(pat, subj), py(pat, subj)))

# ---------------------------------------------------------------------------
hdr("AXIS A5 -- NESTING and the constructs a lookaround may CONTAIN")
print("%-30s %-10s | %-24s | %-24s" % ("pattern", "subject", "libpcre2", "python re"))
NEST = [
    (r"(?=(?<=a)b)b", "ab"),          # lookbehind inside lookahead
    (r"(?=(?<=a)b)b", "cb"),
    (r"(?<=(?=a)a)b", "ab"),          # lookahead inside lookbehind
    (r"(?<=a(?=b))b", "ab"),
    (r"(?<!(?<=a)b)c", "abc"),        # nested, both negative-ish
    (r"(?=a)(?=\w)a", "a"),           # two lookaheads in series
    (r"(?=(?>a|ab))ab", "ab"),        # atomic group inside a lookahead
    (r"(?=(a))\1b", "ab"),            # backref to a group captured INSIDE
    (r"(a)(?=\1)", "aa"),             # backref INSIDE the lookahead
    (r"(a)(?<=\1)", "aa"),            # backref inside a LOOKBEHIND
    (r"(?=a\b)a", "a b"),             # \b inside a lookahead
    (r"(?<=\ba)b", "ab"),             # \b inside a lookbehind
    (r"(?<=^a)b", "ab"),              # ^ inside a lookbehind
    (r"(?=a$)a", "a"),                # $ inside a lookahead
    (r"(?=a*+)a", "aaa"),             # possessive inside a lookahead
]
for pat, subj in NEST:
    print("%-30s %-10s | %-24s | %-24s" % (pat, repr(subj), pc(pat, subj), py(pat, subj)))

# ---------------------------------------------------------------------------
hdr("AXIS A6 -- LOOKAROUND AT PATTERN START and the MATCH START it reports")
print("This is the cell §5's prefilter argument is built on: erasing the")
print("lookaround gives a SUPERSET LANGUAGE, but the reported match START of")
print("the erased pattern is what the hybrid would hand the VM.")
print()
print("%-24s %-14s | %-16s | %-16s | erased pattern -> its span" %
      ("pattern", "subject", "libpcre2", "python re"))
STARTS = [
    (r"(?=\w)\w+", "  abc", r"\w+"),
    (r"(?<=,)\w+", "ab,cd", r"\w+"),
    (r"(?<!\w)\w+", "ab cd", r"\w+"),
    (r"(?!ab)\w\w", "abcd", r"\w\w"),
    (r"\w+(?=,)", "ab,cd", r"\w+"),
    (r"\w+(?<=b)", "abc", r"\w+"),
]
for pat, subj, erased in STARTS:
    print("%-24s %-14s | %-16s | %-16s | %-10s -> %s" %
          (pat, repr(subj), pc(pat, subj), py(pat, subj), erased,
           pc(erased, subj)))
