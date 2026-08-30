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
# [OPT-4] 2026-08-29 — THE THIRD SHAPE NEEDS `-fno-prefilter-collapse` NOW, AND
# THE FOURTH FIELD SAYS SO. `(a|b){0,30000}`'s 1.33 MB was almost entirely its
# hybrid PREFILTER's tables, and [OPT-4] rebuilds that from the count-collapsed
# language: at the default the artifact is **32,279 bytes** in the split
# `.c`+`.h` form this cell emits (43,433 self-contained) and compiles
# cleanly, so the cell had no oversize subject left and the cap it exists to
# test was never reached. That is a WITNESS going vacuous, not a cap that
# stopped working — the other two shapes, whose bulk is the VM body rather than
# a prefilter, still refuse at the default untouched.
#
# Denying the axis restores the exact machine and the refusal (MEASURED at
# 1,333,300 bytes, against the 1,333,109 pinned here before the two new stamp
# lines). The shape keeps its coverage of the ALTERNATION case, and the new
# default outcome is pinned separately below so the size win is recorded rather
# than merely absent.
size_moved=(
    'a{0,25000}:1103367:'
    '[a-z]{0,30000}:1323371:'
    '(a|b){0,30000}:1333109:-fno-prefilter-collapse'
)
for entry in "${size_moved[@]}"; do
    pat="${entry%%:*}"; rest="${entry#*:}"
    was="${rest%%:*}"; extra="${rest#*:}"
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
rm -f "$WORKDIR/o.c"
dflog="$("$ROOT_DIR/scripts/watchdog" -l "sizecap-default alternation" -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -o "$WORKDIR/o.c" '(a|b){0,30000}' 2>&1)"
if [ $? -eq 0 ]; then
    sz=$(wc -c < "$WORKDIR/o.c")
    if [ "$sz" -lt 200000 ]; then
        ok "[OPT-4] '(a|b){0,30000}' now compiles at the DEFAULT in $sz bytes (was 1,333,109 and refused) — its size was its prefilter, and the count-collapsed one does not scale with the count"
    else
        bad "[OPT-4] '(a|b){0,30000}' compiled at the default but emitted $sz bytes, expected well under 200,000 — the collapse is not reaching this shape as it did at the landing"
    fi
else
    bad "[OPT-4] '(a|b){0,30000}' no longer compiles at the DEFAULT — it did at the landing (32,279 bytes); the collapse has stopped firing on it, or a cap moved: $(printf '%s' "$dflog" | head -1)"
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
# [OPT-4] 2026-08-29 — THE SECOND SHAPE KEEPS ITS FLAG, and the flag is what
# keeps this cell non-vacuous rather than a preference. `((a)|bc){0,4000}d` is
# the one shape here whose demand was its PREFILTER, and [OPT-4] rebuilds that
# from the count-collapsed language: MEASURED peak RSS **5 MB at the default**
# against **112 MB with `-fno-prefilter-collapse`** (the comment's original
# "needs 111 MB", reproduced). At the default the 60,000 KB limit no longer
# binds, the compile succeeds, and the `0)` arm above scores that as the
# failure it is. Denying the axis restores the exact machine, the 112 MB
# demand, and therefore this row's coverage of the VM-route-plus-prefilter
# allocators — which is the distinct thing it contributes to the four.
# Re-witnessing with a different pattern would have kept the cell green while
# quietly dropping that allocator path.
enomem_case 100000 'a{9000}'                 # needs 175 MB
enomem_case  60000 '((a)|bc){0,4000}d' -fno-prefilter-collapse   # needs 112 MB (VM route + EXACT prefilter); 5 MB at the default since [OPT-4]
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
