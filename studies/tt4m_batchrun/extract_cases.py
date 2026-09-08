#!/usr/bin/env python3
"""studies/tt4m_batchrun/extract_cases.py — [TT-4M] real-case extraction.

Adapted, verbatim in logic, from studies/tt4_batching/proto/extract_cases.py
([TT-4.1], Linux): pulls the REAL m/n/ms/ns case lines that follow each
collected pattern's own `pattern` line in its source .rxt file -- the same
subject/startpos values tests/harness/run.sh itself would run, never
synthetic ones.

**[R55-5 (num-F4) fix, 2026-09-08, lane tt4m2f]**: a block is now matched on the
(pattern, flags, features) TRIPLE -- the same key collect_patterns.py's own
`dedup_key` already dedups the manifest on -- not on pattern TEXT ALONE.
Text-only matching silently returns the FIRST block in the source file
whose `pattern` line matches, misattributing cases whenever a later block
in the same file repeats the same regex text under different
`flags`/`features` (measured at 54 files carrying this shape across the
corpus, r55 panel finding num-F4,
docs/dev/reviews/2026-09-08-r55-tt4m-batching.md). Every batch-sizing
number this tool feeds (wall/CPU/knee cells, the answer-identity sweep) was
unaffected -- the SAME misattributed population is reused identically at
every cell of a sweep's grid -- but a per-pattern DENSITY reading drawn
from this tool's own case count was wrong, since a mis-keyed lookup can
return either too FEW cases (a leaner block) or the SAME cases more than
once (two prefixes resolving to one populous block): docs/dev/learnings.md
sec3's "populations nobody counts" shape, the general form of this specific
miscount.

Usage: extract_cases.py MANIFEST.tsv [--limit N] > cases.tsv
Output: prefix<TAB>subject_raw<TAB>startpos (subject_raw still carries its
.rxt-file escape sequences -- decoded the same way tests/harness/driver.c
decodes them, by the C driver, not here).
"""
import argparse
import re
import sys

PATTERN_RE = re.compile(r'^pattern (.*)$')
FLAGS_RE = re.compile(r'^flags\s+([a-zA-Z]+)\s*$')
FEATURES_RE = re.compile(r'^features\s+([a-zA-Z0-9,_-]+)\s*$')
M_RE = re.compile(r'^m\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
N_RE = re.compile(r'^n\s+"(.*)"\s*$')
MS_RE = re.compile(r'^ms\s+(\d+)\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
NS_RE = re.compile(r'^ns\s+(\d+)\s+"(.*)"\s*$')

def _case_line(line):
    """Return (subject_raw, startpos) if `line` is an m/n/ms/ns case line,
    else None."""
    m = M_RE.match(line)
    if m:
        return (m.group(1), "0")
    m = N_RE.match(line)
    if m:
        return (m.group(1), "0")
    m = MS_RE.match(line)
    if m:
        return (m.group(2), m.group(1))
    m = NS_RE.match(line)
    if m:
        return (m.group(2), m.group(1))
    return None

def cases_for_pattern(path, pattern_text, flags_text, features_text):
    """Return [(subject_raw, startpos), ...] for the block whose (pattern,
    flags, features) triple matches exactly (the same key
    collect_patterns.py's own dedup_key uses), FIRST such block in the
    file. flags_text/features_text are "" exactly when collect_patterns.py's
    cur[1]/cur[2] would be -- a block carrying no `flags`/`features` line at
    all.

    Each candidate block (one whose `pattern` line matches pattern_text) is
    collected WHOLE -- its own flags/features and its own case lines -- before
    being judged against the wanted triple, so a candidate that turns out to
    be the wrong block never leaks cases into whichever block is judged
    next."""
    cur_cases = []
    cur_flags = ""
    cur_features = ""
    candidate = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = PATTERN_RE.match(line)
            if m:
                if candidate and cur_flags == flags_text and cur_features == features_text:
                    return cur_cases  # only the first matching block
                cur_cases = []
                cur_flags = ""
                cur_features = ""
                candidate = (m.group(1) == pattern_text)
                continue
            fm = FLAGS_RE.match(line)
            if fm:
                cur_flags = fm.group(1)
                continue
            fm = FEATURES_RE.match(line)
            if fm:
                cur_features = fm.group(1)
                continue
            if not candidate:
                continue
            c = _case_line(line)
            if c is not None:
                cur_cases.append(c)
    if candidate and cur_flags == flags_text and cur_features == features_text:
        return cur_cases
    return []

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
        cases = cases_for_pattern(source_file, pattern, flags, features)
        for subj, pos in cases:
            print(f"{prefix}\t{subj}\t{pos}")
            total_cases += 1
    print(f"# {len(rows)} patterns, {total_cases} cases", file=sys.stderr)

if __name__ == "__main__":
    main()
