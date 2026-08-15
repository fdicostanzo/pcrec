# S43 — [M4.5c fix] D45's generated-code compile budget is REMOVED: gen_cc
# invokes the compiler directly instead of through `timeout`.
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
SAB_ID="S43-d45-timeout-removed"
SAB_FILE="tests/lib/gen_timeout.sh"
SAB_SUITES="gentimeout"
SAB_DESC="gen_cc runs the compiler directly instead of under `timeout` (the D45 budget stops being applied; nothing else in the tree changes)"
SAB_DOC_FIGURE="tests/lib/run_gen_timeout_tests.sh: the positive control fails (an over-budget compile succeeds instead of returning 124)"
SAB_COUNT=1
SAB_BEFORE="    GEN_CC_LOG=\"\$(timeout \"\$secs\" \"\$@\" 2>&1)\""
SAB_AFTER="    GEN_CC_LOG=\"\$(\"\$@\" 2>&1)\"  # SABOTAGE S43: budget not applied"
