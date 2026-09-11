#!/usr/bin/env python3
"""extract_byteclasses.py — the BYTE-CLASS population, parsed off EMITTED
ARTIFACTS rather than re-derived from pattern text.

`studies/form_char_twins` established the discipline and the reason for it:
a byte set re-derived from the pattern can disagree with the set the compiler
actually built, and then the study is measuring its own parser.  So this walks
the shipped `.rxt` corpus, compiles each `pattern` block with the worktree's
own `build/pcrec`, and reads the 32-byte `<prefix>_class_bitmapN[32]` tables
and the 256-byte `<prefix>_*_scanN[256]` scan-edge tables straight out of the
emitted C.

Output: `results/byteclasses.tsv`, one row per DISTINCT 256-bit membership
word, with the count of artifacts that produced it and one example site.
Deduplication is by SET CONTENT, which is the same key CONSTITUTIONAL
CONSTRAINT 2(a) requires of any cache — so the row count here is also the
answer to "how many distinct byte classes does the corpus actually contain",
as opposed to how many class SITES it emits.
"""

import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PCREC = os.path.join(REPO, "build", "pcrec")
TESTS = os.path.join(REPO, "tests")
RES = os.path.join(HERE, "results")

BITMAP_RE = re.compile(
    r"\b(\w*class_bitmap\d+)\s*\[\s*32\s*\]\s*=\s*\{(.*?)\}", re.S)
SCAN_RE = re.compile(
    r"\b(\w*scan\d+)\s*\[\s*256\s*\]\s*=\s*\{(.*?)\}", re.S)
NUM_RE = re.compile(r"0[xX][0-9a-fA-F]+|\d+")


def rxt_patterns(limit=0):
    """`pattern` blocks from the corpus, with the flags/features the harness
    itself would pass.  `perr` blocks are skipped (they never compile)."""
    out = []
    for root, _dirs, files in os.walk(TESTS):
        for fn in sorted(files):
            if not fn.endswith(".rxt"):
                continue
            path = os.path.join(root, fn)
            pat = flags = feats = None
            for ln in open(path, encoding="utf-8", errors="replace"):
                s = ln.rstrip("\n")
                if s.startswith("pattern "):
                    if pat is not None:
                        out.append((path, pat, flags, feats))
                    pat, flags, feats = s[8:], None, None
                elif s.startswith("flags "):
                    flags = s[6:].strip()
                elif s.startswith("features "):
                    feats = s[9:].strip()
                elif s.startswith("perr"):
                    pat = None
            if pat is not None:
                out.append((path, pat, flags, feats))
            if limit and len(out) >= limit:
                return out[:limit]
    return out


def bits_of(values):
    """Turn a parsed table into a 256-bit membership word.  A 32-entry table
    is a BIT array (pcrec's VM class test); a 256-entry table is a BYTE
    membership table (the DFA scan edge).  Both are read as what they are —
    the two emitters really did choose differently for the same question, and
    `docs/dev/form_char_step0.md` §4 is where that was measured."""
    if len(values) == 32:
        w = 0
        for i, v in enumerate(values):
            w |= v << (8 * i)
        return w
    if len(values) == 256:
        w = 0
        for i, v in enumerate(values):
            if v:
                w |= 1 << i
        return w
    return None


def main():
    if not os.path.exists(PCREC):
        sys.exit("extract_byteclasses: build/pcrec missing")
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    tmp = os.path.join(HERE, "build", "bc")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    cpath = os.path.join(tmp, "a.c")

    seen = {}
    npat = nok = 0
    for path, pat, flags, feats in rxt_patterns(limit):
        npat += 1
        cmd = ["timeout", "20", PCREC, "-p", "rx", "-o", cpath]
        if flags and "i" in flags:
            cmd.append("-i")
        if feats:
            cmd += ["--features", feats]
        cmd += ["--", pat]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            continue
        nok += 1
        try:
            src = open(cpath, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for rx in (BITMAP_RE, SCAN_RE):
            for tab, body in rx.findall(src):
                vals = [int(x, 0) for x in NUM_RE.findall(body)]
                w = bits_of(vals)
                if not w:
                    continue
                rec = seen.setdefault(w, [0, os.path.relpath(path, REPO),
                                          pat[:60], tab])
                rec[0] += 1

    path = os.path.join(RES, "byteclasses.tsv")
    with open(path, "w") as out:
        out.write("# byte-class population: %d corpus pattern blocks, %d "
                  "compiled, %d DISTINCT sets  date=%s\n"
                  % (npat, nok, len(seen), time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("# bits(256, hex, LSB=byte 0)\tlabel\tsites\tfile\tpattern\n")
        for i, (w, rec) in enumerate(
                sorted(seen.items(), key=lambda kv: -kv[1][0])):
            out.write("%064x\tbc%03d\t%d\t%s\t%s\n"
                      % (w, i, rec[0], rec[1], rec[2].replace("\t", " ")))
    print("wrote %s: %d distinct sets from %d/%d patterns"
          % (path, len(seen), nok, npat))


if __name__ == "__main__":
    main()
