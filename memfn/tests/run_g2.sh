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
# lane g2x, folded by lane g2u: the SHAPE FAMILIES (g2/g2.h G2_FAM_*), the
# site shapes integration.md §15 says pcrec sends the kit, plus g2u's
# semantic differential (sem). Per family, the HARD sites the kit must
# RENDER (generator) and that must RUN (each compiler build). Both tiers
# generate the same sites, so these hold for --quick and the full run alike.
# Measured 2026-10-07 (Linux dev box, seed 20261005, lane g2u), less ~10%.
FAM_FLOORS="ofs:370 ofsrun:1230 stmt:330 onebyte:70 gate:260 setrest:54 vmrun:790 pf:260 sem:1370"
# distinct (opaque) form ids the families are rendered through: counted,
# never parsed (measured: 6 since lane g2pf; the PF shape's two are new)
FLOOR_FAM_FORMS=6
# PER-FORM floors (g2u item 8): hard sites RENDERED per reported form id
# (both tiers: the same sites), and answer CHECKS per form id, per tier.
# Form ids are opaque; a floor names one only to count it. Rendered and
# quick-check floors measured 2026-10-07 (Linux, seed 20261005) less ~10%;
# the FULL check floors are DERIVED (quick x 2.5, the original
# FLOOR_CHECKS/QUICK_FLOOR_CHECKS ratio being 3.9) and are owed a
# confirmation by the manager's first full run.
FORM_FLOORS="generic:5800 ofsskip:1120 precheck:270 runcmp:910 pf_memchr:380 pf_walk:400"
QUICK_FORM_CHECK_FLOORS="generic:22900000 ofsskip:5200000 precheck:960000 runcmp:2480000 pf_memchr:1300000 pf_walk:2150000"
FULL_FORM_CHECK_FLOORS="generic:57250000 ofsskip:13000000 precheck:2400000 runcmp:6200000 pf_memchr:3200000 pf_walk:5300000"
# the POISON differential (g2u item 6): sites poisoned, and per field the
# sites that field was poisoned on (a field whose count falls to 0 is a
# contract clause no longer exercised)
FLOOR_POISON_SITES=8100
FLOOR_POISON_FIELD_SITES=90
# the K-1 name check (site.pred.fn_ref on ALL_PRESENT FUNC): variants whose
# rendered names were checked against fn_name(fn_ref); DERIVED (3 value
# classes x >= 5 hard seeds), owed a measurement
FLOOR_SITEFN=15
# G2pf2: the USE-TIME refusal population. The two entry paths differ BY CONTRACT
# (memfn.h ROW CONTRACTS): mf_emit holds the use hooks at selection and picks a
# serving form; mf_define + mf_use selects with the define hooks and REFUSES, at
# mf_use / mf_call, a use the chosen form does not serve, naming the field. For
# each hard site the generator trial-renders mf_emit, tries define+use in a
# scratch art, counts a field-naming refusal at use as LAWFUL (USEREFUSE) and
# then judges the site, answer for answer, on the one-call path. A refusal at
# mf_define of a site mf_emit rendered, or one at use naming no field, FAILS.
# Measured quick 2026-10-07 (seed 20261005; generator count, tier-independent):
# lawful 26 = on_miss 11 + result_decl 15, unnamed 0; floors ~25% under.
FLOOR_USEREFUSE=20
FLOOR_USEREFUSE_ON_MISS=8
FLOOR_USEREFUSE_RESULT_DECL=11
# lane g2pf, the PF shape (integration.md 15.7 [R4g]). Per EDGE: generator
# cases (rendered + refused naming + refused not naming, sem variants included),
# and the sites of it the driver RAN (rendered ones; a refused-only edge runs
# none). Per CELL (driver, hard sites of every family incl. sem variants):
# sites, positive and negative answer checks, and for cells 3/4 the checks
# whose lo was PAST n. Measured quick 2026-10-07 (Linux, seed 20261005) less
# ~10-15%; both tiers run the same sites and the full tier has more checks.
PF_EDGE_CASE_FLOORS="miss-not-range-end:120 result-not-lo:50 stated-floor:75 stated-note:43 stated-result_decl:39 stated-on_miss:43 table-disagrees:43"
PF_EDGE_RUN_FLOORS="miss-not-range-end:120 result-not-lo:50 stated-floor:75 stated-note:43 stated-result_decl:39 stated-on_miss:43 table-disagrees:43"
# the PF family's own hard sites per form id (the cells reach the kit's PF rows:
# measured pf_memchr 120 (cells 1+2), pf_walk 168 (cells 3+4 and the table that
# disagrees); K35: a cell that fell back to the generic row would drop here)
PF_FAM_FORM_FLOORS="pf_memchr:110 pf_walk:150"
PF_CELL_FLOORS="1:230:750000:19000:0 2:190:600000:14000:0 3:225:660000:360000:330000 4:210:600000:340000:300000"
FLOOR_CLS_EDGE=375       # pf-edge class cases (generator); measured 418
# the semantic differential (g2u item 7): hard variant sites run per field
# the enforced classes' populations (generator cases, tier-independent):
FLOOR_CLS_HOOK=600       # hook-nonident; measured 728 (g2u2)
FLOOR_CLS_MISS=280       # miss-unstated; measured 314
FLOOR_CLS_NAME=12        # refusal-unnamed: the 12 missing-hook refusals
FLOOR_CLS_FNREF=40       # fn_ref-unstated: the explicit fn_ref-0 sample (provisional, re-pin from the first run)
FLOOR_SEM_FIELD_SITES=14     # measured quick: the smallest field (result_decl) 16
# W2 mutation 7 (floor - 1), G1: judged over the mutated sites where a
# REQUIRED term reads BELOW the candidate under a stated floor (the only
# sites where the mutant is never equivalent, floor <= lo being the
# caller's precondition, Q-G2-6). Population floor per tier; the kill-rate
# floor stays FLOOR_HOOK_KILL_PCT.
QUICK_FLOOR_MUT7_NEG=550       # measured quick: 615 (killed 570, 92.7%)
FLOOR_MUT7_NEG=1600            # DERIVED: the full run mutates every batch (~3x the quick sample); owed a measurement
# Row-contract enforcement is in force (memfn.h "THE ROW CONTRACTS"): every
# case of the ENFORCED CLASSES (formerly the PENDING-ENFORCE bucket; internal
# names keep "pend") is a HARD check by default. G2_STRICT_HOOKS=0 is the
# legacy diagnostic (bucket only, never a failure).
strict=${G2_STRICT_HOOKS:-1}
export G2_STRICT_HOOKS=$strict

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
for f in render_ok refusal_pass vocab_pass api_pass poison_pass strict_pass; do passed=$((passed + $(field $f))); done
gfail=0
for f in render_fail refusal_fail vocab_fail api_fail; do gfail=$((gfail + $(field $f))); done
[ "$gfail" -gt 0 ] && note_fail "$gfail" "generator stage (kit refused a contract site, rendered a refused shape, or an API call misbehaved): grep FAIL $work/gen/gen_results.txt"
pzf=$(field poison_fail)
[ "${pzf:-0}" -gt 0 ] && note_fail "$pzf" "poison differential: $pzf site(s) whose rendering moved when a field the contract says they do not use was junk: grep 'FAIL poison' $work/gen/gen_results.txt"
stf=$(field strict_fail)
[ "${stf:-0}" -gt 0 ] && note_fail "$stf" "enforced classes: $stf case(s) not served at generation: grep 'FAIL strict' $work/gen/gen_results.txt"
nref=$(( $(field refusal_pass) + $(field refusal_fail) + $(field api_pass) + $(field api_fail) ))
gres="$work/gen/gen_results.txt"

# --- 1a. the shape families, the form ids, the poison differential --------
echo "== shape families (hard sites rendered / refused, and the form ids they took)"
grep '^FAMILY' "$gres" | sed 's/^FAMILY /   /'
for fl_ in $FAM_FLOORS; do
    fn_=${fl_%%:*}; fv_=${fl_##*:}
    r_=$(grep "^FAMILY $fn_ " "$gres" | sed 's/.* rendered=\([0-9]*\).*/\1/')
    [ "${r_:-0}" -ge "$fv_" ] || note_fail 1 "family $fn_: ${r_:-0} sites rendered < floor $fv_ (K35: the shapes pcrec sends, unreached)"
done
for fl_ in $PF_FAM_FORM_FLOORS; do
    fn_=${fl_%%:*}; fv_=${fl_##*:}
    r_=$(grep '^FAMILY pf ' "$gres" | sed 's/.* forms=//' | tr ',' '\n' | sed -n "s/^$fn_://p")
    [ "${r_:-0}" -ge "$fv_" ] || note_fail 1 "family pf: form $fn_ rendered ${r_:-0} sites < floor $fv_ (a PF cell no longer reaches the kit's PF row)"
done
nforms=$(grep '^FAMILY' "$gres" | grep -v '^FAMILY base ' | sed 's/.* forms=//' | tr ',' '\n' \
         | grep -v '^-$' | sed 's/:[0-9]*$//' | sort -u | grep -c .)
echo "   distinct form ids over the families: $nforms (floor $FLOOR_FAM_FORMS)"
[ "$nforms" -ge "$FLOOR_FAM_FORMS" ] || note_fail 1 "families: $nforms distinct form ids < floor $FLOOR_FAM_FORMS"
echo "== per form id (hard sites rendered; floors FORM_FLOORS)"
grep '^FORMID' "$gres" | sed 's/^FORMID /   /'
for fl_ in $FORM_FLOORS; do
    fn_=${fl_%%:*}; fv_=${fl_##*:}
    r_=$(grep "^FORMID [0-9]* $fn_ " "$gres" | sed 's/.* rendered=\([0-9]*\).*/\1/')
    [ "${r_:-0}" -ge "$fv_" ] || note_fail 1 "form $fn_: ${r_:-0} hard sites rendered < floor $fv_"
done
sfn=$(grep '^SITEFN ' "$gres" | sed 's/.*checked=\([0-9]*\).*/\1/')
echo "== K-1 name check (ALL_PRESENT FUNC site.pred.fn_ref): variants checked ${sfn:-0}"
[ "${sfn:-0}" -ge "$FLOOR_SITEFN" ] || note_fail 1 "K-1 name check: ${sfn:-0} variants < floor $FLOOR_SITEFN"
ur_=$(grep '^USEREFUSE-TOTAL' "$gres")
echo "== use-time refusals on the define+use path (lawful; G2pf2): ${ur_#USEREFUSE-TOTAL }"
ur_n=$(echo "$ur_" | sed 's/.* lawful=\([0-9]*\).*/\1/')
ur_u=$(echo "$ur_" | sed 's/.* unnamed=\([0-9]*\).*/\1/')
ur_m=$(echo "$ur_" | sed 's/.* on_miss=\([0-9]*\).*/\1/')
ur_d=$(echo "$ur_" | sed 's/.* result_decl=\([0-9]*\).*/\1/')
[ "${ur_n:-0}" -ge "$FLOOR_USEREFUSE" ] || note_fail 1 "use-time refusals: ${ur_n:-0} < floor $FLOOR_USEREFUSE"
[ "${ur_m:-0}" -ge "$FLOOR_USEREFUSE_ON_MISS" ] || note_fail 1 "use-time refusals naming on_miss: ${ur_m:-0} < floor $FLOOR_USEREFUSE_ON_MISS"
[ "${ur_d:-0}" -ge "$FLOOR_USEREFUSE_RESULT_DECL" ] || note_fail 1 "use-time refusals naming result_decl: ${ur_d:-0} < floor $FLOOR_USEREFUSE_RESULT_DECL"
[ "${ur_u:-0}" -eq 0 ] || note_fail 1 "use-time refusals naming no field: ${ur_u}"
echo "== poison differential (fields the contract says a site does not use, set to junk)"
grep '^POISON ' "$gres" | sed 's/^/   /'
pzs=$(grep '^POISON ' "$gres" | sed 's/.* sites=\([0-9]*\).*/\1/')
[ "${pzs:-0}" -ge "$FLOOR_POISON_SITES" ] || note_fail 1 "poison: ${pzs:-0} sites poisoned < floor $FLOOR_POISON_SITES"
grep '^POISONFIELD' "$gres" | while read -r _ fn_ st_ mv_; do
    echo "   $fn_ ${st_} ${mv_}"
done
echo "== PF edges (lane g2pf; rendered + answer-equal, or refused naming the field)"
grep '^PFEDGE' "$gres" | sed 's/^PFEDGE /   /'
for fl_ in $PF_EDGE_CASE_FLOORS; do
    fn_=${fl_%%:*}; fv_=${fl_##*:}
    r_=$(grep "^PFEDGE $fn_ " "$gres" | sed 's/.* cases=\([0-9]*\) .*/\1/')
    [ "${r_:-0}" -ge "$fv_" ] || note_fail 1 "pf edge $fn_: ${r_:-0} cases < floor $fv_"
done
pzlow=$(grep '^POISONFIELD' "$gres" | awk -v f="$FLOOR_POISON_FIELD_SITES" '{split($3,a,"="); if (a[2] < f) print $2}' | paste -sd' ' -)
[ -z "$pzlow" ] || note_fail 1 "poison: fields poisoned on fewer than $FLOOR_POISON_FIELD_SITES sites: $pzlow"

# --- 1c. the libc record (lane g2x): MEMFN_LIBC against the compile -------
# §R4.3.3 [rev4.7] (Q53 RULED): the record lists the libc functions the
# artifact's code calls, a source-level inventory, constant-size idiom
# memcpy loads excluded, and "a delegated site's libc use is recorded by
# the kit through mf_art". The control is the compile's own, as the rule
# names it: `nm -u` of an -O0 -fno-builtin object. G2's own text in a batch
# (tables, descriptors, wrappers) calls no libc function, so every libc
# name a batch object needs is the kit's. memcpy is left out on both sides:
# G2 cannot tell an idiom load from a call without parsing. A PENDING-only
# batch whose object does not build (F1) is skipped, counted.
libc_check() {  # libc_check GENDIR
    local gd=$1 od="$work/libc" ok=0 bad=0 skip=0 b stamp got
    mkdir -p "$od"
    ls "$gd"/batch_*.c | "$TO" 900 xargs -P "$nproc_" -I{} sh -c \
        '"$1" -std=gnu11 -O0 -fno-builtin -w -I "$2" -c "$3" -o "$4/$(basename "$3" .c).o" 2>/dev/null' \
        _ "$gencc" "$g2" {} "$od"
    for b in "$gd"/batch_*.c; do
        if [ ! -f "$od/$(basename "$b" .c).o" ]; then
            if is_pending_batch "$b"; then skip=$((skip + 1)); continue; fi
            bad=$((bad + 1)); echo "   $(basename "$b"): does not build at -O0"; continue
        fi
        stamp=$(sed -n 's|^/\* stamp MEMFN_LIBC = \(.*\) \*/$|\1|p' "$b" | tr ',' '\n' \
                | grep -vx 'memcpy' | grep -vx 'none' | LC_ALL=C sort -u | paste -sd, -)
        got=$(nm -u "$od/$(basename "$b" .c).o" 2>/dev/null | sed 's/^ *U *//; s/^_//' \
              | grep -E '^(mem|str)[a-z0-9]*$' | grep -vx 'memcpy' | LC_ALL=C sort -u | paste -sd, -)
        if [ "$stamp" = "$got" ]; then ok=$((ok + 1))
        else
            bad=$((bad + 1))
            [ "$bad" -le 3 ] && echo "   $(basename "$b"): MEMFN_LIBC \"${stamp:-none}\", the compile calls \"${got:-none}\""
        fi
        # lane g2pf: the PF cells each fill a batch of their own, so the record is
        # judged (and shown) per cell
        pfc=$(grep "^PFBATCH $(basename "$b" .c) " "$gd/gen_results.txt" | sed 's/.*cell=//')
        [ -n "$pfc" ] && echo "   pf cell $pfc ($(basename "$b" .c)): MEMFN_LIBC \"${stamp:-none}\", the compile calls \"${got:-none}\""
    done
    echo "== libc record (MEMFN_LIBC vs nm -u of -O0 -fno-builtin, memcpy aside): batches agree $ok, disagree $bad, pending batches not built $skip"
    passed=$((passed + ok))
    [ "$bad" = 0 ] || note_fail "$bad" "libc record: MEMFN_LIBC is not the libc calls of the kit's text in $bad batch(es) (§R4.3.3; objects in $od)"
}
# a batch of PENDING-ENFORCE sites only (its header: "N sites, pending N")
is_pending_batch() {
    head -1 "$1" | grep -q 'batch [0-9]*, \([0-9]*\) sites, pending \1 \*/'
}
libc_check "$work/gen"

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
        # lane g2x: a batch that does not compile is a failure of every site
        # in it (the caller counts them, compile_fail_sites), or a PENDING-
        # ENFORCE outcome when the batch holds only PENDING sites; it is
        # linked as an EMPTY batch so the other batches' sites still run
        local f k
        for f in $(sed -n 's/^COMPILE-FAIL //p' "$bd/compile.log"); do
            k=$(basename "$f" .c | sed 's/^batch_//')
            printf '#include "g2.h"\nconst g2_site g2_batch_%s[] = { { 0 } };\nconst size_t g2_batch_%s_n = 0;\n' "$k" "$k" \
                > "$bd/stub_$k.c"
            "$TO" 300 "$cc" -std=gnu11 -O1 "$@" -I "$g2" -c "$bd/stub_$k.c" -o "$bd/batch_$k.o" || ok=0
        done
    fi
    "$TO" 300 "$cc" "$@" "$bd"/*.o -o "$bd/g2_run" || ok=0
    [ "$ok" = 1 ]
}

# the sites of the batches build NAME could not compile: "HARD PENDING"
compile_fail_sites() {  # compile_fail_sites NAME
    local f h=0 p=0 k
    for f in $(sed -n 's/^COMPILE-FAIL //p' "$work/build-$1/compile.log" 2>/dev/null); do
        k=$(sed -n '1s/.*batch [0-9]*, \([0-9]*\) sites.*/\1/p' "$f")
        if is_pending_batch "$f"; then p=$((p + ${k:-1})); else h=$((h + ${k:-1})); fi
    done
    echo "$h $p"
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
        line=$(grep '^G2 mutants: ' "$work/mut$m.log")
        echo "   W2 mutation $m: ${line#G2 mutants: }"
        mm=$(echo "$line" | sed 's/.*mutated \([0-9]*\).*/\1/')
        killed=$(echo "$line" | sed 's/.*killed \([0-9]*\).*/\1/')
        faults=$(echo "$line" | sed 's/.*faults \([0-9]*\).*/\1/')
        if [ "$m" -le 4 ]; then
            [ "${killed:-0}" -ge 1 ] || note_fail 1 "W2 text mutation $m caught no mutated site"
        else
            if [ "$m" = 7 ]; then
                # G1 (lane g2u): judged over the sites that read below the
                # candidate, where floor - 1 is never an equivalent mutant
                nl=$(grep '^G2 mutants reading below the candidate' "$work/mut$m.log")
                mm=$(echo "$nl" | sed 's/.*mutated \([0-9]*\).*/\1/')
                killed=$(echo "$nl" | sed 's/.*killed \([0-9]*\).*/\1/')
                echo "   W2 mutation 7, sites reading below the candidate: mutated ${mm:-?} killed ${killed:-?} (population floor $floor_m7neg)"
                [ "${mm:-0}" -ge "$floor_m7neg" ] || note_fail 1 "W2 mutation 7: ${mm:-0} mutated sites read below the candidate < floor $floor_m7neg"
            fi
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
    floor_m7neg=$QUICK_FLOOR_MUT7_NEG; form_check_floors=$QUICK_FORM_CHECK_FLOORS
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
    floor_m7neg=$FLOOR_MUT7_NEG; form_check_floors=$FULL_FORM_CHECK_FLOORS
fi

for cc in $cc_list; do
    if ! build "$cc" "$cc" "$work/gen"; then
        note_fail 1 "$cc: the driver, the reference or the link does not build ($work/build-$cc)"
        continue
    fi
    set -- $(compile_fail_sites "$cc")
    cfh=${1:-0}; cfp=${2:-0}
    if [ "$cfh" -gt 0 ] || [ "$cfp" -gt 0 ]; then
        echo "   $cc: rendered text that does not compile: $cfh hard site(s), $cfp PENDING-ENFORCE site(s):"
        for f in $(sed -n 's/^COMPILE-FAIL //p' "$work/build-$cc/compile.log"); do
            echo "     $(basename "$f")$(is_pending_batch "$f" && echo ' (PENDING)'): $(grep -m1 'error:' "$work/build-$cc/$(basename "$f" .c).log" | sed 's/.*error: //')"
        done
    fi
    [ "$cfh" -gt 0 ] && note_fail "$cfh" "$cc: rendered text does not compile ($work/build-$cc/compile.log)"
    if [ "$cfp" -gt 0 ] && [ "$strict" = 1 ]; then
        note_fail "$cfp" "$cc: G2_STRICT_HOOKS=1: PENDING-ENFORCE sites whose rendering does not compile"
    fi
    pend_compile_fail=$cfp
    # shellcheck disable=SC2086
    if ! run_driver "$cc" $drv_tier; then note_fail 1 "$cc: the driver did not finish ($work/run-$cc.err)"; fi
    log="$work/run-$cc.log"
    p=$(num "$log" "checks passed"); f=$(num "$log" "checks failed")
    s=$(num "$log" "sites run"); miss=$(num "$log" "coverage cells missing")
    echo "== $cc${drv_tier:+ (quick subjects)}: passed ${p:-?} failed ${f:-?} sites ${s:-?} coverage-missing ${miss:-?}"
    grep '^G2 \(faults\|sites failed\|layout\|cells\|subjects\|site features\|miss token\|instances\|sites with no\|on_miss_leaves\|family\|semantic\|form\|pending\|pf\)' "$log" | sed 's/^/   /'
    for fl_ in $FAM_FLOORS; do
        fn_=${fl_%%:*}; fv_=${fl_##*:}
        s_=$(grep "^G2 family $fn_:" "$log" | sed 's/.*: sites \([0-9]*\) .*/\1/')
        [ "${s_:-0}" -ge "$fv_" ] || note_fail 1 "$cc: family $fn_ ran ${s_:-0} sites < floor $fv_"
    done
    for fl_ in $form_check_floors; do
        fn_=${fl_%%:*}; fv_=${fl_##*:}
        k_=$(grep "^FORMID [0-9]* $fn_ " "$gres" | awk '{print $2}')
        c_=$(grep "^G2 form ${k_:-x}:" "$log" | sed 's/.* checks \([0-9]*\) .*/\1/')
        [ "${c_:-0}" -ge "$fv_" ] || note_fail 1 "$cc: form $fn_: ${c_:-0} answer checks < floor $fv_"
    done
    semlow=$(grep '^G2 semantic' "$log" | grep -v '^G2 semantic seed:' \
             | awk -v f="$FLOOR_SEM_FIELD_SITES" '{if ($5 + 0 < f) print $3}' | paste -sd' ' -)
    [ -z "$semlow" ] || note_fail 1 "$cc: semantic fields with fewer than $FLOOR_SEM_FIELD_SITES hard variant sites run: $semlow"
    for fl_ in $PF_EDGE_RUN_FLOORS; do
        fn_=${fl_%%:*}; fv_=${fl_##*:}
        s_=$(grep "^G2 pf edge $fn_:" "$log" | sed 's/.*: sites \([0-9]*\) .*/\1/')
        [ "${s_:-0}" -ge "$fv_" ] || note_fail 1 "$cc: pf edge $fn_ ran ${s_:-0} sites < floor $fv_"
    done
    for fl_ in $PF_CELL_FLOORS; do
        IFS=: read -r c_ fs_ fp_ fn2_ fo_ <<EOF_PF
$fl_
EOF_PF
        set -- $(grep "^G2 pf cell $c_:" "$log" | sed 's/.*: sites \([0-9]*\) checks [0-9]* positive \([0-9]*\) negative \([0-9]*\) lo-past-n \([0-9]*\) .*/\1 \2 \3 \4/')
        if [ $# != 4 ]; then note_fail 1 "$cc: no 'G2 pf cell $c_' census line"; continue; fi
        [ "$1" -ge "$fs_" ]  || note_fail 1 "$cc: pf cell $c_: sites $1 < floor $fs_"
        [ "$2" -ge "$fp_" ]  || note_fail 1 "$cc: pf cell $c_: positive checks $2 < floor $fp_"
        [ "$3" -ge "$fn2_" ] || note_fail 1 "$cc: pf cell $c_: negative checks $3 < floor $fn2_"
        [ "$4" -ge "$fo_" ]  || note_fail 1 "$cc: pf cell $c_: lo-past-n checks $4 < floor $fo_"
    done
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
# --- PENDING-ENFORCE: the bucket (never failures unless G2_STRICT_HOOKS=1)
echo "== ENFORCED CLASSES (formerly PENDING-ENFORCE; hard checks unless G2_STRICT_HOOKS=0; strict=$strict)"
grep '^PENDBUCKET' "$gres" | sed 's/^PENDBUCKET /   generator: /'
for cc in $cc_list; do
    grep '^G2 pending' "$work/run-$cc.log" 2>/dev/null | sed "s/^G2 pending /   $cc run: /"
done
echo "   rendered PENDING sites whose batch does not compile: ${pend_compile_fail:-0}"
pend_total=$(grep '^PENDBUCKET' "$gres" | sed 's/.*rendered=\([0-9]*\) refused_named=\([0-9]*\) refused_unnamed=\([0-9]*\)/\1 \2 \3/' \
             | awk '{t += $1 + $2 + $3} END {print t + 0}')
echo "ENFORCED-CLASS cases: $pend_total"
# class populations (named, floored, never dropped): generator outcomes
cls_floor() {   # NAME FLOOR
    n=$(grep "^PENDBUCKET $1 " "$gres" | sed 's/.*rendered=\([0-9]*\) refused_named=\([0-9]*\) refused_unnamed=\([0-9]*\)/\1 \2 \3/' | awk '{print $1 + $2 + $3}')
    echo "   class $1: ${n:-0} cases (floor $2)"
    [ "${n:-0}" -ge "$2" ] || note_fail 1 "enforced class $1: ${n:-0} cases < floor $2"
}
cls_floor hook-nonident "$FLOOR_CLS_HOOK"
cls_floor miss-unstated "$FLOOR_CLS_MISS"
cls_floor refusal-unnamed "$FLOOR_CLS_NAME"
cls_floor fn_ref-unstated "$FLOOR_CLS_FNREF"
cls_floor pf-edge "$FLOOR_CLS_EDGE"
echo "checks passed: $passed"
echo "checks failed: $failed"
if [ "$failed" -gt 0 ]; then
    echo "failures:$fail_notes"
    [ "$keep" = 1 ] || echo "(re-run with --keep to keep $work)"
    exit 1
fi
exit 0
