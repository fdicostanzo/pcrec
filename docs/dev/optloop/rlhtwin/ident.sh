#!/bin/sh
# docs/dev/optloop/rlhtwin/ident.sh -- the answer-identity check per cell:
# today (o) against every variant (h1 h1m h2 r) and against libpcre2-8
# 10.46 (p2), over the loglines short subjects + throughput subjects
# (regenerated in a read-only COPY of pcrec-bench, manifests compared) and
# gen_adv.py's adversarial subjects; each subject as one find-all pass plus
# single searches from every startpos (et1twin's etdrv `ident`). Prints the
# disagreeing-line count per pair; exits 1 on any.
#   OUT=build/rlh/cells BENCHCOPY=<copy> ./ident.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?}; BC=${BENCHCOPY:?}
rc=0
for c in ipv6 ipv4; do
    d=$OUT/$c
    python3 -I "$H/gen_adv.py" "$c" "$d/adv" 400
    subs="$(ls "$BC"/bench/loglines/subjects/*.bin "$BC"/bench/loglines/throughput/*.bin) $(ls "$d"/adv/*.bin)"
    for v in o h1 h1m h2 r; do "$d/$v" ident $subs > "$d/ident.$v"; done
    "$d/p2" "$d/pat" $subs > "$d/ident.p2"
    n=$(wc -l < "$d/ident.o")
    fa=$(awk -F'\t' '{split($3,a,"="); s+=a[2]} END {print s}' "$d/ident.o")
    sp=$(awk -F'\t' '{split($5,a,"[=/]"); h+=a[2]; t+=a[3]} END {print h"/"t}' "$d/ident.o")
    line="$c\tsubjects=$n\tfindall_matches=$fa\tstartpos_hits/searches=$sp"
    for v in h1 h1m h2 r p2; do
        x=$(diff "$d/ident.o" "$d/ident.$v" | grep -c '^<' || true)
        line="$line\tdiff(o,$v)=$x"
        [ "$x" = 0 ] || rc=1
    done
    printf "$line\n"
done
exit $rc
