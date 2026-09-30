#!/usr/bin/env python3
"""[FORM-CHAR2] build every (witness, arm) timing binary + subject files.
Usage: build.py WORKDIR --pcrec BIN --cc CC [--bench DIR]
Arms: fold = default; table = -fno-cls-fold (today's non-fold form: bitmap, or the shared
atom table at >=11 table classes); bitmap = -fno-cls-fold -fno-cls-pack (32B per site).
Prints, per (witness, arm): RX_VM_CLS_FOLDS/_ATOMS stamps, .text, .rodata."""
import argparse, os, re, subprocess, sys, random
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("--pcrec", required=True)
ap.add_argument("--cc", default="gcc"); ap.add_argument("--reuse", action="store_true", help="reuse art/*.c (generated elsewhere; emitted C is byte-identical across boxes)"); ap.add_argument("--bench"); a = ap.parse_args()
if a.bench: os.environ["BENCH_DIR"] = a.bench
import witnesses as WI
ARMS = {"fold": [], "table": ["-fno-cls-fold"], "bitmap": ["-fno-cls-fold", "-fno-cls-pack"]}
for d in ("art", "bin", "subj"): os.makedirs(f"{a.work}/{d}", exist_ok=True)
hay = open(f"{a.work}/subj/hay.bin", "rb").read() if a.reuse else open(os.path.join(WI.BENCH, "capability/throughput/t-256k.bin"), "rb").read()
open(f"{a.work}/subj/hay.bin", "wb").write(hay)
open(f"{a.work}/subj/hot.bin", "wb").write((b"eEeE" * 16 + b" ") * 4000)      # runs of 64 e/E, ~260k
open(f"{a.work}/subj/hotchain.bin", "wb").write((b"eEeEeEeE" * 4 + b" ") * 4000)
def sects(o):
    t = subprocess.run(["objdump", "-h", o], capture_output=True, text=True).stdout; s = {}
    for l in t.splitlines():
        p = l.split()
        if len(p) > 3 and p[0].isdigit() and re.fullmatch(r"[0-9a-f]+", p[2]): s[p[1]] = int(p[2], 16)
    return s
print("witness\tarm\tfolds\tatoms\ttext\trodata\tobj_total")
for w, (pat, eng, msub, note) in WI.W.items():
    open(f"{a.work}/subj/{w}.match", "wb").write(msub)
    base = {"hotloop": (b"eEeE" * 16 + b" ") * 4000, "hotchain": (b"eEeEeEeE" * 4 + b" ") * 4000}.get(w, hay)
    step = 4099 if w not in ("hotloop", "hotchain") else 4160   # find-all subject: the witness's own match text every ~4 KB
    out = bytearray(); i = 0
    while i < len(base):
        out += base[i:i + step]; out += b" " + msub + b" "; i += step
    open(f"{a.work}/subj/{w}.hits", "wb").write(bytes(out))
    for arm, fl in ARMS.items():
        c = f"{a.work}/art/{w}_{arm}.c"; o = f"{a.work}/art/{w}_{arm}.o"; b = f"{a.work}/bin/{w}_{arm}"
        argv = [a.pcrec, "-p", "rx", "--features", "all", *([eng] if eng else []), *fl, "--warn-emit-bytes=0", "-o", c, "--pattern", pat]
        if not (a.reuse and os.path.exists(c)): subprocess.run(argv, check=True, capture_output=True)
        subprocess.run([a.cc, "-O2", "-std=gnu11", "-w", "-c", "-o", o, c], check=True)
        src = open(c).read()
        nf = re.search(r"#define RX_VM_CLS_FOLDS (\d+)", src).group(1); na = re.search(r"#define RX_VM_CLS_ATOMS (\d+)", src).group(1)
        subprocess.run([a.cc, "-O2", "-std=gnu11", "-w", f'-DHDR="{w}_{arm}.h"', f"-I{a.work}/art", "-o", b, f"{here}/drv.c", o], check=True)
        s = sects(o); tx = s.get(".text", s.get("__text", 0)); ro = sum(v for k, v in s.items() if k.startswith(".rodata") or k == "__const")
        print(f"{w}\t{arm}\t{nf}\t{na}\t{tx}\t{ro}\t{os.path.getsize(o)}", flush=True)
