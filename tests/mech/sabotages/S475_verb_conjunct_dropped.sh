#!/usr/bin/env bash
# S475 ([K82] (B), lane k82hbuild) -- THE VERB DECLINE (re-scoped to verbs by [INLINE-C] stage 1b) (litscan_k82h.md §1.4 (g)).
#
# DECLARED UNREACHED: `(*COMMIT)` is refused ("outside pcrec's scope"), so
# no tree ever carries a verb node and the conjunct has nothing to read. The plant marks the conjunct's
# prose; the REACH probe compiles a verb-bearing run pattern, and the day it
# compiles with a handoff this row reads NOW REACHED, which is the signal to
# write the conjunct (S219's precedent).
SAB_ID="S475-verb-conjunct-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the handoff'\''s (g) decline on a backtracking verb is gone (the callout half was retired by [INLINE-C] stage 1b, inline_c.md §1.8 D4); unreachable while the AST has no node kind for a verb'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until a verb compiles.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern '\''(*COMMIT)abc'\'' && grep -q '\''size_t handoff_position'\'' "$REACH_TMP/o.c" && echo REACH-VERB-HANDOFF'
SAB_REACH_EXPECT='REACH-VERB-HANDOFF'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no AST node kind exists for a backtracking verb: (*COMMIT) is refused as outside pcrec'\''s scope before a tree exists (a callout compiles since [INLINE-C] stage 1b, and is no longer this conjunct'\''s: inline_c.md §1.8 D4), so the handoff predicate cannot be asked about one. The REACH probe compiles (*COMMIT)abc and expects a handoff; it fails today by refusal.'
SAB_COUNT=1
SAB_BEFORE=' *   - (g) NO VERB: a `(*COMMIT)` in a failed attempt below the scan start'
SAB_AFTER=' *   - (g) [SABOTAGE S475: dropped] NO VERB: a `(*COMMIT)` in a failed attempt below the scan start'
