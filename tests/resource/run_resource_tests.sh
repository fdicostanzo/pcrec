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
#        K7_SECS  wall budget per compile (default 60)
#        K7_CPU   CPU budget per compile (default 20)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

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
K7_SECS="${K7_SECS:-60}"
K7_CPU="${K7_CPU:-20}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
export WATCHDOG_SECTION="resource"

pass=0; fail=0
ok()   { echo "PASS: $*"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $*"; fail=$((fail + 1)); }

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
    log="$("$ROOT_DIR/scripts/watchdog" -l "compile $pat" \
             -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" \
             -L "$WORKDIR/watchdog.log" -- \
             "$PCREC" -p rx -o "$out" "$pat" 2>&1)"
    rc=$?
    case $rc in
        0) ok "'$pat' compiles within the ceiling" ;;
        1) if printf '%s' "$log" | grep -q 'too complex\|too large\|out of memory'; then
               ok "'$pat' refused cleanly: $(printf '%s' "$log" | head -1)"
           else
               bad "'$pat' exited 1 with an unrecognised diagnostic: $log"
           fi ;;
        122) bad "'$pat' EXCEEDED $K7_MEM of tree RSS — this is K7 itself" ;;
        123) bad "'$pat' EXCEEDED ${K7_CPU}s of CPU — the cap is not firing early enough" ;;
        124) bad "'$pat' EXCEEDED ${K7_SECS}s of wall time (stuck, not working)" ;;
        134) bad "'$pat' ABORTED (rc 134) — a library must not abort its caller" ;;
        137) bad "'$pat' was SIGKILLed (rc 137) — K7's original signature" ;;
        *)   bad "'$pat' exited $rc, which is neither a compile nor a refusal: $log" ;;
    esac
done

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
enomem_case() {
    local vlim="$1" pat="$2"
    local out="$WORKDIR/e.c"
    rm -f "$out"
    local log rc
    log="$( (ulimit -v "$vlim"; exec timeout -s KILL "$K7_SECS" \
                "$PCREC" -p rx -o "$out" "$pat") 2>&1 )"
    rc=$?
    case $rc in
        0)   ok "under ${vlim}KB of address space, '$pat' still compiled (limit not binding — fine)" ;;
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

# 40 MB of address space. Enough for the binary, libc and a small compile;
# far too little for any of these, so malloc genuinely fails partway through.
# Three different pattern shapes so the failure lands in different allocators
# (parser arena, NFA growth, DFA interning, emitter buffer) rather than
# proving one call site works.
enomem_case 40000 'a{0,20000}'
enomem_case 40000 "$(python3 -c 'print("(" + "|".join("w%04d" % i for i in range(4000)) + ")")')"
enomem_case 40000 'a{20000}'
enomem_case 25000 '(a|b){0,4000}c'

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
log="$("$ROOT_DIR/scripts/watchdog" -l "wording a{0,65535}" \
         -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- \
         "$PCREC" -p rx -o "$WORKDIR/w.c" 'a{0,65535}' 2>&1)"
rc=$?
if [ "$rc" -ne 1 ]; then
    bad "'a{0,65535}' should be a diagnosed refusal (rc 1), got rc $rc: $log"
elif ! printf '%s' "$log" | grep -q 'too complex for the DFA engine'; then
    bad "'a{0,65535}' refused outside the 'too complex for the DFA engine' family: $log"
elif ! printf '%s' "$log" | grep -q 'subset construction'; then
    bad "'a{0,65535}' hit a DFA bound but not the subset-construction one: $log"
else
    ok "'a{0,65535}' names the subset-construction bound in the existing family"
fi

# The state-COUNT cap must still be reachable by the shapes it was built for —
# the fix moves refusals EARLIER for one growth law and must not have taken the
# other cap's customers away. An exponential subset blowup has a small state-set
# per state and a huge NUMBER of states, so it is the state cap's own shape.
log="$("$ROOT_DIR/scripts/watchdog" -l "wording state-cap" \
         -s "$K7_SECS" -c "$K7_CPU" -m "$K7_MEM" -L "$WORKDIR/watchdog.log" -- \
         "$PCREC" -p rx -o "$WORKDIR/w2.c" '(a|b)*a(a|b){20}' 2>&1)"
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
[ "$fail" -eq 0 ]
