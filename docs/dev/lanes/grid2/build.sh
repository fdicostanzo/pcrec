#!/bin/bash
# grid2/build.sh -- builds the zen4-grid2 slot under $OUT (default: the slot directory
# worktrees/memfn-slot/grid2). Writes ONLY under $OUT. Light work: compiles pinned to CPUS,
# at most JOBS at once, no clock.
#
#   OUT=... [DRY=1] bash build.sh          # design, grid1's build, ext sets, twins, subjects
#
# What it reuses: grid1/build.sh builds the six grid1 cells (dig bounded dfa-hat hex-run
# word-eq quad) and the new R0 cell `wcls` (\w+=, emitted by the kit-branch compiler through
# grid1/build.sh's EMIT_CELLS hook) with every grid1 arm (walk V1 G1 V2 V3 S1..A3 Sn An),
# runs the G1 control, and builds the ext sets this script lays down:
#   ext/ob/    items 3, 4  (ext_ob/build.sh: five one-byte cells, mkvar2.py `ob`)
#   ext/trig/  item 8      (ext_trig/build.sh)
# What it adds: the item-2 arms tw0/tw1/tw2 (dispatch twins) and sc0 (walk-in-helper
# scaffold) per cell, from mkvar2.py `disp` / `scaf`; and the streamed subjects.
#
# PCREC = the kit-branch compiler (must know --memfn=no-pf-terms-mask: main's does not).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
PCREC=${PCREC:-/home/pcrec/projects/pcrec/worktrees/memfn-r17/build/pcrec}
CPUS=${CPUS:-12-15}
JOBS=${JOBS:-4}
CC=${CC:-gcc}
DRYF=""; [ "${DRY:-0}" = 1 ] && DRYF=--dry
[ -x "$PCREC" ] || { echo "FATAL: no compiler at $PCREC (PCREC=)"; exit 1; }
"$PCREC" --list-axes 2>/dev/null | grep -q pf-terms-mask || { echo "FATAL: $PCREC lacks --memfn=no-pf-terms-mask (use the kit branch's build/pcrec)"; exit 1; }
mkdir -p "$OUT/tmp" "$OUT/subj" "$OUT/ext/ob" "$OUT/ext/trig"
export OUT PCREC CPUS JOBS CC G2=$HERE
TMPDIR=$OUT/tmp; export TMPDIR
{ echo "# grid2 build provenance $(date -u)"; echo "pcrec=$PCREC"; "$PCREC" --version 2>&1 | head -1
  echo "pcrec_sha256=$(sha256sum "$PCREC" | cut -d' ' -f1)"; echo "gcc=$($CC --version | head -1)"
  echo "grid2_commit=$(git -C "$HERE" rev-parse HEAD 2>/dev/null)"; } > "$OUT/provenance.txt"

echo "== 1. design"
python3 -I "$HERE/design2.py" design "$OUT" $DRYF || exit 1
cp "$HERE/ext_ob/build.sh" "$OUT/ext/ob/build.sh"; cp "$HERE/ext_trig/build.sh" "$OUT/ext/trig/build.sh"

echo "== 2. grid1's build (cells, arms, G1 control, ext sets)"
WT=$(dirname "$(dirname "$PCREC")")
SKIP_GEN=1 WT=$WT OUT=$OUT CELLS="dig bounded dfa-hat hex-run word-eq quad wcls" EMIT_CELLS='wcls=\w+=' \
  bash "$G1/build.sh" || { echo "grid1 build FAILED"; exit 1; }
ln -sfn wcls "$OUT/bin/f3-wcls"
python3 -I "$HERE/design2.py" design "$OUT" $DRYF || exit 1      # grid1's build overwrote the root tables

echo "== 3. item 2 arms: tw0 tw1 tw2 sc0"
L=$OUT/lib
jobs=$OUT/tmp/tw.jobs; : > "$jobs"
for c in dig dfa-hat bounded hex-run word-eq quad wcls; do
  for a in tw0 tw1 tw2 sc0; do
    case "$a" in sc0) case "$c" in hex-run|word-eq|wcls) ;; *) continue ;; esac ;; esac
    case "$a" in tw*) [ "$c" = wcls ] && continue ;; esac
    d=$OUT/bin/$c/$a; mkdir -p "$d"
    cp "$OUT/art/$c/new/art.h" "$d/"
    case "$a" in
      tw0|tw1) python3 -I "$HERE/mkvar2.py" disp "$OUT/art/$c/new/art.c" "$OUT/art/$c/deny/art.c" "$d/art.c" "${a#tw}" ;;
      tw2)     python3 -I "$HERE/mkvar2.py" disp "$OUT/art/$c/new/art.c" "$OUT/art/$c/deny/art.c" "$d/art.c" 2 "$OUT/bin/$c/A1/art.c" ;;
      sc0)     python3 -I "$HERE/mkvar2.py" scaf "$OUT/art/$c/deny/art.c" "$d/art.c" ;;
    esac || { echo "MKVAR2 FAILED $c $a"; exit 1; }
    av=""; [ "$a" = tw2 ] && av=-mavx2
    echo "$CC -O2 $av -I$d -I$L -c $d/art.c -o $d/art.o && $CC -O2 -I$d -I$L -c $L/gdrv.c -o $d/gdrv.o && $CC -o $d/run $d/gdrv.o $d/art.o && $CC -O2 -I$d -I$L -o $d/chk $L/gchk.c $d/art.o" >> "$jobs"
  done
done
echo "twin build jobs: $(grep -c . "$jobs")"
tr '\n' '\0' < "$jobs" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' > "$OUT/tmp/tw.build.out" 2>&1
grep -E 'error' "$OUT/tmp/tw.build.out" | head
for c in dig dfa-hat bounded hex-run word-eq quad; do for a in tw0 tw1 tw2; do for b in run chk; do
  [ -x "$OUT/bin/$c/$a/$b" ] || { echo "MISSING $c/$a/$b"; exit 1; }; done; done; done
for c in hex-run word-eq wcls; do for b in run chk; do [ -x "$OUT/bin/$c/sc0/$b" ] || { echo "MISSING $c/sc0/$b"; exit 1; }; done; done

echo "== 4. subjects"
if [ "${SKIP_GEN:-0}" != 1 ]; then
  g0=$(date +%s)
  taskset -c "$CPUS" python3 -I "$HERE/design2.py" gen "$OUT" -j "$JOBS" || { echo "GEN FAILED"; exit 1; }
  echo "gen: wall=$(( $(date +%s) - g0 ))s bytes=$(awk -F'\t' 'NR>1{b+=$3*$8} END{print b}' "$OUT/subjects.tsv")"
fi
echo "build: done"
