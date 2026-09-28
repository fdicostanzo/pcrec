# S320 — [OPT-LITSCAN] F5's FLOOR REVERTS TO TWO (D127, docs/dev/decisions.md)
# `pcrec_lit_run` (src/core/cpset.c) is narrowed back to its abi-41 predicate
# (`len < 2` instead of F5's `len < 3`), so a two-byte literal run takes
# S2a's one-compare form again instead of falling through to the pre-S2a
# per-byte early-exit chain.
#
# S2a's compare is SOUND at any L >= 2 — F5 narrowed the floor for a measured
# COST reason (the [B108] L-sweep: a two-byte compare is the smallest gain in
# the whole L-sweep on a matching subject and a real per-call regression on a
# failing one), never for correctness. So this plant is ANSWER-IDENTITY-
# PRESERVING BY CONSTRUCTION: every subject a two-byte-run pattern can match,
# the reverted compare still matches, and every .rxt corpus cell, oracle
# differential and byte-identity gate in the tree stays green. Its ONLY
# detector is tests/codegen/run_codegen_tests.sh's [OPT-LITSCAN F5] block,
# which reads two real artifacts ('xy' and 'xyz' compiled --engine=vm) for
# the emitted form directly: RX_VM_LIT_RUNS's stamp value, the presence or
# absence of the one-compare `!memcmp(...)`, and the presence or absence of
# the per-byte byte-chain tests — never a differential, since there is
# nothing for a differential to disagree about.
#
# corpus:0fail is therefore the EXPECTED reading on this row, the same shape
# S263/S266/S269/S270 already carry in this file: a plant with no answer-
# level detector, caught only by the structural check built for it.
SAB_ID="S320-lit-run-floor-reverts-to-two"
SAB_FILE="src/core/cpset.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="pcrec_lit_run's floor reverts from three bytes to two (D127's abi-41 predicate), so a two-byte literal run takes S2a's one-compare form instead of F5's per-byte byte chain -- answer-identity-preserving, detected only by tests/codegen/run_codegen_tests.sh's [OPT-LITSCAN F5] block reading real artifacts"
SAB_DOC_FIGURE="MEASURED 2026-09-28 (lane litf5): DETECTED. codegen:3fail/<N>pass (all three failures under the [OPT-LITSCAN F5] heading, naming 'xy' stamping RX_VM_LIT_RUNS 1, carrying the one-compare memcmp, and missing the per-byte chain), harness (tests/litscan/litrun.rxt) EXPECTED 0fail -- the plant changes no answer. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S320."
# [MECH-REACH] the clean tree's two-byte witness carries the byte chain and
# stamps 0, so the plant has something to move.
SAB_REACH='"$PCREC" -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern "xy" && grep -qF "RX_VM_LIT_RUNS 0" "$REACH_TMP/o.c" && grep -qF "subject[scan_position] == 120" "$REACH_TMP/o.c" && echo REACH-TWO-BYTE-CHAIN'
SAB_REACH_EXPECT="REACH-TWO-BYTE-CHAIN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (len < 3) return 0;'
SAB_AFTER='    if (len < 2) return 0;   /* SABOTAGE S320: the floor reverts to two */'
