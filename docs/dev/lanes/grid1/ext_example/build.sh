#!/bin/bash
# grid1 ext_example/build.sh -- a WORKED EXAMPLE of an external arm set (the
# shape main's lane `slotarms` fills in). Copy this directory to
# $OUT/ext/<name>/ and edit. Called by grid1's build.sh with OUT, GRID, CPUS,
# JOBS in the environment; must leave bin/<cell>/<arm>/run for every row of
# arms.tsv (cnt and chk optional).
#
# This example: cell `ex-dig`, the pattern `[0-9]+x` compiled by a pcrec
# binary twice -- base = `--memfn=no-pf-terms-mask` (today's walk), arm =
# the default (R17-b's form) -- each linked with grid1's own driver
# $OUT/lib/gdrv.c, so every run-binary rule (streamed subjects, GRID_OFF,
# GRID_FIXED) holds by construction. PCREC names the compiler (default: the
# worktree that holds grid1).
set -eu
PCREC=${PCREC:-$GRID/../../../../build/pcrec}
L=$OUT/lib
build_one() {   # arm extra-flags...
  local a=$1; shift
  local d=$OUT/bin/ex-dig/$a; mkdir -p "$d"
  "$PCREC" -p rx "$@" -o "$d/art.c" --pattern '[0-9]+x'
  gcc -O2 -I"$d" -I"$L" -o "$d/run" "$L/gdrv.c" "$d/art.c"
  gcc -O2 -I"$d" -I"$L" -o "$d/chk" "$L/gchk.c" "$d/art.c"     # optional: enables leg L
}
build_one walk --memfn=no-pf-terms-mask
build_one r17b
