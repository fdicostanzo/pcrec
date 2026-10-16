#!/bin/bash
# grid2/ext_trig/build.sh -- item 8, the pre-scan TRIGGER PROBE: KEEP vs DROP of the
# whole-window required-byte pre-check on DFA-route cells with OPTIONAL presence. Contract
# as ext_ob/build.sh. keep = the kit compiler's default compile; drop = the same pattern
# with -fno-req-byte -fno-req-run (r17b_prime §5.4 item 8).
#   trig-dig   [0-9]+x      REQ byte x      trig-word  [A-Za-z_]+=   REQ byte =
set -u
: "${OUT:?}" "${PCREC:?}"
CPUS=${CPUS:-12-15}; JOBS=${JOBS:-4}; CC=${CC:-gcc}
L=$OUT/lib
jobs=$OUT/tmp/trig.jobs; : > "$jobs"
CELLS='trig-dig|[0-9]+x
trig-word|[A-Za-z_]+='
while IFS='|' read -r c pat; do
  for a in keep drop; do
    d=$OUT/bin/$c/$a; mkdir -p "$d"
    fl=""; [ "$a" = drop ] && fl="-fno-req-byte -fno-req-run"
    # shellcheck disable=SC2086
    "$PCREC" $fl -p rx -o "$d/art.c" --pattern "$pat" || { echo "EMIT FAILED $c $a"; exit 1; }
    echo "$CC -O2 -I$d -I$L -c $d/art.c -o $d/art.o && $CC -O2 -I$d -I$L -c $L/gdrv.c -o $d/gdrv.o && $CC -o $d/run $d/gdrv.o $d/art.o && $CC -O2 -I$d -I$L -o $d/chk $L/gchk.c $d/art.o" >> "$jobs"
  done
  cmp -s "$OUT/bin/$c/keep/art.c" "$OUT/bin/$c/drop/art.c" && { echo "FATAL: $c keep == drop (the pre-check is not a mover)"; exit 1; }
done <<< "$CELLS"
tr '\n' '\0' < "$jobs" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' > "$OUT/tmp/trig.build.out" 2>&1
grep -E 'error' "$OUT/tmp/trig.build.out" | head
while IFS='|' read -r c pat; do for a in keep drop; do for b in run chk; do [ -x "$OUT/bin/$c/$a/$b" ] || { echo "MISSING $c/$a/$b"; exit 1; }; done; done; done <<< "$CELLS"
echo "ext trig: built"
