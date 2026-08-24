/* mod_assertions.c — module `assertions` ([M6.2]), WAVE A: the three
 * absolute-position escapes `\A`, `\Z` and `\z`, as one shared atom producer.
 *
 * WHICH ESCAPE dispatched here is read off the ELECTED ROW's own `sel`
 * (registry.c's rows for this module), the shape mod_named_groups.c uses for
 * its three declaring spellings and for the same reason: three near-identical
 * hand copies of a rule drift the same way three near-identical hand copies of
 * a module attribution did (the `\v` bug this registry exists to prevent).
 *
 * TWO OF THE THREE ARE EXACT ALIASES OF NODES pcrec HAS SHIPPED SINCE M1, and
 * that is the cheapest finding in the whole module (assertions_design.md
 * §3.2). pcrec's own node comments already state PCRE2's `\A` and `\Z`
 * semantics word for word:
 *
 *     A_BOL   "assert start of subject"                          == PCRE2 \A
 *     A_EOL   "assert end-of-subject or before-final-\n"          == PCRE2 \Z
 *
 * so `\A` lowers to A_BOL, `\Z` lowers to A_EOL, and NO ENGINE WORK EXISTS
 * for either — no closure bit, no table, no VM arm, no emitter branch. The
 * design lane measured the alias claim rather than reading it off the
 * comments: a 1,008-cell differential against libpcre2 at zero
 * disagreements. They are parser rows.
 *
 * `\z` IS NOT ONE OF THEM. "End of subject, full stop" is STRICTLY STRONGER
 * than `\Z`, and the position where they differ is the whole point:
 *
 *     position                        $ / \Z     \z
 *     interior                        no         no
 *     pos + 1 == n && s[pos] == '\n'  YES        no
 *     pos == n                        YES        YES
 *
 * It gets its own AST kind (`A_END`), its own NFA state kind (`N_END`), a
 * third closure view in src/ir/dfa.c and a third position view in both
 * emitters. D62's principle is what makes that the right spelling rather than
 * a flag: node KINDS encode STRUCTURE and node FIELDS encode parse-resolved
 * MODIFIER STATE, and no option turns `\Z` into `\z`.
 *
 * INDEPENDENT OF MULTILINE, AND OF NOTBOL/NOTEOL. PCRE2's `\A`, `\Z` and
 * `\z` "only ever match at the very start and end of the subject string,
 * whatever options are set" (pcre2pattern), which has two consequences this
 * port is responsible for and which are written out at the code below rather
 * than only here: `Ast.u.anch.multiline` is PINNED FALSE (never copied from the
 * scoped state, which is what `^`/`$` do), and the alias is exact AT
 * options = 0 while `PCRE2_NOTBOL`/`PCRE2_NOTEOL` — API-PARAM, RATIFIED D38 —
 * are a committed future surface that will need to tell a `\A` node from a
 * `^` one, which the alias erases.
 *
 * THE ORACLE TRAP, stated here because a test author will hit it before they
 * read the design note (§3.2.1, MEASURED both oracles): **python `re`'s `\Z`
 * IS PCRE2's `\z`.** python has no single escape for PCRE2's `\Z` at all —
 * `(?=\n?\Z)` is the only spelling and it needs lookahead. The disagreement
 * is in the silent direction: python reports NO MATCH exactly where PCRE2
 * matches (`b\Z` on "ab\n" is (1,2) in PCRE2 and None in python), so a `.rxt`
 * cell for `\Z` derived from python would encode `\z` and go green on a
 * miscompile. `\Z` expectations in tests/assertions/ are libpcre2-verified
 * and the blocks carry `# pcre2-only`.
 *
 * NOT REPEATABLE, and inherited rather than restated: `\A*` `\z*` `\Z*` are
 * all PCRE2 error 109 while `(\z)*` compiles (measured against libpcre2
 * 10.46, this lane). A_BOL and A_EOL are already in parse.c's bare-quantified
 * rejection and in the bare-anchor group wrap; A_END joined both, so all
 * three spellings get the base grammar's own answer with no rule of this
 * module's own. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

ExtResult pcrec_asrtport_atom(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from)
{
    AKind k;
    switch (rw->sel) {
    case 'A': k = A_BOL; break;   /* \A — the alias, §3.2 */
    case 'Z': k = A_EOL; break;   /* \Z — the alias, §3.2 */
    case 'z': k = A_END; break;   /* \z — the one that needs a machine */
    /* [M6.2 wave B] the word-boundary pair, and they need the OTHER kind of
     * machine: `\A`/`\Z`/`\z` are questions about the POSITION, answerable by
     * an integer compare, while these are questions about the two BYTES
     * around it. That is what buys the alphabet refinement, the context bit
     * in the DFA state identity and the class-indexed accept — see
     * src/ir/dfa.c. Two kinds rather than one plus a negation flag, on D62's
     * principle: no option turns `\b` into `\B`, so the distinction is
     * structure. */
    case 'b': k = A_WORDB; break;
    case 'B': k = A_NWORDB; break;
    /* [M6.2 wave D] `\G`, and it is a THIRD kind of question again. `\A`/
     * `\Z`/`\z` compare the position against a COMPILE-TIME constant (0, n,
     * n-1); `\b`/`\B` read the two bytes around it; `\G` compares it against
     * a RUNTIME value the match call supplies — `<prefix>_search`'s own
     * `startpos` parameter (docs/spec/match_api.md §3.1). That is why it
     * costs a closure bit and a second family of start states in src/ir/dfa.c
     * and nothing at all in the alphabet: it reads no byte. */
    case 'G': k = A_GSTART; break;
    /* [M6.2 wave E] `\K`, and it is not a question at all. Every kind above
     * this line ASKS something about the position and can answer no; `\K`
     * always succeeds, reads nothing and WRITES — it moves the reported start
     * of the match to here. That is the whole of assertions_design.md §6, and
     * it is why this is the one construct in the module with no DFA path:
     * the position it reports belongs to the WINNING PATH, and a subset state
     * is a set, not a path.
     *
     * THE OFFSET IS RECORDED HERE AND NOWHERE ELSE. `src/opt/select_engine.c`
     * decides the engine by WALKING for an A_KRESET node (the honest
     * question), but the stamp it writes wants a pattern offset and no AST
     * node carries one. `cx->first_cap_pos` is the precedent, field for field,
     * including the first-wins guard: the diagnostic names the FIRST `\K`,
     * not the last one parsed. */
    case 'K':
        k = A_KRESET;
        break;
    default:
        /* Unreachable on the shipped table; a registry defect if it ever
         * fires, reported rather than silently compiled as something else. */
        REFUSE(at, "internal error: module 'assertions' dispatched on an "
                   "unexpected escape selector");
    }

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    /* [M6.5.2] `end` reported explicitly: every construct this port produces
     * IS the two-byte escape, so it is `cx->pos` — but `esc_atom` now
     * ADVANCES to whatever a producer reports rather than assuming that, since
     * module `backrefs` has atom constructs of its own that are longer
     * (`\k<name>`, `\g{-1}`). Leaving it zero would rewind the cursor to the
     * start of the pattern. */
    res.end = cx->pos;
    res.node = pcrec_ast_node(cx, k);
    /* [M6.4.2 / SR-8, D67] THE STAMP, applied UNIFORMLY to all eight rows
     * rather than to `\K` alone, so "this module's producer stamps what it
     * builds" is a property of the port rather than a per-row exception a
     * future row could be forgotten from. Seven of the eight rows are
     * ANY_ENGINE and contribute nothing to the pattern-wide AND; `\K`'s is
     * VM_ONLY and is what `forces_registry` (src/opt/select_engine.c) reads.
     *
     * IT ALSO REPLACES `Ctx.first_kreset_pos`, which used to be recorded in
     * the `'K'` case above: `pcrec_ast_stamp` records the offset for any
     * DFA-excluding row, first-wins, in the same statement that writes the
     * row — so the `engine_why` text and its offset come from one place. The
     * old field's own comment ("read ONLY when the walk already found a node,
     * so it cannot be stale in the direction that matters") carries over
     * verbatim and is restated at `Ctx.first_vmonly_pos`. */
    pcrec_ast_stamp(cx, res.node, rw, at);

    /* MULTILINE IS PINNED FALSE HERE, DELIBERATELY AND EXPLICITLY — never
     * copied from `cx->mods` the way parse.c's `^`/`$` cases copy it.
     *
     * PCRE2's own words (pcre2pattern, "Simple assertions"): `\A`, `\Z` and
     * `\z` "only ever match at the very start and end of the subject string,
     * whatever options are set. Thus, they are independent of multiline
     * mode." `(?m)\Z` is still the subject end (or before a final newline);
     * `(?m)$` is before EVERY newline. The two spellings produce the SAME
     * node kind and must carry DIFFERENT values in this field.
     *
     * The arena already zeroes it, so this assignment changes no bit today —
     * it is written out because the failure it forecloses is a wave-C one and
     * is invisible until then. `(?m)` is refused now, so a version of this
     * port that copied `cx->mods` would be indistinguishable from this one by
     * every test in the tree; the day wave C accepts the `m` letter, that
     * version would leak multiline-`$` machinery into `\Z` silently. This
     * line and this comment exist so the next author cannot "harmonize" the
     * two sites, which is exactly the harmonization that would break it.
     *
     * [D70] GUARDED ON THE KIND. This port produces EIGHT kinds and only two
     * of them own `u.anch` — the pin ran for A_END, A_WORDB, A_NWORDB,
     * A_GSTART and A_KRESET too. Today that aliases nothing, because those
     * five kinds have no payload of their own; the day any of them gains one
     * it becomes a silent clobber of it, and nobody will re-read this line
     * then. The guard costs nothing, changes no bit today, and is what the
     * union's discipline (see the union in src/core/internal.h) requires of
     * every writer: touch `u.<payload>` only under a kind check that owns
     * it. */
    if (k == A_BOL || k == A_EOL)
        res.node->u.anch.multiline = false;

    /* THE ALIAS IS EXACT AT options = 0, AND THE FUTURE HAS ONE KNOWN
     * CONSUMER OF WHAT IT ERASES. `PCRE2_NOTBOL`/`PCRE2_NOTEOL` affect `^`
     * and `$` ONLY — `\A`/`\Z`/`\z` are unaffected — and both are RULED
     * `API-PARAM` (docs/pcre2_options.md rows 200-201, RATIFIED D38): a
     * match-CALL parameter, i.e. a committed future surface, not a NEVER.
     *
     * MEASURED against libpcre2 10.46 by this lane, since the distinction is
     * the whole point and a documentation paragraph is not a measurement:
     *
     *     pattern  subject   options=0   NOTBOL     NOTEOL
     *     ^a       "ab"      (0,1)       NO MATCH   (0,1)     <- affected
     *     \Aa      "ab"      (0,1)       (0,1)      (0,1)     <- not
     *     b$       "ab"      (1,2)       (1,2)      NO MATCH  <- affected
     *     b\Z      "ab"      (1,2)       (1,2)      (1,2)     <- not
     *     b$       "ab\n"    (1,2)       (1,2)      NO MATCH  <- affected
     *     b\Z      "ab\n"    (1,2)       (1,2)      (1,2)     <- not
     *
     * An artifact is compiled ONCE and that parameter arrives at MATCH time,
     * so the emitter will have to know which A_BOL nodes came from `\A` and
     * which from `^` — information a pure alias throws away. The fix, when it
     * has a customer, is a PARSE-RESOLVED PROVENANCE FIELD in D62's shape
     * (kinds encode structure, fields encode parse-resolved state), written
     * exactly here beside `multiline`.
     *
     * IT IS NOT BUILT NOW, and that is the house rule rather than laziness: a
     * field with no consumer has no test that can go red, and unpopulated
     * machinery guessed at sample size zero is what D18/OS-0/D53 forbid (and
     * what [M4.7a] declined SR-8's socket over). What is owed today is that
     * the requirement be RECORDED where the erasure happens — here, and as an
     * annotation on assertions_design.md §3.2, whose alias claim is silent on
     * it. */

    /* `\A`/`\Z`/`\z` are two-byte escapes and the doorway's cursor already
     * sits past both bytes, exactly as it does for the PORT_SCALAR rows.
     * The CALLER advances (check06's rule); the doorway never does. */
    res.end = from;
    return res;
}
