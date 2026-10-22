#!/usr/bin/env bash
# e8min/nonmover_cmp.sh KIT PLAIN CENSUS PATTERNS [SETFLAG...] -- the non-mover byte check (walkcmp.sh's shape):
# every J1 pattern the census does NOT list as a mover is compiled by KIT (with SETFLAG..., e.g.
# --harness=measures=SET while B4 is unbuilt; none on the B4 branch, where the set is the default) and
# by PLAIN (main's compiler), `-o -` on both; the two texts must be byte-identical (their delta is 0
# by construction, so they are not timed). Movers are compared too and counted apart (they must DIFFER
# once B4 routes; before it they are identical). Prints one TSV line per pattern, then totals; exit 1 on a
# non-mover that differs. Scratch under $TMPDIR only.
set -u
KIT=$1 PLAIN=$2 CEN=$3 PATS=$4; shift 4
declare -A MV
while IFS=$'\t' read -r arm pat site mem shape row pick mover lk pc hu w0 qid; do
    [ "${arm:0:1}" = '#' ] && continue
    [ "$mover" = 1 ] && MV[$qid]=1
done < "$CEN"
nm=0 nmdiff=0 mv=0 mvdiff=0 refused=0
printf 'qid\tclass\tresult\n'
while IFS=$'\t' read -r qid extra pat; do
    [ "${qid:0:1}" = '#' ] && continue
    [ "$extra" = - ] && extra=; read -ra ex <<< "$extra"
    a=$("$KIT" -p rx --features all "${ex[@]}" "$@" -o - --pattern "$pat" 2>/dev/null; echo "rc=$?")
    b=$("$PLAIN" -p rx --features all "${ex[@]}" -o - --pattern "$pat" 2>/dev/null; echo "rc=$?")
    if [ "$a" = "$b" ]; then r=identical; else r=DIFFERS; fi
    case "$a" in *rc=0) ;; *) [ "$r" = identical ] && r=refused-in-both;; esac
    if [ -n "${MV[$qid]:-}" ]; then c=mover; mv=$((mv+1)); [ "$r" = DIFFERS ] && mvdiff=$((mvdiff+1))
    else c=non-mover; nm=$((nm+1)); [ "$r" = DIFFERS ] && nmdiff=$((nmdiff+1)); [ "$r" = refused-in-both ] && refused=$((refused+1)); fi
    printf '%s\t%s\t%s\n' "$qid" "$c" "$r"
done < "$PATS"
echo "# non-movers $nm (refused in both $refused), differing $nmdiff; movers $mv, differing $mvdiff"
[ "$nmdiff" = 0 ]
