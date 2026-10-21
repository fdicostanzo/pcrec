#!/usr/bin/env bash
# S1194 ([DD-11.5] P2e, lane ctxp2e) -- POSSESSIFY LOSES `\z`'S EXEMPTION:
# first_of's end-pin case falls through to the CONTEXT widen, so a quantifier
# followed by `\z` is no longer possessified (`a+\z`, `[ab]*\z`). Sound (a
# lost optimization, never a lost match), so the detector is the artifact's
# possessification stamp, not an answer. One of the 8 STILL-SPECIAL sites of
# ctx_span.md §4.6 (possessify.c's `\z` transparency).
SAB_ID="S1194-poss-end-pin-widens"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="assertions"
SAB_DESC='possessify widens at \z instead of treating it as transparent'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            return fst_empty(true);
        case CTX_PIN_START:'
SAB_AFTER='            break;   /* SABOTAGE S1194 */
        case CTX_PIN_START:'
