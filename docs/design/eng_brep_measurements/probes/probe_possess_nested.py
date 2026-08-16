#!/usr/bin/env python3
"""probe_possess_nested.py — the NESTED-LAZY differential.

eng_brep_design.md S8 item 8, narrowed by [R24]: `probe_possess.py` tests
only the OUTERMOST quantifier's verdict (`info[0]`), so the transitive-FOLLOW
line (S2.2: "the enclosing loop's own FIRST set joins the follow") was
differentially untested for a quantifier NESTED inside another quantifier's
body -- until R24's own panel swept it for the GREEDY case (42,336 pairs, 0
diverging, H1 in docs/dev/reviews/2026-08-15-r24-eng-brep.md). The lazy
conjunct (S2.2, S2.3) postdates that sweep, so a LAZY quantifier nested
inside another quantifier's body -- lazy-in-greedy, lazy-in-lazy, and (for
completeness) greedy-in-lazy -- has never been differentially tested. This
probe closes that.

THE SHAPE. Every generated pattern is exactly

    PFX '(' INNER_ATOM INNER_SPELL MIDFIX ')' OUTER_SPELL FOLLOW

one group, one inner quantifier, one outer quantifier, nothing else that can
itself carry a quantifier (PFX/FOLLOW/MIDFIX/INNER_ATOM are all quantifier-
free, asserted below, not assumed). `probe_possess.py`'s own `walk()`
traversal APPENDS a repeat's row before recursing into its body, so for this
exact shape `analyse()` always returns exactly two rows: `info[0]` is the
OUTER quantifier (whatever FOLLOW computes for it) and `info[1]` is the INNER
one (whose FOLLOW is MIDFIX's local first-set unioned with OUTER's own FOLLOW
*and* the enclosing loop's own body FIRST -- S2.2's transitive line, the
thing under test). This is verified structurally (`len(info) == 2` plus a
(lo,hi) identity check against what the generator itself asked for) rather
than assumed, because R24's soundness critic found "index-based `info[i]`
target identification" phantom mismatches in its OWN nested sweep and warned
that `info[0]`'s correctness in the flat family "is correct only by
accident" -- a warning this probe takes as directed at itself.

TWO SEPARATE SOUNDNESS QUESTIONS per generated pattern: is OUTER's own
verdict sound in this nested context (respell OUTER only, holding INNER's
spelling fixed), and is INNER's verdict sound (respell INNER only, holding
OUTER's spelling fixed). Both are checked; a divergence in either is a
soundness counterexample. Comparison is on span AND every capture group
(both INNER_ATOM and the outer group are capturing, so a captured-in-a-
retreated-iteration bug -- exactly the shape S3's third refutation was --
would show up here even if the span happened to agree).

TWO FAILING-DIRECTION CONTROLS, reusing `probe_possess.py`'s own toggles
(module globals, re-read every call, so flipping them between `analyse()`
calls in this one process is enough -- no subprocess, no env var needed):
`pp.NO_LAZY_CONJUNCT = True` reverts to the pre-[R24] rule and should turn a
chunk of nested LAZY "no" verdicts into false "possessifiable" ones that this
harness's own differential then has to catch diverging; `pp.NO_ENCLOSING_FIRST
= True` drops the transitive term itself and should do the same to nested
"no" verdicts of EITHER preference whose retreat lands back in the enclosing
loop's own FIRST set. A control that cannot fail proves nothing
(pcrec-check-design-lessons); both are run and their catch counts reported
next to the real run's counts, not just asserted to exist.

Subjects: `probe_possess.py`'s own `subjects()` (D47.6-fixed: alphabet
includes every prefix byte, plus deterministic repetition-heavy runs/cycles
at lengths 6/8/10/12, prefixed by every pattern byte) PLUS a few longer
deterministic runs/cycles (16/20) added here, because two NESTED bounded
repeats need more depth to reach a retreat position than one flat repeat
does -- the same D47.6 lesson, applied one level up: a subject set built for
the flat family is not guaranteed to reach every nested one.

Every `re.search` is wrapped in a SIGALRM timeout: a body like `(a|ab)`
nested inside another unbounded quantifier is the textbook nested-quantifier
catastrophic-backtracking shape, and this probe deliberately includes
ambiguous bodies (to get "no" verdicts, for non-vacuity) crossed with
unbounded counts on both levels. A timeout is recorded as its own outcome
("TIMEOUT" in the differential column), per the project's rule that a firing
timeout is a finding, never a silent retry.

Usage: probe_possess_nested.py [--verbose] > possess_nested.tsv
"""
import itertools
import os
import signal
import sys
import importlib.util

VERBOSE = "--verbose" in sys.argv

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "pp", os.path.join(_here, "probe_possess.py"))
pp = importlib.util.module_from_spec(_spec)
# Only the ANALYSIS half (everything above probe_possess.py's `main()`) is
# executed, so importing this module never re-runs the flat differential --
# same technique probe_possess_corpus.py already uses, for the same reason.
_src = open(os.path.join(_here, "probe_possess.py")).read().split("def main()")[0]
exec(compile(_src, "probe_possess.py", "exec"), pp.__dict__)

C = pp.C
re = pp.re

# ---- the generated family --------------------------------------------------

INNER_ATOM = ["a", "[ab]", "(a|b)", "(a|ab)", "(?:ab)", "(?:a|bc)"]
# A subset of probe_possess.py's BASE_COUNTS: exact (2,2), disjoint-bounded
# with a zero minimum (0,4) and without (1,3), and unbounded (*) -- one
# representative of each arm the analysis branches on, at both nesting
# levels, is the minimum needed to exercise every combination without the
# full 8-count list blowing up the (already two-axis-deeper) cross product.
COUNTS = ["{0,4}", "{1,3}", "{2,2}", "*"]
MIDFIX = ["", "b", r"\b"]          # empty / local literal follow / assertion
FOLLOW = ["c", "", "$", r"\b"]
PREFIXES = ["", "z"]
# (outer_pref, inner_pref). greedy/greedy is R24's H1 shape, kept here as a
# same-instrument baseline (a different harness reproducing 0 divergences on
# the shape R24 already cleared is itself a small piece of evidence this
# probe's own machinery is not the thing that's broken). The other three are
# the residual: lazy nested in either position.
COMBOS = [("greedy", "greedy"), ("greedy", "lazy"),
          ("lazy", "lazy"), ("lazy", "greedy")]

if os.environ.get("BREP_SMOKE") == "1":
    # Fast structural self-check, not a measurement: trims every axis so the
    # generator/indexing/assertion machinery can be exercised in well under a
    # second. Never used for an archived number.
    INNER_ATOM = INNER_ATOM[:2]
    COUNTS = COUNTS[:2]
    MIDFIX = MIDFIX[:1]
    FOLLOW = FOLLOW[:2]
    PREFIXES = PREFIXES[:1]

for frag in set(MIDFIX) | set(FOLLOW) | set(PREFIXES):
    assert not pp.analyse(frag), \
        "MIDFIX/FOLLOW/PREFIX member %r contains a quantifier -- info[] " \
        "indexing assumption (outer=[0], inner=[1]) would silently break" % frag
for a in INNER_ATOM:
    assert not pp.analyse(a), "INNER_ATOM member %r contains a quantifier" % a

_COUNT_BOUNDS = {"{0,4}": (0, 4), "{1,3}": (1, 3), "{2,2}": (2, 2), "*": (0, None)}


def _hi_matches(row_hi, want_hi):
    if want_hi is None:
        return row_hi is C.MAXREPEAT
    return row_hi == want_hi


def nested_subjects():
    """probe_possess.py's own subjects() (D47.6-fixed) plus longer
    deterministic runs/cycles for the extra depth two nested bounded repeats
    can need to reach a retreat position that one flat repeat could not."""
    s = list(pp.subjects())
    for length in (16, 20):
        for ch in pp._PATTERN_BYTES:
            run = ch * length
            s.append(run)
            for pfx in pp._PATTERN_BYTES:
                s.append(pfx + run)
        for cyc in ("ab", "bc", "ac", "cd"):
            rep = (cyc * (length // len(cyc) + 1))[:length]
            s.append(rep)
    # de-dup, keep order (stable -> re-runs diff cleanly)
    seen, out = set(), []
    for x in s:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


SUBJECTS = nested_subjects()
if os.environ.get("BREP_SMOKE") == "1":
    SUBJECTS = SUBJECTS[:20]


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


signal.signal(signal.SIGALRM, _alarm)
PER_SEARCH_TIMEOUT = 1  # seconds; a body this small should never need it


def compare(rx, rp, subjects):
    """(status, detail) -- status in {"same", "DIVERGES", "TIMEOUT"}."""
    for s in subjects:
        try:
            signal.setitimer(signal.ITIMER_REAL, PER_SEARCH_TIMEOUT)
            mx = rx.search(s)
            my = rp.search(s)
        except _Timeout:
            return "TIMEOUT", s
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        a = None if mx is None else (mx.span(), mx.groups())
        b = None if my is None else (my.span(), my.groups())
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def gen_patterns():
    for atom, ic, mid, oc, fol, pfx, (opref, ipref) in itertools.product(
            INNER_ATOM, COUNTS, MIDFIX, COUNTS, FOLLOW, PREFIXES, COMBOS):
        inner_spell, inner_poss = pp.spellings(ic, ipref)
        outer_spell, outer_poss = pp.spellings(oc, opref)
        base = pfx + "(" + atom + inner_spell + mid + ")" + outer_spell + fol
        inner_target = pfx + "(" + atom + inner_poss + mid + ")" + outer_spell + fol
        outer_target = pfx + "(" + atom + inner_spell + mid + ")" + outer_poss + fol
        yield dict(atom=atom, ic=ic, mid=mid, oc=oc, fol=fol, pfx=pfx,
                   opref=opref, ipref=ipref, base=base,
                   inner_target=inner_target, outer_target=outer_target)


def run(analysis_mode, population, want_verdict_only=None):
    """analysis_mode in {"real", "no_lazy_conjunct", "no_enclosing_first"}.
    Runs the two-target differential over `population` (a list of the dicts
    gen_patterns() yields, pre-filtered to compiling patterns) under the
    given analysis toggles, returns a list of result rows.

    want_verdict_only: if set (e.g. "possessifiable"), only rows whose
    verdict (under THIS analysis_mode) equals it are subject-swept; used for
    the sabotage runs, where the whole point is the newly-flipped rows.
    """
    pp.NO_LAZY_CONJUNCT = (analysis_mode == "no_lazy_conjunct")
    pp.NO_ENCLOSING_FIRST = (analysis_mode == "no_enclosing_first")
    rows = []
    for rec in population:
        info = pp.analyse(rec["base"])
        assert len(info) == 2, \
            "structural assumption broken: %r produced %d rows, not 2" \
            % (rec["base"], len(info))
        outer_row, inner_row = info[0], info[1]
        assert outer_row[1] == _COUNT_BOUNDS[rec["oc"]][0] and \
            _hi_matches(outer_row[2], _COUNT_BOUNDS[rec["oc"]][1]), \
            "info[0] is not the OUTER quantifier for %r: %r" % (rec["base"], outer_row)
        assert inner_row[1] == _COUNT_BOUNDS[rec["ic"]][0] and \
            _hi_matches(inner_row[2], _COUNT_BOUNDS[rec["ic"]][1]), \
            "info[1] is not the INNER quantifier for %r: %r" % (rec["base"], inner_row)

        for target, verdict, why, target_pattern in (
                ("outer", outer_row[5], outer_row[6], rec["outer_target"]),
                ("inner", inner_row[5], inner_row[6], rec["inner_target"])):
            if want_verdict_only is not None and verdict != want_verdict_only:
                continue
            try:
                rx = re.compile(rec["base"])
                rp = re.compile(target_pattern)
            except re.error as e:
                rows.append(dict(rec, target=target, verdict=verdict, why=why,
                                  status="compile-error", detail=str(e)))
                continue
            status, detail = compare(rx, rp, SUBJECTS)
            rows.append(dict(rec, target=target, verdict=verdict, why=why,
                              status=status, detail=detail))
    pp.NO_LAZY_CONJUNCT = False
    pp.NO_ENCLOSING_FIRST = False
    return rows


def main():
    population = []
    skipped_compile = 0
    for rec in gen_patterns():
        try:
            re.compile(rec["base"])
        except re.error:
            skipped_compile += 1
            continue
        population.append(rec)

    print("# population: %d generated, %d dropped (base pattern does not "
          "compile under python re), %d swept" %
          (len(population) + skipped_compile, skipped_compile, len(population)),
          file=sys.stderr)

    print("mode\ttarget\tcombo\tpattern\tverdict\twhy\tstatus")
    real_rows = run("real", population)
    tally = {}
    examples = {}
    for r in real_rows:
        key = ("real", r["target"], (r["opref"], r["ipref"]), r["verdict"], r["status"])
        tally[key] = tally.get(key, 0) + 1
        examples.setdefault(key, []).append(r)
        print("%s\t%s\t%s/%s\t%s\t%s\t%s\t%s" %
              ("real", r["target"], r["opref"], r["ipref"], r["base"],
               r["verdict"], r["why"], r["status"]))

    total_bad = 0
    for target in ("outer", "inner"):
        for combo in COMBOS:
            bad = [r for r in real_rows
                   if r["target"] == target and (r["opref"], r["ipref"]) == combo
                   and r["verdict"] == "possessifiable" and r["status"] != "same"]
            total_bad += len(bad)
            if bad or VERBOSE:
                print("# SOUNDNESS [%s target=%s combo=%s/%s]: %d "
                      "counterexample(s)/timeout(s)" %
                      ("real", target, combo[0], combo[1], len(bad)),
                      file=sys.stderr)
            for r in bad[:10]:
                print("#   %r  status=%s detail=%r" %
                      (r["base"], r["status"], r["detail"]), file=sys.stderr)
    print("# SOUNDNESS [real, all targets/combos]: %d counterexample(s)/timeout(s) "
          "(expected 0)" % total_bad, file=sys.stderr)

    # ---- failing-direction controls ----
    for mode, label in (("no_lazy_conjunct", "NO_LAZY_CONJUNCT"),
                         ("no_enclosing_first", "NO_ENCLOSING_FIRST")):
        sab_rows = run(mode, population, want_verdict_only="possessifiable")
        # a row this control CATCHES is one whose verdict flipped to
        # "possessifiable" under sabotage (so it was swept) and that
        # actually diverges -- i.e. the sabotage's newly-admitted quantifier
        # really is unsound, and the harness sees it.
        caught = [r for r in sab_rows if r["status"] == "DIVERGES"]
        timed_out = [r for r in sab_rows if r["status"] == "TIMEOUT"]
        print("# CONTROL [%s]: %d rows newly 'possessifiable' under sabotage, "
              "%d DIVERGE (caught), %d TIMEOUT" %
              (label, len(sab_rows), len(caught), len(timed_out)), file=sys.stderr)
        for r in caught[:10]:
            print("#   caught: %r target=%s detail=%r" %
                  (r["base"], r["target"], r["detail"]), file=sys.stderr)

    print("# --- confusion matrix (mode, target, combo, verdict, status) ---",
          file=sys.stderr)
    for k in sorted(tally, key=str):
        print("#   %-70s %d" % (str(k), tally[k]), file=sys.stderr)


main()
