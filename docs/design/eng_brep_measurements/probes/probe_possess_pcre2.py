#!/usr/bin/env python3
"""probe_possess_pcre2.py — TASK B item 1: probe_possess.py's own family
(both preference families -- the LAZY half is [R24]'s addition and is the
part §8 item 6 lists as still python-only) re-run against libpcre2, not just
python3 `re`.

R24 already closed the headline for the GREEDY family from outside this
repo (0/5,016×260 against libpcre2, an unarchived panel run). This probe
does the analogous thing for the LAZY family, using the SAME instrument
shape as that panel run and as the flat probe itself, and archives the
result so it can be re-run rather than believed -- the R24 M-F4 lesson
(`../eng_brep_design.md` S10.1) is exactly "a number that cannot be re-run
is not a measurement".

METHOD, and why it is NOT "python-as-written vs libpcre2-possessive". U9
(docs/dev/upstream_issues.md) records that python-possessive and
PCRE2-possessive are not interchangeable -- PCRE2 10.46 has its own bug
where a possessive/atomic BOUNDED repeat of a GROUP also (wrongly) freezes
backtracking into a PRECEDING item that actually consumed. Comparing
python's AS-WRITTEN result against libpcre2's POSSESSIVE result would
conflate two different questions: "is the analysis's verdict sound" and "do
python and PCRE2 agree on what possessive even means here". This probe asks
each oracle the SAME self-consistent question the design note asks of
python: does AS-WRITTEN behave identically to POSSESSIVE, entirely within
ONE engine. Two independent differentials therefore run per pair -- an
all-python one (already the flat probe's own job, reproduced here as a
byte-for-byte cross-check that this new harness agrees with the old one) and
an all-libpcre2 one (the new half). A row's soundness verdict is judged
against EACH oracle separately; only rows verdict=="possessifiable" AND one
oracle's own differential diverges are candidate soundness bugs, and even
then U9's own trigger shape (PREFIX is an OPTIONAL-but-consuming construct,
here exactly "(?:z|)", immediately before a possessive BOUNDED repeat of a
GROUP body) is checked and reported separately before anything is escalated.

Also covers TASK B item 3 in part: FOLLOWS already includes "$", "^", `\\b`,
`\\B` members, so this same run's per-follow slice answers "does libpcre2
agree $ is safe (non-multiline) and unsafe (multiline)" for the greedy
family -- the multiline half needs a small supplementary sweep, in
`probe_dollar_multiline_pcre2.py`, because probe_possess.py's FOLLOWS has no
`(?m)` variant.

Usage: probe_possess_pcre2.py [--verbose] > possess_pcre2.tsv
"""
import itertools
import os
import sys
import importlib.util

VERBOSE = "--verbose" in sys.argv

_here = os.path.dirname(os.path.abspath(__file__))


def _import_bare(name, path, stop_at=None):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    src = open(path).read()
    if stop_at:
        src = src.split(stop_at)[0]
    exec(compile(src, path, "exec"), mod.__dict__)
    return mod


pp = _import_bare("pp", os.path.join(_here, "probe_possess.py"), "def main()")

try:
    pc = _import_bare("pc", os.path.join(_here, "pcre2_ctypes.py"))
    PCRE2_OK = True
    PCRE2_VERSION = pc.version()
except RuntimeError as e:
    PCRE2_OK = False
    PCRE2_VERSION = None
    print("# SKIP: libpcre2 not available: %s" % e, file=sys.stderr)

re = pp.re
C = pp.C


def compare_python(pat, poss, subjects):
    rx, rp = re.compile(pat), re.compile(poss)
    for s in subjects:
        mx, mp = rx.search(s), rp.search(s)
        a = None if mx is None else (mx.span(), mx.groups())
        b = None if mp is None else (mp.span(), mp.groups())
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def compare_pcre2(pat, poss, subjects):
    try:
        rx, rp = pc.compile(pat), pc.compile(poss)
    except pc.Pcre2Error as e:
        return "compile-error", str(e)
    for s in subjects:
        a = rx.search(s)
        b = rp.search(s)
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def is_u9_shape(pfx, body, cposs):
    """U9's trigger: an OPTIONAL-but-consuming preceding construct (here,
    among this family's PREFIXES, exactly "(?:z|)" -- "" has no preceding
    item and "z" is mandatory so has no alternate path to lose) immediately
    before a possessive BOUNDED repeat of a GROUP body (a body wrapped in
    its own parens/alternation, not a bare literal, and a bounded --
    not "*"/"+" -- count)."""
    if pfx != "(?:z|)":
        return False
    if not (body.startswith("(") or body.startswith("[")):
        # bare literal body ("a"): U9's own isolation showed this MATCHES
        # fine ("a?b{0,4}+a" -- character item, not a group).
        return False
    # cposs is the count text with "+" appended, e.g. "{0,4}+"; U9's bug is
    # specific to a BOUNDED count -- "*+"/"++ " were shown to be unaffected.
    core = cposs[:-1] if cposs.endswith("+") else cposs
    return core.startswith("{")


def main():
    subs = pp.subjects()
    print("pref\tpfx\tbody\tcount\tfollow\tverdict\twhy\tpy_status\tpcre2_status\tu9_shape")
    tally = {}
    py_examples = {}
    pcre2_examples = {}
    n_pairs = 0
    for pref, pfx, body, count, follow in itertools.product(
            pp.PREFS, pp.PREFIXES, pp.BODIES, pp.BASE_COUNTS, pp.FOLLOWS):
        cpref, cposs = pp.spellings(count, pref)
        pat = pfx + body + cpref + follow
        poss = pfx + body + cposs + follow
        try:
            re.compile(pat)
            re.compile(poss)
        except re.error:
            continue
        try:
            info = pp.analyse(pat)
        except Exception:                          # noqa: BLE001
            continue
        if not info:
            continue
        verdict, why = info[0][5], info[0][6]
        n_pairs += 1

        py_status, py_detail = compare_python(pat, poss, subs)
        if PCRE2_OK:
            pcre2_status, pcre2_detail = compare_pcre2(pat, poss, subs)
        else:
            pcre2_status, pcre2_detail = "skipped", None

        u9 = is_u9_shape(pfx, body, cposs)

        key = (pref, verdict, py_status, pcre2_status, u9)
        tally[key] = tally.get(key, 0) + 1
        if verdict == "possessifiable" and py_status == "DIVERGES":
            py_examples.setdefault(pref, []).append((pat, py_detail))
        if verdict == "possessifiable" and pcre2_status == "DIVERGES":
            pcre2_examples.setdefault((pref, u9), []).append((pat, pcre2_detail))

        print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
              (pref, pfx, body, count, follow, verdict, why,
               py_status, pcre2_status, u9))

    print("# --- pairs swept: %d, libpcre2 available: %s (%s) ---"
          % (n_pairs, PCRE2_OK, PCRE2_VERSION), file=sys.stderr)
    print("# --- confusion matrix (pref, verdict, py_status, pcre2_status, u9_shape) ---",
          file=sys.stderr)
    for k in sorted(tally, key=str):
        print("#   %-70s %d" % (str(k), tally[k]), file=sys.stderr)

    for pref in pp.PREFS:
        bad = py_examples.get(pref, [])
        print("# PYTHON SOUNDNESS [%s]: %d counterexample(s)" % (pref, len(bad)),
              file=sys.stderr)
        for pat, dv in bad[:10]:
            print("#   %r  %r" % (pat, dv), file=sys.stderr)

    if PCRE2_OK:
        for pref in pp.PREFS:
            non_u9 = pcre2_examples.get((pref, False), [])
            u9_shaped = pcre2_examples.get((pref, True), [])
            print("# LIBPCRE2 SOUNDNESS [%s]: %d counterexample(s) NOT matching "
                  "U9's shape (escalate if any), %d matching U9's shape "
                  "(upstream-note candidates, U9-explained)"
                  % (pref, len(non_u9), len(u9_shaped)), file=sys.stderr)
            for pat, dv in non_u9[:20]:
                print("#   NON-U9 (escalate): %r  %r" % (pat, dv), file=sys.stderr)
            for pat, dv in u9_shaped[:5]:
                print("#   U9-shaped: %r  %r" % (pat, dv), file=sys.stderr)


main()
