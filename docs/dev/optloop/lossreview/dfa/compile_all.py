#!/usr/bin/env python3
"""Compile every DFA-route pattern the bench's way (pcrec-auto: --features all).

    compile_all.py PCREC BENCH_DIR LIST.tsv OUTDIR
Writes OUTDIR/<set>__<pat>.{c,h,facts,ir,err}. Pattern bytes from the .rx
export are passed with --pattern-esc (run_pop.py's escaping)."""
import subprocess, sys, os
pc, bench, lst, out = sys.argv[1:5]
def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return '"' + "".join(o) + '"'
os.makedirs(out, exist_ok=True)
for ln in open(lst):
    s, p = ln.split()
    pat = open(os.path.join(bench, s, "patterns", p + ".rx"), "rb").read()
    if pat.endswith(b"\n"): pat = pat[:-1]
    a = ["--features", "all"] + (["-e", "utf8"] if s == "utf8" else []) + ["--pattern-esc", "--pattern", esc(pat)]
    f = os.path.join(out, s + "__" + p)
    r = subprocess.run([pc, "-p", "rx", "-o", f + ".c"] + a, capture_output=True, timeout=300)
    open(f + ".err", "wb").write(r.stderr)
    for mode, ext in (("--emit-facts", ".facts"), ("--emit-ir", ".ir")):
        r2 = subprocess.run([pc, mode] + a, capture_output=True, timeout=300)
        open(f + ext, "wb").write(r2.stdout + r2.stderr)
    print(s, p, "rc=%d" % r.returncode)
