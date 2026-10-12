/* [EMIT-ENTRIES] THE ARTIFACT'S ENTRY TABLE AND ITS LINKAGE CLOSURE
 * (docs/design/compound.md §A.4, build step B0).
 *
 * Every entry an artifact defines is EXPORTED, kept STATIC, or OMITTED:
 *
 *     linkage(e) = EXPORTED     if the request exports e
 *                  STATIC       else if the request keeps e, or e is
 *                               reachable through the edges below from an
 *                               EXPORTED or kept entry
 *                  OMITTED      otherwise
 *
 * The request is `Ctx.emit_in->req`; NULL is the DEFAULT request, which
 * exports the public default set (match_api.md §3¶1, plus `main` under
 * `--emit-main`) and keeps nothing, so every public entry is EXPORTED and
 * every internal one the default set reaches is STATIC: exactly the
 * linkage every artifact had before this table existed. The VM hybrid's
 * embedded DFA search is its first customer: it was a hard-coded
 * `"static "` at its call site and is now STATIC because `<p>_search`
 * reaches it.
 *
 * THE EDGES ARE PER SHAPE, and the shape is stated by the emitter
 * (`PcrecEntryShape`) before it writes any entry: an edge a shape does not
 * have would keep an unused `static` function (a -Wunused-function error in
 * the caller's -Werror build), and a missing one would omit a callee (an
 * implicit declaration). Both directions are the unit check's
 * (`tests/compound/run_compound_unit.sh` B0: every corpus artifact under
 * several requests, compiled -Werror). */
#include "core/internal.h"
#include "enc/enc.h"

/* One dependency edge: `from`'s emitted body calls `to`, on the shapes
 * `when` accepts. */
typedef struct {
    PcrecEntry from, to;
    bool (*when)(const PcrecEntryShape *s);
} EntryEdge;

static bool sh_dfa(const PcrecEntryShape *s)        { return !s->vm; }
static bool sh_vm(const PcrecEntryShape *s)         { return s->vm; }
static bool sh_vm_fwd(const PcrecEntryShape *s)     { return s->vm && s->fwd; }
static bool sh_vm_direct(const PcrecEntryShape *s)  { return s->vm && !s->fwd; }
static bool sh_vm_hybrid(const PcrecEntryShape *s)  { return s->vm && s->hybrid; }
static bool sh_dfa_wrap(const PcrecEntryShape *s)   { return !s->vm && !s->match_own; }
static bool sh_dfa_own(const PcrecEntryShape *s)    { return !s->vm && s->match_own; }
static bool sh_dfa_utf(const PcrecEntryShape *s)    { return !s->vm && s->utf_check; }
static bool sh_dfa_tie(const PcrecEntryShape *s)    { return !s->vm && s->search_match; }
static bool sh_dfa_own_utf(const PcrecEntryShape *s)
{
    return !s->vm && s->match_own && s->utf_check;
}
static bool sh_vm_utf(const PcrecEntryShape *s)     { return s->vm && s->utf_check; }
static bool sh_vm_vars(const PcrecEntryShape *s)    { return s->vm && s->vars; }
static bool sh_always(const PcrecEntryShape *s)     { (void)s; return true; }

/* The edges, read from the emitted text of each shape (emit_dfa.c's
 * `pcrec_emit_dfa`, emit_vm.c's `vm_emit_entries`, the src/enc/ residual
 * templates, `pcrec_emit_main`). */
static const EntryEdge entry_edges[] = {
    /* DFA: the `_in` entries are the un-suffixed ones plus an unused
     * descriptor (`emit_in_entry_defs`). */
    { PCREC_ENTRY_SEARCH_IN,     PCREC_ENTRY_SEARCH,         sh_dfa },
    { PCREC_ENTRY_MATCH_IN,      PCREC_ENTRY_MATCH,          sh_dfa },
    { PCREC_ENTRY_MATCH_CAPS_IN, PCREC_ENTRY_MATCH_CAPS,     sh_dfa },
    /* DFA: the search-and-filter `_match` pair wraps the search entry;
     * where `_match` has its own body (the anchored and nomatch forms)
     * `_match_caps` delegates to it. */
    { PCREC_ENTRY_MATCH,         PCREC_ENTRY_SEARCH,         sh_dfa_wrap },
    { PCREC_ENTRY_MATCH_CAPS,    PCREC_ENTRY_SEARCH,         sh_dfa_wrap },
    { PCREC_ENTRY_MATCH_CAPS,    PCREC_ENTRY_MATCH,          sh_dfa_own },
    /* DFA: a `rev-end` walk that can tie verifies the tie with `_match`. */
    { PCREC_ENTRY_SEARCH,        PCREC_ENTRY_MATCH,          sh_dfa_tie },
    /* DFA: every caller-position prologue runs the subject check
     * (`pcrec_emit_startpos_guard`). A variable forces the VM, so a DFA
     * entry never resolves one. */
    { PCREC_ENTRY_SEARCH,        PCREC_ENTRY_VALID_UPTO,     sh_dfa_utf },
    { PCREC_ENTRY_MATCH,         PCREC_ENTRY_VALID_UPTO,     sh_dfa_own_utf },
    /* VM: an un-suffixed entry runs its `_run` body on its own storage, or
     * forwards to its `_in` sibling ([CC-DIFF]'s forward rungs); an `_in`
     * entry calls its un-suffixed sibling on a NULL descriptor and its
     * `_run` body otherwise. */
    { PCREC_ENTRY_SEARCH,        PCREC_ENTRY_SEARCH_RUN,     sh_vm_direct },
    { PCREC_ENTRY_SEARCH,        PCREC_ENTRY_SEARCH_IN,      sh_vm_fwd },
    { PCREC_ENTRY_SEARCH_IN,     PCREC_ENTRY_SEARCH,         sh_vm },
    { PCREC_ENTRY_SEARCH_IN,     PCREC_ENTRY_SEARCH_RUN,     sh_vm },
    { PCREC_ENTRY_MATCH,         PCREC_ENTRY_MATCH_RUN,      sh_vm_direct },
    { PCREC_ENTRY_MATCH,         PCREC_ENTRY_MATCH_IN,       sh_vm_fwd },
    { PCREC_ENTRY_MATCH_IN,      PCREC_ENTRY_MATCH,          sh_vm },
    { PCREC_ENTRY_MATCH_IN,      PCREC_ENTRY_MATCH_RUN,      sh_vm },
    { PCREC_ENTRY_MATCH_CAPS,    PCREC_ENTRY_MATCH_CAPS_RUN, sh_vm_direct },
    { PCREC_ENTRY_MATCH_CAPS,    PCREC_ENTRY_MATCH_CAPS_IN,  sh_vm_fwd },
    { PCREC_ENTRY_MATCH_CAPS_IN, PCREC_ENTRY_MATCH_CAPS,     sh_vm },
    { PCREC_ENTRY_MATCH_CAPS_IN, PCREC_ENTRY_MATCH_CAPS_RUN, sh_vm },
    /* VM: the search loop asks the hybrid's embedded DFA search for its
     * window; every `_run` body runs the subject check and resolves the
     * variables. */
    { PCREC_ENTRY_SEARCH_RUN,    PCREC_ENTRY_PREFILTER,      sh_vm_hybrid },
    { PCREC_ENTRY_SEARCH_RUN,    PCREC_ENTRY_VALID_UPTO,     sh_vm_utf },
    { PCREC_ENTRY_MATCH_RUN,     PCREC_ENTRY_VALID_UPTO,     sh_vm_utf },
    { PCREC_ENTRY_MATCH_CAPS_RUN, PCREC_ENTRY_VALID_UPTO,    sh_vm_utf },
    { PCREC_ENTRY_SEARCH_RUN,    PCREC_ENTRY_VAR_VALID,      sh_vm_vars },
    { PCREC_ENTRY_MATCH_RUN,     PCREC_ENTRY_VAR_VALID,      sh_vm_vars },
    { PCREC_ENTRY_MATCH_CAPS_RUN, PCREC_ENTRY_VAR_VALID,     sh_vm_vars },
    /* Both: the residual validator steps through the subject validator
     * (enc.h's `requires`), and `main` drives the search entry. */
    { PCREC_ENTRY_VAR_VALID,     PCREC_ENTRY_VALID_UPTO,     sh_always },
    { PCREC_ENTRY_MAIN,          PCREC_ENTRY_SEARCH,         sh_always },
};

/* The residual rows and the src/enc/ ids they are. */
static const struct { PcrecEntry e; unsigned enc; } entry_enc[] = {
    { PCREC_ENTRY_NEXT_POS,   PCREC_ENCE_NEXT_POS },
    { PCREC_ENTRY_VALID_UPTO, PCREC_ENCE_VALID_UPTO },
    { PCREC_ENTRY_VAR_VALID,  PCREC_ENCE_VAR_VALID },
};

#define ENTRY_PUBLIC_MASK   (PCREC_ENTRY_BIT(PCREC_ENTRY_PUBLIC_N) - 1u)
#define ENTRY_MATCHER_MASK  PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH)

/* The default request: the public default set exported, nothing kept. */
static PcrecEntryReq entry_default_req(const Ctx *cx)
{
    PcrecEntryReq r = { ENTRY_PUBLIC_MASK, 0 };
    if (!pcrec_opt_has(cx->opt, PCREC_EMIT_MAIN))
        r.exported &= ~PCREC_ENTRY_BIT(PCREC_ENTRY_MAIN);
    return r;
}

/* The request's closure over the shape's edges: every entry reachable from
 * an exported or kept one, to a fixpoint. */
static unsigned entry_closure(const PcrecEntryShape *s, unsigned roots)
{
    unsigned live = roots;
    for (;;) {
        unsigned m = live;
        for (size_t i = 0; i < sizeof entry_edges / sizeof *entry_edges; i++) {
            const EntryEdge *ed = &entry_edges[i];
            if ((m & PCREC_ENTRY_BIT(ed->from)) && ed->when(s))
                m |= PCREC_ENTRY_BIT(ed->to);
        }
        if (m == live) return live;
        live = m;
    }
}

void pcrec_entry_shape(Ctx *cx, const PcrecEntryShape *shape)
{
    const PcrecEntryReq dr = entry_default_req(cx);
    const PcrecEntryReq *r =
        cx->emit_in && cx->emit_in->req ? cx->emit_in->req : &dr;
    const unsigned noexport = ~ENTRY_PUBLIC_MASK |
        PCREC_ENTRY_BIT(PCREC_ENTRY_INFO) | PCREC_ENTRY_BIT(PCREC_ENTRY_MAIN);
    /* A request this table cannot honour is the CALLER's (the driver's)
     * error, never the pattern's: an internal row exported, `info`/`main`
     * kept static (an object or a program entry has no static form a
     * controller calls), or a closure without the search entry, whose
     * absence would leave the shared static helpers it calls unused. */
    if ((r->exported & ~ENTRY_PUBLIC_MASK) || (r->kept & noexport & ~r->exported &
        (PCREC_ENTRY_BIT(PCREC_ENTRY_INFO) | PCREC_ENTRY_BIT(PCREC_ENTRY_MAIN))))
        pcrec_ctx_fail(cx, 0, "internal error: an entry request exports an "
                       "internal entry or keeps info/main static");
    unsigned live = entry_closure(shape, r->exported | r->kept);
    if (!(live & ENTRY_MATCHER_MASK))
        pcrec_ctx_fail(cx, 0, "internal error: an entry request whose "
                       "closure does not reach the search entry");
    cx->job->entry_exported = r->exported;
    cx->job->entry_static = live & ~r->exported;
    cx->job->entry_shaped = true;
}

PcrecLinkage pcrec_entry_linkage(const Ctx *cx, PcrecEntry e)
{
    /* Asked before the shape was stated is an emitter-order bug: the
     * answer would be a guess. */
    if (!cx->job->entry_shaped)
        pcrec_ctx_fail((Ctx *)cx, 0, "internal error: entry linkage asked "
                       "before the artifact's shape was stated");
    if (cx->job->entry_exported & PCREC_ENTRY_BIT(e)) return PCREC_LINK_EXPORTED;
    if (cx->job->entry_static & PCREC_ENTRY_BIT(e))   return PCREC_LINK_STATIC;
    return PCREC_LINK_OMITTED;
}

const char *pcrec_entry_storage(const Ctx *cx, PcrecEntry e)
{
    return pcrec_entry_linkage(cx, e) == PCREC_LINK_STATIC ? "static " : "";
}

bool pcrec_entry_emitted(const Ctx *cx, PcrecEntry e)
{
    return pcrec_entry_linkage(cx, e) != PCREC_LINK_OMITTED;
}

/* The src/enc/ ids among the residual rows with linkage `want`. */
static unsigned entry_enc_mask(const Ctx *cx, PcrecLinkage want)
{
    unsigned m = 0;
    for (size_t i = 0; i < sizeof entry_enc / sizeof *entry_enc; i++)
        if (pcrec_entry_linkage(cx, entry_enc[i].e) == want) m |= entry_enc[i].enc;
    return m;
}

unsigned pcrec_entry_enc_omit(const Ctx *cx)
{
    return entry_enc_mask(cx, PCREC_LINK_OMITTED);
}

unsigned pcrec_entry_enc_static(const Ctx *cx)
{
    return entry_enc_mask(cx, PCREC_LINK_STATIC);
}
