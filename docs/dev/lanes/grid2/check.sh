#!/bin/bash
# grid2/check.sh -- the MANDATORY correctness gate before the zen4-grid2 slot
# (r17b_prime.md §5.4 item 5). grid1/check.sh does the work (legs O, R, L, C, the reach
# leg U and the landing-fidelity leg G, over grid2's merged arm tables, ext sets
# included); grid2 changes four things around it:
#   - leg O's oracle is LIBPCRE2 (10.46, refused otherwise) through tests/oracle/'s local
#     adapter (design2.py oracles), not python `re`; the generator's planted-count
#     self-check still uses python `re` (an independent second source);
#   - the deep legs (E N F A, the ASan/UBSan sweep over grid1's own cells) are off: they
#     are grid1's, on grid1's subjects, and grid2 adds no generated W/ALIGN/KEEP arm
#     (item 2's twins and item 3's helpers are checked by R, L, C on the timed subjects);
#   - leg U2 (new): every one-byte group's site is REACHED: the walk arm's `cnt` build
#     (g2_find call/byte counts) must show at least one call per buffer, else the row
#     would time an upstream gate;
#   - a PICKABLE arm in `excluded` FAILS the check (exit 3) whatever ALLOW_EXCLUDED says: a
#     wrong kit form is not a timing question. Pickable = every arm the tables can pick
#     (walk V1 S1 A1 A3, libc v1 loop none, keep drop). Twin/scaffold arms (tw0-2, sc0)
#     are instruments: they may be excluded under ALLOW_EXCLUDED=1.
#   - leg P (rev 3): provcheck.py check -- the COMPILER's commit/abi/staleness and every timed arm's
#     SIGNATURE (a walk built from the V1 text, a VM_ATTEMPT cell built as a DFA hat, a deny the
#     compiler does not take: all answer right, only this leg can see them); leg M: provcheck.py
#     census -- the arm tables hold the rev-3 items (N = 33..46, the three cover shapes, the
#     VM_ATTEMPT groups, NONE's 30 arms) against literal expectations. A failure of P or M ends
#     check.sh with exit 4 and `PROV-FAIL` / `CENSUS-FAIL` lines in check2.status.
#   OUT=... bash check.sh      -> $OUT/check.log, $OUT/excluded, $OUT/unreached, $OUT/check2.status
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
JOBS=${JOBS:-4}
export OUT
S=$OUT/check2.status
: > "$S"
start=$(date +%s)
echo "CHECK_START $(date -Is)" >> "$S"
ORACLE_CMD="python3 -I $HERE/design2.py oracles $OUT -j $JOBS" SKIP_DEEP=1 bash "$G1/check.sh"
rc=$?
echo "G1CHECK rc=$rc" >> "$S"

# ---- leg U2: reach of the one-byte sites
u2=0; u2n=0
if [ -s "$OUT/ext/ob/arms.tsv" ]; then
  python3 -I "$G1/arms.py" "$OUT" groups timed EXT | awk -F'\t' '$1 ~ /^o-/' | while IFS=$'\t' read -r c s m arms; do
    nm=${s%@*}; nb=$(ls "$OUT/subj/$nm" | grep -vc '^\.')
    line=$(taskset -c "${CNT_CPUS:-12-15}" gnutimeout 600 "$OUT/bin/$c/walk/cnt" "$OUT/subj/$nm" list "$m" 2>&1 >/dev/null | tail -1)
    calls=$(sed -n 's/.*calls=\([0-9]*\).*/\1/p' <<<"$line")
    if [ -n "$calls" ] && [ "$calls" -ge "$nb" ]; then echo "$c walk U2 $c $nm $m OK calls=$calls nbuf=$nb"
    else echo "$c walk U2 $c $nm $m FAIL calls=${calls:-?} nbuf=$nb"; fi
  done > "$OUT/res_u2.txt"
  u2n=$(wc -l < "$OUT/res_u2.txt"); u2=$(grep -c ' FAIL ' "$OUT/res_u2.txt")
  cat "$OUT/res_u2.txt" >> "$OUT/check.log"
fi
echo "reach (U2): $u2n one-byte groups, $u2 FAIL"; grep ' FAIL ' "$OUT/res_u2.txt" 2>/dev/null | head
echo "U2 groups=$u2n fail=$u2" >> "$S"

# ---- legs P and M: provenance and the manifest census
python3 -I "$HERE/provcheck.py" "$OUT" check > "$OUT/prov.out" 2>&1; prc=$?
python3 -I "$HERE/provcheck.py" "$OUT" census > "$OUT/census.out" 2>&1; mrc=$?
grep -h -E '^(PROV|CENSUS)-FAIL' "$OUT/prov.out" "$OUT/census.out" >> "$S"
echo "provenance (P): rc=$prc $(tail -1 "$OUT/prov.out" | cut -c1-110)"; echo "census (M): rc=$mrc $(tail -1 "$OUT/census.out" | cut -c1-110)"
echo "P rc=$prc M rc=$mrc" >> "$S"

# ---- pickable arms in `excluded`
PICKABLE=" walk V1 S1 A1 A3 libc v1 loop none keep drop "
pfail=0
if [ -s "$OUT/excluded" ]; then
  while read -r c a; do
    case "$PICKABLE" in *" $a "*) echo "PICKABLE-FAIL $c $a"; pfail=$((pfail + 1)) ;; esac
  done < "$OUT/excluded" | tee -a "$S"
  pfail=$(grep -c '^PICKABLE-FAIL' "$S")
fi
echo "pickable arm failures: $pfail"
verdict=OK
[ "$u2" -gt 0 ] && verdict=FAILED
[ "$pfail" -gt 0 ] && verdict=FAILED
[ "$rc" != 0 ] && [ ! -s "$OUT/excluded" ] && verdict=FAILED       # grid1's check failed for a reason other than arm exclusion
[ "$prc" != 0 ] && verdict=FAILED
[ "$mrc" != 0 ] && verdict=FAILED
echo "$verdict wall=$(( $(date +%s) - start ))s $(date -Is)" | sed 's/^/CHECK_/' >> "$S"
echo "grid2 check: $verdict"
[ "$pfail" -gt 0 ] && exit 3
[ "$prc" != 0 ] || [ "$mrc" != 0 ] && exit 4
[ "$verdict" = OK ] || exit 1
exit 0
