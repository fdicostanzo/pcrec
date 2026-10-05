/* [START-SET] THE START SET: which bytes can the first consumed byte of a
 * non-empty match be? (D148; docs/design/startset.md §3, rev 2.)
 *
 * A CORE fact at E2, on the LOWERED tree (after `pcrec_lower_enc`), so every
 * `A_CLASS` is a BYTE class and the set is a set of BYTES: under `-e utf8` it
 * holds the lead bytes of the characters a match can begin with. Because it
 * is the compile's OWN lowered tree, it reads the compile's real options by
 * construction — `-i` (folded into the classes at parse), `--ucp`, the
 * encoding and inline/per-block flags all reach the tree before this walk
 * does (startset.md §3.1, review r4 sound-F4). It takes no option itself.
 *
 * THE VALUE IS A SUPERSET, never a subset, of the true first bytes. It is the
 * first-byte set of `L+`, the language with every ZERO-WIDTH node replaced by
 * the empty string (§3.2): each zero-width node consumes nothing and only
 * constrains which strings match, so erasing it admits a superset, and the
 * first bytes of a superset are a superset. That covers `\b`, `\B`, every
 * lookaround, `^`, `$`, `\z`, `\G` and `\K` (under `\K` the REPORTED start
 * moves; the ATTEMPT start this set is about does not). A backreference, a
 * subroutine call and a `${var}` are "all 256 bytes, nullable": the walk does
 * not look through them, which is the conservative answer (`possessify.c`'s
 * arm for the same kinds).
 *
 * `nullable` IS THE ERASED LANGUAGE'S (sound-F9 + checks-F9, reconciled under
 * D120's one-owner-per-QUESTION rule). It answers "can `L+` match empty",
 * which is the premise every reader of `bits` needs (a necessary first byte
 * exists only where `L+` is not nullable). The `nullable` FACT answers "can
 * `L` match empty" — a different question with its own owner. `L` is a subset
 * of `L+`, so `nullable` ⇒ `start_set.nullable`, and
 * `tests/startset/run_startset_checks.sh` pins that on every corpus artifact:
 * a walk that under-approximates nullability fails there.
 *
 * WHY possessify's `first_of` IS NOT REUSED (D148 Q4): it runs above the
 * encoding lowering on code points, widens a lookaround to all bytes for its
 * follow-set disjointness test, and answers a different question.
 *
 * THE SPINES ARE WALKED ITERATIVELY. `A_CAT` and `A_ALT` are left-nested and
 * as long as the pattern (K20; `src/opt/atomic.c`'s statement, coding_guide
 * §2.4): the walk descends `->l` in a loop carrying what lies to the RIGHT
 * (`acc`), and recurses only one paren level per frame. It does not follow
 * `Ast.u.call.body`. The switch has no `default:` (`src/opt/mrl.c`'s rule): a
 * new kind is a compile error here, which is the alarm a superset argument
 * wants, since a new CONSUMING kind read as zero-width would be unsound. */

#include <string.h>

#include "core/internal.h"
#include "facts/facts_derive.h"

/* `l` followed by `r`: `l`'s first bytes, plus `r`'s when `l` can be empty. */
static StartSet ss_cat(StartSet l, const StartSet *r)
{
    if (l.nullable)
        for (int i = 0; i < 32; i++) l.bits[i] |= r->bits[i];
    l.nullable = l.nullable && r->nullable;
    return l;
}

/* The empty string: no first byte, nullable — concatenation's identity. */
static StartSet ss_empty(void)
{
    StartSet s;
    memset(s.bits, 0, sizeof s.bits);
    s.nullable = true;
    return s;
}

/* Every byte, nullable: the answer for a node the walk does not look into. */
static StartSet ss_all(void)
{
    StartSet s;
    memset(s.bits, 0xFF, sizeof s.bits);
    s.nullable = true;
    return s;
}

/* The start set of `a` followed by `acc` (what lies to its right). */
static StartSet ss_walk(Ctx *cx, const Ast *a, StartSet acc)
{
    for (;;) {
        switch (a->k) {
        case A_CAT: {
            /* `a->r` sits between everything still to walk and `acc`. */
            StartSet r = ss_walk(cx, a->r, ss_empty());
            acc = ss_cat(r, &acc);
            a = a->l;
            continue;
        }
        case A_CAP:
        case A_ATOMIC:
        case A_WCLASS:
            /* Transparent: a group matches what its body matches, a cut
             * removes matches rather than bytes, and a wide class's child is
             * its byte spelling. */
            a = a->l;
            continue;
        case A_ALT: {
            StartSet u = ss_walk(cx, a->r, ss_empty()), b;
            const Ast *t = a->l;
            for (;;) {
                b = ss_walk(cx, t->k == A_ALT ? t->r : t, ss_empty());
                for (int i = 0; i < 32; i++) u.bits[i] |= b.bits[i];
                u.nullable = u.nullable || b.nullable;
                if (t->k != A_ALT) break;
                t = t->l;
            }
            return ss_cat(u, &acc);
        }
        case A_REP: {
            /* The body's set; a minimum of 0 admits the empty iteration. */
            StartSet b = ss_walk(cx, a->l, ss_empty());
            if (a->u.rep.rmin < 1) b.nullable = true;
            return ss_cat(b, &acc);
        }
        case A_CLASS: {
            StartSet c;
            pcrec_cls_bits(cx, a, c.bits);
            c.nullable = false;
            return ss_cat(c, &acc);
        }
        /* Zero-width: consumes nothing, so the first byte comes from what
         * follows (§3.2). */
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
        case A_CTX:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
            return acc;
        /* Not looked into: every byte, nullable (§3.2). */
        case A_BREF:
        case A_CALL:
        case A_VAR:
            return ss_all();
        }
    }
}

/* THE START SET of the lowered tree `root` into `*out`. */
void pcrec_start_set(Ctx *cx, const Ast *root, StartSet *out)
{
    *out = ss_walk(cx, root, ss_empty());
}
