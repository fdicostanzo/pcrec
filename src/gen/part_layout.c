/* src/gen/part_layout.c — [ENTRY-TABLE] E1 THE PART-LAYOUT TABLES
 * (docs/design/compound_entries.md rev 4 §3.2.2-§3.4, §3.6, §5.1 E1;
 * D163 addenda 8-12; the contract is docs/spec/tuning.md §2.51-§2.53 and
 * §5.3-§5.4).
 *
 * A PART is a static function an artifact's entries call: the VM hybrid's
 * embedded search, a compound's parts. Its LAYOUT is how it is linked into
 * its callers -- a copy in each (`always_inline`) or one out-of-line body
 * they call (`noipa`, guarded) -- never what
 * it computes, so every layout answers identically (I1). Three caller-set
 * controls decide it (`pcrec_options.part_layout`/`part_inline_rank`/
 * `part_residual`); the `--tune` position supplies a preset for each, and
 * every preset cell is empty today (src/core/tune.c), so an artifact's layout
 * moves only where a caller sets a control.
 *
 * FOUR DECLARED FIRST-MATCH TABLES, every conjunct listed (D163 addendum
 * 4), no decision outside them; the render and both listings read each
 * layout's text off [ATTR-TABLE]'s one table (src/gen/attr_text.c):
 *
 *   `art_rows[]`  the ARTIFACT table, once per attempt, every row applied in
 *                 order within its group: K resolves the controls; one of
 *                 T1/TM/T2 resolves `measured`; T0 (nothing to lay out: no
 *                 mark is written, byte-identical by construction) or T3.
 *   `part_rows[]` the PART table, first match per part, constraint rows
 *                 P1-P3 ahead of every control row, total (P10).
 *   `wrap_rows[]` the WRAPPER table, for a caller that only forwards to a
 *                 part a shared row wrote. No such caller exists before the
 *                 iterator and the wrappers' static twins are built (I3), so
 *                 its population is zero today and the listing says so.
 *   `head_rows[]` the HEAD-MARK table: which entry's mark a search head
 *                 writes (a part's shell row, its own subject, or none).
 *
 * I5, THE LAYOUT IS RENDERED AFTER EVERY LENGTH DECISION. Under T3 the
 * search head of every subject writes a MARK (`pcrec_part_head_mark`) and
 * the stamp's place writes one too; the marks' bytes are subtracted by both
 * decision views (StrBuf.layout_bytes), so no rung, ladder step, cap or stamp
 * reads layout text. `pcrec_part_layout_render` runs in `compile_driver`
 * after the size caps and their notes, builds each part's record from the
 * entry table's DERIVED edges (`Job.pl.er`, src/gen/entries.c) and the facts
 * the emitters recorded, walks the part table and replaces every mark. A
 * compound's part writes its SHELL's mark (its `PcrecEmitIn.part_entry`) and
 * leaves it for the shell's render, as it leaves its prefix placeholder.
 *
 * D163 ADDENDUM 12 HOLDS BY CONSTRUCTION: a row writes an attribute on a
 * static part's definition and nothing else. No row adds a call, so no
 * control can create an edge from one exported entry to another. */
#include "core/internal.h"

#include <stdlib.h>
#include <string.h>

/* ---- the vocabulary (core/part_layout.def) ------------------------------ */

static const char *const class_tok[PCREC_PART_NCLASS] = {
#define PL_CLASS(v, tok, subj) [v] = tok,
#include "core/part_layout.def"
};
static const char *const value_tok[] = {
    [PCREC_PART_UNSET] = "unset",
#define PL_VALUE(v, tok, m) [v] = tok,
#include "core/part_layout.def"
};
static const char *const rank_tok[] = {
    [PCREC_PART_RANK_UNSET] = "unset",
#define PL_RANK(v, tok, m) [v] = tok,
#include "core/part_layout.def"
};
enum {
#define PL_WHY(id, tok, m) id,
#include "core/part_layout.def"
    PL_NWHY
};
static const char *const why_tok[PL_NWHY] = {
#define PL_WHY(id, tok, m) [id] = tok,
#include "core/part_layout.def"
};
static const char *const edge_rank_tok[PCREC_RANK_N] = { "R0", "R1", "R2", "R3" };

/* ---- the subjects and the owned functions (§3.1) ------------------------
 *
 * A SUBJECT is in exactly one control class; an OWNED function has an owner
 * that writes its attribute and no class, so no control can name it. Only
 * functions with a row in the entry table are recorded: A1's other helpers,
 * A2's `_deep` and A4's seam are owned too, are never marked and so never
 * laid out; tests/partlayout's attribute census holds every emitted
 * attribute to its writer. */
static const struct { PcrecEntry e; int cls; } subjects[] = {
    { PCREC_ENTRY_PREFILTER, PCREC_PART_PREFILTER },
    { PCREC_ENTRY_COMP_A,    PCREC_PART_COMPOUND },
    { PCREC_ENTRY_COMP_B,    PCREC_PART_COMPOUND },
};
static const PcrecEntry owned[] = {
    PCREC_ENTRY_SEARCH_RUN, PCREC_ENTRY_MATCH_RUN, PCREC_ENTRY_MATCH_CAPS_RUN,
};

#define NSUBJ  ((int)(sizeof subjects / sizeof subjects[0]))
#define NOWNED ((int)(sizeof owned / sizeof owned[0]))

/* `e`'s class, or -1 where `e` is no subject. */
static int subject_class(PcrecEntry e)
{
    for (int i = 0; i < NSUBJ; i++)
        if (subjects[i].e == e) return subjects[i].cls;
    return -1;
}

/* ---- θ_hot (§3.3) --------------------------------------------------------
 *
 * The rank threshold `measured` reads from the active measurement set. No
 * shipped compile carries a set ([MEASURE-SET] M0 is not built; the harness
 * lever's set is the kit's and holds no pcrec-derived row), so the answer is
 * ABSENT on every compile today and row TM/T2 have no witness. */
typedef enum { THETA_ABSENT, THETA_NONE, THETA_RANK } Theta;

/* The active set's `θ_hot`: absent, `none`, or a rank (into `*rank`). */
static Theta theta_hot(const Ctx *cx, int *rank)
{
    (void)cx;
    *rank = PCREC_PART_RANK_UNSET;
    return THETA_ABSENT;
}

/* ---- the artifact table (§3.4) ------------------------------------------ */

typedef enum { AG_ALWAYS, AG_MEASURED, AG_LAYOUT } ArtGroup;

typedef struct {
    const char *id, *name;
    ArtGroup group;            /* ALWAYS: applies; the others: first match */
    const char *conj, *writes; /* the listing's text */
    bool (*holds)(Ctx *cx, PcrecPartLayout *pl);
    void (*apply)(Ctx *cx, PcrecPartLayout *pl);
} ArtRow;

static bool art_always(Ctx *cx, PcrecPartLayout *pl) { (void)cx; (void)pl; return true; }

/* K: each control is the caller's value where set, else the preset's cell,
 * else unset. One rule for all three, so a value means the same whoever set
 * it; the presets set no class value (§3.2.3). */
static void art_resolve(Ctx *cx, PcrecPartLayout *pl)
{
    const pcrec_options *o = cx->opt;
    pl->residual = o->part_residual ? o->part_residual
                                    : pcrec_tune_part_residual(o->tune);
    pl->rank = o->part_inline_rank ? o->part_inline_rank
                                   : pcrec_tune_part_inline_rank(o->tune);
    const uint32_t preset = pcrec_tune_part_layout(o->tune);
    pl->classes = 0;
    for (int k = 0; k < PCREC_PART_NCLASS; k++) {
        int v = PCREC_PART_LAYOUT_GET(o->part_layout, k);
        if (!v) v = PCREC_PART_LAYOUT_GET(preset, k);
        PCREC_PART_LAYOUT_SET(pl->classes, k, v);
    }
}

static bool art_unmeasured(Ctx *cx, PcrecPartLayout *pl)
{
    int r;
    return pl->rank == PCREC_PART_RANK_MEASURED && theta_hot(cx, &r) == THETA_ABSENT;
}
static void art_decline_unmeasured(Ctx *cx, PcrecPartLayout *pl)
{
    (void)cx;
    pl->rank = PCREC_PART_RANK_NONE;
    pl->why = PL_WHY_UNMEASURED;
}
static bool art_measured(Ctx *cx, PcrecPartLayout *pl)
{
    int r;
    return pl->rank == PCREC_PART_RANK_MEASURED && theta_hot(cx, &r) == THETA_RANK;
}
static void art_take_measured(Ctx *cx, PcrecPartLayout *pl)
{
    int r;
    (void)theta_hot(cx, &r);
    pl->rank = r;
    pl->rank_set = true;
}
static bool art_none(Ctx *cx, PcrecPartLayout *pl)
{
    int r;
    return pl->rank == PCREC_PART_RANK_MEASURED && theta_hot(cx, &r) == THETA_NONE;
}
static void art_decline_none(Ctx *cx, PcrecPartLayout *pl)
{
    (void)cx;
    pl->rank = PCREC_PART_RANK_NONE;
    pl->why = PL_WHY_NO_MATERIAL;
}

/* T0's three conjuncts: every class value unset or `auto`, the threshold
 * unset or `none`, the residual unset or `auto`. */
static bool art_as_emitted(Ctx *cx, PcrecPartLayout *pl)
{
    (void)cx;
    for (int k = 0; k < PCREC_PART_NCLASS; k++)
        if (PCREC_PART_LAYOUT_GET(pl->classes, k) > PCREC_PART_AUTO) return false;
    return (pl->rank == PCREC_PART_RANK_UNSET || pl->rank == PCREC_PART_RANK_NONE) &&
           pl->residual <= PCREC_PART_AUTO;
}
static void art_keep(Ctx *cx, PcrecPartLayout *pl) { (void)cx; pl->t3 = false; }
static void art_lay_out(Ctx *cx, PcrecPartLayout *pl) { (void)cx; pl->t3 = true; }

static const ArtRow art_rows[] = {
    { "K",  "resolve",         AG_ALWAYS,
      "(always)",
      "each control := the caller's value if set, else the position's preset cell, else unset",
      art_always, art_resolve },
    { "T1", "rank-unmeasured", AG_MEASURED,
      "the threshold is `measured`; the active set has no theta_hot",
      "the threshold := none; _PART_LAYOUT_WHY \"threshold-unmeasured\"",
      art_unmeasured, art_decline_unmeasured },
    { "TM", "rank-measured",   AG_MEASURED,
      "the threshold is `measured`; the active set's theta_hot is a rank",
      "the threshold := theta_hot (stamped rank=R@set)",
      art_measured, art_take_measured },
    { "T2", "rank-none",       AG_MEASURED,
      "the threshold is `measured`; theta_hot is none",
      "the threshold := none; _PART_LAYOUT_WHY \"no-material-rank\"",
      art_none, art_decline_none },
    { "T0", "as-emitted",      AG_LAYOUT,
      "every class value is unset or auto; the threshold is unset or none; the residual is unset or auto",
      "every function keeps its default layout; no mark, no part table",
      art_as_emitted, art_keep },
    { "T3", "per-part",        AG_LAYOUT,
      "(otherwise)",
      "consult the part table for each part; <PREFIX>_PART_LAYOUT",
      art_always, art_lay_out },
};
#define NART ((int)(sizeof art_rows / sizeof art_rows[0]))

/* Runs the artifact table once per attempt: every ALWAYS row, then the first
 * holding row of each first-match group, in table order. */
static void art_walk(Ctx *cx)
{
    PcrecPartLayout *pl = &cx->job->pl;
    if (pl->resolved) return;
    pl->resolved = true;
    pl->why = -1;
    bool fired[AG_LAYOUT + 1] = { false };
    for (int i = 0; i < NART; i++) {
        const ArtRow *r = &art_rows[i];
        if (r->group != AG_ALWAYS && fired[r->group]) continue;
        if (!r->holds(cx, pl)) continue;
        fired[r->group] = true;
        r->apply(cx, pl);
        pl->arow[pl->narow++] = (unsigned char)i;
    }
    if (!fired[AG_LAYOUT])
        pcrec_ctx_fail(cx, 0, "internal error: part layout: the artifact table is not total");
}

bool pcrec_part_layout_active(Ctx *cx)
{
    art_walk(cx);
    return cx->job->pl.t3;
}

/* ---- the part table (§3.4) ---------------------------------------------- */

typedef struct {
    const char *id, *name, *conj;
    int layout;      /* PCREC_PART_AUTO/_SHARED/_INLINE, or 0: as emitted */
    bool held;       /* a constraint row: it can hold a request */
    bool (*holds)(const PcrecPlPart *p, const PcrecPartLayout *pl);
} PartRow;

/* The minimum edge rank the threshold inlines, or -1 for none/unset. */
static int rank_floor(int thr)
{
    switch (thr) {
    case PCREC_PART_RANK_R3: return PCREC_RANK_R3_INNER;
    case PCREC_PART_RANK_R2: return PCREC_RANK_R2_PER_CALL;
    case PCREC_PART_RANK_R1: return PCREC_RANK_R1_CONDITIONAL;
    case PCREC_PART_RANK_R0: return PCREC_RANK_R0_RARE;
    default:                 return -1;
    }
}

static int class_value(const PcrecPlPart *p, const PcrecPartLayout *pl)
{
    return PCREC_PART_LAYOUT_GET(pl->classes, p->cls);
}

static bool pr_owned(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)pl; return p->cls < 0; }
static bool pr_not_copyable(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)pl; return !p->copyable; }
static bool pr_single(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)pl; return p->callers == 1; }
static bool pr_cls_shared(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ return class_value(p, pl) == PCREC_PART_SHARED; }
static bool pr_cls_inline(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ return class_value(p, pl) == PCREC_PART_INLINE; }
static bool pr_cls_auto(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ return class_value(p, pl) == PCREC_PART_AUTO; }
static bool pr_rank_hot(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ int f = rank_floor(pl->rank); return f >= 0 && (int)p->rank >= f; }
static bool pr_res_shared(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)p; return pl->residual == PCREC_PART_SHARED; }
static bool pr_res_inline(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)p; return pl->residual == PCREC_PART_INLINE; }
static bool pr_always(const PcrecPlPart *p, const PcrecPartLayout *pl)
{ (void)p; (void)pl; return true; }

/* P1 and P2 are HARD (an owner's load-bearing attribute; gcc's refusal to
 * copy a label table or inline a computed goto); P3 is a MEASURED policy
 * (sharing a single-caller part costs bytes for nothing, H3). All three come
 * before every control row, so no control overrides them. P2 writes exactly
 * what the body's head carries today and adds no attribute (design §3.8,
 * F3): gcc keeps such a body out of line by itself, so under a control on
 * any class its head is the default's byte for byte. */
static const PartRow part_rows[] = {
    { "P1",  "owned",           "the function is OWNED (an owner writes its attribute)",
      0,                 true,  pr_owned },
    { "P2",  "not-copyable",    "copyable(part) is false (a label table or a computed goto)",
      0,                 true,  pr_not_copyable },
    { "P3",  "single-caller",   "callers(part) = 1",
      PCREC_PART_AUTO,   true,  pr_single },
    { "P4",  "class-shared",    "the part's class value is shared",
      PCREC_PART_SHARED, false, pr_cls_shared },
    { "P5",  "class-inline",    "the part's class value is inline",
      PCREC_PART_INLINE, false, pr_cls_inline },
    { "P6",  "class-auto",      "the part's class value is auto",
      PCREC_PART_AUTO,   false, pr_cls_auto },
    { "P7",  "rank-hot",        "the threshold is a rank; the part's rank is at or above it",
      PCREC_PART_INLINE, false, pr_rank_hot },
    { "P8",  "residual-shared", "the residual is shared",
      PCREC_PART_SHARED, false, pr_res_shared },
    { "P9",  "residual-inline", "the residual is inline",
      PCREC_PART_INLINE, false, pr_res_inline },
    { "P10", "residual-auto",   "(otherwise: the residual is auto or unset)",
      PCREC_PART_AUTO,   false, pr_always },
};
#define NPART ((int)(sizeof part_rows / sizeof part_rows[0]))

/* ---- the wrapper table (§3.4 W1/W2) -------------------------------------
 *
 * For each caller of a part P4/P8 shared whose own row only FORWARDS to it:
 * W1 keeps a pass-through `return part(args);` (gcc's `jmp`), W2 keeps the
 * caller's adaptation and its call. A forward row's emitter passes its
 * arguments unchanged (src/gen/emit_comb.c), so `forwardable` is that row's
 * combinator; neither row writes new text. No entry row forwards to a part
 * today (a forward row's callee is an exported sibling until I3 gives it a
 * static twin), so the walk reaches no wrapper. */
typedef struct {
    const char *id, *name, *conj, *writes;
    bool forwards;   /* the caller is counted as a wrapper */
    bool (*holds)(const Ctx *cx, PcrecEntry caller);
} WrapRow;

static bool wr_forwardable(const Ctx *cx, PcrecEntry caller)
{ return cx->job->entry_comb[caller] == PCREC_COMB_FORWARD + 1; }
static bool wr_always(const Ctx *cx, PcrecEntry caller)
{ (void)cx; (void)caller; return true; }

static const WrapRow wrap_rows[] = {
    { "W1", "forward", "forwardable(w): the wrapper's row is `forward` (its arguments pass unchanged)",
      "return part(args); -- gcc's tail jump, no frame", true, wr_forwardable },
    { "W2", "adapt",   "(otherwise)",
      "the wrapper's own adaptation and a call (a frame; a canary under -fstack-protector-strong)",
      false, wr_always },
};
#define NWRAP ((int)(sizeof wrap_rows / sizeof wrap_rows[0]))

/* The number of `part`'s callers whose first holding wrapper row forwards. */
static int wrapper_count(const Ctx *cx, PcrecEntry part)
{
    int n = 0;
    for (int f = 0; f < PCREC_ENTRY_N; f++) {
        if (!cx->job->pl.er[f][part] || !pcrec_entry_emitted(cx, (PcrecEntry)f))
            continue;
        for (int r = 0; r < NWRAP; r++)
            if (wrap_rows[r].holds(cx, (PcrecEntry)f)) {
                n += wrap_rows[r].forwards;
                break;
            }
    }
    return n;
}

/* ---- the records (§3.2 callers and rank) --------------------------------
 *
 * `callers(part)` counts the distinct FUNCTIONS holding a call site to it,
 * after every function an owner makes `always_inline` is folded into its own
 * callers (§3.2 [r3 CE-8]): the prefilter of a frameless hybrid at the
 * `inline` rung has two callers (`_search`, `_search_in`), at `forward` one.
 * A part's rank is its hottest in-edge's. Both read the derived edges only. */
static void part_callers_rank(const Ctx *cx, PcrecEntry part,
                              unsigned char *callers, unsigned char *rank)
{
    const PcrecPartLayout *pl = &cx->job->pl;
    unsigned set = 0, done = 0;
    int r = 0;
    for (int f = 0; f < PCREC_ENTRY_N; f++)
        if (pl->er[f][part] && pcrec_entry_emitted(cx, (PcrecEntry)f)) {
            set |= PCREC_ENTRY_BIT(f);
            if (pl->er[f][part] - 1 > r) r = pl->er[f][part] - 1;
        }
    for (bool more = true; more; ) {
        more = false;
        for (int f = 0; f < PCREC_ENTRY_N; f++) {
            if (!(set & pl->owned_inline & PCREC_ENTRY_BIT(f)) ||
                (done & PCREC_ENTRY_BIT(f)))
                continue;
            done |= PCREC_ENTRY_BIT(f);
            set &= ~PCREC_ENTRY_BIT(f);
            for (int g = 0; g < PCREC_ENTRY_N; g++)
                if (g != f && pl->er[g][f] && pcrec_entry_emitted(cx, (PcrecEntry)g))
                    set |= PCREC_ENTRY_BIT(g);
            more = true;
        }
    }
    int n = 0;
    for (int f = 0; f < PCREC_ENTRY_N; f++) n += (set >> f) & 1u;
    *callers = (unsigned char)n;
    *rank = (unsigned char)r;
}

/* `e`'s body can be copied into a caller: the VM hybrid's prefilter is this
 * compile's DFA body, a compound's part reports its own. */
static bool part_copyable(const Ctx *cx, PcrecEntry e)
{
    const PcrecCompShell *sh = cx->job->comp_shell;
    if (e == PCREC_ENTRY_COMP_A) return sh && sh->facts[0].copyable;
    if (e == PCREC_ENTRY_COMP_B) return sh && sh->facts[1].copyable;
    return !cx->job->pl.uncopyable;
}

/* True iff `e` is defined by this artifact: a row on its shape, not omitted. */
static bool entry_present(const Ctx *cx, PcrecEntry e)
{
    return cx->job->entry_comb[e] != 0 && pcrec_entry_emitted(cx, e);
}

/* Builds every present subject's and owned function's record, and runs the
 * part table over the subjects when T3 fired. */
static void build_records(Ctx *cx)
{
    PcrecPartLayout *pl = &cx->job->pl;
    pl->nparts = 0;
    if (!cx->job->entry_shaped) return;
    for (int i = 0; i < NSUBJ + NOWNED; i++) {
        PcrecEntry e = i < NSUBJ ? subjects[i].e : owned[i - NSUBJ];
        if (!entry_present(cx, e)) continue;
        if (pl->nparts >= PCREC_ENTRY_N)
            pcrec_ctx_fail(cx, 0, "internal error: part layout: more parts than records");
        PcrecPlPart *p = &pl->part[pl->nparts++];
        memset(p, 0, sizeof *p);
        p->e = e;
        p->cls = (signed char)subject_class(e);
        part_callers_rank(cx, e, &p->callers, &p->rank);
        p->copyable = p->cls >= 0 && part_copyable(cx, e);
        if (!pl->t3) continue;
        for (int r = 0; r < NPART; r++)
            if (part_rows[r].holds(p, pl)) {
                p->row = (unsigned char)r;
                p->layout = (unsigned char)part_rows[r].layout;
                break;
            }
    }
}

/* ---- the marks ----------------------------------------------------------- */

/* THE HEAD-MARK TABLE: which entry's mark a search head writes, first
 * match, read by `pcrec_part_head_mark` alone. A part is laid out by its
 * shell, whose row names it (M1; a standalone part compile, the unit drive,
 * renders itself and has no shell, M2); any other head writes its own
 * entry's mark where that entry is a subject (M3, `subjects[]`). */
typedef enum { HM_NONE, HM_SHELL_ROW, HM_OWN } HeadMark;

static bool hm_part_shell(const Ctx *cx, PcrecEntry e)
{ return pcrec_is_part(cx) && e == PCREC_ENTRY_SEARCH && cx->emit_in->unrendered; }
static bool hm_part(const Ctx *cx, PcrecEntry e)
{ (void)e; return pcrec_is_part(cx); }
static bool hm_subject(const Ctx *cx, PcrecEntry e)
{ (void)cx; return subject_class(e) >= 0; }
static bool hm_always(const Ctx *cx, PcrecEntry e)
{ (void)cx; (void)e; return true; }

static const struct {
    const char *id, *conj;
    HeadMark mark;
    bool (*holds)(const Ctx *cx, PcrecEntry e);
} head_rows[] = {
    { "M1", "a part's search head, its shell still to render", HM_SHELL_ROW, hm_part_shell },
    { "M2", "any other head of a part",                        HM_NONE,      hm_part },
    { "M3", "the head's entry is a subject",                   HM_OWN,       hm_subject },
    { "M4", "(otherwise)",                                     HM_NONE,      hm_always },
};

void pcrec_part_head_mark(Ctx *cx, StrBuf *c, PcrecEntry e)
{
    if (!pcrec_part_layout_active(cx)) return;
    int r = 0;
    while (!head_rows[r].holds(cx, e)) r++;   /* M4 always holds */
    unsigned id = e;
    switch (head_rows[r].mark) {
    case HM_NONE:
        return;
    case HM_SHELL_ROW:
        id = cx->emit_in->part_entry;
        if (subject_class((PcrecEntry)id) != PCREC_PART_COMPOUND)
            pcrec_ctx_fail(cx, 0, "internal error: part layout: a part with no shell row");
        break;
    case HM_OWN:
        break;
    }
    pcrec_sb_layout_mark(c, id, false);
}

void pcrec_part_stamp_mark(Ctx *cx, StrBuf *c)
{
    if (pcrec_is_part(cx)) return;
    art_walk(cx);
    if (!cx->job->pl.t3 && cx->job->pl.why < 0) return;
    pcrec_sb_layout_mark(c, PCREC_ENTRY_N, true);
    cx->job->pl.stamp_marked = true;
}

/* ---- the render ---------------------------------------------------------- */

/* Each layout a part row writes as a value of [ATTR-TABLE]'s one
 * value-to-guarded-text table (src/gen/attr_text.c): its text, its
 * `--emit-facts` token and its `--list-axes` writes cell. The render
 * (`render_buf`), the facts listing and the table listing all read it, so
 * the text and its description cannot drift apart. `shared`'s text opens a
 * line, so `static ` ends its line, the guard follows, then the signature. */
static PcrecAttr layout_attr(int layout)
{
    switch (layout) {
    case PCREC_PART_AUTO:   return PCREC_ATTR_AUTO;
    case PCREC_PART_SHARED: return PCREC_ATTR_SHARED;
    case PCREC_PART_INLINE: return PCREC_ATTR_INLINE;
    }
    return PCREC_ATTR_AS_EMITTED;
}

/* `<PREFIX>_PART_LAYOUT`'s value: the resolved non-trivial controls in a
 * fixed order (`residual=V`, `rank=R` or `rank=R@set`, each set class as
 * `CLASS=V` with `/held` where a constraint row held one of its parts and
 * `/none` where the artifact has no part of it). */
static const char *stamp_value(Ctx *cx)
{
    const PcrecPartLayout *pl = &cx->job->pl;
    StrBuf v = { .cx = cx };
    const char *sep = "";
    if (pl->residual) {
        pcrec_sb_printf(&v, "%sresidual=%s", sep, value_tok[pl->residual]);
        sep = ";";
    }
    if (pl->rank) {
        pcrec_sb_printf(&v, "%srank=%s%s", sep, rank_tok[pl->rank],
                        pl->rank_set ? "@set" : "");
        sep = ";";
    }
    for (int k = 0; k < PCREC_PART_NCLASS; k++) {
        int cv = PCREC_PART_LAYOUT_GET(pl->classes, k);
        if (!cv) continue;
        bool any = false, held = false;
        for (int i = 0; i < pl->nparts; i++)
            if (pl->part[i].cls == k) {
                any = true;
                if (part_rows[pl->part[i].row].held) held = true;
            }
        pcrec_sb_printf(&v, "%s%s=%s%s", sep, class_tok[k], value_tok[cv],
                        !any ? "/none" : held ? "/held" : "");
        sep = ";";
    }
    const char *out = pcrec_sb_fragf(&cx->arena, "%s", v.p ? v.p : "");
    pcrec_sb_free(&v);
    return out;
}

/* The stamp lines the stamp mark renders to. */
static void stamp_lines(Ctx *cx, StrBuf *out)
{
    const char *up = pcrec_sb_upper(&cx->arena, cx->opt->prefix);
    if (cx->job->pl.t3) pcrec_sb_stamp_str(out, up, "PART_LAYOUT", stamp_value(cx));
    if (cx->job->pl.why >= 0)
        pcrec_sb_stamp_str(out, up, "PART_LAYOUT_WHY", why_tok[cx->job->pl.why]);
}

/* The hex digit `c`'s value, or -1. */
static int hexval(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

/* Rewrites `sb`'s marks into a fresh buffer and swaps it in, counting each
 * subject's head marks into `seen`. A mark with no record, or a stamp mark
 * where none was written, is an internal error. */
static void render_buf(Ctx *cx, StrBuf *sb, unsigned char seen[PCREC_ENTRY_N + 1])
{
    if (!sb->p || !memchr(sb->p, PCREC_PREFIX_LEAD, sb->len)) return;
    const PcrecPartLayout *pl = &cx->job->pl;
    StrBuf o = { .cx = cx };
    size_t i = 0;
    while (i < sb->len) {
        const char *q = memchr(sb->p + i, PCREC_PREFIX_LEAD, sb->len - i);
        size_t at = q ? (size_t)(q - sb->p) : sb->len;
        if (at > i) pcrec_sb_printf(&o, "%.*s", (int)(at - i), sb->p + i);
        if (!q) break;
        int h1 = at + 3 < sb->len ? hexval(sb->p[at + 2]) : -1;
        int h0 = at + 3 < sb->len ? hexval(sb->p[at + 3]) : -1;
        if (at + 1 >= sb->len || sb->p[at + 1] != 'L' || h1 < 0 || h0 < 0) {
            /* not a layout mark: the prefix placeholder, rendered later */
            pcrec_sb_putc(&o, sb->p[at]);
            i = at + 1;
            continue;
        }
        unsigned id = (unsigned)(h1 * 16 + h0);
        if (id == PCREC_ENTRY_N) {
            if (!pl->stamp_marked)
                pcrec_ctx_fail(cx, 0, "internal error: part layout: a stamp mark nobody wrote");
            stamp_lines(cx, &o);
            seen[PCREC_ENTRY_N]++;
            if (at + 4 < sb->len && sb->p[at + 4] == '\n') i = at + 5;   /* the mark's line */
            else pcrec_ctx_fail(cx, 0, "internal error: part layout: a stamp mark not on a line of its own");
            continue;
        } else {
            const PcrecPlPart *p = NULL;
            for (int k = 0; k < pl->nparts; k++)
                if (pl->part[k].e == id && pl->part[k].cls >= 0) p = &pl->part[k];
            if (!p || !pl->t3)
                pcrec_ctx_fail(cx, 0, "internal error: part layout: a mark for "
                               "entry %u with no subject record", id);
            /* Every row writes only on a STATIC definition (§3.4 [r3 LK-9]):
             * on an exported one, gcc 15.2 takes `inline always_inline` as a
             * C99 inline definition without a word under -fPIC, so this is
             * the check, not the compiler. */
            if (at < 7 || memcmp(sb->p + at - 7, "static ", 7) != 0)
                pcrec_ctx_fail(cx, 0, "internal error: part layout: a mark on a "
                               "definition that is not static (entry %u)", id);
            pcrec_sb_puts(&o, pcrec_attr_text(layout_attr(p->layout)));
            seen[id]++;
        }
        i = at + 4;
    }
    char *old = sb->p;
    sb->p = o.p;
    sb->len = o.len;
    sb->cap = o.cap;
    sb->layout_bytes = 0;
    free(old);
}

void pcrec_part_layout_render(Ctx *cx)
{
    art_walk(cx);
    build_records(cx);
    PcrecPartLayout *pl = &cx->job->pl;
    if (!pl->t3 && pl->why < 0) return;
    unsigned char seen[PCREC_ENTRY_N + 1] = { 0 };
    render_buf(cx, &cx->job->csb, seen);
    render_buf(cx, &cx->job->hsb, seen);
    /* Every subject's head was marked exactly once, and the stamp mark too:
     * a head written by some other route, or a second definition, would be
     * laid out by nobody or twice. */
    if (seen[PCREC_ENTRY_N] != (pl->stamp_marked ? 1 : 0))
        pcrec_ctx_fail(cx, 0, "internal error: part layout: the stamp mark was not "
                       "found exactly once");
    for (int k = 0; k < pl->nparts; k++)
        if (pl->t3 && pl->part[k].cls >= 0 && seen[pl->part[k].e] != 1)
            pcrec_ctx_fail(cx, 0, "internal error: part layout: subject %s's head "
                           "mark found %d times", pcrec_entry_name(pl->part[k].e),
                           seen[pl->part[k].e]);
}

/* ---- the listings -------------------------------------------------------- */

void pcrec_part_layout_facts(Ctx *cx, StrBuf *ctl, StrBuf *parts, const char *enc)
{
    const PcrecPartLayout *pl = &cx->job->pl;
    if (!pl->resolved) return;
    StrBuf rows = { .cx = cx };
    for (int i = 0; i < pl->narow; i++)
        pcrec_sb_printf(&rows, "%s%s", i ? "," : "", art_rows[pl->arow[i]].id);
    const char *cells[9];
    cells[0] = enc;
    cells[1] = value_tok[pl->residual];
    cells[2] = pcrec_sb_fragf(&cx->arena, "%s%s", rank_tok[pl->rank],
                              pl->rank_set ? "@set" : "");
    for (int k = 0; k < PCREC_PART_NCLASS; k++)
        cells[3 + k] = value_tok[PCREC_PART_LAYOUT_GET(pl->classes, k)];
    cells[7] = pcrec_sb_fragf(&cx->arena, "%s", rows.p ? rows.p : "");
    cells[8] = pl->why >= 0 ? why_tok[pl->why] : "";
    pcrec_sb_row(ctl, cells, 9);
    pcrec_sb_free(&rows);
    for (int i = 0; i < pl->nparts; i++) {
        const PcrecPlPart *p = &pl->part[i];
        const char *pc[9];
        pc[0] = enc;
        pc[1] = pcrec_entry_name(p->e);
        pc[2] = p->cls >= 0 ? class_tok[p->cls] : "owned";
        pc[3] = pcrec_sb_fragf(&cx->arena, "%u", p->callers);
        pc[4] = edge_rank_tok[p->rank];
        pc[5] = p->cls < 0 ? "-" : p->copyable ? "yes" : "no";
        if (p->cls < 0) {
            pc[6] = "P1 owned";
            pc[7] = "owner";
        } else if (!pl->t3) {
            pc[6] = "T0 as-emitted";
            pc[7] = "auto";
        } else {
            pc[6] = pcrec_sb_fragf(&cx->arena, "%s %s", part_rows[p->row].id,
                                   part_rows[p->row].name);
            pc[7] = pcrec_attr_tok(layout_attr(p->layout));
        }
        int w = p->cls >= 0 && pl->t3 && p->layout == PCREC_PART_SHARED
              ? wrapper_count(cx, p->e) : 0;
        pc[8] = w ? pcrec_sb_fragf(&cx->arena, "%d", w) : "0";
        pcrec_sb_row(parts, pc, 9);
    }
}

bool pcrec_part_layout_table_row(int i, const char **table, const char **id,
                                 const char **name, const char **conj,
                                 const char **writes)
{
    if (i < NART) {
        *table = "artifact"; *id = art_rows[i].id; *name = art_rows[i].name;
        *conj = art_rows[i].conj; *writes = art_rows[i].writes;
        return true;
    }
    i -= NART;
    if (i < NPART) {
        *table = "part"; *id = part_rows[i].id; *name = part_rows[i].name;
        *conj = part_rows[i].conj; *writes = pcrec_attr_writes(layout_attr(part_rows[i].layout));
        return true;
    }
    i -= NPART;
    if (i < NWRAP) {
        *table = "wrapper"; *id = wrap_rows[i].id; *name = wrap_rows[i].name;
        *conj = wrap_rows[i].conj; *writes = wrap_rows[i].writes;
        return true;
    }
    return false;
}
