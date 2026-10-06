#!/usr/bin/env bash
# S496 ([START-SET] stage 2; startset.md §3.3, §6.3) -- V's VERB/CALLOUT
# conjunct removed.
#
# DECLARED UNREACHED: `(*COMMIT)` is refused ("outside pcrec's scope") and
# `(?C1)` by module `callouts`, so no tree carries a verb or a callout and the
# conjunct has nothing to read (S475's precedent, one predicate over). The
# plant marks the conjunct's prose; the REACH probe compiles a verb-bearing
# mover, and the day it compiles with the hat this row reads NOW REACHED,
# which is the signal to write the conjunct.
SAB_ID='S496-vmhat-verb-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='V'\''s decline on a backtracking verb or callout is gone; unreachable while the AST has no node kind for either'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(*COMMIT)(ab)\1'\'' && grep -q '\''RX_VM_START_SCAN "first-class"'\'' "$REACH_TMP/o.c" && echo REACH-VERB-VMHAT'
SAB_REACH_EXPECT='REACH-VERB-VMHAT'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='no AST node kind exists for a backtracking verb or a callout: (*COMMIT) is refused as outside pcrec'\''s scope and (?C1) by module callouts before a tree exists, so V cannot be asked about one. The REACH probe compiles (*COMMIT)(ab)\1 and reads NOW REACHED the day it compiles with the VM hat.'
SAB_COUNT=1
SAB_BEFORE=' *   - NO VERB AND NO CALLOUT: a `(*COMMIT)` in a skipped attempt could end'
SAB_AFTER=' *   - [SABOTAGE S496: dropped] NO VERB AND NO CALLOUT: a `(*COMMIT)` in a skipped attempt could end'
