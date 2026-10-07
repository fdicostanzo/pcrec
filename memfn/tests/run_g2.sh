#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2, lane memfng2).
#
# memfn/tests/run_g2.sh — G2, the kit's own tests, in one command.
#
#   memfn/tests/run_g2.sh [--quick] [--seed N] [--keep]
#
# Generates sites over the kit's vocabulary, renders them through the kit
# (linked from build/libpcrec.a with only -I memfn/include), compiles the
# rendered text with every available compiler (gcc, clang) and an ASan+UBSan
# build, runs it on generated subjects in guarded memory layouts, and
# compares every answer with G2's own reference loop (g2/g2_ref.c). It also
# checks the kit's K1 mf_ref_* functions against G2's loops (g2/g2_k1.c).
# Then it proves the harness can fail: three planted-defect witnesses (W1 a
# wrong reference, W2 mutated kit text or hooks, W3 planted over-/under-
# reads) must fire.
#
# Prints `checks passed: N` / `checks failed: M`, the population against
# its floors (K35), and exits 0 only when M is 0, every floor holds and
# every witness fired. Work files go under $TMPDIR (the session scratchpad;
# never /tmp by default). Every step runs under GNU timeout.
#
# --quick (`make test-memfn-g2`, lane memfnfix): the same checks, judged by
# the same code, on a smaller population, in about a minute on the Mac.
#   - one compiler (gcc), every generated site, the quick subject tier;
#   - ASan+UBSan, W1, W2 and W3 run on a deterministic SAMPLE: every
#     QUICK_STRIDE-th batch of the same generated space, built from a
#     runner-written g2_all.c that lists only those batches;
#   - those legs run concurrently and are judged afterwards;
#   - the floors that scale are the QUICK_* literals below.
# The full run (`make test-memfn-g2-full`) is the one the report's numbers
# come from; --quick never replaces it.
set -u

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
g2="$here/g2"
lib="$root/build/libpcrec.a"
inc="$root/memfn/include"

seed=20261005
keep=0
quick=0
while [ $# -gt 0 ]; do
    case "$1" in
        --quick) quick=1; shift ;;
        --seed) seed=$2; shift 2 ;;
        --keep) keep=1; shift ;;
        *) echo "run_g2.sh: unknown option $1" >&2; exit 2 ;;
    esac
done

# --- the floors (K35): hand-written literals, sharing no source with the
# generator or the driver. Raise them when the space grows; never lower one
# to make a run pass. Measured 2026-10-05 (Mac, seed 20261005): see
# docs/dev/lanes/memfng2_report.md §2.
FLOOR_SITES=3900          # sites that ran >= 1 check, per compiler build
FLOOR_CHECKS=55000000     # answer checks per compiler build
FLOOR_ASAN_CHECKS=1500000 # checks in the ASan+UBSan (quick) build
FLOOR_REFUSALS=60         # refusal-table + API cases
FLOOR_K1_CHECKS=370000    # K1 mf_ref_* checks (deterministic: 377000 measured)
FLOOR_COMBOS=20           # (op, form, handoff) combinations
FLOOR_RUN_CELLS=1644      # RUN (offset x length x mask) cells, all of them
FLOOR_MT_SITES=500          # MF_MISS_N token sites (miss_mode 4), EXPR/FUNC/STMT, all handoffs
FLOOR_MT_RET=130           # ... of them RETURN
FLOOR_MT_ASSIGN=45          # ... of them ASSIGN
FLOOR_MT_FUNC=90            # ... of them FUNC/RETURN (define + call)
FLOOR_MT_CHECKS=1800000    # answer checks on token sites; quick measured 2188666 (the full run has more)
FLOOR_HOOK_KILL_PCT=65    # W2: % of hook-mutated sites caught, each of mutations 5-7
                          # (measured quick tier: 92 / 90 / 72)
# --quick: the sample stride, and the floors that scale with it (measured
# 2026-10-05, Mac, seed 20261005, lane memfnfix: see
# docs/dev/lanes/memfnfix_report.md). FLOOR_SITES, FLOOR_COMBOS,
# FLOOR_RUN_CELLS, FLOOR_REFUSALS, FLOOR_K1_CHECKS and FLOOR_HOOK_KILL_PCT
# hold unchanged: the quick gcc run still covers every site.
QUICK_STRIDE=3                 # batches 0, 3, 6, ... for ASan and the witnesses
QUICK_FLOOR_CHECKS=14000000    # gcc answer checks, every site, quick subjects
QUICK_FLOOR_ASAN_CHECKS=1500000  # ASan+UBSan checks on the sample

# --- tools ---------------------------------------------------------------
if command -v gnutimeout >/dev/null 2>&1; then TO=gnutimeout; else TO=timeout; fi
if ! "$TO" --version 2>/dev/null | grep -q GNU; then
    echo "run_g2.sh: need GNU timeout (bare timeout on the Mac, gnutimeout on ubuntubudu)" >&2
    exit 2
fi
nproc_=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)
cc_list=""
for c in gcc-16 gcc-15 gcc-14 gcc-13 gcc; do
    if command -v "$c" >/dev/null 2>&1 && "$c" --version 2>/dev/null | grep -qi 'free software\|gcc (GCC)\|gcc-'; then
        cc_list="$c"; break
    fi
done
[ "$quick" = 1 ] || { command -v clang >/dev/null 2>&1 && cc_list="$cc_list clang"; }
[ -n "$cc_list" ] || { echo "run_g2.sh: no gcc or clang" >&2; exit 2; }
asan_cc=""
command -v clang >/dev/null 2>&1 && asan_cc=clang
[ -f "$lib" ] || { echo "run_g2.sh: $lib missing (build pcrec first)" >&2; exit 2; }

: "${TMPDIR:?run_g2.sh: set TMPDIR to a scratch directory}"
work=$(mktemp -d "$TMPDIR/g2.XXXXXX") || exit 2
[ "$keep" = 1 ] || trap 'rm -rf "$work"' EXIT
echo "run_g2.sh: work $work; compilers: $cc_list${asan_cc:+; asan: $asan_cc}"

passed=0
failed=0
fail_notes=""
note_fail() { failed=$((failed + $1)); fail_notes="$fail_notes
  - $2"; }

# --- 1. the generator (the kit's only caller) ---------------------------
gencc=${cc_list%% *}
"$TO" 300 "$gencc" -std=gnu11 -O1 -I "$inc" "$g2/g2_gen.c" "$lib" -o "$work/g2_gen" \
    || { echo "run_g2.sh: the generator does not build" >&2; exit 2; }

gen() {  # gen OUTDIR [--mutate K]
    mkdir -p "$1"
    "$TO" 600 "$work/g2_gen" "$@" --seed "$seed"
}
gen "$work/gen" > "$work/gen.log" 2>&1 || { cat "$work/gen.log"; echo "run_g2.sh: generator failed" >&2; exit 2; }
cat "$work/gen.log"
sum=$(grep '^SUMMARY' "$work/gen/gen_results.txt")
[ -n "$sum" ] || { echo "run_g2.sh: no generator SUMMARY" >&2; exit 2; }
field() { echo "$sum" | tr ' ' '\n' | grep "^$1=" | cut -d= -f2; }
for f in render_ok refusal_pass vocab_pass api_pass; do passed=$((passed + $(field $f))); done
gfail=0
for f in render_fail refusal_fail vocab_fail api_fail; do gfail=$((gfail + $(field $f))); done
[ "$gfail" -gt 0 ] && note_fail "$gfail" "generator stage (kit refused a contract site, rendered a refused shape, or an API call misbehaved): grep FAIL $work/gen/gen_results.txt"
nref=$(( $(field refusal_pass) + $(field refusal_fail) + $(field api_pass) + $(field api_fail) ))

# --- 1b. K1: the kit's mf_ref_* reference functions against G2's loops ----
k1() {  # k1 NAME CC [flags]
    local name=$1 cc=$2; shift 2
    if "$TO" 300 "$cc" -std=gnu11 -O1 "$@" -I "$inc" "$g2/g2_k1.c" "$lib" -o "$work/g2_k1-$name" \
        && "$TO" 900 "$work/g2_k1-$name" > "$work/k1-$name.log" 2>&1; then
        local p f
        p=$(grep '^G2-K1 checks passed' "$work/k1-$name.log" | sed 's/.*: *//')
        f=$(grep '^G2-K1 checks failed' "$work/k1-$name.log" | sed 's/.*: *//')
        echo "== K1 mf_ref_* ($name): passed ${p:-?} failed ${f:-?}"
        passed=$((passed + ${p:-0}))
        [ "${f:-1}" = 0 ] || note_fail "${f:-1}" "K1 ($name): mf_ref_* disagrees with G2's loops ($work/k1-$name.log)"
        [ "${p:-0}" -ge "$FLOOR_K1_CHECKS" ] || note_fail 1 "K1 ($name): checks ${p:-0} < floor $FLOOR_K1_CHECKS"
    else
        note_fail 1 "K1 ($name): did not build or run ($work/k1-$name.log)"
    fi
}
k1 plain "$gencc"
[ -n "$asan_cc" ] && k1 asan "$asan_cc" -fsanitize=address,undefined -fno-sanitize-recover=undefined

# --- 2. compile + run, per compiler ---------------------------------------
build() {  # build NAME CC GENDIR EXTRA_FLAGS...
    local name=$1 cc=$2 gd=$3; shift 3
    local bd="$work/build-$name"
    mkdir -p "$bd"
    : > "$bd/compile.log"
    local ok=1
    # each batch on its own, in parallel; a batch that does not compile is
    # a failure of every site in it (named in compile.log)
    ls "$gd"/batch_*.c | "$TO" 1800 xargs -P "$nproc_" -I{} sh -c \
        '"$1" -std=gnu11 -O1 -Wall -Wno-unused-label -Wno-unused-variable -Wno-unused-function \
            -Werror=implicit-function-declaration '"$*"' -I "$2" -c "$3" -o "$4/$(basename "$3" .c).o" \
            >> "$4/$(basename "$3" .c).log" 2>&1 || echo "COMPILE-FAIL $3" >> "$4/compile.log"' \
        _ "$cc" "$g2" {} "$bd" || ok=0
    cat "$bd"/batch_*.log > "$bd/warnings.log" 2>/dev/null
    for f in g2_driver g2_ref; do
        "$TO" 300 "$cc" -std=gnu11 -O1 -Wall "$@" -I "$g2" -c "$g2/$f.c" -o "$bd/$f.o" || ok=0
    done
    "$TO" 300 "$cc" -std=gnu11 -O1 "$@" -I "$g2" -c "$gd/g2_all.c" -o "$bd/g2_all.o" || ok=0
    if grep -q COMPILE-FAIL "$bd/compile.log"; then
        echo "run_g2.sh: $name: batches that do not compile:" >&2
        grep COMPILE-FAIL "$bd/compile.log" >&2
        return 1
    fi
    "$TO" 300 "$cc" "$@" "$bd"/*.o -o "$bd/g2_run" || ok=0
    [ "$ok" = 1 ]
}

run_driver() {  # run_driver NAME [driver flags]
    local name=$1; shift
    "$TO" 3600 "$work/build-$name/g2_run" "$@" > "$work/run-$name.log" 2> "$work/run-$name.err"
    local rc=$?
    [ "$rc" = 0 ] || echo "run_g2.sh: $name driver exit $rc" >&2
    return $rc
}

num() { grep "^G2 $2" "$1" | head -1 | sed 's/.*: *//; s/ .*//'; }

# --quick: GENDIR's every QUICK_STRIDE-th batch, as a generator directory of
# its own (the batch files linked, g2_all.c rewritten to list only them)
sample() {  # sample GENDIR OUTDIR
    local gd=$1 od=$2 i=0 b keep_=""
    mkdir -p "$od"
    for b in "$gd"/batch_*.c; do
        if [ $((i % QUICK_STRIDE)) = 0 ]; then
            ln -s "$b" "$od/"
            keep_="$keep_ $(basename "$b" .c | sed 's/^batch_//')"
        fi
        i=$((i + 1))
    done
    {
        echo '#include "g2.h"'
        for k in $keep_; do echo "extern const g2_site g2_batch_$k[]; extern const size_t g2_batch_${k}_n;"; done
        echo 'const g2_site *const g2_batches[] = {'
        for k in $keep_; do echo "    g2_batch_$k,"; done
        echo '};'
        echo 'const size_t *const g2_batch_ns[] = {'
        for k in $keep_; do echo "    &g2_batch_${k}_n,"; done
        echo '};'
        echo "const size_t g2_nbatches = $(echo $keep_ | wc -w | tr -d ' ');"
    } > "$od/g2_all.c"
}

# Each leg below is a LAUNCH (build + run, writing only files under $work)
# and a JUDGE (reads those files, counts). The full run launches and judges
# each in turn; --quick launches the sampled legs at once, then judges.
asan_flags="-fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=undefined"
asan_launch() {  # asan_launch GENDIR
    # shellcheck disable=SC2086
    if build asan "$asan_cc" "$1" $asan_flags; then
        ASAN_OPTIONS=handle_segv=0:handle_sigbus=0:detect_leaks=0 run_driver asan --quick
        echo $? > "$work/asan.rc"
    else
        echo build > "$work/asan.rc"
    fi
}
w1_launch() {  # w1_launch BUILD K
    "$TO" 1800 "$work/build-$1/g2_run" --quick --ref-defect "$2" > "$work/w1-$2.log" 2>/dev/null
}
w3_launch() {  # w3_launch BUILD
    "$TO" 300 "$work/build-$1/g2_run" --witness-overread > "$work/w3.log" 2>/dev/null
}
w2_launch() {  # w2_launch M CC
    local m=$1 gd="$work/mut$1"
    if gen "$gd" --mutate "$m" > "$work/mut$m.gen.log" 2>&1; then
        if [ "$quick" = 1 ]; then sample "$gd" "$work/mutq$m"; gd="$work/mutq$m"; fi
        if build "mut$m" "$2" "$gd"; then
            "$TO" 3600 "$work/build-mut$m/g2_run" --quick --mutants > "$work/mut$m.log" 2>/dev/null
            echo ok > "$work/mut$m.st"
            return
        fi
    fi
    echo fail > "$work/mut$m.st"
}

asan_judge() {
    local rc
    rc=$(cat "$work/asan.rc" 2>/dev/null || echo none)
    if [ "$rc" = build ] || [ "$rc" = none ]; then
        note_fail 1 "asan: build failed"
        return
    fi
    [ "$rc" = 0 ] || note_fail 1 "asan: the driver stopped (a sanitizer report ends the run: $work/run-asan.err)"
    log="$work/run-asan.log"
    p=$(num "$log" "checks passed"); f=$(num "$log" "checks failed")
    echo "== asan+ubsan: passed ${p:-?} failed ${f:-?}"
    grep -m3 'ERROR: AddressSanitizer\|runtime error' "$work/run-asan.err" | sed 's/^/   /'
    passed=$((passed + ${p:-0}))
    [ "${f:-0}" -gt 0 ] && note_fail "$f" "asan: answer checks failed ($work/run-asan.err)"
    [ "${p:-0}" -ge "$floor_asan" ] || note_fail 1 "asan: checks ${p:-0} < floor $floor_asan"
}
w1_judge() {  # w1_judge K
    local k=$1
    wf=$(num "$work/w1-$k.log" "checks failed")
    echo "   W1 ref-defect $k: checks failed ${wf:-?} (must be > 0)"
    [ "${wf:-0}" -gt 0 ] || note_fail 1 "W1 ref-defect $k did not fire: the harness cannot tell this wrong reference from the kit"
}
w3_judge() {
    sed 's/^/   W3 /' "$work/w3.log"
    wo=$(grep 'overread over' "$work/w3.log" | sed 's/.*faults //')
    wu=$(grep 'overread under' "$work/w3.log" | sed 's/.*faults //')
    wc_=$(grep 'overread clean' "$work/w3.log" | sed 's/.*failed \([0-9]*\).*/\1/')
    [ "${wo:-0}" -gt 0 ] || note_fail 1 "W3 over-read did not fault: the upper guard page is not reached"
    [ "${wu:-0}" -gt 0 ] || note_fail 1 "W3 under-read did not fault: the lower guard page is not reached"
    [ "${wc_:-1}" = 0 ] || note_fail 1 "W3 clean control failed: the witness harness itself is wrong"
}
# W2: mutations 1-4 corrupt the kit's TEXT at a first textual match; many
# such mutants are equivalent (the kit's per-term read guards make a
# loosened loop bound unobservable), so each need only be caught at least
# once. Mutations 5-7 hand the kit a wrong hook, which is never equivalent
# on a site whose answer depends on it: they carry the kill-rate floor, and
# 6 (n + 1: the code reads s[n]) must fault on the guard page.
w2_judge() {  # w2_judge M
    local m=$1
    if [ "$(cat "$work/mut$m.st" 2>/dev/null)" = ok ]; then
        line=$(grep '^G2 mutants' "$work/mut$m.log")
        echo "   W2 mutation $m: ${line#G2 mutants: }"
        mm=$(echo "$line" | sed 's/.*mutated \([0-9]*\).*/\1/')
        killed=$(echo "$line" | sed 's/.*killed \([0-9]*\).*/\1/')
        faults=$(echo "$line" | sed 's/.*faults \([0-9]*\).*/\1/')
        if [ "$m" -le 4 ]; then
            [ "${killed:-0}" -ge 1 ] || note_fail 1 "W2 text mutation $m caught no mutated site"
        else
            [ $(( ${killed:-0} * 100 )) -ge $(( ${mm:-1} * FLOOR_HOOK_KILL_PCT )) ] \
                || note_fail 1 "W2 hook mutation $m caught ${killed:-0} of ${mm:-0} (< $FLOOR_HOOK_KILL_PCT%)"
        fi
        [ "$m" = 6 ] && { [ "${faults:-0}" -gt 0 ] || note_fail 1 "W2 mutation 6 (n + 1) never faulted: the upper guard page missed a kit over-read"; }
        [ "$m" = 7 ] && { [ "${faults:-0}" -gt 0 ] || note_fail 1 "W2 mutation 7 (fl - 1) never faulted: the lower guard page missed a kit under-read"; }
    else
        nb=$(grep -c COMPILE-FAIL "$work/build-mut$m/compile.log" 2>/dev/null || echo 0)
        echo "   W2 mutation $m: $nb batch(es) no longer compile"
        note_fail 1 "W2 mutation $m did not build: the witness did not run"
    fi
}

if [ "$quick" = 1 ]; then
    floor_checks=$QUICK_FLOOR_CHECKS; floor_asan=$QUICK_FLOOR_ASAN_CHECKS; drv_tier=--quick
    wcc=${cc_list%% *}
    # the sampled legs, launched together; the gcc answer run below is the
    # foreground leg
    sample "$work/gen" "$work/genq"
    [ -n "$asan_cc" ] && asan_launch "$work/genq" > "$work/asan.out" 2>&1 &
    { if build wq "$wcc" "$work/genq"; then
          for k in 1 2 3; do w1_launch wq "$k" & done
          w3_launch wq
          wait
      fi; } > "$work/wq.out" 2>&1 &
    for m in 1 2 3 4 5 6 7; do w2_launch "$m" "$wcc" > "$work/mut$m.out" 2>&1 & done
else
    floor_checks=$FLOOR_CHECKS; floor_asan=$FLOOR_ASAN_CHECKS; drv_tier=
fi

for cc in $cc_list; do
    if ! build "$cc" "$cc" "$work/gen"; then
        nb=$(grep -c COMPILE-FAIL "$work/build-$cc/compile.log" 2>/dev/null || echo 0)
        note_fail $((nb > 0 ? nb : 1)) "$cc: rendered text does not compile ($work/build-$cc/compile.log)"
        continue
    fi
    # shellcheck disable=SC2086
    if ! run_driver "$cc" $drv_tier; then note_fail 1 "$cc: the driver did not finish ($work/run-$cc.err)"; fi
    log="$work/run-$cc.log"
    p=$(num "$log" "checks passed"); f=$(num "$log" "checks failed")
    s=$(num "$log" "sites run"); miss=$(num "$log" "coverage cells missing")
    echo "== $cc${drv_tier:+ (quick subjects)}: passed ${p:-?} failed ${f:-?} sites ${s:-?} coverage-missing ${miss:-?}"
    grep '^G2 \(faults\|sites failed\|layout\|cells\|subjects\|site features\|miss token\|instances\|sites with no\)' "$log" | sed 's/^/   /'
    passed=$((passed + ${p:-0}))
    [ "${f:-1}" -gt 0 ] && note_fail "${f:-1}" "$cc: answer checks failed (first failures: $work/run-$cc.err)"
    [ "${s:-0}" -ge "$FLOOR_SITES" ] || note_fail 1 "$cc: sites run ${s:-0} < floor $FLOOR_SITES"
    [ "${p:-0}" -ge "$floor_checks" ] || note_fail 1 "$cc: checks ${p:-0} < floor $floor_checks"
    if [ "$quick" = 1 ]; then
        # the quick subject tier samples alignments (4 of 16): that axis
        # is the full run's to cover, every other coverage cell is ours
        cm=$(grep '^G2 coverage MISSING' "$log" | grep -vc 'MISSING: subject axes$')
        set -- $(grep '^G2 subjects' "$log" | sed 's/.*lengths \([0-9]*\)\/\([0-9]*\), planted-hit offsets \([0-9]*\)\/\([0-9]*\), alignments \([0-9]*\)\/\([0-9]*\)$/\1 \2 \3 \4 \5 \6/')
        sa=0
        [ $# = 6 ] && [ "$1" = "$2" ] && [ "$3" = "$4" ] && [ "$5" != "$6" ] && sa=1
        [ "${miss:-1}" = $((cm + sa)) ] || note_fail 1 "$cc: coverage count ${miss:-?} is not its MISSING lines (grep MISSING $log)"
        [ "$cm" = 0 ] || note_fail "$cm" "$cc: coverage cells missing (grep MISSING $log)"
    else
        [ "${miss:-1}" = 0 ] || note_fail "${miss:-1}" "$cc: coverage cells missing (grep MISSING $log)"
    fi
    combos=$(sed -n '/^G2 census/,/^G2 cells/p' "$log" | grep -c '^  [A-Z]*/[A-Z]*/[A-Z_]* *[1-9]')
    [ "$combos" -ge "$FLOOR_COMBOS" ] || note_fail 1 "$cc: combinations run $combos < floor $FLOOR_COMBOS"
    rc_=$(grep '^G2 cells' "$log" | sed 's/.*RUN (offset x length x mask) \([0-9]*\)\/.*/\1/')
    [ "${rc_:-0}" -ge "$FLOOR_RUN_CELLS" ] || note_fail 1 "$cc: RUN cells ${rc_:-0} < floor $FLOOR_RUN_CELLS"
    # the MF_MISS_N token cells (R6 coverage): sites by shape, and the answer
    # checks that ran on them against G2's reference
    set -- $(grep '^G2 miss token' "$log" | sed 's/.*sites \([0-9]*\) (RETURN \([0-9]*\), ASSIGN \([0-9]*\), FUNC\/RETURN \([0-9]*\)), checks \([0-9]*\).*/\1 \2 \3 \4 \5/')
    if [ $# = 5 ]; then
        [ "$1" -ge "$FLOOR_MT_SITES" ]  || note_fail 1 "$cc: MF_MISS_N sites $1 < floor $FLOOR_MT_SITES"
        [ "$2" -ge "$FLOOR_MT_RET" ]    || note_fail 1 "$cc: MF_MISS_N RETURN sites $2 < floor $FLOOR_MT_RET"
        [ "$3" -ge "$FLOOR_MT_ASSIGN" ] || note_fail 1 "$cc: MF_MISS_N ASSIGN sites $3 < floor $FLOOR_MT_ASSIGN"
        [ "$4" -ge "$FLOOR_MT_FUNC" ]   || note_fail 1 "$cc: MF_MISS_N FUNC/RETURN sites $4 < floor $FLOOR_MT_FUNC"
        [ "$5" -ge "$FLOOR_MT_CHECKS" ] || note_fail 1 "$cc: MF_MISS_N checks $5 < floor $FLOOR_MT_CHECKS"
    else
        note_fail 1 "$cc: no 'G2 miss token' census line in $log"
    fi
    grep -c . "$work/build-$cc/warnings.log" | sed "s/^/   compiler diagnostics lines ($cc): /"
done

# --- 3. ASan + UBSan (quick subjects) --------------------------------------
if [ "$quick" = 1 ]; then
    wait
    [ -n "$asan_cc" ] && asan_judge
elif [ -n "$asan_cc" ]; then
    asan_launch "$work/gen"
    asan_judge
fi

# --- 4. the witnesses: the harness must be able to fail ---------------------
wcc=${cc_list%% *}
if [ "$quick" = 1 ]; then
    echo "== witnesses (W1 wrong reference, W2 mutated kit text, W3 planted reads), on $wcc, sampled batches"
    [ -x "$work/build-wq/g2_run" ] || note_fail 1 "the sampled witness build failed ($work/wq.out)"
else
    echo "== witnesses (W1 wrong reference, W2 mutated kit text, W3 planted reads), on $wcc"
    for k in 1 2 3; do w1_launch "$wcc" "$k"; done
    w3_launch "$wcc"
fi
for k in 1 2 3; do w1_judge "$k"; done
w3_judge
for m in 1 2 3 4 5 6 7; do
    [ "$quick" = 1 ] || w2_launch "$m" "$wcc"
    w2_judge "$m"
done

# --- 5. the verdict ------------------------------------------------------------
echo "population: generator sites $(field sites_generated) in $(field batches) batches;" \
     "refusal+API cases $nref (floor $FLOOR_REFUSALS)"
[ "$nref" -ge "$FLOOR_REFUSALS" ] || note_fail 1 "refusal+API cases $nref < floor $FLOOR_REFUSALS"
echo "checks passed: $passed"
echo "checks failed: $failed"
if [ "$failed" -gt 0 ]; then
    echo "failures:$fail_notes"
    [ "$keep" = 1 ] || echo "(re-run with --keep to keep $work)"
    exit 1
fi
exit 0
