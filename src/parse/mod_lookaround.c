/* mod_lookaround.c — module `lookaround` ([M6.6.2]): the ONE group port all
 * six registry rows dispatch through.
 *
 * Design: docs/design/lookaround_design.md, panel-approved at R33
 * (docs/dev/reviews/2026-08-23-r33-lookaround-design.md). §8.1 is this file's
 * charter; §2.5, §2.6 and §2.7 are the three rules it enforces.
 *
 * WHAT A LOOKAROUND IS, in one sentence (design §0.2): a SUB-MATCH whose
 * result is a VERDICT and whose POSITION is discarded. Everything this file
 * does follows from that — the node consumes nothing (`pcrec_minw` and
 * `pcrec_maxw` both answer 0, and `vm_nullable` answers true), it is not a
 * capturing construct (`cx->ncap` is untouched here; groups INSIDE the body
 * capture exactly as they would anywhere else, measured: `(?=(a))a` on "a" is
 * (0,1) with g1=(0,1)), and the lowering is `vm_atomic`'s shape plus a saved
 * cursor (src/gen/emit_vm.c's `vm_look`).
 *
 * ONE PORT FOR SIX ROWS, and design §8.1's reason is the one that matters: the
 * six constructs differ ONLY in the three `Ast.u.look` flags this function
 * sets, so a second port function would be a SECOND PLACE the `<`-tail split
 * is decided. The dispatch below is a single table keyed on the row's own
 * `sel`/`tail` — the same two fields the registry arbitrated on to get here —
 * so the port cannot disagree with the row that elected it.
 *
 * THE WAVE B+C SPLIT IS GONE, AND WAVE D IS WHAT SPENT IT (design §8.3, R33
 * V-3). D65 derives a row's `built` column from the PORT's `ExtResult` at
 * `WANT_RESULT` (src/parse/syntax_dump.c) and never runs the emitter, so the
 * column flips for exactly the rows whose tail this function ACCEPTS. Wave
 * B+C recognised the three LOOKAHEAD tails (`=`, `!`, `*` at the `(?`
 * doorway) and DECLINED the three `<` tails with the enabled-but-unbuilt
 * diagnostic — the honest answer while `vm_look` had no back-step. Wave D
 * landed `PCREC_ENCE_BACK_STEP` (src/gen/enc/enc_byte.c) and §3.4's emitted
 * shape, so THE DECLINE AND ITS `built` COLUMN ARE DELETED: all six rows read
 * `built`, and the table below has no `built` field left to disagree about.
 * Nothing else in this file changed for the lookbehind, because
 * `Ast.u.look.behind` was always set from the table — what wave D added here
 * is §2.5's WIDTH RULE, and nothing else.
 *
 * §2.5's WIDTH RULE, WHICH IS THIS FILE's THIRD AND LAST CHECK. A lookbehind
 * body's every TOP-LEVEL BRANCH must have a FIXED width: `pcrec_minw(branch)
 * == pcrec_maxw(branch)`, both finite. Widths may DIFFER between branches —
 * `(?<=a|bc)x` ships and is a python `re` ERROR (design §7 G1) — and a body
 * with any variable-width branch is refused HERE, with a pattern offset,
 * rather than discovered by the emitter.
 *
 * WHY TOP-LEVEL BRANCHES AND NOT THE WHOLE BODY, because the asymmetry is the
 * single most likely thing in this module to be read as a defect: §2.4
 * MEASURED that PCRE2 tries a lookbehind's top-level branches in WRITTEN
 * order and, WITHIN one branch, tries the step-back LENGTH longest-first. A
 * branch of one fixed width has one length, so the loop that would order them
 * has one iteration and written order is the whole answer. That is why
 * `(?<=a|bc)x` (two branches, widths 1 and 2) ships and `(?<=(a|bc))x` (ONE
 * branch of width 1..2) is refused: the second needs the longest-first loop
 * this module does not build. §2.5's three reasons for chartering that loop
 * rather than shipping it are in the design.
 *
 * WHY THE DECLINE WAS AN `EXT_REFUSAL` AND NOT AN `EXT_NOT_MINE`, kept
 * because §2.5's refusal is answered the same way: the `(?` doorway CANNOT
 * decline (internal.h's ExtResult comment — its catch-all is REJECTED, so
 * `EXT_NOT_MINE` from it is a registry defect the wall reports).
 *
 * `\K` IS REFUSED INSIDE A LOOKAROUND (§2.7), PERMANENTLY. libpcre2 10.46
 * refuses it in all four polarities with err 199, whose own text names
 * `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`; pcrec matches the DEFAULT and does not
 * implement the option (adopting any `EXTRA_*` bit is a D38 ruling event).
 * Frank ruled the reopening closed on 2026-08-23: "it's considered bad mojo
 * and weird". THE CHECK IS NEEDED RATHER THAN FREE — `\K` is module
 * `assertions` and already ships, so without it `(?=a\K)b` would compile
 * today's `\K` inside tomorrow's lookaround and quietly move the reported
 * match start. `la_has_kreset` below is RECURSIVE THROUGH NESTED GROUPS AND
 * NESTED LOOKAROUNDS and stops AT the assertion's `)` (R33 C1-7): §2.7's
 * eleven refused cells include `(?=(a\K))x`, `(?=a(?:\K))x` and
 * `(?=(?:(?=\K)))x` — the three an immediate-children check would miss — and
 * its four COMPILING cells (`(?=a)\Kb`, `a(?=b)\Kc`, `(?<=a)\Kb`, `a\Kb`) are
 * what a check latching on "a lookaround was seen" would wrongly break. Both
 * sets are `tests/lookaround/refused.rxt`'s and sabotage row S128's.
 *
 * A LOOKAHEAD STILL WRITES `widths = NULL` AND `nbranch = 0`, and that is the
 * ANSWER rather than a placeholder: a lookahead has no width rule at all —
 * any body is legal, measured in both oracles — so there is nothing to
 * tabulate. The two fields are one fact and are written together.
 */

#include <limits.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* THE ROW TABLE — the six constructs, and the only place the three flags are
 * decided. Keyed on the row's own `sel` and `tail`, the two fields
 * `pcrec_registry_arbitrate` already matched to elect the row, so this table
 * cannot elect a different construct than the registry did.
 *
 * THE `built` COLUMN IS GONE AT WAVE D. It existed for exactly one wave and
 * carried exactly one fact — that `vm_look` had no back-step yet — and with
 * `PCREC_ENCE_BACK_STEP` landed there is nothing left for it to say. All six
 * rows are built, so D65 reads `built` for all six. */
typedef struct {
    int         sel;
    const char *tail;       /* NULL for a tail-less row */
    bool        behind;
    bool        neg;
    bool        atomic;
} LaRow;

static const LaRow la_rows[] = {
    /* sel  tail  behind  neg   atomic */
    { '=',  NULL, false, false, true  },
    { '!',  NULL, false, true,  true  },
    /* `(?*X)` is PCRE2's NON-ATOMIC positive lookahead — the `(?` spelling of
     * `(*napla:...)`, proven behaviourally rather than by its name (§2.2, on
     * "abab"): `(?*(a|ab))\1$` is (2,4) where `(?=(a|ab))\1$` is NOMATCH. */
    { '*',  NULL, false, false, false },
    /* THE THREE `<` TAILS. `(?<` is three constructs and a name, split by tail
     * at SR-9; every other tail byte is the named-group row and never reaches
     * this port. Wave D built them: what distinguishes them here is still one
     * bool, because the direction changes the LOWERING (§3.4) and not the
     * parse — plus §2.5's width rule, which `la_widths` below enforces. */
    { '<',  "=",  true,  false, true  },
    { '<',  "!",  true,  true,  true  },
    { '<',  "*",  true,  false, false },
};

static const LaRow *la_kind(const RegRow *rw)
{
    /* [M6.6.2 wave F] AN ALIAS ROW RESOLVES TO ITS PRIMARY FIRST, and this is
     * THE ONE PLACE an alpha spelling is turned into a construct.
     *
     * The twelve `(*` alpha rows (registry.c's `VERB_LA`) carry their
     * primary's own `syntax` in `family` — D71 item 3's field, whose value IS
     * the family's canonical spelling. So an alias does not get flags of its
     * own to be wrong about: it names a ROW, that row's `sel`/`tail` select
     * the LaRow below, and `la_rows` stays the only table where `behind`,
     * `neg` and `atomic` are decided. Twelve more LaRow entries would have
     * been twelve more chances for `(*nla:` to come out positive.
     *
     * ONE LEVEL, NOT A CHAIN: a primary has `family == NULL` by construction
     * (it IS its family's canonical spelling), so the recursive call below
     * cannot re-enter this branch. A row whose `family` names another ALIAS
     * — or names nothing at all — falls out as NULL and reaches the caller's
     * `BAD_ROW`, which is the honest answer for a registry that has been
     * edited into an inconsistent state. `tests/registry/registry_check.c`
     * fails such a row long before a user could reach it. */
    if (rw->family) {
        size_t n;
        const RegRow *rows = pcrec_registry(RK_GROUP, &n);
        for (size_t i = 0; i < n; i++)
            if (!rows[i].family && rows[i].syntax &&
                strcmp(rows[i].syntax, rw->family) == 0)
                return la_kind(&rows[i]);
        return NULL;
    }

    for (size_t i = 0; i < sizeof la_rows / sizeof la_rows[0]; i++) {
        const LaRow *k = &la_rows[i];
        if (k->sel != rw->sel) continue;
        if ((k->tail == NULL) != (rw->tail == NULL)) continue;
        if (k->tail && strcmp(k->tail, rw->tail) != 0) continue;
        return k;
    }
    return NULL;
}

/* §2.7's scope, as a walk. TRUE when an `A_KRESET` occurs ANYWHERE in this
 * subtree — through nested groups, quantifiers, atomic groups and nested
 * lookarounds alike.
 *
 * A nested lookaround's own body is reached by its own port first (the inner
 * `(?=\K)` of `(?=(?:(?=\K)))x` refuses before this walk ever runs), so the
 * `A_LOOK` arm below is belt-and-braces rather than the mechanism — but it is
 * the arm a reader would expect to find, and leaving it out would make the
 * three-cell claim above depend on parse ORDER rather than on this predicate.
 *
 * BOTH SPINES ARE WALKED ITERATIVELY (D10/DD-10): a flat concatenation is as
 * long as the pattern, and this project has paid for that lesson three times.
 * There is NO `default:` — mrl.c:18-24's rule — so a node kind added later is
 * a compile error here rather than a silent "no `\K` in that". */
static bool la_has_kreset(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_KRESET:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_BREF:
            return false;
        /* [DD-14] ANSWERS `false`, AND THE ARM CARRIES AN OBLIGATION FOR THE
         * WAVE THAT BUILDS THE PRODUCER. Read it before touching this line.
         *
         * NOT IN subroutines_design.md §4.4a's TABLE: this site did not exist
         * when that census was taken at eacac76 — it is `lookaround`'s own,
         * added after — so its verdict is decided here rather than inherited.
         *
         * WHY IT CANNOT ANSWER ANYTHING ELSE TODAY. This predicate runs
         * INSIDE THE PARSE HOOK, at the moment the lookaround body is parsed,
         * to raise §2.7's refusal with a pattern OFFSET. A call's
         * `u.call.body` is filled by the END-OF-PARSE resolution pass
         * (subroutines_design.md §4.2) — later — and a FORWARD call names a
         * group that has not been parsed yet at all. So at the instant this
         * walk runs, `.body` is NULL and there is no callee to inspect: the
         * question "does the callee contain a `\K`" is not merely forbidden
         * here by §4.4's back-edge rule, it is UNANSWERABLE here.
         *
         * **WAVE B+C DISCHARGED IT WITH THE THIRD ANSWER, AND `false` IS
         * THEREFORE THE PERMANENTLY CORRECT ONE.** This comment used to say
         * the wave with the producer must either re-run the check after
         * resolution over the call graph, refuse a call inside a lookaround
         * body, or MEASURE what 10.46 does. It measured, and **PCRE2's RULE
         * IS LEXICAL**: `(?=(a\Kb))x` is error 199, and `(?=(?1))(a\Kb)` —
         * where the `\K` is reached THROUGH A CALL — COMPILES and matches
         * (1,2) on "ab". The first two answers would have refused patterns
         * 10.46 accepts.
         *
         * AND pcrec ALREADY REPRODUCES IT, which is what makes "answer
         * `false` and stop" a measurement rather than a shrug: the lane built
         * the post-graph check, measured the oracle, deleted the check and
         * re-measured — 7 of 7 cells agreeing, INCLUDING the isolating
         * `^(?:((?:a)\Kb)){0}(?=(?1))ab$`, where the `\K` is reachable ONLY
         * through the call inside the lookahead. The reason is structural:
         * design §5.3a excludes slots 0 and 1 from `W` BY CONSTRUCTION so a
         * `\K` survives the RETURN, and `vm_look` restores the CURSOR from
         * `SLOT_LOOK_POS` rather than slot 0 so it survives the ASSERTION.
         * `\K` is a PATH FACT at both boundaries.
         *
         * The measurement and the cells are recorded at
         * `src/opt/callgraph.c`'s own `\K` note and in
         * `tests/recursion/kreset.rxt`. */
        case A_CALL:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l)
                if (la_has_kreset(t->r)) return true;
            a = t;
            continue;
        }
        }
        return false;
    }
}

/* §2.5's WIDTH RULE, as a table. Fills `out[0..nbr-1]` with each TOP-LEVEL
 * branch's fixed width IN WRITTEN ORDER and returns true; on the first branch
 * that is NOT fixed-width, writes that branch's `minw`/`maxw` through `bad_lo`
 * / `bad_hi` and returns false.
 *
 * WRITTEN ORDER IS THE WHOLE POINT AND IT IS THE REVERSE OF THE WALK (§2.4
 * level 1). `p_alt_info` builds a flat alternation LEFT-NESTED — `a|b|c` is
 * `A_ALT(A_ALT(a, b), c)` — so descending the `->l` spine yields the branches
 * BACKWARDS through `->r`, with the FIRST branch left over as the innermost
 * `->l`. This function therefore fills `out` from the END, which is what makes
 * `out[0]` the branch PCRE2 tries first. Get this backwards and `(?<=(a)|(aa))c`
 * on "aac" reports the wrong group — the exact cell §2.4 measured.
 *
 * IT IS NOT A SECOND BRANCH-SPLITTING RULE. `nbr` comes from `AltInfo`
 * (PARSE-1), computed by the LOOP THAT DROVE THE PARSE, and this walk asserts
 * it rather than re-deriving it: an A_ALT spine of `nbr` branches has exactly
 * `nbr - 1` A_ALT nodes, so a disagreement is an internal error and not a
 * pattern error. That is D24's rule — a `|`-counting scanner here would be a
 * second implementation of a rule the parser already applied, and it would get
 * `(?<=(a|bc))x` and `(?<=a|bc)x` exactly backwards, which are the two cells
 * §2.5 exists to distinguish.
 *
 * FIXED MEANS `minw == maxw`, BOTH FINITE, and it is `pcrec_maxw` that makes
 * this analysis new (src/opt/mrl.c, wave A). `pcrec_minw` may UNDER-estimate
 * for free and `pcrec_maxw` may OVER-estimate for free; the direction that is
 * NOT free is an under-estimating `maxw`, which would let a variable-width
 * branch through as fixed. That is a silent miscompile rather than a lost
 * optimisation — and on a NEGATIVE lookbehind it is a FALSE MATCH — which is
 * why §3.4's end-check is emitted on both polarities and why sabotage row
 * S136 accepts a `minw != maxw` branch on purpose.
 *
 * A NESTED LOOKAROUND INSIDE A BRANCH CONTRIBUTES 0 AT BOTH ENDS (§3.1(d),
 * wave A's arms), so `(?<=a(?=b))x` stays fixed width 1 — it is not a special
 * case here, it is what both analyses already answer for A_LOOK. */
static bool la_widths(Ctx *cx, const Ast *body, int nbr, int *out,
                      long long *bad_lo, long long *bad_hi)
{
    int i = nbr;
    const Ast *a = body;

    for (; a->k == A_ALT; a = a->l) {
        /* A SPINE LONGER THAN `nbr - 1` IS AN INTERNAL ERROR, NOT A PATTERN
         * ERROR, so it aborts the compile by name rather than being folded
         * into §2.5's capability refusal — a caller told "your lookbehind is
         * variable-length" about a compiler bug has been told something
         * false. `ctx_fail` is the same channel `vm_look`'s own impossible
         * arms use. */
        if (i <= 1)
            ctx_fail(cx, 0, "internal error: a lookbehind body's alternation "
                            "spine is longer than its reported branch count");
        i--;
        long long lo = pcrec_minw(a->r), hi = pcrec_maxw(a->r);
        if (lo != hi || hi >= PCREC_W_UNBOUNDED || hi > INT_MAX) {
            *bad_lo = lo; *bad_hi = hi;
            return false;
        }
        out[i] = (int)hi;
    }
    if (i != 1)
        ctx_fail(cx, 0, "internal error: a lookbehind body's alternation spine "
                        "is shorter than its reported branch count");
    {
        long long lo = pcrec_minw(a), hi = pcrec_maxw(a);
        if (lo != hi || hi >= PCREC_W_UNBOUNDED || hi > INT_MAX) {
            *bad_lo = lo; *bad_hi = hi;
            return false;
        }
        out[0] = (int)hi;
    }
    return true;
}

/* [DD-14.LB] §2.5's REFUSAL SENTENCE — ONE HOME, TWO TIMINGS.
 *
 * The width rule is asked twice now (see this file's `pcrec_lookaround_
 * fix_widths` below and `pcrec_postresolve`'s declaration in internal.h), and
 * the two asks must produce the SAME BYTES: they are one rule, and a caller
 * who writes a call into a lookbehind body must not get a differently-worded
 * refusal from the one who did not. The two paths RAISE it differently and
 * cannot share that — the hook is inside a doorway and owes an `ExtResult`,
 * the pass is not and calls `ctx_fail` — so what is shared is the text.
 *
 * IT IS BYTE-IDENTICAL BY CONSTRUCTION AND NOT BY TRANSCRIPTION: the doorway
 * epilogue is `ctx_fail(cx, r->at, "%s", r->msg)` (src/parse/ext.c), so
 * `REFUSE(at, "%s", buf)` here and `ctx_fail(cx, at, "%s", buf)` there render
 * the same string at the same offset through the same formatter. `buf` is 256
 * bytes for `ExtResult.msg`'s reason, which is the buffer the hook's text used
 * to be formatted straight into; the longest sentence below is under half of
 * it.
 *
 * THE ORDER OF THE THREE ARMS IS PART OF THE RULE, not of either caller.
 * UNBOUNDED IS TESTED FIRST because `PCREC_W_UNBOUNDED` is itself above
 * `INT_MAX`, so the other order reports every `a*` body as "too long" — a
 * different and wrong claim. Here pcrec AGREES WITH PCRE2, whose own answer
 * is err 125 "length of lookbehind assertion is not limited" (§2.5). */
#define LA_MSG_MAX 256
static void la_width_refusal(char *buf, size_t n, long long lo, long long hi)
{
    if (hi >= PCREC_W_UNBOUNDED)
        snprintf(buf, n, "variable-length lookbehind is not implemented: "
                         "every alternative of a lookbehind must have a "
                         "fixed length (this one is unbounded)");
    /* A FIXED width too large to store. Only reachable through a nested
     * exact-count tower; the emitter's own node cap would refuse it a step
     * later, and refusing here keeps `widths` an `int` table rather than
     * making the whole analysis 64-bit for a pattern nothing can compile. */
    else if (hi > INT_MAX)
        snprintf(buf, n, "this lookbehind is too long");
    else
        snprintf(buf, n, "variable-length lookbehind is not implemented: every "
                         "alternative of a lookbehind must have a fixed length "
                         "(this one can match %lld..%lld characters)", lo, hi);
}

/* [DD-14.LB] THE TWO HALVES OF THE DEFERRED RE-CHECK — internal.h's
 * declarations carry the argument for the split; this is the rule.
 *
 * `_pending` IS THE `widths == NULL` STATE READ OUT LOUD, and it is a function
 * rather than an open-coded test at the pass because the encoding of "pending"
 * is this module's business: if a later wave gives the state its own field the
 * pass does not change. It answers false for a LOOKAHEAD without looking at
 * `widths` at all — a lookahead's NULL is the ANSWER (there is no width rule
 * for one), not a deferral, and conflating the two would send every lookahead
 * through the pass. */
bool pcrec_lookaround_width_pending(const Ast *a)
{
    return a->k == A_LOOK && a->u.look.behind && a->u.look.widths == NULL;
}

/* Resolve a deferred lookbehind's width table, or refuse at the offset the
 * hook recorded. A NO-OP on anything `_pending` declines, which is what keeps
 * a second caller from re-deriving a table that already exists — §3.1(c)'s
 * whole reason for storing it.
 *
 * `pcrec_maxw` IS THE SAME FUNCTION THE HOOK CALLED, and that is the point of
 * doing this here rather than teaching the hook to look through a call: by
 * this timing `src/opt/callgraph.c` has published `u.call.maxw`, so the arm
 * that answered `PCREC_W_UNBOUNDED` at parse time answers the callee's real
 * maximum — UNBOUNDED still, and exactly, for a callee in a cycle (design
 * §3.4(d): libpcre2 refuses that itself, err 125). Nothing about the RULE
 * moved; only the moment it is asked. */
void pcrec_lookaround_fix_widths(Ctx *cx, Ast *a)
{
    if (!pcrec_lookaround_width_pending(a)) return;

    const int nbr = a->u.look.nbranch;
    if (nbr < 1)
        ctx_fail(cx, 0, "internal error: a deferred lookbehind carries no "
                        "branch count");

    long long lo = 0, hi = 0;
    int *w = arena_alloc(&cx->arena, (size_t)nbr * sizeof *w);
    if (!la_widths(cx, a->l, nbr, w, &lo, &hi)) {
        char buf[LA_MSG_MAX];
        la_width_refusal(buf, sizeof buf, lo, hi);
        ctx_fail(cx, a->u.look.at, "%s", buf);
    }
    a->u.look.widths = w;
}

ExtResult pcrec_laport_group(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;

    /* The doorway's contract (ExtWant, internal.h): the cursor moves only
     * under WANT_RESULT, and this port is only ever called there — the gate
     * demotes a disabled module's ask to WANT_VERDICT, which ext.c answers
     * with the module refusal before any port runs. `want` is still READ, by
     * the REFUSE macro below, which stamps it as `answered_at`. */
    /* `r` NAMES THE DISPATCHING ROW, which is the convention internal.h's
     * refusal macros state (`UNBUILT` read it; wave D deleted that call and
     * the name is kept because `la_kind` reads the same row the registry
     * arbitrated on to get here). */
    const RegRow *r = rw;
    const LaRow *k = la_kind(r);
    if (!k) BAD_ROW(at, "a module 'lookaround' row");

    /* NO `built` CHECK HERE ANY MORE — wave D deleted it with the column it
     * fed (see this file's header). All six rows are built, so every one of
     * them reaches the body parse below. */

    /* A body-carrying group, so the SCOPED inline-option state is saved and
     * restored around the body exactly as `p_group_body`'s plain-`(` tail and
     * mod_atomic_groups.c's port do — measured behaviour, not a choice:
     * `(?i)` set inside a group is restored at the immediately-enclosing `)`.
     * It is NOT a capturing group (PCRE2 gives a lookaround no number), so
     * `cx->ncap` is untouched. */
    ParseMods saved_mods = *cx->mods;
    size_t    saved_pos  = cx->pos;
    cx->pos = from;

    AltInfo info;
    Ast *body = pcrec_parse_body(cx, &info);

    if (cx->pos >= n || p[cx->pos] != ')') {
        *cx->mods = saved_mods;
        cx->pos = saved_pos;
        REFUSE(at, "missing closing ) for group");
    }
    size_t end = cx->pos + 1;
    *cx->mods = saved_mods;
    cx->pos = saved_pos;

    /* §2.7, and the offset is the ASSERTION's rather than the `\K`'s because
     * `Ast` carries no position of any kind (PARSE-1's own note). D26 puts the
     * wording in tier 3 and the OFFSET convention in tier 2: pointing at the
     * construct pcrec is refusing is that convention. */
    if (la_has_kreset(body))
        REFUSE(at, "\\K is not allowed inside a lookaround");

    /* An EMPTY body needs nothing special — `pcrec_parse_body` returns an
     * A_EMPTY and §3's shapes swallow it, which is why `(?=)` and `(?!)` ship
     * (§2.6, measured in both oracles: `a(?=)b` is (0,2), `a(?!)b` is NOMATCH,
     * `(?:(?!))|a` is (0,1)). The cells are in the corpus because "legal" is
     * the surprising answer, not because the code has an arm for them. */

    Ast *a = pcrec_ast_node(cx, A_LOOK);
    a->l = body;
    /* `r` is unused for this kind — internal.h's A_LOOK comment. */

    /* THE THREE FLAGS, D62 state: resolved HERE, by the position that knows,
     * and read by `vm_look` alone. */
    a->u.look.behind = k->behind;
    a->u.look.neg    = k->neg;
    a->u.look.atomic = k->atomic;

    /* THE WIDTH TABLE (§2.5/§3.1(c)), and it is the LOOKBEHIND's alone. A
     * LOOKAHEAD has no width rule — any body is legal, measured in both
     * oracles — so NULL/0 is the ANSWER there and not a placeholder; the two
     * fields are written together because they are one fact.
     *
     * REFUSED AT THE ASSERTION's OWN OFFSET, and `at` rather than the
     * offending branch's start for the reason §2.7's `\K` refusal gives:
     * `Ast` carries no position of any kind (PARSE-1's note), so the position
     * this port can honestly name is the construct it is refusing. D26 puts
     * the OFFSET convention in tier 2 and the WORDING in tier 3.
     *
     * IT IS A CAPABILITY LIMIT AND IS WORDED AS ONE, NOT AS "requires module
     * 'lookaround'": the module is enabled and the construct is real — PCRE2
     * compiles every body refused here — so what is missing is the
     * longest-first step-back loop §2.5 charters and this module does not
     * build. Saying "enable the module" to a caller who already has would be
     * an actionable-sounding lie, which is D33's own distinction. */
    /* [DD-14.LB] AND THE OFFSET, for EVERY A_LOOK — see `u.look.at`. It is
     * written before the branch below because the deferred arm needs it and
     * "the offset this construct was parsed at" is true of the other two. */
    a->u.look.at = at;

    if (!k->behind) {
        a->u.look.widths  = NULL;
        a->u.look.nbranch = 0;
    } else if (pcrec_has_call(body)) {
        /* [DD-14.LB] THE DEFERRAL. A body carrying an `A_CALL` cannot be
         * measured HERE, and the obstacle is TIMING rather than analysis:
         * `pcrec_maxw`'s `A_CALL` arm answers `PCREC_W_UNBOUNDED` at this
         * instant because `u.call.maxw_known` is still the arena's false —
         * the callee is not bound, and a FORWARD call's target has not been
         * parsed at all — so asking the rule now would refuse
         * `^(?:(?<g>ab)){0}ab(?<=(?&g))$`, which libpcre2 10.46 compiles and
         * matches. So the node RECORDS (`widths` NULL, `nbranch` and `at`
         * set) and `pcrec_postresolve` asks the same rule once the graph
         * exists.
         *
         * `pcrec_has_call` IS THE TEST AND NOT "is any width unbounded",
         * because the two are different questions and only this one is stable:
         * a body that is variable-width for an ORDINARY reason (`(?<=a+)`)
         * must still refuse HERE, at parse time, where every call-free
         * lookbehind refusal has always been raised — that is the control this
         * wave keeps byte-identical. Deferring only what genuinely cannot be
         * answered yet is also what keeps the pass's customer list honest.
         *
         * IT OVER-DEFERS, KNOWINGLY AND HARMLESSLY: a call inside a NESTED
         * lookaround in the body (`(?<=a(?=(?&g))b)`) contributes 0 to both
         * widths, so the hook could have answered — `pcrec_has_call` descends
         * into `A_LOOK` and says "call" anyway. The deferred ask returns the
         * identical table, and a second, narrower predicate ("a call on a
         * width-bearing path") would be a third place this module decides what
         * contributes width, for the `A_LOOK` arm of `pcrec_maxw` to disagree
         * with. The cost is one visit in a pass that runs anyway. */
        a->u.look.widths  = NULL;
        a->u.look.nbranch = info.nbr;
    } else {
        long long lo = 0, hi = 0;
        int *w = arena_alloc(&cx->arena, (size_t)info.nbr * sizeof *w);
        if (!la_widths(cx, body, info.nbr, w, &lo, &hi)) {
            char buf[LA_MSG_MAX];
            la_width_refusal(buf, sizeof buf, lo, hi);
            REFUSE(at, "%s", buf);
        }
        a->u.look.widths  = w;
        a->u.look.nbranch = info.nbr;
    }

    /* PROPAGATED, not defaulted — A_CAP's rule and A_ATOMIC's, for their
     * reason: `not_repeatable` is a property of what this construct RETURNS to
     * `p_rep`, and `p_rep` tests the returned node's own flag. Note what this
     * does and does not decide. `(?=a)*` and the other thirteen quantified
     * forms compile (§2.6, and `pcrec_is_bare_anchor` answers FALSE for
     * A_LOOK, which is what lets them); `(?=(?i))*` COMPILES in libpcre2 10.46
     * (measured at this wave) and pcrec refuses it, exactly as pcrec already
     * refuses `((?i))*` and `(?>(?i))*`. That is ONE pre-existing question
     * about a bare option run — parse.c's A_CAP arm records it — and
     * propagating here keeps it one question instead of giving this construct
     * a second, divergent answer. */
    a->not_repeatable = body->not_repeatable;

    /* SR-8/D67: the stamp, from the row this port was dispatched on — the ROW
     * and not a copy of its mask, so `engines` keeps exactly one home and
     * src/opt/select_engine.c can also name the construct. D67 also says
     * STAMP EVERY NODE THE PORT BUILDS; this port builds exactly one. */
    pcrec_ast_stamp(cx, a, rw, at);

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = end;
    return res;
}
