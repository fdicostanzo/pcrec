#!/usr/bin/env bash
# twincmp.sh TREE: S1224's and S3064's re-aimed runner plants (through tests/lib/plants.py)
# against their mech twins' SAB_BEFORE/AFTER (plain replace), each on a fresh copy.
set -u
W=$1
fn() { awk '/^plant_spec\(\) \{/{f=1} f{print} f&&/^}$/{exit}' "$1"; }
twin() {   # ROW FILE: the row's site(s) replaced once in FILE
    bash -c 'set -a; . "$1"; exec python3 -I -c "
import os, sys
p = sys.argv[1]; s = open(p).read()
for b, a in ((\"SAB_BEFORE\", \"SAB_AFTER\"), (\"SAB_BEFORE2\", \"SAB_AFTER2\")):
    if os.environ.get(b): s = s.replace(os.environ[b], os.environ[a], 1)
open(p, \"w\").write(s)" "$2"' x "$1" "$2"
}
rc=0
T=$(mktemp -d /var/tmp/pcrec-claude/scratch/plantfix/twin.XXXXXX)
cp -r "$W/memfn/src" "$T/a1"; cp -r "$W/memfn/src" "$T/b1"
twin "$W"/tests/mech/sabotages/S1224_*.sh "$T/a1/compose.c"
spec=$(bash -c "$(fn "$W/tests/memfn/run_proof.sh")"$'\nplant_spec S1224')
python3 -I "$W/tests/lib/plants.py" apply win "$T/b1" -- "$spec" || rc=1
if cmp -s "$T/a1/compose.c" "$T/b1/compose.c" && ! cmp -s "$T/a1/compose.c" "$W/memfn/src/compose.c"; then
    echo "S1224: runner plant == mech twin (and differs from the clean file)"; else echo "S1224: DIFFER"; rc=1; fi
cp -r "$W/memfn/src" "$T/a2"; cp -r "$W/memfn/src" "$T/b2"
twin "$W"/tests/mech/sabotages/S3064_*.sh "$T/a2/compose.c"
ed=(); while IFS= read -r l; do ed+=("$l"); done <<< "$(bash -c "$(fn "$W/memfn/tests/run_g2_pres.sh")"$'\nplant_spec S3064')"
python3 -I "$W/tests/lib/plants.py" apply pres "$T/b2" "$T/b2" -- "${ed[@]}" || rc=1
if cmp -s "$T/a2/compose.c" "$T/b2/compose.c" && ! cmp -s "$T/a2/compose.c" "$W/memfn/src/compose.c"; then
    echo "S3064: runner plant (both edits) == mech twin (both sites)"; else echo "S3064: DIFFER"; diff "$T/a2/compose.c" "$T/b2/compose.c"; rc=1; fi
echo "twin dir: $T"
exit $rc
