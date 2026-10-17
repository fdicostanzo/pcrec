# S992 — [WINDOW-E1] PROVENANCE BY NAME (src/core/findings.c,
# `find_block_prior`): a block is a prior's iff its bundle is NAMED
# `default`, instead of by its own provenance stanza (D162 add. 4). A user
# `-I` bundle named `default` that declares a measured source reads AUTHORED,
# and every other authored or synthesized bundle reads MEASURED.
#
# Detector: run_findings_tests.sh §14 C-E1-1's `mdef` cell (expected
# MEASURED, got PRIOR_AUTHORED), and its `log`/`auth` cells.
SAB_ID="S992-provenance-by-name"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='find_block_prior answers by the bundle'\''s NAME ("default"), not by the answering block'\''s own provenance stanza: a measured user bundle named default reads AUTHORED, an authored user bundle reads MEASURED'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 C-E1-1 (mdef/byte, auth/byte, log/*).'
SAB_REACH='python3 "$TREE/tests/findings/e1_fixtures.py" "$TREE" "$REACH_TMP/fx" && "$PCREC" -p rx -I "$REACH_TMP/fx/MDEF" --analysis default -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o.c" && echo REACH-E1-MEASURED-DEFAULT'
SAB_REACH_EXPECT="REACH-E1-MEASURED-DEFAULT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return (fb->prov_source && !strcmp(fb->prov_source, "authored")) ||
           (fb->prov_fidelity && !strcmp(fb->prov_fidelity, "synthesized"));'
SAB_AFTER='    return !strcmp(fb->bundle, "default");   /* SABOTAGE S992: provenance by name */'
