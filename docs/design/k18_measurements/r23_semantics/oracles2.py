#!/usr/bin/env python3
"""Oracle-vs-oracle: python3 `re` against libpcre2 10.x over a pattern list x a
subject cross product. The note (§4.6) uses python `re` ALONE and justifies it
by "the K17/K18 entries record zero disagreements between the two oracles
across this whole space". This re-measures that on the spaces at issue."""
import re as _re, subprocess, sys
from itertools import product
patfile, alpha, maxlen = sys.argv[1], sys.argv[2], int(sys.argv[3])
SPAN = "/tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics/pcre2_span"
pats = [l.rstrip("\n") for l in open(patfile) if l.strip() and not l.startswith("#")]
subj = [""]
for n in range(1, maxlen+1):
    subj += ["".join(t) for t in product(alpha, repeat=n)]
lines, keys = [], []
pyres = {}
skipped = 0
for p in pats:
    try:
        c = _re.compile(p)
    except _re.error:
        skipped += 1
        continue
    for s in subj:
        m = c.search(s)
        pyres[(p, s)] = (m.start(), m.end()) if m else None
        lines.append("%s\t%s" % (p, s)); keys.append((p, s))
r = subprocess.run([SPAN], input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=3600)
out = r.stdout.split("\n")
ndiff = 0; nerr = 0; nlim = 0; bad = set()
for k, o in zip(keys, out):
    o = o.strip()
    if o == "err": nerr += 1; continue
    if o.startswith("pcre2err"): nlim += 1; continue
    v = None if o == "nomatch" else tuple(int(x) for x in o.split())
    if v != pyres[k]:
        ndiff += 1; bad.add(k[0])
        if ndiff <= 20: print("ORACLE-DIFF\t%s\t%r\tpy=%s\tpcre2=%s" % (k[0], k[1], pyres[k], v))
print("== %s: %d patterns (%d unparseable by python), %d subjects, %d cells; "
      "%d oracle disagreements on %d patterns; %d pcre2 compile errors; %d pcre2 match-limit cells (excluded)"
      % (patfile, len(pats), skipped, len(subj), len(keys), ndiff, len(bad), nerr, nlim))
