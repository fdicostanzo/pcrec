#!/usr/bin/env python3
"""[OPT-REQPOS] tier 2b's own number: how rare is the RUN against the single
BYTE, on the bench's own throughput text.  Counts only, no timing.

For every censused pattern whose necessary run is >= 2 bytes, counts the run
as a literal in `t-1m.bin` and divides by the count of the rarest byte in it.
That ratio IS the pair filter's selectivity gain -- the factor by which
`memchr(rarest) + one word compare at the known delta` reduces the candidate
rate against `memchr(rarest)` alone.

A run is only a candidate where the byte is PRESENT: where the byte is absent
[OPT-REQBYTE]'s whole-window pre-check already answers the call in one pass
and nothing downstream of it can pay.
"""
import json, sys, os, collections
d = json.load(open(sys.argv[1]))
b = open(os.path.join(os.environ["SUBJ"], "t-1m.bin"), "rb").read()
n = len(b); freq = collections.Counter(b)

def count(s):
    c, i = 0, b.find(s)
    while i >= 0: c += 1; i = b.find(s, i + 1)
    return c

print("%-44s %-14s %4s %10s %10s %9s" %
      ("pattern", "run", "len", "byte hits", "run hits", "gain"))
rows = []
for r in sorted(d["bench"], key=lambda r: r["id"]):
    if r["status"] != "ok" or r["run_hex"] == "-": continue
    run = bytes.fromhex(r["run_hex"])
    if len(run) < 2: continue
    rarest = min(freq[x] for x in set(run))
    rc = count(run)
    gain = (rarest / rc) if rc else float("inf")
    rows.append((r["id"], run, rarest, rc, gain))
for i, run, rarest, rc, gain in rows:
    print("%-44s %-14r %4d %10d %10d %9s" %
          (i[:44], run.decode("latin-1"), len(run), rarest, rc,
           ("inf" if gain == float("inf") else "%.1fx" % gain)))
fin = [g for *_ , g in rows if g != float("inf")]
inf = sum(1 for *_ , g in rows if g == float("inf"))
fin.sort()
print("\nruns >= 2 bytes: %d   run NEVER occurs (gain infinite): %d" % (len(rows), inf))
if fin:
    print("finite gains: min %.2fx  median %.2fx  max %.2fx"
          % (fin[0], fin[len(fin)//2], fin[-1]))
