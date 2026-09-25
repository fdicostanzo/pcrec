# S270 — [OPT-PRECHECK-ADMIT] G1 DOMINANCE REMOVED (src/gen/emit_dfa.c,
# `req_byte_dominated_by`): the comparison that answers "is a pre-check on `q`
# dominated by a candidate-start scan already running on `p`" always says no,
# so an artifact emits a second whole-window `memchr` on a byte its own
# prefilter already scans — `wild-codegrammar-json-array-begin`'s
# `memchr(..., 91, ...)` twice per call, the ledger's 4-cell +32.6% class
# (docs/dev/optloop/cycle1_ledger_reading.md §4.3, §6 G1).
#
# ANSWER-INVISIBLE, exactly as S269 is, and for the same reason: a redundant
# conservative pre-check returns the answer the pass below it returns anyway.
# The `harness` arm is listed and is EXPECTED to stay green; the structural
# section is the detector.
#
# THE PLANT EMPTIES THE COMPARISON AND NOT THE CALL, its sibling's reason: the
# call site stays, the `req_run.len` scoping stays, the byte the artifact
# scans is still derived, so the only thing the suite sees is the density
# comparison's absence. It also keeps the IDENTITY arm out of the way of any
# encoding question — the plant makes the same-byte case fail to decline too,
# which is the one direction of this rule that holds under every encoding.
SAB_ID="S270-precheck-dominance-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the [OPT-PRECHECK-ADMIT] G1 DOMINANCE rule is removed, so an artifact that already scans a candidate-start byte at least as rare as its necessary byte emits the whole-window memchr pre-check on top of it — two passes on the same byte value where the ledger measured one, which is the json-array-begin regression class"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh is the detector: section 5.1 reports the two dominance witnesses stamping RX_REQ_WHY 'emitted' where 'dominated' is expected, 5.1b reports the redundant pre-check back in each file, 5.3 reports the byte-encoding row's decline gone (and leaves its two 'emitted' rows green, which is what makes the failure a direction rather than a blanket), and 5.5's G1 population floor drops to 0. Measured on the clean tree at 274 passed / 0 failed (267 before K66 added §5.8, 258 before K65 added §5.7, 250 before K64 added §5.6). The harness arm is expected to stay GREEN. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S270."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# single-literal pattern `\[` derives byte 91, carries its own memchr
# prefilter on 91, and emits NO second pass.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\[" && grep -q "^#define RX_REQ_WHY \"dominated\"" "$REACH_TMP/o.c" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && ! grep -q "memchr(subject + search_from," "$REACH_TMP/o.c" && echo REACH-DOMINANCE-DECLINES-DUPLICATE-PASS'
SAB_REACH_EXPECT="REACH-DOMINANCE-DECLINES-DUPLICATE-PASS"
SAB_COUNT=1
SAB_BEFORE='static bool req_byte_dominated_by(Ctx *cx, int p, int q)
{
    if (p < 0) return false;
    if (p == q) return true;
    if (cx->opt->encoding != PCREC_ENC_BYTE) return false;
    return pcrec_byte_freq_ppm(p) <= pcrec_byte_freq_ppm(q);
}'
SAB_AFTER='static bool req_byte_dominated_by(Ctx *cx, int p, int q)
{
    (void)cx; (void)p; (void)q;
    return false;   /* SABOTAGE S270: the G1 dominance rule removed */
}'
