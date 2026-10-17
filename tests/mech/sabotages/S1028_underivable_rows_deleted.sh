# S1028 — [WINDOW-E1] T-KIND'S `underivable*` ROWS DELETED
# (src/core/findings.c, `find_kind_rows[]`): an answering block whose
# derivation fails falls through to a later row. With the predicates as
# built it lands on `authored-absent` (the `l1none` block is authored), so
# the frequency kind is listed ABSENT — against D162 add. 2, and against the
# note's `underivable-arrives` reading (PRIOR_NONE). (The note predicted the
# fall-through to `measured` with a NULL payload; the built predicates
# require a derivation for `measured`, so the payload invariant is not the
# detector here.)
#
# Detector: run_findings_tests.sh §14 C-E1-1's `l1none/utf8` cell (expected
# underivable-arrives PRESENT/PRIOR_NONE) and its reach floor (the row never
# fires).
SAB_ID="S1028-underivable-rows-deleted"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='find_kind_rows[] loses its two underivable rows, so an underivable answering block falls through to a later T-KIND row'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 C-E1-1 (l1none/utf8; reach: underivable-arrives never fired).'
SAB_REACH='mkdir -p "$REACH_TMP/L1" && printf "%s\n" "analysis l1none" "    cpfreq" "        question q" "        reader r" "        analyzer authored" "        encoding utf8" "        serves byte-rate when utf8 via encode-latin1" "        row U+20AC 7" "        provenance" "            source authored" "            retrieved 2026-09-28" > "$REACH_TMP/L1/l1none.rxt" && "$PCREC" -p rx -e utf8 -I "$REACH_TMP/L1" --analysis l1none -fno-req-byte -o "$REACH_TMP/o.c" --pattern "^abc" && echo REACH-E1-UNDERIVABLE-QUIET'
SAB_REACH_EXPECT="REACH-E1-UNDERIVABLE-QUIET"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "underivable-arrives", fk_undrv_arr,  PCREC_FIND_KIND_PRESENT, PCREC_FIND_SRC_PRIOR_NONE,     false },
    { "underivable",         fk_undrv,      PCREC_FIND_KIND_ABSENT,  PCREC_FIND_SRC_UNSTATED,       false },'
SAB_AFTER='    /* SABOTAGE S1028: the underivable rows deleted */'
