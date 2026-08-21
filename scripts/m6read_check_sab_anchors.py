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
unreadable, stale = [], []
for fn in sorted(f for f in os.listdir(sabdir) if f.endswith(".sh")):
    path = os.path.join(sabdir, fn)
    # SAB_FILE / SAB_BEFORE are shell assignments; ask bash for their values so
    # quoting and continuations are handled by the shell that will run them.
    # stderr is CAPTURED, never discarded: a file that fails to source is the
    # case that used to vanish.
    out = subprocess.run(
        ["bash", "-c",
         'set -a; SAB_ID=; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; . "%s"; '
         'printf "%%s\\x00%%s\\x00" "$SAB_FILE" "$SAB_BEFORE"' % path],
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
    if before not in body:
        stale.append((fn, tgt, "ANCHOR NOT FOUND"))

print("sabotages checked:", len([f for f in os.listdir(sabdir) if f.endswith('.sh')]))
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
sys.exit(1 if (unreadable or stale) else 0)
