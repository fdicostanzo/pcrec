#!/usr/bin/env python3
"""probe_dollar_multiline_pcre2.py — TASK B item 3 (remainder): the `$`
follow's multiline gate (eng_brep_design.md S2.5, [R24 S-F2]), re-measured
with libpcre2 as a second oracle.

WHAT THIS IS NOT TESTING. probe_possess.py's own analysis treats every
zero-width assertion in the follow (including `$`) as "widen FOLLOW to all
bytes, decline" -- `first_and_nullable`'s `C.AT` arm has no `$`-specific
carve-out, so under the CURRENT instrument a `$`-follow quantifier never
receives a "possessifiable" verdict via the disjoint arm. S2.5's "0 of 720
diverging (safe), 180 of 720 (unsafe under multiline)" figures are a
different, EMPIRICAL question: if `$` WERE exempted (as D47 ruling 5 says it
should ship, gated live on !multiline), would the as-written/possessive pair
actually agree? That is measured directly here by comparing AS-WRITTEN
against POSSESSIVE regardless of the analysis's own (conservative) verdict,
for every (pref, prefix, body, count) combination against a fixed `$`
follow -- once under default (non-multiline) semantics and once under
`(?m)`. Both python3 `re` and libpcre2 run every cell; S8 item 6 lists this
sweep as python-only today.

Subjects need embedded NEWLINES to exercise `(?m)`'s per-line semantics at
all -- probe_possess.py's own `subjects()` has none (its alphabet is
`abcdz `), so a dedicated subject set is built here: every body/prefix byte,
with 0-3 embedded `\\n`s at various positions, plus a trailing-newline and
no-trailing-newline variant of each (PCRE2 and python both treat "before a
final newline" as also `$`-worthy in non-multiline mode -- that variant is
what makes the safe/unsafe split show up at all).

POPULATION FILTER, added after an unfiltered first run's own finding.
Sweeping ALL (pref, prefix, body, count) combinations against a `$` follow
unfiltered gives 63/528 diverging even with multiline OFF -- which looks
like it refutes S2.5's "0 of 720, safe" claim, but does not: most of that 63
comes from bodies the analysis already declines for reasons that have
nothing to do with `$` (ambiguous bodies like `(a|ab)`, nullable bodies like
`b*`), which diverge against ANY follow, benign or not. The `$`-safety
QUESTION is narrower -- "for a quantifier that is ALREADY sound against an
ordinary follow, does swapping that follow to `$` break it" -- so
`qualifies_except_for_follow()` filters the population to exactly the
combinations the current analysis (unmodified) already calls possessifiable
against a plain literal follow, before ever looking at what `$` does to
them. That is the population S2.5's own figures describe.

Usage: probe_dollar_multiline_pcre2.py [--verbose] > dollar_multiline.tsv
"""
import itertools
import os
import re
import sys
import importlib.util

VERBOSE = "--verbose" in sys.argv

_here = os.path.dirname(os.path.abspath(__file__))


def _import_bare(name, path, stop=None):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    src = open(path).read()
    if stop:
        src = src.split(stop)[0]
    exec(compile(src, path, "exec"), m.__dict__)
    return m


pp = _import_bare("pp", os.path.join(_here, "probe_possess.py"), "def main()")

try:
    pc = _import_bare("pc", os.path.join(_here, "pcre2_ctypes.py"))
    PCRE2_OK = True
    PCRE2_VERSION = pc.version()
except RuntimeError as e:
    PCRE2_OK = False
    PCRE2_VERSION = None
    print("# SKIP: libpcre2 not available: %s" % e, file=sys.stderr)

PCRE2_MULTILINE = 0x00000400


def newline_subjects():
    """Deterministic subjects carrying embedded newlines, built from the
    same alphabet the flat family's bodies/prefixes use (a,b,c,d,z), so a
    body's own FIRST/FOLLOW bytes actually appear around the newlines."""
    base_runs = ["a", "aa", "aaa", "aaaa", "ab", "abab", "z", "za", "zaa",
                 "zab", "zabab", "", "b", "bb"]
    subs = set(base_runs)
    for a in base_runs:
        for b in base_runs:
            subs.add(a + "\n" + b)
            subs.add(a + "\n" + b + "\n")
            subs.add(a + "\n\n" + b)
    return sorted(subs)


SUBJECTS = newline_subjects()


def compare_python(pat, poss, multiline, subjects):
    flags = re.MULTILINE if multiline else 0
    rx, rp = re.compile(pat, flags), re.compile(poss, flags)
    for s in subjects:
        mx, mp = rx.search(s), rp.search(s)
        a = None if mx is None else (mx.span(), mx.groups())
        b = None if mp is None else (mp.span(), mp.groups())
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def compare_pcre2(pat, poss, multiline, subjects):
    opt = PCRE2_MULTILINE if multiline else 0
    try:
        rx, rp = pc.compile(pat, opt), pc.compile(poss, opt)
    except pc.Pcre2Error as e:
        return "compile-error", str(e)
    for s in subjects:
        a, b = rx.search(s), rp.search(s)
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def qualifies_except_for_follow(pfx, body, count, pref):
    """True when (pfx, body, count, pref) would be declared possessifiable
    by the CURRENT analysis for an ordinary literal follow -- i.e. the body
    passes unique-iteration + non-nullable and the count/preference combo
    clears the exact-count or disjointness arm. Used to isolate the
    population the `$`-exemption QUESTION is actually about: bodies/counts
    that are ALREADY sound for a benign follow, so that swapping the follow
    to `$` isolates what `$` itself changes, rather than mixing in
    divergences from bodies the analysis would decline anyway (ambiguous or
    nullable bodies, which the unfiltered sweep found first and which have
    nothing to do with the `$`-follow question -- see this probe's own
    finding, recorded in nestedlazy_findings.txt, for why the filter was
    added after an unfiltered first run misattributed that noise to `$`)."""
    cpref, _ = pp.spellings(count, pref)
    probe_pat = pfx + body + cpref + "c"      # a follow the model never widens
    info = pp.analyse(probe_pat)
    if not info or info[0][5] != "possessifiable":
        return False, None
    return True, info[0][6]                    # (qualifies, why-for-follow="c")


def main():
    follow = "$"
    print("pref\tpfx\tbody\tcount\twhy_for_c_follow\tmultiline\tpy_status\tpcre2_status")
    tally = {}
    arm_tally = {}
    n = 0
    n_skipped_unqualified = 0
    for pref, pfx, body, count in itertools.product(
            pp.PREFS, pp.PREFIXES, pp.BODIES, pp.BASE_COUNTS):
        cpref, cposs = pp.spellings(count, pref)
        pat = pfx + body + cpref + follow
        poss = pfx + body + cposs + follow
        try:
            re.compile(pat)
            re.compile(poss)
        except re.error:
            continue
        qualifies, why = qualifies_except_for_follow(pfx, body, count, pref)
        if not qualifies:
            n_skipped_unqualified += 1
            continue
        arm = "exact-count" if why.startswith("exact-count") else "disjoint"
        n += 1
        for multiline in (False, True):
            py_status, py_detail = compare_python(pat, poss, multiline, SUBJECTS)
            if PCRE2_OK:
                pcre2_status, pcre2_detail = compare_pcre2(pat, poss, multiline, SUBJECTS)
            else:
                pcre2_status, pcre2_detail = "skipped", None
            key = (pref, multiline, py_status, pcre2_status)
            tally[key] = tally.get(key, 0) + 1
            akey = (pref, arm, multiline, py_status)
            arm_tally[akey] = arm_tally.get(akey, 0) + 1
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                  (pref, pfx, body, count, why, multiline, py_status, pcre2_status))
            if VERBOSE and (py_status == "DIVERGES" or pcre2_status == "DIVERGES"):
                print("#   %r vs %r multiline=%s why=%s py=%r pcre2=%r"
                      % (pat, poss, multiline, why, py_detail, pcre2_detail),
                      file=sys.stderr)

    print("# --- pairs per multiline setting: %d qualified (would be "
          "possessifiable for a benign follow), %d skipped (declined "
          "regardless of $ -- ambiguous/nullable body etc.), libpcre2: %s (%s) ---"
          % (n, n_skipped_unqualified, PCRE2_OK, PCRE2_VERSION), file=sys.stderr)
    print("# --- confusion matrix (pref, multiline, py_status, pcre2_status) ---",
          file=sys.stderr)
    for k in sorted(tally, key=str):
        print("#   %-60s %d" % (str(k), tally[k]), file=sys.stderr)

    for multiline in (False, True):
        py_div = sum(v for k, v in tally.items() if k[1] == multiline and k[2] == "DIVERGES")
        pcre2_div = sum(v for k, v in tally.items() if k[1] == multiline and k[3] == "DIVERGES")
        total = sum(v for k, v in tally.items() if k[1] == multiline)
        print("# multiline=%s: python %d/%d diverging, libpcre2 %d/%d diverging"
              % (multiline, py_div, total, pcre2_div, total), file=sys.stderr)

    print("# --- split by which arm qualified the row for follow=\"c\" "
          "(pref, arm, multiline, python status) ---", file=sys.stderr)
    for k in sorted(arm_tally, key=str):
        print("#   %-55s %d" % (str(k), arm_tally[k]), file=sys.stderr)
    print("# EXACT-COUNT ARM is follow-independent by construction (the "
          "rule never inspects FOLLOW): every exact-count row above should "
          "read 'same' regardless of pref/multiline, or the arm itself is "
          "unsound -- not just the $ exemption.", file=sys.stderr)
    print("# DISJOINT ARM, LAZY: a `$` follow makes the remainder "
          "match-may-end-here (nullable-rest in S2.2's sense) whether or "
          "not (?m) is set, which is exactly the condition the LAZY "
          "CONJUNCT already declines for an ordinary follow -- so a lazy "
          "divergence here even at multiline=False is not a NEW `$` defect, "
          "it is the existing lazy+nullable-rest rule, and a real `$` "
          "exemption must feed `$`'s presence into that SAME conjunct "
          "(end_here=True) rather than bypass it.", file=sys.stderr)


main()
