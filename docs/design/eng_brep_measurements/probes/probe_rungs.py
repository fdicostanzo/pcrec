#!/usr/bin/env python3
"""probe_rungs.py — the RUNG CENSUS.

Runs `pcrec --emit-ir` over a pattern list and reports, per QUANTIFIER (not
per pattern — D46's stamp is per A_REP and two quantifiers in one pattern do
land on different rungs), which S2.5 ladder rung today's emitter selected.

The census is taken from the emitter's OWN listing rather than from a second
walk over the pattern text, which is the only reason it can be trusted to
describe what is emitted: DD-8/S10's constraint is that the listing is
written by the same call that writes the C.

Usage: probe_rungs.py BINARY PATTERNS_FILE > census.tsv
Emits one TSV row per quantifier, plus a `#` summary block on stderr.

`--emit-ir` is a VM listing, so a pattern the selector sends to the DFA has no
rungs to report; those rows are counted separately as `engine=dfa` rather than
dropped, because a bounded repeat that never reaches the VM is exactly the
population ENG-BREP's question 2 is about.
"""
import collections
import re
import subprocess
import sys

BIN, PATS = sys.argv[1], sys.argv[2]

hdr = re.compile(r"^; (\w[\w ]*?)\s{2,}(.*)$")
rung = re.compile(r"^\s+at (L\d+)\s+(\S+)\s+(.*)$")

rows = []
tally = collections.Counter()
refused = []

with open(PATS, errors="replace") as fh:
    pats = [l.rstrip("\n") for l in fh if l.strip()]

print("pattern\tengine\tlabel\trung\tdetail")
for p in pats:
    try:
        r = subprocess.run([BIN, "--emit-ir", "--", p],
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        refused.append((p, "TIMEOUT"))
        tally["timeout"] += 1
        continue
    if r.returncode != 0:
        refused.append((p, r.stderr.strip().split("\n")[0][:100]))
        tally["refused"] += 1
        continue
    meta, quants, in_rungs = {}, [], False
    for line in r.stdout.split("\n"):
        m = hdr.match(line)
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()
        if line.startswith("RUNGS"):
            in_rungs = True
            continue
        if in_rungs:
            m = rung.match(line)
            if m:
                quants.append(m.groups())
            elif line.strip() == "":
                in_rungs = False
    eng = meta.get("engine", "?").split()[0]
    if not quants:
        tally["no-quantifier(%s)" % eng] += 1
        continue
    for lbl, kind, detail in quants:
        tally[kind] += 1
        print("%s\t%s\t%s\t%s\t%s" % (p, eng, lbl, kind, detail))

print("# --- summary ---", file=sys.stderr)
for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
    print("#   %-28s %d" % (k, v), file=sys.stderr)
print("# patterns in: %d, refused: %d" % (len(pats), len(refused)), file=sys.stderr)
for p, why in refused[:40]:
    print("#   refused %r: %s" % (p, why), file=sys.stderr)
