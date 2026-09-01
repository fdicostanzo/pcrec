#!/usr/bin/env bash
# tests/resource/run_resource_tests.sh — [M4.7b] the K7 pin.
#
# WHY THIS FILE EXISTS AND IS NOT A .rxt. K7's own entry said so before the fix
# did: "a SIGKILL is not a `perr` (the harness correctly treats rc >= 124 as a
# crash, not a rejection), so pinning it needs a purpose-built check." Every
# other suite here asserts something about what a pattern MATCHES or what
# diagnostic it draws. This one asserts something about what compiling it
# COSTS, which no .rxt block can express: the `perr` expectation a repro shape
# needs is indistinguishable, to the harness, from the crash it used to
# produce. So the assertions below are on the process, not on the language.
#
# WHAT K7 WAS. A large bounded repeat (`a{0,65535}`, `a{0,40000}`) exhausted
# memory and the process was SIGKILLed, instead of reaching the DFA state cap
# that exists to prevent exactly this — and under a caller-set address-space
# limit, pcrec_compile ABORTED THE CALLER'S PROCESS with no diagnostic at all,
# which for a library is the worst outcome on the list. Measured before the
# fix, on this box: `a{0,16000}` cost 2.7 GB, `a{0,20000}` cost 4.7 GB, and
# `a{0,25000}` upward died one way or the other.
#
# WHAT THE FIX WAS, in one line each, because these assertions are only
# meaningful against it:
#   1. PCREC_MAX_SUBSET_ELEMS (src/core/limits.h) bounds the subset
#      construction's own dominant memory term — the total number of NFA-state
#      list ELEMENTS interned — which the pre-existing state-COUNT cap does
#      not, because `a{0,N}` builds Theta(N) states whose lists are each
#      Theta(N) long. Charged in src/ir/dfa.c's intern(), so the refusal
#      happens DURING construction rather than after it.
#   2. Every allocation on the compile path reports through ctx_nomem()
#      instead of abort() (src/core/{arena,sb,compile}.c, src/ir/{nfa,dfa}.c,
#      src/opt/minimize.c), so a malloc that fails under a caller's limit is a
#      diagnosed refusal and not a dead caller process.
#
# THE TWO SECTIONS BELOW TEST THOSE TWO THINGS SEPARATELY, and they have to be
# separate: with the budget in place, section 1's shapes are refused by the
# BUDGET long before any malloc fails, so section 1 cannot exercise the
# allocator paths at all. Section 2 forces a real allocation failure with an
# address-space limit far below what a legitimate pattern needs, which is the
# only way to reach that code — and is a positive control for it, not just a
# repro: if ctx_nomem were reverted to abort(), section 2 fails and section 1
# does not notice.
#
# Usage: bash tests/resource/run_resource_tests.sh
# Env:   PCREC (default <root>/build/pcrec)
#        K7_MEM   peak-tree-RSS ceiling per compile (default 512m)
#        K7_SECS  wall budget per compile (default 120)
#        K7_CPU   CPU budget per compile (default 45)
#        LOAD_GUARD_RATIO  [TT-10] 1-min-load/nproc threshold above which a
#                  123/124 kill is reported INCONCLUSIVE instead of FAIL
#                  (default 2.0; tests/lib/load_guard.sh has the measurement)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

# [TT-10] tests/lib/load_guard.sh — see its own header for the measurement
# and threshold. Section 1's watchdog CPU/wall kills (123/124) are the two
# outcomes a contended box can produce for a reason unrelated to the
# compiler; every other outcome (0, 1, 122, 134, 137) is unaffected by load
# and stays a real PASS/FAIL exactly as before.
. "$ROOT_DIR/tests/lib/timeout_bin.sh"   # [TT-6]/[K37] $TIMEOUT_BIN for the exec'd bound below
. "$ROOT_DIR/tests/lib/load_guard.sh"

# The ceiling. 512m matches tests/lib/gen_timeout.sh's GENRUNMEM default, and
# is chosen the same way: three-and-change times the worst LEGITIMATE cost, so
# a breach is a runaway rather than a busy box. Post-fix, the most expensive
# case below peaks at roughly 150 MB (the budget's own ceiling — see
# PCREC_MAX_SUBSET_ELEMS for the measured bytes-per-element that sets it), and
# every case that COMPILES peaks far under that. Pre-fix, four of these cases
# exceeded 2 GB and three could not finish at all.
#
# Same revisit-when as D45's budgets: if a legitimate case is MEASURED needing
# more, raise the default with the measurement recorded, never silently.
K7_MEM="${K7_MEM:-512m}"
K7_SECS="${K7_SECS:-120}"
# THE CPU BUDGET IS SET BY A COST THIS LANE DID NOT FIX, and saying which one
# is the difference between a budget and a fudge factor. `a{0,25000}` spends a
# MEASURED 15.3 s of its 15.4 s inside pcrec_minimize_dfa — 7.50 s on the
# forward machine and 7.76 s on the reverse — against 0.03 s for parse, NFA
# construction and BOTH subset constructions combined. That is Moore partition
# refinement needing O(n) rounds on an n-state chain, an optimization pass
# untouched by [M4.7b], not the resource accounting K7 is about; it has bounded
# memory and always terminates, and it is filed separately.
#
# 45 s is ~3x the measured 15.4 s, which is the headroom D45's own calibration
# note says a CPU budget needs: CPU is load-RESILIENT but not load-independent,
# and that file records a measured >2x inflation under a real `make -j12` mix.
# WHEN THE MINIMIZATION COST IS FIXED THIS SHOULD COME BACK DOWN to ~10 s,
# which is what the construction side alone would need.
K7_CPU="${K7_CPU:-45}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
export WATCHDOG_SECTION="resource"

pass=0; fail=0; inconc=0
ok()   { echo "PASS: $*"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $*"; fail=$((fail + 1)); }
# [TT-10] a THIRD outcome, counted and printed separately — never folded
# into pass (that would misreport an unreliable reading as validated) or
# into fail (that would misreport box contention as a regression).
inc()  { echo "INCONCLUSIVE: $*"; inconc=$((inconc + 1)); }

echo "== [K7] COMPILE-SIDE RESOURCE BOUNDS =="
echo "   ceiling: peak tree RSS $K7_MEM, wall ${K7_SECS}s, CPU ${K7_CPU}s per compile"
echo

# ---------------------------------------------------------------------------
# Section 1 — the K7 repro shapes reach a bounded outcome.
#
# Each shape must end in one of exactly two states: compiled (rc 0), or
# REFUSED with a diagnostic (rc 1). Everything else is the bug: 134 is the
# abort K7's entry calls the worst failure mode, 122 is the memory runaway it
# was filed for, 124/123 the unbounded grind that preceded it, and 137 an
# external OOM kill.
#
# WHICH SHAPES COMPILE AND WHICH REFUSE IS DELIBERATELY NOT ASSERTED HERE.
# That boundary is a function of PCREC_MAX_SUBSET_ELEMS, and pinning it in
# this file would mean re-tuning the budget and this test together — a control
# sharing a source with what it controls, which is the failure mode this
# project has hit most often. What is asserted is the property the budget
# EXISTS to provide and that no tuning may cost: bounded time, bounded memory,
# and a diagnosis either way. Section 3 pins the refusal's WORDING against the
# one shape whose verdict cannot turn on any plausible retuning; where the
# boundary sits for everything else is limits.h's business.
# ---------------------------------------------------------------------------
shapes=(
    'a{0,65535}'      # K7's headline repro — SIGKILL before the fix
    'a{,65535}'       # the `{,m}` spelling of the same (PCRE2 10.43+)
    'a{1,65535}'      # non-zero lower bound, same optional tail
    'a{0,40000}'      # K7's second recorded SIGKILL
    'a{0,25000}'      # the narrowed threshold: SIGABRT under a 6 GB limit
    'a{0,20000}'      # the last form that "worked", at 4.7 GB
    'a{65535}'        # exact count: reached its diagnostic at 2.1 GB / 23.9 s
    'a{20000}'        # exact count, mid-range — compiled, at 845 MB
    '(ab){0,30000}'   # multi-byte body, so the blowup is not a single-atom quirk
    '[a-z]{0,30000}'  # class body
    '(a|b){0,30000}'  # a choice point in the body (the VM's own replication axis)
)

for pat in "${shapes[@]}"; do
    out="$WORKDIR/o.c"
    rm -f "$out"
    log="$("$ROOT_DIR/scripts/watchdog" -l "compile $pat" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -o "$out" "$pat" 2>&1)"   # [K37]: the wrapper (watchdog) IS the bound and execs a BINARY -- the compiler itself, never a bash function -- on ONE line so the check sees both
    rc=$?
    case $rc in
        0) ok "'$pat' compiles within the ceiling" ;;
        1) if printf '%s' "$log" | grep -q 'too complex\|too large\|out of memory'; then
               ok "'$pat' refused cleanly: $(printf '%s' "$log" | head -1)"
           else
               bad "'$pat' exited 1 with an unrecognised diagnostic: $log"
           fi ;;
        122) bad "'$pat' EXCEEDED $K7_MEM of tree RSS — this is K7 itself" ;;
        # [TT-10] 123/124 are the two outcomes docs/testing.md's own
        # measurement (and the K31 addendum) says a contended box can
        # produce for a reason that has nothing to do with the compiler:
        # CPU-TIME ACCOUNTING itself inflates under real contention, not
        # merely wall stretching around fixed work. Check the load AFTER
        # the kill, not before running the shape — a box that was fine at
        # the START of the loop and got contended by the END must not be
        # read as quiet, and checking only on the two outcomes that could
        # plausibly BE a load artifact means every other outcome (0, 1,
        # 122, 134, 137) keeps its full meaning regardless of load.
        123) if load_guard_tripped; then
                 inc "'$pat' EXCEEDED ${K7_CPU}s of CPU, but the box is too contended for that to mean anything (ratio $(load_guard_ratio) > $LOAD_GUARD_RATIO) — solo re-run owed"
             else
                 bad "'$pat' EXCEEDED ${K7_CPU}s of CPU — the cap is not firing early enough"
             fi ;;
        124) if load_guard_tripped; then
                 inc "'$pat' EXCEEDED ${K7_SECS}s of wall time, but the box is too contended for that to mean anything (ratio $(load_guard_ratio) > $LOAD_GUARD_RATIO) — solo re-run owed"
             else
                 bad "'$pat' EXCEEDED ${K7_SECS}s of wall time (stuck, not working)"
             fi ;;
        134) bad "'$pat' ABORTED (rc 134) — a library must not abort its caller" ;;
        137) bad "'$pat' was SIGKILLed (rc 137) — K7's original signature" ;;
        *)   bad "'$pat' exited $rc, which is neither a compile nor a refusal: $log" ;;
    esac
done

echo

# ---------------------------------------------------------------------------
# Section 1b — [ART-SIZE]/D84: the three shapes above whose ACCEPTANCE MOVED.
#
# These COMPILED before the emitted-size caps landed and REFUSE now. That is
# the intended reading of D84 ruling 2 ("a large byte count makes the artifact
# unusable"; Frank: "I'd rather it FAIL and document how to handle oversized
# results") — but an acceptance change has to be RECORDED, not discovered, so
# each shape is pinned here with the size it used to produce. Section 1's loop
# above already accepts a clean 'too large' refusal as a pass; this section is
# what makes these three shapes' refusal EXPECTED rather than merely tolerated,
# and what would fail loudly if a future change silently re-accepted them at a
# megabyte-plus.
#
# All three are TABLE-dominated (their code is tens of KB), so it is the TOTAL
# cap that refuses them and `--unroll` would not shrink them — which is exactly
# what docs/spec/limits.md's "Handling an oversized artifact" tells a user, and
# these are the shapes it is written about.
#
# THE SECOND CELL PER SHAPE IS THE OVERRIDE'S OWN TEST: raising the cap past
# the measured size must re-accept the pattern. That is the only place the
# raise-only override is exercised end to end, and it is the answer to "how do
# I still get this artifact" being a real answer rather than a sentence.
# ---------------------------------------------------------------------------
# [OPT-4] 2026-08-29 — THE THIRD SHAPE KEEPS `-fno-prefilter-collapse`, AND
# UNDER FRANK'S RULING B THE REASON IS BETTER THAN IT WAS. `(a|b){0,30000}`'s
# 1.33 MB is almost entirely its hybrid PREFILTER's tables. Ruling B builds the
# EXACT prefilter at the default, so the total cap REFUSES that artifact as it
# always did — and then the SIZE RUNG retries with the collapsed prefilter and
# ships 32,298 bytes instead. The cap therefore still fires on this shape; what
# changed is that firing is no longer the end of the story.
#
# So this row denies the axis to observe the REFUSAL (the rung is what
# `-fno-prefilter-collapse` turns off, and observing a refusal is the only
# thing that flag still buys a caller), and the row below pins the DEFAULT
# outcome — the rescue — from a run. Together they assert both halves of
# ruling B on one shape: the cap catches the exact artifact, the rung ships a
# smaller one. The other two shapes, whose bulk is the VM body rather than a
# prefilter, have nothing to collapse and refuse at the default untouched,
# which is why they carry no flag.
size_moved=(
    '(?:[a-z][0-9]){0,8000}:1063395:'
    'a{0,25000}:1103670:-fno-scan-edge'
    '(a|b){0,30000}:1333410:-fno-scan-edge -fno-prefilter-collapse -fprefilter'
)
# [OPT-5] 2026-08-31, the rows above REWRITTEN the day the scan edge landed:
# the old natural witnesses (a{0,25000}, [a-z]{0,30000}, (a|b){0,30000}) all
# collapsed to ~18-35 KB artifacts — the CAP still works, the WITNESSES
# stopped reaching it. Row 1 is the new NATURAL witness: (?:[a-z][0-9]) is a
# PERIOD-2 chain the period-1 criterion refuses (scanedge.c precondition 1 —
# advance class alternates), so its tables still emit big; when [OPT-5]
# STEP 2's period-k edge lands, THIS row goes red and moves again — that is
# the tripwire working, not breaking. Rows 2-3 keep the ORIGINAL witnesses
# alive under the deny flag (refusals re-MEASURED 2026-08-31 with the new
# byte figures), so the cap's behavior on the classic shapes stays pinned.
#
# [OPT-4.2] (2026-08-31, lane o42) ROW 3 GAINED `-fprefilter`, AND WITHOUT IT
# THE ROW GOES VACUOUS RATHER THAN WRONG. `(a|b){0,30000}`'s own EXACT
# language is nullable, so [OPT-4.2]'s decline (src/opt/select_engine.c's
# `prefilter_declined_nullable_default`) now fires on the FIRST compile
# attempt, BEFORE the exact prefilter machine is ever built and therefore
# BEFORE `-fno-scan-edge`/`-fno-prefilter-collapse` have anything to act on
# — MEASURED: without `-fprefilter` this row compiles successfully at 20,628
# bytes, no refusal at all, which is CORRECT per [OPT-4.2] and not a defect,
# but leaves this row asserting nothing about the size cap. `-fprefilter`
# is the one flag [OPT-4.1]/[OPT-4.2] both let override the decline (a
# caller who explicitly demands a prefilter gets the exact one, nullable or
# not), which restores the huge exact build this row exists to refuse:
# MEASURED, with all three flags, exit 1 / "pattern too large: 1333410
# bytes" — matching the pinned `1333406` within the caller-args/pattern-text
# rounding this section's own byte figures already carry elsewhere. The
# raise-cap re-accept check below (line ~259) was re-verified with the same
# three flags plus `--max-emit-bytes=9000000`: exit 0 / 1,341,343 bytes.
for entry in "${size_moved[@]}"; do
    # [OPT-5] 2026-08-31: split from the RIGHT — the PATTERN may contain
    # `:` ((?:...) does), the last two fields never do. A left split read
    # '(?:[a-z][0-9]){0,8000}' as pattern '(?' (measured, fix-wave rerun).
    extra="${entry##*:}"; rest="${entry%:*}"
    was="${rest##*:}"; pat="${rest%:*}"
    out="$WORKDIR/o.c"; rm -f "$out"
    # shellcheck disable=SC2086
    log="$("$ROOT_DIR/scripts/watchdog" -l "sizecap $pat" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx $extra -o "$out" "$pat" 2>&1)"
    rc=$?
    if [ "$rc" -eq 1 ] && printf '%s' "$log" | grep -q 'bytes of emitted C source'; then
        ok "'$pat' refused by the total emitted-size cap (was $was bytes before [ART-SIZE]): $(printf '%s' "$log" | head -1 | cut -c1-90)"
    elif [ "$rc" -eq 0 ]; then
        bad "'$pat' was ACCEPTED — it emitted $was bytes before [ART-SIZE] and the total cap is meant to refuse it; if that is intended the pin here moves in the same commit"
    else
        bad "'$pat' exited $rc, expected the size-cap refusal: $log"
    fi

    # the override re-accepts it
    rm -f "$out"
    # shellcheck disable=SC2086
    log="$("$ROOT_DIR/scripts/watchdog" -l "sizecap-raise $pat" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx $extra --max-emit-bytes=9000000 -o "$out" "$pat" 2>&1)"
    rc=$?
    if [ "$rc" -eq 0 ]; then
        ok "'$pat' is re-accepted with --max-emit-bytes raised (the override works end to end)"
    else
        bad "'$pat' still refused with --max-emit-bytes=9000000 (rc $rc): $log"
    fi
done

# [OPT-4] THE THIRD SHAPE'S NEW DEFAULT, PINNED FROM A RUN. Without this the
# only record that `(a|b){0,30000}` stopped being oversize would be the
# `-fno-prefilter-collapse` in its row above, which reads like a detail. It is
# the largest single artifact this row shrinks outside the corpus, and if it
# ever grows back past the cap the loop above would still pass (its own row
# denies the axis) while a user's default build started refusing again.
# ONE LINE, like every other watchdog invocation in this file: [K37]'s check
# is line-based (it looks for the bound on the SAME line as the compiler call),
# so a continuation line carrying `"$PCREC"` alone reads as unbounded. Split
# across lines this cell failed make test-codegen while being perfectly bounded.
#
# [OPT-4.1] THE ROW BECAME A PAIR, AND THE PAIR IS THE POINT. `(a|b){0,30000}`
# is NULLABLE — its collapsed language `(a|b)*` matches the empty string at
# every position, so the collapsed prefilter could never dismiss one — and
# [OPT-4.1] declines it, shipping an artifact with NO prefilter, which is
# SMALLER still and therefore rescues the compile just as the collapse did.
# `(a|b){1,30000}` is the same pattern one character over, is NOT nullable, and
# must still take the size rung and its stamp.
#
# EACH IS THE OTHER'S CONTROL, and neither direction is safe alone. Without the
# non-nullable twin, a compiler that had stopped taking the size rung at all
# would leave the nullable row green (no prefilter is exactly what it asserts)
# while every oversize collapsible pattern started refusing. Without the
# nullable row, a compiler that had stopped declining would leave the twin
# green while shipping the scan pcrec-bench measured at 1.2-9.9x slower than
# none. The `size cap retry` bucket ALSO has no other witness in this tree —
# the corpus reaches neither rung — so the twin is what keeps that stamp value
# reachable at all (K35).
size_rung_cell() {  # size_rung_cell PATTERN want_prefilter(none|hybrid) LABEL [EXTRA-FLAGS]
    local pat="$1" want="$2" label="$3" extra="${4-}"
    rm -f "$WORKDIR/o.c"
    local dflog rc
    # shellcheck disable=SC2086
    dflog="$("$ROOT_DIR/scripts/watchdog" -l "sizecap-default $label" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx $extra -o "$WORKDIR/o.c" "$pat" 2>&1)"
    rc=$?
    if [ "$rc" -ne 0 ]; then
        bad "[OPT-4] '$pat' no longer compiles at the DEFAULT — the size rung has stopped rescuing this shape, or a cap moved: $(printf '%s' "$dflog" | head -1)"
        return
    fi
    local sz pf szwhy sel
    sz=$(wc -c < "$WORKDIR/o.c")
    pf=$(grep -oE '^#define RX_VM_PREFILTER .*' "$WORKDIR/o.c" | head -1 | sed 's/.*PREFILTER //;s/"//g')
    szwhy=$(grep -oE '^#define RX_VM_PREFILTER_LANG_WHY .*' "$WORKDIR/o.c" | sed 's/.*WHY //;s/"//g')
    sel=$(grep -oE '^#define RX_ENGINE_SEL .*' "$WORKDIR/o.c" | sed 's/.*SEL //;s/"//g')
    if [ "$sz" -ge 200000 ]; then
        bad "[OPT-4] '$pat' compiled at the default but emitted $sz bytes, expected well under 200,000 — the size rung is not reaching this shape"
        return
    fi
    if [ "$want" = hybrid ]; then
        # [LIM-1] (D90, 2026-08-30): the expectation moved from reading the
        # _LANG_WHY prefix to reading RX_ENGINE_SEL directly — before this
        # fold-in a successful size-rung rescue stamped ENGINE_SEL "selected",
        # indistinguishable from an ordinary compile that never touched a
        # cap; it now stamps "size-cap-retry", ITS OWN closed-value-set
        # member (match_api.md §6.3), which is what this cell is this
        # constant's ONLY witness in the tree for (see this file's own
        # [LIM-1] note below). LANG_WHY is still read and still reported for
        # its own information (which cap, and the byte comparison), but the
        # PASS/FAIL verdict no longer depends on parsing its prefix.
        if [ "$pf" = hybrid ] && [ "$sel" = size-cap-retry ]; then
            ok "[OPT-4] '$pat' compiles at the DEFAULT in $sz bytes via the SIZE RUNG (RX_ENGINE_SEL '$sel', LANG_WHY '$szwhy') — the cap refused the exact artifact and ruling B's retry shipped a smaller one"
        elif [ "$pf" != hybrid ]; then
            bad "[OPT-4] '$pat' compiled small at the default with RX_VM_PREFILTER '$pf' — its collapsed language is NOT nullable, so the rung must KEEP the prefilter; the [OPT-4.1] decline is over-firing"
        else
            bad "[OPT-4] '$pat' compiled small at the default with RX_VM_PREFILTER hybrid but RX_ENGINE_SEL '$sel' (LANG_WHY '$szwhy'), expected 'size-cap-retry' — something OTHER than the size rung made it small, which under ruling B means a knee has come back, or [LIM-1]'s fold-in regressed"
        fi
    else
        # [OPT-4.2] (2026-08-31, lane o42) THE EXPECTED VALUE MOVED FROM
        # 'declined-nullable' TO 'declined-nullable-default', AND THIS IS NOT
        # A RELABELING -- IT IS A REACHABILITY FACT. [OPT-4.2] generalizes
        # the nullability decline to fire at the FIT SITE, on the FIRST
        # compile attempt, for ANY VM-chosen pattern whose EXACT language is
        # nullable -- which this witness always is, since `(a|b)` is a
        # capturing group and captures force `fit.chosen == ENGM_VM` from
        # attempt 1 (src/opt/select_engine.c's forces_captures rule). So
        # `-fno-scan-edge` alone can no longer force this witness through
        # the SIZE rung AT ALL: the decline fires before the exact machine
        # is even attempted, before scan-edge or the size cap ever matter,
        # so `collapse_reason` never leaves `CR_NONE` and the rung-scoped
        # `ESEL_DECLINED_NULLABLE` is unreachable BY THIS WITNESS regardless
        # of flags short of `-fprefilter` (which overrides the decline
        # entirely rather than reaching it — see the size_moved row below
        # and its own [OPT-4.2] note). MEASURED directly (lane o42,
        # 2026-08-31): under `-fno-scan-edge` alone this pattern now emits
        # 20,628 bytes with RX_VM_PREFILTER "none" / RX_ENGINE_SEL
        # "declined-nullable-default" — the SAME rungless value the
        # tripwire-turned-fixed cell below asserts at the plain DEFAULT,
        # confirming the decline does not depend on scan-edge either.
        #
        # WHETHER `ESEL_DECLINED_NULLABLE`'s OWN SIZE-CAP-RUNG POPULATION IS
        # NOW EMPTY IN THIS CORPUS is a real, open, K35-shaped question this
        # lane is FLAGGING rather than silently deciding: by the "collapsed
        # language's nullability is the exact pattern's" invariant
        # (src/opt/CLAUDE.md's [OPT-4.1] entry), any pattern whose collapsed
        # language is nullable has an EXACT language that is ALSO nullable —
        # so the ONLY way left to reach `ESEL_DECLINED_NULLABLE` via the SIZE
        # rung is a pattern that is DFA-chosen (not VM) on attempt 1 (e.g.
        # under `--no-captures`), whose first attempt overflows a DIFFERENT
        # cap in a way that still leads to a SIZE-cap retry while nullable.
        # No such witness exists in this file today. Left for the manager
        # to rule on rather than invented under this lane's own time
        # pressure.
        if [ "$pf" = none ] && [ -z "$szwhy" ] && [ "$sel" = declined-nullable-default ]; then
            ok "[OPT-4.2] '$pat' compiles at the DEFAULT in $sz bytes with RX_VM_PREFILTER \"none\" / RX_ENGINE_SEL \"declined-nullable-default\" — the pattern's own EXACT language is nullable, the decline fires before any rung is ever offered, and dropping the prefilter still gets the artifact under the cap"
        elif [ "$pf" = hybrid ]; then
            bad "[OPT-4.2] '$pat' kept a prefilter (RX_VM_PREFILTER 'hybrid', LANG_WHY '$szwhy') — its own language matches the empty string, so this artifact pays a scan that can never dismiss a position (pcrec-bench O-10: 1.2-9.9x)"
        elif [ "$sel" != declined-nullable-default ]; then
            bad "[OPT-4.2] '$pat' has RX_VM_PREFILTER '$pf' but RX_ENGINE_SEL '$sel', expected 'declined-nullable-default' (the rungless decline fires on attempt 1 for this witness; see this function's own [OPT-4.2] comment for why 'declined-nullable' is no longer reachable here)"
        else
            bad "[OPT-4.2] '$pat' has RX_VM_PREFILTER '$pf' and LANG_WHY '$szwhy' — no prefilter, yet a language macro beside it; the two lines disagree about one artifact"
        fi
    fi
}
# [OPT-5] 2026-08-31: `-fno-scan-edge` on both rows — at the default the scan
# edge collapses the (a|b) class chain inside the hybrid's DFA, the exact
# artifact never trips the cap, and neither rung runs (the patterns compile
# small via a route these cells were never about). The deny flag reproduces
# the SIZE-rung path deterministically for the NON-nullable row
# (MEASURED: size-cap-retry, as it expects). [OPT-4.2] (2026-08-31) NARROWED
# THIS CLAIM FOR THE NULLABLE ROW: the deny flag no longer reproduces a rung
# at all for it — see size_rung_cell's own [OPT-4.2] comment above.
size_rung_cell '(a|b){0,30000}' none   'alternation nullable'     '-fno-scan-edge'
size_rung_cell '(a|b){1,30000}' hybrid 'alternation non-nullable' '-fno-scan-edge'

# [OPT-4.2] LANDED, 2026-08-31 (lane o42) — this cell used to be a TRIPWIRE
# pinning a KNOWN gap (see the pcrec_reflog for the retired comment): at the
# DEFAULT, '(a|b){0,30000}' compiles (it was size-refused before [OPT-5]) as
# a VM hybrid whose EXACT prefilter language is NULLABLE, and until [OPT-4.2]
# the [OPT-4.1] gate covered only the COLLAPSE rungs
# (`collapse_reason != CR_NONE`), so the ordinary hybrid still built and
# shipped that useless filter (bench O-10: 1.2-9.9x loss on exactly this
# shape). The general decline now covers this path too
# (`src/opt/select_engine.c`'s `prefilter_declined_nullable_default`), so
# the artifact now ships with NO prefilter and stamps
# `RX_ENGINE_SEL "declined-nullable-default"` — the SIZE rung's own nullable
# twin ([LIM-1]) reads the rung-scoped `"declined-nullable"` instead, and the
# two are kept as two values for the reason `docs/spec/match_api.md` §6.3
# gives: a rung OFFERED and REFUSED a rescue is a different population from
# an ordinary compile that never had a rung to begin with.
rm -f "$WORKDIR/o.c"
o42log="$("$ROOT_DIR/scripts/watchdog" -l "opt42-tripwire" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -o "$WORKDIR/o.c" '(a|b){0,30000}' 2>&1)"
if [ $? -eq 0 ]; then
    o42pf=$(grep -oE '^#define RX_VM_PREFILTER .*' "$WORKDIR/o.c" | head -1 | sed 's/.*PREFILTER //;s/"//g')
    o42sel=$(grep -oE '^#define RX_ENGINE_SEL .*' "$WORKDIR/o.c" | head -1 | sed 's/.*SEL //;s/"//g')
    o42why=$(grep -oE '^#define RX_VM_PREFILTER_LANG_WHY .*' "$WORKDIR/o.c" | sed 's/.*WHY //;s/"//g')
    if [ "$o42pf" = none ] && [ "$o42sel" = declined-nullable-default ] && [ -z "$o42why" ]; then
        ok "[OPT-4.2] '(a|b){0,30000}' at the DEFAULT ships with NO prefilter (RX_ENGINE_SEL declined-nullable-default) — the ordinary hybrid's own nullable EXACT language is declined off the rung"
    elif [ "$o42pf" = hybrid ] && [ "$o42why" = exact ]; then
        bad "[OPT-4.2] '(a|b){0,30000}' at the DEFAULT REGRESSED to hybrid/exact with a nullable prefilter language — the [OPT-4.2] decline stopped firing"
    else
        bad "[OPT-4.2] '(a|b){0,30000}' at the DEFAULT stamps PREFILTER '$o42pf' / RX_ENGINE_SEL '$o42sel' / LANG_WHY '$o42why' — neither the fixed behavior nor the pre-fix gap; investigate"
    fi
else
    bad "[OPT-4.2] '(a|b){0,30000}' no longer compiles at the DEFAULT: $(printf '%s' "$o42log" | head -1)"
fi

# [OPT-4.1] `-fprefilter` OVERRIDES THE DECLINE, AND THIS IS THE ONLY PLACE IN
# THE TREE WHERE THAT IS REACHABLE. On the [SEL-1] rung `-fprefilter` makes
# `compile_driver`'s `ovf_eligible` false, so that rung is never OFFERED and
# the decline is never reached (tests/codegen/run_prefilter_collapse.sh §6b(3)
# says so at its own site). On the SIZE rung it IS reached — and without the
# override this pattern would REFUSE, because declining the collapse keeps the
# exact prefilter that the cap already refused and `size_eligible`'s
# `collapse_reason != CR_SIZECAP` makes a third attempt unreachable.
#
# SO THIS CELL IS `docs/spec/limits.md` §3.3's "no pattern that compiles today
# stops compiling" MADE FALSIFIABLE. It was a review finding rather than a red
# run — nothing covered `-fprefilter` on an oversize nullable pattern — which
# is exactly why it gets a cell now.
#
# MEASURED 2026-08-30: the same pattern is 32,076 B / `PREFILTER "none"` at the
# default and 43,773 B / `"hybrid"` / `count-collapsed` / `size cap retry,
# exact 1333437 > 1000000` under `-fprefilter`. The default being SMALLER is
# the same fact limits.md leans on, on ONE pattern rather than across two.
rm -f "$WORKDIR/o.c"
# [OPT-5] 2026-08-31: `-fno-scan-edge` added here too — same reason as the
# cells above; MEASURED: FNSE -fprefilter stamps hybrid / "size cap retry,
# exact 1333406 > 1000000".
fplog="$("$ROOT_DIR/scripts/watchdog" -l "sizecap-fprefilter alternation" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -fno-scan-edge -fprefilter -o "$WORKDIR/o.c" '(a|b){0,30000}' 2>&1)"
if [ $? -eq 0 ]; then
    fpsz=$(wc -c < "$WORKDIR/o.c")
    fppf=$(grep -oE '^#define RX_VM_PREFILTER .*' "$WORKDIR/o.c" | head -1 | sed 's/.*PREFILTER //;s/"//g')
    fpwhy=$(grep -oE '^#define RX_VM_PREFILTER_LANG_WHY .*' "$WORKDIR/o.c" | sed 's/.*WHY //;s/"//g')
    if [ "$fppf" = hybrid ] && [ "${fpwhy#size cap retry}" != "$fpwhy" ]; then
        ok "[OPT-4.1] '(a|b){0,30000}' under -fprefilter KEEPS the collapsed prefilter ($fpsz bytes, '$fpwhy') — the do-or-die request overrides the nullability decline, and the pattern still compiles"
    elif [ "$fppf" = none ]; then
        bad "[OPT-4.1] '(a|b){0,30000}' under -fprefilter stamps RX_VM_PREFILTER \"none\" — an explicit do-or-die request was silently answered with its opposite"
    else
        bad "[OPT-4.1] '(a|b){0,30000}' under -fprefilter stamps PREFILTER '$fppf' / LANG_WHY '$fpwhy', expected the size rung's collapsed prefilter"
    fi
else
    bad "[OPT-4.1] '(a|b){0,30000}' under -fprefilter no longer COMPILES — this is limits.md §3.3's 'no pattern that compiles today stops compiling' going false: declining the collapse keeps the exact prefilter the cap refused, and the size rung has no third attempt: $(printf '%s' "$fplog" | head -1)"
fi

echo

# ---------------------------------------------------------------------------
# Section 2 — a real allocation failure is DIAGNOSED, not aborted.
#
# This is K7's third and worst measured consequence: "under a 2 GB
# address-space limit `pcrec_compile` ABORTS THE CALLER'S PROCESS with no
# diagnostic at all. pcrec is a library; killing the caller is a worse failure
# than the SIGKILL recorded below, because a caller that set a limit did so
# precisely to avoid this."
#
# `ulimit -v` is the right instrument here and RSS-polling is not: this
# section needs malloc to actually RETURN NULL inside the process, which only
# an address-space rlimit causes. (scripts/watchdog's own header explains why
# it polls RSS instead — it is solving the opposite problem, bounding a tree
# that is not cooperating.)
#
# THE LIMIT IS SET BELOW WHAT THE PATTERN NEEDS, NOT BELOW WHAT K7 NEEDED.
# A limit tuned to sit just under the budget's own ceiling would be a control
# calibrated against the thing it controls; a limit of a few tens of MB is
# under any plausible future budget, so this stays a positive control for the
# allocator paths no matter how PCREC_MAX_SUBSET_ELEMS is retuned.
# ---------------------------------------------------------------------------
enomem_case() {   # enomem_case <vlimKB> <pattern> [pcrec flags...]
    local vlim="$1" pat="$2"; shift 2
    local out="$WORKDIR/e.c"
    rm -f "$out"
    local log rc
    log="$( (ulimit -v "$vlim"; exec "$TIMEOUT_BIN" -s KILL "$K7_SECS" "$PCREC" -p rx "$@" -o "$out" "$pat") 2>&1 )"   # [K37]/[TT-6]: exec'd GNU-timeout bound, one line
    rc=$?
    case $rc in
        0)   bad "under ${vlim}KB, '$pat' compiled — the limit did not bind, so this cell proved nothing. Lower it or pick a hungrier pattern" ;;
        1)   if printf '%s' "$log" | grep -q 'out of memory\|too complex\|too large'; then
                 ok "under ${vlim}KB, '$pat' DIAGNOSED: $(printf '%s' "$log" | head -1)"
             else
                 bad "under ${vlim}KB, '$pat' exited 1 with no recognisable diagnostic: $log"
             fi ;;
        134) bad "under ${vlim}KB, '$pat' ABORTED the process (rc 134) — K7's worst case, unfixed" ;;
        139) bad "under ${vlim}KB, '$pat' SEGFAULTED (rc 139) — an allocation failure went unchecked" ;;
        *)   bad "under ${vlim}KB, '$pat' exited $rc: $log" ;;
    esac
}

# EACH LIMIT IS WELL ABOVE THE LOADER'S FLOOR AND WELL BELOW WHAT ITS PATTERN
# NEEDS, and both halves matter. Below about 15000 KB this box cannot even map
# libc, so the cell would test the dynamic loader and report a pcrec pass;
# above what the pattern needs the cell compiles and proves nothing (which the
# `0)` arm above now scores as a FAILURE rather than a shrug — an unbinding
# limit is a silently vacuous control, the exact shape of check this project
# has been bitten by most).
#
# The patterns are chosen to need 110-215 MB, measured, so the limits sit at
# roughly half their need and nothing here is sensitive to the precise value of
# PCREC_MAX_SUBSET_ELEMS. Four shapes so the failure lands in different
# allocators — the DFA state array and its hash table, the arena behind the
# interned state-sets, the emitter's string buffer — rather than proving one
# call site works four times.
#
# [OPT-4] 2026-08-29 — THIS ROW NEEDED A FLAG FOR ONE AFTERNOON AND DOES NOT
# ANY MORE. Under the knee this pattern's prefilter collapsed at the default,
# its peak RSS fell to 5 MB, the 60,000 KB limit stopped binding, and the cell
# had to pass `-fno-prefilter-collapse` to keep its subject. Frank's ruling B
# made the exact prefilter the default again, so the demand is back where the
# comment always said it was: MEASURED 112 MB at the default (the original
# "needs 111 MB", reproduced). The flag is removed rather than left as a
# harmless belt — a flag whose reason has gone is a flag the next reader has to
# re-derive.
enomem_case 100000 'a{9000}'                 # needs 175 MB
enomem_case  60000 '((a)|bc){0,4000}d'       # needs 112 MB (VM route + prefilter)
enomem_case  80000 '[a-zA-Z0-9_.-]{9000}'    # needs 175 MB, wide alphabet
enomem_case  60000 'a{8000}'                 # needs 140 MB

echo

# ---------------------------------------------------------------------------
# Section 3 — the refusal is the RIGHT refusal, not merely a nonzero exit.
#
# `a{0,65535}` is PCRE2's largest legal bounded repeat, so its subset
# construction charges on the order of 65535^2/2 = 2.1e9 state-set elements —
# tens of gigabytes at the measured cost per element. No retuning of
# PCREC_MAX_SUBSET_ELEMS that anyone would make for a real pattern can let this
# one through, which is what makes it safe to pin a verdict on when section 1
# deliberately pins none.
#
# The wording matters for the reason every diagnostic in this tree does: it is
# the caller's only pointer to what happened. "Too complex for the DFA engine"
# is the EXISTING family (D26 — no new wording tier was invented for this), and
# naming the subset construction is what tells a reader which of the two DFA
# bounds they hit and therefore which direction to shrink in.
# ---------------------------------------------------------------------------
echo "== [K7] the refusal's identity =="

# name_check <pattern> <expected-substring> <what it proves> [extra pcrec flags...]
#
# [SEL-1] (2026-08-28) EXTRA FLAGS ARE HOW THIS STAYS A REFUSAL WITNESS. Under
# `--engine=auto`, a DFA-cap overflow is now a SELECTION OUTCOME (fall back to
# the VM) rather than a refusal (docs/spec/tuning.md §2.11) -- so plain `auto`
# on a pattern that used to reach exactly the cap this section names now
# compiles instead, and this check's own claim (name the refusal's WORDING)
# has nothing to read. `--engine=dfa` is the FORCE form and stays do-or-die,
# unconditionally, which is the one property the fallback does not touch --
# passing it as an extra flag restores the refusal text as the observable
# while the construction under test (the same DFA build, same caps) is
# unchanged. See the call sites below for which patterns also need
# `--no-captures` alongside it (a live capturing group forces the VM at
# SELECTION time, before this section's construction is ever reached).
name_check() {
    local pat="$1" want="$2" why="$3"; shift 3
    local log rc
    log="$("$ROOT_DIR/scripts/watchdog" -l "wording $pat" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx "$@" -o "$WORKDIR/w.c" "$pat" 2>&1)"   # [K37]: the wrapper (watchdog) IS the bound and execs a BINARY -- the compiler itself, never a bash function -- on ONE line so the check sees both
    rc=$?
    if [ "$rc" -ne 1 ]; then
        bad "'$pat' should be a diagnosed refusal (rc 1), got rc $rc: $log"
    elif ! printf '%s' "$log" | grep -q "$want"; then
        bad "'$pat' should name '$want' ($why), said: $log"
    else
        ok "$why"
    fi
}

# THREE BOUNDS, THREE SHAPES, THREE DIFFERENT DIAGNOSTICS. K7's complaint was
# that the shape which needed a cap could not reach one; the answer is not "now
# it reaches THE cap" but "each shape reaches the cap that describes it", and
# a reader has to be able to tell which one they hit from the message alone.
#
#   `a{0,65535}` builds 2n NFA states with tiny state-sets — the NFA SIZE cap
#     is the right one, and it fires during construction, in 0.1 s.
#   `a{65535}` builds few states with enormous state-sets — the SUBSET-ELEMENT
#     bound is the only one that can see it (measured 216 MB / 0.9 s, against
#     2.1 GB / 12.3 s before this lane, when the state cap eventually caught it).
#   an exponential subset blowup builds a huge NUMBER of small states — the
#     state-COUNT cap, which is the pre-existing one, and it must still work.
#     This is the check that notices if the new bounds took the old one's
#     customers away.
# `a{0,65535}` needs no extra flag: it hits PCREC_MAX_NFA_STATES, which has no
# `--engine=auto` fallback (there is no other engine to hand a pattern to when
# the NFA itself cannot be built at all -- src/opt/select_engine.c never sees
# it, since NFA construction runs for every engine choice). `a{65535}` DOES,
# so both of its checks below force `--engine=dfa` -- see name_check's own
# comment for why that is do-or-die and unaffected by SEL-1.
name_check 'a{0,65535}' 'NFA exceeds' \
    "the bounded-OPTIONAL family reaches the NFA size cap"
name_check 'a{65535}' 'subset construction' \
    "the EXACT-count family reaches the subset-element bound" \
    --engine=dfa
name_check 'a{65535}' 'too complex for the DFA engine' \
    "that bound refuses inside the EXISTING diagnostic family (D26), not a new tier" \
    --engine=dfa

# [SEL-1] (2026-08-28) THE AUTO-SIDE TWIN, for this shape as the family's own
# representative (all three name_check cells above and the state-cap check
# below are the identical shape one cap over): plain `auto`, no `--engine=dfa`,
# must COMPILE (the do-or-die refusal `--engine=dfa` still gives is what SEL-1
# turns into a fallback here) and stamp the fact rather than staying silent
# about it. `a{65535}` has no capturing group, so `--engine=dfa` alone was
# already the do-or-die twin of this cell with nothing else to control for.
out="$WORKDIR/w3.c"
rm -f "$out"
log="$("$ROOT_DIR/scripts/watchdog" -l "auto fallback a{65535}" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -o "$out" 'a{65535}' 2>&1)"   # [K37]
rc=$?
if [ "$rc" -ne 0 ]; then
    bad "'a{65535}' under plain auto should COMPILE (SEL-1's fallback), got rc $rc: $log"
elif ! grep -q '^#define RX_ENGINE "vm"$' "$out"; then
    bad "'a{65535}' under auto compiled but did not stamp RX_ENGINE \"vm\" (fallback did not fire the way expected)"
elif ! grep -q '^#define RX_ENGINE_WHY "dfa overflowed: subset construction exceeds' "$out"; then
    bad "'a{65535}' under auto compiled as VM but RX_ENGINE_WHY does not name the subset-element overflow: $(grep '^#define RX_ENGINE_WHY' "$out")"
else
    ok "[SEL-1] 'a{65535}' under auto falls back instead of refusing: RX_ENGINE \"vm\", RX_ENGINE_WHY names the subset-construction overflow"
fi

# The state-COUNT cap must still be reachable by the shapes it was built for —
# the fix moves refusals EARLIER for one growth law and must not have taken the
# other cap's customers away. An exponential subset blowup has a small state-set
# per state and a huge NUMBER of states, so it is the state cap's own shape.
#
# [SEL-1] `--no-captures --engine=dfa`: this pattern's `(a|b)` groups are
# capturing groups (default on), so `--engine=dfa` ALONE would refuse on the
# earlier, unrelated "requires captures" ground before ever reaching the
# construction under test (measured, first draft of this fix) — exactly
# run_trie_identity.sh's own finding one section over. `--no-captures` is
# answer-neutral for what this check reads: D31's A_CAP erasure already makes
# captures invisible to nfa.c's construction, so the automaton is unchanged.
log="$("$ROOT_DIR/scripts/watchdog" -l "wording state-cap" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx --no-captures --engine=dfa -o "$WORKDIR/w2.c" '(a|b)*a(a|b){20}' 2>&1)"   # [K37]: the wrapper (watchdog) IS the bound and execs a BINARY -- the compiler itself, never a bash function -- on ONE line so the check sees both
rc=$?
if [ "$rc" -eq 1 ] && printf '%s' "$log" | grep -q 'states'; then
    ok "the state-COUNT cap still fires on its own shape: $(printf '%s' "$log" | head -1)"
elif [ "$rc" -eq 1 ]; then
    bad "exponential blowup refused, but not by the state cap: $log"
else
    bad "'(a|b)*a(a|b){20}' should hit the state cap (rc 1), got rc $rc: $log"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks inconclusive: $inconc"
[ "$fail" -eq 0 ]
