#!/usr/bin/env python3
"""[M6.1] The D47.5 gate is SCOPE-BLIND — the concrete cells, both oracles.

`src/opt/possessify.c:579` captures `cx->mods.multiline` ONCE, and
`pcrec_possessify` is called from `src/opt/select_engine.c:145` AFTER the parse
completes, so the value is the parser's END-OF-PATTERN multiline state. `(?m)`
is SCOPED, so for two shapes the end-of-pattern state is FALSE while the `$`'s
own state is TRUE, and the `$`-follow possessification exemption
(eng_brep_design.md §2.5) fires on a `$` it is unsound for.

This probe does NOT test pcrec — pcrec refuses `(?m)` today, which is exactly
what makes the defect latent. It measures what the two spellings MEAN, so that
the difference between "what the gate would decide" and "what is correct" is a
number rather than an argument:

  as-written  = the pattern as the user wrote it            (the CORRECT answer)
  possessive  = the same pattern with the quantifier possessified
                (what a WRONGLY-EXEMPTING gate would compile it to)

A row where the two differ is a cell the shipped gate design would MISCOMPILE
the day the `m` letter is accepted.

Both oracles run every cell: python3 `re` (possessive quantifiers are native
from 3.11) and libpcre2 through the eng_brep lane's ctypes binding.

Usage: probe_d475_scope.py
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(HERE, os.pardir, os.pardir,
                  "eng_brep_measurements", "probes", "pcre2_ctypes.py")
spec = importlib.util.spec_from_file_location("pcre2_ctypes", P2)
p2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2)

# (label, as-written, possessified, subject, end-of-parse multiline, the $'s own)
CELLS = [
    ("leading (?m)      ", r"(?m)[^c]{1,3}$",        r"(?m)[^c]{1,3}+$",
     "a\nc", True,  True),
    ("SCOPED (?m:...)   ", r"(?m:[^c]{1,3}$)",       r"(?m:[^c]{1,3}+$)",
     "a\nc", False, True),
    ("(?m) then (?-m)   ", r"(?m)[^c]{1,3}$(?-m)",   r"(?m)[^c]{1,3}+$(?-m)",
     "a\nc", False, True),
    ("(?m) AFTER the $  ", r"[^c]{1,3}$(?m)",        r"[^c]{1,3}+$(?m)",
     "ab",   True,  False),
    ("no (?m) at all    ", r"[^c]{1,3}$",            r"[^c]{1,3}+$",
     "ab",   False, False),
]


class Unsupported(Exception):
    """The oracle cannot express this pattern at all — reported, never
    silently skipped. python3 `re` rejects a BARE `(?-m)` (it demands the
    `(?-m:...)` form) where PCRE2 accepts it, so one cell below is
    libpcre2-only and says so."""


def spans(engine, pat, subj):
    if engine == "py":
        try:
            m = re.search(pat, subj)
        except re.PatternError as e:
            raise Unsupported(str(e))
        return m.span() if m else None
    got = p2.compile(pat.encode()).search(subj.encode(), 0)
    return got[0] if got else None


print("libpcre2 %s ; python %s" % (p2.version(), sys.version.split()[0]))
print()
print("%-19s %-22s %-7s %-9s %-9s %-9s %s" %
      ("shape", "pattern (as written)", "subject", "as-written", "possessive",
       "pcre2 poss", "verdict"))

wrong = []
py_cannot = []
for label, pat, poss, subj, end_ml, real_ml in CELLS:
    a2 = spans("p2", pat, subj)
    b2 = spans("p2", poss, subj)
    try:
        a = spans("py", pat, subj)
        b = spans("py", poss, subj)
        assert a == a2 and b == b2, ("oracles disagree", label, a, a2, b, b2)
    except Unsupported as e:
        py_cannot.append((label.strip(), str(e)))
        a, b = a2, b2                       # libpcre2 alone carries this row

    # What the SHIPPED gate decides: it reads the end-of-parse multiline state.
    # multiline seen as True  -> widen -> DECLINE  -> as-written, always safe.
    # multiline seen as False -> exempt -> POSSESSIFY -> the possessive answer.
    gate_compiles_to = a if end_ml else b
    correct = a
    ok = gate_compiles_to == correct
    if not ok:
        wrong.append(label.strip())
    print("%-19s %-22s %-7r %-9s %-9s %-9s %s" %
          (label, pat, subj, a, b, b2,
           "ok" if ok else "*** MISCOMPILE ***"))

print()
print("end-of-parse multiline vs the `$`'s OWN multiline state:")
for label, pat, _, _, end_ml, real_ml in CELLS:
    note = ("AGREE" if end_ml == real_ml else
            ("DISAGREE -> unsound" if real_ml else "DISAGREE -> merely conservative"))
    print("  %-19s end-of-parse=%-5s  the $ is multiline=%-5s  %s"
          % (label, end_ml, real_ml, note))

print()
print("%d of %d cells MISCOMPILE under the shipped gate design: %s"
      % (len(wrong), len(CELLS), ", ".join(wrong) if wrong else "none"))
if py_cannot:
    print()
    print("ORACLE COVERAGE: %d cell(s) libpcre2-only, python3 `re` cannot "
          "express the pattern:" % len(py_cannot))
    for label, why in py_cannot:
        print("  %-19s python: %s" % (label, why))
    print("  (every OTHER cell was checked against BOTH oracles and they "
          "agree — asserted, not merely reported.)")
else:
    print("Both oracles agree on every cell (asserted above, not just reported).")
