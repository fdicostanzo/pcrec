# S298 — [PATFACTS] step 3.0: ONE FACT'S DENY BIT FLIPPED IN THE TABLE
# (src/facts/facts.def: the `req_run` row loses `PCREC_NO_REQ_RUN`).
#
# THE DEFECT IT STANDS FOR: the record's deny column disagreeing with what
# the spec says a flag empties. Under the plant `-fno-req-run` still leaves
# the run window EMPTY (it is derived from the denied whole run), so no
# emitted byte and no answer moves — but the window now reads `derived`
# rather than `denied`, i.e. the fact-level deny's CONSUMER LIST (design
# §7.2) silently shrinks. The why-truthfulness check's oracle is
# docs/spec/tuning.md's hand-written "Facts emptied" line, never facts.def's
# own column, which is exactly what makes this row detectable (design §11.6
# check 3, r1 C5: an oracle that shared the column would agree with it).
#
# `facts` (tests/codegen/run_facts_checks.sh, [facts-why]) is its only
# detector.
SAB_ID="S298-facts-deny-column-flipped"
SAB_FILE="src/facts/facts.def"
SAB_SUITES="facts"
SAB_DESC="facts.def's req_run row loses its PCREC_NO_REQ_RUN deny bit, so -fno-req-run no longer lists deny:-fno-req-run on req_run while tuning.md says it empties it — the why-truthfulness check must fail; no answer and no emitted byte moves"
SAB_DOC_FIGURE="facts:1fail/5pass expected (verified by hand before the solo mech run) — [facts-why] reports -fno-req-run: tuning.md names [req_run req_whole_run], the listing denies [req_whole_run]. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S298."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='PF_FACT(REQ_RUN,       "req_run",       2, PF_DERIVED, PCREC_NO_REQ_BYTE | PCREC_NO_REQ_RUN,'
SAB_AFTER='PF_FACT(REQ_RUN,       "req_run",       2, PF_DERIVED, PCREC_NO_REQ_BYTE /* SABOTAGE S298 */,'
