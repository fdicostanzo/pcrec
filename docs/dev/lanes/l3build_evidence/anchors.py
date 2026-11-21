#!/usr/bin/env python3
"""anchors.py TREE [FILES...]: for every tests/mech/sabotages row whose SAB_FILE is in FILES (all if none),
print id, file, count of SAB_BEFORE in TREE/SAB_FILE. Rows read from TREE's own sabotages dir."""
import os, subprocess, sys, glob
tree = sys.argv[1]; files = set(sys.argv[2:])
for f in sorted(glob.glob(os.path.join(tree, 'tests/mech/sabotages/*.sh'))):
    out = subprocess.run(['bash', '-c', 'SAB_FILE=; SAB_BEFORE=; . "$1" >/dev/null 2>&1; printf "%s\\0%s" "$SAB_FILE" "$SAB_BEFORE"', '_', f],
                         capture_output=True, text=True).stdout
    sf, _, before = out.partition('\0')
    if not sf or (files and sf not in files) or not before: continue
    p = os.path.join(tree, sf)
    try: n = open(p, errors='replace').read().count(before)
    except OSError: n = -1
    print(f"{os.path.basename(f)[:-3]}\t{sf}\t{n}")
