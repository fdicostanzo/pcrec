# S993 — [WINDOW-E1] PRIOR-NONE CARRIES A UNIFORM TABLE (src/core/findings.c,
# `pcrec_find_offer`): where no table exists, the offer hands the kit a
# uniform byte-rate as its payload — D126 Q4's false confidence (a uniform
# table answers COMPARE "true" for every pair, a density claim no data
# supports) and D162 add. 2's "providing defaults there might give false
# confidence".
#
# Detector: the object's own invariant (src/gen/memfn_sites.c,
# `analysis_invariant`: a payload without a table-bearing source) refuses
# every `-e utf8` compile with no analysis; run_findings_tests.sh §14 C-E1-3.
SAB_ID="S993-prior-none-uniform-payload"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='the offer'\''s PRIOR_NONE state carries a uniform 256-entry table as its payload, where window_contract.md §3.1'\''s invariant says no payload travels'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §4/§14 (every -e utf8 default compile refuses: the invariant'\''s internal error); corpus red on every utf8 block.'
SAB_REACH='"$PCREC" -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=none\"" "$REACH_TMP/o.c" && echo REACH-E1-PRIOR-NONE'
SAB_REACH_EXPECT="REACH-E1-PRIOR-NONE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!find_kind_rows[r].table) return;'
SAB_AFTER='    if (!find_kind_rows[r].table) {
        static uint32_t uniform[256];   /* SABOTAGE S993: a false-confidence table */
        if (out->source == PCREC_FIND_SRC_PRIOR_NONE) {
            for (int b = 0; b < 256; b++) uniform[b] = 3906;
            uniform[0] += 1000000 - 3906 * 256;
            out->payload = uniform;
        }
        return;
    }'
