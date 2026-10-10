#!/usr/bin/env python3
"""studies/locate_finish/l2_movers.py -- [OPT-REVEND] L2's MOVER CENSUS.

Compiles every corpus pattern (scripts/emit_sweep.py's own enumeration:
every `pattern`/`pattern-esc` line `pcrec --list-source` reads under
tests/, `-p rx --features all`, `-o -`) with two pcrec binaries, A (the
parent) and B (the change), at one option set, and classifies each pattern
whose artifact differs by WHAT moved:

  - the `#define RX_<NAME>` stamp lines whose value changed (by name),
  - the `rx_info` initializer fields that changed (`.search_form`, ...),
  - `text` where any other line changed (a body, a table, a comment).

Output: one TSV row per mover (file, line-kind, pattern-escaped, class,
stamp transitions), and a summary of classes to stdout. The census is a
COUNT FROM THE BYTES; the design's expectation (locate_finish.md §5 L2.1:
T8 u F-12; L2.2: T4 and the `revend_seed` text) is compared by the caller.

  python3 -I studies/locate_finish/l2_movers.py A_BIN B_BIN OUT.tsv [-- OPTS...]

Run from the repo root (the corpus is read from ./tests through A_BIN's
--list-source). Scratch only; nothing under `make` reads it.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import emit_sweep as es  # noqa: E402

STAMP = re.compile(rb"^#define (RX_[A-Z0-9_]+) (.*)$")
FIELD = re.compile(rb"^    \.([a-z_]+) = (.*),$")


def compile_c(binp, pat, opts):
    argv = [binp, "-p", "rx", "--features", "all"] + opts + ["-o", "-"] + es._pattern_argv(binp, pat)
    r = subprocess.run(argv, capture_output=True, timeout=120)
    return r.returncode, r.stdout


def classify(a, b):
    la, lb = a.splitlines(), b.splitlines()
    sa = {m.group(1): m.group(2) for m in map(STAMP.match, la) if m}
    sb = {m.group(1): m.group(2) for m in map(STAMP.match, lb) if m}
    fa = {m.group(1): m.group(2) for m in map(FIELD.match, la) if m}
    fb = {m.group(1): m.group(2) for m in map(FIELD.match, lb) if m}
    moved = []
    for k in sorted(set(sa) | set(sb)):
        if sa.get(k) != sb.get(k):
            moved.append("%s:%s>%s" % (k.decode(), (sa.get(k) or b"-").decode(errors="replace"),
                                         (sb.get(k) or b"-").decode(errors="replace")))
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k) != fb.get(k):
            moved.append(".%s:%s>%s" % (k.decode(), (fa.get(k) or b"-").decode(errors="replace"),
                                          (fb.get(k) or b"-").decode(errors="replace")))
    ra = [l for l in la if not STAMP.match(l) and not FIELD.match(l)]
    rb = [l for l in lb if not STAMP.match(l) and not FIELD.match(l)]
    if ra != rb:
        moved.append("text")
    return moved


def main():
    argv = sys.argv[1:]
    opts = []
    if "--" in argv:
        k = argv.index("--")
        argv, opts = argv[:k], argv[k + 1:]
    a_bin, b_bin, out = argv
    pats = es.enumerate_corpus(a_bin, ".", 60)

    def task(row):
        f, kind, pat = row
        ra, ca = compile_c(a_bin, pat, opts)
        rb, cb = compile_c(b_bin, pat, opts)
        if ra != rb:
            return row, ["rc:%d>%d" % (ra, rb)]
        if ra != 0 or ca == cb:
            return row, None
        return row, classify(ca, cb)

    with ThreadPoolExecutor(max_workers=12) as ex:
        res = list(ex.map(task, pats))
    classes = {}
    nmov = 0
    with open(out, "w") as fh:
        fh.write("#file\tkind\tpattern\tmoved\n")
        for (f, kind, pat), mv in res:
            if mv is None:
                continue
            nmov += 1
            key = ",".join(sorted({m.split(":")[0] for m in mv}))
            classes[key] = classes.get(key, 0) + 1
            fh.write("%s\t%s\t%s\t%s\n" % (f, kind, es.encode_escape(pat.encode("utf-8", "surrogateescape")
                                                                         if isinstance(pat, str) else pat),
                                           " ".join(mv)))
    print("population %d, movers %d" % (len(pats), nmov))
    for k, v in sorted(classes.items(), key=lambda kv: -kv[1]):
        print("%6d  %s" % (v, k))


if __name__ == "__main__":
    main()
