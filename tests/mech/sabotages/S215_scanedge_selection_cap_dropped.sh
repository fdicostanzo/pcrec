# S215 (r48 F1, 2026-08-31) — THE SCAN-EDGE SELECTION CAP'S TRUE ENFORCER
# LOSES ITS CONJUNCT.
#
# WHAT IT BREAKS. PCREC_MAX_SCAN_EDGES (limits.def, 4 per machine) has TWO
# sites: the PASS's own selection conjunct (this row's plant — the site that
# decides which chains' interior states are marked dead) and emit_dfa.c's
# annotation-reading cap (redundant BY CONSTRUCTION only while the pass
# never selects more). r48's checks critic named the gap: with the pass
# conjunct gone the two sites diverge — the pass accepts EVERY found chain
# (also overrunning its own taken[SCAN_MAX_EDGES] array), states beyond the
# emit side's 4 are already condemned, and the artifact ships dead table
# cells with no loop to replace them — the same failure family S213/S214
# pin on the criterion, on the CAP instead. Nothing else in the tree
# watches that divergence; tests/classes/multi_chain.rxt was added as this
# row's detector (patterns with ~10 chain candidates against a cap of 4).
SAB_ID="S215-scanedge-selection-cap-dropped"
SAB_FILE="src/opt/scanedge.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/classes/multi_chain.rxt"
SAB_DESC="scanedge.c's selection loop drops its 'nedges < SCAN_MAX_EDGES' conjunct — the CAP's true enforcer (emit_dfa.c's annotation cap is redundant only by construction). The pass then selects every found chain on a >4-chain machine, condemning interior states the emitter will never cover with a loop (and overrunning taken[]), so multi-chain patterns lose matches or the compiler misbehaves outright. Detector: tests/classes/multi_chain.rxt (added with this row — five-segment counted-class patterns, ~10 chain candidates vs the cap's 4, python3-re-verified cells)"
SAB_DOC_FIGURE="PREDICTED at wiring: the multi_chain.rxt cells flip (lost matches on the segments whose chains fall past the emit cap) or the sabotaged compile itself fails on the witness; measured figure recorded by the manager's solo run below this line."
SAB_COUNT=1
SAB_BEFORE='    for (int i = 0; i < nfound && nedges < SCAN_MAX_EDGES; i++) {'
SAB_AFTER='    for (int i = 0; i < nfound /* SABOTAGE S215: cap conjunct dropped */; i++) {'
