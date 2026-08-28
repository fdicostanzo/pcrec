#!/usr/bin/env bash
# tests/codegen/run_form_census.sh — [CHK-2] piece 3: THE FORM CENSUS.
#
# Compiles every `.rxt` corpus pattern (default/auto engine, AND
# `--engine=vm` forced where accepted — the WIDER population for the
# VM-only stamps, since auto only routes ~54% of the corpus to the VM) and
# COUNTS artifacts per STAMP VALUE for every stamp docs/spec/match_api.md
# §6.3 documents, plus the joint distributions §6.3 singles out:
# (RX_DFA_SCAN, RX_DFA_PREFILTER, RX_DFA_TABLE) and (RX_ENGINE,
# RX_VM_PREFILTER). K35's rule applies here exactly as it does to a
# structural check's population: a FLOOR for every value the corpus
# actually reaches (rounded down generously, so a later change can only
# cross it LOUDLY), and a REQUIRED NAMED SYNTHETIC WITNESS — built and
# asserted right here, printed as `synthetic-only` — for every value in
# the spec's own value set that the corpus alone never reaches. A value
# neither population produces is RED: "a form nobody can reach."
#
# WHY THIS IS A SEPARATE SCRIPT FROM run_dfa_stamps.sh, WHICH ALREADY
# COUNTS TWO OF THESE STAMPS (docs/spec/tuning.md §3's 2026-08-25 numbers
# come from it): that script's populations are a BY-PRODUCT of a
# STRUCTURAL check (stamp agrees with the emitted loop it names) and it
# does not print floors, does not cover RX_DFA_TABLE/RX_VM_PREFILTER/the
# RUNGS-STRATS-PRUNES bitmasks/RX_ALTCLS_*, and does not build the
# `--engine=vm`-forced population at all. This script's job is narrower and
# different in kind: not "does the stamp match the mechanism" (that check
# already exists and stays where it is) but "has every value in the spec's
# own vocabulary been produced by SOMETHING in this tree, and how often" —
# the K39/[OPT-4] style of printing populations beside a verdict, applied
# to the stamp vocabulary itself. Reuses `pcrec_run` (D45's bounded
# compiler) and the sharded-worker/tally-token shape run_dfa_stamps.sh
# established (`split -n l/N`, one verdict-token stream per shard, the
# parent tallies — never a shared counter across processes); does not
# reuse that script's `read_artifact`/`mirror_check` functions, which are
# STRUCTURAL-comparison machinery this script has no use for.
#
# THE DETECT DEMONSTRATION (docs/dev/learnings.md §3). Performed once,
# 2026-08-26, in a SCRATCH copy under the session scratchpad (never this
# worktree's own `src/`): `dfa_table_name` (src/gen/emit_dfa.c:2288-2296)
# returns `"mixed"` when the forward and reverse machines took different
# table forms. Changed the final `return "mixed";` to
# `return f ? "premultiplied" : "indexed";` (collapse "mixed" into whatever
# the FORWARD machine chose) in the scratch copy, rebuilt `build/pcrec`,
# and ran this script's FULL synthetic-witness section against the
# sabotaged binary (`PCREC=<sabotaged binary> bash
# tests/codegen/run_form_census.sh`, full corpus, so the "mixed" witness
# ran alongside the (unaffected) "indexed" one and the rest of the census):
#
#     census: SYNTHETIC WITNESS '[01]*1[01]{13}' (flags: none) for RX_DFA_TABLE "mixed"...
#     FAIL: census: synthetic witness '[01]*1[01]{13}' (flags: none) was
#       built to prove RX_DFA_TABLE "mixed" is reachable, but the artifact
#       stamps RX_DFA_TABLE "indexed" instead — "mixed" is a form nobody
#       can reach on this tree
#     census: SYNTHETIC WITNESS '(?:[a-z]+)@(?:[a-z]+)' (flags: -fno-premul-table) for RX_DFA_TABLE "indexed"...
#       synthetic-only: RX_DFA_TABLE "indexed" <- '(?:[a-z]+)@(?:[a-z]+)' (flags: -fno-premul-table)
#     FAIL: census: 'D:RX_DFA_TABLE=mixed' has ZERO population (corpus AND
#       no synthetic witness) — a form nobody can reach, or the spec lists
#       a value nothing produces any more
#     checks passed: 0
#
# ("indexed" rather than "premultiplied" because the k=13 witness's FORWARD
# machine is the one that exceeds the 65,535-entry bound, so `f` is false in
# the sabotaged branch — the sabotage still fires, on the value it was
# built to fire on, just not the value a first guess at the branch's
# arithmetic would name; recorded exactly as measured, not as first
# predicted.) Named the exact value ("mixed") and the exact witness pattern
# whose whole reason for existing is producing it, TWICE — once from the
# witness's own local check, once from the completeness loop that would
# have caught it even if the witness function's own assertion had a bug.
# The scratch tree was deleted
# immediately after (never built inside this worktree, never committed).
#
# Usage: bash tests/codegen/run_form_census.sh
# Env: PCREC, CC (unused directly — compile-only, no gcc, like
#      run_dfa_stamps.sh's own corpus sweep), PROCS (shard count, default
#      nproc), KEEP=1 to keep the work directory.

set -u
export LC_ALL=C   # K35

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="form_census"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

if [ ! -x "$PCREC" ]; then
    echo "run_form_census.sh: $PCREC not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-formcensus.XXXXXX")"
cleanup() { [ "$KEEP" = "1" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

fail=0
bad() { echo "FAIL: census: $1" >&2; fail=1; }

t_start=$(date +%s)

# ---------------------------------------------------------------------------
# §1 THE CORPUS POPULATION (K35: LC_ALL=C, never the ambient locale)
# ---------------------------------------------------------------------------
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
# Same shape as run_dfa_stamps.sh's own floor: ~95% of what this tree
# measures at delivery (2,772, 2026-08-25/26) — a shrink below it is a
# population change to investigate, not silently re-pin.
if [ "$npat" -lt 2620 ]; then
    bad "corpus extraction found only $npat patterns, below the 2620 floor (K35 — a locale regression or a real shrink)"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
echo "census: $npat corpus patterns (LC_ALL=C sort -u over tests/**/*.rxt)"

# ---------------------------------------------------------------------------
# §2 THE SHARDED SWEEP — every pattern, DEFAULT engine AND --engine=vm
# ---------------------------------------------------------------------------
NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh" "$WORKDIR/tally"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

cat > "$WORKDIR/worker.sh" <<'WORKER'
#!/usr/bin/env bash
# One shard. Reads patterns on stdin, writes tally TOKENS to stdout — one
# per fact observed, `sort | uniq -c` on the merged stream is the whole
# reduction (no shared counter across processes, run_dfa_stamps.sh's own
# discipline).
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD_WORKER pcrec_run"; exit 1; }
art="$WORKDIR/a.$$.c"
trap 'rm -f "$art"' EXIT

# stamp <artifact-file> <name> -> prints the #define's string/hex value, or
# nothing if absent. String stamps come back WITHOUT quotes; hex stamps
# (the three OR-masks) come back as the raw 0x... token.
stamp() {
    sed -n "s/^#define $2 \"\\([^\"]*\\)\"\$/\\1/p; s/^#define $2 \\(0x[0-9a-fA-F]*u\\{0,1\\}\\)\$/\\1/p; s/^#define $2 \\([0-9][0-9]*\\)\$/\\1/p" "$1" | head -1
}

while IFS= read -r pat; do
    # ---- DEFAULT (auto) engine ------------------------------------------
    if pcrec_run "$PCREC" --features all -p rx -o "$art" -- "$pat" >/dev/null 2>&1; then
        eng="$(stamp "$art" RX_ENGINE)"
        [ -n "$eng" ] && echo "D:RX_ENGINE=$eng"
        scan="$(stamp "$art" RX_DFA_SCAN)"
        pf="$(stamp "$art" RX_DFA_PREFILTER)"
        tbl="$(stamp "$art" RX_DFA_TABLE)"
        [ -n "$scan" ] && echo "D:RX_DFA_SCAN=$scan"
        [ -n "$pf" ] && echo "D:RX_DFA_PREFILTER=$pf"
        [ -n "$tbl" ] && echo "D:RX_DFA_TABLE=$tbl"
        if [ -n "$scan" ] && [ -n "$pf" ] && [ -n "$tbl" ]; then
            echo "D:TRIPLE=$scan,$pf,$tbl"
        fi
        vmpf="$(stamp "$art" RX_VM_PREFILTER)"
        [ -n "$vmpf" ] && echo "D:RX_VM_PREFILTER=$vmpf"
        [ -n "$eng" ] && [ -n "$vmpf" ] && echo "D:PAIR=$eng,$vmpf"
        [ -n "$eng" ] && [ -z "$vmpf" ] && echo "D:PAIR=$eng,-"
        ceil="$(stamp "$art" RX_VM_PRUNE_CEILING)"
        [ -n "$ceil" ] && echo "D:RX_VM_PRUNE_CEILING=$ceil"
        rungs="$(stamp "$art" RX_VM_RUNGS)"
        strats="$(stamp "$art" RX_VM_STRATS)"
        prunes="$(stamp "$art" RX_VM_PRUNES)"
        if [ -n "$rungs" ]; then
            v=$(( ${rungs%u} ))
            for b in 0 1 2 3 4; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "D:RX_VM_RUNGS_BIT$b=set"; else echo "D:RX_VM_RUNGS_BIT$b=clear"; fi
            done
        fi
        if [ -n "$strats" ]; then
            v=$(( ${strats%u} ))
            for b in 0 1; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "D:RX_VM_STRATS_BIT$b=set"; else echo "D:RX_VM_STRATS_BIT$b=clear"; fi
            done
        fi
        if [ -n "$prunes" ]; then
            v=$(( ${prunes%u} ))
            for b in 0 1; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "D:RX_VM_PRUNES_BIT$b=set"; else echo "D:RX_VM_PRUNES_BIT$b=clear"; fi
            done
        fi
        am="$(stamp "$art" RX_ALTCLS_MERGES)"
        af="$(stamp "$art" RX_ALTCLS_FACTORED)"
        [ -n "$am" ] && echo "D:RX_ALTCLS_MERGES=$([ "$am" -gt 0 ] && echo '>0' || echo '0')"
        [ -n "$af" ] && echo "D:RX_ALTCLS_FACTORED=$([ "$af" -gt 0 ] && echo '>0' || echo '0')"
    else
        echo "D:REFUSED=1"
    fi

    # ---- FORCED --engine=vm, the WIDER population for VM-only stamps ---
    if pcrec_run "$PCREC" --features all --engine=vm -p rx -o "$art" -- "$pat" >/dev/null 2>&1; then
        vmpf="$(stamp "$art" RX_VM_PREFILTER)"
        [ -n "$vmpf" ] && echo "V:RX_VM_PREFILTER=$vmpf"
        ceil="$(stamp "$art" RX_VM_PRUNE_CEILING)"
        [ -n "$ceil" ] && echo "V:RX_VM_PRUNE_CEILING=$ceil"
        rungs="$(stamp "$art" RX_VM_RUNGS)"
        strats="$(stamp "$art" RX_VM_STRATS)"
        prunes="$(stamp "$art" RX_VM_PRUNES)"
        if [ -n "$rungs" ]; then
            v=$(( ${rungs%u} ))
            for b in 0 1 2 3 4; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "V:RX_VM_RUNGS_BIT$b=set"; else echo "V:RX_VM_RUNGS_BIT$b=clear"; fi
            done
        fi
        if [ -n "$strats" ]; then
            v=$(( ${strats%u} ))
            for b in 0 1; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "V:RX_VM_STRATS_BIT$b=set"; else echo "V:RX_VM_STRATS_BIT$b=clear"; fi
            done
        fi
        if [ -n "$prunes" ]; then
            v=$(( ${prunes%u} ))
            for b in 0 1; do
                if [ $(( (v >> b) & 1 )) -eq 1 ]; then echo "V:RX_VM_PRUNES_BIT$b=set"; else echo "V:RX_VM_PRUNES_BIT$b=clear"; fi
            done
        fi
    else
        echo "V:REFUSED=1"
    fi
done
WORKER

export ROOT_DIR WORKDIR PCREC
running=0
for f in "$WORKDIR"/sh/p*; do
    [ -f "$f" ] || continue
    bash "$WORKDIR/worker.sh" < "$f" > "$WORKDIR/tally/$(basename "$f").out" 2>"$WORKDIR/tally/$(basename "$f").err" &
    running=$((running + 1))
    if [ "$running" -ge "$NSHARD" ]; then wait -n || true; running=$((running - 1)); fi
done
wait

for f in "$WORKDIR"/tally/*.err; do
    [ -s "$f" ] && cat "$f" >&2
done
cat "$WORKDIR"/tally/*.out > "$WORKDIR/tally_all"
if grep -q '^BAD_WORKER' "$WORKDIR/tally_all"; then
    bad "a worker could not load pcrec_run — extraction is broken, not merely a compile failure"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi

t_sweep=$(date +%s)
LC_ALL=C sort "$WORKDIR/tally_all" | LC_ALL=C uniq -c | LC_ALL=C sort -rn > "$WORKDIR/counts"

echo
echo "== census: corpus sweep ($((t_sweep - t_start))s, $npat patterns x 2 engine requests) =="
column -t "$WORKDIR/counts" 2>/dev/null || cat "$WORKDIR/counts"

# ---------------------------------------------------------------------------
# §3 FLOORS — every value WITH corpus witnesses gets one, generous (K35: a
# floor a later change can only cross LOUDLY, never an exact count).
# ---------------------------------------------------------------------------
count_of() {   # count_of <exact tally token>
    awk -v t="$2" '$2==t{print $1; found=1} END{if(!found) print 0}' "$WORKDIR/counts" \
        | awk '{s+=$1} END{print s+0}'
}
floor_check() {   # floor_check <token> <floor>
    local tok="$1" floor="$2" n
    n="$(count_of x "$tok")"
    if [ "$n" -lt "$floor" ]; then
        bad "population floor crossed: '$tok' has $n witnesses, floor is $floor"
    else
        echo "  floor OK: $tok = $n (floor $floor)"
    fi
}

echo
echo "== census: floors (every value the corpus reaches) =="
# Selection facts (a) — present on every DFA-containing artifact.
floor_check "D:RX_ENGINE=dfa"                 400
floor_check "D:RX_ENGINE=vm"                  1000
floor_check "D:RX_DFA_SCAN=unanchored"        1400
floor_check "D:RX_DFA_SCAN=attempt"           250
floor_check "D:RX_DFA_PREFILTER=none"         500
# [OPT-K] (2026-08-28, abi 9) put two candidates at the HEAD of the prefilter
# list, so ~75 memchr witnesses and some byte-class ones became offset-set
# forms: memchr measured 900+ → 825 on the union sweep (floor re-derived,
# rounded down), offset-set 360, offset-set-bounded 40 (floored on first
# sight — K35: every value the corpus reaches gets a floor in the same change).
floor_check "D:RX_DFA_PREFILTER=memchr"       750
floor_check "D:RX_DFA_PREFILTER=byte-class"   250
floor_check "D:RX_DFA_PREFILTER=offset-set"   300
floor_check "D:RX_DFA_PREFILTER=offset-set-bounded" 30
floor_check "D:RX_DFA_TABLE=premultiplied"    1500
# Capacity/activity (b) — VM artifacts, DEFAULT population.
floor_check "D:RX_VM_PREFILTER=hybrid"        900
floor_check "D:RX_VM_PREFILTER=none"          150
floor_check "D:RX_VM_PRUNE_CEILING=prefilter-window" 100
# "none" is a THIRD value this census measured live (§6.3 does not give
# RX_VM_PRUNE_CEILING a value-set TABLE the way it does RX_DFA_PREFILTER, so
# it is floored here as an observed fact rather than asserted complete
# against a documented set) — the reading is "no MRL clamp applied at all"
# (RX_VM_PRUNES both bits clear), distinct from either ceiling arithmetic.
floor_check "D:RX_VM_PRUNE_CEILING=none"      500
# The WIDER --engine=vm-forced population.
floor_check "V:RX_VM_PREFILTER=none"          2000
floor_check "V:RX_VM_PRUNE_CEILING=subject-end" 100

# ---------------------------------------------------------------------------
# §4 SYNTHETIC WITNESSES — required for every §6.3 value with ZERO corpus
# population. Two turned up MEASURED (not assumed) this session:
#
#   - "mixed" (tuning.md §2.13's own documented likely-first case): the
#     corpus's largest machine is 40,010 entries, strictly inside the
#     65,535-entry bound both machines must separately clear for "mixed"
#     (forward/reverse disagreeing) to appear, so the corpus alone never
#     produces it.
#   - "indexed": every DFA-containing corpus artifact is small enough that
#     the pre-multiplied form ALWAYS wins by default ([OPT-3] ships it ON),
#     so plain "indexed" turned up as a SECOND zero-population value the
#     first run of this script found — not documented as a likely gap
#     anywhere, which is exactly why the completeness loop below exists
#     rather than a hand-picked list of "the ones we expect to be empty".
#     `-fno-premul-table` (§2.13's own deny flag) is the direct witness: it
#     forces the indexed form on ANY DFA-containing pattern.
#
# declare -A SYN_OK tracks which values a synthetic witness actually
# produced, so the completeness loop below never needs a hand-maintained
# exclusion list — a value is clean if EITHER the corpus floor above fired
# OR its own synthetic witness (right here) confirmed the stamp.
# ---------------------------------------------------------------------------
echo
echo "== census: synthetic witnesses (zero corpus population; asserted here) =="
declare -A SYN_OK=()

synthetic_table_witness() {   # synthetic_table_witness <pattern> <extra-flags> <want-value>
    local pat="$1" flags="$2" want="$3"
    local tok="D:RX_DFA_TABLE=$want"
    local seen; seen="$(count_of x "$tok")"
    if [ "$seen" -gt 0 ]; then
        echo "  $tok now has $seen CORPUS witnesses — the synthetic below is redundant but still asserted (never silently dropped)"
    fi
    echo "census: SYNTHETIC WITNESS '$pat' (flags: ${flags:-none}) for RX_DFA_TABLE \"$want\"..."
    local wart="$WORKDIR/witness_$want.c"
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" -p rx --no-captures $flags -o "$wart" -- "$pat" >/dev/null 2>&1; then
        bad "synthetic witness '$pat' (flags: ${flags:-none}) failed to compile at all — the witness itself is broken, not merely unreachable"
        return
    fi
    local wv; wv="$(sed -n 's/^#define RX_DFA_TABLE "\([^"]*\)"$/\1/p' "$wart")"
    if [ "$wv" = "$want" ]; then
        SYN_OK["$tok"]=1
        echo "  synthetic-only: RX_DFA_TABLE \"$want\" <- '$pat' (flags: ${flags:-none})"
    else
        bad "synthetic witness '$pat' (flags: ${flags:-none}) was built to prove RX_DFA_TABLE \"$want\" is reachable, but the artifact stamps RX_DFA_TABLE \"$wv\" instead — \"$want\" is a form nobody can reach on this tree"
    fi
}

synthetic_table_witness '[01]*1[01]{13}' '' 'mixed'
synthetic_table_witness '(?:[a-z]+)@(?:[a-z]+)' '-fno-premul-table' 'indexed'

# Every OTHER §6.3 value is asserted to have EITHER a corpus floor above OR
# a synthetic witness — checked here so a value dropped from BOTH lists
# above is caught by name rather than by silent omission.
declare -A KNOWN_VALUES=(
    ["D:RX_ENGINE=vm"]=1 ["D:RX_ENGINE=dfa"]=1
    ["D:RX_DFA_SCAN=unanchored"]=1 ["D:RX_DFA_SCAN=attempt"]=1 ["D:RX_DFA_SCAN=empty"]=1
    ["D:RX_DFA_PREFILTER=none"]=1 ["D:RX_DFA_PREFILTER=memchr"]=1
    ["D:RX_DFA_PREFILTER=byte-class"]=1 ["D:RX_DFA_PREFILTER=memchr-bounded"]=1
    ["D:RX_DFA_PREFILTER=byte-class-bounded"]=1
    ["D:RX_DFA_PREFILTER=offset-set"]=1 ["D:RX_DFA_PREFILTER=offset-set-bounded"]=1
    ["D:RX_DFA_TABLE=premultiplied"]=1 ["D:RX_DFA_TABLE=indexed"]=1
    ["D:RX_DFA_TABLE=mixed"]=1 ["D:RX_DFA_TABLE=none"]=1
    ["D:RX_VM_PREFILTER=hybrid"]=1 ["D:RX_VM_PREFILTER=none"]=1
)
for tok in "${!KNOWN_VALUES[@]}"; do
    n="$(count_of x "$tok")"
    if [ "$n" -eq 0 ] && [ -z "${SYN_OK[$tok]:-}" ]; then
        bad "'$tok' has ZERO population (corpus AND no synthetic witness) — a form nobody can reach, or the spec lists a value nothing produces any more"
    fi
done

# ---------------------------------------------------------------------------
# §5 THE JOINT DISTRIBUTIONS (§6.3's own two)
# ---------------------------------------------------------------------------
echo
echo "== census: (RX_DFA_SCAN, RX_DFA_PREFILTER, RX_DFA_TABLE) triples =="
grep '^D:TRIPLE=' "$WORKDIR/tally_all" | LC_ALL=C sort | LC_ALL=C uniq -c | LC_ALL=C sort -rn
echo
echo "== census: (RX_ENGINE, RX_VM_PREFILTER) pairs =="
grep '^D:PAIR=' "$WORKDIR/tally_all" | LC_ALL=C sort | LC_ALL=C uniq -c | LC_ALL=C sort -rn

# ---------------------------------------------------------------------------
t_end=$(date +%s)
echo
echo "checks passed: $([ "$fail" -eq 0 ] && echo 1 || echo 0)"
echo "checks failed: $([ "$fail" -eq 0 ] && echo 0 || echo 1)"
echo "census total wall time: $((t_end - t_start))s"
[ "$fail" -eq 0 ] || exit 1
exit 0
