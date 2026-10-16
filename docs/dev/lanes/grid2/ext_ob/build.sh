#!/bin/bash
# grid2/ext_ob/build.sh -- builds the one-byte cells (items 3, 4) under $OUT/bin. Contract:
# grid1/README.md "External arm sets": run with OUT, GRID (grid1's directory), CPUS, JOBS in
# the environment; leaves bin/<cell>/<arm>/{run,chk} for every row of ../arms.tsv.
# PCREC (the kit-branch compiler) and G2 (the grid2 directory) come from grid2/build.sh.
#
# The five cells are emitted by the compiler with -fno-req-byte -fno-req-run: the
# whole-window pre-check would answer a member-free subject before the site ran (the site
# would be UNREACHED, the row would time the pre-check). That is a property of these
# cells, stated here; item 8 (ext trig) measures the pre-check on its own.
#   cell    pattern              extra flags                       memchr byte
#   o-fwd   xy+z                                                  120   DFA_SCAN forward
#   o-bnd   xy+(?=z)                                              120   DFA_SCAN bounded (memchr-bounded)
#   o-hat   \bx[a-z]+\b                                           120   DFA_HAT (first-memchr-bounded)
#   o-hyb   xy+z                 --engine=vm -fprefilter          120   HYB_PF
#   o-back  (?m)^xy+z                                              10   DFA_ATTEMPT (the (?m)^ skip; rev 3's name for ATTEMPT_PRED)
#   o-vm    xy+z                 --engine=vm                      120   VM_ATTEMPT [rev3 A7]: the VM hat's seek at |S| = 1
#                                (RX_VM_START_SCAN "first-class"); NEW = the default compile (the compiler's own
#                                V1 text), DENY = --memfn=no-pf-terms-mask (the table walk): arms walk, libc, v1
set -u
: "${OUT:?}" "${GRID:?}" "${G2:?}" "${PCREC:?}"
CPUS=${CPUS:-12-15}; JOBS=${JOBS:-4}; CC=${CC:-gcc}
L=$OUT/lib
HDR=$OUT/art/dig/new/art.c        # carries the kit's W8 block (PCREC_MFK_W8_H)
CELLS="o-fwd|xy+z||120
o-bnd|xy+(?=z)||120
o-hat|\\bx[a-z]+\\b||120
o-hyb|xy+z|--engine=vm -fprefilter|120
o-back|(?m)^xy+z||10
o-vm|xy+z|--engine=vm|120"
jobs=$OUT/tmp/ob.jobs; : > "$jobs"
arms_of_cell() { case "$1" in o-back) echo "walk libc none" ;; o-vm) echo "walk libc v1" ;; *) echo "walk libc loop v1 none" ;; esac; }
while IFS='|' read -r c pat extra byte; do
  d0=$OUT/art/$c; mkdir -p "$d0"
  # shellcheck disable=SC2086
  "$PCREC" --features all -fno-req-byte -fno-req-run $extra -p rx -o "$d0/art.c" --pattern "$pat" || { echo "EMIT FAILED $c"; exit 1; }
  if [ "$c" = o-vm ]; then     # the deny compile lives beside it, at the same -o basename (art.c)
    mkdir -p "$d0/deny"
    # shellcheck disable=SC2086
    "$PCREC" --features all -fno-req-byte -fno-req-run $extra --memfn=no-pf-terms-mask -p rx -o "$d0/deny/art.c" --pattern "$pat" || { echo "EMIT FAILED $c deny"; exit 1; }
    cmp -s "$d0/art.c" "$d0/deny/art.c" && { echo "FATAL: $c new == deny (the VM hat does not take the kit's V1 form: not a mover)"; exit 1; }
  fi
  arms=$(arms_of_cell "$c")
  for a in $arms; do
    d=$OUT/bin/$c/$a; mkdir -p "$d"
    if [ "$c" = o-vm ]; then
      hsrc=$d0/deny/art.h; [ "$a" = v1 ] && hsrc=$d0/art.h
      cp "$hsrc" "$d/art.h"
      python3 -I "$G2/mkvar2.py" vm "$d0/deny/art.c" "$d0/art.c" "$d/art.c" "$a" "$byte" || { echo "MKVAR2 FAILED $c $a"; exit 1; }
    else
      cp "$d0/art.h" "$d/"
      python3 -I "$G2/mkvar2.py" ob "$d0/art.c" "$d/art.c" "$a" "$byte" "$HDR" || { echo "MKVAR2 FAILED $c $a"; exit 1; }
    fi
    echo "$CC -O2 -I$d -I$L -c $d/art.c -o $d/art.o && $CC -O2 -I$d -I$L -c $L/gdrv.c -o $d/gdrv.o && $CC -o $d/run $d/gdrv.o $d/art.o && $CC -O2 -I$d -I$L -o $d/chk $L/gchk.c $d/art.o" >> "$jobs"
    # the walk arm also gets `cnt` (the reach leg U2: g2_find call/byte counts, -DG2_COUNT)
    [ "$a" = walk ] && echo "$CC -O2 -DG2_COUNT -I$d -I$L -o $d/cnt $L/gchk.c $d/art.c" >> "$jobs"
  done
done <<< "$CELLS"
tr '\n' '\0' < "$jobs" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' > "$OUT/tmp/ob.build.out" 2>&1
grep -E 'error|warning: implicit' "$OUT/tmp/ob.build.out" | head
fail=0
while IFS='|' read -r c pat extra byte; do
  arms=$(arms_of_cell "$c")
  for a in $arms; do for b in run chk; do [ -x "$OUT/bin/$c/$a/$b" ] || { echo "MISSING $c/$a/$b"; fail=1; }; done; done
done <<< "$CELLS"
[ "$fail" = 0 ] || exit 1
echo "ext ob: built"
