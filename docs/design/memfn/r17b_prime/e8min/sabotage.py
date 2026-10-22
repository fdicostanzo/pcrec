#!/usr/bin/env python3
"""e8min/sabotage.py SCRATCH_DIR -- verdict.py's sabotage pair, on a SYNTHETIC cells table (no clock was read):
  baseline         every anchor reads R at grid2's magnitude, 76 J1 cells (the census's 19 movers x 4 subjects) read W/N
                   -> must PASS (the table is sound, so a REFUTED below is the plant's)
  planted UNLISTED a J1 cell reads R with a sparse, irregular landing profile (gap 1000 B)   -> must REFUTE
  planted LISTED   a J1 cell reads R with a dense, regular profile (gap 4 B, 0.01 misses/match) -> must NOT refute
  planted INVALID  an anchor (EL1) reads N: the positive control failed                       -> must read INVALID
Writes the three tables under SCRATCH_DIR and runs verdict.py on each; exit 0 iff all four expectations hold."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict  # noqa: E402
from readslot import COLS  # noqa: E402

exp = verdict.expected_list(os.path.join(HERE, "../b4prep/expected_losses.md"))
movers = sorted({ln.rstrip("\n").split("\t")[12] for ln in open(os.path.join(HERE, "j1_census.tsv"))
                 if not ln.startswith("#") and ln.split("\t")[7] == "1"})


def row(**kw):
    d = dict(set="J1", cell="", id="", subject="", nbytes=1 << 20, shape="r1e0c0", walk_ns=1000000.0, v1_ns=900000.0,
             floor_ns=3000.0, aac_ns=2000.0, delta_pct=-10.0, verdict="W", nullb="N", matches=5000, misses_pass="-", suspect=0)
    d.update(kw)
    return d


def table():
    rows = []
    for (fam, subj), (i, pct, line) in exp.items():
        rows.append(row(set="AN", cell="an-" + fam, id=i, subject=subj, nbytes=65536, shape="-", walk_ns=10000.0,
                        v1_ns=10000.0 * (1 + pct / 100), floor_ns=100.0, delta_pct=pct, verdict="R"))
    for i, fam, subj, pct in verdict.LOSER_CONTROLS:
        rows.append(row(set="AN", cell="an-" + fam, id=i, subject=subj, nbytes=1 << 20, shape="-", walk_ns=200000.0,
                        v1_ns=200000.0 * (1 + pct / 100), floor_ns=150.0, delta_pct=pct, verdict="R"))
    for q in movers:
        for k in range(4):
            win = k == 0
            rows.append(row(cell="j1-" + q, id=q, subject="c__f%d" % k, v1_ns=900000.0 if win else 1000500.0,
                            delta_pct=-10.0 if win else 0.05, verdict="W" if win else "N"))
    return rows


def write(path, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in COLS) + "\n")


def run(name, rows, want):
    p = os.path.join(sys.argv[1], name + ".tsv")
    write(p, rows)
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "verdict.py"), p,
                        os.path.join(HERE, "../b4prep/expected_losses.md"), os.path.join(HERE, "j1_census.tsv")],
                       capture_output=True, text=True)
    last = [ln for ln in r.stdout.splitlines() if ln.startswith("E8 VERDICT")][-1]
    keep = [ln for ln in r.stdout.splitlines() if "UNLISTED" in ln or "LISTED(rule)" in ln or "REFUTED" in ln
            or "INVALID" in ln or "REVISIT" in ln]
    print("--- %s (want %s)" % (name, want))
    for ln in keep:
        print(ln)
    print(last)
    return last.endswith(want)


base = table()
ok = run("baseline", base, "PASS")
t = table()
t[-1].update(verdict="R", delta_pct=8.0, v1_ns=1080000.0, nbytes=1000000, matches=1000, misses_pass="900.00")
ok &= run("planted_unlisted", t, "REFUTED")
t = table()
t[-1].update(verdict="R", delta_pct=8.0, v1_ns=1080000.0, nbytes=1000000, matches=250000, misses_pass="2500.00")
ok &= run("planted_listed", t, "PASS")
t = table()
i = next(k for k, r in enumerate(t) if r["id"] == "EL1")
t[i].update(verdict="N", delta_pct=0.1)
ok &= run("planted_invalid", t, "INVALID")
print("sabotage pair: " + ("ALL FOUR EXPECTATIONS HOLD" if ok else "FAILED"))
sys.exit(0 if ok else 1)
