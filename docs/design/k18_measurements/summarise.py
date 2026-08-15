#!/usr/bin/env python3
"""Summarise a k18_stats.py TSV: distributions of the cost-bearing counters.

Usage: summarise.py stats.tsv [label]
"""
import collections
import sys

path = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else path

rows = []
with open(path) as fh:
    hdr = fh.readline().rstrip("\n").split("\t")
    for line in fh:
        f = line.rstrip("\n").split("\t")
        if len(f) != len(hdr):
            continue
        rows.append(dict(zip(hdr, f)))

if not rows:
    print("%s: no rows" % label)
    sys.exit(0)


def col(name, cast=int):
    return [cast(r[name]) for r in rows if r[name] != ""]


def pct(v, p):
    v = sorted(v)
    if not v:
        return 0
    i = min(len(v) - 1, int(round((p / 100.0) * (len(v) - 1))))
    return v[i]


print("== %s == (%d patterns)" % (label, len(rows)))
for name in ("maxdepth", "ctxs"):
    v = col(name)
    d = collections.Counter(v)
    print("  %-9s min=%d p50=%d p90=%d p99=%d max=%d   histogram=%s"
          % (name, min(v), pct(v, 50), pct(v, 90), pct(v, 99), max(v),
             " ".join("%d:%d" % kv for kv in sorted(d.items())[:12])))

vis = col("visits")
exp = col("expansions")
red = col("redirects")
nst = col("nonstacktop")
clo = col("closures")
print("  visits     total=%d  max=%d  p99=%d" % (sum(vis), max(vis), pct(vis, 99)))
print("  expansions total=%d  max=%d  p99=%d" % (sum(exp), max(exp), pct(exp, 99)))
print("  redirects  total=%d  max=%d" % (sum(red), max(red)))
print("  NONSTACKTOP redirects total=%d  (patterns with any: %d)"
      % (sum(nst), sum(1 for x in nst if x)))
print("  closures   total=%d  max=%d" % (sum(clo), max(clo)))

# expansions-per-closure: the direct memo-inflation number
infl = [e / float(c) for e, c in zip(exp, clo) if c]
infl.sort()
print("  expansions/closure  p50=%.2f p90=%.2f p99=%.2f max=%.2f"
      % (pct(infl, 50, ), pct(infl, 90), pct(infl, 99), max(infl)))

secs = col("secs", float)
print("  compile secs total=%.2f max=%.3f p99=%.3f" % (sum(secs), max(secs), pct(secs, 99)))

# the patterns at the top of each ceiling, named
worst = sorted(rows, key=lambda r: -int(r["ctxs"]))[:8]
print("  top-ctxs patterns:")
for r in worst:
    print("    ctxs=%-5s maxdepth=%-3s nfa=%-6s visits=%-9s  %s"
          % (r["ctxs"], r["maxdepth"], r["nfa"], r["visits"], r["pattern"][:70]))
