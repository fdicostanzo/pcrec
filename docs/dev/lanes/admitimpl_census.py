#!/usr/bin/env python3
# docs/dev/lanes/admitimpl_census.py -- [OPT-PRECHECK-ADMIT]'s MOVERS CENSUS
# (lane admitimpl, 2026-09-23), the committed reproduction piece for
# admitimpl_report.md section 2.  w4_modesweep.py's precedent: a lane's
# acceptance instrument is committed beside its report rather than left in a
# scratchpad, so the next reader re-derives nothing.
#
#   python3 docs/dev/lanes/admitimpl_census.py feat --features all
#   python3 docs/dev/lanes/admitimpl_census.py utf8 --features all -e utf8
#   python3 docs/dev/lanes/admitimpl_census.py dflt
#
# It needs a REFERENCE compiler built from the branch point at
# build/ref/build/pcrep and the tree's own at build/pcrec, and it writes both
# sides to the SAME -o basename in two directories -- the house's recorded
# basename trap, which reports a false difference on the #include line
# otherwise.  Its real work is the CLASSIFIER: every changed line of every
# mover is matched against the pre-check's own emitted text, and a line it
# cannot account for is printed rather than counted, which is how the first
# run's 112 "unexplained" removals turned out to be one missing alternative.
import subprocess, sys, os, re, glob, json, collections, difflib
ROOT="/Users/fdicostanzo/pcrec/worktrees/admitimpl"
REF=ROOT+"/build/ref/build/pcrec"; TIP=ROOT+"/build/pcrec"
tag=sys.argv[1]; extra=sys.argv[2:]
pats=[]
for f in sorted(glob.glob(ROOT+"/tests/**/*.rxt", recursive=True)):
    for line in open(f, errors="replace"):
        if line.startswith("pattern "): pats.append(line[8:].rstrip("\n"))
pats=list(dict.fromkeys(pats))
dA=ROOT+"/build/c2A_"+tag; dB=ROOT+"/build/c2B_"+tag
os.makedirs(dA,exist_ok=True); os.makedirs(dB,exist_ok=True)
def emit(binp,d,pat):
    r=subprocess.run([binp,"-p","rx","-o",d+"/o.c","--pattern",pat]+extra,capture_output=True,timeout=120)
    return open(d+"/o.c",errors="replace").read() if r.returncode==0 else None
def st(t,n):
    m=re.search(r'#define RX_%s "([^"]*)"'%n,t); return m.group(1) if m else None
both=0; refb=0; mism=0; movers=[]; why=collections.Counter(); clsc=collections.Counter()
for p in pats:
    try: a=emit(REF,dA,p); b=emit(TIP,dB,p)
    except subprocess.TimeoutExpired: continue
    if a is None and b is None: refb+=1; continue
    if a is None or b is None: mism+=1; continue
    both+=1
    ta=a.replace("(abi 30)","(abi X)").replace(".abi = 30",".abi = X")
    tb=b.replace("(abi 31)","(abi X)").replace(".abi = 31",".abi = X")
    tb=re.sub(r'#define RX_REQ_WHY "[^"]*"\n','',tb)
    if ta==tb: continue
    w=st(b,"REQ_WHY"); why[w]+=1
    # classify every changed line
    al=ta.splitlines(); bl=tb.splitlines()
    removed=[];added=[]
    for line in difflib.unified_diff(al,bl,n=0,lineterm=""):
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"): continue
        if line.startswith("-"): removed.append(line[1:])
        elif line.startswith("+"): added.append(line[1:])
    ok_rem=re.compile(r'^\s*(/\* \[OPT-REQ|\* |if \(subject_length <= search_from|!memchr\(subject \+ search_from|return 0;|#include <string\.h>|#define RX_REQ_(BYTE|RUN|WHY) "|\{|\}|size_t rp_pos|for \(;;\)|const void \*rp_q|if \(!rp_q\)|size_t rp_c|if \(rp_c|&& !memcmp|rp_pos = rp_c|rp_c = \(size_t\)|if \(rp_pos >=|\*/)')
    bad_rem=[l for l in removed if not ok_rem.match(l.strip()) and not ok_rem.match(l)]
    bad_add=[l for l in added if l.strip()]
    cls = "clean" if (not bad_rem and not bad_add) else "OTHER"
    clsc[cls]+=1
    movers.append((w,cls,p,len(a),len(b),bad_rem[:3],bad_add[:3]))
print(json.dumps({"tag":tag,"extra":extra,"patterns":len(pats),"compiled_both":both,
 "refused_both":refb,"refusal_mismatch":mism,"movers":len(movers),
 "by_why":dict(why),"by_class":dict(clsc)}))
with open(ROOT+"/build/census2_%s.tsv"%tag,"w") as f:
    for m in movers: f.write("\t".join(str(x) for x in m)+"\n")
