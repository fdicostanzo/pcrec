#!/usr/bin/env python3
r"""lane sar1fix's TIE CENSUS (review 2026-11-09 r5, rulings R1): every
`--emit-facts=byte,utf8` row of REF (the tree before the fix, f7809e83a =
lane/sae1 merged into lane/sar1) against NEW (the fixed tree), over the
corpus and the bench patterns (census_r1.py's population and reader).

Counts, per encoding, the texts whose `req_whole_run` moved and how many of
them moved its INFORMATION (`Σ popcount` of the masks; a tie broken another
way keeps it, a different tie upstream of a join can change it), and the
texts where only other facts moved. `utf8` compiles under the byte-rate's
NONE answer, so its count is rulings R1's "the NONE value equals today's
core value on the corpus (count, not assumption)".

With `--census DIR` (census_r1.py's output for the R1 model, REF = lane/sae1)
it also reconciles: every R1 census difference (OBS-NOT-PRED, PRED-NOT-OBS,
VALUE) must be a text this census saw move, i.e. explained by the fix.

usage: tiecensus.py REF NEW TREE BENCH OUT_DIR [--census DIR] [--jobs N]
"""
import concurrent.futures as cf
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sar1_evidence"))
import census_r1 as C  # noqa: E402


def main():
    a = sys.argv[1:]
    jobs, cdir = 8, None
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    if "--census" in a:
        k = a.index("--census"); cdir = a[k + 1]; del a[k:k + 2]
    ref, new, tree, bdir, out = a
    os.makedirs(out, exist_ok=True)
    seen = {}
    for src, pat in C.corpus(new, tree) + C.bench(bdir):
        seen.setdefault(pat, src)

    def one(it):
        pat, src = it
        return src, pat, C.facts(ref, pat), C.facts(new, pat)

    with cf.ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, seen.items()))

    def esc(b):
        return b.decode("latin-1").encode("unicode_escape").decode()

    def val(rows, e):
        return (rows.get((e, "req_whole_run")) or [None] * 8)[6]

    comp = [(s, p, r0, r1) for s, p, r0, r1 in res if r0 is not None and r1 is not None]
    movers = {}
    run_mv = {"byte": [], "utf8": []}
    info_mv = {"byte": [], "utf8": []}
    other = []
    valmv = set()
    for s, p, r0, r1 in comp:
        moved = sorted({k[1] for k in set(r0) | set(r1)
                        if (r0.get(k) or [None] * 8)[6:8] != (r1.get(k) or [None] * 8)[6:8]})
        if not moved:
            continue
        movers[p] = (s, moved)
        if any((r0.get(k) or [None] * 8)[6] != (r1.get(k) or [None] * 8)[6] for k in set(r0) | set(r1)):
            valmv.add(p)
        for e in ("byte", "utf8"):
            x, y = val(r0, e), val(r1, e)
            if x != y:
                run_mv[e].append((s, p, x, y))
                if C.info(x) != C.info(y):
                    info_mv[e].append((s, p, x, y))
        if "req_whole_run" not in moved:
            other.append((s, p, moved))
    lines = [
        "population: %d distinct texts, %d compiled on both sides" % (len(seen), len(comp)),
        "texts with a moved fact value or why: %d (a moved VALUE: %d; the rest moved only a why,"
        " `req_whole_run`'s now the rate rule's)" % (len(movers), len(valmv)),
    ]
    for e in ("byte", "utf8"):
        lines.append("req_whole_run movers [%s]: %d (information moved: %d)" % (e, len(run_mv[e]), len(info_mv[e])))
    lines.append("NONE (utf8) req_whole_run equal to the tree before the fix: %d of %d compiled texts"
                 % (len(comp) - len(run_mv["utf8"]), len(comp)))
    lines.append("texts where only other facts moved: %d" % len(other))
    unexpl = []
    if cdir:
        csum = open(os.path.join(cdir, "summary.txt"), encoding="utf-8").read().splitlines()
        # R1's own exact-repeat pieces movers: the census lists them as PIECES (the design predicts them,
        # span_arms T2 row 2) and the fix does not touch them, so they are not the fix's to explain
        pieces = {l.split(None, 2)[2] for l in csum if l.startswith("  PIECES ")}
        for l in csum:
            t = l.rstrip("\n").split(None, 2)
            if len(t) >= 3 and t[0] in ("OBS-NOT-PRED", "PRED-NOT-OBS", "VALUE"):
                if re.sub(r" (moved|work)=.*$", "", t[2]) in pieces and " moved=req_pieces " in t[2]:
                    continue
                # the pattern text may hold spaces: it is the rest after the source, up to " moved="
                pat = re.sub(r" (moved|work)=.*$", "", t[2])
                if pat not in {esc(p) for p in movers}:
                    unexpl.append(l.rstrip("\n"))
        lines.append("R1 census differences not explained by a fix mover: %d" % len(unexpl))
        lines += ["  UNEXPLAINED " + u for u in unexpl]
    for e in ("byte", "utf8"):
        for s, p, x, y in run_mv[e]:
            lines.append("  RUN[%s]%s %s %s %s -> %s" % (e, "+INFO" if (s, p, x, y) in info_mv[e] else "", s, esc(p), x, y))
    for s, p, m in other:
        lines.append("  OTHER %s %s moved=%s" % (s, esc(p), ",".join(m)))
    lines.append("== tiecensus COMPLETE: %d movers, %d unexplained census differences" % (len(movers), len(unexpl)))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    with open(os.path.join(out, "census.tsv"), "w") as h:
        h.write("#src\tpattern\tmoved_facts\n")
        for p, (s, m) in sorted(movers.items(), key=lambda x: x[1][0]):
            h.write("%s\t%s\t%s\n" % (s, esc(p), ",".join(m)))
    print("\n".join(l for l in lines if not l.startswith("  RUN") and not l.startswith("  OTHER")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
