#!/usr/bin/env python3
"""Parallel oracle-cost filter: each pattern is exercised in its own python
process with a wall budget, so a catastrophic-backtracking ORACLE cannot hold
the sweep hostage."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
patfile, alpha, maxlen, budget = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
CODE = ("import re,sys\nfrom itertools import product\n"
        "a=sys.argv[1];n=int(sys.argv[2]);p=sys.argv[3]\n"
        "s=['']+[''.join(t) for k in range(1,n+1) for t in product(a,repeat=k)]\n"
        "c=re.compile(p)\n[c.search(x) for x in s]\n")
pats=[l.rstrip("\n") for l in open(patfile) if l.strip()]
def ok(p):
    try:
        r=subprocess.run([sys.executable,"-c",CODE,alpha,maxlen,p],
                         capture_output=True,timeout=float(budget))
        return p if r.returncode==0 else None
    except subprocess.TimeoutExpired:
        return None
with ThreadPoolExecutor(max_workers=12) as ex: res=list(ex.map(ok,pats))
keep=[p for p in res if p]
sys.stderr.write("kept %d of %d\n"%(len(keep),len(pats)))
print("\n".join(keep))
