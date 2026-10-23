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
 * several requests, compiled -Werror).
 *
 * [COMPOUND] E0 (docs/design/compound_entries.md §4.1): THE EDGES ARE
 * DERIVED from `entry_rows[]`, where each entry is a controller row over
 * the parts its body calls. B0's hand list `entry_edges[]` was held against
 * the derivation over the corpus (E0a's both-walks oracle, 0
 * disagreements) and deleted (E0b). */
#include "core/internal.h"
#include "enc/enc.h"

#include <string.h>

/* ---- [COMPOUND] E0: `entry_rows[]` (docs/design/compound_entries.md §4.1)
 *
 * Each entry is a CONTROLLER, a combinator over the parts its body calls,
 * and the edge list is DERIVED from the rows' part references. Every part
 * reference carries the edge's RANK (§3.2), new data written by hand from
 * the emitters' call sites and held by tests/compound/entry_ranks.tsv. A
 * rank is a shape predicate, as `when` is, because one edge can hold call
 * sites of two kinds (the hybrid's entry call is per call, its retry's
 * re-seed per attempt). A part reference has its own `when` too: a
 * controller's body holds a call only on some of the shapes its row serves
 * (the subject check, a `rev-end` tie). The combinator column chooses
 * which ONE emitter writes each entry (E0c, src/gen/emit_comb.c, through
 * `pcrec_entry_comb`); the form column says whether the function is an
 * entry or a search BODY (`pcrec_entry_is_body`). The combinator enum is
 * `PcrecEntryComb` (core/internal.h). */

/* What the function is ([FINDALL-NEXT]): an ENTRY, with its own head and
 * caller-position prologue, or a BODY, a search without that prologue which
 * its callers run after theirs (`<p>__find`): its head is the iterator's
 * scaffold, it writes no guard of its own, and it is copied into its callers
 * unless it keeps label addresses (src/gen/emit_dfa.c's search head). */
typedef enum { EF_ENTRY, EF_BODY } EntryForm;

static PcrecEdgeRank rk_r0(const PcrecEntryShape *s) { (void)s; return PCREC_RANK_R0_RARE; }
static PcrecEdgeRank rk_r1(const PcrecEntryShape *s) { (void)s; return PCREC_RANK_R1_CONDITIONAL; }
static PcrecEdgeRank rk_r2(const PcrecEntryShape *s) { (void)s; return PCREC_RANK_R2_PER_CALL; }
static PcrecEdgeRank rk_r3(const PcrecEntryShape *s) { (void)s; return PCREC_RANK_R3_INNER; }
/* The hybrid's embedded search: per attempt where the retry re-seeds from
 * it (emit_vm.c's `retry_win`/`retry_seed`), else only the entry's call. */
static PcrecEdgeRank rk_prefilter(const PcrecEntryShape *s)
{
    return s->prefilter_retry ? PCREC_RANK_R3_INNER : PCREC_RANK_R2_PER_CALL;
}
/* A compound's first operand: on every call where the floor is live at
 * every position (`\G`), else only at offset 0. */
static PcrecEdgeRank rk_comp_a(const PcrecEntryShape *s)
{
    return s->comp_floor_any ? PCREC_RANK_R2_PER_CALL : PCREC_RANK_R1_CONDITIONAL;
}

/* One call from a controller's body to a part: on the shapes `when` accepts,
 * at the rank `rank` gives. */
typedef struct {
    PcrecEntry part;
    bool (*when)(const PcrecEntryShape *s);
    PcrecEdgeRank (*rank)(const PcrecEntryShape *s);
} PartRef;

/* One entry as a controller on the shapes `when` accepts. */
typedef struct {
    PcrecEntry entry;
    bool (*when)(const PcrecEntryShape *s);
    PcrecEntryComb comb;
    const PartRef *parts;
    int nparts;
    EntryForm form;
} EntryRow;

/* The shapes a row or a part reference serves. */
static bool sh_always(const PcrecEntryShape *s)     { (void)s; return true; }
static bool sh_dfa(const PcrecEntryShape *s)        { return !s->vm; }
static bool sh_vm(const PcrecEntryShape *s)         { return s->vm; }
static bool sh_vm_fwd(const PcrecEntryShape *s)     { return s->vm && s->fwd; }
static bool sh_vm_direct(const PcrecEntryShape *s)  { return s->vm && !s->fwd; }
static bool sh_vm_hybrid(const PcrecEntryShape *s)  { return s->vm && s->hybrid; }
static bool sh_plain_dfa(const PcrecEntryShape *s)  { return !s->vm && !s->compound; }
static bool sh_plain_wrap(const PcrecEntryShape *s) { return sh_plain_dfa(s) && !s->match_own; }
static bool sh_plain_own(const PcrecEntryShape *s)  { return sh_plain_dfa(s) && s->match_own; }
static bool sh_comp(const PcrecEntryShape *s)       { return !s->vm && s->compound; }
static bool sh_comp_b(const PcrecEntryShape *s)     { return sh_comp(s) && s->comp_b; }
static bool sh_utf(const PcrecEntryShape *s)        { return s->utf_check; }
static bool sh_tie(const PcrecEntryShape *s)        { return s->search_match; }
static bool sh_hybrid(const PcrecEntryShape *s)     { return s->hybrid; }
static bool sh_vars(const PcrecEntryShape *s)       { return s->vars; }
static bool sh_cb(const PcrecEntryShape *s)         { return s->comp_b; }
static bool sh_find(const PcrecEntryShape *s)       { return s->find; }
static bool sh_tie_whole(const PcrecEntryShape *s)  { return s->search_match && !s->find; }
static bool sh_cb_whole(const PcrecEntryShape *s)   { return s->comp_b && !s->find; }
static bool sh_whole(const PcrecEntryShape *s)      { return !s->find; }
static bool sh_plain_find(const PcrecEntryShape *s) { return sh_plain_dfa(s) && s->find; }
static bool sh_vm_find(const PcrecEntryShape *s)    { return s->vm && s->find; }
static bool sh_retry(const PcrecEntryShape *s)      { return s->retry; }
static bool sh_hybrid_whole(const PcrecEntryShape *s) { return s->hybrid && !s->find; }
static bool sh_vars_whole(const PcrecEntryShape *s) { return s->vars && !s->find; }
static bool sh_comp_find(const PcrecEntryShape *s)  { return sh_comp(s) && s->find; }

#define PARTS(a) a, (int)(sizeof a / sizeof *a)
#define NOPARTS NULL, 0

/* The part references, one list per controller body, read from the emitted
 * text of each shape (emit_dfa.c's `pcrec_emit_dfa`, emit_compound.c's
 * `first-nonzero` emitters, emit_vm.c's `vm_emit_entries` and search body,
 * the src/enc/ residual templates, `pcrec_emit_main`). */
/* [FINDALL-NEXT] where `<p>_next` is emitted, a DFA `<p>_search` is its
 * caller-position prologue over the body, `<p>__find`, which the iterator's
 * every step runs too; elsewhere it is one function, the body its own. */
static const PartRef pr_dfa_search[] = {
    { PCREC_ENTRY_FIND,        sh_find,      rk_r2 },
    /* a `rev-end` walk that can tie verifies the tie with `_match` */
    { PCREC_ENTRY_MATCH,       sh_tie_whole, rk_r0 },
    /* every caller-position prologue runs the subject check
     * (`pcrec_emit_startpos_guard`) */
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,       rk_r2 },
};
static const PartRef pr_dfa_find[] = {
    /* a `rev-end` walk that can tie verifies the tie with `_match` */
    { PCREC_ENTRY_MATCH,       sh_tie,    rk_r0 },
};
static const PartRef pr_dfa_own[]   = { { PCREC_ENTRY_VALID_UPTO, sh_utf, rk_r2 } };
static const PartRef pr_to_search[] = { { PCREC_ENTRY_SEARCH, sh_always, rk_r2 } };
static const PartRef pr_to_match[]  = { { PCREC_ENTRY_MATCH, sh_always, rk_r2 } };
static const PartRef pr_to_caps[]   = { { PCREC_ENTRY_MATCH_CAPS, sh_always, rk_r2 } };
/* split's `first-nonzero(F @ x, Q @ next_pos(x))` (§B.2): F where the floor
 * can be live, a relocation and Q unless Q is `never`. */
static const PartRef pr_comp_search[] = {
    { PCREC_ENTRY_FIND,        sh_find,     rk_r2 },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,      rk_r2 },
    { PCREC_ENTRY_COMP_A,      sh_whole,    rk_comp_a },
    { PCREC_ENTRY_NEXT_POS,    sh_cb_whole, rk_r1 },
    { PCREC_ENTRY_COMP_B,      sh_cb_whole, rk_r2 },
};
static const PartRef pr_comp_find[] = {
    { PCREC_ENTRY_COMP_A,      sh_always, rk_comp_a },
    { PCREC_ENTRY_NEXT_POS,    sh_cb,     rk_r1 },
    { PCREC_ENTRY_COMP_B,      sh_cb,     rk_r2 },
};
/* the match-here pair (§B.3): F's one attempt at `ctx->pos`, each entry
 * with its own prologue */
static const PartRef pr_comp_match[] = {
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r2 },
    { PCREC_ENTRY_COMP_A,      sh_always, rk_r2 },
};
/* VM: an un-suffixed entry binds its own storage and runs its `_run` body,
 * or forwards to its `_in` sibling ([CC-DIFF]'s forward rungs); an `_in`
 * entry calls its un-suffixed sibling on a NULL descriptor and its `_run`
 * body otherwise. */
static const PartRef pr_vm_search[]     = { { PCREC_ENTRY_SEARCH_RUN, sh_always, rk_r2 } };
static const PartRef pr_vm_search_fwd[] = { { PCREC_ENTRY_SEARCH_IN, sh_always, rk_r2 } };
static const PartRef pr_vm_search_in[]  = {
    { PCREC_ENTRY_SEARCH,      sh_always, rk_r1 },
    { PCREC_ENTRY_SEARCH_RUN,  sh_always, rk_r1 },
};
static const PartRef pr_vm_match[]      = { { PCREC_ENTRY_MATCH_RUN, sh_always, rk_r2 } };
static const PartRef pr_vm_match_fwd[]  = { { PCREC_ENTRY_MATCH_IN, sh_always, rk_r2 } };
static const PartRef pr_vm_match_in[]   = {
    { PCREC_ENTRY_MATCH,       sh_always, rk_r1 },
    { PCREC_ENTRY_MATCH_RUN,   sh_always, rk_r1 },
};
static const PartRef pr_vm_caps[]       = { { PCREC_ENTRY_MATCH_CAPS_RUN, sh_always, rk_r2 } };
static const PartRef pr_vm_caps_fwd[]   = { { PCREC_ENTRY_MATCH_CAPS_IN, sh_always, rk_r2 } };
static const PartRef pr_vm_caps_in[]    = {
    { PCREC_ENTRY_MATCH_CAPS,     sh_always, rk_r1 },
    { PCREC_ENTRY_MATCH_CAPS_RUN, sh_always, rk_r1 },
};
/* VM: the search loop asks the hybrid's embedded DFA search for its window;
 * every `_run` body runs the subject check and resolves the variables.
 * [FINDALL-NEXT] Where `<p>_next` skips a caller-position prologue, the
 * search `_run` static is that prologue over the loop, `<p>__find`. */
static const PartRef pr_vm_search_run[] = {
    { PCREC_ENTRY_FIND,        sh_find,         rk_r2 },
    { PCREC_ENTRY_PREFILTER,   sh_hybrid_whole, rk_prefilter },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,          rk_r2 },
    { PCREC_ENTRY_VAR_VALID,   sh_vars_whole,   rk_r2 },
};
static const PartRef pr_vm_find[] = {
    { PCREC_ENTRY_PREFILTER,   sh_hybrid, rk_prefilter },
    { PCREC_ENTRY_VAR_VALID,   sh_vars,   rk_r2 },
};
static const PartRef pr_vm_run[] = {
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r2 },
    { PCREC_ENTRY_VAR_VALID,   sh_vars,   rk_r2 },
};
/* [FINDALL-NEXT] the iterator (findall_iter.md §2.1): every step runs the
 * search body (`<p>__find` where the search entry has a prologue to skip,
 * else the search itself: a DFA's `<p>_search`, a VM's `<p>_search_run`)
 * and advances with the `next_pos` twin; the once-per-iterator bind runs the
 * subject check where the artifact has one. */
static const PartRef pr_next_dfa[] = {
    { PCREC_ENTRY_FIND,        sh_find,   rk_r2 },
    { PCREC_ENTRY_SEARCH,      sh_whole,  rk_r2 },
    { PCREC_ENTRY_RETRY,       sh_retry,  rk_r1 },
    { PCREC_ENTRY_NEXT_POS,    sh_always, rk_r2 },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r1 },
};
static const PartRef pr_next_vm[] = {
    { PCREC_ENTRY_FIND,        sh_find,   rk_r2 },
    { PCREC_ENTRY_SEARCH_RUN,  sh_whole,  rk_r2 },
    { PCREC_ENTRY_RETRY,       sh_retry,  rk_r1 },
    { PCREC_ENTRY_NEXT_POS,    sh_always, rk_r2 },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r1 },
};
/* `<prefix>_next_n` runs the same step in its loop, and a NULL
 * `capture_spans` through `<prefix>_next` with a local buffer */
static const PartRef pr_next_n_dfa[] = {
    { PCREC_ENTRY_NEXT,        sh_always, rk_r0 },
    { PCREC_ENTRY_FIND,        sh_find,   rk_r3 },
    { PCREC_ENTRY_SEARCH,      sh_whole,  rk_r3 },
    { PCREC_ENTRY_RETRY,       sh_retry,  rk_r1 },
    { PCREC_ENTRY_NEXT_POS,    sh_always, rk_r3 },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r1 },
};
static const PartRef pr_next_n_vm[] = {
    { PCREC_ENTRY_NEXT,        sh_always, rk_r0 },
    { PCREC_ENTRY_FIND,        sh_find,   rk_r3 },
    { PCREC_ENTRY_SEARCH_RUN,  sh_whole,  rk_r3 },
    { PCREC_ENTRY_RETRY,       sh_retry,  rk_r1 },
    { PCREC_ENTRY_NEXT_POS,    sh_always, rk_r3 },
    { PCREC_ENTRY_VALID_UPTO,  sh_utf,    rk_r1 },
};
/* the residual validator steps through the subject validator (enc.h's
 * `requires`) */
static const PartRef pr_var_valid[] = { { PCREC_ENTRY_VALID_UPTO, sh_always, rk_r2 } };

/* THE TABLE, first match per entry: an entry's controller on a shape is its
 * first row whose `when` holds, and an entry with no such row is not part of
 * that shape (the closure must never reach one: `pcrec_entry_shape` checks). */
static const EntryRow entry_rows[] = {
    /* DFA (not a compound) */
    { PCREC_ENTRY_SEARCH,       sh_plain_dfa,  PCREC_COMB_LOCATE_FINISH, PARTS(pr_dfa_search),    EF_ENTRY },
    { PCREC_ENTRY_FIND,         sh_plain_find, PCREC_COMB_LOCATE_FINISH, PARTS(pr_dfa_find),      EF_BODY },
    { PCREC_ENTRY_MATCH,        sh_plain_own,  PCREC_COMB_FINISH_AT,     PARTS(pr_dfa_own),       EF_ENTRY },
    { PCREC_ENTRY_MATCH,        sh_plain_wrap, PCREC_COMB_FINISH_AT,     PARTS(pr_to_search),     EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS,   sh_plain_own,  PCREC_COMB_FINISH_AT,     PARTS(pr_to_match),      EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS,   sh_plain_wrap, PCREC_COMB_FINISH_AT,     PARTS(pr_to_search),     EF_ENTRY },
    /* a compound's controller (emit_compound.c) */
    { PCREC_ENTRY_SEARCH,       sh_comp,       PCREC_COMB_FIRST_NONZERO, PARTS(pr_comp_search),   EF_ENTRY },
    { PCREC_ENTRY_FIND,         sh_comp_find,  PCREC_COMB_FIRST_NONZERO, PARTS(pr_comp_find),     EF_BODY },
    { PCREC_ENTRY_MATCH,        sh_comp,       PCREC_COMB_FINISH_AT,     PARTS(pr_comp_match),    EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS,   sh_comp,       PCREC_COMB_FINISH_AT,     PARTS(pr_comp_match),    EF_ENTRY },
    { PCREC_ENTRY_COMP_A,       sh_comp,       PCREC_COMB_LOCATE_FINISH, NOPARTS,                 EF_ENTRY },
    { PCREC_ENTRY_COMP_B,       sh_comp_b,     PCREC_COMB_LOCATE_FINISH, NOPARTS,                 EF_ENTRY },
    /* DFA and compound: the `_in` entries are the un-suffixed ones plus an
     * unused descriptor (emit_comb.c's `forward`, INERT) */
    { PCREC_ENTRY_SEARCH_IN,    sh_dfa,        PCREC_COMB_FORWARD,       PARTS(pr_to_search),     EF_ENTRY },
    { PCREC_ENTRY_MATCH_IN,     sh_dfa,        PCREC_COMB_FORWARD,       PARTS(pr_to_match),      EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS_IN, sh_dfa,       PCREC_COMB_FORWARD,       PARTS(pr_to_caps),       EF_ENTRY },
    /* VM */
    { PCREC_ENTRY_SEARCH,       sh_vm_direct,  PCREC_COMB_FORWARD,       PARTS(pr_vm_search),     EF_ENTRY },
    { PCREC_ENTRY_SEARCH,       sh_vm_fwd,     PCREC_COMB_FORWARD,       PARTS(pr_vm_search_fwd), EF_ENTRY },
    { PCREC_ENTRY_SEARCH_IN,    sh_vm,         PCREC_COMB_FORWARD,       PARTS(pr_vm_search_in),  EF_ENTRY },
    { PCREC_ENTRY_MATCH,        sh_vm_direct,  PCREC_COMB_FORWARD,       PARTS(pr_vm_match),      EF_ENTRY },
    { PCREC_ENTRY_MATCH,        sh_vm_fwd,     PCREC_COMB_FORWARD,       PARTS(pr_vm_match_fwd),  EF_ENTRY },
    { PCREC_ENTRY_MATCH_IN,     sh_vm,         PCREC_COMB_FORWARD,       PARTS(pr_vm_match_in),   EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS,   sh_vm_direct,  PCREC_COMB_FORWARD,       PARTS(pr_vm_caps),       EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS,   sh_vm_fwd,     PCREC_COMB_FORWARD,       PARTS(pr_vm_caps_fwd),   EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS_IN, sh_vm,        PCREC_COMB_FORWARD,       PARTS(pr_vm_caps_in),    EF_ENTRY },
    { PCREC_ENTRY_SEARCH_RUN,   sh_vm,         PCREC_COMB_LOCATE_FINISH, PARTS(pr_vm_search_run), EF_ENTRY },
    { PCREC_ENTRY_FIND,         sh_vm_find,    PCREC_COMB_LOCATE_FINISH, PARTS(pr_vm_find),       EF_BODY },
    { PCREC_ENTRY_MATCH_RUN,    sh_vm,         PCREC_COMB_FINISH_AT,     PARTS(pr_vm_run),        EF_ENTRY },
    { PCREC_ENTRY_MATCH_CAPS_RUN, sh_vm,       PCREC_COMB_FINISH_AT,     PARTS(pr_vm_run),        EF_ENTRY },
    { PCREC_ENTRY_PREFILTER,    sh_vm_hybrid,  PCREC_COMB_LOCATE_FINISH, NOPARTS,                 EF_ENTRY },
    /* both: the residuals, the stamp object, and `main` driving the search */
    { PCREC_ENTRY_NEXT_POS,     sh_always,     PCREC_COMB_LEAF,          NOPARTS,                 EF_ENTRY },
    { PCREC_ENTRY_VALID_UPTO,   sh_always,     PCREC_COMB_LEAF,          NOPARTS,                 EF_ENTRY },
    { PCREC_ENTRY_VAR_VALID,    sh_always,     PCREC_COMB_LEAF,          PARTS(pr_var_valid),     EF_ENTRY },
    { PCREC_ENTRY_INFO,         sh_always,     PCREC_COMB_DATA,          NOPARTS,                 EF_ENTRY },
    { PCREC_ENTRY_NEXT,         sh_dfa,        PCREC_COMB_ITERATE,       PARTS(pr_next_dfa),      EF_ENTRY },
    { PCREC_ENTRY_NEXT,         sh_vm,         PCREC_COMB_ITERATE,       PARTS(pr_next_vm),       EF_ENTRY },
    { PCREC_ENTRY_NEXT_N,       sh_dfa,        PCREC_COMB_ITERATE,       PARTS(pr_next_n_dfa),    EF_ENTRY },
    { PCREC_ENTRY_NEXT_N,       sh_vm,         PCREC_COMB_ITERATE,       PARTS(pr_next_n_vm),     EF_ENTRY },
    { PCREC_ENTRY_RETRY,        sh_retry,      PCREC_COMB_FINISH_AT,     NOPARTS,                 EF_BODY },
    { PCREC_ENTRY_MAIN,         sh_always,     PCREC_COMB_DRIVER,        PARTS(pr_to_search),     EF_ENTRY },
};

#define NROWS ((int)(sizeof entry_rows / sizeof *entry_rows))

/* `e`'s controller on shape `s`: its first row whose `when` holds, or NULL
 * where `e` is not part of the shape. */
static const EntryRow *entry_row_of(const PcrecEntryShape *s, PcrecEntry e)
{
    for (int i = 0; i < NROWS; i++)
        if (entry_rows[i].entry == e && entry_rows[i].when(s)) return &entry_rows[i];
    return NULL;
}

/* The shape's DERIVED edge relation: `edge_rank[from][to]` = rank + 1, 0 for
 * no edge. */
static void entry_derive(const PcrecEntryShape *s,
                         unsigned char edge_rank[PCREC_ENTRY_N][PCREC_ENTRY_N])
{
    memset(edge_rank, 0, PCREC_ENTRY_N * sizeof *edge_rank);
    for (int e = 0; e < PCREC_ENTRY_N; e++) {
        const EntryRow *r = entry_row_of(s, (PcrecEntry)e);
        if (!r) continue;
        for (int k = 0; k < r->nparts; k++)
            if (r->parts[k].when(s)) {
                unsigned char v = (unsigned char)(r->parts[k].rank(s) + 1);
                if (v > edge_rank[e][r->parts[k].part])
                    edge_rank[e][r->parts[k].part] = v;
            }
    }
}

static const char *const entry_names[PCREC_ENTRY_N] = {
    "search", "search_in", "match", "match_in", "match_caps", "match_caps_in",
    "next_pos", "valid_upto", "var_valid", "info", "main", "next", "next_n",
    "search_run", "match_run", "match_caps_run", "prefilter", "comp_a", "comp_b",
    "find", "retry",
};

const char *pcrec_entry_name(PcrecEntry e)
{
    return e < PCREC_ENTRY_N ? entry_names[e] : "?";
}

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

/* The request's closure over the shape's derived edges `er`: every entry
 * reachable from an exported or kept one, to a fixpoint. */
static unsigned entry_closure(unsigned char er[PCREC_ENTRY_N][PCREC_ENTRY_N],
                              unsigned roots)
{
    unsigned live = roots;
    for (;;) {
        unsigned m = live;
        for (int f = 0; f < PCREC_ENTRY_N; f++)
            if (m & PCREC_ENTRY_BIT(f))
                for (int t = 0; t < PCREC_ENTRY_N; t++)
                    if (er[f][t]) m |= PCREC_ENTRY_BIT(t);
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
    unsigned char er[PCREC_ENTRY_N][PCREC_ENTRY_N];
    entry_derive(shape, er);
    /* [ENTRY-TABLE] E1: the part-layout render reads the derived edges for
     * each part's callers and rank (src/gen/part_layout.c). */
    memcpy(cx->job->pl.er, er, sizeof er);
    if (cx->emit_in && cx->emit_in->edge_rank)
        memcpy(cx->emit_in->edge_rank, er, sizeof er);
    unsigned live = entry_closure(er, r->exported | r->kept);
    /* An entry the closure reaches with no row on this shape would be
     * emitted from no controller: the table's gap, never the request's. */
    for (int e = 0; e < PCREC_ENTRY_N; e++)
        if ((live & PCREC_ENTRY_BIT(e)) && !entry_row_of(shape, (PcrecEntry)e))
            pcrec_ctx_fail(cx, 0, "internal error: entry %s reached with no "
                           "row of entry_rows[] on this shape",
                           pcrec_entry_name((PcrecEntry)e));
    if (!(live & ENTRY_MATCHER_MASK))
        pcrec_ctx_fail(cx, 0, "internal error: an entry request whose "
                       "closure does not reach the search entry");
    cx->job->entry_exported = r->exported;
    cx->job->entry_static = live & ~r->exported;
    for (int e = 0; e < PCREC_ENTRY_N; e++) {
        const EntryRow *row = entry_row_of(shape, (PcrecEntry)e);
        cx->job->entry_comb[e] = row ? (unsigned char)(row->comb + 1) : 0;
        if (row && row->form == EF_BODY) cx->job->entry_body |= PCREC_ENTRY_BIT(e);
    }
    cx->job->entry_shaped = true;
}

PcrecEntryComb pcrec_entry_comb(const Ctx *cx, PcrecEntry e)
{
    /* Asked before the shape, or of an entry the shape has no row for, is an
     * emitter's bug: an entry written by no row's emitter. */
    if (!cx->job->entry_shaped || !cx->job->entry_comb[e])
        pcrec_ctx_fail((Ctx *)cx, 0, "internal error: entry %s has no row of "
                       "entry_rows[] on this shape to write it",
                       pcrec_entry_name(e));
    return (PcrecEntryComb)(cx->job->entry_comb[e] - 1);
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

bool pcrec_entry_is_body(const Ctx *cx, PcrecEntry e)
{
    return (cx->job->entry_body & PCREC_ENTRY_BIT(e)) != 0;
}

bool pcrec_iter_requested(const Ctx *cx)
{
    return pcrec_entry_requested(cx, PCREC_ENTRY_NEXT) ||
           pcrec_entry_requested(cx, PCREC_ENTRY_NEXT_N);
}

bool pcrec_entry_requested(const Ctx *cx, PcrecEntry e)
{
    const PcrecEntryReq dr = entry_default_req(cx);
    const PcrecEntryReq *r =
        cx->emit_in && cx->emit_in->req ? cx->emit_in->req : &dr;
    return ((r->exported | r->kept) & PCREC_ENTRY_BIT(e)) != 0;
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
