# S317 — [FINDINGS] B2 F-13: G1 ELIDES A PRE-CHECK WITH NO DFA SCAN IN FRONT
# (src/gen/emit_dfa.c, `req_byte_dominated_by`): the `p < 0` guard — no
# candidate scan byte, so nothing to dominate the pre-check — is replaced by a
# rate comparison, so wherever a byte-rate exists the whole-window pre-check
# is declared "dominated" and dropped on a VM route whose ONLY linear absence
# proof it was. Whether that route gives up then follows the rate (design
# §6.2a's C3 row, [r2 S-F2]: a rate may decide whether a pre-check is emitted
# only where a linear machine in front makes both forms answer and give up
# identically).
#
# Detector: run_findings_tests.sh §9 — K65's repro (a framed VM, no DFA in
# front) under the default (`byte`) and under fire-c3: the sabotaged tree
# gives up (exit 3) where NOMATCH is the answer.
SAB_ID="S317-findings-g1-elides-without-scan"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="findings prechecks"
SAB_DESC="G1's no-scan guard (p < 0 -> keep the pre-check) is replaced by a rate comparison, so on a VM route with no DFA in front the whole-window pre-check is dropped wherever a byte-rate exists and the backtracker gives up on subjects the pre-check alone proved NOMATCH — a rate deciding a give-up"
SAB_DOC_FIGURE="Since B3b: prechecks red (hand-measured by lane b3bmtri on the planted tree: 25 failed / 369 passed, §5.1/§5.6/§5.11 REQ_WHY \"dominated\" where \"emitted\" is expected) and findings GREEN (the VM route's spans are REQUIRED and P0 decides them first). Before B3b: findings red on §9 (K65 witness cells exit 3 under the default's byte-rate and under fire-c3, both encodings for the bundles). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S317."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && grep -q "^#define RX_FINDINGS \"byte-rate=default:" "$REACH_TMP/o.c" && echo REACH-FINDINGS-G1-NO-SCAN-KEEPS'
SAB_REACH_EXPECT="REACH-FINDINGS-G1-NO-SCAN-KEEPS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-18 (lane b3bmtri, [MEMFN] R17-b' B3b): G1 IS THE KIT'S PRES
# row P2 now (memfn/src/presence.c `kit_pres_picks`, the P2 block, read by
# finder.c `fd_pres` as SF_PROVEN); pcrec's `req_byte_dominated_by` survives
# only in the PCREC_CAND_TRACE build as the five-pick shadow's expectation,
# so the old plant landed on code no default artifact reads. The plant moves
# to the same conjunct of the port; the plant's intent is unchanged.
# THE DETECTOR MOVES (b3bmtri, measured): on the VM route with no DFA in
# front pcrec states every presence span REQUIRED (`req_pres_spans`:
# VM_ATTEMPT), and the kit's row P0 decides a REQUIRED span BEFORE P2 is
# asked, so the K65 give-up this row was written for now needs P0 to fail
# too (P0's own plants: S1105, S1122). The planted K65 witness is byte-
# identical to the clean one (byte and utf8), emit_sweep reads 0 c-vm movers
# and 238 c-default movers: the plant still moves every DFA-route pre-check
# whose start search proves no byte from REQ_WHY "emitted" to "dominated",
# which run_prechecks.sh §5.1/§5.6/§5.11 hold. findings stays listed: it is
# the answer-level arm should P0 ever stop shadowing P2 on that route.
SAB_BEFORE='        if (!proof || proof->byte < 0) dom = 0;'
SAB_AFTER='        if (!proof || proof->byte < 0) dom = rate && lead >= 0 && rate[lead] <= rate[lead];   /* SABOTAGE S317 */'
