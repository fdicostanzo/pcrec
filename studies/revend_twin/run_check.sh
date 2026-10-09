#!/bin/bash
# [OPT-REVEND] hand-twin answer identity over patterns.tsv (STUDY).
#   PCREC=build/pcrec [PATTERNS=file.tsv] [TWIN_FORM=exact|lower] [TWIN_SABOTAGE=noeol|firstseed] ./run_check.sh
# (TWIN_SABOTAGE is a CONTROL: the sweep must then report twin_diff > 0)
# Per pattern: emit the artifact twice (-p o, -p t) with the bench's flags
# (--features all; -e utf8 on utf8 rows), twin the t copy (mktwin.py), build
# check.c against libpcre2-8 and sweep the pools. Generated files go to work/
# (gitignored). Exit status: 1 if any twin disagreed with its artifact.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
: "${PCREC:?set PCREC to a built pcrec}"
W=$HERE/work; S=$W/subj; A=$W/art${TWIN_FORM:+-$TWIN_FORM}${TWIN_SABOTAGE:+-$TWIN_SABOTAGE}; mkdir -p "$A"
[ -f "$S/pool_byte.hex" ] || python3 "$HERE/mksubj.py" "$(git -C "$HERE" rev-parse --show-toplevel)" "$S" >/dev/null
bad=0
while IFS=$'\t' read -r name enc eol pat; do
    case "$name" in ''|'#'*) continue ;; esac
    d=$A/$name; mkdir -p "$d"
    for p in o t; do
        "$PCREC" --features all -e "$enc" -p $p -o "$d/$p.c" --pattern "$pat" 2>"$d/$p.err" \
            || { echo "$name REFUSED: $(cat "$d/$p.err")"; continue 2; }
    done
    stamps=$(grep -E '^#define O_(ENGINE|DFA_PREFILTER|DFA_START|END_WINDOW) ' "$d/o.c" | awk '{printf "%s=%s ", substr($2,3), $3}')
    if ! python3 "$HERE/mktwin.py" "$d/t.c" "$d/t.c.twin" t "$eol" 2>"$d/twin.err"; then
        echo "$name NOT-TWINNABLE ($stamps): $(cat "$d/twin.err")"; continue
    fi
    mv "$d/t.c.twin" "$d/t.c"
    gcc -O2 -w -I"$d" -o "$d/check" "$HERE/check.c" "$d/o.c" "$d/t.c" -lpcre2-8 || { echo "$name CCFAIL"; bad=1; continue; }
    pools="$S/pool_$enc.hex"; [ "$enc" = byte ] && pools="$pools $S/long.hex"
    for pool in $pools; do
        printf '%-20s %-6s ' "$name" "$(basename "$pool" .hex)"
        gnutimeout 600 "$d/check" "$pat" "$enc" "$pool" || bad=1
    done
    echo "    stamps: $stamps"
done < "${PATTERNS:-$HERE/patterns.tsv}"
exit $bad
