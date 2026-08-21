#!/usr/bin/env python3
"""Verify every mech sabotage's SAB_BEFORE anchor still occurs in its target
file. A stale anchor means the sabotage silently fails to apply, i.e. a
sabotage row that certifies nothing."""
import os, re, subprocess, sys
root = "/home/duxevents/pcrec/worktrees/m6read"
sabdir = os.path.join(root, "tests/mech/sabotages")
stale = []
for fn in sorted(os.listdir(sabdir)):
    if not fn.endswith(".sh"):
        continue
    path = os.path.join(sabdir, fn)
    src = open(path).read()
    # SAB_FILE / SAB_BEFORE are shell assignments; ask bash for their values so
    # quoting and continuations are handled by the shell that will run them.
    out = subprocess.run(
        ["bash", "-c",
         'set -a; SAB_ID=; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; . "%s" 2>/dev/null; '
         'printf "%%s\\x00%%s\\x00" "$SAB_FILE" "$SAB_BEFORE"' % path],
        capture_output=True, text=True)
    parts = out.stdout.split("\x00")
    if len(parts) < 2:
        continue
    tgt, before = parts[0].strip(), parts[1]
    if not tgt or not before.strip():
        continue
    tp = os.path.join(root, tgt)
    if not os.path.exists(tp):
        stale.append((fn, tgt, "TARGET MISSING"))
        continue
    body = open(tp, errors="replace").read()
    if before not in body:
        stale.append((fn, tgt, "ANCHOR NOT FOUND"))
print("sabotages checked:", len([f for f in os.listdir(sabdir) if f.endswith('.sh')]))
if stale:
    print("STALE ANCHORS:", len(stale))
    for fn, tgt, why in stale:
        print("  %-42s %-24s %s" % (fn, tgt, why))
else:
    print("all anchors resolve")
