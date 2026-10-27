#!/usr/bin/env bash
# tests/code/card_inline.sh — the INLINE-MODE measurement card ([INLINE-C]
# stage 2; docs/design/inline_c.md goal 3b and standing question 1; memory
# "new method needs measurement card").
#
# THE QUESTION IT ANSWERS: does an embedded segment cost only its fires? Per
# pattern, three artifacts of the same text:
#   inline  the pattern with the empty predicate `(?C`c: return RX_PASS;`)`
#   twin    the same pattern with the segment removed, `--engine=vm`
#   count   the inline pattern with a counting segment, run once to read n,
#           the fires per pass (DT-4.1's counting binding, inline)
# and one driver per artifact that searches the subject PASSES times (find
# all, non-overlapping). Each artifact is timed REPEATS times, interleaved;
# the A/A spread is the twin's own (max-min)/median over its repeats. The
# card's verdict per pattern is `within` when inline's median is at most
# twin's median plus the spread, else `over`; on a box nobody has cleared
# for timing the verdict is meaningless and every row says UNMEASURED.
#
# Usage: card_inline.sh [--smoke] [--timed] [-o OUT.tsv]
#   --smoke   tiny subject, one repeat: proves the card BUILDS and RUNS (the
#             make test arm); never a timing
#   --timed   a real run (bench window only: docs/dev/lanes/BOILERPLATE.md);
#             without it every verdict is UNMEASURED
# Env: PCREC, CC (gcc), CARD_REPEATS (default 9), CARD_BYTES (default 4 MiB).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
smoke=0; timed=0; out=/dev/stdout
while [ $# -gt 0 ]; do
    case "$1" in
        --smoke) smoke=1 ;;
        --timed) timed=1 ;;
        -o) out="$2"; shift ;;
        *) echo "card_inline.sh: unknown argument $1" >&2; exit 2 ;;
    esac
    shift
done
REPEATS="${CARD_REPEATS:-9}"; BYTES="${CARD_BYTES:-4194304}"
[ "$smoke" = 1 ] && { REPEATS=1; BYTES=4096; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/card_inline.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# name | pattern with @ where the segment goes | subject unit (hit-dense)
ROWS='site_hit|(\d+)@x|12x 345x 6x |
site_miss|(\d+)@x|12y 345y 6y |
tail|[a-z]+=\d+@|key=12 val=345 |'

cat > "$WORK/drv.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define PASTE2(a, b) a##b
#define PASTE(a, b) PASTE2(a, b)
#define SEARCH PASTE(PX, _search)
#define NCAPS PASTE(UPX, _NCAPS)
#ifdef COUNT
#include "count.h"
#endif
int main(int argc, char **argv)
{
    const char *unit = argv[1];
    size_t bytes = strtoul(argv[2], NULL, 10), ul = strlen(unit);
    unsigned char *s = malloc(bytes + ul);
    size_t n = 0;
    while (n < bytes) { memcpy(s + n, unit, ul); n += ul; }
    ptrdiff_t c[NCAPS][2];
    long hits = 0;
    struct timespec a, b;
    clock_gettime(CLOCK_MONOTONIC, &a);
    for (size_t at = 0; at <= n && SEARCH(s, n, at, c) == 1; hits++)
        at = (size_t)c[0][1] > at ? (size_t)c[0][1] : at + 1;
    clock_gettime(CLOCK_MONOTONIC, &b);
    double ns = (b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec);
#ifdef COUNT
    printf("%ld %ld\n", hits, card_fires);
#else
    printf("%ld %.4f\n", hits, ns / (double)n);
#endif
    (void)argc;
    return 0;
}
C
printf 'static long card_fires;\n' > "$WORK/count.h"

build() {   # build PX PATTERN [extra pcrec args...] -> $WORK/PX
    local px="$1" pat="$2"; shift 2
    local upx; upx="$(printf '%s' "$px" | tr '[:lower:]' '[:upper:]')"
    "$PCREC" -p "$px" "$@" -o "$WORK/$px.c" --pattern "$pat" || return 1
    printf '#include "%s.c"\n#include "drv.c"\n' "$px" > "$WORK/u_$px.c"
    "$CC" -O2 -std=gnu11 -I"$WORK" -DPX="$px" -DUPX="$upx" ${CDEF:-} \
        -o "$WORK/$px" "$WORK/u_$px.c" || return 1
}
median() { sort -g | awk '{v[NR]=$1} END {print (NR%2) ? v[(NR+1)/2] : (v[NR/2]+v[NR/2+1])/2}'; }

status=0
printf 'card\tpattern\tbytes\tfires\tinline_ns_per_byte\ttwin_ns_per_byte\taa_spread\tverdict\n' > "$out"
while IFS='|' read -r name pat unit _; do
    [ -z "$name" ] && continue
    pin="${pat//@/(?C\`c: return RX_PASS;\`)}"
    pcount="${pat//@/(?C\`c: card_fires++; return RX_PASS;\`)}"
    ptwin="${pat//@/}"
    if ! build "i_$name" "$pin" --allow-code=c || \
       ! build "t_$name" "$ptwin" --engine=vm || \
       ! CDEF=-DCOUNT build "c_$name" "$pcount" --allow-code=c --code-header 'c:"count.h"'; then
        echo "card_inline: $name did not build" >&2
        status=1
        continue
    fi
    fires="$("$WORK/c_$name" "$unit" "$BYTES" | awk '{print $2}')"
    : > "$WORK/i.t"; : > "$WORK/t.t"
    for _r in $(seq "$REPEATS"); do
        "$WORK/i_$name" "$unit" "$BYTES" | awk '{print $2}' >> "$WORK/i.t"
        "$WORK/t_$name" "$unit" "$BYTES" | awk '{print $2}' >> "$WORK/t.t"
    done
    hi="$(head -1 < <("$WORK/i_$name" "$unit" 64))"; ht="$(head -1 < <("$WORK/t_$name" "$unit" 64))"
    if [ "${hi%% *}" != "${ht%% *}" ]; then
        echo "card_inline: $name: inline and twin disagree on the hit count ($hi vs $ht)" >&2
        status=1
    fi
    mi="$(median < "$WORK/i.t")"; mt="$(median < "$WORK/t.t")"
    sp="$(sort -g "$WORK/t.t" | awk -v m="$mt" 'NR==1{lo=$1} {hi=$1} END {print (m > 0) ? (hi-lo)/m : 0}')"
    if [ "$timed" = 1 ]; then
        verdict="$(awk -v i="$mi" -v t="$mt" -v s="$sp" 'BEGIN {print (i <= t * (1 + s)) ? "within" : "over"}')"
    else
        verdict=UNMEASURED
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "inline:$name" "$pat" "$BYTES" "$fires" "$mi" "$mt" "$sp" "$verdict" >> "$out"
done <<< "$ROWS"
exit $status
