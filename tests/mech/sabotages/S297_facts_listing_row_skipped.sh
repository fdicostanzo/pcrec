# S297 — [PATFACTS] step 3.0: THE `--emit-facts` PRINTER SKIPS A FACT
# (src/dump/facts_dump.c: the `req_set` row is never printed).
#
# THE DEFECT IT STANDS FOR: "populations nobody counts" (K35) inside the
# record's own inspection surface — a fact the record HAS that the listing
# silently does not show, so a reader concludes the compiler never computed
# it. The completeness check's expected count is the PLAIN-TEXT row count of
# src/facts/facts.def, never the X-macro expansion the printer iterates, so
# the printer dropping a row cannot also drop it from the expectation
# (design §11.6 check 2, r1 C4).
#
# NOT ANSWER-DETECTABLE: the plant is in the listing, not the compiler; no
# artifact byte moves. `facts` (tests/codegen/run_facts_checks.sh,
# [facts-complete]) is its only detector.
SAB_ID="S297-facts-listing-row-skipped"
SAB_FILE="src/dump/facts_dump.c"
SAB_SUITES="facts"
SAB_DESC="the --emit-facts printer skips the req_set row, so the listing shows 5 facts per encoding where facts.def declares 6 — the completeness check must fail; no artifact byte moves"
SAB_DOC_FIGURE="facts:2fail/4pass expected (verified by hand before the solo mech run) — [facts-complete] reports 10 facts rows for 2 encodings where facts.def has 6 rows, and [facts-why] reports -fno-req-byte denying three of the four facts tuning.md names (the skipped req_set row is missing from the listing, so the claim cannot be read off it either). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S297."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int f = 0; f < PF_NFACTS; f++) {
        const char *cells[9];'
SAB_AFTER='    for (int f = 0; f < PF_NFACTS; f++) {
        const char *cells[9];
        if (f == PF_REQ_SET) continue;   /* SABOTAGE S297: a row is never printed */'
