#!/usr/bin/env bash
# tests/landwalk/card_lwalk.sh — the LANDMARK WALK's measurement card
# ([LANDWALK-CARD]; docs/dev/lanes/p1dsg3_report.md "Measurement card";
# memory "new method needs measurement card"). Timing only, in walkbytes
# (the forward DFA scan's own cost per byte, measured in the same run), with
# the card's two rows:
#
#   lwhit   per landmark hit, by the walked width `wlen` in {2, 8, 32} and an
#           ARM: `miss` (the walk finds a start, the verify fails) and `hit`
#           (the verify matches and the match is reported). The subject is one
#           unit repeated, `<wlen letters>@y ` (miss) or `<wlen letters>@x `
#           (hit), searched find-all by `[a-z]+@x`; a row is the unit's whole
#           time (the hit search between landmarks included), beside the
#           denied twin's over the same unit. The fit `a + b*wlen` per arm is
#           printed beside the rows (`lwfit`).
#   lwcall  the per-call fixed term: a 5-byte subject `ab@x ` searched once
#           per call, walk against `-fno-landmark-walk`.
#
# `u` (ns per byte) is one forward DFA step: the denied artifact built
# `-fno-scan-edge` too (so no edge loop skips the run) over a letter run (the
# kit's u is the same quantity, beta_walk(DFA_SCAN)); every walkbytes value is
# ns / u. Each arm is
# timed REPEATS times; the A/A spread is the denied twin's own
# (max-min)/median. On a box nobody cleared for timing every row's verdict
# is UNMEASURED and the numbers are not a measurement. Beside the time, each
# arm's user-mode instruction count (`perf stat -e instructions:u`; NA where
# perf cannot count), which is not a timing and so is read on any box.
#
# The rarity row's per-hit constant `k_hit` (LMWALK_K_HIT_UNMEASURED,
# src/gen/lmwalk.c) is this card's `lwhit` intercept, an UNMEASURED default
# until a measurement set carries it ([MEASURE-SET] M3's cards.tsv).
#
# Usage: card_lwalk.sh [--smoke] [--timed] [-o OUT.tsv]
#   --smoke   tiny subjects, one repeat: proves the card BUILDS and RUNS
#             (run_landmark_walk.sh calls it); never a timing
#   --timed   a real run (a cleared timing window only); without it every
#             verdict is UNMEASURED
# Env: PCREC, CC (gcc), CARD_REPEATS (default 9), CARD_BYTES (default 4 MiB),
#      CARD_CALLS (default 2,000,000).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh" >/dev/null
smoke=0; timed=0; out=/dev/stdout
while [ $# -gt 0 ]; do
    case "$1" in
        --smoke) smoke=1 ;;
        --timed) timed=1 ;;
        -o) out="$2"; shift ;;
        *) echo "card_lwalk.sh: unknown argument $1" >&2; exit 2 ;;
    esac
    shift
done
REPEATS="${CARD_REPEATS:-9}"; BYTES="${CARD_BYTES:-4194304}"; CALLS="${CARD_CALLS:-2000000}"
[ "$smoke" = 1 ] && { REPEATS=1; BYTES=4096; CALLS=1000; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/card_lwalk.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# MODE find: find-all over BYTES of UNIT repeated, its last three bytes
# replaced by ` @x`, prints `hits ns_per_byte`.
# MODE call: CALLS searches of UNIT itself, prints `hits ns_per_call`.
cat > "$WORK/drv.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define PASTE2(a, b) a##b
#define PASTE(a, b) PASTE2(a, b)
#define SEARCH PASTE(PX, _search)
#define NCAPS PASTE(UPX, _NCAPS)
int main(int argc, char **argv)
{
    const char *mode = argv[1], *unit = argv[2];
    size_t count = strtoul(argv[3], NULL, 10), ul = strlen(unit), n = 0;
    int call = strcmp(mode, "call") == 0;
    size_t bytes = call ? ul : count;
    unsigned char *s = malloc(bytes + ul);
    while (n < bytes) { memcpy(s + n, unit, ul); n += ul; }
    /* find: the subject ends in " @x", so the pattern's required run is
     * present (no whole-window pre-check answers a miss subject early) and
     * the ending adds no match */
    if (!call && n >= 3) memcpy(s + n - 3, " @x", 3);
    ptrdiff_t c[NCAPS][2];
    long hits = 0;
    struct timespec a, b;
    clock_gettime(CLOCK_MONOTONIC, &a);
    if (call) {
        for (size_t k = 0; k < count; k++) hits += SEARCH(s, n, 0, c) == 1;
    } else {
        for (size_t at = 0; at <= n && SEARCH(s, n, at, c) == 1; hits++)
            at = (size_t)c[0][1] > at ? (size_t)c[0][1] : at + 1;
    }
    clock_gettime(CLOCK_MONOTONIC, &b);
    double ns = (b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec);
    printf("%ld %.4f\n", hits, ns / (double)(call ? count : n));
    (void)argc;
    return 0;
}
C

build() {   # build PX [pcrec args...] -> $WORK/PX
    local px="$1"; shift
    local upx; upx="$(printf '%s' "$px" | tr '[:lower:]' '[:upper:]')"
    "$TIMEOUT_BIN" 60 "$PCREC" --features all -p "$px" "$@" -o "$WORK/$px.c" || return 1
    printf '#include "%s.c"\n#include "drv.c"\n' "$px" > "$WORK/u_$px.c"
    "$TIMEOUT_BIN" 120 "$CC" -O2 -std=gnu11 -I"$WORK" -DPX="$px" -DUPX="$upx" \
        -o "$WORK/$px" "$WORK/u_$px.c" || return 1
}
instr() {   # instr BIN ARGS... -> user-mode instructions, or NA
    local v
    v="$(perf stat -x, -e instructions:u "$@" 2>&1 >/dev/null | awk -F, '$3 ~ /^instructions/ {print $1}')"
    case "$v" in ''|*[!0-9]*) echo NA ;; *) echo "$v" ;; esac
}
median() { sort -g | awk '{v[NR]=$1} END {print (NR%2) ? v[(NR+1)/2] : (v[NR/2]+v[NR/2+1])/2}'; }
# timeit BIN MODE UNIT COUNT -> median of REPEATS (field 2), hits in $WORK/hits
timeit() {
    local bin="$1"; shift
    : > "$WORK/t.t"
    for _r in $(seq "$REPEATS"); do
        "$bin" "$@" > "$WORK/one" || return 1
        awk '{print $2}' "$WORK/one" >> "$WORK/t.t"
        awk '{print $1}' "$WORK/one" > "$WORK/hits"
    done
    median < "$WORK/t.t"
}

PAT='[a-z]+@x'
status=0
if ! build lw --pattern "$PAT" || ! build fw -fno-landmark-walk --pattern "$PAT" ||
   ! build uw -fno-landmark-walk -fno-scan-edge --pattern "$PAT"; then
    echo "card_lwalk: the walk or its denied twin did not build" >&2; exit 1
fi
grep -q '^#define LW_DFA_SCAN "landmark-walk"$' "$WORK/lw.c" \
    || { echo "card_lwalk: '$PAT' no longer takes the walk; the card measures nothing" >&2; exit 1; }

u="$(timeit "$WORK/uw" find 'abcdefghijklmnopqrstuvwxyz' "$BYTES")" || exit 1
printf 'card\trow\twlen\tarm\tbytes\thits\twalk_ns\tdenied_ns\tunit\twalk_wb\tdenied_wb\taa_spread\twalk_instr\tdenied_instr\tverdict\n' > "$out"
fitrows=""
for arm in miss hit; do
    for wlen in 2 8 32; do
        w="$(head -c "$wlen" < <(yes abcdefghijklmnopqrstuvwxyz | tr -d '\n'))"
        [ "$arm" = miss ] && unit="$w@y " || unit="$w@x "
        tl="$(timeit "$WORK/lw" find "$unit" "$BYTES")" || { status=1; continue; }
        hl="$(cat "$WORK/hits")"
        tf="$(timeit "$WORK/fw" find "$unit" "$BYTES")" || { status=1; continue; }
        hf="$(cat "$WORK/hits")"
        [ "$hl" = "$hf" ] || { echo "card_lwalk: lwhit $wlen $arm: hit counts disagree ($hl vs $hf)" >&2; status=1; }
        sp="$(sort -g "$WORK/t.t" | awk -v m="$tf" 'NR==1{lo=$1} {hi=$1} END {print (m > 0) ? (hi-lo)/m : 0}')"
        ul=${#unit}
        # per hit: ns per byte times the unit length (one landmark per unit)
        read -r wl wf < <(awk -v a="$tl" -v b="$tf" -v l="$ul" -v u="$u" 'BEGIN {printf "%.2f %.2f\n", a*l/u, b*l/u}')
        il="$(instr "$WORK/lw" find "$unit" "$BYTES")"; if_="$(instr "$WORK/fw" find "$unit" "$BYTES")"
        verdict=UNMEASURED; [ "$timed" = 1 ] && verdict=measured
        printf 'lwalk\tlwhit\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$wlen" "$arm" "$BYTES" "$hl" "$tl" "$tf" "$u" "$wl" "$wf" "$sp" "$il" "$if_" "$verdict" >> "$out"
        fitrows="$fitrows$arm $wlen $wl"$'\n'
    done
done
# the per-arm least-squares fit a + b*wlen (walkbytes per hit)
printf '%s' "$fitrows" | awk -v v="$([ "$timed" = 1 ] && echo measured || echo UNMEASURED)" '
    { n[$1]++; sx[$1]+=$2; sy[$1]+=$3; sxx[$1]+=$2*$2; sxy[$1]+=$2*$3 }
    END { for (a in n) { d = n[a]*sxx[a] - sx[a]*sx[a]; b = d ? (n[a]*sxy[a] - sx[a]*sy[a]) / d : 0
          printf "lwalk\tlwfit\t-\t%s\t-\t-\t-\t-\t-\ta=%.2f\tb=%.3f\t-\t-\t-\t%s\n", a, (sy[a] - b*sx[a]) / n[a], b, v } }' >> "$out"
# lwcall: the per-call fixed term on a short subject (ns per call)
tl="$(timeit "$WORK/lw" call 'ab@x ' "$CALLS")" && tf="$(timeit "$WORK/fw" call 'ab@x ' "$CALLS")" || status=1
sp="$(sort -g "$WORK/t.t" | awk -v m="${tf:-0}" 'NR==1{lo=$1} {hi=$1} END {print (m > 0) ? (hi-lo)/m : 0}')"
il="$(instr "$WORK/lw" call 'ab@x ' "$CALLS")"; if_="$(instr "$WORK/fw" call 'ab@x ' "$CALLS")"
verdict=UNMEASURED; [ "$timed" = 1 ] && verdict=measured
printf 'lwalk\tlwcall\t-\t-\t5\t%s\t%s\t%s\t-\t-\t-\t%s\t%s\t%s\t%s\n' \
    "$CALLS" "${tl:-NA}" "${tf:-NA}" "$sp" "$il" "$if_" "$verdict" >> "$out"
exit $status
