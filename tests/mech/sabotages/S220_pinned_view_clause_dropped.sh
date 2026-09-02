# S220 ([OPT-5] STEP 2) — P2'S VIEW/CONTEXT CLAUSE IS DROPPED: the elision no
# longer requires the start state's accept to be INVARIANT.
#
# WHAT IT BREAKS. P2 is the second half of "the start state accepts
# UNCONDITIONALLY": not merely that it accepts under the plain view, but that
# its accept does not vary with WHERE the position is (`eolvar`/`endvar`, the
# `$`/`\Z`/`\z` views) or with WHAT COMES NEXT (`up[u]`, the class-context
# axis `\b` and `(?m)$` read). `pcrec_state_view_invariant` is that predicate,
# shared with `src/opt/scanedge.c`'s own precondition (3) — one derivation,
# two readers — and this plant makes the axis-J caller stop consulting it.
#
# THE FAILURE MODE. A state whose accept holds only at some positions is
# treated as accepting at all of them, so the elision fires on a machine that
# does NOT have a match at every `search_from` and writes `caps[0][0] =
# search_from` where the true match begins later. The span is too wide at the
# front: the verdict and the match END stay right, and only the reported start
# moves — the quiet direction again.
#
# ITS DISJOINTNESS FROM S218 IS OWED AND IS ARGUED HERE RATHER THAN ASSUMED
# (the design note's §7 item 13, and the S79/S80 rule). The two plants edit
# DIFFERENT CLAUSES of the same predicate and their populations are NOT the
# same:
#
#   - S218 widens P1 and is discriminated by the `(?m)…$` family, where the
#     start state does NOT accept under the plain view but DOES under the EOL
#     view. Those artifacts fail P1 first; P2 is never reached on them.
#   - S220 drops P2 and is discriminated by a state that DOES accept under the
#     plain view and whose accept VARIES — the `classctx` family, `\bx*` and
#     relatives, which M1 counted at 8 corpus artifacts. S218 leaves every one
#     of those DECLINED, because P1 passes on them and P2 is what refuses.
#
# So `\bx*` is the member of S220's population that S218's plant does NOT
# catch, and it is a NAMED witness in `tests/codegen/run_search_pinned.sh` §1
# for exactly that reason. The two rows are not redundant.
#
# A POPULATION OF 8 IS THIN, so it is FLOORED FROM BIRTH rather than watched
# ([MECH-REACH]; and [OPT-VEDGE] relaxes the same view precondition from the
# other side, which is what the S206/[OPT-4.2] lesson says will move it).
SAB_ID="S220-pinned-view-clause-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="The start-pinned predicate's P2 stops asking whether the start state's accept is invariant in position and in class context, so a state that accepts only at some positions is treated as accepting at all of them. The elision then fires on a machine that has no match at every search_from and writes caps[0][0] = search_from where the true match begins later -- a span too wide at the front, with the verdict and the match end both still right"
SAB_DOC_FIGURE="PREDICTED (the canonical DETECTED figure is owed from the manager's own matrix run): searchpinned RED in §1 (the '\\bx*' and '(?m)a*\$' witnesses stamp \"pinned\") and in §8; harness RED on the classctx cells that carry capture lines. Its disjointness from S218 is argued in this header: '\\bx*' passes P1 and is refused by P2 alone, so S218's plant leaves it DECLINED."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `\bx*`
# is DECLINED, and it is declined at P2 rather than P1 (its start state DOES
# accept under the plain view — a bare `x*` is nullable — so P1 passes). THE
# FLOOR says the classctx population still exists.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "\bx*" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/p.c" -- "x*" && grep -q "RX_DFA_START \"pinned\"" "$REACH_TMP/p.c" && echo REACH-CLASSCTX-DECLINED-BY-P2'
SAB_REACH_EXPECT="REACH-CLASSCTX-DECLINED-BY-P2"
SAB_REACH_POP="docs/dev/opt5m2_m2_changed_patterns.txt|^\(\?m|12"
SAB_COUNT=1
SAB_BEFORE='    /* P2 — one derivation, shared with the scan-edge pass. */
    if (!pcrec_state_view_invariant(&fd->st[fs])) return false;'
SAB_AFTER='    /* SABOTAGE S220: P2 is dropped -- the accept no longer has to be
     * invariant in position or in class context. */'
