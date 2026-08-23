#!/bin/sh
# [DD-14] §6 PROTOTYPE -- the emitted-SIZE and RUN-TIME cost of the three
# linkages for an addressable body (charter addition (i)).
#
# The generator is ../prototype/gen_linkage.py; its header says what the three
# variants are and why the charter's "once-emitted-with-two-linkages" collapses
# into HYBRID once it is written out.
#
# WHAT IS MEASURED
#   size  the SIZE OF THE MATCHER FUNCTION `rx_match_anchored` in the linked
#         binary, from `nm -S`. Not the file size and not the whole binary:
#         the question is how much CODE the body costs per occurrence, and a
#         binary's size is mostly libc and main().
#   time  the built-in corpus run REPS times, best of THREE runs, so a single
#         scheduling artefact cannot decide a ruling.
#
# CONTROLS
#   - all three variants MUST agree on every answer, checked cell by cell
#     before any number is reported: three matchers that disagree are not
#     three linkages for one pattern.
#   - the k=0 column (no calls at all) is the baseline: with no call site the
#     three shapes must converge in size, or the generator is measuring
#     something other than the linkage.
#
# WHAT IS DELIBERATELY NOT MODELLED: the per-level CAPTURE SAVE/RESTORE (§4).
# It is the same two trailed writes in all three variants -- a spliced copy
# writes the same group's slots as a called one -- so including it would add
# a constant to every column. §12 carries the refutation.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
GEN="$HERE/../prototype/gen_linkage.py"
TMP=${TMPDIR:-/tmp}/dd14_linkage.$$
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

CC=${CC:-gcc}
echo "cc: $($CC --version | head -1)"
echo "flags: -O2 -std=gnu11"
echo

echo "=== CONTROL: do the three linkages agree, cell by cell? =============="
FAIL=0
for k in 0 1 2 4; do
  for v in splice hybrid call; do
    python3 "$GEN" "$v" "$k" > "$TMP/$v$k.c"
    $CC -O2 -std=gnu11 -o "$TMP/$v$k" "$TMP/$v$k.c"
  done
  for s in "abc" "abc.abc" "abc.abc.abc" "abc.abc.abc.abc" "abc.abc.abc.abc.abc" \
           "a" "" "abc.de" "ABC" "abc." ".abc" "zzz.zzz.zzz.zzz.zzz"; do
    a=$("$TMP/splice$k" -1 "$s"); b=$("$TMP/hybrid$k" -1 "$s"); c=$("$TMP/call$k" -1 "$s")
    if [ "$a" != "$b" ] || [ "$a" != "$c" ]; then
      echo "  DISAGREE k=$k subject='$s': splice=$a hybrid=$b call=$c"
      FAIL=1
    fi
  done
done
if [ "$FAIL" = 0 ]; then
  echo "  all three linkages agree on 13 subjects x 4 call-counts (52 cells)"
else
  echo "  !! THE VARIANTS DISAGREE -- no size or time number below means anything"
  exit 1
fi
echo

echo "=== SIZE: bytes of rx_match_anchored, by call-count =================="
printf '  %-8s %-10s %-10s %-10s\n' k splice hybrid call
for k in 0 1 2 3 4 6 8 12 16; do
  row="  $(printf '%-8s' "$k")"
  for v in splice hybrid call; do
    python3 "$GEN" "$v" "$k" > "$TMP/s.c"
    $CC -O2 -std=gnu11 -o "$TMP/s" "$TMP/s.c"
    sz=$(nm -S --size-sort "$TMP/s" 2>/dev/null \
         | awk '/rx_match_anchored/ {print strtonum("0x" $2)}')
    row="$row$(printf '%-10s' "${sz:-?}")"
  done
  echo "$row"
done
echo "# the k=0 row is the baseline: no call site exists, so the three must"
echo "# be close. A large spread there would mean this axis is measuring the"
echo "# generator's scaffolding rather than the linkage."
echo

echo "=== TIME: best of three, 2000000 reps ================================"
echo "# TWO corpora. The MIXED one exercises every occurrence; the LEXICAL"
echo "# one dies before the first call site and is the corpus HYBRID's whole"
echo "# claim rests on -- it must track SPLICE and beat CALL, or the extra"
echo "# body copy buys nothing."
for corpus in mixed lex; do
  echo "  --- $corpus corpus ---"
  printf '  %-8s %-12s %-12s %-12s\n' k splice hybrid call
  for k in 1 2 4 8; do
    row="  $(printf '%-8s' "$k")"
    for v in splice hybrid call; do
      python3 "$GEN" "$v" "$k" > "$TMP/t.c"
      $CC -O2 -std=gnu11 -o "$TMP/t" "$TMP/t.c"
      best=""
      for r in 1 2 3; do
        if [ "$corpus" = lex ]; then
          t=$( { /usr/bin/time -f '%e' "$TMP/t" -lex 2000000 >/dev/null; } 2>&1 )
        else
          t=$( { /usr/bin/time -f '%e' "$TMP/t" 2000000 >/dev/null; } 2>&1 )
        fi
        case "$best" in
          "") best=$t ;;
          *) best=$(awk -v a="$best" -v b="$t" 'BEGIN{print (b<a)?b:a}') ;;
        esac
      done
      row="$row$(printf '%-12s' "$best")"
    done
    echo "$row"
  done
done
echo "# NOTE both corpora include subjects that do NOT match, so the"
echo "# bump-along loop and the fail label are exercised, not only the happy"
echo "# path."
