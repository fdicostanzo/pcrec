#!/usr/bin/env python3
"""Sweep the A2-SHADOW detector: which patterns have a redirect verdict that
DIFFERS between the correct open-stack and prototype A2's no-restore one."""
import subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
BIN = sys.argv[1]; patfile = sys.argv[2]
pats = [l.rstrip("\n") for l in open(patfile) if l.strip() and not l.startswith("#")]
def one(p):
    try:
        r = subprocess.run([BIN, "-p", "rx", "-o", "/dev/stdout", "--", p],
                           capture_output=True, timeout=120,
                           env={"PCREC_K18_STATS": "1", "PATH": "/usr/bin:/bin"})
    except subprocess.TimeoutExpired:
        return p, -1, -1, -1
    sd = cd = cb = 0
    for m in re.finditer(rb"K18STATS scandiff=(\d+) ctxdiff=(\d+) clobber=(\d+)", r.stderr):
        sd += int(m.group(1)); cd += int(m.group(2)); cb += int(m.group(3))
    return p, sd, cd, cb
with ThreadPoolExecutor(max_workers=12) as ex:
    res = list(ex.map(one, pats))
nsd = sum(1 for _,s,_,_ in res if s > 0)
ncd = sum(1 for _,_,c,_ in res if c > 0)
ncb = sum(1 for _,_,_,b in res if b > 0)
for p,s,c,b in sorted(res, key=lambda t:-t[1])[:40]:
    if s > 0: print("SCANDIFF\t%d\tctxdiff=%d\tclobber=%d\t%s" % (s,c,b,p))
print("== %d patterns: scandiff>0 on %d, ctxdiff>0 on %d, clobber>0 on %d"
      % (len(res), nsd, ncd, ncb))
