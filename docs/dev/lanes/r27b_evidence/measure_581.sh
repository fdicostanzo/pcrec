#!/usr/bin/env bash
# docs/dev/lanes/r27b_evidence/measure_581.sh — job 581 (lane r27b, MEASUREMENT ONLY): the 650
# harness (docs/design/kit_proof/measure/, unchanged and reused) extended over the arms of
# proto_bodies_581.py, behind a no-clock DIFFERENTIAL stage that runs FIRST.
#
#   measure_581.sh smoke OUT        build (base + protos + diff binaries), the differential, the
#                                   answer gates: NO clock. SMOKE_CELLS="c1 c2" restricts every
#                                   per-cell stage (the queue's --dry-run uses two cells).
#   measure_581.sh run OUT [L T N]  smoke over ALL cells, then L launches over the arms (rotated
#                                   order, pinned), the population counts, then the tables
#
# STAGES of `run`, in order (each prints a "== r27b STAGE" line; a red stage aborts, rc 3):
#   1 build   measure.sh build (DEF COV AA, subjects), proto text rendered and compiled
#   2 diff    THE DIFFERENTIAL: per cell about 2000 random small subjects (length 0..40), every arm's
#             rx_search for every lo against python `re` (python3 -I), sentinel-padded buffers
#             (every phase) AND, when libasan is present, an exact-size malloc block under ASan+UBSan
#   3 gate    the 650 answer gate (DEF COV AA) and the same for every proto arm, on the full subjects
#   4 time    L launches; per launch a cpu_busy reading of the pinned CPU and its SMT sibling
#   5 table   pop_581.py (population counts, predictor), read_581.py (tables), final load1 line
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../.." && pwd)
M=$TREE/docs/design/kit_proof/measure
export PCREC=${PCREC:-$TREE/build/r27b/bin/pcrec}
export HARNESS=${HARNESS:-$TREE/build/r27b/bin/pcrec-harness}
CPU=${MEASURE_CPU:-7}
SIB=${MEASURE_SIBLING:-15}
CC=${CC:-gcc}
REGIMES="throughput search_short match"
CLASSES="real none dense"
say() { printf '%s\n' "$*"; }
allcells() { grep -v '^#' "$M/cells.tsv" | grep -v '^$' | cut -f1; }
cells() { if [ -n "${SMOKE_CELLS:-}" ] && [ "${ALLCELLS:-0}" != 1 ]; then echo $SMOKE_CELLS | tr ' ' '\n'; else allcells; fi; }
arms_of() { python3 -I "$here/proto_bodies_581.py" --arms "$1"; }
dir_of() { case $2 in DEF|COV|AA) echo "$OUT/arts/$1/$2";; *) echo "$OUT/proto/$1/$2";; esac; }
bin_of() { echo "$(dir_of "$1" "$2")/bin"; }

cpu_busy() {   # CPU_ID SECONDS -> percent busy over the window (idle + iowait count as idle)
    local c=$1 s=$2 a b
    a=$(command grep -m1 "^cpu$c " /proc/stat); sleep "$s"; b=$(command grep -m1 "^cpu$c " /proc/stat)
    echo "$a $b" | awk '{ t0 = 0; t1 = 0; for (i = 2; i <= 9; i++) { t0 += $i; t1 += $(i + 11) }
        d = t1 - t0; busy = (d > 0) ? 100 * (1 - (($16 + $17) - ($5 + $6)) / d) : 0; printf "%.1f", busy }'
}

stage_build() {
    say "== r27b STAGE build"
    # base: measure.sh build compiles ALL cells (cached by a key of its inputs); the gate is stage 3
    bash "$M/measure.sh" build "$OUT" || return $?
    rm -rf "$OUT/proto"
    python3 -I "$here/proto_bodies_581.py" "$OUT" "$OUT/proto" || return 1
    local cell arm d
    for cell in $(cells); do
        for arm in $(arms_of "$cell"); do
            case $arm in DEF|COV|AA) continue;; esac
            d=$OUT/proto/$cell/$arm
            $CC -O2 -c -o "$d/a.o" "$d/a.c" || return 1
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -c -o "$d/d.o" "$M/cdrv.c" || return 1
            $CC -O2 -o "$d/bin" "$d/d.o" "$d/a.o" || return 1
        done
        cmp -s "$OUT/proto/$cell/PRO/a.c" "$OUT/proto/$cell/PRO2/a.c" || { say "PRO and PRO2 sources differ: $cell"; return 1; }
    done
    say "build: proto arms rendered and compiled for: $(cells | tr '\n' ' ')"
}

stage_diff() {
    say "== r27b STAGE diff"
    local cell arm d dd bad=0 n=0 asan=1 tile
    rm -rf "$OUT/diff" "$OUT/diffbin"
    # the generator takes ALL cells of cells.tsv unless named
    python3 -I "$here/diff_581.py" "$M/cells.tsv" "$OUT/diff" $(cells) || return 1
    echo 'int main(void){return 0;}' > "$OUT/asan_probe.c"
    $CC -fsanitize=address,undefined -o "$OUT/asan_probe" "$OUT/asan_probe.c" 2> /dev/null && "$OUT/asan_probe" || asan=0
    [ "$asan" = 1 ] || say "diff: libasan NOT available: the exact-size ASan arm is SKIPPED (sentinel arm only)"
    for cell in $(cells); do
        tile=$(cat "$OUT/diff/$cell.tile")
        for arm in $(arms_of "$cell"); do
            d=$(dir_of "$cell" "$arm")
            dd=$OUT/diffbin/$cell/$arm
            mkdir -p "$dd"
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -o "$dd/plain" "$here/ddrv.c" "$d/a.c" || return 1
            n=$((n + 1))
            if ! "$dd/plain" "$OUT/diff/$cell.cases" "$tile" > "$dd/plain.out" 2> "$dd/plain.err"; then
                bad=$((bad + 1)); say "DIFF RED: $cell arm $arm (sentinel buffers): $(cat "$dd/plain.out")"; head -5 "$dd/plain.err"
            fi
            if [ "$asan" = 1 ]; then
                $CC -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -DEXACT -DHDR="\"a.h\"" -I"$d" \
                    -o "$dd/asan" "$here/ddrv.c" "$d/a.c" || return 1
                n=$((n + 1))
                if ! "$dd/asan" "$OUT/diff/$cell.cases" "$tile" > "$dd/asan.out" 2> "$dd/asan.err"; then
                    bad=$((bad + 1)); say "DIFF RED: $cell arm $arm (exact-size, ASan/UBSan): $(cat "$dd/asan.out")"; head -8 "$dd/asan.err"
                fi
            fi
        done
        say "diff: $cell: $(for arm in $(arms_of "$cell"); do printf '%s ' "$arm"; done)| $(cat "$OUT/diffbin/$cell/PRO/plain.out")"
    done
    [ "$bad" = 0 ] || { say "== r27b DIFFERENTIAL RED: $bad of $n arm builds disagree with python re"; return 3; }
    say "== r27b differential GREEN: $n arm builds equal to python re ($(cells | wc -l) cells, asan=$asan)"
}

stage_gate() {
    say "== r27b STAGE gate"
    bash "$M/measure.sh" gate "$OUT" || return $?
    local cell arm cls reg f bad=0 n=0
    for cell in $(cells); do
        for arm in $(arms_of "$cell"); do
            case $arm in DEF|COV|AA) continue;; esac
            for cls in $CLASSES; do
                for reg in $REGIMES; do
                    case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                    n=$((n + 1))
                    [ "$("$(bin_of "$cell" "$arm")" check "$reg" "$OUT/subj/$cell.$cls.$f")" = "$(cat "$OUT/subj/$cell.$cls.$reg.expect")" ] ||
                        { say "ANSWER MISMATCH: $cell/$cls/$reg arm $arm"; bad=$((bad + 1)); }
                done
            done
        done
    done
    [ "$bad" = 0 ] || { say "== r27b GATE FAILED: $bad of $n"; return 3; }
    say "== r27b gate passed: $n proto arm cells equal to python re"
}

timeloop() {
    local L=$1 T=$2 N=$3 l cell reg cls f arm order k=0 rot out nitems=0 arms m
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/r27b_results.tsv"
    : > "$OUT/cpu_busy.tsv"
    for l in $(seq 1 "$L"); do
        say "launch $l/$L start $(date +%T) load1=$(cut -d' ' -f1 /proc/loadavg) cpu$CPU=$(cpu_busy "$CPU" 1)% sibling cpu$SIB=$(cpu_busy "$SIB" 1)%"
        for cell in $(cells); do
            arms=$(arms_of "$cell"); m=$(echo $arms | wc -w)
            for reg in $REGIMES; do
                case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                for cls in $CLASSES; do
                    rot=$(( (k + l) % m )); k=$((k + 1))
                    set -- $arms $arms
                    shift "$rot"
                    order=""; for _ in $(seq 1 "$m"); do order="$order $1"; shift; done
                    for arm in $order; do
                        out=$(taskset -c "$CPU" "$(bin_of "$cell" "$arm")" time "$reg" "$OUT/subj/$cell.$cls.$f" "$T" "$N") ||
                            { say "time: $cell/$cls/$reg/$arm failed"; return 1; }
                        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$cell" "$reg" "$cls" "$arm" \
                            "$(echo "$out" | awk '{print $2"\t"$4"\t"$6"\t"$8"\t"$10}')" >> "$OUT/r27b_results.tsv"
                        nitems=$((nitems + 1))
                    done
                done
            done
        done
    done
    say "time: $nitems timed arm cells over $L launches"
}

cmd=${1:-}; OUT=${2:-}
[ -n "$OUT" ] || { sed -n '2,19p' "$0"; exit 64; }
mkdir -p "$OUT" "${TMPDIR:-$OUT}" || exit 1
case $cmd in
    smoke) stage_build && stage_diff && stage_gate ;;
    run)
        L=${3:-5}; T=${4:-20000000}; N=${5:-9}
        ALLCELLS=1
        say "== r27b START $(date -Is) L=$L T=$T N=$N cpu=$CPU sibling=$SIB"
        stage_build || exit $?
        stage_diff || exit $?
        stage_gate || exit $?
        say "== r27b STAGE time"
        timeloop "$L" "$T" "$N" || exit 1
        say "end sibling cpu$SIB=$(cpu_busy "$SIB" 2)% cpu$CPU=$(cpu_busy "$CPU" 2)%"
        say "final load1=$(cut -d' ' -f1 /proc/loadavg)"
        say "== r27b STAGE table"
        python3 -I "$here/pop_581.py" "$OUT/subj" "$TREE/tests/findings/default_ppm.tsv" > "$OUT/pop.tsv" || exit 1
        {
            echo "# job 581 (lane r27b): window-search arms, SCALAR layer only"
            echo
            echo "- layer: SCALAR (portable C, \`-fno-memfn-simd\`, the kit's default OFF); SIMD is NOT read here and its verdict is pcrec-bench's (D144 addendum 4)"
            echo "- memfn profile: none named by the kit (D147: there is no portable/native/baseline profile); arms are hand-rendered REPORT text over the harness build (\`pcrec-harness --harness=kit-proof\`), gcc -O2, no -march, one pinned core (cpu $CPU, sibling $SIB), $($CC --version | head -1)"
            echo "- compilers: pcrec $(sha256sum "$PCREC" | cut -c1-12), pcrec-harness $(sha256sum "$HARNESS" | cut -c1-12) (the 580 build)"
            echo "- L=$L launches, T=$T ns per sample, N=$N samples"
        } > "$OUT/header.md"
        python3 -I "$here/read_581.py" "$OUT" "$OUT/header.md" > "$OUT/r27b_table.md" || exit 1
        cat "$OUT/r27b_table.md"
        rows=$(( $(wc -l < "$OUT/r27b_results.tsv") - 1 ))
        say "== r27b COMPLETE rows=$rows launches=$L"
        ;;
    *) exit 64 ;;
esac
