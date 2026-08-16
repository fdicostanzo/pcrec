#!/usr/bin/env python3
"""probe_possess_corpus.py — the same analysis probe_possess.py validates,
applied to the REAL corpus, to answer "how much of the population does
question 1 actually take off the table".

probe_possess.py measures whether the analysis is SOUND on a designed family.
This measures whether it is USEFUL on the patterns the project actually has.
The two are different questions and a note that reports only one of them is
half a note.

Reuses probe_possess.py's analysis verbatim (imported, not copied), so a
refutation of the analysis moves both numbers at once.

Usage: probe_possess_corpus.py PATTERNS_FILE > corpus_possess.tsv
Patterns python3 `re` cannot parse (PCRE-only syntax) are REPORTED, not
dropped silently: they are the analysis's blind spot in this instrument, not
in the design, and the denominator has to say so.
"""
import collections
import importlib.util
import os
import re
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location(
    "pp", os.path.join(_here, "probe_possess.py"))
_pp = importlib.util.module_from_spec(_spec)
# Only the ANALYSIS half is taken (everything above probe_possess.py's
# `main`), so importing this file never re-runs the differential sweep.
_src = open(os.path.join(_here, "probe_possess.py")).read().split("def main()")[0]
exec(compile(_src, "probe_possess.py", "exec"), _pp.__dict__)

pats = [l.rstrip("\n") for l in open(_argv[1], errors="replace")
        if l.strip() and not l.startswith("#")]

tally = collections.Counter()
whys = collections.Counter()
unparsed = []
print("pattern\tkind\tlo\thi\tverdict\twhy")
for p in pats:
    try:
        info = _pp.analyse(p)
    except Exception as e:                     # noqa: BLE001
        unparsed.append((p, str(e)[:60]))
        tally["unparsed-by-python-re"] += 1
        continue
    if not info:
        tally["no-quantifier"] += 1
        continue
    for op, lo, hi, bf, eff, verdict, why in info:
        bounded = hi is not _pp.C.MAXREPEAT
        kind = ("bounded" if bounded else "unbounded")
        tally["%s/%s" % (kind, verdict)] += 1
        whys[why.split(":")[0]] += 1
        print("%s\t%s\t%s\t%s\t%s\t%s"
              % (p, kind, lo, "inf" if not bounded else hi, verdict, why))

print("# --- corpus verdicts ---", file=sys.stderr)
for k, v in sorted(tally.items()):
    print("#   %-30s %d" % (k, v), file=sys.stderr)
print("# --- reasons ---", file=sys.stderr)
for k, v in whys.most_common():
    print("#   %-30s %d" % (k, v), file=sys.stderr)
print("# patterns in %d, unparsed by python re %d"
      % (len(pats), len(unparsed)), file=sys.stderr)
for p, e in unparsed[:25]:
    print("#   unparsed %r: %s" % (p, e), file=sys.stderr)
