# S84 — [M6.2 WAVE D] `\G` TAKES `\z`'s POSSESSIFICATION EXEMPTION INSTEAD OF
# `\A`'s DECLINE.
#
# D47.5's `$`-follow exemption rests on UPWARD CLOSURE: if the assertion fails
# at a quantifier's maximal exit it fails at every smaller retreat position
# too, so no retreat can rescue a match and possessifying loses nothing. `\z`
# takes it with no gate at all — its satisfying set is the singleton `{n}`,
# which is the sharpest possible version of the argument (wave A).
#
# `\G` LOOKS LIKE `\z` AND BEHAVES LIKE `\A`, and that is the whole content of
# this row. Its satisfying set is a singleton too — `{startpos}` — so the
# "singleton, therefore exempt" reading is available and wrong: a singleton is
# only safe when it sits ABOVE every retreat position. `\z`'s does, at `n`.
# `\G`'s sits BELOW every retreat position, at the very offset the quantifier
# started from, so `\G` is DOWNWARD-closed exactly like `\A` and a retreat CAN
# reach a position satisfying it from one that does not.
#
# MEASURED, and it is a lost match rather than a slow pattern:
#
#     (x)?a{0,4}\G   on "aaaa"
#         libpcre2:               (0,0) at startpos 0, (2,2) at startpos 2
#         shipped pcrec:          (0,0) / (2,2), RX_VM_STRATS 0x2 (backtracking)
#         with \z's arm:          NO MATCH at either, RX_VM_STRATS 0x1
#
# because possessified, the loop consumes every `a`, `\G` fails at the maximal
# exit, and the retreat to `startpos` — the only route to the correct empty
# match — has been proved dead by an argument that does not hold here.
#
# THIS IS D47.5's OWN FAILURE MODE, ONE CONSTRUCT OVER, which is why the row
# exists rather than being covered by S77 (the multiline flag-reader). S77
# guards the analysis reading the WRONG SOURCE for a fact; this one guards it
# reaching the wrong CONCLUSION from the right source. `tests/assertions/`'s
# STRATS check is the instrument, because a possessified quantifier and a
# backtracking one match identically on every pattern where the verdict is
# CORRECT — so no `.rxt` corpus can see the verdict, only the artifact's stamp
# can, and only a pattern where the verdict is WRONG shows up in answers.
SAB_ID="S84-gstart-takes-end-exemption"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="assertions harness"
SAB_HARNESS_TARGET="tests/assertions/gpos.rxt"
SAB_DESC="\\G takes \\z's transparent (exempt) arm in first_of instead of \\A's widen-and-decline, on the false reading that a singleton satisfying set is enough. It is not: \\z's singleton is at n (above every retreat) and \\G's is at startpos (below every retreat), so possessification deletes the retreat that is the only route to the match — '(x)?a{0,4}\\G' on \"aaaa\" answers NO MATCH where libpcre2 gives (0,0)"
SAB_DOC_FIGURE="tests/assertions/run_assertions_tests.sh's STRATS row for '(x)a{0,4}\\G' reads 0x1 instead of 0x2"
SAB_COUNT=1
SAB_BEFORE='    case A_GSTART:
        /* [M6.2 wave D] WIDEN AND DECLINE'
SAB_AFTER='    case A_GSTART:
        return fst_empty(true);   /* SABOTAGE S84 */
        /* [M6.2 wave D] WIDEN AND DECLINE'
