#!/bin/sh
# docs/dev/optloop/rlhbuild/ident.sh -- answer identity per cell: base
# (main) against new, deny, newm and libpcre2-8 10.46 (p2), each subject as
# one find-all pass plus single searches from every startpos (et1twin's
# etdrv `ident`). Subjects: the cell's bench short + throughput subjects
# (regenerated in a read-only COPY of pcrec-bench) + 400 adversarial
# subjects (rlhtwin's gen_adv.py for ipv6/ipv4/dotted4, et1twin's for
# kvq/sfx64, gen_hostile.py for the K-admission cells). Prints the
# disagreeing-line count per pair; exits 1 on any.
#   OUT=<dir> BENCHCOPY=<copy> BENCH=<pcrec-bench> ./ident.sh [CELL...]
set -e
H=$(cd "$(dirname "$0")" && pwd); E=$H/../et1twin; R=$H/../rlhtwin
OUT=${OUT:?}; BC=${BENCHCOPY:?}; B=${BENCH:?}
rc=0
CELLS=${*:-"ipv6 ipv4 dotted4 sfx64 kvq hostile hcolon hcolon_in"}
for c in $CELLS; do
    d=$OUT/$c
    case $c in
    ipv6|ipv4) set_=loglines; python3 -I "$R/gen_adv.py" "$c" "$d/adv" 400 ;;
    dotted4)   set_=bounded;  python3 -I "$R/gen_adv.py" ipv4 "$d/adv" 400 ;;
    kvq)       set_=loglines; python3 -I "$E/gen_adv.py" kvq "$B" "$d/adv" 400 ;;
    sfx64)     set_=altwide;  python3 -I "$E/gen_adv.py" sfx64 "$B" "$d/adv" 400 ;;
    *)         set_=;         python3 -I "$H/gen_hostile.py" "$d/adv" ;;
    esac
    if [ -n "$set_" ]; then
        subs="$(ls "$BC"/bench/$set_/subjects/*.bin "$BC"/bench/$set_/throughput/*.bin) $(ls "$d"/adv/*.bin)"
    else
        subs="$(ls "$d"/adv/adv_*.bin "$d"/adv/*-0004k.bin "$d"/adv/*-0064k.bin)"
    fi
    for v in base new deny newm; do "$d/$v" ident $subs > "$d/ident.$v"; done
    "$d/p2" "$d/pat" $subs > "$d/ident.p2"
    n=$(wc -l < "$d/ident.base")
    fa=$(awk -F'\t' '{split($3,a,"="); s+=a[2]} END {print s}' "$d/ident.base")
    sp=$(awk -F'\t' '{split($5,a,"[=/]"); h+=a[2]; t+=a[3]} END {print h"/"t}' "$d/ident.base")
    line="$c\tsubjects=$n\tfindall_matches=$fa\tstartpos_hits/searches=$sp"
    for v in new deny newm p2; do
        x=$(diff "$d/ident.base" "$d/ident.$v" | grep -c '^<' || true)
        line="$line\tdiff(base,$v)=$x"
        [ "$x" = 0 ] || rc=1
    done
    printf "$line\n"
done
exit $rc
