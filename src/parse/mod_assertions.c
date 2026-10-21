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
 *     `^`     "assert start of subject"                          == PCRE2 \A
 *     A_EOL   "assert end-of-subject or before-final-\n"          == PCRE2 \Z
 *
 * so `\A` builds `^`'s node (since [DD-11.5] P2e the SUBJECT_START context
 * row, `pcrec_ast_pin`), `\Z` builds A_EOL, and NO ENGINE WORK EXISTS
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
 * It gets its own node, the context row `SUBJECT_END` (src/core/ctxfn.def,
 * the end PIN; the AST kind `A_END` until [DD-11.5] P2e, the NFA kind
 * `N_END` until P2d), a third closure view in src/ir/dfa.c and a third
 * position view in both emitters. D62's principle is what makes that the
 * right spelling rather than a flag on `$`: no option turns `\Z` into `\z`,
 * so they are two nodes, and the row's CLASS (`CTX_PIN_END`) is the
 * structure every analysis that must decide about `\z` switches on.
 *
 * INDEPENDENT OF MULTILINE, AND OF NOTBOL/NOTEOL. PCRE2's `\A`, `\Z` and
 * `\z` "only ever match at the very start and end of the subject string,
 * whatever options are set" (pcre2pattern), which has two consequences this
 * port is responsible for and which are written out at the code below rather
 * than only here: no multiline state reaches these nodes (`(?m)` changes
 * which node `^`/`$` build, never `\A`/`\Z`), and the alias is exact AT
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
 * 10.46, this lane). `^` and A_EOL are already in parse.c's bare-quantified
 * rejection and in the bare-anchor group wrap; `\z` joined both (since P2e
 * through the pin's `u.ctx.anchor`), so all three spellings get the base
 * grammar's own answer with no rule of this module's own. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"   /* [UCP] U2 pcrec_enc_set_bytes, `\b`'s precondition */

/* Module assertions' single producer for the position/boundary escapes routed
 * to it (`\A`/`\Z`/`\z` position aliases; `\b`/`\B` word-boundary; `\G` -- see
 * the per-case comments for why each is a DIFFERENT kind of question). Sets
 * `res.end` just past the escape's bytes; the CALLER advances from there per
 * check06's rule, this port never does. `\A`/`\Z` read no scoped state --
 * see the file header for the alias's options=0 exactness. */
ExtResult pcrec_asrtport_atom(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from)
{
    AKind k;
    uint16_t pin = 0;   /* A_CTX: the subject PIN's row (`\A`, `\z`) */
    switch (rw->sel) {
    /* [UTF-VALID] `\A` counts 1 toward LB and `^` does not (both are the
     * SUBJECT_START row, which is why the fact is raised HERE and not read
     * off the tree): measured on 10.46, utf_valid_design.md §1.4. */
    case 'A':   /* \A — the alias, §3.2 */
        k = A_CTX; pin = CTXFN_SUBJECT_START; pcrec_lb_raise(cx, 1); break;
    case 'Z': k = A_EOL; break;   /* \Z — the alias, §3.2 */
    case 'z':   /* \z — the one that needs a machine */
        k = A_CTX; pin = CTXFN_SUBJECT_END; break;
    /* [M6.2 wave B] the word-boundary pair, and they need the OTHER kind of
     * machine: `\A`/`\Z`/`\z` are questions about the POSITION, answerable by
     * an integer compare, while these are questions about the two BYTES
     * around it. That is what buys the alphabet refinement, the context bit
     * in the DFA state identity and the class-indexed accept — see
     * src/ir/dfa.c. Two kinds rather than one plus a negation flag, on D62's
     * principle: no option turns `\b` into `\B`, so the distinction is
     * structure. */
    case 'b':
    case 'B': {
        /* [UTF-VALID] a word boundary reads the character BEFORE the
         * position, so PCRE2 counts it 1 toward LB (utf_valid_design.md
         * §1.4), whichever word set the scope resolves below. */
        pcrec_lb_raise(cx, 1);
        /* [UCP] U2 `\b`/`\B` BUILD THE CONTEXT NODE DIRECTLY (ucp_design.md
         * §2.2): A_CTX over the word set the scope resolved, with the
         * boundary / non-boundary function. T1 FIRST: the row's DEF_UCP_W
         * entry answers under UCP with `aW` unrestricted and the set is then
         * `\w`'s UCP set (`\p{Xwd}` clamped to the encoding — Latin-1 under
         * `byte`); otherwise it is `\w`'s own byte table, exactly the set
         * wave B's N_WORDB read, so every shipped `\b` artifact is unmoved.
         *
         * §2.3's PRECONDITION DECIDES WHETHER IT BUILDS: under `byte` every
         * set is byte-expressible; under utf8 the UCP word set is not, and
         * that `\b` is refused by name until the island ([UCP] U3) / the VM
         * decode ([UCP] U4) — never answered from its ASCII bytes. */
        const RegDef *def = pcrec_def_resolve(cx, rw);
        PcrecCpSet w;
        pcrec_cpset_init(&w, &cx->arena);
        if (def && def->tag != DEF_ALWAYS)
            pcrec_setdef_build(cx, &pcrec_ucp_set_word, &w);
        else
            pcrec_cpset_add_bits(&w, pcrec_cls_word_esc);
        uint8_t bits[32];
        if (!pcrec_enc_set_bytes(pcrec_enc_by_id(cx->opt->encoding),
                                 w.iv, w.n, bits))
            REFUSE(at, "UCP \\%c is not built yet under encoding '%s': it "
                       "reads the Unicode word set, which is not "
                       "byte-expressible, and needs [UCP] U3/U4; (?aW) "
                       "restricts it to the ASCII word set, or use -e byte",
                       rw->sel, pcrec_enc_by_id(cx->opt->encoding)->name);
        ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                          .answered_at = want };
        res.end = cx->pos;
        res.node = pcrec_ast_ctx(cx, w.iv, w.n, rw->sel == 'b'
                                 ? CTXFN_BOUNDARY : CTXFN_NONBOUNDARY);
        res.node->u.ctx.anchor = true;
        pcrec_ast_stamp(res.node, rw, at);
        return res;
    }
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
    res.node = k == A_CTX ? pcrec_ast_pin(cx, pin) : pcrec_ast_node(cx, k);
    /* [M6.4.2 / SR-8, D67] THE STAMP, applied UNIFORMLY to all eight rows
     * rather than to `\K` alone, so "this module's producer stamps what it
     * builds" is a property of the port rather than a per-row exception a
     * future row could be forgotten from. Seven of the eight rows are
     * ANY_ENGINE and contribute nothing to the pattern-wide AND; `\K`'s is
     * VM_ONLY and is what `forces_registry` (src/opt/select_engine.c) reads.
     *
     * IT ALSO REPLACES `Ctx.first_kreset_pos`, which used to be recorded in
     * the `'K'` case above: `pcrec_ast_stamp` records the offset on the
     * node (`Ast.reg_at`) in the same statement that writes the row — so the
     * `engine_why` text and its offset come from one place, and a node that
     * survives a rewrite keeps its own offset ([K110]). */
    pcrec_ast_stamp(res.node, rw, at);

    /* `\A`/`\Z`/`\z` are independent of multiline mode (pcre2pattern:
     * "whatever options are set"), and `(?m)` reaches a node only through
     * the parser's choice of node for `^`/`$` ([DD-11.5], parse.c), so these
     * kinds carry no modifier state to pin. */

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
     * so the emitter will have to know which SUBJECT_START nodes came from
     * `\A` and which from `^` — information a pure alias throws away. The
     * fix, when it has a customer, is a PARSE-RESOLVED PROVENANCE FIELD in
     * D62's shape (kinds encode structure, fields encode parse-resolved
     * state), written exactly here.
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
