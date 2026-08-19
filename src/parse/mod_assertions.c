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
    default:
        /* Unreachable on the shipped table; a registry defect if it ever
         * fires, reported rather than silently compiled as something else. */
        REFUSE(at, "internal error: module 'assertions' dispatched on an "
                   "unexpected escape selector");
    }

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = pcrec_ast_node(cx, k);
    /* `Ast.multiline` IS DELIBERATELY LEFT AT THE ARENA'S ZERO, and that is
     * the alias claim's fine print rather than an omission. PCRE2's `\A` and
     * `\Z` are "unaffected by multiline" — `(?m)\Z` still means the subject
     * end (or before a final newline), where `(?m)$` means before EVERY
     * newline. So the node these two produce is an A_BOL/A_EOL that is
     * PERMANENTLY non-multiline, while parse.c's `^`/`$` cases copy the
     * scoped state in force. Both write the same field and they must write
     * different values; the zero is the right one here and setting it from
     * `cx->mods` would be the bug. */
    /* `\A`/`\Z`/`\z` are two-byte escapes and the doorway's cursor already
     * sits past both bytes, exactly as it does for the PORT_SCALAR rows.
     * The CALLER advances (check06's rule); the doorway never does. */
    res.end = from;
    return res;
}
