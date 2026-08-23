#!/usr/bin/env python3
"""studies/tt4_batching/proto/extract_cases.py — [TT-4.1] Stage A2 exec-cost
prototype support.

For the per-case exec-cost comparison (harness shape: one `timeout t subj
pos` spawn per case, vs. one process per PATTERN reading all its cases),
this pulls the REAL m/n/ms/ns case lines that follow each collected
pattern's own `pattern` line in its source .rxt file — the same
subject/startpos values `tests/harness/run.sh` itself would run, not
synthetic ones.

Usage: extract_cases.py MANIFEST.tsv [--limit N] > cases.tsv
Output: prefix<TAB>subject_raw<TAB>startpos (subject_raw still carries its
.rxt-file escape sequences -- decoded the same way tests/harness/driver.c
decodes them, by the C driver, not here).
"""
import argparse
import re
import sys

PATTERN_RE = re.compile(r'^pattern (.*)$')
M_RE = re.compile(r'^m\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
N_RE = re.compile(r'^n\s+"(.*)"\s*$')
MS_RE = re.compile(r'^ms\s+(\d+)\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
NS_RE = re.compile(r'^ns\s+(\d+)\s+"(.*)"\s*$')

def cases_for_pattern(path, pattern_text):
    """Return [(subject_raw, startpos), ...] for the block whose pattern
    line matches pattern_text exactly, FIRST such block in the file."""
    cases = []
    in_block = False
    found = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = PATTERN_RE.match(line)
            if m:
                if found:
                    break  # only the first matching block
                in_block = (m.group(1) == pattern_text)
                if in_block:
                    found = True
                continue
            if not in_block:
                continue
            m = M_RE.match(line)
            if m:
                cases.append((m.group(1), "0"))
                continue
            m = N_RE.match(line)
            if m:
                cases.append((m.group(1), "0"))
                continue
            m = MS_RE.match(line)
            if m:
                cases.append((m.group(2), m.group(1)))
                continue
            m = NS_RE.match(line)
            if m:
                cases.append((m.group(2), m.group(1)))
                continue
    return cases

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    with open(args.manifest) as f:
        header = f.readline()
        rows = []
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 5:
                continue
            rows.append(parts)  # prefix, source_file, features, flags, pattern

    if args.limit:
        rows = rows[:args.limit]

    total_cases = 0
    for prefix, source_file, features, flags, pattern in rows:
        cases = cases_for_pattern(source_file, pattern)
        for subj, pos in cases:
            print(f"{prefix}\t{subj}\t{pos}")
            total_cases += 1
    print(f"# {len(rows)} patterns, {total_cases} cases", file=sys.stderr)

if __name__ == "__main__":
    main()
