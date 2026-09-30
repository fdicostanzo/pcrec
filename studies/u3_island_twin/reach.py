#!/usr/bin/env python3
"""reach.py -- REACH of the correctness set on the twins' island code: how
often each case's kit4 twin enters an island, meets an ill-formed byte, and
back-steps.  A green differential over a population that never reaches the
code proves nothing (learnings.md s3, MECH-REACH)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CASES = sys.argv[1:] or ["c1", "c3", "nd", "l", "xwd", "x1", "x2", "x3"]
rows = []
for c in CASES:
    d = os.path.join(OUT, c)
    src = open(os.path.join(d, "tw_kit4.c")).read()
    drv = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
extern int ia_search(const unsigned char*, size_t, size_t, ptrdiff_t (*)[2]);
extern unsigned long ia_cnt[4];
int main(int argc, char **argv){ FILE *f=fopen(argv[1],"rb"); uint32_t ns; fread(&ns,4,1,f);
 unsigned char **s=malloc(ns*sizeof*s); uint32_t *l=malloc(ns*4);
 for(uint32_t i=0;i<ns;i++){fread(&l[i],4,1,f); s[i]=malloc(l[i]+1); fread(s[i],1,l[i],f);}
 FILE *c=fopen(argv[2],"r"); unsigned i,fr; unsigned long n=0;
 while(fscanf(c,"%u\t%u\n",&i,&fr)==2){ ptrdiff_t caps[1][2]; ia_search(s[i],l[i],fr,caps); n++; }
 printf("%lu\t%lu\t%lu\t%lu\t%lu\n", n, ia_cnt[0], ia_cnt[1], ia_cnt[2], ia_cnt[3]); return 0; }
'''
    open(os.path.join(d, "reach_drv.c"), "w").write(drv)
    exe = os.path.join(d, "reach_exe")
    subprocess.check_call(["gcc-16", "-O1", "-w", "-DU3_COUNT", os.path.join(d, "reach_drv.c"),
                           os.path.join(d, "tw_kit4.c"), "-o", exe])
    out = subprocess.check_output([exe, os.path.join(OUT, "subjects.bin"), os.path.join(OUT, "cases.tsv")], text=True).split()
    rows.append([c] + out)
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
with open(os.path.join(HERE, "results", "reach.tsv"), "w") as f:
    f.write("case\tsearch_calls\tfwd_island_entries\tfwd_BOT_decodes\trev_island_entries\trev_BOT_backsteps\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print(open(os.path.join(HERE, "results", "reach.tsv")).read())
