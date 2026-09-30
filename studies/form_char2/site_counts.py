#!/usr/bin/env python3
"""[FORM-CHAR2] (i) per-site static instruction counts from the built timing artifacts (build.py's art/*.o).
sites = number of `(x | 0x20) == c` tests in the fold arm's emitted C (each is one fold-site instance in the program);
body  = instruction count of the LARGEST function of the object (the program body); total = whole object.
Usage: site_counts.py WORKDIR"""
import re, subprocess, sys, os
w = sys.argv[1]
def fns(o):
    d = subprocess.run(["objdump", "-d", "--no-show-raw-insn", o], capture_output=True, text=True).stdout
    cur = None; cnt = {}
    for l in d.splitlines():
        m = re.match(r"[0-9a-f]+ <(.+)>:", l)
        if m: cur = m.group(1); cnt[cur] = 0; continue
        if cur and re.match(r"\s+[0-9a-f]+:", l): cnt[cur] += 1
    return cnt
names = sorted({f.rsplit("_", 1)[0] for f in os.listdir(f"{w}/art") if f.endswith(".o")})
print("witness\tfold_sites\tarm\tbody_instr\ttotal_instr\tbody_per_site\tdelta_vs_fold_per_site")
for n in names:
    sites = len(re.findall(r"\| 0x20\) == \d+\)", open(f"{w}/art/{n}_fold.c").read()))
    base = None
    for arm in ("fold", "table", "bitmap"):
        c = fns(f"{w}/art/{n}_{arm}.o"); body = max(c.values()); tot = sum(c.values())
        if arm == "fold": base = body
        print(f"{n}\t{sites}\t{arm}\t{body}\t{tot}\t{body/max(sites,1):.2f}\t{(body-base)/max(sites,1):+.2f}")
