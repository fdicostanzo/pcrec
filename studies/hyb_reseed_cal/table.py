#!/usr/bin/env python3
"""studies/hyb_reseed_cal/table.py — one row of the base / new / deny table.

usage: table.py NAME PATTERN ENC SUBJECT.bin...
env:   PCREC_BASE  the branch-point compiler (abi 46; build it from
                   `git archive` of the branch point, never a checkout)
       PCREC_NEW   the compiler under test
       CC          default gcc-16;  LAUNCHES  default 5;  REPS  default 5

Compiles NAME three ways (base; new; new with -fno-hyb-reseed), links each
with drv.c at -O2, then for each subject launches the three binaries
round-robin LAUNCHES times (REPS passes per launch) and prints one markdown
row: the median of the per-launch medians, ns per subject byte, for each,
plus base/new. `answers` is `same` iff all three agree on the match count
and the hash of every span.

THE NOISE FLOOR IS IN THE ROW: base and deny are byte-identical programs
(the identity sweep proves it), so |base/deny - 1| is what this box's noise
reads on that subject, and a base/new ratio inside it is a null result.
"""
import os, statistics, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
name, pat, enc = sys.argv[1:4]
subs = sys.argv[4:]
base, new = os.environ["PCREC_BASE"], os.environ["PCREC_NEW"]
cc = os.environ.get("CC", "gcc-16")
launches = int(os.environ.get("LAUNCHES", "5")); reps = os.environ.get("REPS", "5")
eo = ["-e", "utf8"] if enc == "utf8" else []


def comp(binp, out, extra=()):
    subprocess.run([binp, "--features", "all", "-p", "rx"] + eo + list(extra) + ["-o", out, "--pattern", pat], check=True)


comp(base, f"{name}_base.c"); comp(new, f"{name}_new.c"); comp(new, f"{name}_deny.c", ["-fno-hyb-reseed"])
row = [l.split()[2] for l in open(f"{name}_new.c") if l.startswith("#define RX_VM_RESEED")]
row = row[0].strip('"') if row else "-"
for v in ("base", "new", "deny"):
    subprocess.run([cc, "-O2", "-o", f"{name}_{v}", f"{name}_{v}.c", os.path.join(here, "drv.c")], check=True)
for s in subs:
    t = {v: [] for v in ("base", "new", "deny")}; a = {}
    for _ in range(launches):
        for v in ("base", "new", "deny"):
            o = subprocess.run([f"./{name}_{v}", s, reps], capture_output=True, text=True).stdout.strip()
            a[v] = o.split(" med")[0]; t[v].append(float(o.split("med_ns_per_B=")[1].split()[0]))
    m = {v: statistics.median(t[v]) for v in t}
    same = "same" if a["base"] == a["new"] == a["deny"] else "DIFF"
    print(f"| {name} | {row} | {os.path.basename(s)[:-4]} | {a['base'].split()[0][8:]} | {same} "
          f"| {m['base']:.3f} | {m['new']:.3f} | {m['deny']:.3f} | x{m['base']/m['deny']:.2f} | x{m['base']/m['new']:.2f} |", flush=True)
