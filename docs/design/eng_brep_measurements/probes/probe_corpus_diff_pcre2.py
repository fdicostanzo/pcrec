#!/usr/bin/env python3
"""probe_corpus_diff_pcre2.py — TASK B item 2: the two S2.6 censuses'
DIFFERENTIAL-relevant populations, checked against python3 `re` AND
libpcre2 (S8 item 6 lists both censuses as python-only today; strictly they
were not differentially checked against ANY oracle before this --
`probe_possess_corpus.py` only counts verdicts, it never compares a match).

WHAT "differential-relevant" MEANS HERE. Every quantifier
`probe_possess_corpus.py` finds verdict=="possessifiable" in the .rxt corpus
or `realistic_patterns.txt`, differentially tested. Not the whole pattern
verbatim -- S2.2's rule is a function of the quantifier's BODY, its (lo,hi)
count, its preference and its computed FOLLOW (`eff`), nothing else about
the rest of the pattern text (backreferences, named groups, sibling
quantifiers elsewhere in the same pattern). So each row is tested as a
MINIMAL standalone reconstruction: `(?:BODY){lo,hi}[?] FOLLOW` against
`(?:BODY){lo,hi}+ FOLLOW`, where BODY is regenerated from the row's own
parsed body sequence (`walk()` now appends `body` as an 8th tuple element,
added by this lane for exactly this purpose -- see probe_possess.py's own
comment on it) via `regen_body.py` (see that module's docstring for why a
full-pattern unparser is neither needed nor built: any body opcode outside
its modeled set is already declined by the analysis before reaching
"possessifiable", so this probe never needs to round-trip one). FOLLOW is a
concretization of the row's own computed `eff` byte set, not a guess: one
literal byte sampled FROM eff for the non-exact arms (exact-count doesn't
care, so FOLLOW is empty there), plus, for the GREEDY disjoint arm
specifically, an ADDITIONAL empty-follow variant -- greedy's own soundness
argument (S2.3 step 3) claims to hold whether or not the remainder is
nullable, so both are exercised rather than assumed.

Subjects are built the same way -- deterministically, from the row's own
`bf` (body FIRST) and `eff` (FOLLOW) byte sets, not a fixed alphabet -- so a
real corpus body using bytes this lane's OTHER probes never touch (digits,
uppercase, punctuation, whatever `\\d`/`[A-Z0-9._-]`/etc. widen to or
literally consume) still gets subjects that can reach a retreat position.
This is the D47.6 lesson (eng_brep_design.md S10.2) applied to a population
whose alphabet is not chosen by this lane at all.

A body `regen_body.py` cannot round-trip (`Unsupported`) is COUNTED, not
silently skipped, and a nonzero count is itself a finding about the
analysis's own opcode coverage (see that module's docstring for why it
should be rare).

Usage: probe_corpus_diff_pcre2.py PATTERNS_FILE [PATTERNS_FILE...] [--verbose]
"""
import os
import sys
import importlib.util

VERBOSE = "--verbose" in sys.argv
_argv = [a for a in sys.argv[1:] if a != "--verbose"]

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
rb = _import_bare("rb", os.path.join(_here, "regen_body.py"), "if __name__")

try:
    pc = _import_bare("pc", os.path.join(_here, "pcre2_ctypes.py"))
    PCRE2_OK = True
    PCRE2_VERSION = pc.version()
except RuntimeError as e:
    PCRE2_OK = False
    PCRE2_VERSION = None
    print("# SKIP: libpcre2 not available: %s" % e, file=sys.stderr)

C = pp.C


def count_text(lo, hi):
    hi_txt = "" if hi is C.MAXREPEAT else str(hi)
    return "{%d,%s}" % (lo, hi_txt)


def build_variants(op, lo, hi, body_text, eff, why):
    """-> list of (label, as_written, possessive) minimal reconstructions
    for one quantifier row. The two patterns in each pair differ ONLY in
    the trailing quantifier suffix ("" / "?" vs "+")."""
    base = "(?:%s)%s" % (body_text, count_text(lo, hi))
    lazy_suffix = "?" if op is C.MIN_REPEAT else ""
    exact = why.startswith("exact-count")
    follows = []
    if exact:
        follows.append(("exact", ""))
    else:
        if eff:
            b = sorted(eff)[0]
            follows.append(("eff-byte", rb._escape_literal(b, in_class=False)))
        if op is C.MAX_REPEAT:
            # Greedy's own argument (S2.3 step 3) claims to hold whether or
            # not the remainder is nullable -- exercise end-here too.
            follows.append(("end-here", ""))
        if not follows:
            follows.append(("end-here", ""))
    return [(label, base + lazy_suffix + follow, base + "+" + follow)
            for label, follow in follows]


def row_subjects(bf, eff, lo, hi):
    """Deterministic subjects built from THIS row's own computed byte sets."""
    body_bytes = sorted(bf)[:4] or [ord("a")]
    follow_bytes = sorted(eff)[:2]
    hi_n = hi if hi is not C.MAXREPEAT else lo + 4
    lengths = sorted(set(x for x in
                         [0, lo, lo + 1, hi_n, hi_n + 1, max(0, lo - 1), hi_n + 2]
                         if x <= hi_n + 2))
    subs = {""}
    for bb in body_bytes:
        ch = chr(bb) if bb < 128 else bytes([bb]).decode("latin-1")
        for n in lengths:
            run = ch * n
            subs.add(run)
            for fb in follow_bytes:
                fc = chr(fb) if fb < 128 else bytes([fb]).decode("latin-1")
                subs.add(run + fc)
                subs.add(run + fc + fc)
    return sorted(subs)


def compare_python(pat, poss, subjects):
    try:
        rx, rp = pp.re.compile(pat), pp.re.compile(poss)
    except pp.re.error as e:
        return "compile-error", str(e)
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
        a, b = rx.search(s), rp.search(s)
        if a != b:
            return "DIVERGES", (s, a, b)
    return "same", None


def main():
    if not _argv:
        print("usage: probe_corpus_diff_pcre2.py PATTERNS_FILE...", file=sys.stderr)
        sys.exit(2)

    print("source\tpattern\tpref\tlo\thi\twhy\tvariant\tas_written\tpossessive"
          "\tpy_status\tpcre2_status")
    tally = {}
    n_rows = 0
    n_unparsed_patterns = 0
    n_regen_unsupported = 0
    for path in _argv:
        source = os.path.basename(path)
        pats = [l.rstrip("\n") for l in open(path, errors="replace")
                if l.strip() and not l.startswith("#")]
        for p in pats:
            try:
                info = pp.analyse(p)
            except Exception:                       # noqa: BLE001
                n_unparsed_patterns += 1
                continue
            for op, lo, hi, bf, eff, verdict, why, body in info:
                if verdict != "possessifiable":
                    continue
                try:
                    body_text = rb.unparse(body)
                except rb.Unsupported as e:
                    n_regen_unsupported += 1
                    if VERBOSE:
                        print("# regen unsupported for %r: %s" % (p, e),
                              file=sys.stderr)
                    continue
                n_rows += 1
                subs = row_subjects(bf, eff, lo, hi)
                pref = "lazy" if op is C.MIN_REPEAT else "greedy"
                for label, as_written, poss in build_variants(op, lo, hi, body_text, eff, why):
                    py_status, py_detail = compare_python(as_written, poss, subs)
                    if PCRE2_OK:
                        pcre2_status, pcre2_detail = compare_pcre2(as_written, poss, subs)
                    else:
                        pcre2_status, pcre2_detail = "skipped", None
                    key = (source, pref, label, py_status, pcre2_status)
                    tally[key] = tally.get(key, 0) + 1
                    print("%s\t%r\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                          (source, p, pref, lo,
                           "inf" if hi is C.MAXREPEAT else hi,
                           why, label, as_written, poss, py_status, pcre2_status))
                    if py_status == "DIVERGES" or pcre2_status == "DIVERGES":
                        print("# DIVERGE source=%s pattern=%r row=(lo=%s hi=%s pref=%s "
                              "why=%s) variant=%s as_written=%r possessive=%r "
                              "py=%r pcre2=%r" %
                              (source, p, lo, hi, pref, why, label,
                               as_written, poss, py_detail, pcre2_detail),
                              file=sys.stderr)

    print("# --- rows: %d possessifiable quantifiers tested, %d patterns "
          "unparsed by python re, %d bodies regen_body.py could not round-trip "
          "(counted, not silently skipped) ---"
          % (n_rows, n_unparsed_patterns, n_regen_unsupported), file=sys.stderr)
    print("# --- libpcre2: %s (%s) ---" % (PCRE2_OK, PCRE2_VERSION), file=sys.stderr)
    print("# --- confusion matrix (source, pref, variant, py_status, pcre2_status) ---",
          file=sys.stderr)
    for k in sorted(tally, key=str):
        print("#   %-70s %d" % (str(k), tally[k]), file=sys.stderr)

    total_bad_py = sum(v for k, v in tally.items() if k[3] == "DIVERGES")
    total_bad_pcre2 = sum(v for k, v in tally.items() if k[4] == "DIVERGES")
    print("# SOUNDNESS: %d python counterexample(s), %d libpcre2 "
          "counterexample(s) (expected 0 both)" % (total_bad_py, total_bad_pcre2),
          file=sys.stderr)


main()
