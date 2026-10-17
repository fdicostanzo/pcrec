# S1030 — [WINDOW-E1] PROVENANCE BY LINK, revision 3's rule
# (src/core/findings.c, `find_block_prior`): a block is a prior's iff it is
# the embedded store's `default`, anything else MEASURED. A byte-identical
# user copy of `default.rxt` then reads MEASURED, and the authored prior is
# admitted as EVIDENCE (window_contract.md rev 3.1 M2; D162 add. 4).
#
# Detector: run_findings_tests.sh §14 C-E1-1's `copy` cell (a verbatim `-I`
# copy: expected PRIOR_AUTHORED) and its `auth` (`source authored`) and
# `log` (`fidelity synthesized`) cells.
SAB_ID="S1030-provenance-by-link"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='find_block_prior answers by the answering link'\''s identity (the store'\''s own default block) instead of the block'\''s provenance stanza'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 C-E1-1 (copy/byte, auth/byte, log/*).'
SAB_REACH='mkdir -p "$REACH_TMP/C" && cp "$TREE/src/findings/default.rxt" "$REACH_TMP/C/" && "$PCREC" -p rx -I "$REACH_TMP/C" --analysis default -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o.c" && echo REACH-E1-USER-COPY'
SAB_REACH_EXPECT="REACH-E1-USER-COPY"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return (fb->prov_source && !strcmp(fb->prov_source, "authored")) ||
           (fb->prov_fidelity && !strcmp(fb->prov_fidelity, "synthesized"));'
SAB_AFTER='    size_t nt;   /* SABOTAGE S1030: provenance by link (the store'\''s default) */
    const PcrecFindTblBlock *t = pcrec_find_store_blocks(&nt);
    return fb >= t && fb < t + nt && !strcmp(fb->bundle, "default");'
