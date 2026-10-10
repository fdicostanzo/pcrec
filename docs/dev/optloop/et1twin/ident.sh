#!/bin/sh
# docs/dev/optloop/et1twin/ident.sh -- the answer-identity check per cell:
# today's artifact (o), the twin (t) and libpcre2-8 (p2) over
#   - the bench set's short subjects and throughput subjects (regenerated
#     in a read-only COPY of pcrec-bench, sha-checked against its manifests)
#   - gen_adv.py's adversarial subjects
# each subject as one find-all pass plus single searches from every
# startpos (etdrv.c `ident`). Prints per cell the subject counts and the
# number of lines on which o/t/p2 disagree; exits 1 on any disagreement.
#   OUT=build/et1twin BENCHCOPY=<copy with generators run> BENCH=<pcrec-bench> ./ident.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?}; BC=${BENCHCOPY:?}; B=${BENCH:?}
rc=0
for spec in ipv6:loglines kvq:loglines sfx64:altwide; do
    c=${spec%%:*}; set_=${spec#*:}; d=$OUT/$c
    python3 "$H/gen_adv.py" "$c" "$B" "$d/adv" 400
    subs="$(ls "$BC"/bench/$set_/subjects/*.bin "$BC"/bench/$set_/throughput/*.bin) $(ls "$d"/adv/*.bin)"
    for v in o t; do "$d/$v" ident $subs > "$d/ident.$v"; done
    "$d/p2" "$d/pat" $subs > "$d/ident.p2"
    n=$(wc -l < "$d/ident.o")
    ot=$(diff "$d/ident.o" "$d/ident.t" | grep -c '^<' || true)
    op=$(diff "$d/ident.o" "$d/ident.p2" | grep -c '^<' || true)
    tp=$(diff "$d/ident.t" "$d/ident.p2" | grep -c '^<' || true)
    fa=$(awk -F'\t' '{split($3,a,"="); s+=a[2]} END {print s}' "$d/ident.o")
    sp=$(awk -F'\t' '{split($5,a,"[=/]"); h+=a[2]; t+=a[3]} END {print h"/"t}' "$d/ident.o")
    echo "$c\tsubjects=$n\tfindall_matches=$fa\tstartpos_hits/searches=$sp\tdiff(o,t)=$ot\tdiff(o,p2)=$op\tdiff(t,p2)=$tp"
    [ "$ot$op$tp" = "000" ] || rc=1
done
exit $rc
