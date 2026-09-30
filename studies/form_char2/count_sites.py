#!/usr/bin/env python3
"""[FORM-CHAR2] (i): static size + instruction counts, fold vs table forms,
from REAL compiler output (the shipped axes select the forms, no hand twins):
  fold   = default                    (x|0x20)==c, no table
  atom   = -fno-cls-fold              shared 256B atom table iff >=11 table classes, else bitmap
  bitmap = -fno-cls-fold -fno-cls-pack  32-byte per-site bitmap
Usage: count_sites.py OUTDIR [--pcrec P] [--cc CC]   -> TSV on stdout
"""
import subprocess, sys, os, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--pcrec"); ap.add_argument("--cc", default="gcc")
ap.add_argument("--bench", default=None); ap.add_argument("--reuse", action="store_true"); a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
pcrec = a.pcrec or os.path.join(here, "../../build/pcrec")
bench = a.bench or os.path.join(here, "../../../pcrec-bench/bench/altwide/patterns/ci-256.rx")
os.makedirs(a.out, exist_ok=True)
letters = "abcdefghijklmnopqrstuvwxyz"
W = {"ci256": (open(bench).read().strip() if os.path.exists(bench) else None),
     "kw5": "(?i)select",
     "kw16": "(?i)" + letters[:16],
     "kw32": "(?i)" + (letters * 2)[:32],
     "kw64": "(?i)" + (letters * 3)[:64]}
FORMS = {"fold": [], "atom": ["-fno-cls-fold"], "bitmap": ["-fno-cls-fold", "-fno-cls-pack"]}
def sect(o):
    t = subprocess.run(["objdump", "-h", o], capture_output=True, text=True).stdout
    s = {}
    for l in t.splitlines():
        p = l.split()
        if len(p) > 3 and re.fullmatch(r"[0-9a-f]+", p[2]) and p[0].isdigit():
            s[p[1]] = int(p[2], 16)
    return s
print("witness\tform\tfold_sites\ttext\trodata\tinstr")
for w, pat in W.items():
    for f, fl in FORMS.items():
        c = f"{a.out}/{w}_{f}.c"; o = f"{a.out}/{w}_{f}.o"
        if not (a.reuse and os.path.exists(c)):
            subprocess.run([pcrec, "-p", "rx", "--engine=vm", *fl, "--warn-emit-bytes=0", "-o", c, "--pattern", pat],
                           check=True, capture_output=True)
        subprocess.run([a.cc, "-O2", "-std=gnu11", "-w", f"-I{a.out}", "-c", "-o", o, c], check=True)
        nf = re.search(r"#define RX_VM_CLS_FOLDS (\d+)", open(c).read()).group(1)
        d = subprocess.run(["objdump", "-d", "--no-show-raw-insn", o], capture_output=True, text=True).stdout
        n = sum(1 for l in d.splitlines() if re.match(r"\s+[0-9a-f]+:", l))
        s = sect(o)
        tx = s.get(".text", s.get("__text", 0))
        ro = sum(v for k, v in s.items() if k in (".rodata", "__const") or k.startswith(".rodata"))
        print(f"{w}\t{f}\t{nf}\t{tx}\t{ro}\t{n}", flush=True)
