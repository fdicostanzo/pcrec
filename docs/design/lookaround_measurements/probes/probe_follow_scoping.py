#!/usr/bin/env python3
"""[M6.6.1] R33 C1-1 -- THE FOLLOW-MIN SCOPING, measured on both sides.

R33's sharpest finding. `v->fmin` / `v->fdyn` -- the minimum width of what
FOLLOWS the node being emitted -- are baked into a body's rung bound as a
LITERAL. A lookahead's follow starts at the assertion's ENTRY position, so the
body's bytes and the follow's bytes are THE SAME BYTES and `bodyremaining +
fmin` double-counts them. `vm_atomic` scopes both terms
(`emit_vm.c:4244-4247`, restored at `:4285-4286`) but its own header
attributes the scoping to THE CUT -- so the design's §3.6, which derives the
non-atomic form BY DELETING THE CUT, invited an implementer to delete the
scoping with it.

FOUR AXES, and the first two are the ones the fix rests on:

  F1  THE EMITTER'S BOUND LITERALS, reproduced from the shipped compiler:
      does the SAME body really get a different bound when something follows
      it? This is the mechanism, and it is in-pcrec rather than modelled.
  F2  THE PREDICTED CELLS against libpcre2 and python: what the right answer
      is for the three shapes an unscoped body would miscompile, and WHICH
      DIRECTION each one fails in. The negative row is the dangerous one --
      an unsound prune inside a negative assertion is a FALSE MATCH.
  F3  THE LOOKBEHIND's own arithmetic, per polarity, because C1-1's own
      finding is that "the same as the lookahead" is wrong there: for
      `(?<=X)` the body ENDS at the entry position, so an inherited bound is
      arithmetically sound -- and under the NEGATIVE polarity an early body
      failure still flips the verdict.
  F4  THE NON-ATOMIC LOOKBEHIND's observable branch retry (R33 C1-3), folded
      in here because it is the same emitted region and the same probe run.
"""
import importlib.util
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "la_oracle", os.path.join(_HERE, "la_oracle.py"))
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

PCREC = os.path.join(_ROOT, "build", "pcrec")


def show(v):
    if v == "ERR":
        return "ERR"
    if v is None:
        return "nomatch"
    span, groups = v
    g = " ".join("_" if x is None else "(%d,%d)" % x for x in groups)
    return "(%d,%d)%s" % (span[0], span[1], (" g:" + g) if g else "")


def emit(pat):
    r = subprocess.run(["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                        "--features", "all", "-o", "-", "--", pat],
                       capture_output=True, text=True, cwd=_ROOT)
    return None if r.returncode else r.stdout


_BOUND = re.compile(r"RX_PRUNE_TOO_SHORT\((\w+),\s*(\d+)\)")


def bounds(pat):
    """Every emitted prune bound literal, in order -- or the string "REFUSED"
    when pcrec will not compile the pattern at all.

    R33 V-4: the first version returned None for BOTH "refused" and "no such
    pattern", and the caller printed None as an empty site list -- so
    `a(?=b+c)`, which pcrec REFUSES because module `lookaround` is not built,
    was published as a measurement reading "no prune sites". A compile failure
    printed as a measurement is the shape this lane's own defect list is
    about."""
    src = emit(pat)
    if src is None:
        return "REFUSED"
    return _BOUND.findall(src)


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


print("libpcre2:", la.version())
print("python3 :", sys.version.split()[0])
print("pcrec   :", "present" if os.path.exists(PCREC) else "ABSENT")
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")

# ---------------------------------------------------------------------------
hdr("F1 -- THE EMITTER'S BOUND LITERALS: does the follow really change them?")
print("R33 C1-1 named four patterns. Reproduced here against this lane's own")
print("build rather than quoted, because the whole fix rests on the mechanism")
print("being real.")
print()
print("%-24s | %s" % ("pattern", "emitted RX_PRUNE_TOO_SHORT(cursor, N)"))
print("-" * 78)
PAIRS = [
    (r"(?:(a+)b)",       r"(?:(a+)b)a+b",   "the SAME body, alone and followed"),
    (r"((?:aa|a)+)",     r"((?:aa|a)+)bcd", "a second body, alone and followed"),
    (r"((?:ab|a)+)",     r"((?:ab|a)+)xyz", "a third"),
]
if not os.path.exists(PCREC):
    print("  SKIPPED -- no build/pcrec. This line is the skip, not silence.")
else:
    moved = 0
    for alone, followed, note in PAIRS:
        ba, bf = bounds(alone), bounds(followed)
        print("%-24s | %s" % (alone, ba))
        print("%-24s | %s   <- %s" % (followed, bf, note))
        if ba != bf:
            moved += 1
    print()
    print("BODIES WHOSE BOUND MOVED WHEN A FOLLOW WAS ADDED: %d of %d"
          % (moved, len(PAIRS)))
    if moved == 0:
        print("  !! NONE MOVED -- C1-1's mechanism is not reproduced on this")
        print("  !! build and the fix below has no measured basis.")
    print()
    print("# THE CONTROL, and it is what makes the numbers above mean what")
    print("# C1-1 says: an ATOMIC group's body does NOT inherit the follow,")
    print("# because vm_atomic zeroes fmin/fdyn (emit_vm.c:4244-4247).")
    # THE COMPARISON IS ON THE BODY'S OWN SITE, not on the whole list. A
    # first version compared the lists and reported the control FAILING,
    # because `(?>(a+)b)a+b` emits TWO sites -- the atomic body's (unchanged
    # at 1) and the trailing `a+b`'s own (also 1). Comparing lists conflated
    # two different sites; the control passes on the site it is about.
    for alone, followed in [(r"(?>(a+)b)", r"(?>(a+)b)a+b")]:
        ba, bf = bounds(alone), bounds(followed)
        print("%-24s | %s" % (alone, ba))
        print("%-24s | %s" % (followed, bf))
        print("   the ATOMIC BODY's own site is bf[0]; the second entry in the")
        print("   followed row is the trailing `a+b`'s own site, a DIFFERENT")
        print("   node -- comparing whole lists conflates them")
        same = ba and bf and ba[0] == bf[0]
        print("  atomic body's own bound is follow-INDEPENDENT: %s (%s vs %s)"
              % ("YES" if same else "NO", ba[0] if ba else None,
                 bf[0] if bf else None))
        if not same:
            print("  !! the control FAILED -- then vm_atomic does not scope")
            print("  !! after all, and the proposed rule is not merely inherited")

# ---------------------------------------------------------------------------
hdr("F2 -- THE PREDICTED CELLS: what the right answer is, and which way it fails")
print("%-18s %-8s | %-22s | %-22s | the failure an unscoped body would cause"
      % ("pattern", "subject", "libpcre2 10.46", "python3 re"))
print("-" * 118)
CELLS = [
    (r"(?=(a+)b)a+b",  "aab",
     "MISSED MATCH: body bound 1+2=3, no cursor clears it -> nomatch"),
    (r"(?!(a+)b)a+b",  "aab",
     "FALSE MATCH: body pruned to fail -> the NEGATIVE assertion SUCCEEDS"),
    (r"(?*(a+)b)a+b",  "aab",
     "as row 1; §3.6 is the arm most likely to lose the scoping"),
    (r"(?<=(a+)b)c",   "aabc",
     "LOOKBEHIND: body ENDS at entry, so an inherited bound is SOUND here"),
    (r"(?<!(a+)b)c",   "aabc",
     "LOOKBEHIND NEGATIVE: an early body failure still FLIPS the verdict"),
]
for pat, subj, note in CELLS:
    print("%-18s %-8s | %-22s | %-22s | %s"
          % (pat, repr(subj), show(la.search(pat, subj)),
             show(la.pyre_search(pat, subj)), note))
print()
print("# THE CONTROLS: the same shapes with the assertion REMOVED, so a reader")
print("# can see that the answers above are about the assertion and not about")
print("# the body:")
for pat, subj in [(r"(a+)b", "aab"), (r"a+b", "aab")]:
    print("    %-18s %-8s -> %s" % (pat, repr(subj), show(la.search(pat, subj))))
print()
print("# THE TWO LOOKBEHIND ROWS ABOVE ARE err 125 AND THAT IS THE POINT:")
for pat in [r"(?<=(a+)b)c", r"(?<!(a+)b)c"]:
    ee = la.compile_err(pat)
    print("    %-18s -> %s" % (pat, "ok" if ee is None else "err %d (%s)" % (ee[0], ee[2])))
print("# a VARIABLE-width lookbehind body is refused by PCRE2 and by §2.5, so")
print("# the lookahead's own counterexample shape has no lookbehind spelling.")
print("# F3 is where the lookbehind's real cells are.")

# ---------------------------------------------------------------------------
hdr("F3 -- CAN A LOOKBEHIND BODY EVEN HAVE A PRUNE SITE? (measured, and the")
print("     answer refuted this lane's first simplification)")
print()
print("The tempting derivation: §2.5 ships only FIXED-width lookbehind")
print("branches, a fixed-width body has no quantifier to prune, so the hazard")
print("cannot arise behind. **THAT IS FALSE**, and one row below is why: an")
print("EXACT COUNT `a{3}` is fixed-width by §2.5's rule AND is lowered as an")
print("`A_REP` that takes a cursor rung with an MRL clamp. A design that had")
print("shipped the derivation would have left the lookbehind unscoped on")
print("exactly the bodies §2.5 admits.")
print()
print("A capture wrapper is needed to force the VM at all (a capture-free")
print("pattern compiles to the DFA, which has no prune sites); it is stated")
print("rather than hidden, because a sweep without it measures nothing.")
print()
print("%-26s %-12s | %s" % ("body, wrapped + followed", "engine", "prune sites"))
print("-" * 78)
if os.path.exists(PCREC):
    for body, note in [(r"a{3}",   "EXACT COUNT -- FIXED per §2.5, and it PRUNES"),
                       (r"ab",     "a literal run -- fixed, no rung"),
                       (r"(a)(b)", "two captures -- fixed, no rung"),
                       (r"a|bc",   "two fixed branches -- no rung"),
                       (r"a{2,3}", "bounded variable -- REFUSED by §2.5"),
                       (r"a+",     "unbounded -- REFUSED by §2.5"),
                       # R33 verifier: exact-count GROUPS behave like `a{3}`
                       # and are the sharper cells, because a reader is more
                       # likely to think a group is not a rung.
                       (r"(?:ab){2}", "an exact count over a GROUP -- FIXED, and it PRUNES"),
                       (r"a{2}",      "a second exact count -- FIXED, and it PRUNES"),
                       (r"a(?=b+c)",  "fixed width 1 but CONTAINS a lookahead -- "
                                      "pcrec REFUSES it (the module is not built), "
                                      "so this row is a REFUSAL, not a measurement")]:
        alone = "((?:" + body + "))x"
        followed = "((?:" + body + "))xyz"
        ba, bf = bounds(alone), bounds(followed)
        src = emit(followed) or ""
        eng = "vm" if 'RX_ENGINE "vm"' in src else ("dfa" if src else "-")
        def fmt(b):
            return "REFUSED" if b == "REFUSED" else [x[1] for x in b]
        print("%-26s %-12s | alone=%-9s followed=%-9s   <- %s"
              % (body, eng, fmt(ba), fmt(bf), note))
    print()
    print()
    print("THE LAST ROW READS `REFUSED` AND THAT IS THE POINT (R33 V-4): pcrec")
    print("cannot compile a lookaround at all, so the nesting cell CANNOT be")
    print("measured in-pcrec today. §3.4's sentence about a lookbehind body")
    print("containing a lookahead is therefore ARGUED FROM PCRE2's semantics")
    print("(the inner assertion's cursor runs AHEAD of the entry position, so")
    print("`cursor + bodyremaining == p` does not hold inside it), and it is")
    print("marked ARGUED in the design rather than MEASURED.")
    print()
    print("READ THIS AS: a lookbehind body that §2.5 ADMITS can still carry a")
    print("prune site whose literal moves with the follow, so the lookbehind")
    print("needs its own ruling and cannot inherit the lookahead's by")
    print("derivation. R33 C1-1 said exactly this and it is now measured.")
print()
print("THE ARITHMETIC, per direction (ARGUED, with the cells that would break it):")
print("  LOOKAHEAD:  the body's bytes and the follow's bytes are THE SAME")
print("              BYTES (both start at the entry position p), so")
print("              `cursor + bodyremaining + fmin` double-counts and the")
print("              bound is UNSOUND. Under the NEGATIVE polarity an unsound")
print("              prune makes the body fail, which makes the assertion")
print("              SUCCEED -- a FALSE MATCH, not a missed one.")
print("  LOOKBEHIND: the body ENDS at p, so a cursor inside it satisfies")
print("              `cursor + bodyremaining == p` and the test becomes")
print("              `p + fmin <= ceiling` -- EXACTLY the follow's real")
print("              requirement, hence SOUND in both polarities.")
print("  BUT the last row of the table above is the reason the RULE is still")
print("  uniform: a lookbehind body may CONTAIN a lookahead, and that inner")
print("  lookahead's scoping requirement is unconditional. Scoping at")
print("  `vm_look` for every direction and polarity is one rule at one site;")
print("  the cost is the lookbehind's lost (sound) prune, and the table above")
print("  prices it -- `a{3}` behind a 3-byte follow keeps bound 1 instead of 3.")

# ---------------------------------------------------------------------------
hdr("F4 -- THE NON-ATOMIC LOOKBEHIND's BRANCH RETRY (R33 C1-3)")
print("The cell that separates the two lookbehind atomicities ACROSS BRANCHES,")
print("which is what §3.6 has to draw and §10's nonatomic.rxt has to contain.")
print()
print("%-26s %-10s | %-26s | note" % ("pattern", "subject", "libpcre2"))
for pat, subj, note in [
    (r"(?<*(a)|(ba))c\2", "bacba", "NON-atomic: retries into branch 2"),
    (r"(?<=(a)|(ba))c\2", "bacba", "atomic: keeps branch 1, so \\2 is unset"),
    (r"(?<*(a)|(ba))c",   "bac",   "no follow to force a retry: branch 1 wins"),
    (r"(?<*(ba)|(a))c\2", "baca",  "branch order reversed"),
    (r"(?*(a)|(ab))\2",   "abab",  "the LOOKAHEAD analogue, for comparison"),
    (r"(?=(a)|(ab))\2",   "abab",  "  ... atomic"),
]:
    print("%-26s %-10s | %-26s | %s"
          % (pat, repr(subj), show(la.search(pat, subj)), note))

# ---------------------------------------------------------------------------
hdr("F5 -- `\\K`'s REFUSAL SCOPE (R33 C1-7): the NEGATIVE controls")
print("§2.7 says the hook rejects an A_KRESET 'while parsing a lookaround")
print("body'. That sentence has two readings and only one matches PCRE2. The")
print("REFUSED set must be recursive through nested groups AND nested")
print("lookarounds; the COMPILING set is what a too-broad check would break.")
print()
print("REFUSED (err 199 expected):")
for pat in [r"(?=(a\K))x", r"(?=a(?:\K))x", r"(?=(?:(?=\K)))x", r"(?*a\K)x",
            r"(?<*\Ka)x", r"(*pla:a\K)x", r"(*nlb:\Ka)x", r"(?<=\Ka)x",
            r"(?=a\K)x", r"(?!a\K)x", r"(?<!\Ka)x"]:
    e = la.compile_err(pat)
    print("    %-20s -> %s" % (pat, "ok  <-- NOT REFUSED" if e is None
                               else "err %d" % e[0]))
print("COMPILES (a too-broad check would break these):")
for pat in [r"(?=a)\Kb", r"a(?=b)\Kc", r"(?<=a)\Kb", r"a\Kb"]:
    e = la.compile_err(pat)
    print("    %-20s -> %s" % (pat, "ok" if e is None
                               else "err %d  <-- WRONGLY REFUSED" % e[0]))
