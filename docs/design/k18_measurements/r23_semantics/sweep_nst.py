#!/usr/bin/env python3
"""Re-measure §2a's 'the open loop is always the STACK TOP' claim
(nonstacktop == 0) on corpora the note did not use."""
import subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
BIN=sys.argv[1]
pats=[]
for f in sys.argv[2:]:
    pats += [l.rstrip("\n") for l in open(f) if l.strip() and not l.startswith("#")]
pats=list(dict.fromkeys(pats))
def one(p):
    try:
        r=subprocess.run([BIN,"-p","rx","-o","/dev/stdout","--",p],capture_output=True,
                         timeout=180,env={"PCREC_K18_STATS":"1","PATH":"/usr/bin:/bin"})
    except subprocess.TimeoutExpired: return p,-1,0,0
    nst=red=md=0
    for m in re.finditer(rb"redirects=(\d+) nonstacktop=(\d+) maxdepth=(\d+)", r.stderr):
        red+=int(m.group(1)); nst+=int(m.group(2)); md=max(md,int(m.group(3)))
    return p,nst,red,md
with ThreadPoolExecutor(max_workers=12) as ex: res=list(ex.map(one,pats))
bad=[r for r in res if r[1]>0]
for p,n,red,md in bad[:20]: print("NONSTACKTOP\t%d\tredirects=%d\tmaxdepth=%d\t%s"%(n,red,md,p))
print("== %d patterns; nonstacktop>0 on %d; total redirects %d; max depth %d; timeouts %d"
      % (len(res), len(bad), sum(r[2] for r in res), max(r[3] for r in res),
         sum(1 for r in res if r[1]==-1)))
