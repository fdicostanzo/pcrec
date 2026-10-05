#!/bin/bash
# [OPT-REVEND] SCRATCH-TIER timing of today's search on end-anchored,
# start-unanchored patterns over 1 MiB prose-like subjects.
#   PCREC=/path/build/pcrec  SUBJ=/path/subjects  WORK=/path/scratch  ./run_timing.sh
# One line per (pattern, flags, subject): rc/span/min-of-7 ns and ns/B.
set -u
: "${PCREC:?}" "${SUBJ:?}" "${WORK:?}"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$WORK"
run() {  # pattern flags... -- subjects...
    local pat=$1; shift
    local flags=()
    while [ "$1" != "--" ]; do flags+=("$1"); shift; done
    shift
    local tag; tag=$(printf '%s' "$pat${flags[*]:-}" | sha1sum | cut -c1-8)
    "$PCREC" -p rx "${flags[@]}" -o "$WORK/a$tag.c" --pattern "$pat" >/dev/null 2>"$WORK/a$tag.err" || { echo "REFUSED $pat"; return; }
    cp "$WORK/a$tag.h" "$WORK/art.h"
    local stamps; stamps=$(grep -E '^#define RX_(ENGINE|DFA_PREFILTER|END_WINDOW|DFA_START) ' "$WORK/a$tag.c" | awk '{printf "%s=%s ", substr($2,4), $3}')
    gcc -O2 -I"$WORK" -o "$WORK/drv$tag" "$HERE/timedrv.c" "$WORK/a$tag.c" || { echo "CCFAIL $pat"; return; }
    for s in "$@"; do
        printf '%-18s %-18s %-14s %s | ' "$pat" "${flags[*]:-}" "$s" "$stamps"
        "$WORK/drv$tag" "$SUBJ/$s.bin" 7
    done
}
run '\d+$'        -- nomatch match_digits
run '\w+$'        -- nomatch match_word
run '\s+$'        -- nomatch match_ws
run '.*\.txt$'    -- nomatch match_txt
run '[a-z]+\.txt$' -- nomatch match_txt
run '\s*$'        -- nomatch match_ws
run '\.txt$'      -- nomatch match_txt
run '\.txt$' -fno-end-window -- nomatch match_txt
run 'abc$'        -- nomatch
run 'abc$' -fno-end-window -- nomatch
