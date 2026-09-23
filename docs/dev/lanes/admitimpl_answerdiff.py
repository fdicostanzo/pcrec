#!/usr/bin/env python3
# docs/dev/lanes/admitimpl_answerdiff.py -- [OPT-PRECHECK-ADMIT]'s REF-vs-TIP
# ANSWER differential (lane admitimpl, 2026-09-23), the committed reproduction
# piece for admitimpl_report.md section 5.1 item 1.
#
#   CC=gcc-16 ADIFF_CAP=120 python3 docs/dev/lanes/admitimpl_answerdiff.py feat --features all
#
# Reads the census's own TSV (admitimpl_census.py, same directory) for the
# DECLINING population, builds each pattern's --emit-main artifact with BOTH
# compilers, and compares answers cell for cell.  Read the docstring on
# answers(): the first build of this differential fed the subject on STDIN,
# both sides printed their own usage line WITH THEIR OWN PATH IN IT, and all
# 240 sampled patterns read as differing on all 25 subjects -- a comparison
# whose difference was the filename.
"""REF-vs-TIP ANSWER differential over the DECLINING population.

For every pattern whose artifact loses its pre-check, compile the reference
(main) and the tip artifact with --emit-main and compare find-all answers over
a generated subject set at EVERY startpos.  The subjects are built so that the
declined pre-check's own byte is sometimes absent and sometimes present, which
is the only axis on which the two artifacts could differ.
"""
import subprocess, sys, os, re, json, collections
ROOT="/Users/fdicostanzo/pcrec/worktrees/admitimpl"
REF=ROOT+"/build/ref/build/pcrec"; TIP=ROOT+"/build/pcrec"
CC=os.environ.get("CC","gcc-16")
tag=sys.argv[1]; extra=sys.argv[2:]
tsv=ROOT+"/build/census2_%s.tsv"%tag
rows=[l.rstrip("\n").split("\t") for l in open(tsv)]
pats=[(r[0],r[2]) for r in rows if r[1]=="clean"]
# STRATIFIED SAMPLE, cap per why-class: this is a gcc-bound differential
# (2 builds + 26 runs per pattern) and the population is ~1,100.  Sampling is
# EVERY Nth row of each class rather than the head, so the sample is not the
# corpus's own alphabetical prefix.
CAP=int(os.environ.get("ADIFF_CAP","120"))
byw=collections.defaultdict(list)
for w,q in pats: byw[w].append(q)
sample=[]
for w,qs in byw.items():
    step=max(1,len(qs)//CAP)
    sample += [(w,q) for q in qs[::step]][:CAP]
pats=sample
work=ROOT+"/build/adiff_"+tag; os.makedirs(work,exist_ok=True)

SUBJECTS=[b"", b"a", b"abc", b"foo", b"xfoox", b"aaab", b"ab"*8,
          b"Q1x", b"x1Q", b"[", b"]", b"[[]]", b"A:\\x\\y",
          b"zz.tar.gz", b"q", b"user@host", b"/user", b"/users",
          b"ERROR: x", b"\n^abc$\n", b"\xc3\xa9@", b"\xff\xfe",
          b"The quick brown fox", b"a"*40, b"0123456789"*3]

def build(binp, out, pat):
    r=subprocess.run([binp,"-p","rx","--emit-main","-o",out+".c","--pattern",pat]+extra,
                     capture_output=True,timeout=120)
    if r.returncode!=0: return False
    r=subprocess.run([CC,"-O1","-o",out,out+".c"],capture_output=True,timeout=180)
    return r.returncode==0

def answers(exe):
    """The emitted --emit-main program takes the subject in ARGV, not on stdin.
    The first build of this differential fed stdin, both sides printed their own
    usage line WITH THEIR OWN PATH IN IT, and all 240 sampled patterns read as
    differing on all 25 subjects -- a comparison whose difference is the
    filename, this house's recorded trap in a new place.  The exe basename is
    also normalised out of stderr, belt and braces."""
    out=[]
    base=os.path.basename(exe)
    for s in SUBJECTS:
        r=subprocess.run([exe, s],capture_output=True,timeout=60)
        norm=lambda b: b.replace(exe.encode(),b"<EXE>").replace(base.encode(),b"<EXE>")
        out.append((r.returncode, norm(r.stdout), norm(r.stderr)))
    return out

ok=0; diff=0; skipped=0; bad=[]
for why,pat in pats:
    a=work+"/ref"; b=work+"/tip"
    try:
        if not build(REF,a,pat) or not build(TIP,b,pat): skipped+=1; continue
        ra=answers(a); rb=answers(b)
    except subprocess.TimeoutExpired: skipped+=1; continue
    if ra==rb: ok+=1
    else:
        diff+=1
        bad.append((why,pat,[i for i,(x,y) in enumerate(zip(ra,rb)) if x!=y]))
print(json.dumps({"tag":tag,"declining_patterns":len(pats),"identical":ok,
  "differing":diff,"skipped":skipped,"subjects_per_pattern":len(SUBJECTS),
  "cells":ok*len(SUBJECTS)}))
for x in bad[:20]: print("DIFF", x)
