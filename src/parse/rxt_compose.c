/* rxt_compose.c — [DD-13b.W1.3] THE COMPOSER: binding a `.rxt` source's
 * definitions into the target pattern's tree.
 *
 * ONE FILE, because every mechanism in it is meaningless without the others
 * and a reviewer must be able to read the whole thing without leaving it:
 * the sub-parse, the assignment MAP, the injection, the two re-basing
 * passes, and the re-resolution that turns a deferred by-name call into a
 * number. Design: docs/design/dd13_format/w1_impl.md §2 (the mechanism) and
 * §8 (what D89 changed and why §2 alone is not buildable as written).
 *
 * THE ONE-PARAGRAPH VERSION. `pcrec_parse` has already run and has left
 * every by-name subroutine call this pattern could not resolve sitting in
 * `cx->pending_refs` with `deferred` set (DECIDED (6); the flag is
 * `cx->defer_file_refs`, which is on only when a definition set exists). For
 * each such name that the set declares, the definition's own text is
 * SUB-PARSED on the SAME `Ctx` with the numbering scope swapped out, so it
 * is numbered from 1 in its own space and means exactly what it means in its
 * own file; the sub-parse's result is then re-based into the caller's space
 * through a MAP and concatenated onto the caller's root as
 * `A_REP{0,0}(A_CAP{base}(body))`, which is the shape `(?(DEFINE)…)` already
 * desugars to. Binding a definition can defer further names, so the whole
 * thing is a worklist to a fixpoint with a visited set — cycles are legal
 * (self- and mutual recursion compile and match on both oracles, r44-sem M8)
 * and terminate there.
 *
 * WHAT D89 ADDED, AND IT IS THE PART §2 HAS NO MECHANISM FOR. Frank's Q-W1
 * ruling makes a library's groups NON-CAPTURING TO THE CALLER by default,
 * in three tiers:
 *
 *   DELIVERED  the definition NAMES it -> a slot above `ngroups` AND a
 *              `groups[]` row whose `.ref` is the definition's name. This is
 *              the only tier a caller can see, and it is seen BY NAME.
 *   HIDDEN     unnamed, but the definition itself references it (a backref
 *              target, a call target) -> a slot, no row, no name lookup.
 *   ERASED     unnamed and referenced by nothing inside the definition ->
 *              the `A_CAP` is DELETED and it spends NO NUMBER AT ALL, which
 *              is D89(2)(a)'s "rewritten to `(?:…)` … truly non-capturing,
 *              zero slots, and the PCRE2 textual control is the same pattern
 *              byte for byte".
 *
 * A tier that spends no number is not expressible by §2.5's "add `base` to
 * every `A_CAP`" walk, because the survivors must then CLOSE UP. So the
 * offset becomes a MAP, `local number -> final number, or 0 for erased`,
 * which is the ASSIGNMENT TABLE §2.7 already names as the one derivation
 * with three readers (`RX_NCAPS`, the `rx_group_entry` array,
 * `--emit-composed`). The map is strictly more general than the offset it
 * replaces: with nothing erased it IS `+base`, which is why §2.5's MEASURED
 * cell (library `dd` = `(\d)\1`, caller `^(\d)-(?&dd)$`, `dd`'s own group 1
 * -> 3 and `\1` -> `\3`, matching `5-77` and rejecting `5-75`) is still the
 * expected answer.
 *
 * DELIVERY IS DECLARED BY NAMING (DECIDED, w13). D89 point 4 leaves delivery
 * to "the lib's own names" and builds no in-pattern syntax in W1, so: a
 * definition's group is delivered exactly when the definition NAMES it.
 * Naming a group in a library IS the author's declaration that it is part of
 * the library's interface. Every alternative — a head line listing delivered
 * names, a per-target list, an in-pattern marker — either builds W1.4's
 * syntax early or creates a SECOND place an interface is declared, and this
 * project refuses second places (memory
 * `pcrec-general-mechanisms-not-special-cases`). The cost is that a
 * definition cannot name a group PRIVATELY; that is question Q-W3 in
 * w1_impl §8.8, and today's workaround is `(?:…)` plus a comment.
 *
 * WHAT THIS FILE DOES NOT DO. `(?&^.name)` (the caller-scope prefix),
 * `(?&site=name)` (the delivering call) and `--emit-composed` are §1.5's
 * pattern-level extensions and are W1.4's, not W1.3's — none of them is
 * spellable today, so nothing here can reach them. `(?R)`/`(?0)` inside a
 * bound definition is REFUSED (Q-W2, D89 point 3): the ruling is missing,
 * not the meaning.
 */

#include <string.h>

#include "core/internal.h"
#include "gen/enc/enc.h"
#include "parse/parse_mods.h"

/* ---- the saved numbering scope (w1_impl §2.2) --------------------------
 *
 * A definition lives in a different `pattern` line — a different STRING —
 * and the tree makes a SUB-PARSE ON THE SAME `Ctx` the cheap answer: the
 * alternative is a second `Ctx` with its own arena plus a deep node-clone
 * pass, i.e. a second place that must know every `AKind` and every D70
 * payload and that goes stale silently when a kind is added.
 *
 * EVERY FIELD BELOW IS LOAD-BEARING, and `ncap` most of all: it is read
 * DURING the parse, because PCRE2's multi-digit rule makes `\12` a
 * backreference iff the RUNNING count is >= 12 and an octal literal
 * otherwise (`Ctx.ncap`'s own comment). Parsing a definition with the
 * caller's count already advanced would therefore change what the
 * definition MEANS, not merely how it is numbered — which is why
 * w1_impl §3's sabotage row for a forgotten swap tests MEANING and not only
 * renumbering.
 *
 * `pending_refs` is CAPTURED, not merely restored (§2.5's N4). The re-basing
 * pass is keyed on the definition's OWN pending records; if leaving the
 * sub-parse simply put the caller's list back, the very things the pass is
 * keyed on would be gone before it ran. */
typedef struct {
    const char          *pat;
    size_t               patlen;
    size_t               pos;
    unsigned             ncap;
    NamedGroup          *named_groups;
    unsigned             n_named_groups;
    PendingRef          *pending_refs;
    unsigned             n_pending_refs;
    ParseMods           *mods;
    const pcrec_options *opt;
    bool                 in_quote;
    int                  depth;
} RxtScope;

/* One bound definition, in binding (closure) order.
 *
 * [DD-13b.W1.3, D89 addendum 4(1)] THE COMPOSER IS TWO PASSES AND THIS
 * STRUCT IS WHY. Numbering used to happen inside the bind, which was correct
 * while "which of a definition's groups survive" was answerable from the
 * definition alone. It is not any more: addendum 4(1) makes a group survive
 * when it is referenced inside the definition OR exported AND DELIVERED BY
 * SOME SITE IN THIS COMPOSITION — and the delivering sites are not all known
 * until the fixpoint has bound everything, because a definition bound LATER
 * may itself carry the delivering call.
 *
 * So pass 1 SUB-PARSES (scope swap, capture, the refusals a definition's own
 * text earns) and assigns nothing; pass 2 counts the sites, computes each
 * map, re-bases, allocates the per-site slots and injects. Splitting it is
 * what lets the erasure rule be asked once, with the whole composition in
 * hand, instead of guessed per definition. */
typedef struct {
    const RxtDef *def;
    Ast          *body;        /* the sub-parsed subtree, NOT yet re-based */
    NamedGroup   *names;       /* the definition's own, NOT yet re-based   */
    PendingRef   *pend;        /* its captured pending list                */
    int           k;           /* its own group count, 1..k                */
    int           base;        /* the WRAPPER's number (INTERNAL), pass 2  */
    int          *map;         /* local -> final, or 0 for ERASED, pass 2  */
    int           nmap;
    Ast          *inject;      /* A_REP{0,0}(A_CAP{base}(body))            */
    int           nsites;      /* delivering sites naming this definition  */
} Bound;

/* One DELIVERING CALL SITE. A site is a (call node, scope name) pair, and it
 * is per SITE and not per definition on purpose: two delivering calls of one
 * definition under two site names are two scopes with two slot sets (D89
 * addendum point 3), which is exactly the case a per-definition record
 * cannot express. */
typedef struct {
    Bound      *to;            /* the definition it delivers from          */
    Ast        *node;          /* the `A_CALL`, for the retention plan     */
    const char *site;          /* the scope name, or "*" for a flat import */
    size_t      at;            /* the call's offset, for its diagnostics   */
    const char *what;          /* the spelling, for its diagnostics        */
} Site;

typedef struct {
    Ctx    *cx;
    Bound  *bound;
    size_t  nbound;
    Site   *site;
    size_t  nsite, sitecap;
} Composer;

/* ---- looking a name up ------------------------------------------------- */

static const RxtDef *def_by_name(const Ctx *cx, const char *name)
{
    for (size_t i = 0; i < cx->defs->n; i++)
        if (strcmp(cx->defs->v[i].name, name) == 0) return &cx->defs->v[i];
    return NULL;
}

static Bound *bound_by_name(Composer *co, const char *name)
{
    for (size_t i = 0; i < co->nbound; i++)
        if (strcmp(co->bound[i].def->name, name) == 0) return &co->bound[i];
    return NULL;
}

/* ---- the re-basing tree walk (w1_impl §2.5, pass 1 of 2) ---------------
 *
 * Remap every `A_CAP.u.cap.no` through `map`, and SPLICE OUT the wrapper of
 * every group `map` sends to 0 (the ERASED tier). This is deliberately the
 * same traversal `mod_backrefs.c`'s `br_strip_caps` uses for
 * `--no-captures`, down to the iterative `A_CAT`/`A_ALT` spine walks: a flat
 * concatenation is as long as the pattern and this project has paid for that
 * lesson three times (D10/DD-10). The two are not folded into one function
 * because they decide DIFFERENT questions — one asks "did any reference name
 * this group", the other "what is this group's number in the caller's space"
 * — and folding them would make a `--no-captures` composed build ask the
 * first question twice with two different `keep` arrays.
 *
 * AN `A_CALL` IS VISITED AS ITSELF and `u.call.body` is never followed
 * (design §4.4a site 27, `br_strip_caps`' own note): there is nothing to
 * descend into, and following the back edge in a tree REWRITE would rewrite
 * nodes another part of the tree still points at and would not terminate on
 * a recursive callee. Call TARGETS are re-based by the second pass, off the
 * pending records, which is the only place that can tell a locally-resolved
 * call from a deferred one. */
static Ast *rc_remap_caps(Ast *a, const int *map, int nmap)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_CALL:
            return a;
        case A_CAP:
            a->l = rc_remap_caps(a->l, map, nmap);
            if (a->u.cap.no > 0 && a->u.cap.no < nmap) {
                int to = map[a->u.cap.no];
                if (to == 0) { a = a->l; continue; }   /* ERASED */
                a->u.cap.no = to;
            }
            return a;
        case A_LOOK:
        case A_REP: case A_ATOMIC:
            a->l = rc_remap_caps(a->l, map, nmap);
            return a;
        case A_CAT:
            for (Ast *t = a; t->k == A_CAT; t = t->l)
                t->r = rc_remap_caps(t->r, map, nmap);
            {
                Ast *t = a;
                while (t->l->k == A_CAT) t = t->l;
                t->l = rc_remap_caps(t->l, map, nmap);
            }
            return a;
        case A_ALT:
            for (Ast *t = a; t->k == A_ALT; t = t->l)
                t->r = rc_remap_caps(t->r, map, nmap);
            {
                Ast *t = a;
                while (t->l->k == A_ALT) t = t->l;
                t->l = rc_remap_caps(t->l, map, nmap);
            }
            return a;
        }
        return a;
    }
}

/* ---- marking which groups survive -------------------------------------
 *
 * `keep[i]` is true when local group `i` is HIDDEN — the definition's own
 * resolved references reach it. **NAMING A GROUP NO LONGER KEEPS IT**: D89's
 * addendum point 2 revised delivery from "every named group" to "the names
 * the library EXPORTS", and addendum 4(1) narrowed it again to the names some
 * site in THIS composition actually delivers. So this function answers only
 * the internal half, and `rc_assign` adds the delivered half once the site
 * count is known — which is exactly why the composer became two passes.
 *
 * It is derived from the captured `PendingRef` list and from nothing else —
 * in particular NOT from a tree walk, because a tree walk cannot distinguish
 * a call the sub-parse resolved locally from one it deferred, and a deferred
 * call's `target` is 0. */
static void rc_mark_kept(const PendingRef *pend, bool *keep, int nmap)
{
    for (const PendingRef *pr = pend; pr; pr = pr->next) {
        if (pr->deferred) continue;          /* a FILE reference: not local */
        if (pr->kind == PEND_CALL) {
            int t = pr->node->u.call.target;
            if (t > 0 && t < nmap) keep[t] = true;
        } else {
            for (int i = 0; i < pr->node->u.bref.nrefs; i++) {
                int t = pr->node->u.bref.refs[i];
                if (t > 0 && t < nmap) keep[t] = true;
            }
        }
    }
}

/* ---- the pending-record pass (w1_impl §2.5, pass 2 of 2) ---------------
 *
 * Re-base the resolved targets of exactly the references the SUB-PARSE
 * resolved locally. Stating this as one walk with the tree pass hid that the
 * two need different iteration; stating it as two makes the `(?R)` and
 * deferred cases fall out, because neither is in this list with a resolved
 * value.
 *
 * A REFERENCED GROUP IS NEVER ERASED by construction (`rc_mark_kept` above
 * marks exactly these), so `map[t] == 0` here would be an internal
 * inconsistency rather than an input a pattern can produce; the guard is
 * written as `> 0` so a future tier cannot turn it into a silent zero. */
static void rc_rebase_refs(Ctx *cx, PendingRef *pend, const int *map, int nmap)
{
    for (PendingRef *pr = pend; pr; pr = pr->next) {
        if (pr->deferred) continue;
        if (pr->kind == PEND_CALL) {
            int t = pr->node->u.call.target;
            if (t > 0 && t < nmap && map[t] > 0) pr->node->u.call.target = map[t];
            continue;
        }
        /* `A_BREF.refs` IS A `const int *` and the re-base writes a FRESH
         * array rather than casting the const away. It is not defensiveness:
         * `br_name_run` resolves a duplicated name to a RUN whose members
         * are all in the definition's own space, and the emitted matcher
         * reads that array at match time, so an in-place write would be a
         * write through a pointer the type says nobody writes through — the
         * exact shape a future sharing of one run between two nodes would
         * turn into a silent aliasing bug. One arena array per node costs a
         * handful of bytes on a pattern that has a backreference at all. */
        int n = pr->node->u.bref.nrefs;
        if (n <= 0) continue;
        int *fresh = arena_alloc(&cx->arena, (size_t)n * sizeof *fresh);
        for (int i = 0; i < n; i++) {
            int t = pr->node->u.bref.refs[i];
            fresh[i] = (t > 0 && t < nmap && map[t] > 0) ? map[t] : t;
        }
        pr->node->u.bref.refs = fresh;
    }
}

/* ---- finding a whole-pattern recursion inside a definition -------------
 *
 * `(?R)`, `(?0)`, `(?00)` and `\g<0>` all build an `A_CALL` with
 * `u.call.target == 0` and QUEUE NO PENDING RECORD (`mod_recursion.c:41`
 * and `:128`) — which is precisely what makes them findable here and
 * nowhere later. By the time the composer's re-basing runs, `target == 0`
 * has FOUR readings (the arena zero, `(?R)`, a deferred cross-definition
 * call, and a call this pass has not reached yet), and w1_impl §2.5 deleted
 * revision 1's `target == 0` carve-out for exactly that reason. So the test
 * is not "target is 0" but "this `A_CALL` is in the tree and no record in
 * the sub-parse's own pending list mentions it", which is decidable ONLY
 * here, with the definition's captured list in hand.
 *
 * The membership test is linear in the list. A definition is one pattern
 * line and its call count is a handful; the alternative — a mark bit on the
 * node — would be a field on `Ast` for one question asked once, which
 * PARSE-1 forbids for far better reasons than cost. */
static bool rc_recorded(const Ast *a, const PendingRef *pend)
{
    for (const PendingRef *pr = pend; pr; pr = pr->next)
        if (pr->node == a) return true;
    return false;
}

static const Ast *rc_find_root_call(const Ast *a, const PendingRef *pend)
{
    if (!a) return NULL;
    switch (a->k) {
    case A_CALL:
        return rc_recorded(a, pend) ? NULL : a;
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
    case A_BREF:
        return NULL;
    case A_CAP: case A_LOOK: case A_REP: case A_ATOMIC:
        return rc_find_root_call(a->l, pend);
    case A_CAT: case A_ALT: {
        const Ast *h = rc_find_root_call(a->l, pend);
        return h ? h : rc_find_root_call(a->r, pend);
    }
    }
    return NULL;
}

/* ---- binding one definition -------------------------------------------- */

/* The sub-parse's own refusals must name the DEFINITION's file and line, not
 * an offset into a pattern the author never wrote (w1_impl §2.9: provenance
 * is a property of the SUB-PARSE, not a field on a node — `internal.h`'s
 * PARSE-1 invariant says `Ast` carries no position of any kind). `ctx_fail`
 * takes a pattern offset, so the definition's coordinates go in the TEXT and
 * the offset stays the sub-parse's own, which is the only number that
 * locates a failure inside the definition. */
static void rc_bind(Composer *co, const RxtDef *def)
{
    Ctx *cx = co->cx;

    RxtScope sc = {
        cx->pat, cx->patlen, cx->pos, cx->ncap,
        cx->named_groups, cx->n_named_groups,
        cx->pending_refs, cx->n_pending_refs,
        cx->mods, cx->opt, cx->in_quote, cx->depth
    };

    /* [Q-W4, Frank 2026-09-03] A DEFINITION'S OWN `encoding` MUST AGREE WITH
     * THE ARTIFACT'S, AND DISAGREEING IS A REFUSAL RATHER THAN AN IGNORE.
     *
     * A definition does not inherit the target's config (Q-W4, confirmed):
     * its own `flags` seed its sub-parse and nothing else reaches it, which
     * is what makes a library mean the same thing in every file that binds
     * it. `encoding` is the one setting where that rule and the artifact
     * collide — D58 makes encoding a per-PATTERN scalar and a composed
     * artifact has exactly ONE, so a definition asking for a different one
     * is asking for something the format cannot give.
     *
     * IGNORING IT WAS THE OTHER OPTION AND IT IS THE WORSE ONE: a directive
     * that is silently dropped is a population nobody counts, and the author
     * who wrote it has no way to learn it did nothing. Equal or absent is
     * fine, so a library that states the encoding it was written for keeps
     * working in every artifact built at that encoding and refuses — by
     * name, naming both — in one built at another.
     *
     * The comparison is by NAME against the encoding registry's own spelling
     * for the artifact's id, so there is no second name-to-id mapping here:
     * `--encoding` and this line resolve through the same table. */
    if (def->encoding) {
        const PcrecEnc *have = pcrec_enc_by_id(cx->opt->encoding);
        const char *hn = have ? have->name : "(unknown)";
        if (strcmp(def->encoding, hn) != 0)
            /* THE CONTRACT COMES FIRST AND THE ADVICE LAST, because
             * `rxt_fail`'s caller truncates the TAIL: the definition's name,
             * both encodings and the definition's line must survive a long
             * path, and the sentence telling the author what to do about it
             * is the part that may be cut. The file is named too, and it is
             * the second-longest thing here — the same doubled-path cost
             * `lib_chain_text` records — so it goes after the two encodings
             * rather than before them. */
            ctx_fail(cx, 0,
                     "definition '%s' declares `encoding %s` but this "
                     "artifact is '%s' (%s:%zu); one artifact, one encoding",
                     def->name, def->encoding, hn, def->file, def->line);
    }

    /* `mods` is SEEDED FROM THE DEFINITION BLOCK'S OWN `flags`, not restored
     * and not inherited (r45sem M2): format_design §2.6 makes `flags`
     * block-scoped, so a definition that wrote `flags i` must get it and one
     * that did not must NOT pick up the target's. `pcrec_parse_mods_init`
     * seeds `.caseless` from `cx->opt->flags`, so the seed is supplied by
     * swapping a private options copy in for the sub-parse — the ONE field
     * that differs, with everything else (encoding, the capture request, the
     * budgets) staying the target's, because those are properties of the
     * ARTIFACT and a definition has no artifact of its own. */
    pcrec_options defopt = *cx->opt;
    defopt.flags = (defopt.flags & ~(unsigned long long)PCREC_CASELESS)
                 | (def->flags & (unsigned long long)PCREC_CASELESS);

    cx->pat            = def->pattern;
    cx->patlen         = strlen(def->pattern);
    cx->pos            = 0;
    cx->ncap           = 0;
    cx->named_groups   = NULL;
    cx->n_named_groups = 0;
    cx->pending_refs   = NULL;
    cx->n_pending_refs = 0;
    cx->in_quote       = false;
    cx->depth          = 0;
    cx->opt            = &defopt;
    pcrec_parse_mods_init(cx);

    Ast *body = pcrec_parse_info(cx, NULL);

    int          k     = (int)cx->ncap;
    NamedGroup  *names = cx->named_groups;
    PendingRef  *pend  = cx->pending_refs;

    cx->pat            = sc.pat;
    cx->patlen         = sc.patlen;
    cx->pos            = sc.pos;
    cx->named_groups   = sc.named_groups;
    cx->n_named_groups = sc.n_named_groups;
    cx->pending_refs   = sc.pending_refs;
    cx->n_pending_refs = sc.n_pending_refs;
    cx->mods           = sc.mods;
    cx->opt            = sc.opt;
    cx->in_quote       = sc.in_quote;
    cx->depth          = sc.depth;
    /* `ncap` is NOT restored: the caller's count keeps running upward as
     * definitions are injected above it, and `ncap_primary` (frozen before
     * the first bind) is what `rx_info.ngroups` emits. */
    cx->ncap = sc.ncap;

    /* Q-W2, D89 point 3: `(?R)`/`(?0)`/`(?00)`/`\g<0>` inside a bound
     * definition is REFUSED for W1. After injection the two readings — the
     * caller's root, or the definition's own wrapper — are both defensible,
     * and D87 chose mechanisms over silent defaults. The refusal is raised
     * HERE, at the sub-parse, because nothing later can tell it from the
     * three other situations that leave `u.call.target` at 0 (the arena
     * zero, and a deferred cross-definition call). A whole-pattern
     * recursion queues NO pending record, so it is exactly an `A_CALL` the
     * captured list does not mention — which is what this walk tests. */
    {
        const Ast *rec = rc_find_root_call(body, pend);
        if (rec)
            ctx_fail(cx, 0,
                     "definition '%s' (%s:%zu) uses whole-pattern recursion "
                     "((?R), (?0) or \\g<0>) inside a definition, which this "
                     "build refuses: after composition it could mean the "
                     "caller's whole pattern or the definition's own body, "
                     "and the ruling that picks one is not written yet",
                     def->name, def->file, def->line);
    }

    /* [D89 addendum point 2] THE EXPORT LIST IS CHECKED HERE, and this is
     * the only place it can be: `export` names GROUPS, the head reader does
     * not parse patterns, and the sub-parse above is the first moment the
     * definition's own `named_groups` exists. A name the definition does not
     * declare is refused naming BOTH — the export and the definition —
     * because a reader shown only the name cannot tell a typo in the export
     * list from a group that was renamed inside the pattern. */
    for (const char *e = def->exports; e && *e; ) {
        while (*e == ' ' || *e == '\t' || *e == ',') e++;
        if (!*e) break;
        const char *b = e;
        while (*e && *e != ',' && *e != ' ' && *e != '\t') e++;
        size_t elen = (size_t)(e - b);
        bool found = false;
        for (const NamedGroup *g = names; g && !found; g = g->next)
            found = strlen(g->name) == elen && memcmp(g->name, b, elen) == 0;
        if (!found)
            ctx_fail(cx, 0,
                     "definition '%s' exports '%.*s', which it declares no "
                     "capture group for (%s:%zu)",
                     def->name, (int)elen, b, def->file, def->line);
    }

    co->bound[co->nbound].def    = def;
    co->bound[co->nbound].body   = body;
    co->bound[co->nbound].names  = names;
    co->bound[co->nbound].pend   = pend;
    co->bound[co->nbound].k      = k;
    co->bound[co->nbound].nsites = 0;
    co->nbound++;
}

/* ---- pass 2: numbering, erasure, the delivered rows, the injection -----
 *
 * Runs once the fixpoint has bound everything and every delivering site is
 * known, because addendum 4(1)'s erasure rule needs both.
 */
static bool rc_export_lists(const RxtDef *def, const char *want, size_t wlen)
{
    for (const char *e = def->exports; e && *e; ) {
        while (*e == ' ' || *e == '\t' || *e == ',') e++;
        if (!*e) break;
        const char *b = e;
        while (*e && *e != ',' && *e != ' ' && *e != '\t') e++;
        if ((size_t)(e - b) == wlen && memcmp(b, want, wlen) == 0) return true;
    }
    return false;
}

/* Assign this definition's numbers and splice it. */
static void rc_assign(Composer *co, Bound *bd)
{
    Ctx *cx = co->cx;
    const RxtDef *def = bd->def;

    /* THE WRAPPER TAKES A NUMBER, AND IT IS INTERNAL (w1_impl §2.6, D89
     * point 1). `A_CALL.target` is a group number and `callgraph.c` binds by
     * matching `A_CAP.u.cap.no`, so a callable body must hold a number in
     * the same space every other group is in; a separate id space would be a
     * second key in the binder. The number is never authored, never a
     * `groups[]` row and never a name — Frank's Q-W1 ruling withdrew the
     * caller-visible half r45sem had attached to it. */
    int base = (int)cx->ncap + 1;
    int nmap = bd->k + 1;
    bool *keep = arena_alloc(&cx->arena, (size_t)nmap * sizeof *keep);
    int  *map  = arena_alloc(&cx->arena, (size_t)nmap * sizeof *map);

    /* TIER 2, HIDDEN: a group the definition's own resolved references
     * reach. Unchanged since the first version, and D89 addendum point 1
     * reaffirms it — a group-number reference within a pattern always works,
     * so an internally-referenced group is never erased. */
    rc_mark_kept(bd->pend, keep, nmap);

    /* TIER 1, DELIVERED — and addendum 4(1) is why this is a PER-COMPOSITION
     * question rather than a per-definition one. An exported name survives
     * only if some site in THIS composition actually delivers it: "the export
     * list declares what MAY be delivered; the composition decides what IS."
     * So an exported name with no delivering site is ERASED exactly like an
     * unnamed unreferenced one, and a library that exports ten names costs a
     * caller that delivers none of them nothing at all. */
    if (bd->nsites > 0)
        for (const NamedGroup *g = bd->names; g; g = g->next)
            if (g->number > 0 && g->number < nmap &&
                rc_export_lists(def, g->name, strlen(g->name)))
                keep[g->number] = true;

    int next = base;
    for (int i = 1; i < nmap; i++) map[i] = keep[i] ? ++next : 0;

    bd->body = rc_remap_caps(bd->body, map, nmap);
    rc_rebase_refs(cx, bd->pend, map, nmap);
    for (NamedGroup *g = bd->names; g; g = g->next)
        if (g->number > 0 && g->number < nmap)
            g->number = map[g->number];

    cx->ncap = (unsigned)next;
    bd->base = base;
    bd->map  = map;
    bd->nmap = nmap;

    /* THE INJECTION (w1_impl §2.4): `A_REP{0,0}(A_CAP{base}(body))`. Not a
     * new shape — `mod_recursion.c`'s `(?(DEFINE)…)` port builds exactly
     * this, quoting D71 item 4's "the `{0}` layout rule the R34 verifier
     * forced already IS DEFINE's semantics", so `callgraph.c`'s
     * number-to-`A_CAP` bind, the splice/linkage choice, the slot layout and
     * `rx_group_entry.ref` are all reused unchanged.
     *
     * `greedy` is semantically dead at a zero repetition (the emitter writes
     * "X{0}: matches empty, no code") but is set from the SAME scoped
     * `(?U)` state `p_rep` and the DEFINE port both read, so the injected
     * shape and the textual `(?(DEFINE)…)` control produce structurally
     * identical trees and a check can ASSERT that rather than assume it. */
    Ast *cap = pcrec_ast_node(cx, A_CAP);
    cap->l = bd->body;
    cap->u.cap.no = base;

    Ast *rep = pcrec_ast_node(cx, A_REP);
    rep->l = cap;
    rep->u.rep.rmin = 0;
    rep->u.rep.rmax = 0;
    rep->u.rep.greedy = !cx->mods->ungreedy;
    bd->inject = rep;
}

/* ---- the fixpoint ------------------------------------------------------
 *
 * WHICH DEFERRED REFERENCE IS TAKEN NEXT decides the CLOSURE ORDER, which
 * decides the numbers, which a caller can see through `RX_NCAPS` and through
 * the delivered rows' `slot` column. So it is not left to whatever order a
 * prepended list happens to be in: the caller's references are taken in
 * SOURCE ORDER (the list is prepended, so it is walked and the LEFTMOST
 * unbound name is chosen), then each bound definition's own, recursively, in
 * the same rule. That is a depth-independent, text-order closure — the same
 * order a reader gets tracing the file by hand, and the same order the
 * textual oracle control can re-derive from the source without asking the
 * composer.
 *
 * CYCLES ARE LEGAL AND TERMINATE HERE: `bound_by_name` is the visited set,
 * so a definition that reaches itself or reaches back into a caller is bound
 * ONCE and the second reference simply binds to the existing wrapper. */
static const RxtDef *rc_next_wanted(Composer *co, PendingRef *list,
                                    const char **unknown, size_t *at)
{
    const RxtDef *best = NULL;
    size_t        best_at = 0;
    for (PendingRef *pr = list; pr; pr = pr->next) {
        if (!pr->deferred || !pr->name) continue;
        if (bound_by_name(co, pr->name)) continue;
        const RxtDef *d = def_by_name(co->cx, pr->name);
        if (!d) {
            /* A name the set does not declare: not this pass's business, and
             * NOT an error here either — the re-resolution raises it, once,
             * with the leftmost-failure rule the parser already keeps. */
            if (!*unknown || pr->at < *at) { *unknown = pr->name; *at = pr->at; }
            continue;
        }
        if (!best || pr->at < best_at) { best = d; best_at = pr->at; }
    }
    return best;
}

Ast *pcrec_rxt_compose(Ctx *cx, Ast *root)
{
    /* THE EARLY RETURN IS THE IDENTITY CLAIM. Without a definition set this
     * pass is one pointer test, and every artifact pcrec emits without
     * `--source` is byte-identical to before this file existed — which is
     * what makes the identity gate's comparison (A) a real check of this
     * change rather than a tautology. */
    if (!cx->defs || cx->defs->n == 0) return root;

    /* `ncap_primary` is NOT set here: `compile_driver` seeds it from `ncap`
     * on EVERY compile, immediately before this call, so the field is right
     * whether or not this function does anything and `emit_dfa.c` can read
     * it unconditionally. Setting it here as well would be a second writer
     * of one fact, agreeing today and available to disagree later. */

    Composer co;
    co.cx      = cx;
    co.nbound  = 0;
    co.bound   = arena_alloc(&cx->arena, cx->defs->n * sizeof *co.bound);
    co.site    = NULL;
    co.nsite   = 0;
    co.sitecap = 0;

    /* ---- PASS 1: THE FIXPOINT ------------------------------------------
     *
     * Each round takes the leftmost unbound name reachable from the caller
     * or from anything bound so far; binding it may defer more names, which
     * the next round sees. It cannot run more than `defs->n` rounds, because
     * every round binds one definition and `bound_by_name` never lets one be
     * bound twice. NOTHING IS NUMBERED HERE. */
    for (size_t round = 0; round <= cx->defs->n; round++) {
        const char *unknown = NULL;
        size_t      uat     = 0;
        const RxtDef *want = rc_next_wanted(&co, cx->pending_refs,
                                            &unknown, &uat);
        for (size_t i = 0; !want && i < co.nbound; i++)
            want = rc_next_wanted(&co, co.bound[i].pend, &unknown, &uat);
        if (!want) break;
        rc_bind(&co, want);
    }

    /* ---- RE-RESOLUTION -------------------------------------------------
     *
     * Every deferred by-name call now binds to its definition's WRAPPER
     * number, which is the group `callgraph.c` will find. A name the set
     * does not declare RE-RAISES `mod_backrefs.c`'s own refusal — the same
     * sentence at the same offset — so the four `perr` blocks in
     * `tests/recursion/d27/sr_refusals.rxt` are untouched by this step, and
     * a file that composes nothing behaves as it always did.
     *
     * THE TARGET IS FILLED IN PASS 3, not here: a wrapper has no number yet.
     * What this pass does is DECIDE which definition each call reaches, and
     * record a DELIVERING call as a SITE — which is the input addendum
     * 4(1)'s erasure rule needs before any number is assigned.
     *
     * THE LEFTMOST FAILURE IS STILL THE ONE REPORTED, and under composition
     * a bare offset is no longer totally ordered — `pr->at` may be an offset
     * into a DEFINITION's text (r45sem S2). The ordering key is therefore
     * (which list, then offset): the caller's references are compared among
     * themselves first, and only if the caller has none does a definition's
     * unresolved name get reported, naming that definition's file and line
     * so the two coordinate systems are never silently mixed. */
    {
        const PendingRef *worst = NULL;
        for (const PendingRef *pr = cx->pending_refs; pr; pr = pr->next)
            if (pr->deferred && pr->name && !bound_by_name(&co, pr->name) &&
                (!worst || pr->at < worst->at))
                worst = pr;
        if (worst)
            ctx_fail(cx, worst->at,
                     "%s refers to a capture group named '%s', which this "
                     "pattern does not declare", worst->what, worst->name);
    }
    for (size_t i = 0; i < co.nbound; i++)
        for (PendingRef *pr = co.bound[i].pend; pr; pr = pr->next)
            if (pr->deferred && pr->name && !bound_by_name(&co, pr->name))
                ctx_fail(cx, 0,
                         "definition '%s' (%s:%zu): %s refers to '%s', which "
                         "is neither one of its own groups nor a definition "
                         "this source declares",
                         co.bound[i].def->name, co.bound[i].def->file,
                         co.bound[i].def->line, pr->what, pr->name);

    /* ---- PASS 2: COLLECT THE DELIVERING SITES --------------------------
     *
     * In SOURCE ORDER within each list, and the caller's list before any
     * definition's, because the site order decides the slot order a caller
     * reads off `groups[]`. The lists are PREPENDED, so each is reversed
     * into source order before it is walked — the same reason
     * `br_name_run` sorts its own run rather than trusting the walk. */
    for (size_t li = 0; li <= co.nbound; li++) {
        PendingRef *list = li == 0 ? cx->pending_refs : co.bound[li - 1].pend;
        /* count, then walk backwards by index: no allocation, and the
         * reversal is local to this loop rather than a mutation of a list
         * three other passes read. */
        size_t n = 0;
        for (PendingRef *pr = list; pr; pr = pr->next) n++;
        for (size_t back = n; back-- > 0; ) {
            PendingRef *pr = list;
            for (size_t j = 0; j < back; j++) pr = pr->next;
            if (!pr->name || pr->kind != PEND_CALL) continue;
            if (!pr->node->u.call.delivers) continue;
            Bound *b = bound_by_name(&co, pr->name);
            if (!b) continue;            /* refused above */
            if (co.nsite == co.sitecap) {
                size_t nc = co.sitecap ? co.sitecap * 2 : 8;
                Site *nv = arena_alloc(&cx->arena, nc * sizeof *nv);
                for (size_t j = 0; j < co.nsite; j++) nv[j] = co.site[j];
                co.site = nv; co.sitecap = nc;
            }
            co.site[co.nsite].to   = b;
            co.site[co.nsite].node = pr->node;
            co.site[co.nsite].site = pr->node->u.call.deliver_site;
            co.site[co.nsite].at   = pr->at;
            co.site[co.nsite].what = pr->what;
            co.nsite++;
            b->nsites++;
        }
    }

    /* A DELIVERING SITE ON A DEFINITION THAT EXPORTS NOTHING IS A REFUSAL,
     * not a no-op. The default IS "nothing exported" (D89 addendum point 2),
     * so a caller writing `(?&s=lib)` against a library that never published
     * an interface has written something that cannot do anything — and a
     * delivering call that delivers nothing is precisely the half-feature
     * these rulings removed. Naming both sides is what lets the author tell
     * "I misread the library" from "the library forgot its export line". */
    for (size_t i = 0; i < co.nsite; i++)
        if (!co.site[i].to->def->exports)
            ctx_fail(cx, co.site[i].at,
                     "%s delivers from definition '%s', which exports nothing "
                     "(%s:%zu); add an `export` line to it, or call it plainly "
                     "as (?&%s)",
                     co.site[i].what, co.site[i].to->def->name,
                     co.site[i].to->def->file, co.site[i].to->def->line,
                     co.site[i].to->def->name);

    /* ---- PASS 3: NUMBER, ERASE, INJECT --------------------------------- */
    for (size_t i = 0; i < co.nbound; i++) rc_assign(&co, &co.bound[i]);

    for (PendingRef *pr = cx->pending_refs; pr; pr = pr->next) {
        if (!pr->deferred || !pr->name) continue;
        Bound *b = bound_by_name(&co, pr->name);
        if (b) { pr->node->u.call.target = b->base; pr->deferred = false; }
    }
    for (size_t i = 0; i < co.nbound; i++)
        for (PendingRef *pr = co.bound[i].pend; pr; pr = pr->next) {
            if (!pr->deferred || !pr->name) continue;
            Bound *b = bound_by_name(&co, pr->name);
            if (b) { pr->node->u.call.target = b->base; pr->deferred = false; }
        }

    /* ---- PASS 4: THE DELIVERED ROWS, PER SITE --------------------------
     *
     * THE FLAT INJECTION OF EVERY LIBRARY NAME IS GONE (D89 addendum point
     * 3, WITHDRAWN and removed rather than left dormant). A `groups[]` row
     * for a library group now exists only because some site asked for it,
     * and it is named for that site.
     *
     * TWO SHAPES, ONE LOOP:
     *   `(?&site=name)` / `(?&=name)`  ->  row `site.group`, `ref` = the
     *       definition's name. It is a LIBRARY row: it sorts BELOW the
     *       primary's, `nnames` does not count it, and a caller reaches it
     *       by the qualified name.
     *   `(?&*=name)`                   ->  row `group`, `ref` = NULL. The
     *       author asked for it in the CALLER's own scope, so that is where
     *       it goes — counted by `nnames`, found by `match_api.md` §6's
     *       bsearch, indistinguishable from a group the caller declared.
     *       That last clause is exactly what the clash refusal below pays
     *       for, and it is the tradeoff the form exists to make.
     *
     * EACH SITE GETS ITS OWN SLOTS. The definition's own copy of an exported
     * group stays where it is; the site's slot is a new caller-space number,
     * and the retention plan recorded on the node is what will copy one into
     * the other at the site's return. Two sites of one definition therefore
     * cannot alias, which is the whole reason a site is a scope. */
    for (size_t i = 0; i < co.nsite; i++) {
        Site *st = &co.site[i];
        bool flat = strcmp(st->site, "*") == 0;
        int nex = 0;
        for (const NamedGroup *g = st->to->names; g; g = g->next)
            if (g->number > 0 &&
                rc_export_lists(st->to->def, g->name, strlen(g->name))) nex++;
        if (nex == 0) continue;

        int *from = arena_alloc(&cx->arena, (size_t)nex * sizeof *from);
        int *to   = arena_alloc(&cx->arena, (size_t)nex * sizeof *to);
        int  n    = 0;
        /* IN THE ORDER THE `export` LINE WRITES THEM, not the order the
         * definition's `named_groups` list happens to be in. That list is
         * PREPENDED at declaration (`mod_named_groups.c`), so walking it
         * yields REVERSE declaration order — and the slot order is
         * caller-visible through every row's `slot` column, so it must be an
         * order somebody chose. The export line is the definition author's
         * own statement of its interface, which makes it the only order here
         * with a reason behind it. */
        for (const char *e = st->to->def->exports; e && *e; ) {
            while (*e == ' ' || *e == '\t' || *e == ',') e++;
            if (!*e) break;
            const char *eb = e;
            while (*e && *e != ',' && *e != ' ' && *e != '\t') e++;
            size_t elen = (size_t)(e - eb);
            NamedGroup *g = NULL;
            for (NamedGroup *q = st->to->names; q; q = q->next)
                if (strlen(q->name) == elen &&
                    memcmp(q->name, eb, elen) == 0) { g = q; break; }
            if (!g || g->number <= 0) continue;
            char *rowname;
            if (flat) {
                rowname = arena_alloc(&cx->arena, strlen(g->name) + 1);
                memcpy(rowname, g->name, strlen(g->name) + 1);
            } else {
                size_t sl = strlen(st->site), gl = strlen(g->name);
                rowname = arena_alloc(&cx->arena, sl + 1 + gl + 1);
                memcpy(rowname, st->site, sl);
                rowname[sl] = '.';
                memcpy(rowname + sl + 1, g->name, gl + 1);
            }
            /* THE CLASH REFUSAL, BY NAME, and one test covers both shapes
             * because they are one collision: a flat import landing on a
             * caller's own group or on another flat import, and two
             * delivering calls that named the same site. A row name is a
             * caller's whole handle on a delivered group, so two rows
             * sharing one would make `match_api.md` §6's bsearch return
             * whichever the sort happened to put first. */
            for (const NamedGroup *o = cx->named_groups; o; o = o->next)
                if (strcmp(o->name, rowname) == 0)
                    ctx_fail(cx, st->at,
                             "%s would deliver a group named '%s', which this "
                             "pattern already has; give the site another name",
                             st->what, rowname);

            int slot = (int)cx->ncap + 1;
            cx->ncap = (unsigned)slot;

            NamedGroup *row = arena_alloc(&cx->arena, sizeof *row);
            row->name   = rowname;
            row->number = slot;
            row->scope  = flat ? NULL : st->to->def->name;
            row->next   = cx->named_groups;
            cx->named_groups = row;
            cx->n_named_groups++;

            from[n] = g->number;      /* already re-based by rc_assign */
            to[n]   = slot;
            n++;
        }
        /* THE RETENTION PLAN, recorded on the node for the emitter. Filling
         * it here rather than in the emitter is what keeps "which slots does
         * this site deliver" a COMPOSITION fact — the emitter has no notion
         * of an export list — and it is why a plain call carries `n == 0`
         * and copies nothing without the emitter testing for a site. */
        st->node->u.call.deliver_n    = n;
        st->node->u.call.deliver_from = from;
        st->node->u.call.deliver_to   = to;
    }

    /* ---- THE SPLICE ----------------------------------------------------
     *
     * Concatenated onto the caller's root in CLOSURE ORDER, left-leaning, so
     * the spine `br_strip_caps` and every other `A_CAT` walker expects is
     * the spine they get. Nothing is injected when nothing was bound, which
     * is the case for a `--source` build whose target references no
     * definition — and that artifact is then byte-identical to the same
     * pattern built with plain `-p`, which is the cheapest control this step
     * has. */
    for (size_t i = 0; i < co.nbound; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = root;
        cat->r = co.bound[i].inject;
        root = cat;
    }
    return root;
}
