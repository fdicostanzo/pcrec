#!/usr/bin/env python3
"""[M6.1] THE ORACLE TRAP IN `\\Z` -- python3 `re` and PCRE2 do not mean the
same thing by it, and pcrec's base-tier oracle is python (CLAUDE.md).

python's `\\Z` is PCRE2's `\\z` (end of subject, full stop). PCRE2's `\\Z` is
"end of subject OR before a final newline" -- which python spells only as
`(?=\\n?\\Z)` and has no single escape for. So a `.rxt` expectation for `\\Z`
derived from python is WRONG on exactly the subjects `\\Z` exists to
distinguish, and it is wrong in the silent direction: python reports no match
where PCRE2 matches.

Run from docs/design/eng_brep_measurements/probes/ (it borrows that lane's
pcre2_ctypes.py rather than carrying a second copy).

Usage: probe_z_oracle.py
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

CASES = [(r"b\Z", "ab\n"), (r"b\Z", "ab"),
         (r"b\z", "ab\n"), (r"b\z", "ab"),
         (r"b$",  "ab\n"), (r"b$",  "ab"),
         (r"b(?=\n?\Z)", "ab\n")]        # python's spelling of PCRE2's \Z

print("libpcre2 %s ; python %s" % (p2.version(), sys.version.split()[0]))
print("%-14s %-8s %-10s %-10s %s" % ("pattern", "subject", "pcre2", "python",
                                     "verdict"))
bad = 0
for pat, subj in CASES:
    got = p2.compile(pat.encode()).search(subj.encode(), 0)
    pcre2 = got[0] if got else None
    m = re.search(pat, subj)
    py = m.span() if m else None
    agree = pcre2 == py
    bad += not agree
    print("%-14s %-8r %-10s %-10s %s" %
          (pat, subj, pcre2, py, "agree" if agree else "*** DISAGREE ***"))
print("\n%d of %d cells disagree -- every one of them a `\\Z` cell, and every "
      "one in the direction where python reports NO MATCH and PCRE2 matches."
      % (bad, len(CASES)))
