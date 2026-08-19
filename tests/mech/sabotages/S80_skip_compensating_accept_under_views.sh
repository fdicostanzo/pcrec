# S80 — [M6.2 wave C] THE SKIP'S COMPENSATING SCALAR ACCEPT EMITTED UNDER A
# CLASS AXIS (§3.6.1 row 4).
#
# Mechanism 4 in §3.6.1's table is the POST-SKIP COMPENSATING ACCEPT: with the
# accept check ahead of the skip (the non-views evaluation order), a skipped
# run's final position would go unrecorded, so the emitter plants a bare
# `last = pos;` after the skip. Under `views` that line is NOT emitted at all,
# because the ordering flips — the accept check runs AFTER the skip and
# already covers the landing position.
#
# So this mechanism's cure is the ORDERING, and the ordering's guard is the
# `!views` in the emit condition. This sabotage drops it, planting the scalar
# compensating accept in an artifact whose accept is class-indexed. The
# recorded `last` is then the state's UPC_PLAIN bit at a landing position
# whose actual class may say otherwise — a match recorded where there is none,
# which is worse than a lost one.
#
# NOTE THE ASYMMETRY WITH S72, which is the same shape on the reverse machine
# and was wave B's. That row could fire on a `\b` pattern because the reverse
# skip's writer is `sfound` and the invariant it breaks is §3.8.3.1's. This
# one is the FORWARD writer, and the forward `last` wants the LARGEST
# accepting position, so it needs a pattern where the accept genuinely varies
# inside the run — the `(?m)$` family, not `\b`.
SAB_ID="S80-skip-compensating-accept-under-views"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness mlinediff"
SAB_HARNESS_TARGET="tests/assertions/multiline.rxt"
SAB_DESC="the forward self-loop skip emits its bare scalar 'last = pos;' compensating accept under a class axis too, so a skip landing on a byte whose class does NOT accept still records a match end (S3.6.1 row 4; the cure is the evaluation ORDER, and this removes its guard)"
SAB_DOC_FIGURE="tests/assertions/run_mline_diff.sh: the (?m)\$-with-quantifier patterns report match ends libpcre2 does not"
SAB_COUNT=1
SAB_BEFORE='            if (!views && fd->st[K].up[UPC_PLAIN].accept)'
SAB_AFTER='            if (fd->st[K].up[UPC_PLAIN].accept)   /* SABOTAGE S80 */'
