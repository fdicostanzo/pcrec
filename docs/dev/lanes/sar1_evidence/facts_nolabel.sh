#!/usr/bin/env bash
# facts_nolabel.sh: exec wrapper for ident_check's emit_sweep runs (sar1mrg). FACTS_REAL = the real build/pcrec.
# Under --emit-facts it strips the note column's leading core/derived provenance label (req_whole_run is DERIVED
# since R1; census_r1.py drops the same label, so the census's movers are value/why movers only); every other
# call is a plain exec. Usage: write a two-line wrapper per side: FACTS_REAL=/path/pcrec exec facts_nolabel.sh "$@"
real=${FACTS_REAL:?FACTS_REAL unset}
for a in "$@"; do
    case "$a" in
    --emit-facts*)
        set -o pipefail
        "$real" "$@" | awk -F'\t' -v OFS='\t' '{ if (NF>=9 && $9 ~ /^(core|derived)(;|$)/) { n=index($9,";"); $9 = (n ? substr($9,n+1) : ""); sub(/^ /,"",$9) } print }'
        exit "${PIPESTATUS[0]}" ;;
    esac
done
exec "$real" "$@"
