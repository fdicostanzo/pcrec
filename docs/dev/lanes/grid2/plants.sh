#!/bin/bash
# grid2/plants.sh -- the gate's FAILING DIRECTION for grid2's new arms (grid1/plants.sh does
# grid1's own). Each plant is a one-line sabotage of a generated grid2 arm (or of the streamed
# driver for one arm); check.sh's own legs must report it: a plant on a PICKABLE arm must end
# check.sh with exit 3 (and a PICKABLE-FAIL line), a plant on an INSTRUMENT arm (tw*, sc0) must
# put that arm in $OUT/excluded. Run after a green check.sh on a BUILT slot directory (the DRY
# one is enough); each plant is applied to bin/<cell>/<arm>/art.c, the arm rebuilt, check.sh run,
# the original restored and rebuilt; a last check.sh must be green again.
#   OUT=... bash plants.sh     -> $OUT/plants2.log, last line "plants: ALL DETECTED" | "plants: FAILED ..."
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?set OUT to a built slot directory}
CC=${CC:-gcc}
L=$OUT/lib
LOG=$OUT/plants2.log; : > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }
build_arm() {   # cell arm [drv-file]
  local c=$1 a=$2 drv=${3:-$L/gdrv.c} d=$OUT/bin/$1/$2 av="" kd=""
  [ "$a" = tw2 ] && av=-mavx2; case "$a" in A*) av=-mavx2 ;; esac
  $CC -O2 $av -I"$d" -I"$L" -c "$d/art.c" -o "$d/art.o" && $CC -O2 -I"$d" -I"$L" -c "$drv" -o "$d/gdrv.o" && $CC -o "$d/run" "$d/gdrv.o" "$d/art.o" \
    && $CC -O2 -I"$d" -I"$L" -o "$d/chk" "$L/gchk.c" "$d/art.o" || { say "REBUILD FAILED $c $a"; return 1; }
}
# name | cell | arm | kind (art|drv) | old=>new | expectation (pickable|instrument) | what it breaks
PLANTS=(
"v1lane|o-fwd|v1|art|pcrec_mfk_w8_first_lane(m)=>pcrec_mfk_w8_first_lane(m) + 1|pickable|the one-term SWAR find answers one byte late"
"walktab|o-fwd|walk|art|[120] = 1=>[121] = 1|pickable|the BASE walk's table holds the wrong member byte (leg O: base vs libpcre2)"
"nonerev|o-fwd|none|art|match_start_position = rewind_position;=>match_start_position = rewind_position + 1;|pickable|the NONE arm's match start one byte late"
"tw0walk|dig|tw0|art|!rx_search_pf__tab[c->s[lo]]=>rx_search_pf__tab[c->s[lo]]|instrument|the twin's walk helper inverted"
"tw1mask|dig|tw1|art|pcrec_mfk_w8_range(v, 0x30, 10)=>pcrec_mfk_w8_range(v, 0x30, 9)|instrument|the twin's V1 mask misses the digit 9"
"sc0walk|hex-run|sc0|art|!rx_search_pf__tab[c->s[lo]]=>rx_search_pf__tab[c->s[lo]]|instrument|the scaffold's walk helper inverted (only a GATE-ONLY dense group can see it)"
"tw2cycle|dig|tw2|drv|if (++cur == gnbuf) cur = 0;=>cur = 0;|instrument|the streamed timed loop re-times buffer 0 forever (leg C)"
)
fails=0
bash "$HERE/check.sh" > "$OUT/plants2.base.out" 2>&1 || { say "plants: the unplanted check is not green; run check.sh first"; exit 2; }
for p in "${PLANTS[@]}"; do
  IFS='|' read -r name cell arm kind repl expect why <<<"$p"
  old=${repl%%=>*}; new=${repl#*=>}
  d=$OUT/bin/$cell/$arm; cp "$d/art.c" "$d/art.c.orig"
  drv=$L/gdrv.c
  if [ "$kind" = drv ]; then
    python3 -I - "$L/gdrv.c" "$OUT/tmp/gdrv_plant.c" "$old" "$new" <<'PY' || { say "PLANT $name: anchor not found"; fails=1; continue; }
import sys
t = open(sys.argv[1]).read(); assert sys.argv[3] in t, "anchor"
open(sys.argv[2], "w").write(t.replace(sys.argv[3], sys.argv[4], 1))
PY
    drv=$OUT/tmp/gdrv_plant.c
  else
    python3 -I - "$d/art.c.orig" "$d/art.c" "$old" "$new" <<'PY' || { say "PLANT $name: anchor not found"; cp "$d/art.c.orig" "$d/art.c"; fails=1; continue; }
import sys
t = open(sys.argv[1]).read(); assert sys.argv[3] in t, "anchor"
open(sys.argv[2], "w").write(t.replace(sys.argv[3], sys.argv[4]))
PY
  fi
  build_arm "$cell" "$arm" "$drv" || { fails=1; continue; }
  bash "$HERE/check.sh" > "$OUT/plants2.$name.out" 2>&1; rc=$?
  if [ "$expect" = pickable ]; then
    { [ "$rc" = 3 ] && grep -q "^PICKABLE-FAIL $cell $arm" "$OUT/check2.status"; } && v=DETECTED || { v=UNDETECTED; fails=1; }
  else
    grep -qx "$cell $arm" "$OUT/excluded" && v=DETECTED || { v=UNDETECTED; fails=1; }
  fi
  say "PLANT $name: $v  (expect $expect, check rc=$rc, excluded: $(tr '\n' ',' < "$OUT/excluded" | cut -c1-80))  -- $why"
  cp "$d/art.c.orig" "$d/art.c"; rm -f "$d/art.c.orig"; build_arm "$cell" "$arm" >/dev/null 2>&1
done
bash "$HERE/check.sh" > "$OUT/plants2.restore.out" 2>&1 && say "restore: check.sh green again" || { say "restore: check.sh NOT green after the plants"; fails=1; }
[ "$fails" = 0 ] && say "plants: ALL DETECTED" || say "plants: FAILED"
[ "$fails" = 0 ]
