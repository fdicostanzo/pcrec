#!/usr/bin/env python3
"""Verify every mech sabotage's SAB_BEFORE anchor still occurs in its target
file. A stale anchor means the sabotage silently fails to apply, i.e. a
sabotage row that certifies nothing.

Pure grep -- no builds, seconds to run -- which is what makes it usable as a
standing tripwire beside `make mech`'s build-per-sabotage sweep. It was that
gap that let seven anchors drift undetected for weeks.

Graduated from the [M6-READ] lane. Its root was HARDCODED to that lane's
worktree, so it ran nowhere else once the worktree was removed; the root is
now derived from this file's own location, the same way every tests/ script
derives ROOT_DIR from BASH_SOURCE. Run it from anywhere.
"""
import os, subprocess, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sabdir = os.path.join(root, "tests/mech/sabotages")

# THREE OUTCOMES, and keeping them apart is the point of this tool.
#
#   unreadable  the row cannot be READ -- it does not parse, or it names no
#               target, or it carries no anchor. Says nothing about the anchor;
#               says the tripwire is blind to this row.
#   stale       the row reads fine and its anchor does NOT occur in its target.
#   (neither)   fine.
#
# The first class used to be a silent `continue`, which scored an unreadable
# row as healthy -- a blind spot of exactly the kind this tool exists to catch,
# and this tree's catalogue lesson 9 (extraction helpers hard-fail on empty,
# never default). Found by a positive control, after that control's own first
# attempt was itself vacuous: the sabotage regex matched an ESCAPED quote and
# never corrupted the anchor at all, so the resulting "all resolve" was read as
# a checker failure when in fact nothing had been sabotaged. Prove the sabotage
# reached the target before believing what the check says about it.
# [M6.5.2-FIX] A ROW MAY CARRY A SECOND SITE, and this tool checks BOTH.
# `run_sabotage_matrix.sh` grew an optional SAB_FILE2/BEFORE2/AFTER2/COUNT2
# for S108, whose claim needs two independent gates removed at once. A second
# site the tripwire did not read would be exactly the blind spot this file
# exists to close -- a stale anchor there fails the row's apply at mech time
# and nowhere earlier. SITES are counted and printed alongside rows, so
# "sabotages checked: 118" can never again be mistaken for "anchors checked".
unreadable, stale = [], []
sites = 0
for fn in sorted(f for f in os.listdir(sabdir) if f.endswith(".sh")):
    path = os.path.join(sabdir, fn)
    # SAB_FILE / SAB_BEFORE are shell assignments; ask bash for their values so
    # quoting and continuations are handled by the shell that will run them.
    # stderr is CAPTURED, never discarded: a file that fails to source is the
    # case that used to vanish.
    out = subprocess.run(
        ["bash", "-c",
         'set -a; SAB_ID=; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; SAB_COUNT=; '
         'SAB_FILE2=; SAB_BEFORE2=; SAB_AFTER2=; SAB_COUNT2=; . "%s"; '
         'printf "%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00" '
         '"$SAB_FILE" "$SAB_BEFORE" "${SAB_COUNT:-1}" '
         '"$SAB_FILE2" "$SAB_BEFORE2" "${SAB_COUNT2:-1}"' % path],
        capture_output=True, text=True)
    if out.returncode != 0 or out.stderr.strip():
        why = (out.stderr.strip().splitlines() or ["exit %d" % out.returncode])[-1]
        unreadable.append((fn, "DOES NOT SOURCE: " + why[:70]))
        continue
    parts = out.stdout.split("\x00")
    if len(parts) < 2:
        unreadable.append((fn, "NO SAB_FILE/SAB_BEFORE EXTRACTED"))
        continue
    tgt, before = parts[0].strip(), parts[1]
    # [M6.4.4] the EXACT-COUNT check: mech's apply (tests/mech/lib/replace.py)
    # refuses unless the anchor occurs exactly SAB_COUNT times, so a presence-
    # only check here passed S48 while mech scored it ANOMALY (the block had
    # been duplicated by a refactor). The two instruments now ask the same question.
    try:
        want = int((parts[2] if len(parts) > 2 else "1").strip() or "1")
    except ValueError:
        want = 1
    if not tgt:
        unreadable.append((fn, "SAB_FILE IS EMPTY"))
        continue
    if not before.strip():
        unreadable.append((fn, "SAB_BEFORE IS EMPTY"))
        continue
    tp = os.path.join(root, tgt)
    if not os.path.exists(tp):
        stale.append((fn, tgt, "TARGET MISSING"))
        continue
    body = open(tp, errors="replace").read()
    sites += 1
    if before not in body:
        stale.append((fn, tgt, "ANCHOR NOT FOUND"))
    elif body.count(before) != want:
        stale.append((fn, tgt, "ANCHOR COUNT %d, SAB_COUNT %d" % (body.count(before), want)))

    # The optional SECOND site, asked the identical question. A row that names
    # SAB_FILE2 with no anchor is UNREADABLE rather than fine: the matrix will
    # score it ANOMALY, and this tool must not say "resolves" about a site it
    # could not read.
    tgt2 = parts[3].strip() if len(parts) > 3 else ""
    if tgt2:
        before2 = parts[4] if len(parts) > 4 else ""
        try:
            want2 = int((parts[5] if len(parts) > 5 else "1").strip() or "1")
        except ValueError:
            want2 = 1
        if not before2.strip():
            unreadable.append((fn, "SAB_FILE2 SET BUT SAB_BEFORE2 IS EMPTY"))
        else:
            tp2 = os.path.join(root, tgt2)
            sites += 1
            if not os.path.exists(tp2):
                stale.append((fn, tgt2, "SITE 2: TARGET MISSING"))
            else:
                body2 = open(tp2, errors="replace").read()
                if before2 not in body2:
                    stale.append((fn, tgt2, "SITE 2: ANCHOR NOT FOUND"))
                elif body2.count(before2) != want2:
                    stale.append((fn, tgt2, "SITE 2: ANCHOR COUNT %d, SAB_COUNT2 %d"
                                  % (body2.count(before2), want2)))

print("sabotages checked:", len([f for f in os.listdir(sabdir) if f.endswith('.sh')]),
      "(%d anchor sites)" % sites)
if unreadable:
    print("UNREADABLE ROWS:", len(unreadable), "-- the tripwire is BLIND to these")
    for fn, why in unreadable:
        print("  %-42s %s" % (fn, why))
if stale:
    print("STALE ANCHORS:", len(stale))
    for fn, tgt, why in stale:
        print("  %-42s %-24s %s" % (fn, tgt, why))
if not unreadable and not stale:
    print("all anchors resolve")

# ---------------------------------------------------------------------------
# THE RUNNER PLANT PASS (lane plantfix, 2026-11-24; FUW-12's class, triage
# docs/dev/lanes/plantri_report.md). Four runners carry plants of their own --
# a `plant_spec` case function and a `PLANTS` id list, applied by their
# `--plant ID` / `--plants` modes, which nothing runs automatically -- and the
# pass above never read them: four FROM texts went stale and nothing noticed.
# The pass reads each plant through THE RUNNER'S OWN APPLIER: every runner's
# `--plant-check` mode hands its edits, built by the same `plant_edits` its
# --plants mode applies, to tests/lib/plants.py's `check` entry, the same file
# whose `apply` entry the --plants mode calls. There is no second decoder here;
# this pass only discovers, runs, parses and counts.
#
#   discovery   every *.sh under tests/ and memfn/tests/ that defines
#               `plant_spec() {`. A discovered runner with no --plant-check
#               mode is UNREADABLE and is never run (it would run the suite).
#   per plant   STALE / AMBIGUOUS / MISSING FILE / NO SPEC / UNDECODABLE per
#               edit, and ORPHAN for a plant_spec case PLANTS does not list.
#   population  its OWN line, "runner plants checked: N", held to a LITERAL
#               floor: a runner dropped from discovery (renamed, its list
#               emptied, its mode broken into an empty answer) must go red,
#               not read "0 stale". Raise the floor in the change that adds
#               plants; never lower it to make a run pass.
#
# The four runners run CONCURRENTLY (owner ruling 2026-11-23: the pass rides
# test-codegen): measured ~0.2 s each, ~0.3 s for the pass.
PLANT_FLOOR = 81   # measured 2026-11-24 (lane plantfix): win 38, pres 35, proof 6, wreply 2
PLANT_DIRS = ("tests", "memfn/tests")
runners = []
for d in PLANT_DIRS:
    for dp, dns, fns in os.walk(os.path.join(root, d)):
        dns.sort()
        for fn in sorted(fns):
            if fn.endswith(".sh"):
                fp = os.path.join(dp, fn)
                txt = open(fp, errors="replace").read()
                if any(ln.startswith("plant_spec() {") for ln in txt.split("\n")):
                    runners.append((os.path.relpath(fp, root), txt))
p_unreadable, p_bad = [], []
nplants = nedits = 0
env = dict(os.environ, CC_RESOLVE_ANNOUNCED="1")   # cc_resolve's notice; any OTHER stderr is a finding
procs = []
for rel, txt in runners:
    if '"--plant-check"' not in txt:
        p_unreadable.append((rel, "DEFINES plant_spec BUT HAS NO --plant-check MODE"))
        continue
    procs.append((rel, subprocess.Popen(["bash", os.path.join(root, rel), "--plant-check"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, env=env)))
for rel, pr in procs:
    try:
        out, err = pr.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        pr.kill(); pr.communicate()
        p_unreadable.append((rel, "--plant-check TIMED OUT (120 s)"))
        continue
    lines = out.split("\n")
    summ = [l for l in lines if l.startswith("plant-check: ")]
    rows = [l.split("\t") for l in lines if l and not l.startswith("plant-check: ")]
    if err.strip() or pr.returncode not in (0, 1) or len(summ) != 1 \
            or any(len(r) != 5 for r in rows):
        why = (err.strip().splitlines() or ["exit %d, %d summary line(s)" % (pr.returncode, len(summ))])[-1]
        p_unreadable.append((rel, "--plant-check UNREADABLE: " + why[:70]))
        continue
    try:
        P, E, Bn = [int(x.split()[0]) for x in summ[0][len("plant-check: "):].split(", ")]
    except ValueError:
        p_unreadable.append((rel, "--plant-check SUMMARY UNREADABLE: " + summ[0][:60]))
        continue
    bad = [r for r in rows if r[2] != "OK"]
    ids = {r[0] for r in rows if r[2] != "ORPHAN"}
    if len(ids) != P or len(bad) != Bn or (pr.returncode == 0) != (Bn == 0):
        p_unreadable.append((rel, "--plant-check INCONSISTENT: %d ids, summary %s" % (len(ids), summ[0])))
        continue
    nplants += P
    nedits += E
    for r in bad:
        p_bad.append((rel, r))
print("runner plants checked: %d (%d edits, %d runners), floor %d"
      % (nplants, nedits, len(runners), PLANT_FLOOR))
if p_unreadable:
    print("UNREADABLE RUNNERS:", len(p_unreadable), "-- the plant pass is BLIND to these")
    for rel, why in p_unreadable:
        print("  %-42s %s" % (rel, why))
if nplants < PLANT_FLOOR:
    print("RUNNER PLANT POPULATION %d IS BELOW ITS FLOOR %d -- a runner left discovery "
          "or lost its list; the plants were not all read" % (nplants, PLANT_FLOOR))
if p_bad:
    print("BAD RUNNER PLANTS:", len(p_bad))
    for rel, (pid, edit, st, c, path) in p_bad:
        print("  %-30s %-6s edit %-4s %-13s count %s  %s" % (rel, pid, edit, st, c, path))
p_fail = bool(p_unreadable or p_bad or nplants < PLANT_FLOOR)
if not p_fail:
    print("all runner plants apply")
sys.exit(1 if (unreadable or stale or p_fail) else 0)
