# S218 ([OPT-5] STEP 2) — THE START-PINNED PREDICATE'S P1 IS WIDENED FROM THE
# PLAIN-VIEW ACCEPT BIT TO "ACCEPTS UNDER SOME VIEW".
#
# WHAT IT BREAKS. Axis J elides `<prefix>_search`'s whole reverse pass on a
# machine whose forward START STATE ACCEPTS UNCONDITIONALLY — at every
# position, under every position view, in every class context. P1 is the first
# half of that and it reads the state's PLAIN-view accept bit. The neighbouring
# `unanch_start` computes a DIFFERENT bit for a DIFFERENT consumer —
# `state_acc_any`, "accepts under SOME view" — and its own comment calls that
# widening BELT-AND-BRACES and instructs the reader NOT TO CITE IT AS A
# PREMISE. This plant cites it anyway.
#
# THE FAILURE MODE IS A SILENT MISCOMPILE OF THE QUIETEST AVAILABLE KIND: a
# `caps[0][0]` that is TOO SMALL. `$` is the emitter's own named
# counter-example — it never leaves the start state and
# `forward_is_accepting[fs]` is 0, but its EOL variant accepts — so on `"abc"`
# from startpos 0 the true span is [3,3) and the widened predicate reports
# [0,3). Nothing crashes, nothing is lost, and the match/no-match verdict is
# right in every cell; only the reported START moves, which is the field
# docs/dev/learnings.md §3 records as blind twice of three.
#
# THE DISCRIMINATING POPULATION IS THE `(?m)…$` FAMILY and it is a real one:
# sixteen corpus artifacts change under this edit at this tree
# (docs/dev/opt5m2_m2_changed_patterns.txt), every one of them a
# multiline-EOL shape. `tests/codegen/run_search_pinned.sh` §8 asserts them
# ALL-AND-ONLY declined and names five shape-anchors; this row's own
# `SAB_REACH_POP` floors the file that holds them, because a probe and a
# population are different claims that expire separately ([MECH-REACH]).
#
# WHY THE `harness` ARM IS THE RIGHT SECOND DETECTOR. The corpus's `(?m)…$`
# cells carry `g` capture lines, so a moved `caps[0][0]` is a moved answer
# there even at startpos 0 — unlike S221's absolute-offset trap, which the
# corpus structurally cannot see.
SAB_ID="S218-pinned-predicate-widened"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="The start-pinned search's P1 reads state_acc_any (accepts under SOME view) instead of the PLAIN-view accept bit, so a state that accepts only under the EOL/END view is treated as accepting at every position and the reverse pass is elided on it. '\$' over \"abc\" from startpos 0 then reports the span [0,3) where the true span is [3,3): a caps[0][0] that is too small, with the verdict and the match end both still right"
SAB_DOC_FIGURE="PREDICTED (the canonical DETECTED figure is owed from the manager's own matrix run): searchpinned RED in §1 (the '\$' and '(?m)a*\$' witnesses stamp \"pinned\"), in §8 (every shape-anchor is ACCEPTED where all five must be DECLINED) and in §10 (the '\$' and '(?m)a*\$' differentials diverge on caps[0][0]); harness RED on the (?m) cells that carry capture lines."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `$`
# compiles to an artifact the predicate DECLINES, which is the verdict this
# plant inverts. THE FLOOR says the WITNESS ROWS still exist.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "$" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && echo REACH-DOLLAR-DECLINED'
SAB_REACH_EXPECT="REACH-DOLLAR-DECLINED"
SAB_REACH_POP="docs/dev/opt5m2_m2_changed_patterns.txt|^\(\?m|12"
SAB_COUNT=1
SAB_BEFORE='    /* P1 — the NARROWED read. */
    if (!fd->st[fs].up[UPC_PLAIN].accept) return false;'
SAB_AFTER='    /* SABOTAGE S218: P1 reads the WIDENED bit, the one `unanch_start`
     * computes for the prefilter and tells the reader not to cite. */
    if (!state_acc_any(&fd->st[fs])) return false;'
