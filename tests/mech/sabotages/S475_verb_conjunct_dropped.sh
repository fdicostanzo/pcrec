#!/usr/bin/env bash
# S475 ([K82] (B), lane k82hbuild) -- THE VERB/CALLOUT DECLINE (litscan_k82h.md §1.4 (g)).
#
# DECLARED UNREACHED: `(*COMMIT)` is refused ("outside pcrec's scope") and
# `(?C1)` by module `callouts`, so no tree ever carries a verb or a callout
# node and the conjunct has nothing to read. The plant marks the conjunct's
# prose; the REACH probe compiles a verb-bearing run pattern, and the day it
# compiles with a handoff this row reads NOW REACHED, which is the signal to
# write the conjunct (S219's precedent).
SAB_ID="S475-verb-conjunct-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the handoff'\''s (g) decline on a backtracking verb or callout is gone; unreachable while the AST has no node kind for either'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until a verb or callout compiles.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern '\''(*COMMIT)abc'\'' && grep -q '\''size_t handoff_position'\'' "$REACH_TMP/o.c" && echo REACH-VERB-HANDOFF'
SAB_REACH_EXPECT='REACH-VERB-HANDOFF'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no AST node kind exists for a backtracking verb or a callout: (*COMMIT) is refused as outside pcrec'\''s scope and (?C1) by module callouts before a tree exists, so the handoff predicate cannot be asked about one. The REACH probe compiles (*COMMIT)abc and expects a handoff; it fails today by refusal.'
SAB_COUNT=1
SAB_BEFORE=' *   - (g) NO VERB AND NO CALLOUT: a `(*COMMIT)` in a failed attempt below the'
SAB_AFTER=' *   - (g) [SABOTAGE S475: dropped] NO VERB AND NO CALLOUT: a `(*COMMIT)` in a failed attempt below the'
