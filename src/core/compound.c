/* [COMPOUND] THE COMPOUND TOOL'S PARTS (docs/design/compound.md §A.1, §A.5;
 * build step B1). Driver tier: it calls the pipeline driver, as compile.c's
 * own entries do.
 *
 * A PART is the unchanged pipeline run on a derived input and rendered as
 * `<prefix>__<role>` inside a compound's one artifact. What makes it a part
 * is two things the driver is handed and no `pcrec_options` field carries
 * (`PcrecEmitIn`): an entry request that exports nothing and keeps what the
 * controller reads (`need`, through [EMIT-ENTRIES]' closure), and PART MODE
 * (the role, which renders the prefix and drops the shared blocks, and the
 * bound, which the start table's BOUND slot reads).
 *
 * NO SILENT DEFAULT (memory `pcrec-no-silent-defaults`, compound.md §A.1).
 * Every `CompPart` field is stated: the two enums' zero values are UNSTATED
 * and refused, a NULL derivation is unstated (`pcrec_derive_none` is the
 * explicit none), and a part that forces a flag both on and off is
 * refused. A part's options are the parent's with `flags_set` OR-ed in and
 * `flags_clear` masked out; `tune`, `analysis`, `features`, `encoding` and
 * every cap are the parent's by that one written rule. B4's compound_rows[]
 * runs `pcrec_comp_part_check` over every part of every row at table build;
 * until then its callers are the unit drive and `pcrec_compile_part`.
 * A part's derivation runs as the driver's tree-hook (B2); its report goes
 * to the caller's `report` (NULL: none wanted). */
#include "core/internal.h"

#include <stdio.h>
#include <string.h>

const PcrecDerive pcrec_derive_none = { "none", NULL };

/* The pipeline's engine request for each stated part engine. */
static const int part_engine[] = {
    [PCREC_PE_AUTO] = PCREC_ENGINE_AUTO,
    [PCREC_PE_DFA] = PCREC_ENGINE_DFA,
    [PCREC_PE_VM] = PCREC_ENGINE_VM,
};

/* The [EMIT-ENTRIES] kept roots a part's `need` names. */
static unsigned part_kept(unsigned need)
{
    unsigned m = 0;
    if (need & PCREC_PART_NEED_SEARCH)     m |= PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH);
    if (need & PCREC_PART_NEED_MATCH_CAPS) m |= PCREC_ENTRY_BIT(PCREC_ENTRY_MATCH_CAPS);
    if (need & PCREC_PART_NEED_NEXT_POS)   m |= PCREC_ENTRY_BIT(PCREC_ENTRY_NEXT_POS);
    if (need & PCREC_PART_NEED_VALID_UPTO) m |= PCREC_ENTRY_BIT(PCREC_ENTRY_VALID_UPTO);
    return m;
}

/* Compiles `pattern` as `part` under `parent`'s options plus the part's: the
 * request (nothing exported, `need` kept) and part mode, its derivation's
 * report to `report` and its facts to `facts` (each NULL: not wanted).
 * `unrendered` keeps the placeholder prefix, for text the compound splices
 * into its own (which renders it). `meas` is the walking attempt's
 * measurement set and analysis chain/object, which the part reads instead of
 * resolving `parent`'s options again (NULL: no walk, as from `pcrec_compile_part`). The part is
 * already checked. */
static int part_compile(const char *pattern, const pcrec_options *parent,
                        const CompPart *part, PcrecDeriveReport *report,
                        PcrecPartFacts *facts, bool unrendered, PcrecEntry pe,
                        const PcrecMeasInherit *meas,
                        pcrec_output *out, pcrec_error *err)
{
    pcrec_options o;
    pcrec_default_options(&o);
    if (parent) o = *parent;
    o.flags = pcrec_flags_without(o.flags | part->flags_set, part->flags_clear);
    o.engine = part_engine[part->engine];
    o.header_name = NULL;
    const PcrecEntryReq req = { 0, part_kept(part->need) };
    const PcrecEmitIn in = { .req = &req, .part_role = part->role,
                             .part_entry = pe,
                             .bound = part->bound, .derive = part->derive->fn,
                             .derive_report = report, .unrendered = unrendered,
                             .facts = facts, .harness = NULL, .meas = meas };
    return pcrec_compile_driver(pattern, &o, out, err, NULL, NULL, NULL, NULL,
                                NULL, &in);
}

const char *pcrec_comp_part_check(const CompPart *part)
{
    if (!part) return "no part";
    const char *r = part->role;
    size_t n = r ? strlen(r) : 0;
    if (n < 1 || n > PCREC_PART_ROLE_MAX) return "role: 1 to 3 characters";
    for (size_t i = 0; i < n; i++)
        if (!((r[i] >= 'a' && r[i] <= 'z') || (r[i] >= '0' && r[i] <= '9')))
            return "role: [a-z0-9] only";
    if (!part->derive) return "derive: unstated (pcrec_derive_none is the explicit none)";
    if (part->derive != &pcrec_derive_none && !part->derive->fn)
        return "derive: a derivation with no function";
    if (part->flags_set & part->flags_clear) return "flags: one flag both set and cleared";
    if (part->engine == PCREC_PE_UNSTATED) return "engine: unstated";
    if (part->bound == PCREC_PB_UNSTATED) return "bound: unstated";
    if (!(part->need & PCREC_PART_NEED_SEARCH)) return "need: no search entry";
    if (part->need & ~PCREC_PART_NEED_ALL) return "need: an unknown bit";
    if (part->groups.kind == CG_UNSTATED) return "groups: unstated";
    return NULL;
}

int pcrec_compile_part(const char *pattern, const pcrec_options *parent,
                       const CompPart *part, PcrecDeriveReport *report,
                       pcrec_output *out, pcrec_error *err)
{
    const char *why = pcrec_comp_part_check(part);
    if (why) {
        if (out) memset(out, 0, sizeof *out);
        if (err) {
            snprintf(err->msg, sizeof err->msg, "internal error: compound part: %s", why);
            err->pos = 0;
            err->input = PCREC_ERR_INPUT_PATTERN;
        }
        return -1;
    }
    return part_compile(pattern, parent, part, report, NULL, false,
                        PCREC_ENTRY_COMP_A, NULL, out, err);
}

/* ---- [COMPOUND] B4: THE ROW TABLE, THE PLACEMENT TABLE AND THE WALK -------
 *
 * docs/design/compound.md §A.1-§A.3, §A.14, §B.1-§B.4. `compound_rows[]` is
 * a first-match table; a client is a row. Its ONE client today is
 * [MATCH-SPLIT], pin-only: P = a floor arm (`^`/`\A`/`\G`) beside arms that
 * are pinned to the END, compiled as two DFA parts -- F, P bounded to one
 * attempt (the floor's own answer), and Q, P with its floor anchors killed
 * and pruned (every later start's) -- under `first-nonzero(F at the floor, Q
 * from the next character)`. The walk runs on P's plain compile, its
 * machines built and nothing emitted, so a conjunct reads the plain
 * compile's selections (`pcrec_cand_plain_selection`); a row that admits
 * becomes the attempt's SHELL, which the DFA emitter writes in place of the
 * plain artifact. Nothing here refuses the compile: a failing conjunct, a
 * part that refuses, ends the row. */

/* split's parts: both DFA, guards-off and check-clear (the controller owns
 * P's one prologue, §A.6), each the parent's groups by identity. The
 * controller calls the compound's own `<p>_next_pos`, so F needs only its
 * search. */
#define SPLIT_GUARDS_OFF_SET   PCREC_NO_STARTPOS_GUARD
#define SPLIT_GUARDS_OFF_CLEAR (PCREC_FORCE_UTF_CHECK | PCREC_FORCE_STARTPOS_ALIGN)
enum { SPLIT_F, SPLIT_Q };
static const CompPart split_parts[] = {
    [SPLIT_F] = { "f", &pcrec_derive_none, SPLIT_GUARDS_OFF_SET, SPLIT_GUARDS_OFF_CLEAR,
                  PCREC_PE_DFA, PCREC_PB_ONE_ATTEMPT, PCREC_PART_NEED_SEARCH,
                  { CG_IDENTITY } },
    [SPLIT_Q] = { "q", &pcrec_derive_split_q_row, SPLIT_GUARDS_OFF_SET,
                  SPLIT_GUARDS_OFF_CLEAR, PCREC_PE_DFA, PCREC_PB_NONE,
                  PCREC_PART_NEED_SEARCH, { CG_IDENTITY } },
};

/* The walk's state for one row: P's plain compile and tree, and each part's
 * compile, made on first ask (A2 asks Q's for its derivation report, the
 * POST phase every part's). */
struct CompWalk {
    Ctx *cx;
    const Ast *root;
    const CompRow *row;
    bool tried[PCREC_COMP_MAXPARTS];
    int rc[PCREC_COMP_MAXPARTS];
    pcrec_output out[PCREC_COMP_MAXPARTS];
    pcrec_error err[PCREC_COMP_MAXPARTS];
    PcrecDeriveReport rep[PCREC_COMP_MAXPARTS];
    PcrecPartFacts facts[PCREC_COMP_MAXPARTS];
};

/* Part `i` of the walk's row, compiled on its first ask: 0, or -1 (the part
 * refused). Its parent options are P's own (the placeholder prefix: the text
 * is spliced unrendered, so K79 holds across the compound), and so is its
 * measurement set: this attempt's resolved one, never resolved again. */
static int walk_part(CompWalk *w, int i)
{
    if (!w->tried[i]) {
        const Job *job = w->cx->job;
        const PcrecMeasInherit meas = { job->meas, job->meas_stamp, job->mf_ms,
                                        &job->find.chain, job->analysis };
        w->tried[i] = true;
        w->rep[i].killed = -1;   /* stays -1 unless the derivation ran */
        w->facts[i].into = &w->cx->arena;
        w->rc[i] = part_compile(w->cx->pat, w->cx->opt, &w->row->parts[i],
                                &w->rep[i], &w->facts[i], true,
                                /* [ENTRY-TABLE] E1 the shell row the part's
                                 * part-layout mark names: its operand's */
                                i == w->row->arg[0] ? PCREC_ENTRY_COMP_A
                                                    : PCREC_ENTRY_COMP_B,
                                &meas, &w->out[i],
                                &w->err[i]);
    }
    return w->rc[i];
}

static void walk_free(CompWalk *w)
{
    for (int i = 0; i < PCREC_COMP_MAXPARTS; i++)
        if (w->tried[i] && w->rc[i] == 0) pcrec_output_free(&w->out[i]);
}

/* A1: P's plain compile runs today's attempt loop over every start -- a DFA
 * artifact on the ATTEMPT route whose BOUND is `all` and whose LOCATE row
 * hands its result to NEXT there (the attempt loop itself; [KIT-VERIFY]
 * kit_proof.md §2.6, a field read, never the row's name). A fully anchored P
 * is already one attempt. */
static const CompRead a1_reads[] = {
    { CAND_SLOT_BOUND, CAND_ROUTE_ATTEMPT }, { CAND_SLOT_LOCATE, CAND_ROUTE_ATTEMPT },
};
static bool a1_attempt_all(CompWalk *w)
{
    Ctx *cx = w->cx;
    return cx->job->fit.chosen == ENGM_DFA &&
           pcrec_cand_body_route(cx) == CAND_ROUTE_ATTEMPT &&
           !strcmp(pcrec_cand_plain_selection(cx, CAND_SLOT_BOUND, CAND_ROUTE_ATTEMPT), "all") &&
           pcrec_cand_plain_locate_asks_next(cx, CAND_ROUTE_ATTEMPT);
}

/* A2: Q's derivation ran and did not decline (it killed a floor anchor and
 * left no `\G`, G5's walk holding), and no called or referenced group was
 * kept as a never arm (the first build: B6 keeps such a group as DEFINE). */
static bool a2_derived(CompWalk *w)
{
    (void)walk_part(w, SPLIT_Q);
    const PcrecDeriveReport *r = &w->rep[SPLIT_Q];
    return r->killed >= 0 && !r->decline && r->kept_never == 0;
}

/* A3: no construct in P observes or changes the attempt sequence (the
 * registry's attempt-scope column, §B.8): the controller runs P's attempts
 * as separate calls. */
static bool a3_no_attempt_scope(CompWalk *w)
{
    return !pcrec_ast_crosses_attempts(w->root);
}

/* A4: every part compiled on the DFA with no fallback-table row fired (no
 * size-cap retry, no [SEL-1] rung, no collapse): D158 and Q's own caps. */
static bool a4_parts_dfa(CompWalk *w)
{
    for (int i = 0; i < w->row->nparts; i++)
        if (w->rc[i] != 0 || !w->facts[i].dfa || w->facts[i].degraded) return false;
    return true;
}

/* A5, PIN-ONLY: Q is never (the floor-only form), or Q's LOCATE walk is
 * seeded at the subject end (the `rev-end` walk's field, [KIT-VERIFY]
 * kit_proof.md §2.6) -- an end-pinned Q has at most the end matches per
 * subject; an unanchored Q's many-match cost waits for B5's cost conjunct. */
static bool a5_pin_only(CompWalk *w)
{
    return w->rep[SPLIT_Q].never || w->facts[SPLIT_Q].end_seeded;
}

static const CompConj split_conj[] = {
    { "A1", "P's plain compile attempts every start (DFA attempt route, BOUND all)",
      CC_PRE, a1_attempt_all, a1_reads, 2 },
    { "A2", "the derivation killed a floor anchor, left no \\G, and kept no group as a never arm",
      CC_PRE, a2_derived, NULL, 0 },
    { "A3", "no construct observes or changes the attempt sequence",
      CC_PRE, a3_no_attempt_scope, NULL, 0 },
    { "A4", "every part compiled on the DFA with no fallback row fired",
      CC_POST, a4_parts_dfa, NULL, 0 },
    { "A5", "pin-only: Q is never, or Q's LOCATE is rev-end",
      CC_POST, a5_pin_only, NULL, 0 },
};

static const CompRow compound_rows[] = {
    { "split", split_conj, (int)(sizeof split_conj / sizeof split_conj[0]),
      split_parts, (int)(sizeof split_parts / sizeof split_parts[0]),
      COMB_FIRST_NONZERO, { SPLIT_F, SPLIT_Q }, 0 },
};
#define NROWS ((int)(sizeof compound_rows / sizeof compound_rows[0]))

const CompRow *pcrec_compound_row(int i)
{
    return i >= 0 && i < NROWS ? &compound_rows[i] : NULL;
}

/* ---- `compound_place[]`: IN-JOB ROW OR COMPOUND PART (§A.2) ---------------
 *
 * A first-match table asked of every part of every row at table build: a
 * part must land on row 1 or 2; a part on row 3 is an in-Job row (a
 * `cand_rows[]` LOCATE or FINISH row: P's tree under erasure, P's options)
 * mis-placed as a part. Review asks it of every in-Job candidate. */
typedef struct {
    const char *name;
    bool (*holds)(const CompPart *p);
} CompPlace;

static bool place_tree(const CompPart *p)
{
    return p->derive && p->derive != &pcrec_derive_none;
}
static bool place_options(const CompPart *p)
{
    return p->flags_set || p->flags_clear || p->engine != PCREC_PE_AUTO ||
           p->bound == PCREC_PB_ONE_ATTEMPT;
}
static bool place_always(const CompPart *p) { (void)p; return true; }

static const CompPlace compound_place[] = {
    { "different-tree",    place_tree },
    { "different-options", place_options },
    { "erasure-only",      place_always },
};

int pcrec_compound_place(const CompPart *part)
{
    for (int i = 0; ; i++)
        if (compound_place[i].holds(part)) return i + 1;
}

/* ---- the combinator's type check (§A.2) ------------------------------------
 *
 * A part's entry hands a type read off its bound: one attempt is `verify-at`
 * (a SPAN at the point, or NOMATCH), an unbounded search `search-from`.
 * `first-nonzero` takes a `verify-at` first operand and a `search-from`
 * second. */
typedef enum { CT_VERIFY_AT, CT_SEARCH_FROM } CompEntryType;

static CompEntryType part_type(const CompPart *p)
{
    return p->bound == PCREC_PB_ONE_ATTEMPT ? CT_VERIFY_AT : CT_SEARCH_FROM;
}

static const struct {
    CompComb comb;
    int nargs;
    CompEntryType arg[2];
} comb_types[] = {
    { COMB_FIRST_NONZERO, 2, { CT_VERIFY_AT, CT_SEARCH_FROM } },
};

const char *pcrec_compound_rows_check(const CompRow *rows, int nrows)
{
    for (int r = 0; r < nrows; r++) {
        const CompRow *row = &rows[r];
        if (!row->name || !row->nconj || !row->conj) return "a row's admission is empty";
        if (row->nparts < 1 || row->nparts > PCREC_COMP_MAXPARTS)
            return "a row's part count is out of range";
        bool post = false;
        for (int i = 0; i < row->nconj; i++) {
            const CompConj *c = &row->conj[i];
            if (!c->id || !c->name || !c->holds || c->phase == CC_UNSTATED)
                return "a conjunct is unstated";
            if (c->phase == CC_PRE && post) return "a CC_PRE conjunct follows a CC_POST one";
            post |= c->phase == CC_POST;
            for (int j = 0; j < i; j++)
                if (!strcmp(row->conj[j].id, c->id)) return "two conjuncts share an id";
        }
        for (int i = 0; i < row->nparts; i++) {
            const CompPart *p = &row->parts[i];
            if (pcrec_comp_part_check(p)) return "a part is unstated or inconsistent";
            if (pcrec_compound_place(p) == 3)
                return "a part is an in-Job row (compound_place row 3)";
            /* The slot-coverage check's table half: every caller slot is
             * written on every success path, which a part derived from the
             * parent (identity) does for its own NCAPS and the pad for the
             * rest; no other map is built. */
            if (p->groups.kind != CG_IDENTITY) return "a part's group map is unbuilt";
        }
        bool typed = false;
        for (size_t t = 0; t < sizeof comb_types / sizeof comb_types[0]; t++) {
            if (comb_types[t].comb != row->comb) continue;
            typed = true;
            if (comb_types[t].nargs > row->nparts) return "a combinator has too few operands";
            for (int a = 0; a < comb_types[t].nargs; a++) {
                int k = row->arg[a];
                if (k < 0 || k >= row->nparts) return "a combinator operand is no part";
                if (part_type(&row->parts[k]) != comb_types[t].arg[a])
                    return "a combinator operand's entry type does not check";
            }
        }
        if (!typed) return "a row's combinator has no type row";
    }
    return NULL;
}

const char *pcrec_compound_tables_check(void)
{
    return pcrec_compound_rows_check(compound_rows, NROWS);
}

/* Runs `row`'s conjuncts of `phase` in table order; the first that fails, or
 * NULL. The trace build holds each one's selection reads to its declared
 * set. */
static const CompConj *walk_phase(CompWalk *w, CompPhase phase)
{
    for (int i = 0; i < w->row->nconj; i++) {
        const CompConj *c = &w->row->conj[i];
        if (c->phase != phase) continue;
#ifdef PCREC_CAND_TRACE
        pcrec_comp_reading = c;
#endif
        bool ok = c->holds(w);
#ifdef PCREC_CAND_TRACE
        pcrec_comp_reading = NULL;
#endif
        if (!ok) return c;
    }
    return NULL;
}

void pcrec_compound_walk(Ctx *cx, const Ast *root)
{
#ifdef PCREC_CAND_TRACE
    const char *bad = pcrec_compound_tables_check();
    if (bad) pcrec_ctx_fail(cx, 0, "internal error: compound table self-check: %s", bad);
#endif
    for (int r = 0; r < NROWS; r++) {
        CompWalk w;
        memset(&w, 0, sizeof w);
        w.cx = cx;
        w.root = root;
        w.row = &compound_rows[r];
        const CompConj *fail = walk_phase(&w, CC_PRE);
        if (!fail)
            for (int i = 0; i < w.row->nparts; i++) (void)walk_part(&w, i);
        if (!fail) fail = walk_phase(&w, CC_POST);
        PCREC_CAND_TRACE_RECF("compound", "-", "compound", "%s %s", w.row->name,
                              fail ? fail->id : "admit");
        if (cx->emit_in && cx->emit_in->comp_verdict)
            *cx->emit_in->comp_verdict = fail ? fail->id : "admit";
        if (fail) {
            walk_free(&w);
            continue;
        }
        /* THE SLOT-COVERAGE CHECK's compile half (§A.1): F is P, so its
         * slots are P's; Q's are at most P's, and the pad writes the rest. */
        const int ncaps = pcrec_dfa_ncaps(cx);
        if (w.facts[w.row->arg[0]].ncaps != ncaps ||
            w.facts[w.row->arg[1]].ncaps > ncaps)
            pcrec_ctx_fail(cx, 0, "internal error: compound: a part's slots do not "
                           "cover the caller's (%d, %d of %d)",
                           w.facts[w.row->arg[0]].ncaps, w.facts[w.row->arg[1]].ncaps,
                           ncaps);
        PcrecCompShell *sh = pcrec_arena_alloc(&cx->arena, sizeof *sh);
        sh->row = w.row->name;
        sh->comb = w.row->comb;
        sh->ncaps = ncaps;
        sh->floor_any = w.rep[SPLIT_Q].has_g;
        for (int a = 0; a < 2; a++) {
            const int k = w.row->arg[a];
            sh->role[a] = w.row->parts[k].role;
            sh->facts[a] = w.facts[k];
            /* the derived operand that matches nothing is never called */
            if (w.row->parts[k].derive != &pcrec_derive_none && w.rep[k].never) {
                pcrec_output_free(&w.out[k]);
            } else {
                sh->text[a] = w.out[k].c_src;
                w.out[k].c_src = NULL;
                pcrec_output_free(&w.out[k]);
            }
            w.tried[k] = false;
        }
        cx->job->comp_shell = sh;
        return;
    }
}
