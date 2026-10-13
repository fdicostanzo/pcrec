#!/bin/bash
# slotarms/build.sh -- build the pcrec-engine arms in the kit harness's layout. Writes ONLY under $OUT.
#   bash build.sh            # subjects + every cell of arms.tsv
# Per cell $OUT/bin/<cell>/V0/: art.c art.h (pcrec output, -p rx) and run (drv.c + art.c, -O2, the TIMED binary).
# $OUT/subj/ holds the subjects (gen_subj.py). Builds are pinned to CPUS and run -j2 at most.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
PCREC=${PCREC:-$ROOT/build/pcrec}
OUT=${OUT:-$ROOT/build/slotarms}
CPUS=${CPUS:-12-13}
JOBS=${JOBS:-2}
CC=${CC:-gcc}
[ -x "$PCREC" ] || { echo "FATAL: no $PCREC (run make first)"; exit 1; }
mkdir -p "$OUT/bin" "$OUT/tmp"; TMPDIR=$OUT/tmp; export TMPDIR
python3 -I "$HERE/gen_subj.py" "$OUT/subj" || exit 1
: > "$OUT/tmp/jobs"
while IFS=$'\t' read -r cell pat flags fam eng vmp note; do
  case "$cell" in '#'*|'') continue ;; esac
  d=$OUT/bin/$cell/V0; mkdir -p "$d"
  # shellcheck disable=SC2086
  [ "$flags" = - ] && flags=
  "$PCREC" $flags -p rx -o "$d/art.c" --pattern "$pat" || { echo "PCREC FAILED $cell"; exit 1; }
  echo "$CC -O2 -I$d -c $d/art.c -o $d/art.o && $CC -O2 -I$d -c $HERE/drv.c -o $d/drv.o && $CC -o $d/run $d/drv.o $d/art.o" >> "$OUT/tmp/jobs"
done < "$HERE/arms.tsv"
tr '\n' '\0' < "$OUT/tmp/jobs" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' || { echo "BUILD FAILED"; exit 1; }
echo "built $(wc -l < "$OUT/tmp/jobs") cells under $OUT"
