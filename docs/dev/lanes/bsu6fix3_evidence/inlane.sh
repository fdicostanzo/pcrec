#!/bin/bash
# lane bsu6fix3: bsu6fix2's inlane.sh re-aimed at worktrees/bsu6fix3 + scratch/bsu6fix3 (paths only). Was: lane bsu6fix2's in-lane runs (bsu6fix's runner, re-aimed; the g1 stage's verdict is now the CASES' dry verdicts), one STAGE per call (each run under `scripts/boxlock run`, or as its own queue job):
#   selftest | mutants | dryfull | g1 | strict | arch
# Logs: /var/tmp/pcrec-pcrec/scratch/bsu6fix3/inlane_<stage>.log; the last line is "INLANE <stage> DONE rc=N".
set -u
S=/var/tmp/pcrec-pcrec/scratch/bsu6fix3
W=/home/pcrec/projects/pcrec/worktrees/bsu6fix3
CARDS=$W/memfn/tests/span_forms/cards.py
export TMPDIR=$S/tmp PCREC_TMPDIR=$S PCREC_TREE=$W JOBS=${JOBS:-4}
mkdir -p "$TMPDIR"
st=${1:?stage}
log=$S/inlane_$st.log
run() { echo "+ $*"; "$@"; }
{
case "$st" in
    selftest)
        run nice gnutimeout 1800 python3 -I "$CARDS" c6selftest "$S/rd"; rc=$? ;;
    mutants)
        run nice gnutimeout 12000 python3 -I "$S/mutants/mutb.py" "$CARDS" | tee "$S/mutants/table.txt"; rc=${PIPESTATUS[0]}
        if grep -q ' -> SURVIVED$\| -> PATTERN MATCHES' "$S/mutants/table.txt"; then echo "MUTANTS: survivors or unapplied present (see table.txt)"; fi ;;
    dryfull)
        d=$S/rd_full; mkdir -p "$d"
        for x in art bin reach subj fx; do [ -e "$d/$x" ] || ln -s "$S/rd/$x" "$d/$x"; done
        rm -f "$d/c6_prepared.json"
        run nice gnutimeout 3000 python3 -I "$CARDS" time "$d" --prepare --cards C6,C6c; rc=$?
        if [ $rc -eq 0 ]; then
            echo "+ CARD_TIME=1 (preset) time $d --dry"
            CARD_TIME=1 nice gnutimeout 1800 python3 -I "$CARDS" time "$d" --dry > "$S/dryfull_time.out" 2>&1; rc=$?
            cat "$S/dryfull_time.out"
            rec=$(sed -n 's/.*-> \(\S*results_c6_\S*\.tsv\);.*/\1/p' "$S/dryfull_time.out" | head -1)
            echo "+ c6decide $rec"
            python3 -I "$CARDS" c6decide "$rec" > "$S/dryfull_decide.out" 2>&1; drc=$?
            echo "c6decide rc=$drc"
            sed -n '/the record read back/,/^cards: time: TRUNCATED$\|^cards: time: DONE/p' "$S/dryfull_time.out" | sed '1d;/^cards: time:/d' > "$S/dryfull_readback.out"
            if cmp -s "$S/dryfull_readback.out" "$S/dryfull_decide.out"; then echo "ROUND TRIP: identical ($(wc -l < "$S/dryfull_decide.out") lines)"; else echo "ROUND TRIP: DIFFERS"; rc=1; fi
        fi ;;
    g1)
        # Three cases (setup in $G, built by lane bsu6fix2): base (clean bench, the tree's own span_seed.rxt), wrap (the deny
        # compile of exactly [0-9a-f]{17} exits 3: RED BY DESIGN, and ONLY for its deny-fail count), crlf (a bench file
        # ending CRLF beside the three real sites: crlf=1 counted, green). The stage rc is the CASES' verdicts: any
        # unexpected red (or an expected red for another reason) fails it.
        G=$S/g1; rc=0
        for case in base:$W/build/pcrec:benchok wrap:$G/wrap.sh:benchok crlf:$W/build/pcrec:bench; do
            n=${case%%:*}; rest=${case#*:}; bin=${rest%%:*}; bench=${rest#*:}
            rm -rf "$G/out_$n"
            run nice gnutimeout 900 python3 -I "$W/tests/memfn/g1_span_vector.py" manifest --pcrec "$bin" --root "$G/root" --bench "$G/$bench" --out "$G/out_$n" --jobs 4 || { echo "g1 manifest $n FAILED"; rc=1; }
            python3 -I "$W/tests/memfn/g1_span_vector.py" dry --out "$G/out_$n" > "$G/dry_$n.out" 2>&1; drc=$?
            cat "$G/dry_$n.out"; echo "g1 dry $n rc=$drc"
            fails=$(grep -c '^G1 DRY FAIL: ' "$G/dry_$n.out")
            case "$n" in
                base) [ $drc -eq 0 ] && [ "$fails" -eq 0 ] && v=ok || v=UNEXPECTED ;;
                crlf) [ $drc -eq 0 ] && [ "$fails" -eq 0 ] && grep -q ' crlf=1;' "$G/dry_$n.out" && v=ok || v=UNEXPECTED ;;
                wrap) [ $drc -eq 1 ] && [ "$fails" -eq 1 ] && grep -qE '^G1 DRY FAIL: [1-9][0-9]* deny-fail cell\(s\)' "$G/dry_$n.out" && v="ok (red by design: deny-fail only)" || v=UNEXPECTED ;;
            esac
            echo "g1 case $n: $v"
            [ "${v%% *}" = ok ] || rc=1
        done ;;
    strict)
        run make -C "$W" strict; rc=$? ;;
    arch)
        run make -C "$W" test-memfn-arch; rc=$? ;;
    all)
        rc=0
        for x in selftest mutants dryfull g1 strict arch; do
            "$0" "$x"
            echo "== STAGE $x: $(tail -n 1 "$S/inlane_$x.log")"
            case "$x" in
                selftest) grep -E '^c6selftest: [0-9]+ rows' "$S/inlane_$x.log" | sed 's/^/== /';;
                mutants)  grep -E '^TOTALS:|SURVIVED$|PATTERN MATCHES' "$S/inlane_$x.log" | sed 's/^/== /';;
                dryfull)  grep -E 'clock calls|ROUND TRIP|^C6c? [a-z-]+: |DONE rc=|c6decide rc=|refused [0-9]+$|prepared ' "$S/inlane_$x.log" | sed 's/^/== /';;
                g1)       grep -E '^g1 case |^g1 dry [a-z]+ rc=|G1 DRY FAIL|^cells: |stripped of one' "$S/inlane_$x.log" | sed 's/^/== /';;
            esac
            tail -n 1 "$S/inlane_$x.log" | grep -q 'rc=0$' || rc=1
        done
        echo "INLANE ALL DONE rc=$rc"
        exit $rc ;;
    *) echo "unknown stage $st"; rc=2 ;;
esac
echo "INLANE $st DONE rc=$rc"
} > "$log" 2>&1
exit 0
