#!/usr/bin/env bash
# e1build: a LIGHT pre-mech check of the E-1 sabotage rows — NOT the mech
# matrix (which is owed): each row's SAB_BEFORE -> SAB_AFTER applied to a
# `git archive REV` copy, a plain and a -DPCREC_KS_TRACE pcrec built, and the
# rows' named detectors run directly: e1_object_check.py (§14), the §4/§12
# stamp and refusal cells, and c_pert.py --every 16 (§15). Prints one line
# per row: the FAIL count each detector reports (> 0 = detected).
# usage: plant_precheck.sh TREE REV SCRATCH ROW...
set -u
T=$1; REV=$2; S=$3; shift 3
mkdir -p "$S"
for row in "$@"; do
  f=$(ls "$T"/tests/mech/sabotages/${row}_*.sh | head -1)
  W="$S/$row"; rm -rf "$W"; mkdir -p "$W/tree"
  git -C "$T" archive "$REV" | tar -x -C "$W/tree"
  ( unset SAB_FILE2 SAB_BEFORE2 SAB_AFTER2; . "$f"
    python3 - "$W/tree/$SAB_FILE" "$SAB_BEFORE" "$SAB_AFTER" <<'PY'
import sys
p, b, a = sys.argv[1:4]
s = open(p).read()
assert s.count(b) == 1, "anchor"
open(p, "w").write(s.replace(b, a))
PY
    if [ -n "${SAB_FILE2:-}" ]; then
      python3 - "$W/tree/$SAB_FILE2" "$SAB_BEFORE2" "$SAB_AFTER2" <<'PY'
import sys
p, b, a = sys.argv[1:4]
s = open(p).read()
assert s.count(b) == 1, "anchor2"
open(p, "w").write(s.replace(b, a))
PY
    fi )
  ( cd "$W/tree" && make -s -j4 build/pcrec > "$W/b.log" 2>&1 &&
    make -s -j4 BUILD_DIR=build-kst CFLAGS="-O2 -g -DPCREC_KS_TRACE" build-kst/pcrec >> "$W/b.log" 2>&1 )
  if [ ! -x "$W/tree/build/pcrec" ] || [ ! -x "$W/tree/build-kst/pcrec" ]; then
    echo "$row BUILD-FAILED"; continue
  fi
  P="$W/tree/build/pcrec"; K="$W/tree/build-kst/pcrec"
  mkdir -p "$W/fx" "$W/res" "$W/w" "$W/cp" "$W/L1"
  python3 "$T/tests/findings/e1_fixtures.py" "$T" "$W/fx"
  python3 "$T/tests/findings/res_fixtures.py" "$W/res"
  cp "$W/fx/L1/l1none.rxt" "$W/L1/"
  e1=$(gnutimeout 600 python3 "$T/tests/findings/e1_object_check.py" "$T" "$K" "$W/fx" "$W/res" "$W/w" 2>&1 | grep -c '^FAIL')
  st=0
  "$P" -p rx -fno-req-byte -o "$W/q.c" --pattern '^abc' 2>/dev/null && grep -q '_FINDINGS ""' "$W/q.c" || st=$((st+1))
  "$P" -p rx -o "$W/a.c" --pattern abc 2>/dev/null && grep -q '_FINDINGS "byte-rate=default:' "$W/a.c" || st=$((st+1))
  "$P" -p rx -e utf8 -I "$W/L1" --analysis l1none -o "$W/r.c" --pattern 'caf.' 2>/dev/null && st=$((st+1))
  "$P" -p rx -e utf8 -I "$W/L1" --analysis l1none -fno-req-byte -o "$W/r2.c" --pattern '^abc' 2>/dev/null && grep -q '_FINDINGS ""' "$W/r2.c" || st=$((st+1))
  cp=$(gnutimeout 900 python3 -I "$T/tests/findings/c_pert.py" "$T" "$P" "$W/cp" --every 16 --jobs 4 2>&1 | grep -c '^FAIL')
  echo "$row e1_object_check_fails=$e1 stamp_refusal_cells_failed=$st c_pert_fails=$cp"
  rm -rf "$W/tree/build" "$W/tree/build-kst"
done
echo "== plant precheck COMPLETE"
