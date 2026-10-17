# S1029 — [WINDOW-E1] T-KIND'S `authored` ROW LOSES ITS `unmeasured =
# ARRIVES` CONJUNCT (src/core/findings.c, `fk_authored`): an authored block
# answering a MEASURED-ONLY kind would be listed PRESENT/PRIOR_AUTHORED,
# where D162 add. 2 keeps every kind but the frequency one ABSENT unless
# measured.
#
# UNREACHED until [FINDINGS] B4 gives `run-rarity` a payload shape: today the
# only shaped kind (byte-rate) ARRIVES, so the conjunct cannot change an
# answer. Then a user `-I` bundle with an authored `bigram` block reaches it,
# and §14 C-E1-1 gains that cell (expected ABSENT via authored-absent).
SAB_ID="S1029-authored-loses-arrives"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='fk_authored drops its f->arrives conjunct, so an authored block answering a kind whose unmeasured column is ABSENT would be listed PRESENT'
SAB_DOC_FIGURE='UNREACHED (declared): no shaped MEASURED-ONLY kind exists before [FINDINGS] B4.'
SAB_REACH='grep -Eq "\"run-rarity\", [1-9]" "$TREE/src/core/findings.c" && echo REACH-E1-SHAPED-MEASURED-ONLY-KIND'
SAB_REACH_EXPECT="REACH-E1-SHAPED-MEASURED-ONLY-KIND"
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no find_queries[] row other than byte-rate has a payload shape before [FINDINGS] B4, and byte-rate'\''s unmeasured column is ARRIVES, so the dropped conjunct is true on every reachable cell; the reach probe requires run-rarity'\''s payload version > 0 (window_contract.md §3.7.8 S1029)'
SAB_COUNT=1
SAB_BEFORE='static bool fk_authored(const FindKindFacts *f)  { return f->answers && f->derives && f->prior && f->arrives; }'
SAB_AFTER='static bool fk_authored(const FindKindFacts *f)  { return f->answers && f->derives && f->prior; }   /* SABOTAGE S1029 */'
