#!/usr/bin/env python3
"""s3012tri evidence (one-shot, run by no suite): for every runner plant id that
shares an id with a tests/mech/sabotages row, does the mech row's SAB_SUITES still
name the runner's own arm, and does the row record a RE-AIM / a retired detector?
A twin whose mech row moved its detector away from the runner is S3012's shape.
Usage: python3 -I twin_detector_census.py ROOT"""
import os, re, subprocess, sys
root = sys.argv[1]
RUNNERS = {  # runner -> the mech arm names that ARE this runner
    "memfn/tests/run_g2_pres.sh": {"g2pres", "g2pres-asan"},  # -asan: the same runner, ASan plants
    "memfn/tests/run_g2_win.sh": {"g2win"},
    "tests/memfn/run_proof.sh": {"memfnfinder"},  # run_finder.sh runs run_proof.sh (part `proof`)
    "tests/memfn/run_wreply.sh": {"wreply", "memfnwreply"},
}
mech = {}
sd = os.path.join(root, "tests/mech/sabotages")
for f in sorted(os.listdir(sd)):
    m = re.match(r"(S\d+)_", f)
    if not m: continue
    t = open(os.path.join(sd, f), errors="replace").read()
    s = re.search(r'^SAB_SUITES="([^"]*)"', t, re.M)
    mech.setdefault(m.group(1), []).append((f, s.group(1).split() if s else [], t))
arms_seen = {}
for rel, arms in RUNNERS.items():
    out = subprocess.run(["bash", os.path.join(root, rel), "--plant-check", "dump"],
                         capture_output=True, text=True, cwd=root).stdout
    ids = sorted({l.split("\t")[0] for l in out.splitlines() if re.match(r"S\d+\t", l)})
    for i in ids:
        for f, suites, t in mech.get(i, []):
            arms_seen.setdefault(rel, set()).update(suites)
    n = moved = 0
    for i in ids:
        for f, suites, t in mech.get(i, []):
            n += 1
            reaimed = bool(re.search(r"RE-AIMED|Former detector|no longer reach", t))
            names_runner = bool(set(suites) & arms)
            if not names_runner:
                moved += 1
                print("%s\t%s\tmech=%s\tsuites=%s\tnames_runner=%s\treaimed_text=%s" % (
                    rel, i, f, ",".join(suites), names_runner, reaimed))
    print("SUMMARY %s: plants=%d twins_with_mech_row=%d flagged=%d arms_in_twin_rows=%s" % (
        rel, len(ids), n, moved, ",".join(sorted(arms_seen.get(rel, set())))))
