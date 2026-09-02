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
#
# ============ MEASURED 2026-09-02: ONE HUNK IS NOT ENOUGH ============
#
# THE ROW SHIPS AS A TWO-HUNK MUTATION, and the reason is S108's exactly:
# "a one-hunk mutation cannot falsify a defence-in-depth pair". P1 and P2 are
# such a pair, and the lane MEASURED both halves separately before writing
# this row rather than assuming the note's §3.4(a) reachability:
#
#   plant P1 alone (widen to `state_acc_any`):  224 pinned artifacts — the
#     SAME 224 the clean tree produces — and `tests/codegen/
#     run_search_pinned.sh` 17 passed / 0 FAILED. UNDETECTABLE.
#   plant P2 alone (drop the invariance check):  224 again. UNDETECTABLE.
#     That is S220, which ships declared UNDETECTED with its own derivation.
#   plant BOTH:  243 pinned, 19 artifacts flip, and the check goes RED in
#     three independent places — §1's `(?m)a*$` witness, §8's manifest (four
#     of the five shape-anchors ACCEPTED), and §10's ANSWER differential,
#     which reports a real divergence rather than only a stamp move.
#
# WHY ONE HUNK IS INERT, derived rather than observed: `state_acc_any` ORs
# over the CLASS-CONTEXT views (`up[u]`), not over the POSITION views. So the
# two spellings of P1 disagree ONLY on a state whose accept varies by class
# context — and `pcrec_state_view_invariant` refuses exactly those states in
# its `up[u] != up[0]` loop. P2 subsumes the P1 widening. Conversely the
# `(?m)…$` family, which the note names as F3's discriminating population,
# fails P1 in BOTH spellings: its start state accepts only under the EOL
# VIEW, which `state_acc_any` does not see either.
#
# THIS IS A FINDING AGAINST THE NOTE'S §3.4(a), recorded here rather than
# worked around: the widened bit is a miscompile only once P2 is also gone.
# The 16 corpus artifacts memo M2 measured are a fact about `unanch_start`'s
# PREFILTER gate, which has no P2 beside it; they are not a discriminating
# population for THIS predicate.
SAB_ID="S218-pinned-predicate-widened"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="BOTH HALVES of the start-pinned predicate's accept guard are removed together (P1 widened to state_acc_any AND P2 dropped) -- a two-hunk mutation, because each half alone is MEASURED inert. P1 reads state_acc_any (accepts under SOME view) instead of the PLAIN-view accept bit, so a state that accepts only under the EOL/END view is treated as accepting at every position and the reverse pass is elided on it. '\$' over \"abc\" from startpos 0 then reports the span [0,3) where the true span is [3,3): a caps[0][0] that is too small, with the verdict and the match end both still right. MEASURED: 19 corpus artifacts flip from reverse-pass to pinned (224 -> 243)"
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
SAB_AFTER='    /* SABOTAGE S218 hunk 1: P1 reads the WIDENED bit, the one
     * `unanch_start` computes for the prefilter and tells the reader not to
     * cite as a premise. */
    if (!state_acc_any(&fd->st[fs])) return false;'
# THE SECOND HUNK, in the same file. Without it this row is MEASURED inert
# (224 pinned, searchpinned 17/0) — P2 refuses every state on which the two
# spellings of P1 disagree, which is the defence-in-depth pair S108 is about.
SAB_FILE2="src/gen/emit_dfa.c"
SAB_COUNT2=1
SAB_BEFORE2='    /* P2 — one derivation, shared with the scan-edge pass. */
    if (!pcrec_state_view_invariant(&fd->st[fs])) return false;'
SAB_AFTER2='    /* SABOTAGE S218 hunk 2: P2 dropped, so the widened P1 above can
     * actually reach a state whose accept is not invariant. */'
