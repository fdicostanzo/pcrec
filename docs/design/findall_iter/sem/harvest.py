#!/usr/bin/env python3
# docs/design/findall_iter/sem/harvest.py — lane iterdes, [FINDALL-NEXT] design probe.
#
# Harvests (pattern, subject) pairs from the shipped .rxt corpus for semprobe.c:
# every `pattern` block whose `--list-source` row has NO flags, NO pcrec extra
# flags and an empty or `byte` encoding (so libpcre2 at options 0, byte mode, is
# the pattern's own oracle), paired with every DISTINCT inline subject any of the
# block's case lines carries (m/n/ms/ns/mc/g/gp/gu: the startpos is ignored, the
# probe runs a whole find-all from 0). One line per pair, `PATTERN<TAB>SUBJECT`,
# both re-escaped in the .rxt subject-escape vocabulary semprobe.c decodes.
#
# usage: python3 -I harvest.py PCREC_BIN TREE > pairs.tsv
import os
import subprocess
import sys

PCREC, TREE = sys.argv[1], sys.argv[2]


def rxt_files(tree):
    out = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in fs:
            if f.endswith(".rxt"):
                out.append(os.path.join(d, f))
    return sorted(out)


def unquote(s):
    # the cases section's subject column is "..." in the subject-escape vocabulary
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return None


pairs = set()
nblocks = 0
for f in rxt_files(TREE):
    try:
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        continue
    if r.returncode != 0:
        continue
    plain = {}      # block_line -> pattern (escaped)
    section = None
    for raw in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if raw.startswith("#section "):
            section = raw.split()[1]
            continue
        if raw.startswith("#") or not raw.strip():
            continue
        c = raw.split("\t")
        if section is None:
            if c[0] != "pattern" or len(c) < 20:
                continue
            flags, enc, extra = c[5], c[8], c[14]
            if flags or extra or enc not in ("", "byte"):
                continue
            plain[c[1]] = c[4]
            nblocks += 1
        elif section == "cases":
            if len(c) < 8 or c[6] != "inline":
                continue
            pat = plain.get(c[1])
            sub = unquote(c[7])
            if pat is None or sub is None:
                continue
            pairs.add((pat, sub))

for p, s in sorted(pairs):
    print(f"{p}\t{s}")
print(f"harvest: {nblocks} plain byte blocks, {len(pairs)} distinct (pattern, subject) pairs",
      file=sys.stderr)
