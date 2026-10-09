#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2, lane memfng2).
#
# memfn/tests/run_g2.sh — G2, the kit's own tests, in one command.
#
#   memfn/tests/run_g2.sh [--quick] [--rows|--no-rows] [--seed N] [--keep]
#
# --rows: per-ROW floor from the kit's MFTRACE REACH lines (section 4b)
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
rows=0
norows=0
while [ $# -gt 0 ]; do
    case "$1" in
        --quick) quick=1; shift ;;
        --rows) rows=1; shift ;;
        --no-rows) norows=1; shift ;;
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
# Measured 2026-10-07 (Linux dev box, seed 20261005, lane g2u), less ~10%;
# mline measured 2026-10-08 (lane g2m4: 406 rendered and run), less ~10%.
FAM_FLOORS="ofs:370 ofsrun:1230 stmt:330 onebyte:70 gate:260 setrest:54 vmrun:790 pf:260 mline:360 mismatch:185 sem:1370"
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
FORM_FLOORS="generic:5800 ofsskip:1120 precheck:270 runcmp:910 pf_memchr:380 pf_walk:400 mismatch_inplace:62"
QUICK_FORM_CHECK_FLOORS="generic:22900000 ofsskip:5200000 precheck:960000 runcmp:2480000 pf_memchr:1300000 pf_walk:2150000 mismatch_inplace:290000"
FULL_FORM_CHECK_FLOORS="generic:57250000 ofsskip:13000000 precheck:2400000 runcmp:6200000 pf_memchr:3200000 pf_walk:5300000 mismatch_inplace:725000"
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
FLOOR_CLS_LOOPX=140      # loop-exit class cases (generator: sites + the 7 refusal-table shapes); measured 161
FLOOR_LOOPX_MUT=115      # W2 mutation 8: LOOP_EXIT sites mutated (measured 130; every one must be killed)
# lane g2m4, MF_SITE_ABI 6: the three contract changes, each a counted population
# (hard sites that RAN; tier-independent site counts, quick check counts, the
# full tier has more). Measured 2026-10-08, Linux dev box, seed 20261005, less ~10%.
#   Q-R7-1 read-bounded range: reads-below FIND sites (458), their checks (1.67M),
#     checks whose planted hit IS the candidate n (304k), answers that ARE a hit at n (125k)
#   Q-R7-2 AT_N: sites (454), checks (1.65M), checks run with lo == n (67k)
#   Q-R7-3 LOOP_EXIT: sites (130), checks (467k), checks that took the break (26k) and
#     that fell through (441k)
FLOOR_RB_SITES=410;   FLOOR_RB_CHECKS=1500000; FLOOR_RB_PLANT_N=270000; FLOOR_RB_HIT_N=110000
FLOOR_ATN_SITES=410;  FLOOR_ATN_CHECKS=1480000; FLOOR_ATN_LO_N=60000
FLOOR_LX_SITES=115;   FLOOR_LX_CHECKS=420000;  FLOOR_LX_BREAK=23000; FLOOR_LX_FALL=390000
# lane g2m7, MF_SITE_ABI 7: MF_OP_MISMATCH (R-8, M7). G2 GENERATES the fold maps (identity, ASCII /
# Latin-1 lower, upper, per-pair random representative, and a bijection after a representative: the
# last two NON-idempotent), spells each in both text shapes, and holds the spelled text to the map
# (mm_chk). Floors: hard sites that RAN (tier-independent), their answer checks (quick), and the
# populations that make the answers mean something. Measured 2026-10-08, Linux dev box, seed
# 20261005, quick tier, less ~10%.
FLOOR_MM_SITES=185;      FLOOR_MM_CHECKS=870000
FLOOR_MM_EQ=395000;        FLOOR_MM_DIFF=470000;     FLOOR_MM_DIFF0=225000;   FLOOR_MM_DIFFLAST=150000;  FLOOR_MM_ENDED=208000
FLOOR_MM_RL0=170000;       FLOOR_MM_LOGEN=195000;    FLOOR_MM_FOLDDEC=195000; FLOOR_MM_DECOY=70000
FLOOR_MM_NONIDEM=42;   FLOOR_MM_ALIAS=41000;    FLOOR_MM_SNULL=5500;   FLOOR_MM_RNULL=83000
FLOOR_MM_SITES_ASCII=61; FLOOR_MM_SITES_UCP=62; FLOOR_MM_SITES_EXPR=61; FLOOR_MM_SITES_STMT=62
FLOOR_MM_REFUSALS=510   # MISMATCH refusal cases (generator): header-derived + vocabulary-absent
FLOOR_MM_POISON=185     # REF-term junk-data renderings, every one byte-identical
FLOOR_MMMUT_SITES=185; FLOOR_MMMUT_FOLD_SITES=61   # W2 9/10 mutated MISMATCH sites; W2 11 the caseless ones
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
# --quick includes the rows half (measured cost: none, see G2ROWS_REPORT.md);
# --no-rows leaves it out
[ "$quick" = 1 ] && [ "$norows" = 0 ] && rows=1
# --rows (N4 follow-up, the per-ROW floor): every process that calls the kit
# links the MF_TRACE build instead; the REACH lines it writes at exit are
# summed in section 4b. The plain library is kept for the (d) control.
plainlib="$lib"
[ "$rows" = 1 ] && lib="$root/build/libpcrec_mftrace.a"
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

mkdir -p "$work/reach"
gen() {  # gen OUTDIR [--mutate K]
    mkdir -p "$1"
    if [ "$rows" = 1 ]; then
        # stderr to a file of its own (one per generator process); the
        # non-trace lines are passed on as before
        local rf="$work/reach/gen-$(basename "$1").err" rc_
        "$TO" 600 "$work/g2_gen" "$@" --seed "$seed" 2> "$rf"; rc_=$?
        grep -v '^MFTRACE ' "$rf" >&2
        return $rc_
    fi
    "$TO" 600 "$work/g2_gen" "$@" --seed "$seed"
}
gen "$work/gen" > "$work/gen.log" 2>&1 || { cat "$work/gen.log"; echo "run_g2.sh: generator failed" >&2; exit 2; }
# lane g2m7: a generator process of its OWN that makes only the MISMATCH sites, so the rows chosen
# for them are countable apart from every other family's (section 4b prints them)
[ "$rows" = 1 ] && { gen "$work/mmonly" --mm-only 1 > "$work/mmonly.log" 2>&1 || { cat "$work/mmonly.log"; echo "run_g2.sh: the MISMATCH-only generator failed" >&2; exit 2; }; }
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
echo "== LOOP_EXIT (Q-R7-3) rendered sites by form id: $(grep '^LOOPX forms=' "$gres" | sed 's/^LOOPX forms=//')"
if grep '^LOOPX forms=' "$gres" | grep -q 'generic'; then
    note_fail 1 "LOOP_EXIT: the generic row rendered a site (Q-R7-3: it serves none)"
fi
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
echo "== MISMATCH (lane g2m7): generator populations"
grep '^MMSITES\|^MMVARS\|^MMREFUSE\|^MMPOISON\|^INFO vocab.* mm' "$gres" | sed 's/^/   /'
mmr_=$(grep '^MMREFUSE' "$gres" | sed 's/.*cases=\([0-9]*\) .*/\1/')
[ "${mmr_:-0}" -ge "$FLOOR_MM_REFUSALS" ] || note_fail 1 "MISMATCH refusal cases ${mmr_:-0} < floor $FLOOR_MM_REFUSALS"
mmp_=$(grep '^MMPOISON' "$gres" | sed 's/.*identical=\([0-9]*\) .*/\1/')
[ "${mmp_:-0}" -ge "$FLOOR_MM_POISON" ] || note_fail 1 "MISMATCH REF-term poison renderings ${mmp_:-0} < floor $FLOOR_MM_POISON"
[ "$(grep '^MMPOISON' "$gres" | sed 's/.*differ=\([0-9]*\) .*/\1/')" = 0 ] || note_fail 1 "MISMATCH rendering moved with junk in the REF term's unread fields"
[ "$(grep '^MMPOISON' "$gres" | sed 's/.*control_unstable=\([0-9]*\).*/\1/')" = 0 ] || note_fail 1 "MISMATCH poison control: a clean re-rendering is not byte-identical"
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
sample() {  # sample GENDIR OUTDIR [pend]
    local gd=$1 od=$2 mode=${3:-stride} i=0 b keep_="" take
    mkdir -p "$od"
    for b in "$gd"/batch_*.c; do
        # mode pend (lane g2m4, W2 mutation 8): the batches that hold ONLY enforced-class
        # sites, where the LOOP_EXIT sites live; they are few and every one is wanted
        take=0
        if [ "$mode" = pend ]; then is_pending_batch "$b" && take=1
        else [ $((i % QUICK_STRIDE)) = 0 ] && take=1; fi
        if [ "$take" = 1 ]; then
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
        if [ "$quick" = 1 ]; then
            if [ "$m" = 8 ]; then sample "$gd" "$work/mutq$m" pend; elif [ "$m" -lt 9 ]; then sample "$gd" "$work/mutq$m"; fi
            [ "$m" -ge 9 ] || gd="$work/mutq$m"
        fi
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
    # lane g2m7: MISMATCH's two operands each have a guard page on both sides
    for w_ in mm-ref-over mm-ref-under mm-s-over mm-s-under; do
        wf_=$(grep "overread $w_:" "$work/w3.log" | sed 's/.*faults //')
        [ "${wf_:-0}" -gt 0 ] || note_fail 1 "W3 $w_ did not fault: the guard page for that read is not reached"
    done
    wmc_=$(grep 'overread mm-clean:' "$work/w3.log" | sed 's/.*failed \([0-9]*\).*/\1/')
    [ "${wmc_:-1}" = 0 ] || note_fail 1 "W3 mm-clean control failed: the MISMATCH witness harness itself is wrong"
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
        elif [ "$m" = 8 ]; then
            # lane g2m4 (Q-R7-3): every LOOP_EXIT site's kit text wrapped in a loop of ITS OWN, so
            # the break leaves that loop and not the driver's. A site that misses even once
            # cannot be an equivalent mutant, so EVERY mutated site must be caught
            echo "   W2 mutation 8, LOOP_EXIT sites (population floor $FLOOR_LOOPX_MUT): mutated ${mm:-?} killed ${killed:-?}"
            [ "${mm:-0}" -ge "$FLOOR_LOOPX_MUT" ] || note_fail 1 "W2 mutation 8: ${mm:-0} LOOP_EXIT sites mutated < floor $FLOOR_LOOPX_MUT"
            [ "${killed:-0}" = "${mm:-x}" ] || note_fail 1 "W2 mutation 8: a kit break inside a loop of its own was caught on ${killed:-0} of ${mm:-0} LOOP_EXIT sites (must be all): the driver-owned-loop check does not see where the break goes"
        elif [ "$m" -ge 9 ]; then
            # lane g2m7 (MISMATCH, MF_SITE_ABI 7): W2 9 hands the kit reflen + 1, 10 the subject as the
            # reference, 11 a fold that does nothing (caseless sites only). Each changes a hook the answer
            # depends on, so a mutated site that survives every instance is a hole: EVERY one must be caught
            echo "   W2 mutation $m, MISMATCH sites (population floor $FLOOR_MMMUT_SITES): mutated ${mm:-?} killed ${killed:-?}"
            fl_=$FLOOR_MMMUT_SITES; [ "$m" = 11 ] && fl_=$FLOOR_MMMUT_FOLD_SITES
            [ "${mm:-0}" -ge "$fl_" ] || note_fail 1 "W2 mutation $m: ${mm:-0} MISMATCH sites mutated < floor $fl_"
            [ "${killed:-0}" = "${mm:-x}" ] || note_fail 1 "W2 mutation $m: a MISMATCH site given a wrong hook was caught on ${killed:-0} of ${mm:-0} sites (must be all)"
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
        if [ "$m" = 9 ]; then
            # the fault must come from the REFERENCE's own guard page (a non-alias instance with reflen > 0), not from
            # a NULL reference at reflen 0 or from the subject's guard through an alias
            rg_=$(grep '^G2 mutants MISMATCH reference-guard faults' "$work/mut$m.log" | sed 's/.*: *//')
            echo "   W2 mutation 9, faults on the reference's guard pages (non-alias, reflen > 0): ${rg_:-?} (must be > 0)"
            [ "${rg_:-0}" -gt 0 ] || note_fail 1 "W2 mutation 9 (reflen + 1) never faulted on the reference's guard page: a kit over-read of ref[reflen] goes unseen"
        fi
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
          for k in 1 2 3 4 5 6 7; do w1_launch wq "$k" & done
          w3_launch wq
          wait
      fi; } > "$work/wq.out" 2>&1 &
    for m in 1 2 3 4 5 6 7 8 9 10 11; do w2_launch "$m" "$wcc" > "$work/mut$m.out" 2>&1 & done
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
    grep '^G2 \(faults\|sites failed\|layout\|cells\|subjects\|site features\|miss token\|instances\|sites with no\|on_miss_leaves\|read-bounded\|AT_N\|loop-exit\|mismatch\|family\|semantic\|form\|pending\|pf\)' "$log" | sed 's/^/   /'
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
    # lane g2m4: the three MF_SITE_ABI 6 populations (driver census lines)
    set -- $(grep '^G2 read-bounded range (Q-R7-1)' "$log" | sed 's/.*sites \([0-9]*\), checks \([0-9]*\), planted hit at n \([0-9]*\), answers that ARE a hit at n \([0-9]*\)$/\1 \2 \3 \4/')
    if [ $# = 4 ]; then
        [ "$1" -ge "$FLOOR_RB_SITES" ]   || note_fail 1 "$cc: read-bounded range: reads-below FIND sites $1 < floor $FLOOR_RB_SITES"
        [ "$2" -ge "$FLOOR_RB_CHECKS" ]  || note_fail 1 "$cc: read-bounded range: checks $2 < floor $FLOOR_RB_CHECKS"
        [ "$3" -ge "$FLOOR_RB_PLANT_N" ] || note_fail 1 "$cc: read-bounded range: checks with the planted hit at n $3 < floor $FLOOR_RB_PLANT_N"
        [ "$4" -ge "$FLOOR_RB_HIT_N" ]   || note_fail 1 "$cc: read-bounded range: answers that ARE a hit at n $4 < floor $FLOOR_RB_HIT_N"
    else
        note_fail 1 "$cc: no 'G2 read-bounded range' census line in $log"
    fi
    set -- $(grep '^G2 AT_N' "$log" | sed 's/.*sites \([0-9]*\) checks \([0-9]*\) checks with lo == n \([0-9]*\),.*/\1 \2 \3/')
    if [ $# = 3 ]; then
        [ "$1" -ge "$FLOOR_ATN_SITES" ]  || note_fail 1 "$cc: AT_N sites $1 < floor $FLOOR_ATN_SITES"
        [ "$2" -ge "$FLOOR_ATN_CHECKS" ] || note_fail 1 "$cc: AT_N checks $2 < floor $FLOOR_ATN_CHECKS"
        [ "$3" -ge "$FLOOR_ATN_LO_N" ]   || note_fail 1 "$cc: AT_N checks with lo == n $3 < floor $FLOOR_ATN_LO_N"
    else
        note_fail 1 "$cc: no 'G2 AT_N' census line in $log"
    fi
    set -- $(grep '^G2 loop-exit' "$log" | sed 's/.*sites \([0-9]*\) checks \([0-9]*\) break-path \([0-9]*\) fall-through \([0-9]*\)$/\1 \2 \3 \4/')
    if [ $# = 4 ]; then
        [ "$1" -ge "$FLOOR_LX_SITES" ]  || note_fail 1 "$cc: LOOP_EXIT sites $1 < floor $FLOOR_LX_SITES"
        [ "$2" -ge "$FLOOR_LX_CHECKS" ] || note_fail 1 "$cc: LOOP_EXIT checks $2 < floor $FLOOR_LX_CHECKS"
        [ "$3" -ge "$FLOOR_LX_BREAK" ]  || note_fail 1 "$cc: LOOP_EXIT checks that took the break $3 < floor $FLOOR_LX_BREAK"
        [ "$4" -ge "$FLOOR_LX_FALL" ]   || note_fail 1 "$cc: LOOP_EXIT checks that fell through $4 < floor $FLOOR_LX_FALL"
    else
        note_fail 1 "$cc: no 'G2 loop-exit' census line in $log"
    fi
    # lane g2m7: the MISMATCH populations (driver census lines)
    mml_=$(grep '^G2 mismatch (R-8):' "$log")
    mmv_() { echo "$mml_" | sed -n "s/.*$1 \([0-9]*\).*/\1/p" | head -1; }
    if [ -n "$mml_" ]; then
        mmchk_() {  # mmchk_ LABEL VALUE FLOOR
            [ "${2:-0}" -ge "$3" ] || note_fail 1 "$cc: MISMATCH $1 ${2:-0} < floor $3"
        }
        mmchk_ sites "$(mmv_ sites)" "$FLOOR_MM_SITES"
        mmchk_ checks "$(mmv_ checks)" "$FLOOR_MM_CHECKS"
        mmchk_ "equal outcomes" "$(mmv_ equal)" "$FLOOR_MM_EQ"
        mmchk_ "difference outcomes" "$(mmv_ diff)" "$FLOOR_MM_DIFF"
        mmchk_ "differences at 0" "$(mmv_ diff-at-0)" "$FLOOR_MM_DIFF0"
        mmchk_ "differences at reflen-1" "$(mmv_ diff-at-reflen-1)" "$FLOOR_MM_DIFFLAST"
        mmchk_ "ended by the subject" "$(mmv_ ended-by-subject)" "$FLOOR_MM_ENDED"
        mmchk_ "reflen 0" "$(mmv_ reflen-0)" "$FLOOR_MM_RL0"
        mmchk_ "lo >= n" "$(mmv_ lo-ge-n)" "$FLOOR_MM_LOGEN"
        mmchk_ "fold-decided answers" "$(mmv_ fold-decided)" "$FLOOR_MM_FOLDDEC"
        mmchk_ "near-class decoys" "$(mmv_ near-class-decoys)" "$FLOOR_MM_DECOY"
    else
        note_fail 1 "$cc: no 'G2 mismatch (R-8)' census line in $log"
    fi
    mms_=$(grep '^G2 mismatch sites:' "$log")
    if [ -n "$mms_" ]; then
        mmchk_ "ASCII sites" "$(echo "$mms_" | sed -n 's/.*ascii \([0-9]*\).*/\1/p')" "$FLOOR_MM_SITES_ASCII"
        mmchk_ "UCP sites" "$(echo "$mms_" | sed -n 's/.*ucp \([0-9]*\).*/\1/p')" "$FLOOR_MM_SITES_UCP"
        mmchk_ "FOLD_EXPR sites" "$(echo "$mms_" | sed -n 's/.*expr \([0-9]*\).*/\1/p')" "$FLOOR_MM_SITES_EXPR"
        mmchk_ "FOLD_STMT sites" "$(echo "$mms_" | sed -n 's/.*stmt \([0-9]*\).*/\1/p')" "$FLOOR_MM_SITES_STMT"
        mmchk_ "non-idempotent-map sites" "$(echo "$mms_" | sed -n 's/.*non-idempotent maps \([0-9]*\).*/\1/p')" "$FLOOR_MM_NONIDEM"
        [ "$(echo "$mms_" | sed -n 's/.*hook-text checks ok [0-9]* bad \([0-9]*\).*/\1/p')" = 0 ] || note_fail 1 "$cc: a generated fold text does not realize its generated map"
    else
        note_fail 1 "$cc: no 'G2 mismatch sites' census line in $log"
    fi
    mmo_=$(grep '^G2 mismatch operands:' "$log")
    if [ -n "$mmo_" ]; then
        mmchk_ "aliased reference checks" "$(echo "$mmo_" | sed -n 's/.*alias before-lo \([0-9]*\) at-lo \([0-9]*\) overlapping \([0-9]*\),.*/\1 \2 \3/p' | awk '{print ($1<$2?($1<$3?$1:$3):($2<$3?$2:$3))}')" "$FLOOR_MM_ALIAS"
        mmchk_ "NULL subject checks" "$(echo "$mmo_" | sed -n 's/.*s NULL \([0-9]*\).*/\1/p')" "$FLOOR_MM_SNULL"
        mmchk_ "NULL reference checks" "$(echo "$mmo_" | sed -n 's/.*ref NULL \([0-9]*\)$/\1/p')" "$FLOOR_MM_RNULL"
    else
        note_fail 1 "$cc: no 'G2 mismatch operands' census line in $log"
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
    for k in 1 2 3 4 5 6 7; do w1_launch "$wcc" "$k"; done
    w3_launch "$wcc"
fi
for k in 1 2 3 4 5 6 7; do w1_judge "$k"; done
w3_judge
for m in 1 2 3 4 5 6 7 8 9 10 11; do
    [ "$quick" = 1 ] || w2_launch "$m" "$wcc"
    w2_judge "$m"
done

# --- 4b. --rows: the per-ROW floor, from the kit's own REACH trace ----------
# Sources: the `MFTRACE REACH table=T row=R chosen=N` lines of every G2
# process that SELECTS rows (the generator, once per W2 mutation; K1 calls
# only mf_ref_*, selects nothing and prints no REACH line, so it is not one),
# linked against libpcrec_mftrace.a. Nothing here reads G2's generator or
# driver output, and FLOOR_ROWS below is a literal measured once.
MM_ROW_FLOORS="arms:generic:600 arms:mismatch_inplace:300"   # (f): the MISMATCH-only process, measured less ~10%
FLOOR_ROWS=15   # distinct (table,row) pairs in the registry (lane g2m4: 14, with arms/pf_memchr_back; lane g2m7: 15, with arms/mismatch_inplace)
reach_pass() { echo "PASS: $1"; passed=$((passed + 1)); }
reach_fail() { echo "FAIL: $1"; note_fail 1 "rows: $1"; }
# reach_lines FILE: the chosen-lines of one process
reach_lines() { grep -E '^MFTRACE REACH table=[^ ]+ row=[^ ]+ chosen=[0-9]+$' "$1"; }
# (d) as a function: reach_has_lines FILE -> 0 when the process printed any
reach_has_lines() { [ -n "$(reach_lines "$1" | head -1)" ]; }
# rows_zero FILE: the rows of a row-chosen file with n == 0
rows_zero() { awk '$4 == 0 {printf "%s/%s ", $2, $3}' "$1"; }
if [ "$rows" = 1 ]; then
    echo "== rows: kit selection-table rows chosen over the whole tier (MFTRACE REACH, summed)"
    nproc_files=0; noreach=""
    for f in "$work"/reach/*.err; do
        nproc_files=$((nproc_files + 1))
        reach_has_lines "$f" || noreach="$noreach $(basename "$f")"
    done
    if [ -z "$noreach" ] && [ "$nproc_files" -gt 0 ]; then
        reach_pass "(d) all $nproc_files G2 kit processes printed REACH lines"
    else
        reach_fail "(d) G2 kit process(es) printed no REACH line (wrong library linked?):${noreach:- none found at all}"
    fi
    # control: the generator linked against the PLAIN library must
    # trip the same (d) test
    ctl="$work/reach-control"; mkdir -p "$ctl"
    if "$TO" 300 "$gencc" -std=gnu11 -O1 -I "$inc" "$g2/g2_gen.c" "$plainlib" -o "$ctl/gen_plain_lib" \
       && mkdir -p "$ctl/out" && "$TO" 600 "$ctl/gen_plain_lib" "$ctl/out" --seed "$seed" > /dev/null 2> "$ctl/out.err"; then
        if reach_has_lines "$ctl/out.err"; then
            reach_fail "(d) control: a generator linked against the plain library printed REACH lines (the test cannot tell)"
        else
            reach_pass "(d) control: a generator linked against the plain library printed no REACH line, so (d) is red for it"
        fi
    else
        reach_fail "(d) control program did not build or run ($ctl)"
    fi
    for f in "$work"/reach/*.err; do reach_lines "$f"; done \
      | sed 's/^MFTRACE REACH table=\([^ ]*\) row=\([^ ]*\) chosen=\([0-9]*\)$/\1 \2 \3/' \
      | awk '{ k = $1 " " $2; s[k] += $3 } END { for (k in s) print "row-chosen " k " " s[k] }' \
      | LC_ALL=C sort > "$work/row-chosen.txt"
    cat "$work/row-chosen.txt"
    # lane g2m7: the rows the MISMATCH-only generator process chose (its own REACH lines), apart from the tier sum
    echo "== rows chosen by the MISMATCH-only generator process (MISMATCH sites alone)"
    reach_lines "$work/reach/gen-mmonly.err" | sed 's/^MFTRACE REACH table=\([^ ]*\) row=\([^ ]*\) chosen=\([0-9]*\)$/\1 \2 \3/' \
        | awk '$3 > 0 {print "row-chosen-mismatch-only " $1 " " $2 " " $3}' | LC_ALL=C sort | tee "$work/row-chosen-mm.txt"
    for fl_ in $MM_ROW_FLOORS; do
        t_=${fl_%%:*}; r_=${fl_#*:}; r_=${r_%%:*}; v_=${fl_##*:}
        c_=$(awk -v t="$t_" -v r="$r_" '$2 == t && $3 == r {print $4}' "$work/row-chosen-mm.txt")
        if [ "${c_:-0}" -ge "$v_" ]; then reach_pass "(f) MISMATCH sites chose $t_/$r_ ${c_:-0} times >= floor $v_"
        else reach_fail "(f) MISMATCH sites chose $t_/$r_ ${c_:-0} times < floor $v_"; fi
    done
    dropped=$(cat "$work"/reach/*.err | sed -n 's/^MFTRACE REACH_DROPPED n=\([0-9]*\)$/\1/p' | awk '{t += $1} END {print t + 0}')
    ndrop=$(cat "$work"/reach/*.err | grep -c '^MFTRACE REACH_DROPPED n=')
    if [ "$dropped" = 0 ] && [ "$ndrop" -ge "$nproc_files" ]; then
        reach_pass "(a) every REACH_DROPPED is 0 ($ndrop lines)"
    else
        reach_fail "(a) REACH_DROPPED total $dropped over $ndrop lines ($nproc_files processes)"
    fi
    zero=$(rows_zero "$work/row-chosen.txt")
    if [ -z "$zero" ]; then
        reach_pass "(b) every row chosen >= 1 over the tier"
    else
        reach_fail "(b) rows never chosen: $zero"
    fi
    # control: a row-chosen file with one row zeroed must make (b) red
    awk 'NR == 1 {$4 = 0} {print}' "$work/row-chosen.txt" > "$work/row-chosen.ctl"
    if [ -n "$(rows_zero "$work/row-chosen.ctl")" ]; then
        reach_pass "(b) control: a file with row $(rows_zero "$work/row-chosen.ctl")zeroed is red for (b)"
    else
        reach_fail "(b) control: a zeroed row was not named"
    fi
    nrows=$(wc -l < "$work/row-chosen.txt" | tr -d ' ')
    if [ "$nrows" -ge "$FLOOR_ROWS" ]; then
        reach_pass "(c) $nrows distinct (table,row) pairs >= floor $FLOOR_ROWS"
    else
        reach_fail "(c) $nrows distinct (table,row) pairs < floor $FLOOR_ROWS"
    fi
    # (e) the per-row floors, when the caller names a floor file (make passes
    # tests/memfn/row_floors.tsv: columns table, row, pcrec_floor, g2_floor;
    # PLACEHOLDER/`-` cells are skipped). Added by the kit manager at the
    # merge ([MEMFN-ROWCON] N4 follow-up); the floors are data, measured on
    # this tier, so this reads no source the generator shares.
    if [ -n "${G2_ROW_FLOORS:-}" ]; then
        if [ ! -f "$G2_ROW_FLOORS" ]; then
            reach_fail "(e) G2_ROW_FLOORS=$G2_ROW_FLOORS is not a file"
        else
            efail=$(awk -F'\t' 'NR == FNR { if ($1 == "row-chosen") n[$2 "/" $3] = $4; next }
                     /^#/ || NF < 4 || $4 !~ /^[0-9]+$/ { next }
                     { k = $1 "/" $2; seen++; if (!(k in n) || n[k] + 0 < $4 + 0) printf "%s(%s<%s) ", k, (k in n) ? n[k] : "absent", $4 }
                     END { if (!seen) printf "no-numeric-g2-floor " }' \
                 <(tr ' ' '\t' < "$work/row-chosen.txt") "$G2_ROW_FLOORS")
            if [ -z "$efail" ]; then
                reach_pass "(e) every row meets its g2_floor in $G2_ROW_FLOORS"
            else
                reach_fail "(e) rows under their g2_floor: $efail"
            fi
        fi
    fi
fi

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
cls_floor loop-exit "$FLOOR_CLS_LOOPX"
echo "checks passed: $passed"
echo "checks failed: $failed"
if [ "$failed" -gt 0 ]; then
    echo "failures:$fail_notes"
    [ "$keep" = 1 ] || echo "(re-run with --keep to keep $work)"
    exit 1
fi
exit 0
