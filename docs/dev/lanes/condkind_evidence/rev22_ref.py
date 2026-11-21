# condkind: REV 22's own answers, dumped as a reference table for condkind_model.py (lane condkind, 2026-11-16;
# design only, an EXPLORATION). Nothing here is new semantics: predspec21_check.py (rev 21/22's engine, THE RULE =
# "MANAGER") is exec'd VERBATIM with its output suppressed, exactly as predspec22_check.py does, and its own pools and
# condition codings are evaluated for every program of 1-3 LEGAL rev 22 conditions (a condition whose name starts with
# `!` is a rev 22 compile ERROR, **not-is-complement**, and is left out).
#
# Output: one TSV line per (pool, program, subject): pool \t program (condition names joined by " & ", in the pool's
# index order) \t subject \t 1|0. Written to the path given as argv[1].
# Run from the scratch dir: `timeout 300 python3 -I /abs/path/docs/dev/lanes/condkind_evidence/rev22_ref.py OUT.tsv`.
import contextlib, io, itertools, os, sys

LANES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
__file__ = os.path.join(LANES, "predspec21_check.py")     # the exec'd script reads its siblings by its own path
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    exec(open(os.path.join(LANES, "predspec21_check.py")).read(), globals())
out = open(sys.argv[1], "w")
nprog = 0
for pname, pat, pop, recs, pool in POOLS:
    legal = [i for i, (nm, f) in enumerate(pool) if not nm.startswith("!")]
    vrec = (lambda recs: lambda s, lab: [recs[s][lab]] if recs[s][lab] is not None else [])(recs)
    for n in (1, 2, 3):
        for combo in itertools.combinations(legal, n):
            facs = [Fac(pool[i][1].names, (lambda f, recs=recs: (lambda s, Dm: f.fn(recs[s], Dm)))(pool[i][1]),
                        marks=pool[i][1].marks, negmark=pool[i][1].negmark) for i in combo]
            a = answers(pop, ["h", "k"], vrec, facs, "MANAGER")[0]
            nprog += 1
            name = " & ".join(pool[i][0] for i in combo)
            for s in pop:
                out.write("%s\t%s\t%s\t%d\n" % (pname, name, s, int(a[s])))
# the LST pool's codings read the global PS, which predspec21_check.py reuses for another table after (1c): rebuild it
# here exactly as (1c) built it (the passes read item by item from the engine)
PS = {s: [(g["h"], g["m"]) for g in (groups(ITM, x + ",", ["h", "m"]) for x in s.split(",")[:-1])] for s in POPL}
legal = [i for i, (nm, f) in enumerate(poolL) if not nm.startswith("!")]
for n in (1, 2, 3):
    for combo in itertools.combinations(legal, n):
        a = answers(POPL, ["m"], vL, [poolL[i][1] for i in combo], "MANAGER")[0]
        nprog += 1
        name = " & ".join(poolL[i][0] for i in combo)
        for s in POPL:
            out.write("LST\t%s\t%s\t%d\n" % (name, s, int(a[s])))
out.close()
print("rev22_ref: predspec21_check.py exec'd verbatim (%s); %d programs written to %s" % (
    [l for l in _buf.getvalue().splitlines() if l.startswith("TOTAL")][0], nprog, sys.argv[1]))
