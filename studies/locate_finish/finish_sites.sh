#!/bin/sh
# The FINISH decision as it is spelled today: every CODE line (comment lines
# dropped) under src/gen/ that tests which engine finishes the search
# (`fit.chosen`) or whether a DFA body exists in front of the VM
# (`fit.prefilter`, `prefn`).  locate_finish.md §3.3 dispositions each line;
# this script only finds them, so a later tree re-derives the list instead of
# trusting a hand-kept one.
#
#   sh studies/locate_finish/finish_sites.sh > studies/locate_finish/results/finish_sites.txt
cd "$(dirname "$0")/../.." || exit 2
for f in src/gen/emit_dfa.c src/gen/emit_vm.c; do
    grep -nE 'fit\.chosen|fit\.prefilter\b|\bprefn\b' "$f" |
    awk -v f="$f" -F: '{
        t = $0; sub(/^[0-9]+:/, "", t); s = t; gsub(/^[ \t]+/, "", s)
        if (s ~ /^(\*|\/\*|\/\/)/) next
        printf "%s:%s\t%s\n", f, $1, s
    }'
done
