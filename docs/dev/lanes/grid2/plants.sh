#!/bin/bash
# grid2/plants.sh -- the gate's FAILING DIRECTION for grid2's new arms (grid1/plants.sh does
# grid1's own). Each plant is a one-line sabotage of a generated grid2 arm (or of the streamed
# driver for one arm); check.sh's own legs must report it: a plant on a PICKABLE arm must end
# check.sh with exit 3 (and a PICKABLE-FAIL line), a plant on an INSTRUMENT arm (tw*, sc0) must
# put that arm in $OUT/excluded. Run after a green check.sh on a BUILT slot directory (the DRY
# one is enough); each plant is applied to bin/<cell>/<arm>/art.c, the arm rebuilt, check.sh run,
# the original restored and rebuilt; a last check.sh must be green again.
# Rev 3 adds the plants that no answer leg can see (the provenance leg P and the manifest census M,
# provcheck.py): N=33..46 point dropped from the arm tables, the VM_ATTEMPT cell silently built as a
# DFA hat, a walk arm silently built from the V1 text, a cover-shape group dropped, a compiler whose
# abi is not the expected one, and a compiler without the deny. Each must end check.sh with exit 4 and
# the named PROV-FAIL / CENSUS-FAIL line (the legs R, L, C, O stay GREEN under the first four).
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
# ---- rev-3 plants
backup_tables() { cp "$OUT/arms.tsv" "$OUT/tmp/arms.tsv.r3"; cp "$OUT/ext/ob/arms.tsv" "$OUT/tmp/arms_ob.tsv.r3"; }
restore_tables() { cp "$OUT/tmp/arms.tsv.r3" "$OUT/arms.tsv"; cp "$OUT/tmp/arms_ob.tsv.r3" "$OUT/ext/ob/arms.tsv"; }
drop_token() {   # file token: remove one subject token from a comma list in column 4
  python3 -I - "$1" "$2" <<'PY'
import sys
p, tok = sys.argv[1], sys.argv[2]
out, hit = [], 0
for l in open(p).read().split("\n"):
    f = l.split("\t")
    if len(f) == 5 and not l.startswith("#") and tok in f[3].split(","):
        f[3] = ",".join(x for x in f[3].split(",") if x != tok); hit += 1
        if not f[3]: continue
        l = "\t".join(f)
    out.append(l)
assert hit, "token not found: " + tok
open(p, "w").write("\n".join(out))
PY
}
r3() {   # name marker expect-rc "what it breaks" prep restore [ENV=val ...]
  local name=$1 marker=$2 want=$3 why=$4 prep=$5 restore=$6 v; shift 6
  backup_tables
  eval "$prep" || { say "PLANT $name: prep failed"; fails=1; restore_tables; return; }
  env "$@" bash "$HERE/check.sh" > "$OUT/plants2.$name.out" 2>&1; rc=$?
  if [ "$rc" = "$want" ] && grep -q "$marker" "$OUT/check2.status"; then v=DETECTED; else v=UNDETECTED; fails=1; fi
  say "PLANT $name: $v  (expect rc $want + '$marker', got rc=$rc; legs R/L/C/O: $(grep -c ' FAIL ' "$OUT/check.log" 2>/dev/null) failing lines)  -- $why"
  eval "$restore"; restore_tables
}
NPT=46      # in the DRY subset (design2.py DRY_N) and in the full design
r3 n_dropped "CENSUS-FAIL item 2a" 4 "the N=$NPT point silently dropped from the arm tables (nothing answers wrong, the staircase just has a hole)" \
   "drop_token '$OUT/arms.tsv' 'g2-dig-n$NPT-ginf-Lnone-S'" ":"
r3 cover_dropped "CENSUS-FAIL item 3a" 4 "one cover-shape group (c001, 64 KiB) dropped" \
   "drop_token '$OUT/arms.tsv' 'g2-f3-c001-n64k-ginf-Lnone-S'" ":"
cp "$OUT/bin/o-vm/v1/art.c" "$OUT/tmp/ovm_v1.art.c.orig"; cp "$OUT/bin/o-vm/v1/art.h" "$OUT/tmp/ovm_v1.art.h.orig"
r3 vm_as_dfa "^PROV-FAIL o-vm v1" 4 "the VM_ATTEMPT v1 arm silently built as a DFA hat (same pattern, same answers, wrong ROUTE)" \
   "cp '$OUT/art/o-fwd/art.c' '$OUT/bin/o-vm/v1/art.c'; cp '$OUT/art/o-fwd/art.h' '$OUT/bin/o-vm/v1/art.h'; build_arm o-vm v1" \
   "cp '$OUT/tmp/ovm_v1.art.c.orig' '$OUT/bin/o-vm/v1/art.c'; cp '$OUT/tmp/ovm_v1.art.h.orig' '$OUT/bin/o-vm/v1/art.h'; build_arm o-vm v1 >/dev/null 2>&1"
cp "$OUT/bin/c020/walk/art.c" "$OUT/tmp/c020_walk.art.c.orig"; cp "$OUT/bin/c020/walk/art.h" "$OUT/tmp/c020_walk.art.h.orig"
r3 walk_as_v1 "^PROV-FAIL c020 walk" 4 "the c020 walk arm silently built from the V1 text (the deny never took; legs R/L/C/O all green)" \
   "cp '$OUT/bin/c020/V1/art.c' '$OUT/bin/c020/walk/art.c'; cp '$OUT/bin/c020/V1/art.h' '$OUT/bin/c020/walk/art.h'; build_arm c020 walk" \
   "cp '$OUT/tmp/c020_walk.art.c.orig' '$OUT/bin/c020/walk/art.c'; cp '$OUT/tmp/c020_walk.art.h.orig' '$OUT/bin/c020/walk/art.h'; build_arm c020 walk >/dev/null 2>&1"
r3 abi_mismatch "^PROV-FAIL compiler" 4 "the compiler's abi is not the expected one (EXPECT_ABI)" ":" ":" EXPECT_ABI=1
if [ -x /home/pcrec/projects/pcrec/build/pcrec ]; then
  r3 no_deny "^PROV-FAIL compiler" 4 "main's compiler (no pf-terms-mask deny): the walk arms could not be built" ":" ":" PCREC=/home/pcrec/projects/pcrec/build/pcrec
fi
bash "$HERE/check.sh" > "$OUT/plants2.restore.out" 2>&1 && say "restore: check.sh green again" || { say "restore: check.sh NOT green after the plants"; fails=1; }
[ "$fails" = 0 ] && say "plants: ALL DETECTED" || say "plants: FAILED"
[ "$fails" = 0 ]
