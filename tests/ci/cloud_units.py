#!/usr/bin/env python3
"""tests/ci/cloud_units.py -- the per-UNIT wall times of one cloud shard ([CLOUD-SUITE] reweigh).

  cloud_units.py record LOG OUT [SECTIONS_TSV]

Writes (or completes) OUT, a `units.tsv` of `unit<TAB>seconds` lines, from what the shard left behind:
  - SECTIONS_TSV: scripts/sectiontimes report output (section start end wall state): one unit per DONE section;
  - LOG: an answer-identity sweep's per-job summary lines (`label|OK|..|NNNs`: one unit per job label), its
    `baseline: .. NNNs` line (`@baseline`), and the `time` trailer (`real XmY.Zs`: `@wall`, the shard step's wall).
A row already in OUT (a wrapper such as cloud_san_shard.sh writes its own) is kept, never overwritten. `@`-names are
per-shard facts, not units: `@wall` the step, `@baseline` / `@build` a fixed cost the shard pays once.
tests/ci/cloud_measure.py reads these files (and CI's sections.tsv, the same shape) from the run artifacts.
"""
import os
import re
import sys

JOB = re.compile(r"^\s*(.+?)\|(?:OK|FAIL[^|]*)\|.*\|(\d+)s\s*$")
BASE = re.compile(r"baseline:.*?(\d+)s\s*$")
REAL = re.compile(r"^real\s+(\d+)m([\d.]+)s")


def parse(log, sections):
    rows = {}
    if sections and os.path.exists(sections):
        for line in open(sections, encoding="utf-8", errors="replace"):
            c = line.rstrip("\n").split("\t")
            # `test-shard` is the make wrapper target around the shard's sections, not a section
            if len(c) >= 5 and c[4] == "done" and c[0] != "test-shard":
                rows[c[0]] = float(c[3])
    if log and os.path.exists(log):
        for line in open(log, encoding="utf-8", errors="replace"):
            line = line.rstrip("\n")
            m = JOB.match(line)
            if m:
                rows[m.group(1).strip()] = float(m.group(2))
                continue
            m = BASE.search(line) if line.startswith("axes: baseline:") else None
            if m:
                rows["@baseline"] = float(m.group(1))
                continue
            m = REAL.match(line)
            if m:
                rows["@wall"] = int(m.group(1)) * 60 + float(m.group(2))
    return rows


def record(log, out, sections=None):
    have = {}
    if os.path.exists(out):
        for line in open(out):
            c = line.rstrip("\n").split("\t")
            if len(c) == 2:
                have[c[0]] = c[1]
    for k, v in parse(log, sections).items():
        have.setdefault(k, "%g" % v)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as f:
        for k, v in have.items():
            f.write("%s\t%s\n" % (k, v))
    return len(have)


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] != "record":
        sys.exit(__doc__)
    n = record(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    print("cloud_units: %d unit row(s) in %s" % (n, sys.argv[3]))
