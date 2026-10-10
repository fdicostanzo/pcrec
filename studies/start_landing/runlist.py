#!/usr/bin/env python3
"""[START-LANDING] the twin run list from the census (STUDY).

    runlist.py CENSUS.tsv POP.tsv [--subjects] [--rows end-minus-width,landing] > RUNLIST.tsv

One line per distinct (pid, config) whose design row is in --rows: name enc
icase cfg pattern_hex row W subjects. --subjects attaches the population's
own subject files (the bench's throughput + search_short subjects).
"""
import sys
cen, pop = sys.argv[1], sys.argv[2]
withsub = "--subjects" in sys.argv
rows = {"end-minus-width", "landing"}
if "--rows" in sys.argv:
    rows = set(sys.argv[sys.argv.index("--rows") + 1].split(","))
pat, subs = {}, {}
for line in open(pop):
    f = line.rstrip("\n").split("\t")
    if f[0] == "pid": continue
    pat[f[0]] = (f[2], f[3], f[4])
    if f[5] in ("throughput", "search_short", "findall", "search"):
        lst = subs.setdefault(f[0], [])
        new = [s for s in f[6].split(",") if s and s not in lst]
        # throughput subjects first (the dense find-all the twin must match
        # call for call), then up to 4 short ones
        if f[5] in ("throughput", "findall"): lst[:0] = new
        else: lst.extend(new[:4])
print("name\tenc\ticase\tcfg\tpattern_hex\trow\tW\tsubjects")
for line in open(cen):
    f = line.rstrip("\n").split("\t")
    if f[0] == "pid" or len(f) < 13 or f[12] not in rows: continue
    enc, icase, ph = pat[f[0]]
    print("\t".join([f[0], enc, icase, f[1], ph, f[12], f[9],
                     ",".join(subs.get(f[0], [])[:8]) if withsub else ""]))
