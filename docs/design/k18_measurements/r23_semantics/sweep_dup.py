#!/usr/bin/env python3
import subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
BIN, patfile = sys.argv[1], sys.argv[2]
pats=[l.rstrip("\n") for l in open(patfile) if l.strip() and not l.startswith("#")]
def one(p):
    try:
        r=subprocess.run([BIN,"-p","rx","-o","/dev/stdout","--",p],capture_output=True,timeout=120,
                         env={"PCREC_K18_STATS":"1","PATH":"/usr/bin:/bin"})
    except subprocess.TimeoutExpired: return p,-1,-1,-1
    d=md=nf=0
    for m in re.finditer(rb"K18STATS dup=(\d+) nfa=(\d+) .*?maxdepth=(\d+)", r.stderr):
        d+=int(m.group(1)); nf=max(nf,int(m.group(2))); md=max(md,int(m.group(3)))
    return p,d,md,nf
with ThreadPoolExecutor(max_workers=12) as ex: res=list(ex.map(one,pats))
nd=[r for r in res if r[1]>0]
for p,d,md,nf in sorted(nd,key=lambda t:-t[1])[:15]: print("DUP\t%d\tmaxdepth=%d\tnfa=%d\t%s"%(d,md,nf,p))
over=[r for r in res if r[2] > r[3]+2]
print("== %d patterns: dup>0 on %d; maxdepth>nfa+2 on %d; max maxdepth=%d"
      % (len(res), len(nd), len(over), max((r[2] for r in res), default=0)))
