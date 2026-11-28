#!/usr/bin/env python3
"""Round r114 probe: load predfold1129_model.py up to '# ==== CHECKS129' (no checks run), then run programs.
Usage (from ANY cwd): timeout 600 python3 -I -B probe.py CASEFILE
CASEFILE: blocks separated by a blank line; in each block:
  P: <program expression>
  B: <binding>            (zero or more lines, e.g. B: A := [g = /\\d/])
  T: <text> [<text> ...]  (texts, space-separated; optional)
Prints per block: LEGAL / ERROR <message>, and for each text WHOLE/SEARCHED/FIND-ALL.
Switch: R114_CONTROL=1 runs the control (X129[0] off = predfix113 as merged, the documents' engine BEFORE the fold).
"""
import builtins, os, sys
TREE = "/var/tmp/pcrec-pcrec/scratch/crit-predfold1129/R/tree"
M = os.path.join(TREE, "docs/dev/lanes/predfold1129_evidence/predfold1129_model.py")
src = builtins.open(M, encoding="utf-8").read()
src = src[:src.index("# ==== CHECKS129")]
os.chdir(TREE)
g = {"__file__": M, "__name__": "probe114"}
_out = sys.stdout
sys.stdout = open(os.devnull, "w")
exec(compile(src, M, "exec"), g)
sys.stdout = _out
if os.environ.get("R114_CONTROL") == "1":
    g["X129"][0] = False
run11 = g["run11"]
blocks = builtins.open(sys.argv[1], encoding="utf-8").read().strip().split("\n\n")
for b in blocks:
    P, B, T = None, [], []
    for l in b.splitlines():
        if l.startswith("P:"): P = l[2:].strip()
        elif l.startswith("B:"): B.append(l[2:].strip())
        elif l.startswith("T:"): T += l[2:].split()
    if P is None: continue
    Pg, err = run11(P, B)
    print("PROGRAM %s  BINDS %s" % (P, B))
    if Pg is None:
        print("  ERROR", err); continue
    print("  LEGAL")
    for t in T:
        try:
            r = Pg.search(t)
            print("  %-14s WHOLE %s  SEARCHED %s  FIND-ALL %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS",
                  (r[0], r[1]) if r else None, list(Pg.findall(t))))
        except Exception as e:
            print("  %-14s RUN-CRASH %s %s" % (t, type(e).__name__, str(e)[:100]))
