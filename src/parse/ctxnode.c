/* [UCP] U2 T3 — A LOOKAROUND'S LOWERING (docs/design/ucp_design.md §0.1,
 * §2.2): the recognizer that turns every lookaround whose body's LANGUAGE is
 * a set of single characters into ONE context node, A_CTX.
 *
 * WHY A NODE AND NOT A REWRITE (§2.2): `(?<=C)` at a position is "the
 * previous character is in C" and `(?!C)` is "the next one is not" — exactly
 * the two-sided question `\b` already asks, over a different set. The DFA
 * answers it on its class axis (src/ir/dfa.c's context-set list), so a
 * pattern whose only VM-forcing construct is such a lookaround moves VM ->
 * DFA with no island and no new machinery; the VM tests it as one guarded
 * byte read (emit_vm.c's `vm_ctx`).
 *
 * THE PREDICATE IS OVER THE LANGUAGE, NOT THE SYNTAX: `(?<=a|b)` and
 * `(?=[ab])` are the same node — [ENG-ISL] STEP 1's recorded lesson (the
 * per-branch predicate was measured wrong, alt_dispatch_study.md). And it is
 * asked HERE, by the lookaround port at construction, rather than by a
 * separate pass over the finished tree: the body is complete when the port
 * builds the node, and a node born as A_CTX is never stamped with the
 * lookaround rows' VM_ONLY mask, so `Ctx.first_vmonly_pos` never records an
 * offset for a construct the tree no longer carries.
 *
 * THE TABLE (§0.1's rule): an ordered first-match list of rows, each a name,
 * a deny flag, a one-line predicate and its test, walked by `pcrec_look_t3`;
 * a denied or non-applying row is transparent and the last row is always
 * true. `--list-axes`' `ctx-node` rows are a plain read of it
 * (src/dump/axes_dump.c).
 *
 * THE BYTE-EXPRESSIBILITY CONJUNCT IS U2's, NOT THE DESIGN'S LANGUAGE ROW.
 * §0.1's T3 row 1 is language-only; §2.3 then sends a non-byte-expressible
 * context set to the island (U3) or the VM decode (U4). Neither exists in
 * U2, so a node built for such a set would have no engine that can read it:
 * the row admits a set only when `pcrec_enc_set_bytes` says every member is
 * one byte of the encoding, and the lookaround keeps today's VM lowering
 * otherwise — which is exact, `back_step` refusing ill-formed bytes (the
 * `(?<=[^a])a` on `80 61` hazard cell). U3/U4 drop the conjunct. */

#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"

/* Accumulate the LANGUAGE of `a` into `acc` when it is a set of single
 * characters; false when it is anything else (a width other than exactly one
 * character, an assertion, a capture, a reference, a call). Iterative on both
 * spines (K20's discipline). */
static bool lang_charset(const Ast *a, PcrecCpSet *acc)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS:
            pcrec_cpset_add_set(acc, a->u.cls.iv, a->u.cls.n);
            return true;
        case A_ALT:
            while (a->k == A_ALT) {
                if (!lang_charset(a->r, acc)) return false;
                a = a->l;
            }
            continue;
        case A_CAT: {
            /* One element carries the character; every other element must be
             * the empty string, so `(?:)a` is `a`. */
            const Ast *one = NULL;
            while (a->k == A_CAT) {
                if (a->r->k != A_EMPTY) {
                    if (one) return false;
                    one = a->r;
                }
                a = a->l;
            }
            if (a->k != A_EMPTY) {
                if (one) return false;
                one = a;
            }
            if (!one) return false;
            a = one;
            continue;
        }
        case A_REP:
            if (a->u.rep.rmin != 1 || a->u.rep.rmax != 1) return false;
            a = a->l;
            continue;
        /* An atomic group over a set of single characters has no choice point
         * to cut: every alternative consumes exactly one character, so its
         * language is its body's. */
        case A_ATOMIC:
            a = a->l;
            continue;
        /* Capture-bearing (§6's own sabotage row), zero-width, or consuming
         * text whose width is not one character: not this row's language. */
        case A_CAP:
        case A_EMPTY:
        case A_BOL: case A_EOL: case A_END: case A_CTX: case A_GSTART:
        case A_KRESET: case A_LOOK:
        case A_BREF: case A_VAR: case A_CALL:
        /* [CLS-TREE] S3: made below the lowering, never at parse time.
         * Declining is the sound answer: its child is BYTES, not the
         * characters this set is made of. */
        case A_WCLASS:
            return false;
        }
        return false;   /* unreachable under -Wswitch (make strict) */
    }
}

/* The truth function a lookaround of this direction and polarity asks of
 * its set: `(?<=C)` prev, `(?<!C)` not prev, `(?=C)` next, `(?!C)` not next. */
static uint8_t look_fn(bool behind, bool neg)
{
    if (behind) return neg ? CTXFN_NOT_PREV : CTXFN_PREV;
    return neg ? CTXFN_NOT_NEXT : CTXFN_NEXT;
}

/* Row 1's test: the body's language is a set of single characters and that
 * set is byte-expressible under the compile's encoding. */
static bool t3_ctx_applies(Ctx *cx, const Ast *body, PcrecCpSet *set)
{
    pcrec_cpset_init(set, &cx->arena);
    if (!lang_charset(body, set)) return false;
    uint8_t bits[32];
    return pcrec_enc_set_bytes(pcrec_enc_by_id(cx->opt->encoding),
                               set->iv, set->n, bits);
}

static bool t3_always(Ctx *cx, const Ast *body, PcrecCpSet *set)
{
    (void)cx; (void)body; (void)set;
    return true;
}

const PcrecLookRow pcrec_look_rows[] = {
    { "ctx-node", PCREC_NO_CTX_NODE,
      "the body is capture-free and assertion-free, its LANGUAGE is a set of "
      "single characters, and every member is one byte of the encoding "
      "(ucp_design.md §2.3)",
      t3_ctx_applies, true },
    { "lookaround", 0,
      "always (fallback) — today's A_LOOK lowering: a VM sub-match",
      t3_always, false },
};
const int pcrec_look_nrows = (int)(sizeof pcrec_look_rows / sizeof pcrec_look_rows[0]);

/* T3's walk: the A_CTX node the first applying, undenied row builds, or NULL
 * when the row that fired is `lookaround` (the caller builds its A_LOOK). */
Ast *pcrec_look_t3(Ctx *cx, const Ast *body, bool behind, bool neg)
{
    for (int i = 0; i < pcrec_look_nrows; i++) {
        const PcrecLookRow *r = &pcrec_look_rows[i];
        if (r->deny && (cx->opt->flags & r->deny)) continue;
        PcrecCpSet set;
        if (!r->applies(cx, body, &set)) continue;
        if (!r->ctx) return NULL;
        return pcrec_ast_ctx(cx, set.iv, set.n, look_fn(behind, neg));
    }
    return NULL;   /* unreachable: the last row is always true */
}
