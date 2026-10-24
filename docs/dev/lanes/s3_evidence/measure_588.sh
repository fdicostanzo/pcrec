#!/usr/bin/env bash
# docs/dev/lanes/s3_evidence/measure_588.sh — job 588 (lane s3, D172 S3's acceptance,
# docs/design/memfn/window_site.md rev 3.2 §6): the 650 harness's 8 cells x 3 regimes x 3 classes
# (docs/design/kit_proof/measure/: cells.tsv, gen_subjects.py, cdrv.c; job 581's calibration),
# timing the S3 compiler's DEFAULT (routed) artifacts against its own OFF arm, at the SCALAR layer
# (the bar) and with -fmemfn-simd (reported), BEHIND a no-clock differential stage.
#
#   measure_588.sh smoke OUT        build + differential + answer gate: NO clock. SMOKE_CELLS="c1 c2"
#                                   restricts every per-cell stage (the queue's --dry-run), and
#                                   SMOKE_SAMPLE="smp01" the mover sample's and SMOKE_ESH="esh02"
#                                   the D-hors admission sites' (below)
#   measure_588.sh run OUT [L T N]  smoke over ALL cells, then L launches (rotated order, pinned),
#                                   then read_588.py's table
#
# THE ARMS (one compiler, $PCREC, the S3 build; every arm `--features all -p rx`):
#   DEF   --memfn=no-window-search,no-window-skip   the OFF arm: byte-identical to main c3ea619c3 but for the
#                                         abi digits (bytediff.sh) -- §6's DEF, and G1's deny arm
#   RTE   (default)                       the routed form (E-find; D-hors where it fires)
#   RT2   (default, a second compile + link)   the A/A pair of RTE (the floor's AA)
#   NOH   --memfn=no-window-skip              G1's deny arm of D-hors; built everywhere, TIMED only where
#                                         its text differs from RTE's (hex8-bounded, §6)
#   DEFs RTEs NOHs   the same with -fmemfn-simd (the SIMD-on layer, REPORTED, never the bar)
#
# STAGES of `run` (each prints "== s3t STAGE"; a red stage aborts, rc 3):
#   1 build   subjects (gen_subjects.py), every arm compiled; PREMISES: RTE reads RX_DFA_SCAN
#             "cover" on every cell, DEF on none, RT2 == RTE text, NOH != RTE exactly where D-hors fires
#   2 diff    job 581's differential (diff_581.py + ddrv.c, r27b_evidence/): ~2000 random small
#             subjects per cell, every arm's rx_search at every lo against python `re`, sentinel
#             buffers and (libasan present) exact-size ASan+UBSan blocks
#   3 gate    every arm on the full subjects equal to python `re` (gen_subjects' .expect)
#   4 time    L launches; cpu_busy of the pinned CPU and its sibling per launch
#   5 table   read_588.py
#
# THE MOVER SAMPLE (the S3 review's item E; PART OF THE BAR since the S3 code review r1, C10:
# read_588.py's strata rule, a dropped row a FAIL):
# sample_588.tsv (pick_588.py's committed pick: ~24 other cover movers, stratified by B form x D x
# C-run). Subjects by gen_sample_588.py (classes real / none / random where generatable), regimes
# throughput and search_short, arms DEF RTE at the scalar layer and DEFs RTEs at the SIMD layer;
# an arm whose TEXT equals its other-layer twin's (a cover artifact carries no SIMD form) is
# built and timed once and read for both. Its stages (sample-build, sample-gate) run after the
# gate and its items after each launch's cells, in the same launches, same calibration and core;
# a sample row that fails a premise, a compile or the answer gate is DROPPED with a loud
# `SAMPLE ... ` line and never stops the job (read_588.py then FAILS the bar for it). Results:
# s3t_sample.tsv; read_588.py prints them under "Mover sample (part of the bar)".
#
# THE D-HORS ADMISSION SITES (Frank's ruling 2026-10-23 on the S3 review's fix C: measure, do not
# decline; FINDINGS, NEVER part of the bar, no default changes): esh_588.tsv (pick_esh_588.py's
# committed pick: ~12 D-hors sites stratified by E[sh], the expected shift per probe under the
# default byte-rate prior, esh_588.py). The same machinery as the mover sample (use_set), with arms
# NOH (--memfn=no-window-skip: D-one) and RTE (default: D-hors) at the scalar layer and NOHs/RTEs at the
# SIMD layer; premise: both read cover, RTE carries `_sh[256]` and NOH does not. Stages esh-build,
# esh-gate; items after the sample's in each launch; results s3t_esh.tsv; read_588.py prints them
# under "D-hors admission (E[sh])".
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../.." && pwd)
M=$TREE/docs/design/kit_proof/measure
R=$TREE/docs/dev/lanes/r27b_evidence
export PCREC=${PCREC:-$TREE/build/s3/bin/pcrec}
CPU=${MEASURE_CPU:-7}
SIB=${MEASURE_SIBLING:-15}
CC=${CC:-gcc}
REGIMES="throughput search_short match"
CLASSES="real none dense"
ALLARMS="DEF RTE RT2 NOH DEFs RTEs NOHs"
SAMPLE=$here/sample_588.tsv
ESH=$here/esh_588.tsv
SREGIMES="throughput search_short"
SCLASSES="real none random"
say() { printf '%s\n' "$*"; }
allcells() { grep -v '^#' "$M/cells.tsv" | grep -v '^$' | cut -f1; }
cells() { if [ -n "${SMOKE_CELLS:-}" ] && [ "${ALLCELLS:-0}" != 1 ]; then echo $SMOKE_CELLS | tr ' ' '\n'; else allcells; fi; }
pat_of() { grep -v '^#' "$M/cells.tsv" | awk -F'\t' -v c="$1" '$1 == c { print $2 }'; }
flags_of() {
    case $1 in
        DEF)  echo "--memfn=no-window-search,no-window-skip" ;;
        RTE|RT2) echo "" ;;
        NOH)  echo "--memfn=no-window-skip" ;;
        DEFs) echo "-fmemfn-simd --memfn=no-window-search,no-window-skip" ;;
        RTEs) echo "-fmemfn-simd" ;;
        NOHs) echo "-fmemfn-simd --memfn=no-window-skip" ;;
    esac
}
# the arms TIMED for a cell: every arm but a NOH/NOHs whose text is its routed twin's
arms_of() { cat "$OUT/arts/$1/arms"; }
bin_of() { echo "$OUT/arts/$1/$2/bin"; }
stamp_of() { sed -n 's/^#define RX_DFA_SCAN "\([^"]*\)".*/\1/p' "$1"; }

cpu_busy() {   # CPU_ID SECONDS -> percent busy over the window (idle + iowait count as idle)
    local c=$1 s=$2 a b
    a=$(command grep -m1 "^cpu$c " /proc/stat); sleep "$s"; b=$(command grep -m1 "^cpu$c " /proc/stat)
    echo "$a $b" | awk '{ t0 = 0; t1 = 0; for (i = 2; i <= 9; i++) { t0 += $i; t1 += $(i + 11) }
        d = t1 - t0; busy = (d > 0) ? 100 * (1 - (($16 + $17) - ($5 + $6)) / d) : 0; printf "%.1f", busy }'
}

stage_build() {
    say "== s3t STAGE build"
    [ -x "$PCREC" ] || { say "build: no compiler $PCREC"; return 1; }
    rm -rf "$OUT/subj" "$OUT/arts"
    mkdir -p "$OUT/subj" "$OUT/arts" || return 1
    python3 -I "$M/gen_subjects.py" "$M/cells.tsv" "$OUT/subj" || return 1
    local cell arm d pat bad=0 nhors=0
    for cell in $(cells); do
        pat=$(pat_of "$cell")
        for arm in $ALLARMS; do
            d=$OUT/arts/$cell/$arm
            mkdir -p "$d"
            # shellcheck disable=SC2046
            "$PCREC" --features all -p rx $(flags_of "$arm") -o "$d/a.c" --pattern "$pat" > "$d/compile.log" 2>&1 ||
                { say "build: $arm compile of $cell failed"; cat "$d/compile.log"; return 1; }
            $CC -O2 -c -o "$d/a.o" "$d/a.c" || return 1
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -c -o "$d/d.o" "$M/cdrv.c" || return 1
            $CC -O2 -o "$d/bin" "$d/d.o" "$d/a.o" || return 1
        done
        # PREMISES (rc 3 on any): the routed arms read cover, the OFF arms do not; RT2 is RTE's text
        for arm in RTE RT2 NOH RTEs NOHs; do
            [ "$(stamp_of "$OUT/arts/$cell/$arm/a.c")" = cover ] || { say "build: PREMISE FAILED: $cell $arm does not read cover"; bad=1; }
        done
        for arm in DEF DEFs; do
            [ "$(stamp_of "$OUT/arts/$cell/$arm/a.c")" = cover ] && { say "build: PREMISE FAILED: $cell $arm reads cover"; bad=1; }
        done
        cmp -s "$OUT/arts/$cell/RTE/a.c" "$OUT/arts/$cell/RT2/a.c" || { say "build: PREMISE FAILED: $cell RTE and RT2 texts differ"; bad=1; }
        local arms="DEF RTE RT2"
        cmp -s "$OUT/arts/$cell/NOH/a.c" "$OUT/arts/$cell/RTE/a.c" || { arms="$arms NOH"; nhors=$((nhors + 1)); }
        arms="$arms DEFs RTEs"
        cmp -s "$OUT/arts/$cell/NOHs/a.c" "$OUT/arts/$cell/RTEs/a.c" || arms="$arms NOHs"
        echo "$arms" > "$OUT/arts/$cell/arms"
        say "build: $cell: timed arms $arms"
    done
    [ "$bad" = 0 ] || return 3
    say "build: $nhors cell(s) where D-hors fires (NOH's text differs from RTE's)"
}

# TWO SIDE SETS ride the cells' launches, both FINDINGS (never the bar), one machinery: `use_set`
# selects one. sample: the mover sample (DEF vs routed). esh: the D-hors admission sites (D-one, the
# `no-window-skip` deny NOH, vs D-hors, routed RTE).
use_set() {
    SET=$1
    case $1 in
        sample) SET_FILE=$SAMPLE SET_SMOKE=${SMOKE_SAMPLE:-} SET_TAG=SAMPLE SET_SUBJ=ssubj SET_ARTS=sarts
                SET_ARMS="DEF RTE DEFs RTEs" ;;
        esh)    SET_FILE=$ESH SET_SMOKE=${SMOKE_ESH:-} SET_TAG=ESH SET_SUBJ=esubj SET_ARTS=earts
                SET_ARMS="NOH RTE NOHs RTEs" ;;
    esac
}
# the set's ids (SET_SMOKE restricts them outside `run`) and their patterns
sids() {
    if [ -n "$SET_SMOKE" ] && [ "${ALLCELLS:-0}" != 1 ]; then echo $SET_SMOKE | tr ' ' '\n'
    else grep -v '^#' "$SET_FILE" | cut -f1; fi
}
spat_of() { python3 -I -c 'import sys; sys.path.insert(0, sys.argv[2]); import emit_sweep
for l in open(sys.argv[1]):
    f = l.rstrip("\n").split("\t")
    if f[0] == sys.argv[3]: sys.stdout.buffer.write(bytes(emit_sweep.decode_escape(f[2])))' "$SET_FILE" "$TREE/scripts" "$1"; }
# the surviving rows (a dropped row has no arms file)
live_sids() { for s in $(sids); do [ -s "$OUT/$SET_ARTS/$s/arms" ] && echo "$s"; done; }
# a row's PREMISE: sample, RTE reads cover and DEF does not; esh, both read cover, RTE carries
# D-hors's `_sh[256]` table and NOH (D-one) does not
set_premise() {
    local a=$OUT/$SET_ARTS/$1
    case $SET in
        sample) [ "$(stamp_of "$a/RTE/a.c")" = cover ] && [ "$(stamp_of "$a/DEF/a.c")" != cover ] ;;
        esh)    [ "$(stamp_of "$a/RTE/a.c")" = cover ] && [ "$(stamp_of "$a/NOH/a.c")" = cover ] &&
                    command grep -q '_sh\[256\]' "$a/RTE/a.c" && ! command grep -q '_sh\[256\]' "$a/NOH/a.c" ;;
    esac
}

stage_set_build() {
    say "== s3t STAGE $SET-build"
    rm -rf "$OUT/$SET_SUBJ" "$OUT/$SET_ARTS"
    mkdir -p "$OUT/$SET_SUBJ" "$OUT/$SET_ARTS" || return 1
    [ -f "$SET_FILE" ] || { say "$SET_TAG MISSING: $SET_FILE"; return 0; }
    if [ -n "$SET_SMOKE" ] && [ "${ALLCELLS:-0}" != 1 ]; then
        { grep '^#' "$SET_FILE"; for s in $SET_SMOKE; do grep "^$s	" "$SET_FILE"; done; } > "$OUT/$SET.tsv"
    else cp "$SET_FILE" "$OUT/$SET.tsv"; fi
    python3 -I "$here/gen_sample_588.py" "$OUT/$SET.tsv" "$OUT/$SET_SUBJ" || { say "$SET_TAG SUBJECTS FAILED"; return 0; }
    local sid arm d pat twin arms nok=0
    for sid in $(sids); do
        pat=$(spat_of "$sid")
        arms=""
        for arm in $SET_ARMS; do
            d=$OUT/$SET_ARTS/$sid/$arm
            mkdir -p "$d"
            # shellcheck disable=SC2046
            "$PCREC" --features all -p rx $(flags_of "$arm") -o "$d/a.c" --pattern "$pat" > "$d/compile.log" 2>&1 ||
                { say "$SET_TAG COMPILE FAILED: $sid $arm (dropped)"; arms=""; break; }
            twin=${arm%s}
            if [ "$twin" != "$arm" ] && cmp -s "$d/a.c" "$OUT/$SET_ARTS/$sid/$twin/a.c"; then continue; fi
            { $CC -O2 -c -o "$d/a.o" "$d/a.c" && $CC -O2 -DHDR="\"a.h\"" -I"$d" -c -o "$d/d.o" "$M/cdrv.c" &&
                $CC -O2 -o "$d/bin" "$d/d.o" "$d/a.o"; } || { say "$SET_TAG BUILD FAILED: $sid $arm (dropped)"; arms=""; break; }
            arms="$arms $arm"
        done
        [ -n "$arms" ] || continue
        set_premise "$sid" || { say "$SET_TAG PREMISE FAILED: $sid (dropped)"; continue; }
        echo $arms > "$OUT/$SET_ARTS/$sid/arms"
        nok=$((nok + 1))
        say "$SET-build: $sid: timed arms$arms"
    done
    say "$SET-build: $nok of $(sids | wc -l) $SET rows built"
}

stage_set_gate() {
    say "== s3t STAGE $SET-gate"
    local sid arm cls reg f n=0 bad
    for sid in $(live_sids); do
        bad=0
        for arm in $(cat "$OUT/$SET_ARTS/$sid/arms"); do
            for cls in $SCLASSES; do
                [ -f "$OUT/$SET_SUBJ/$sid.$cls.raw" ] || continue
                for reg in $SREGIMES; do
                    case $reg in throughput) f=raw;; search_short) f=srec;; esac
                    n=$((n + 1))
                    [ "$("$OUT/$SET_ARTS/$sid/$arm/bin" check "$reg" "$OUT/$SET_SUBJ/$sid.$cls.$f")" = "$(cat "$OUT/$SET_SUBJ/$sid.$cls.$reg.expect")" ] ||
                        { say "$SET_TAG ANSWER MISMATCH: $sid/$cls/$reg arm $arm (the row is dropped; a FINDING)"; bad=1; }
                done
            done
        done
        [ "$bad" = 0 ] || rm -f "$OUT/$SET_ARTS/$sid/arms"
    done
    say "$SET-gate: $n arm cells read; $(live_sids | wc -l) $SET rows live"
}

stage_diff() {
    say "== s3t STAGE diff"
    local cell arm d dd bad=0 n=0 asan=1 tile
    rm -rf "$OUT/diff" "$OUT/diffbin"
    python3 -I "$R/diff_581.py" "$M/cells.tsv" "$OUT/diff" $(cells) || return 1
    echo 'int main(void){return 0;}' > "$OUT/asan_probe.c"
    $CC -fsanitize=address,undefined -o "$OUT/asan_probe" "$OUT/asan_probe.c" 2> /dev/null && "$OUT/asan_probe" || asan=0
    [ "$asan" = 1 ] || say "diff: libasan NOT available: the exact-size ASan arm is SKIPPED (sentinel arm only)"
    for cell in $(cells); do
        tile=$(cat "$OUT/diff/$cell.tile")
        for arm in $ALLARMS; do
            d=$OUT/arts/$cell/$arm
            dd=$OUT/diffbin/$cell/$arm
            mkdir -p "$dd"
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -o "$dd/plain" "$R/ddrv.c" "$d/a.c" || return 1
            n=$((n + 1))
            if ! "$dd/plain" "$OUT/diff/$cell.cases" "$tile" > "$dd/plain.out" 2> "$dd/plain.err"; then
                bad=$((bad + 1)); say "DIFF RED: $cell arm $arm (sentinel buffers): $(cat "$dd/plain.out")"; head -5 "$dd/plain.err"
            fi
            if [ "$asan" = 1 ]; then
                $CC -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -DEXACT -DHDR="\"a.h\"" -I"$d" \
                    -o "$dd/asan" "$R/ddrv.c" "$d/a.c" || return 1
                n=$((n + 1))
                if ! "$dd/asan" "$OUT/diff/$cell.cases" "$tile" > "$dd/asan.out" 2> "$dd/asan.err"; then
                    bad=$((bad + 1)); say "DIFF RED: $cell arm $arm (exact-size, ASan/UBSan): $(cat "$dd/asan.out")"; head -8 "$dd/asan.err"
                fi
            fi
        done
        say "diff: $cell: $ALLARMS | $(cat "$OUT/diffbin/$cell/RTE/plain.out")"
    done
    [ "$bad" = 0 ] || { say "== s3t DIFFERENTIAL RED: $bad of $n arm builds disagree with python re"; return 3; }
    say "== s3t differential GREEN: $n arm builds equal to python re ($(cells | wc -l) cells, asan=$asan)"
}

stage_gate() {
    say "== s3t STAGE gate"
    local cell arm cls reg f bad=0 n=0
    for cell in $(cells); do
        for arm in $ALLARMS; do
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
    [ "$bad" = 0 ] || { say "== s3t GATE FAILED: $bad of $n"; return 3; }
    say "== s3t gate passed: $n arm cells equal to python re"
}

timeloop() {
    local L=$1 T=$2 N=$3 l cell reg cls f arm order k=0 rot out nitems=0 arms m
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/s3t_results.tsv"
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/s3t_sample.tsv"
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/s3t_esh.tsv"
    SK=0
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
                            "$(echo "$out" | awk '{print $2"\t"$4"\t"$6"\t"$8"\t"$10}')" >> "$OUT/s3t_results.tsv"
                        nitems=$((nitems + 1))
                    done
                done
            done
        done
        use_set sample; timeloop_set "$l" "$T" "$N" "$OUT/s3t_sample.tsv"
        use_set esh; timeloop_set "$l" "$T" "$N" "$OUT/s3t_esh.tsv"
    done
    say "time: $(( $(wc -l < "$OUT/s3t_sample.tsv") - 1 )) sample items over $L launches"
    say "time: $(( $(wc -l < "$OUT/s3t_esh.tsv") - 1 )) esh items over $L launches"
    say "time: $nitems timed arm cells over $L launches"
}

# the selected set's items, one launch: rotated as the cells' are; into TSV
timeloop_set() {
    local l=$1 T=$2 N=$3 tsv=$4 sid reg cls f arm order m arms rot out
    for sid in $(live_sids); do
        arms=$(cat "$OUT/$SET_ARTS/$sid/arms"); m=$(echo $arms | wc -w)
        for reg in $SREGIMES; do
            case $reg in throughput) f=raw;; search_short) f=srec;; esac
            for cls in $SCLASSES; do
                [ -f "$OUT/$SET_SUBJ/$sid.$cls.$f" ] || continue
                rot=$(( (SK + l) % m )); SK=$((SK + 1))
                set -- $arms $arms
                shift "$rot"
                order=""; for _ in $(seq 1 "$m"); do order="$order $1"; shift; done
                for arm in $order; do
                    out=$(taskset -c "$CPU" "$OUT/$SET_ARTS/$sid/$arm/bin" time "$reg" "$OUT/$SET_SUBJ/$sid.$cls.$f" "$T" "$N") ||
                        { say "$SET_TAG TIME FAILED: $sid/$cls/$reg/$arm"; continue; }
                    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$sid" "$reg" "$cls" "$arm" \
                        "$(echo "$out" | awk '{print $2"\t"$4"\t"$6"\t"$8"\t"$10}')" >> "$tsv"
                done
            done
        done
    done
}

# both side sets' build and answer gate (each drops its own failing rows, never stops the job)
sets() { local x; for x in sample esh; do use_set $x; stage_set_build && stage_set_gate || return $?; done; }

cmd=${1:-}; OUT=${2:-}
[ -n "$OUT" ] || { sed -n '2,30p' "$0"; exit 64; }
mkdir -p "$OUT" "${TMPDIR:-$OUT}" || exit 1
case $cmd in
    smoke) stage_build && stage_diff && stage_gate && sets ;;
    run)
        L=${3:-5}; T=${4:-20000000}; N=${5:-9}
        ALLCELLS=1
        say "== s3t START $(date -Is) L=$L T=$T N=$N cpu=$CPU sibling=$SIB pcrec=$(sha256sum "$PCREC" | cut -c1-12)"
        stage_build || exit $?
        stage_diff || exit $?
        stage_gate || exit $?
        sets || exit $?
        say "== s3t STAGE time"
        timeloop "$L" "$T" "$N" || exit 1
        say "end sibling cpu$SIB=$(cpu_busy "$SIB" 2)% cpu$CPU=$(cpu_busy "$CPU" 2)%"
        say "final load1=$(cut -d' ' -f1 /proc/loadavg)"
        say "== s3t STAGE table"
        {
            echo "# job 588 (lane s3): D172 S3's acceptance, window_site.md rev 3.2 §6"
            echo
            echo "- the bar: the SCALAR layer (\`-fno-memfn-simd\`, the default); the SIMD-on layer (\`-fmemfn-simd\`) REPORTED, each cell against SIMD-on DEF; the official SIMD verdict stays pcrec-bench's (D144 addendum 4)"
            echo "- one compiler (the S3 build, pcrec $(sha256sum "$PCREC" | cut -c1-12)); arms by flags (measure_588.sh header); gcc -O2, no -march, one pinned core (cpu $CPU, sibling $SIB), $($CC --version | head -1)"
            echo "- L=$L launches, T=$T ns per sample, N=$N samples (job 581's calibration)"
        } > "$OUT/header.md"
        python3 -I "$here/read_588.py" "$OUT" "$OUT/header.md" "$R/r27b_table_581.md" > "$OUT/s3t_table.md" || exit 1
        cat "$OUT/s3t_table.md"
        rows=$(( $(wc -l < "$OUT/s3t_results.tsv") - 1 ))
        say "== s3t COMPLETE rows=$rows launches=$L"
        ;;
    *) exit 64 ;;
esac
