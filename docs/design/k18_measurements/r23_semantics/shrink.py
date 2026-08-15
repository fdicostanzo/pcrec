#!/usr/bin/env python3
"""Shrink a pattern while keeping 'A2 much slower than base'."""
import subprocess, sys, time, re
BASE="protos/base/build/pcrec"; A2="protos/a2/build/pcrec"
def t(b, p, lim):
    s=time.time()
    try:
        r=subprocess.run([b,"-p","rx","-o","/dev/null.c" if False else "sh_%s.c"%("b" if b==BASE else "a"),"--",p],
                         capture_output=True,timeout=lim)
    except subprocess.TimeoutExpired: return lim, False
    return time.time()-s, r.returncode==0
def interesting(p):
    tb, okb = t(BASE, p, 20)
    if not okb or tb > 2.0: return False
    ta, oka = t(A2, p, 30)
    return (ta > 15 * max(tb, 0.12)) and ta > 2.0
P = sys.argv[1]
assert interesting(P), "seed not interesting"
changed=True
while changed:
    changed=False
    # try deleting bracketed groups / quantifiers / alternation arms
    cands=set()
    for m in re.finditer(r"\{\d+,\d+\}\??|\{\d+,\}\??|\*\??|\+\??|\?\??", P):
        cands.add(P[:m.start()]+P[m.end():])
    for m in re.finditer(r"\|", P):
        # drop an arm: crude, split top-level-ish
        pass
    for m in re.finditer(r"\((\?:)?", P):
        # try removing the group's parens by matching
        i=m.start(); d=0
        for j in range(i, len(P)):
            if P[j]=="(": d+=1
            elif P[j]==")":
                d-=1
                if d==0:
                    inner=P[m.end():j]
                    cands.add(P[:i]+inner+P[j+1:]); cands.add(P[:i]+P[j+1:])
                    break
    for c in sorted(cands, key=len):
        if not c or c==P: continue
        try:
            if interesting(c): P=c; changed=True; print("shrunk ->", P, flush=True); break
        except Exception: pass
print("FINAL", P)
