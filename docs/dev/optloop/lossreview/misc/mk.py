#!/usr/bin/env python3
"""lossreview/misc: compile ONE bench pattern the way the bench's pcrec-auto
testee does, into OUTDIR/rx.c (+ rx.h), print the stamps / facts on request.

    mk.py PCREC BENCH SET PATTERN OUTDIR [nocaps] [-- extra pcrec flags]   (a `-p PFX` among the extras sets the
    emitted prefix and the file names PFX.c / PFX.h; default rx)

BENCH is a (git archive) copy of pcrec-bench's tree; the pattern is read
byte-exactly from BENCH/bench/SET/patterns/PATTERN.rx and passed with
--pattern-esc (every byte as \\xNN outside printable ASCII), as run_pop.py does.
"""
import os, subprocess, sys

def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)

def main():
    pcrec, bench, st, pat, out = sys.argv[1:6]
    rest = sys.argv[6:]
    nocaps = "nocaps" in rest
    extra = rest[rest.index("--") + 1:] if "--" in rest else []
    b = open(os.path.join(bench, "bench", st, "patterns", pat + ".rx"), "rb").read().rstrip(b"\n")
    os.makedirs(out, exist_ok=True)
    args = ["--features", "all"] + (["-e", "utf8"] if st == "utf8" else []) + (["--no-captures"] if nocaps else []) + extra
    args += ["--pattern-esc", "--pattern", '"' + esc(b) + '"']
    pfx = "rx"
    if "-p" in extra:
        i = extra.index("-p"); pfx = extra[i + 1]; del extra[i:i + 2]
        args = [a for a in args]  # extra was already folded into args below
    args = ["--features", "all"] + (["-e", "utf8"] if st == "utf8" else []) + (["--no-captures"] if nocaps else []) + extra + ["--pattern-esc", "--pattern", '"' + esc(b) + '"']
    r = subprocess.run([pcrec, "-p", pfx, "-o", os.path.join(out, pfx + ".c")] + args, capture_output=True)
    sys.stderr.write(r.stderr.decode("utf8", "replace"))
    sys.exit(r.returncode)

main()
