#!/usr/bin/env bash
# docs/design/kit_proof/measure/measure.sh — [KIT-VERIFY] `measure` (docs/design/kit_proof.md
# section 7, row "measure"): the harness-routed `cover` artifacts against the default ones.
#
#   measure.sh build  OUT          subjects + artifacts + binaries (cached: a key of every input)
#   measure.sh gate   OUT          THE ANSWER GATE, no clock: for every cell, class and regime the
#                                  three arms agree with each other AND with python `re`
#                                  (gen_subjects.py's .expect); any disagreement exits 3
#   measure.sh time   OUT L T N    L launches; per launch, per (cell, regime, class), the three
#                                  arms once each in a rotated order, pinned (taskset) to
#                                  MEASURE_CPU; each arm calibrates reps to T ns per sample and
#                                  takes N samples; the median ns per pass -> OUT/results.tsv
#   measure.sh calib  OUT          one launch at a small target; prints the wall (the cap's input)
#   measure.sh run    OUT [L T N]  build, gate, timing, table (the queued job's work)
#   measure.sh smoke  OUT          build, gate; NO clock (the lane's and --dry-run's check)
#
# ARMS (names are the arm column of results.tsv):
#   DEF  build/pcrec, default routing                      (the baseline)
#   COV  build/pcrec-harness --harness=kit-proof           (the `cover` LOCATE row routed)
#   AA   build/pcrec again, a SEPARATE compile and link    (the A/A noise floor: DEF against AA)
# Every arm compiles with --features all (the \b and lookahead cells need it) and links the
# same cdrv.c at gcc -O2. REGIMES are cdrv.c's header. TREE is this file's worktree.
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../.." && pwd)
PCREC=${PCREC:-$TREE/build/pcrec}
HARNESS=${HARNESS:-$TREE/build/pcrec-harness}
CPU=${MEASURE_CPU:-7}
SIB=${MEASURE_SIBLING:-15}
CC=${CC:-gcc}
ARMS="DEF COV AA"
REGIMES="throughput search_short match"
CLASSES="real none dense"
say() { printf '%s\n' "$*"; }
die() { say "measure: $*" >&2; exit 2; }
cmd_cells() { grep -v '^#' "$here/cells.tsv" | grep -v '^$'; }   # id TAB pattern

arm_compiler() { case $1 in COV) echo "$HARNESS --harness=kit-proof";; *) echo "$PCREC";; esac; }
stamp_of() { sed -n 's/^#define RX_DFA_SCAN "\([^"]*\)".*/\1/p' "$1"; }

key() {   # every input of the build, as one hash
    { sha256sum "$PCREC" "$HARNESS" "$here/cdrv.c" "$here/cells.tsv" "$here/gen_subjects.py"
      $CC --version | head -1; } | sha256sum | cut -d' ' -f1
}

build() {
    local OUT=$1 k
    [ -x "$PCREC" ] && [ -x "$HARNESS" ] || die "build/pcrec and build/pcrec-harness must exist (make)"
    mkdir -p "$OUT"
    k=$(key)
    if [ "$(cat "$OUT/build.key" 2>/dev/null)" = "$k" ] && [ -f "$OUT/build.done" ]; then
        say "build: cached ($k)"; return 0
    fi
    rm -rf "$OUT/subj" "$OUT/arts" "$OUT/build.done" "$OUT/cover_stamps.tsv"
    mkdir -p "$OUT/subj" "$OUT/arts" || return 1
    python3 -I "$here/gen_subjects.py" "$here/cells.tsv" "$OUT/subj" || return 1
    printf 'cell\tarm\tstamp\n' > "$OUT/cover_stamps.tsv"
    local cell pat arm d
    while IFS=$'\t' read -r cell pat; do
        for arm in $ARMS; do
            d=$OUT/arts/$cell/$arm
            mkdir -p "$d"
            # shellcheck disable=SC2046
            $(arm_compiler "$arm") --features all -p rx -o "$d/a.c" --pattern "$pat" > "$d/compile.log" 2>&1 ||
                { say "build: $arm compile of $cell failed"; cat "$d/compile.log"; return 1; }
            printf '%s\t%s\t%s\n' "$cell" "$arm" "$(stamp_of "$d/a.c")" >> "$OUT/cover_stamps.tsv"
            $CC -O2 -c -o "$d/a.o" "$d/a.c" || return 1
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -c -o "$d/d.o" "$here/cdrv.c" || return 1
            $CC -O2 -o "$d/bin" "$d/d.o" "$d/a.o" || return 1
        done
        cmp -s "$OUT/arts/$cell/DEF/a.c" "$OUT/arts/$cell/AA/a.c" ||
            { say "build: $cell DEF and AA sources differ (the compiler is not deterministic)"; return 1; }
    done < <(cmd_cells)
    # the premise: COV reads `cover`, DEF and AA do not
    local ncov=0 bad=0
    while IFS=$'\t' read -r cell arm st; do
        [ "$cell" = cell ] && continue
        case $arm in
            COV) [ "$st" = cover ] && ncov=$((ncov + 1)) ;;
            *)   [ "$st" = cover ] && { say "build: PREMISE FAILED: $cell $arm reads cover"; bad=1; } ;;
        esac
    done < "$OUT/cover_stamps.tsv"
    say "build: $ncov cell(s) read RX_DFA_SCAN \"cover\" on the harness build"
    [ "$bad" = 0 ] || return 1
    echo "$ncov" > "$OUT/ncover"
    echo "$k" > "$OUT/build.key"; : > "$OUT/build.done"
}

gate() {
    local OUT=$1 cell pat arm cls reg n=0 bad=0 f exp got
    [ -f "$OUT/build.done" ] || die "gate: build first"
    : > "$OUT/gate.tsv"
    while IFS=$'\t' read -r cell pat; do
        for cls in $CLASSES; do
            for reg in $REGIMES; do
                case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                exp=$(cat "$OUT/subj/$cell.$cls.$reg.expect")
                for arm in $ARMS; do
                    got=$("$OUT/arts/$cell/$arm/bin" check "$reg" "$OUT/subj/$cell.$cls.$f")
                    n=$((n + 1))
                    if [ "$got" != "$exp" ]; then
                        bad=$((bad + 1))
                        say "ANSWER MISMATCH: $cell/$cls/$reg arm $arm: got [$got] python [$exp]"
                    fi
                done
                printf '%s\t%s\t%s\t%s\n' "$cell" "$cls" "$reg" "$exp" >> "$OUT/gate.tsv"
            done
        done
    done < <(cmd_cells)
    if [ "$bad" != 0 ]; then say "== covertime GATE FAILED: $bad of $n arm cells disagree"; return 3; fi
    say "== covertime gate passed: $n arm cells (3 arms x $((n / 3)) subjects), all equal to python re"
}

cpu_busy() {   # CPU_ID SECONDS -> percent busy over the window (idle + iowait count as idle)
    local c=$1 s=$2 a b
    a=$(command grep -m1 "^cpu$c " /proc/stat); sleep "$s"; b=$(command grep -m1 "^cpu$c " /proc/stat)
    echo "$a $b" | awk '{ t0 = 0; t1 = 0; for (i = 2; i <= 9; i++) { t0 += $i; t1 += $(i + 11) }
        d = t1 - t0; busy = (d > 0) ? 100 * (1 - (($16 + $17) - ($5 + $6)) / d) : 0; printf "%.1f", busy }'
}

timeloop() {
    local OUT=$1 L=$2 T=$3 N=$4 l cell pat cls reg f arm order i k=0 out rot nitems=0
    [ -f "$OUT/gate.tsv" ] || die "time: run the gate first"
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/results.tsv"
    for l in $(seq 1 "$L"); do
        say "launch $l/$L start $(date +%T) load1=$(cut -d' ' -f1 /proc/loadavg) cpu$CPU=$(cpu_busy "$CPU" 1)% sibling cpu$SIB=$(cpu_busy "$SIB" 1)%"
        while IFS=$'\t' read -r cell pat; do
            for reg in $REGIMES; do
                case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                for cls in $CLASSES; do
                    rot=$(( (k + l) % 3 )); k=$((k + 1))
                    set -- $ARMS
                    case $rot in 0) order="$1 $2 $3";; 1) order="$2 $3 $1";; 2) order="$3 $1 $2";; esac
                    for arm in $order; do
                        out=$(taskset -c "$CPU" "$OUT/arts/$cell/$arm/bin" time "$reg" "$OUT/subj/$cell.$cls.$f" "$T" "$N") ||
                            { say "time: $cell/$cls/$reg/$arm failed"; return 1; }
                        # out: ns M min m reps R ops O bytes B
                        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$cell" "$reg" "$cls" "$arm" \
                            "$(echo "$out" | awk '{print $2"\t"$4"\t"$6"\t"$8"\t"$10}')" >> "$OUT/results.tsv"
                        nitems=$((nitems + 1))
                    done
                done
            done
        done < <(cmd_cells)
    done
    say "time: $nitems timed arm cells over $L launches"
}

table() {
    local OUT=$1
    python3 -I "$here/read.py" "$OUT" > "$OUT/table.md" || return 1
    cat "$OUT/table.md"
}

cmd=${1:-}; OUT=${2:-}
[ -n "$OUT" ] || { sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 64; }
case $cmd in
    build) build "$OUT" ;;
    gate)  gate "$OUT" ;;
    smoke) build "$OUT" && gate "$OUT" ;;
    time)  timeloop "$OUT" "${3:?L}" "${4:?T}" "${5:?N}" ;;
    calib)
        build "$OUT" && gate "$OUT" || exit $?
        t0=$(date +%s.%N)
        timeloop "$OUT" 1 2000000 3 || exit $?
        t1=$(date +%s.%N)
        awk -v a="$t0" -v b="$t1" 'BEGIN { printf "calib: one launch at T=2ms N=3 took %.1f s\n", b - a }' ;;
    run)
        L=${3:-5}; T=${4:-20000000}; N=${5:-9}
        say "== covertime START $(date -Is) L=$L T=$T N=$N cpu=$CPU sibling=$SIB"
        build "$OUT" || exit 1
        gate "$OUT" || exit $?
        timeloop "$OUT" "$L" "$T" "$N" || exit 1
        say "end sibling cpu$SIB=$(cpu_busy "$SIB" 2)% cpu$CPU=$(cpu_busy "$CPU" 2)%"
        table "$OUT" || exit 1
        rows=$(( $(wc -l < "$OUT/results.tsv") - 1 ))
        say "== covertime COMPLETE rows=$rows launches=$L"
        ;;
    *) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 64 ;;
esac
