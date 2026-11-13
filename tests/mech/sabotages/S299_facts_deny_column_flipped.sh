# S299 — [PATFACTS] step 3.0: ONE FACT'S DENY BIT FLIPPED IN THE TABLE
# (src/facts/facts.def: the `req_pieces` row loses `PCREC_NO_REQ_RUN`;
# re-aimed from the retired `req_run` row, review 2026-11-11 r1 k382 F5,
# lane k382fix: `req_pieces` is read by the listing alone, so the plant
# still moves no emitted byte).
#
# THE DEFECT IT STANDS FOR: the record's deny column disagreeing with what
# the spec says a flag empties. Under the plant `-fno-req-run` leaves the
# piece set derived; nothing but the listing reads it, so no emitted byte
# and no answer moves — but the row now reads `derived` rather than `denied`, i.e. the fact-level deny's CONSUMER LIST (design
# §7.2) silently shrinks. The why-truthfulness check's oracle is
# docs/spec/tuning.md's hand-written "Facts emptied" line, never facts.def's
# own column, which is exactly what makes this row detectable (design §11.6
# check 3, r1 C5: an oracle that shared the column would agree with it).
#
# `facts` (tests/codegen/run_facts_checks.sh, [facts-why]) is its only
# detector.
SAB_ID="S299-facts-deny-column-flipped"
SAB_FILE="src/facts/facts.def"
SAB_SUITES="facts"
SAB_DESC="facts.def's req_pieces row loses its PCREC_NO_REQ_RUN deny bit, so -fno-req-run no longer lists deny:-fno-req-run on req_pieces while tuning.md says it empties it — the why-truthfulness check must fail; no answer and no emitted byte moves"
SAB_DOC_FIGURE="facts:1fail/5pass expected (verified by hand before the solo mech run) — [facts-why] reports -fno-req-run: tuning.md names [req_pieces req_whole_run], the listing denies [req_whole_run] (re-aimed by lane k382fix; re-measure). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S299."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='PF_FACT(REQ_PIECES,    "req_pieces",    2, PF_CORE,    PCREC_NO_REQ_BYTE | PCREC_NO_REQ_RUN,'
SAB_AFTER='PF_FACT(REQ_PIECES,    "req_pieces",    2, PF_CORE,    PCREC_NO_REQ_BYTE /* SABOTAGE S299 */,'
