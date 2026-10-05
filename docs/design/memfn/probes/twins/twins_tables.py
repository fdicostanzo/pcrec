#!/usr/bin/env python3
"""memfn twins: render T-A transcripts (ta_set output) as markdown tables.

    python3 twins_tables.py ta TRANSCRIPT [SPANS]   # default 16,256,4096,65536

One table per hit density: rows = set/variant, columns = span, cells = the
min ns per find-all; a last column gives shape/nib2 at the largest span
(< 1 = the tailored classifier is faster)."""
import re
import sys


def ta(path, spans):
    rows, cols, cur = {}, None, None
    for line in open(path):
        m = re.match(r"## set (\S+)\s+shape=(\S+)", line)
        if m:
            cur = (m.group(1), m.group(2))
            continue
        f = line.split()
        if not f or f[0] not in ("none", "sparse", "dense", "real") or f[1] == "members":
            continue
        vals = [float(x) for x in re.findall(r"([\d.]+)\(\+", line)]
        rows.setdefault(f[0], []).append((cur, f[1], vals))
    allspans = [16, 64, 256, 1024, 4096, 16384, 65536]
    idx = [allspans.index(s) for s in spans]
    for dens, rs in rows.items():
        print("\n%s (ns per find-all)\n" % dens)
        print("| set | shape | variant | " + " | ".join("%d B" % s for s in spans) + " | shape/nib2 |")
        print("|---" * (len(spans) + 4) + "|")
        nib = {r[0][0]: r[2] for r in rs if r[1] == "nib2"}
        for (sid, shp), var, vals in rs:
            ratio = ""
            if var == "shape" and sid in nib:
                ratio = "%.2f" % (vals[-1] / nib[sid][-1])
            print("| %s | %s | %s | %s | %s |" % (sid, shp, var, " | ".join(
                "%.1f" % vals[i] if vals[i] < 1000 else "%.0f" % vals[i] for i in idx), ratio))


if __name__ == "__main__":
    spans = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [16, 256, 4096, 65536]
    if sys.argv[1] == "ta":
        ta(sys.argv[2], spans)
