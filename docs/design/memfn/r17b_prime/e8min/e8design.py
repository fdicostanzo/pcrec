#!/usr/bin/env python3
"""e8min/e8design.py -- the window's cell design, from the census and the corpus (no clock, no build).

  e8design.py plan                 one line per cell: kind, cell, subject-name, source (path), qid-or-fam
  e8design.py arms OUT             the ext arm table (cell arm role subjects modes) for grid1's arms.py

J1 cells: every census mover (mover=1, any site) x every corpus file >= 1 MiB of the question's class
(worktrees/.corpus/<class>/, not raw/), mode all only. Anchor cells: the subjects of expected_losses.md's EL and SS
rows (verdict.expected_list, the one parse of that file) and the two >= 3-term losers, on grid2's own subjects.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict  # noqa: E402

CORPUS = "/home/pcrec/projects/pcrec/worktrees/.corpus"
MIB = 1 << 20


def movers():
    q = {}
    for ln in open(os.path.join(HERE, "j1_census.tsv"), encoding="utf-8"):
        f = ln.rstrip("\n").split("\t")
        if not ln.startswith("#") and f[7] == "1":
            q[f[12]] = 1
    return sorted(q)


def classes():
    c = {}
    rows = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(HERE, "../../../../dev/lanes/rwquest/questions.tsv"))]
    for r in rows[1:]:
        c[r[0]] = r[1]
    return c


def files_of(cls):
    d = os.path.join(CORPUS, cls)
    return sorted(f for f in os.listdir(d)
                  if os.path.isfile(os.path.join(d, f)) and os.path.getsize(os.path.join(d, f)) >= MIB)


def plan():
    out, cls = [], classes()
    for q in movers():
        for f in files_of(cls[q]):
            out.append(("J1", "j1-" + q, "%s__%s" % (cls[q], f), os.path.join(CORPUS, cls[q], f), q))
    exp = verdict.expected_list(os.path.join(HERE, "../b4prep/expected_losses.md"))
    for (fam, subj), (i, _p, _l) in sorted(exp.items(), key=lambda kv: kv[1][0]):
        out.append(("AN", "an-" + fam, subj, subj, fam))
    for i, fam, subj, _p in verdict.LOSER_CONTROLS:
        out.append(("AN", "an-" + fam, subj, subj, fam))
    return out


def main():
    if sys.argv[1] == "plan":
        for r in plan():
            print("\t".join(r))
    elif sys.argv[1] == "arms":
        by = {}
        for kind, cell, subj, _src, _q in plan():
            by.setdefault(cell, []).append(subj)
        print("# e8min's ext arm table (e8design.py arms): cell arm role subjects modes")
        for cell in sorted(by):
            s = ",".join(by[cell])
            for arm, role in (("walk", "base"), ("V1", "arm")):
                print("%s\t%s\t%s\t%s\tall" % (cell, arm, role, s))
    else:
        sys.exit("usage: e8design.py plan | arms OUT")


if __name__ == "__main__":
    main()
