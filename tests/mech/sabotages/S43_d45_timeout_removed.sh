# S43 — [M4.5c fix] D45's generated-code compile budget is REMOVED: gen_cc
# invokes the compiler directly instead of under the budget wrapper.
#
# This is the shape D45 exists to prevent, and it is invisible to everything
# else: the emitted matchers are unchanged, every suite still passes, and the
# only difference is that the next pathological artifact hangs a battery for
# hours instead of failing in five seconds. That is precisely what happened
# before the ruling -- two cc1 processes at 99.9% for 1h40m and 55m -- and the
# reason it went unnoticed is that an unbounded compile reads as "still
# running", never as "failed".
#
# tests/lib/run_gen_timeout_tests.sh's positive control is the only thing in
# the tree that can see it.
#
# ANCHOR RE-DERIVED 2026-08-17 (twenty-eighth session). The original anchor
# (`GEN_CC_LOG="$(timeout "$secs" "$@" 2>&1)"`) was rewritten by the D45 THIRD
# addendum's CPU-primary change ([WDOG-WIRE] c78ef6b: wall timeout + RLIMIT_CPU
# via a bash -c trampoline), and S43 sat APPLY-FAILED — silently unmeasured —
# from that commit until the counter-K landing battery ran the full matrix
# (its report attributed the drift exactly). The re-derived edit removes BOTH
# clocks (the CPU rlimit and the wall timeout), which is what "budget removed"
# means under the CPU-primary design; removing only one is a DIFFERENT, weaker
# sabotage that the fire controls would still partially catch. Note the meta
# lesson recorded with the fix: the row that verifies the budget is WIRED
# (run_gen_timeout_tests.sh's coverage assertion) is a different row from the
# one that verifies its REMOVAL IS CAUGHT (this one), so the wiring check
# could not see this row go dark.
SAB_ID="S43-d45-timeout-removed"
SAB_FILE="tests/lib/gen_timeout.sh"
SAB_SUITES="gentimeout"
SAB_DESC="gen_cc runs the compiler directly instead of under the D45 budget (both clocks removed: no RLIMIT_CPU, no wall timeout; nothing else in the tree changes)"
SAB_DOC_FIGURE="tests/lib/run_gen_timeout_tests.sh: the CPU fire control fails (an over-budget compile succeeds instead of dying of SIGXCPU with the D45 diagnostic)"
SAB_COUNT=1
# ANCHOR RE-DERIVED AGAIN 2026-08-22 (thirty-fifth session, manager). [TT-3]'s
# CCACHE=1 wiring (merge ee57668) replaced the trampoline's `exec "$@"` with
# `_gen_cc_run "$@"` (the compile/link-split dispatcher), moving this anchor's
# quoted text. Caught by scripts/m6read_check_sab_anchors.py at the [DOC-DRV]
# merge review — the tripwire's first live catch since its promotion-readiness
# fix, and the reason it now joins the merge bar. The re-derived edit still
# removes BOTH clocks and ONLY the clocks: the sabotaged call still routes
# through _gen_cc_run, because removing the split as well would be a
# DIFFERENT sabotage (the fire controls would catch pieces of it for the
# wrong reason).
#
# ANCHOR RE-DERIVED AGAIN 2026-08-23 ([TT-6]). The bare `timeout` binary name
# was replaced with `"$TIMEOUT_BIN"` (tests/lib/timeout_bin.sh's resolved
# choice, sourced at this file's own top) -- the uutils-vs-GNU coreutils
# `timeout` finding, docs/dev/tt4_measurement.md. The sabotage's INTENT is
# unchanged: it still removes both clocks and only the clocks, routing
# through _gen_cc_run exactly as before; only the literal binary-name token
# in the quoted anchor text moved.
SAB_BEFORE='    GEN_CC_LOG="$("$TIMEOUT_BIN" "$wall" bash -c \
        '"'"'ulimit -S -t "$1" 2>/dev/null; ulimit -H -t $(($1 + 30)) 2>/dev/null; shift; _gen_cc_run "$@"'"'"' \
        _ "$cpu" "$@" 2>&1)"'
SAB_AFTER='    GEN_CC_LOG="$(_gen_cc_run "$@" 2>&1)"  # SABOTAGE S43: budget not applied (neither clock)'
