# S-U8 ([M5.0] stage 2; utf8_design.md §8.2, RE-AIMED AS BUILT) -- THE MRL
# BOUND UNDER UTF8 STOPS COUNTING ENCODED BYTES.
#
# THE DESIGN'S FORM OF THIS ROW IS A NO-OP AS BUILT, AND THE REASON IS THE
# BUILD BEING MORE GENERAL THAN THE DESIGN. §8.2 asks to sabotage a per-class
# encoded-length arm in `pcrec_minw` ("return the old constant 1") — but no
# such arm was built: §5.6.1's exactness arrives through the LOWERING instead
# (the emitter's follow-min walks the LOWERED tree, where a two-byte character
# is an A_CAT of two byte classes and the constant-1 arm is exact per BYTE
# class), so `pcrec_minw`'s A_CLASS arm legitimately still reads 1 and the
# designed edit changes nothing. The claim survives; its sabotage moves to
# the mechanism that now carries it.
#
# THE SABOTAGE adds a matches-nothing branch (an EMPTY class) to every
# multi-byte class's lowered alternation. The LANGUAGE is untouched — an
# empty class has no path — but `pcrec_minw` charges every A_CLASS 1, so the
# alternation's minimum drops to 1, the lowered body stops being the
# fixed-stride shape the cursor rung wants, and the emitted MRL/rung
# machinery moves — `(a)(?:\x{3b1}){0,3}x` loses its
# `RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)` (the stride 2 IS the encoded
# length) and its `RX_VM_RUNGS` stamp changes. NO ANSWER MOVES ANYWHERE (a
# looser bound prunes less, never more), no byte-axis instrument can see it
# (utf8-only), and the corpus is structurally blind — which is §8.2's whole
# point for this row: the detector is the STAMP-READING check (check 3 /
# run_encoding_checks.sh's clamp-stride probe), not any answer.
SAB_ID="S-U8-mrl-bound-loosened-utf8"
SAB_FILE="src/opt/lower_enc.c"
SAB_SUITES="codegen encoding"
SAB_DESC="the utf8 lowering adds a matches-nothing empty-class branch to every multi-byte class's alternation; the language is identical, every answer is identical, and the emitted MRL prune bound quietly loosens from the true encoded byte count — only a bound-reading check sees it"
SAB_DOC_FIGURE="PREDICTED: 0 corpus failures, 0 identity-gate failures, and run_encoding_checks.sh's clamp-stride probe RED ((a)(?:\x{3b1}){0,3}x stops emitting RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2) — the stride-2 clamp that proves the bound counts ENCODED bytes — and its RX_VM_RUNGS stamp moves). DEMONSTRATED at stage 2: the clamp literal present clean, absent sabotaged, answers identical on every subject tried. [ENCCHK-DD12A], 2026-09-06: the prediction is now a SCORED arm (the encoding suite word, newly wired) rather than an unfulfilled claim in this header — see docs/dev/lanes/encchk_report.md for the solo-run transcript against a green baseline."
SAB_REACH='"$PCREC" -e utf8 -p rx -o - -- "(a)(?:\x{3b1}){0,3}x" | grep -o "RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)" | head -1'
SAB_REACH_EXPECT='RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)'
SAB_REACH_POP='tests/codegen/run_encoding_checks.sh|RX_PRUNE_CLAMP_SPAN|1'
SAB_COUNT=1
SAB_BEFORE='            if (bl.n > 1) {
                Ast *seal = pcrec_ast_node(lc->cx, A_CAT);
                seal->l = pcrec_ast_node(lc->cx, A_EMPTY);
                seal->r = res;
                res = seal;
            }
            return res;'
SAB_AFTER='            {   /* SABOTAGE S-U8: a matches-nothing branch — language
                 * identical, minw of the alternation loosened to 1 */
                Ast *alt = pcrec_ast_node(lc->cx, A_ALT);
                Ast *dead = pcrec_ast_node(lc->cx, A_CLASS);
                PcrecCpSet ds;
                pcrec_cpset_init(&ds, &lc->cx->arena);
                pcrec_cpset_publish(&ds, dead);
                alt->l = res; alt->r = dead; res = alt;
            }
            {
                Ast *seal = pcrec_ast_node(lc->cx, A_CAT);
                seal->l = pcrec_ast_node(lc->cx, A_EMPTY);
                seal->r = res;
                res = seal;
            }
            return res;'
