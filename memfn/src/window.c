/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text, except the A-model and
 *   C-model rows, which transcribe pcrec 7050f8652's src/opt/prefix_k.c
 *   selection (verify_cost, model_cost, the scan loop, the greedy verify
 *   pick, its exchange sort, the materiality test), relicensed 0BSD by its
 *   author (D145 addendum 1) (memfn/PROVENANCE.md).
 *
 * memfn/src/window.c — THE WINDOW FAMILY (D172, S2 commit 1;
 * docs/design/memfn/window_site.md rev 3.2 §2, §3).
 *
 * WHAT IT IS. One row family over a WINDOW SITE's facts (memfn.h "THE WINDOW
 * SITE": spans with start, sets, core and verify; one or two alternatives,
 * each with its ENTRY; table offers; the floor; the frame). Since S2 commit 6
 * it is the route of EVERY site stating alternatives, on every art (through
 * commit 5 an art had to preview "window-family"; the old path, the site's
 * own old fields, is deleted).
 *
 *   phase 1 (DECISION, no text; mf_wdecide)
 *     A  the STOP per alternative (rows A-empty A-parked A-model A-mass
 *        A-floor), then the choice over alternatives (rows M-one MARGIN
 *        M-parked): one least-cost choice over (alternative, stop)
 *     C  the VERIFY PLAN of the chosen (alternative, stop): steps C-meet,
 *        C-yes / C-model / C-none, C-pin, C-stop, C-run, C-table / C-own,
 *        C-asc
 *   phase 2 (TEXT, in the frame pcrec states; mf_define)
 *     B  how the stop is found: the finder's FIND slot (finder.c fd_rows[])
 *        and the offset-skip function's BODY/PREFIX slots (ofsskip.c), reached
 *        through the row E hands the plan to (no parallel table, see E). On
 *        E-find's own text the FIND slot is asked about the stop itself
 *        (fd_find: its set, its offset, the site's kind and options) and
 *        the deciding row's PICK is rendered (Table B's
 *        renderers, `wf_brows`: B-fn, B-pair, B-memchr, B-walk)
 *     D  the resume (E-find's text; a kit_table whose rows carry their
 *        text, wf_d_text): D-hors, Horspool over the tested sets on a dense
 *        stop (HORS_MIN), else D-one, `c + 1`
 *     E  the frame: E-func, E-stmt (the plan translated into the site today's
 *        row renders, selected by the composer's walk as ever, so its text is
 *        that row's), E-find (D172 S3: the family's own find-then-verify
 *        text, below), E-generic (the family's floor, below)
 *   floor: a byte loop over the plan under the core rule (window_site.md §2
 *   "floor: generic"), with ONE hoisted core bound per candidate and the
 *   THREE-WAY guard outside it.
 *
 * Every table is a `kit_table` on the one walk (kit_walk; Tables A, M, D, E)
 * or a declared row list read in order (C, TIE, and B's renderers, keyed on
 * the FIND slot's pick); every cost row reads ONE cost table, plan_cost.def.
 * The decision reads no frame fact.
 *
 * THE TIE TABLE (window_site.md §2.1) is `wf_ties[]`: every tie rule of the
 * family lives there and every comparison that can tie reads its row.
 *
 * A PARKED ALTERNATIVE'S verify-NO spans (the pinned run R, stated only under
 * §1.1's pin fact) are sound only if the matcher is re-seeded at the
 * candidate. So the family READS them (their sets, their cores) only where
 * its plan sets RE-SEED (C-pin, or the floor row testing every span); C-meet's
 * intersection at a position is taken over the spans the plan may read
 * (`rd_set`, `rd_core`). Otherwise testing a verify-YES position C-meet
 * merged with R would filter parked candidates by R without the re-seed
 * (docs/dev/lanes/wsc1_report.md, finding F-1).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- THE COST TABLE (plan_cost.def; window_site.md §3.3) ------------------ */

enum {
#define MF_COST(name, value, unit, provenance, box, basis) WC_##name = (value),
#include "plan_cost.def"
#undef MF_COST
};
#define COST(name) ((unsigned long long)WC_##name)
#define PPM ((unsigned long long)MF_PPM_FULL)

/* ---- THE TIE TABLE (window_site.md §2.1 [rev3.2 n6]) ---------------------- */

typedef enum { TIE_HIGHER, TIE_LOWER, TIE_EXCHANGE, TIE_PARKED, TIE_RESEED,
               TIE_LEFTMOST } wf_tie_to;
enum { T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW, T_N };
static const struct {
    const char *where;
    wf_tie_to   to;
    const char *code;           /* the code it reproduces                    */
    const char *basis;
} wf_ties[T_N] = {
    [T_MASS_STRETCH] = { "A-mass at a position inside a stated run stretch (one-member or cube, "
                         "C-run's grouping), the run MEMBER and C-pin included", TIE_HIGHER,
                         "pcrec_find_run_scan_index / pcrec_find_run_rank ([n-1..0]), "
                         "pcrec_run_pin (exact positions highest first)",
                         "today's; on REPORT literal stretches UNMEASURED DEFAULT" },
    [T_MASS_SET]     = { "A-mass at a set position", TIE_LOWER, "strict < over ascending offsets",
                         "MEASURED on REPORT (581: the rightmost loses 1.23-1.57x on year4)" },
    [T_MODEL]        = { "A-model, stop offsets of equal cost", TIE_LOWER,
                         "prefix_k's strict `cost < best` over walk-index order",
                         "today's; under the walk-index listing obligation" },
    [T_CMODEL]       = { "C-model, verify-NO offsets of equal mass", TIE_EXCHANGE,
                         "prefix_k's exchange sort over walk-index order (unstable)", "today's" },
    [T_MARGIN]       = { "MARGIN, best * NUM == base * DEN", TIE_PARKED,
                         "prefix_k's `>=` rejects", "today's" },
    [T_WINDOW]       = { "the run truncation window (pcrec's, a limit of its statement)",
                         TIE_LEFTMOST, "pcrec_find_run_window_start's strict <",
                         "today's; no kit reader (window_site.md §9)" },
};

/* 1 iff a candidate at offset `c`, of a mass EQUAL to the best's at an
 * offset `b` the walk met first (ascending), takes the tie under row `r`. */
static int tie_takes(int r, int32_t c, int32_t b)
{
    return wf_ties[r].to == TIE_HIGHER ? c > b : wf_ties[r].to == TIE_LOWER ? c < b : 0;
}

/* ---- THE DECISION's working state ----------------------------------------- */

#define WF_LO   (-MF_MAX_BACK)          /* the least offset a position may take  */
#define WF_NPOS MF_WPLAN_MAX            /* positions, offset - WF_LO             */

/* One OFFSET of an alternative after C-meet: the intersection of every
 * covering span's set (`set`, `core`) and of the verify-YES ones (`yset`,
 * `ycore`, `yes`). */
typedef struct {
    uint8_t present, yes, core, ycore, one_pos, multi;
    uint8_t set[32], yset[32];
} wf_pos;

typedef struct {
    const mf_walt *alt;
    wf_pos   p[WF_NPOS];
    int      run;               /* R: THE span of >= 2 positions, each one
                                   member or a cube (wf_check refuses a second,
                                   so no list order decides it), else -1      */
    size_t   arow;              /* Table A's chosen row                       */
    int      has_stop;
    int32_t  stop;
    int      priced;            /* `cost` set: A-parked's base, A-model's best */
    unsigned long long cost;
    unsigned npick;             /* C-model's verify-NO picks (offsets)        */
    int32_t  pick[2];
} wf_alt;

typedef struct {
    const mf_art   *art;
    const mf_site  *s;
    const uint32_t *rate;
    unsigned        na;
    wf_alt          a[MF_WMAX_ALT];
    int             ch;         /* the chosen alternative                     */
    /* the plan (Table C) */
    int             reseed, pinned;
    int             run_stated, run_len;
    int32_t         member, run_lo;
    unsigned        np;
    int32_t         poff[WF_NPOS];
    uint8_t         pterm[WF_NPOS];
    char            path[16];
} wf_dec;

static int in_set(const uint8_t s[32], unsigned b) { return s[b >> 3] >> (b & 7) & 1; }

static unsigned count(const uint8_t s[32])
{
    unsigned n = 0;
    for (unsigned i = 0; i < 32; i++) n += (unsigned)__builtin_popcount(s[i]);
    return n;
}

/* 1: one member (*a); 2: a two-member cube, members *a < *b differing in one
 * bit; 0: neither. */
static int shape(const uint8_t s[32], int *a, int *b)
{
    int m[3], k = 0;
    for (unsigned x = 0; x < 256 && k < 3; x++)
        if (in_set(s, x)) m[k++] = (int)x;
    if (k == 1) { *a = m[0]; *b = -1; return 1; }
    if (k == 2 && __builtin_popcount((unsigned)(m[0] ^ m[1])) == 1) {
        *a = m[0]; *b = m[1];
        return 2;
    }
    return 0;
}

/* The two members of a two-byte set, ascending (any two: PAIR's stop). */
static void two(const uint8_t s[32], int m[2])
{
    int k = 0;
    for (unsigned x = 0; x < 256 && k < 2; x++)
        if (in_set(s, x)) m[k++] = (int)x;
}

static int full(const uint8_t s[32])
{
    for (unsigned i = 0; i < 32; i++) if (s[i] != 0xFF) return 0;
    return 1;
}

static wf_pos *pos_at(wf_alt *m, int32_t off)
{
    return off >= WF_LO && off - WF_LO < WF_NPOS ? &m->p[off - WF_LO] : NULL;
}

static int span_in_core(const mf_wspan *sp, unsigned j)
{
    return j >= sp->core_lo && j < (unsigned)sp->core_lo + sp->core_len;
}

/* 1 iff span `sp` has the run R's SHAPE: two or more positions, each one
 * member or a cube. R is identified by this shape alone (the facts carry no
 * R label), so an alternative states at most one such span (wf_check; the
 * kit manager's F-8 ruling: alternatives and spans are unordered, D172). */
static int run_shaped(const mf_wspan *sp)
{
    int a, b;
    if (sp->len < 2) return 0;
    for (unsigned j = 0; j < sp->len; j++)
        if (!shape(sp->set[j], &a, &b)) return 0;
    return 1;
}

/* C-MEET (step 1): every offset the alternative states, as one position. */
static void merge(const mf_walt *alt, wf_alt *m)
{
    memset(m, 0, sizeof *m);
    m->alt = alt;
    m->run = -1;
    for (unsigned k = 0; k < WF_NPOS; k++) {
        memset(m->p[k].set, 0xFF, 32);
        memset(m->p[k].yset, 0xFF, 32);
    }
    for (unsigned i = 0; i < alt->nspan; i++) {
        const mf_wspan *sp = &alt->spans[i];
        int yes = sp->verify == MF_VERIFY_YES;
        for (unsigned j = 0; j < sp->len; j++) {
            wf_pos *p = pos_at(m, sp->start + (int32_t)j);
            p->present = 1;
            for (unsigned x = 0; x < 32; x++) p->set[x] &= sp->set[j][x];
            if (span_in_core(sp, j)) p->core = 1;
            if (yes) {
                p->yes = 1;
                for (unsigned x = 0; x < 32; x++) p->yset[x] &= sp->set[j][x];
                if (span_in_core(sp, j)) p->ycore = 1;
            }
            if (sp->len == 1) p->one_pos = 1;
            else p->multi = 1;
        }
        if (run_shaped(sp)) m->run = (int)i;
    }
}

/* What the plan may READ at position `p` of the chosen alternative: every
 * covering span's facts, or, on a PARKED alternative whose plan does not
 * re-seed, the verify-YES spans' only (the file header). */
static const uint8_t *rd_set(const wf_dec *d, const wf_pos *p)
{
    return d->a[d->ch].alt->entry == MF_ENTRY_PARKED && !d->reseed ? p->yset : p->set;
}

static int rd_core(const wf_dec *d, const wf_pos *p)
{
    return d->a[d->ch].alt->entry == MF_ENTRY_PARKED && !d->reseed ? p->ycore : p->core;
}

/* ---- THE STATEMENT'S RULES (wf_check) -------------------------------------- */

static int in_enum(unsigned v, unsigned last) { return v <= last; }

/* NULL iff window site `s` states none of the RENDERER INTERFACE's fields
 * (memfn.h "A WINDOW SITE STATES NOTHING ELSE"; the kit manager's R1, D172
 * S2 commit 6): those are the translation's and G2's, never a host's, so a
 * window site stating one beside its window facts is refused, naming it. */
static const char *wf_old_fields(const mf_site *s)
{
    const mf_pred *p = &s->pred;
    if (p->nterm) return "a window site states terms (`pred.nterm`): its spans are its statement";
    if (p->need) return "a window site states `pred.need` (the renderer interface's)";
    if (p->plan_hint && p->plan_hint != MF_NO_PRED)
        return "a window site states `plan_hint` (the renderer interface's)";
    if (p->plan_pos) return "a window site states `plan_pos` (the renderer interface's)";
    if (p->rank_n) return "a window site states a ranking (`rank_n`; the renderer interface's)";
    if (p->span_class) return "a window site states `span_class` (the renderer interface's)";
    if (s->end_back) return "a window site states `end_back` (the renderer interface's)";
    return NULL;
}

const char *wf_check(const mf_site *s, int frame)
{
    if (!s->nalt && !s->alts) {
        if (s->wfloor) return "`wfloor` stated on a site with no alternatives (`alts`)";
        return NULL;
    }
    if (!s->nalt || !s->alts) return "`nalt` and `alts` are stated together";
    const char *old = wf_old_fields(s);
    if (old) return old;
    if (s->nalt > MF_WMAX_ALT) return "`nalt` > MF_WMAX_ALT";
    if (!in_enum(s->wfloor, MF_WFLOOR_EXPR)) return "`wfloor` outside mf_wfloor";
    int below = 0, parked = 0, reseed = 0;
    for (unsigned a = 0; a < s->nalt; a++) {
        const mf_walt *al = &s->alts[a];
        if (!in_enum(al->entry, MF_ENTRY_RESEED)) return "`entry` outside mf_entry";
        if (al->entry == MF_ENTRY_UNSTATED)
            return "an alternative leaves `entry` UNSTATED (NONE, PARKED or RESEED is stated)";
        parked += al->entry == MF_ENTRY_PARKED;
        reseed += al->entry == MF_ENTRY_RESEED;
        if (!al->nspan || !al->spans) return "an alternative states no span (`nspan`, `spans`)";
        if (al->nspan > MF_WMAX_SPAN) return "`nspan` > MF_WMAX_SPAN";
        unsigned nrun = 0;
        for (unsigned i = 0; i < al->nspan; i++) {
            const mf_wspan *sp = &al->spans[i];
            if (!sp->len || sp->len > MF_WSPAN_POS) return "a span's `len` is not 1..MF_WSPAN_POS";
            if (sp->start < -MF_MAX_BACK) return "a span's `start` < -MF_MAX_BACK";
            if ((int64_t)sp->start + sp->len > MF_WREACH)
                return "a span reaches past MF_WREACH (`start` + `len`)";
            if (!in_enum(sp->verify, MF_VERIFY_NO)) return "`verify` outside mf_verify";
            if (sp->verify == MF_VERIFY_UNSTATED)
                return "a span leaves `verify` UNSTATED (YES or NO is stated)";
            if (!in_enum(sp->core, MF_CORE_STATED)) return "`core` outside mf_core";
            if (sp->core == MF_CORE_UNSTATED)
                return "a span leaves `core` UNSTATED (an empty core is a value: core_len 0)";
            if ((unsigned)sp->core_lo + sp->core_len > sp->len)
                return "a span's core lies outside it (`core_lo` + `core_len` > `len`)";
            if (!sp->core_len && sp->core_lo)
                return "an empty core states `core_lo` 0 (one spelling of no core)";
            if (sp->start < 0) below = 1;
            nrun += (unsigned)run_shaped(sp);
        }
        if (nrun > 1)
            return "an alternative states two spans of the run R's shape (two or more positions, "
                   "each one member or a cube): R is identified by its shape, so it is unique";
    }
    if (below && s->wfloor == MF_WFLOOR_UNSTATED)
        return "a span reaches below the candidate and `wfloor` is UNSTATED (SUBJECT or EXPR "
               "is stated, window_site.md §0)";
    if (s->nalt == 2 && !(parked == 1 && reseed == 1))
        return "two alternatives are one PARKED and one RESEED (the MARGIN row's case; no "
               "other pair is described)";
    if (!frame) return NULL;
    /* THE FRAME the family reads (window_site.md §0's frame row): the FIND
       sites of the family, forward, in the three frames Table E renders */
    if (s->op != MF_OP_FIND || s->reverse)
        return "a window site is a forward FIND (`op`, `reverse`)";
    int func = s->form == MF_FORM_FUNC && s->handoff == MF_H_RETURN;
    int stmt = s->form == MF_FORM_STMT &&
               (s->handoff == MF_H_ASSIGN || s->handoff == MF_H_ON_MISS);
    if (!func && !stmt)
        return "a window site's frame is FUNC/RETURN, STMT/ASSIGN or STMT/ON_MISS (`form`, "
               "`handoff`)";
    if (!in_enum(s->empty, MF_EMPTY_AT_N)) return "empty outside mf_empty";
    if (s->empty == MF_EMPTY_NOP && !stmt)
        return "an EXPR or FUNC site cannot write nothing on an empty range";
    if (s->use > MF_USE_DISCARD) return "a window site's `use` is POSITION or DISCARD";
    if (!in_enum(s->body, MF_BODY_PARAM) || s->body != MF_BODY_ONESHOT)
        return "a window site's `body` is ONESHOT (UNSTATED is no call mode; PARAM is "
               "reserved)";
    if (!in_enum(s->site_kind, MF_SK_REPORT)) return "`site_kind` outside mf_site_kind";
    if (s->decl_point > 1) return "`decl_point` is not 0 or 1";
    if (s->on_miss_leaves > 1) return "on_miss_leaves is not 0 or 1";
    if (s->on_miss_leaves && !stmt) return "on_miss_leaves is for an ON_MISS/ASSIGN site only";
    /* NOP's empty range is the chosen alternative's (wf_plan's `hy`): two
       alternatives must agree on it, or the outcome is a choice */
    if (s->empty == MF_EMPTY_NOP && s->nalt == 2) {
        int32_t hy[2];
        for (unsigned a = 0; a < 2; a++) {
            hy[a] = -1;
            const mf_walt *al = &s->alts[a];
            for (unsigned i = 0; i < al->nspan; i++) {
                const mf_wspan *sp = &al->spans[i];
                if (sp->verify != MF_VERIFY_YES) continue;
                for (unsigned j = sp->core_lo; j < (unsigned)sp->core_lo + sp->core_len; j++)
                    if (sp->start + (int32_t)j >= 0 && sp->start + (int32_t)j > hy[a])
                        hy[a] = sp->start + (int32_t)j;
            }
        }
        if (hy[0] != hy[1])
            return "a NOP site's two alternatives disagree on the empty range (their largest "
                   "verify-YES core offset)";
    }
    return NULL;
}

/* ---- TABLE A: the stop, per alternative (window_site.md §2.1) ------------- */

/* The walk's input: the decision and the alternative weighed. */
typedef struct { wf_dec *d; unsigned ai; } wf_x;

/* prefix_k's verify_cost and model_cost, verbatim (§3.2: integer, truncating,
 * in this order). */
static unsigned long long verify_cost(unsigned long long ppm)
{
    unsigned long long tail = ppm < PPM - ppm ? ppm : PPM - ppm;
    return COST(C_VERIFY) + COST(C_MISPRED) * tail / PPM;
}

static unsigned long long model_cost(unsigned long long scan, unsigned long long m,
                                     unsigned long long vc, unsigned long long vr)
{
    return scan + m * vc / PPM + m * vr / PPM * COST(C_ENTER) / PPM;
}

/* A-empty: an empty meet inside a core (C-meet step 1's floor clause). */
static int a_empty_holds(const wf_x *x)
{
    const wf_alt *m = &x->d->a[x->ai];
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (m->p[k].present && m->p[k].core && !count(m->p[k].set)) return 1;
    return 0;
}

/* A-parked: the alternative's verify-YES core position at offset 0 (k0). */
static int a_parked_holds(const wf_x *x)
{
    const wf_pos *p = &x->d->a[x->ai].p[0 - WF_LO];
    return p->present && p->yes && p->ycore;
}

static void a_parked_choose(wf_x *x)
{
    wf_alt *m = &x->d->a[x->ai];
    const uint8_t *k0 = m->p[0 - WF_LO].yset;
    m->has_stop = 1;
    m->stop = 0;
    /* `base`: the parked scan priced by k0's count, not by B's form (§2.1) */
    m->cost = model_cost(count(k0) == 1 ? COST(C_MEMCHR) : COST(C_BITMAP),
                         kit_set_mass(x->d->rate, k0), 0, PPM);
    m->priced = 1;
}

/* F0, the first verify-YES span starting at offset 0 (its position 0 is F0;
 * a D11 bound rides it as a core `{1: any}`, window_site.md §1.2's bounded
 * PF row), or -1. */
static int f0_of(const mf_walt *a)
{
    for (unsigned i = 0; i < a->nspan; i++)
        if (a->spans[i].start == 0 && a->spans[i].verify == MF_VERIFY_YES)
            return (int)i;
    return -1;
}

/* 1 iff span `i` is a WALKED offset: one position, offset != 0 (§1.1: each
 * walked offset its own one-position span, listed in walk-index order). */
static int walked(const mf_walt *a, unsigned i)
{
    return a->spans[i].len == 1 && a->spans[i].start != 0;
}

/* 1 iff walked span `i` may be the STOP: one member, and core (B finds the
 * next byte of its set inside the subject, so a candidate whose stop lies off
 * it would be lost: §1.2 states every walked offset core). */
static int scan_ok(const mf_walt *a, unsigned i)
{
    return walked(a, i) && a->spans[i].core_len && count(a->spans[i].set[0]) == 1;
}

static int a_model_holds(const wf_x *x)
{
    const mf_walt *a = x->d->a[x->ai].alt;
    if (f0_of(a) < 0) return 0;
    for (unsigned i = 0; i < a->nspan; i++)
        if (scan_ok(a, i)) return 1;
    return 0;
}

/* A-MODEL and C-MODEL: prefix_k's selection (§3.2), over the alternative's
 * walked spans' OWN sets. The scan (the stop) runs over every walked span of
 * one member and core (scan cost C_MEMCHR), in listed order; per scan, the other
 * walked spans by ascending mass through prefix_k's exchange sort, taken
 * greedily (`continue`, never an early stop) while the plan holds fewer than
 * MAX_SET - 1 offsets, F0 the first; the least cost, strict, wins. */
static void a_model_choose(wf_x *x)
{
    wf_alt *m = &x->d->a[x->ai];
    const mf_walt *a = m->alt;
    const uint32_t *rate = x->d->rate;
    unsigned long long mass[MF_WMAX_SPAN];
    for (unsigned i = 0; i < a->nspan; i++) mass[i] = kit_set_mass(rate, a->spans[i].set[0]);
    int f0 = f0_of(a);
    int best_si = -1, best_sel[2] = { -1, -1 };
    unsigned best_n = 0;
    unsigned long long best = 0;
    for (unsigned si = 0; si < a->nspan; si++) {
        if (!scan_ok(a, si)) continue;
        int order[MF_WMAX_SPAN], no = 0;
        for (unsigned j = 0; j < a->nspan; j++)
            if (walked(a, j) && j != si) order[no++] = (int)j;
        if (wf_ties[T_CMODEL].to == TIE_EXCHANGE)
            for (int p = 0; p < no; p++)
                for (int q = p + 1; q < no; q++)
                    if (mass[order[q]] < mass[order[p]]) {
                        int t = order[p]; order[p] = order[q]; order[q] = t;
                    }
        int sel[2] = { -1, -1 };
        unsigned n = 1;                                 /* F0 */
        unsigned long long vr = mass[f0], vc = verify_cost(mass[f0]);
        unsigned long long cost = model_cost(COST(C_MEMCHR), mass[si], vc, vr);
        for (int p = 0; p < no && n < COST(MAX_SET) - 1; p++) {
            unsigned long long nv = vr * mass[order[p]] / PPM;
            unsigned long long nvc = vc + verify_cost(mass[order[p]]);
            unsigned long long nc = model_cost(COST(C_MEMCHR), mass[si], nvc, nv);
            if (nc >= cost) continue;
            sel[n - 1] = order[p];
            n++;
            vr = nv;
            vc = nvc;
            cost = nc;
        }
        if (best_si < 0 || cost < best ||
            (cost == best && tie_takes(T_MODEL, a->spans[si].start, a->spans[best_si].start))) {
            best = cost;
            best_si = (int)si;
            best_n = n - 1;
            best_sel[0] = sel[0];
            best_sel[1] = sel[1];
        }
    }
    m->has_stop = 1;
    m->stop = a->spans[best_si].start;
    m->cost = best;
    m->priced = 1;
    m->npick = best_n;
    for (unsigned i = 0; i < best_n; i++) m->pick[i] = a->spans[best_sel[i]].start;
}

/* 1 iff position `p` lies inside a stated run stretch: one member or a cube,
 * covered by a span of two or more positions (the TIE table's first row). */
static int in_stretch(const wf_pos *p)
{
    int a, b;
    return p->multi && shape(p->set, &a, &b);
}

/* A-mass: over the core positions, the least mass (PICK's cube mass), ties
 * per the TIE table (a stretch position to the higher offset, a set position
 * to the lower). A full-set position is no stop (C-bound: the bound alone). */
static int mass_domain(const wf_pos *p)
{
    return p->present && p->core && !full(p->set);
}

static int a_mass_holds(const wf_x *x)
{
    const wf_alt *m = &x->d->a[x->ai];
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (mass_domain(&m->p[k])) return 1;
    return 0;
}

static void a_mass_choose(wf_x *x)
{
    wf_alt *m = &x->d->a[x->ai];
    int bk = -1;
    uint32_t bm = 0;
    for (unsigned k = 0; k < WF_NPOS; k++) {
        const wf_pos *p = &m->p[k];
        if (!mass_domain(p)) continue;
        uint32_t ms = kit_set_sum(x->d->rate, p->set);
        int row = in_stretch(p) ? T_MASS_STRETCH : T_MASS_SET;
        if (bk < 0 || ms < bm ||
            (ms == bm && tie_takes(row, (int32_t)k + WF_LO, bk + WF_LO))) {
            bk = (int)k;
            bm = ms;
        }
    }
    m->has_stop = 1;
    m->stop = bk + WF_LO;
}

static int a_floor_holds(const wf_x *x)
{
    (void)x;
    return 1;
}

static void a_none_choose(wf_x *x)
{
    x->d->a[x->ai].has_stop = 0;
}

/* ---- the family's row contracts ------------------------------------------
 *
 * The family's rows read the window fields (fields.def's last section) and
 * the frame; every other field is irrelevant to them (the family never reads
 * an old field), so they serve every class of each. A field added to
 * fields.def without a line here would DECLINE every family row wherever a
 * site states it: loud in G2's window family. */
#define WF_SERVES_FRAME \
    [FLD_form] = MF_ANY, [FLD_handoff] = MF_ANY,
#define WF_SERVES_REST \
    [FLD_op] = MF_ANY, \
    [FLD_reverse] = MF_ANY, [FLD_empty] = MF_ANY, [FLD_end_back] = MF_ANY, \
    [FLD_pred] = MF_ANY, [FLD_preds] = MF_ANY, [FLD_ret_pred] = MF_ANY, \
    [FLD_guard_by_caller] = MF_ANY, [FLD_on_miss_leaves] = MF_ANY, \
    [FLD_count_by_caller] = MF_ANY, [FLD_span_hi] = MF_ANY, [FLD_denies] = MF_ANY, \
    [FLD_policy] = MF_ANY, [FLD_fn_ref] = MF_ANY, [FLD_table_ref] = MF_ANY, \
    [FLD_fold_kind] = MF_ANY, [FLD_stride] = MF_ANY, [FLD_decl_point] = MF_ANY, \
    [FLD_body] = MF_ANY, [FLD_site_kind] = MF_ANY, \
    [FLD_layer] = MF_ANY, [FLD_need] = MF_ANY, [FLD_s] = MF_ANY, [FLD_n] = MF_ANY, \
    [FLD_lo] = MF_ANY, [FLD_floor] = MF_ANY, [FLD_result] = MF_ANY, \
    [FLD_result_decl] = MF_ANY, [FLD_miss] = MF_ANY, [FLD_on_miss] = MF_ANY, \
    [FLD_step] = MF_ANY, [FLD_more] = MF_ANY, [FLD_peek] = MF_ANY, [FLD_count] = MF_ANY, \
    [FLD_count_start] = MF_ANY, [FLD_on_cand] = MF_ANY, [FLD_on_cand_reach] = MF_ANY, \
    [FLD_member] = MF_ANY, [FLD_table_name] = MF_ANY, [FLD_fn_name] = MF_ANY, \
    [FLD_note] = MF_ANY, [FLD_note_tag] = MF_ANY, [FLD_indent] = MF_ANY, \
    [FLD_comment_tier] = MF_ANY, [FLD_ref] = MF_ANY, [FLD_reflen] = MF_ANY, \
    [FLD_fold] = MF_ANY, [FLD_start] = MF_ANY, \
    [FLD_cursor] = MF_ANY, [FLD_run] = MF_ANY, [FLD_run_len] = MF_ANY,
#define WF_SERVES_LEGACY WF_SERVES_FRAME WF_SERVES_REST [FLD_moved] = MF_ANY,
#define WF_SERVES_WINDOW \
    [FLD_alts] = MF_ANY, [FLD_span_start] = MF_ANY, [FLD_verify] = MF_ANY, \
    [FLD_toffer] = MF_ANY, [FLD_wfloor] = MF_ANY,

#define NU(u) u, (unsigned)(sizeof u / sizeof u[0])
static const gate_use use_entry[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(entry), GATE_ALWAYS } };
static const gate_use use_nothing[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, 0, GATE_ALWAYS } };

/* A Table-A row's contract: keyed on `entry` and `core` (§2.1: every rule
 * keyed on a stated fact, never on a label [rev3 dD2]). */
#define WF_CT_A(name, row, uses, entries, cores) \
    static const gate_contract name = { "wfA", row, NU(uses), { \
        WF_SERVES_LEGACY WF_SERVES_WINDOW \
        [FLD_entry] = (entries), [FLD_core] = (cores), \
    } };
WF_CT_A(ct_a_empty,  "A-empty",  use_nothing, MF_ANY,     MF_ANY)
WF_CT_A(ct_a_parked, "A-parked", use_entry,   CM(PARKED),  CM(CORED))
WF_CT_A(ct_a_model,  "A-model",  use_entry,   CM(RESEED),  CM(CORED))
WF_CT_A(ct_a_mass,   "A-mass",   use_entry,   CM(NOENTRY), CM(CORED))
WF_CT_A(ct_a_floor,  "A-floor",  use_nothing, MF_ANY,     MF_ANY)

typedef struct {
    int  (*holds)(const wf_x *x);
    void (*choose)(wf_x *x);
    const gate_contract *ct;
    const char *path;           /* the decision's path id                    */
    const char *basis;
} wf_arow;

/* TABLE A, first match (window_site.md §2.1, with C-meet's empty-meet floor
 * clause first and the floor row last). A-model's domain is MEASURED (the
 * scan moves, as a singleton: uuid 4.5x, iso-ts 4.8x, stack-frame 7.2x,
 * needleXYZW 17.1x; bignum 0.96-1.02x stayed, offset_k_skip.md §7.3). */
static const wf_arow wf_arows[] = {
    { a_empty_holds,  a_none_choose,   &ct_a_empty,  "empty",
      "C-meet: an empty meet inside a core never holds (window_site.md §2.3 step 1)" },
    { a_parked_holds, a_parked_choose, &ct_a_parked, "parked",
      "role A: the parked scan may skip only bytes that keep the machine parked (today's)" },
    { a_model_holds,  a_model_choose,  &ct_a_model,  "reseed",
      "prefix_k verbatim (§3.2); the domain MEASURED (offset_k_skip.md §7.3)" },
    { a_mass_holds,   a_mass_choose,   &ct_a_mass,   "mass",
      "580/581 (REPORT); pcrec_find_run_rank (parts)" },
    { a_floor_holds,  a_none_choose,   &ct_a_floor,  "floor",
      "no core position constraining a byte: the floor row" },
};
#define WF_NAROWS (sizeof wf_arows / sizeof wf_arows[0])

static const gate_contract *a_ct(size_t i) { return wf_arows[i].ct; }
static int a_holds(size_t i, const void *x) { return wf_arows[i].holds(x); }
static const kit_table wf_atable = { "wfA", WF_NAROWS, a_ct, NULL, NULL, a_holds, NULL };

/* ---- the MARGIN, the choice over alternatives (window_site.md §2.1) -------- */

static int m_one_holds(const wf_x *x)
{
    return x->d->na == 1;
}

/* The two stated alternatives' indices: PARKED's and RESEED's (wf_check). */
static void m_pair(const wf_dec *d, unsigned *pk, unsigned *rs)
{
    *pk = d->a[0].alt->entry == MF_ENTRY_PARKED ? 0 : 1;
    *rs = 1 - *pk;
}

/* MARGIN: a RESEED alternative wins only at less than HALF the least-cost
 * PARKED one, `best * NUM < base * DEN` (prefix_k: `best * MATERIAL_NUM >=
 * base * MATERIAL_DEN` rejects); both priced, the PARKED by A-parked's empty
 * plan and the RESEED by A-model. A tie is the TIE table's. */
static int m_margin_holds(const wf_x *x)
{
    const wf_dec *d = x->d;
    unsigned pk, rs;
    if (d->na != 2) return 0;
    m_pair(d, &pk, &rs);
    if (!d->a[pk].priced || !d->a[rs].priced || wf_arows[d->a[rs].arow].ct != &ct_a_model)
        return 0;
    unsigned long long l = d->a[rs].cost * COST(MATERIAL_NUM);
    unsigned long long r = d->a[pk].cost * COST(MATERIAL_DEN);
    return l < r || (l == r && wf_ties[T_MARGIN].to == TIE_RESEED);
}

static int m_parked_holds(const wf_x *x)
{
    return x->d->na == 2;
}

static const gate_use use_alts[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(alts), GATE_ALWAYS } };
#define WF_CT_M(name, row, alts) \
    static const gate_contract name = { "wfM", row, NU(use_alts), { \
        WF_SERVES_LEGACY \
        [FLD_alts] = (alts), [FLD_entry] = MF_ANY, [FLD_span_start] = MF_ANY, \
        [FLD_core] = MF_ANY, [FLD_verify] = MF_ANY, [FLD_toffer] = MF_ANY, \
        [FLD_wfloor] = MF_ANY, \
    } };
WF_CT_M(ct_m_one,    "M-one",    CM(ONE))
WF_CT_M(ct_m_margin, "MARGIN",   CM(MANY))
WF_CT_M(ct_m_parked, "M-parked", CM(MANY))

enum { M_ONE, M_MARGIN, M_PARKED };
static const struct {
    int (*holds)(const wf_x *x);
    const gate_contract *ct;
    const char *basis;
} wf_mrows[] = {
    [M_ONE]    = { m_one_holds,    &ct_m_one,    "one alternative stated: it" },
    [M_MARGIN] = { m_margin_holds, &ct_m_margin, "ARGUED (offset_k_skip.md §4.5; ipv4's "
                                                 "1.5-1.6x inside the error bars)" },
    [M_PARKED] = { m_parked_holds, &ct_m_parked, "the PARKED alternative: today's baseline" },
};
#define WF_NMROWS (sizeof wf_mrows / sizeof wf_mrows[0])

static const gate_contract *m_ct(size_t i) { return wf_mrows[i].ct; }
static int m_holds(size_t i, const void *x) { return wf_mrows[i].holds(x); }
static const kit_table wf_mtable = { "wfM", WF_NMROWS, m_ct, NULL, NULL, m_holds, NULL };

/* ---- TABLE C: the verify plan (window_site.md §2.3) ------------------------
 *
 * Its rows in step order, each applied where it holds, over the chosen
 * alternative and its stop; the rows sharing a step hold exclusively (C-floor
 * or C-yes; C-model or C-none; C-table or C-own). Three rows are applied
 * elsewhere and listed for the order: C-meet by `merge` (Table A reads the
 * meet), C-bound inside C-floor and C-yes (the bound itself is `plan_of`'s)
 * and C-table/C-own by `plan_of` (phase 2, where the hooks say whether pcrec
 * names its tables). */

/* 1 iff offset `off` is in the plan so far. */
static int in_plan(const wf_dec *d, int32_t off)
{
    for (unsigned i = 0; i < d->np; i++) if (d->poff[i] == off) return 1;
    return 0;
}

static void plan_add(wf_dec *d, int32_t off)
{
    if (!in_plan(d, off) && d->np < WF_NPOS) d->poff[d->np++] = off;
}

static void plan_drop(wf_dec *d, int32_t off)
{
    for (unsigned i = 0; i < d->np; i++)
        if (d->poff[i] == off) { d->poff[i] = d->poff[--d->np]; return; }
}

static const wf_alt *chosen(const wf_dec *d) { return &d->a[d->ch]; }

/* R's MEMBER and STRETCH (the reply owns both, §2.3 [rev3.2 n4]), keyed on
 * R's stated verify (wsc3 rulings 3-4):
 *   verify NO   R is a filter the plan may skip in part (the DFA prefilter's
 *               pinned run, stated as its walk-proven positions): the member
 *               is the least-mass EXACT position (one member), ties per the
 *               TIE table's stretch row, and the stretch the maximal run of
 *               exact positions around it (today's run-pinned compare); no
 *               exact position, no member;
 *   verify YES  R must hold whole (a pre-check part's run): the member is
 *               the least-mass position of all of R (PICK's cube mass, the
 *               same tie: pcrec_find_run_scan_index's rule, the part's scan
 *               and `@idx`), and the stretch R whole (a masked part is one
 *               compare today). */
static void run_member(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    d->run_stated = m->run >= 0;
    if (!d->run_stated) return;
    const mf_wspan *r = &m->alt->spans[m->run];
    int exact = r->verify == MF_VERIFY_NO;
    int bj = -1;
    uint32_t bm = 0;
    for (unsigned j = 0; j < r->len; j++) {
        if (exact && count(r->set[j]) != 1) continue;
        uint32_t ms = kit_set_sum(d->rate, r->set[j]);
        if (bj < 0 || ms < bm ||
            (ms == bm && tie_takes(T_MASS_STRETCH, r->start + (int32_t)j, r->start + bj))) {
            bj = (int)j;
            bm = ms;
        }
    }
    if (bj < 0) {                       /* no exact position: no member */
        d->run_stated = 0;
        return;
    }
    unsigned lo = 0, hi = r->len;
    if (exact) {
        lo = (unsigned)bj;
        hi = (unsigned)bj + 1;
        while (lo > 0 && count(r->set[lo - 1]) == 1) lo--;
        while (hi < r->len && count(r->set[hi]) == 1) hi++;
    }
    d->member = r->start + bj;
    d->run_lo = r->start + (int32_t)lo;
    d->run_len = (int)(hi - lo);
}

static int in_pinned(const wf_dec *d, int32_t o)
{
    return d->pinned && o >= d->run_lo && o < d->run_lo + d->run_len;
}

static int c_floor_holds(const wf_dec *d) { return !chosen(d)->has_stop; }
static int c_stop_holds(const wf_dec *d)  { return chosen(d)->has_stop; }
static int c_model_holds(const wf_dec *d)
{
    return chosen(d)->has_stop && wf_arows[chosen(d)->arow].ct == &ct_a_model;
}
static int c_none_holds(const wf_dec *d)  { return chosen(d)->has_stop && !c_model_holds(d); }
static int c_always(const wf_dec *d)      { (void)d; return 1; }

/* C-floor: the FLOOR row's plan, a byte loop over every position of the
 * chosen alternative's spans; on a PARKED alternative that reads R, so the
 * plan re-seeds wherever a verify-NO span is stated (§3.5) */
static void c_floor(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    for (unsigned i = 0; i < m->alt->nspan; i++)
        if (m->alt->spans[i].verify == MF_VERIFY_NO && m->alt->entry == MF_ENTRY_PARKED)
            d->reseed = 1;
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (m->p[k].present && !full(rd_set(d, &m->p[k]))) plan_add(d, (int32_t)k + WF_LO);
}

/* C-yes: every verify-YES position whose verify-YES meet constrains a byte
 * (on a RESEED alternative, F0 at 0); C-bound keeps a full one out. */
static void c_yes(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (m->p[k].present && m->p[k].yes && !full(m->p[k].yset))
            plan_add(d, (int32_t)k + WF_LO);
}

/* C-model: A-model's greedy picks (prefix_k's `sel[]`). */
static void c_model(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    for (unsigned i = 0; i < m->npick; i++) plan_add(d, m->pick[i]);
}

static void c_none(wf_dec *d) { (void)d; }

/* 1 iff the plan tests offset `o` through a span OTHER than R: a C-model
 * pick, or another verify-YES span constraining a byte there (C-yes). */
static int tested_elsewhere(const wf_dec *d, int32_t o)
{
    const wf_alt *m = chosen(d);
    if (!in_plan(d, o)) return 0;
    for (unsigned i = 0; i < m->npick; i++)
        if (m->pick[i] == o) return 1;
    for (unsigned i = 0; i < m->alt->nspan; i++) {
        const mf_wspan *sp = &m->alt->spans[i];
        if ((int)i == m->run || sp->verify != MF_VERIFY_YES || o < sp->start ||
            o >= sp->start + sp->len)
            continue;
        if (!full(sp->set[o - sp->start])) return 1;
    }
    return 0;
}

/* C-pin: R becomes ONE compare where it is stated (two or more positions),
 * the stop IS its member, and the plan does not already test all of it
 * through the other spans (`[code]`: pf_run_applies_common requires the
 * member to EQUAL the scan; its clause 4 asks whether the model's own
 * selection tests the run, so R's own verify-YES positions do not count).
 * On a PARKED alternative the plan then reads R: it re-seeds. */
static void c_pin(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    if (!m->has_stop || !d->run_stated || d->run_len < 2 || m->stop != d->member) return;
    const mf_wspan *r = &m->alt->spans[m->run];
    int all = 1;
    for (unsigned j = 0; j < r->len; j++)
        if (r->start + (int32_t)j != m->stop && !tested_elsewhere(d, r->start + (int32_t)j))
            all = 0;
    if (all) return;
    d->pinned = 1;
    if (m->alt->entry == MF_ENTRY_PARKED) d->reseed = 1;
    for (int j = 0; j < d->run_len; j++) plan_add(d, d->run_lo + j);
}

/* C-stop: minus the stop's own position (B finds its set, the position's
 * own), except inside a pinned stretch (C-pin keeps it whole). */
static void c_stop(wf_dec *d)
{
    if (!in_pinned(d, chosen(d)->stop)) plan_drop(d, chosen(d)->stop);
}

/* C-asc: ascending offset (today's). */
static void c_asc(wf_dec *d)
{
    for (unsigned i = 1; i < d->np; i++)
        for (unsigned j = i; j > 0 && d->poff[j] < d->poff[j - 1]; j--) {
            int32_t t = d->poff[j]; d->poff[j] = d->poff[j - 1]; d->poff[j - 1] = t;
        }
}

/* C-run: the compare each plan position belongs to, in plan order. A pinned
 * stretch is ONE compare, of exactly its positions; otherwise a maximal
 * stretch of consecutive one-member or cube positions inside ONE stated span
 * of two or more positions, never through a position a one-position span
 * covers ([rev3.1 W2]: ofs_test_model's one term per selected offset).
 * Grouping reads adjacency, so it orders first (C-asc is idempotent). */
static void c_run(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    uint8_t term = 0;
    c_asc(d);
    for (unsigned i = 0; i < d->np; i++) {
        if (i && d->poff[i] == d->poff[i - 1] + 1) {
            int32_t o = d->poff[i];
            int join;
            if (in_pinned(d, o) || in_pinned(d, o - 1)) {
                join = in_pinned(d, o) && in_pinned(d, o - 1);
            } else {
                const wf_pos *p = &m->p[o - WF_LO], *q = &m->p[o - 1 - WF_LO];
                int a, b;
                join = !p->one_pos && !q->one_pos &&
                       shape(rd_set(d, p), &a, &b) && shape(rd_set(d, q), &a, &b);
                int same = 0;       /* both inside ONE stated span of >= 2 */
                for (unsigned k = 0; join && !same && k < m->alt->nspan; k++) {
                    const mf_wspan *sp = &m->alt->spans[k];
                    same = sp->len >= 2 && o - 1 >= sp->start && o < sp->start + sp->len;
                }
                join = join && same;
            }
            if (join) {
                d->pterm[i] = d->pterm[i - 1];
                continue;
            }
        }
        d->pterm[i] = term++;
    }
}

static const struct {
    int         step;
    const char *row;
    int       (*holds)(const wf_dec *d);
    void      (*apply)(wf_dec *d);      /* NULL: applied where the doc says */
    const char *rule;
} wf_crows[] = {
    { 1, "C-meet",  c_always,      NULL,
      "positions at one offset, across spans, are ONE position: their sets' intersection "
      "over the spans the plan may read (`merge`, before Table A)" },
    { 2, "C-floor", c_floor_holds, c_floor,
      "the floor row (no stop): every position of the chosen alternative's spans" },
    { 2, "C-yes",   c_stop_holds,  c_yes,   "every verify-YES position" },
    { 2, "C-bound", c_always,      NULL,
      "a FULL-SET position is never a plan test: its only role is the hoisted core bound "
      "(`plan_of`; window_site.md F3, end_back a core position). Applied inside C-yes (over "
      "the verify-YES meet) and C-floor (over the meet the plan reads)" },
    { 2, "C-model", c_model_holds, c_model,
      "on a RESEED alternative: plus prefix_k's greedy pick among the walked offsets" },
    { 2, "C-none",  c_none_holds,  c_none,  "otherwise no verify-NO position" },
    { 3, "C-pin",   c_stop_holds,  c_pin,
      "R becomes ONE compare when stated, the stop IS its member and the plan does not "
      "already test all of it through the other spans; the stretch is the exact run around "
      "the member (verify NO) or R whole (verify YES; wsc3 rulings 3-4)" },
    { 4, "C-stop",  c_stop_holds,  c_stop,
      "minus the stop's own position, except inside a pinned stretch" },
    { 5, "C-run",   c_always,      c_run,
      "a maximal stretch of consecutive one-member or cube positions inside ONE stated span "
      "is one compare; never across a one-position span" },
    { 6, "C-table", c_always,      NULL,
      "an offered table, pcrec's name (`plan_of`, phase 2: the hooks name it)" },
    { 6, "C-own",   c_always,      NULL,    "else the kit's own set test (`plan_of`)" },
    { 7, "C-asc",   c_always,      c_asc,   "ascending offset (today's)" },
};
#define WF_NCROWS (sizeof wf_crows / sizeof wf_crows[0])

static void c_plan(wf_dec *d)
{
    d->np = 0;
    d->pinned = 0;
    d->reseed = chosen(d)->alt->entry == MF_ENTRY_RESEED;
    run_member(d);
    for (size_t i = 0; i < WF_NCROWS; i++)
        if (wf_crows[i].apply && wf_crows[i].holds(d)) wf_crows[i].apply(d);
}

/* ---- THE DECISION (phase 1) ------------------------------------------------ */

/* Tables A, M and C over window site `s` (wf_check'd) into `d`; the walks are
 * traced unless `quiet`. */
static void decide(const mf_art *art, const mf_site *s, int quiet, wf_dec *d)
{
    memset(d, 0, sizeof *d);
    d->art = art;
    d->s = s;
    d->rate = kit_byte_rate(art);
    d->na = s->nalt;
    for (unsigned ai = 0; ai < d->na; ai++) {
        merge(&s->alts[ai], &d->a[ai]);
        wf_facts f = { s, &s->alts[ai] };
        gate_in in = { s, NULL, NULL, NULL, &f };
        gate_tctx tc = { art, "wfA", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
        gate_verdict why = { 0, 0 };
        wf_x x = { d, ai };
        size_t r = kit_walk(&wf_atable, 0, &in, MF_PH_DEFINE, 0, &x, &tc, &why);
        /* the floor row serves every class: the walk always chooses */
        d->a[ai].arow = r < WF_NAROWS ? r : WF_NAROWS - 1;
        wf_arows[d->a[ai].arow].choose(&x);
    }
    wf_facts f = { s, NULL };
    gate_in in = { s, NULL, NULL, NULL, &f };
    gate_tctx tc = { art, "wfM", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
    gate_verdict why = { 0, 0 };
    wf_x x = { d, 0 };
    size_t mr = kit_walk(&wf_mtable, 0, &in, MF_PH_DEFINE, 0, &x, &tc, &why);
    if (mr == M_MARGIN) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)rs;
    } else if (mr == M_PARKED) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)pk;
    } else {
        d->ch = 0;
    }
    c_plan(d);
    snprintf(d->path, sizeof d->path, "%s%s", wf_arows[d->a[d->ch].arow].path,
             d->pinned ? "+pin" : "");
}

static void reply_of(const wf_dec *d, mf_wreply *out)
{
    const wf_alt *m = &d->a[d->ch];
    memset(out, 0, sizeof *out);
    out->alt = (uint8_t)d->ch;
    out->reseed = (uint8_t)d->reseed;
    out->has_stop = (uint8_t)m->has_stop;
    if (m->has_stop) {
        out->stop = m->stop;
        memcpy(out->stop_set, rd_set(d, &m->p[m->stop - WF_LO]), 32);
    }
    out->nplan = (uint8_t)d->np;
    for (unsigned i = 0; i < d->np; i++) {
        out->plan[i] = d->poff[i];
        out->plan_term[i] = d->pterm[i];
    }
    out->pinned = (uint8_t)d->pinned;
    out->run_stated = (uint8_t)d->run_stated;
    if (d->run_stated) {
        out->run_member = d->member;
        out->run_lo = d->run_lo;
        out->run_len = (uint8_t)d->run_len;
    }
    snprintf(out->path, sizeof out->path, "%s", d->path);
}


/* -1 where the art has failed, the site is not a window site the family
 * reads, or the decision's heap allocation is refused (OOM, R-28): every
 * pcrec caller turns -1 into pcrec_ctx_fail, so a refusal is never read as
 * a decision. */
int mf_wdecide(const mf_art *art, const mf_site *site, mf_wreply *out)
{
    memset(out, 0, sizeof *out);
    /* the decision reads no frame fact (§0): only the window facts are held */
    if (art->err[0] || site->abi != MF_SITE_ABI || !site->nalt ||
        wf_check(site, 0))
        return -1;
    /* the decision is ~10 KB, so it lives on the heap (R-28: a stack frame
       above 4 KB is a kit defect; terms.c's targets are the precedent); the
       ask is pure, so not the art's arena; a refused allocation is -1 */
    wf_dec *d = calloc(1, sizeof *d);
    if (!d) return -1;
    decide(art, site, 1, d);
    reply_of(d, out);
    free(d);
    return 0;
}

/* ---- THE PLAN the text tests (phase 2) ------------------------------------ */

struct wf_plan {
    unsigned n;                         /* tested positions: the stop and the plan */
    int32_t  off[WF_NPOS];
    uint8_t  set[WF_NPOS][32];
    uint8_t  core[WF_NPOS];
    uint32_t table[WF_NPOS];            /* C-table's offer, 0: C-own            */
    int      ncore;                     /* the hoisted bound: core positions'   */
    int32_t  clo, chi;                  /* least and largest offset             */
    int      hy_set;                    /* THE EMPTY RANGE: the largest offset  */
    int32_t  hy;                        /* >= 0 of a verify-YES core position   */
    uint8_t  wfloor;
    uint8_t  reads_table;
    /* the family row rendering it (wf_floor_arm, or E-find's wf_find_arm),
       its libc and include bounds (the text's own, wf_plan_class), and on
       E-find (D172 S3, wf_find_prepare): */
    const struct arm *row;
    uint8_t  libc;
    uint32_t includes;
    int      stop_ix;                   /* the stop's index in off[]            */
    uint8_t  stop_alone;                /* C-stop dropped it: B finds it, the
                                           test does not repeat it             */
    fd_form  pick;                      /* B: the FIND slot's pick, its row,  */
    const char *brow;                   /* and its renderer (wf_brows)        */
    uint8_t  bren;
    const mf_site *fsite;               /* B-fn: the plan as the offset-skip
                                           function's site and predicate       */
    int8_t   grp[WF_NPOS];              /* C-run's compare: a run term of
                                           `runs`, -1 a lone position          */
    unsigned nrun;
    mf_pred *runs;                      /* the run compares' terms (runcmp.c),
                                           built at define only                */
    uint8_t  drow;                      /* Table D's row (wf_drows); D-hors:  */
    int32_t  hl;                        /* its probe offset and the shift
                                           table sh[] over its window          */
    uint8_t  sh[256];
};

/* C-table's offer at offset `off`: a covering span's table whose own set is
 * the set tested there; 0 where none is (C-own). */
static uint32_t offer_at(const mf_walt *al, int32_t off, const uint8_t set[32])
{
    for (unsigned i = 0; i < al->nspan; i++) {
        const mf_wspan *sp = &al->spans[i];
        if (off < sp->start || off >= sp->start + sp->len) continue;
        unsigned j = (unsigned)(off - sp->start);
        if (sp->table_ref[j] && !memcmp(sp->set[j], set, 32)) return sp->table_ref[j];
    }
    return 0;
}

static void plan_of(const wf_dec *d, const mf_hooks *def, struct wf_plan *w)
{
    const wf_alt *m = &d->a[d->ch];
    memset(w, 0, sizeof *w);
    w->wfloor = d->s->wfloor;
    w->row = &wf_floor_arm;
    w->stop_ix = -1;
    int32_t offs[WF_NPOS + 1];
    unsigned n = 0;
    for (unsigned i = 0; i < d->np; i++) offs[n++] = d->poff[i];
    if (m->has_stop && !in_plan(d, m->stop)) offs[n++] = m->stop;
    for (unsigned i = 1; i < n; i++)
        for (unsigned j = i; j > 0 && offs[j] < offs[j - 1]; j--) {
            int32_t t = offs[j]; offs[j] = offs[j - 1]; offs[j - 1] = t;
        }
    for (unsigned i = 0; i < n; i++) {
        const wf_pos *p = &m->p[offs[i] - WF_LO];
        w->grp[i] = -1;
        w->off[i] = offs[i];
        if (m->has_stop && offs[i] == m->stop) w->stop_ix = (int)i;
        memcpy(w->set[i], rd_set(d, p), 32);
        w->core[i] = (uint8_t)rd_core(d, p);
        w->table[i] = def && def->table_name ? offer_at(m->alt, offs[i], w->set[i]) : 0;
        if (w->table[i]) w->reads_table = 1;
        if (w->core[i]) {
            if (!w->ncore || offs[i] < w->clo) w->clo = offs[i];
            if (!w->ncore || offs[i] > w->chi) w->chi = offs[i];
            w->ncore = 1;
        }
    }
    w->n = n;
    /* THE BOUND also spans every verify-YES core position the plan does not
       test (C-bound's full-set positions: a D11 `{1: any}` is the bound
       alone), since every yielded candidate must hold it inside the subject */
    for (unsigned k = 0; k < WF_NPOS; k++) {
        const wf_pos *p = &m->p[k];
        int32_t o = (int32_t)k + WF_LO;
        if (!p->present || !p->yes || !p->ycore) continue;
        if (!w->ncore || o < w->clo) w->clo = o;
        if (!w->ncore || o > w->chi) w->chi = o;
        w->ncore = 1;
        if (o >= 0 && (!w->hy_set || o > w->hy)) {
            w->hy = o;
            w->hy_set = 1;
        }
    }
}

/* ---- TABLE E's legacy rows: the plan as today's row's site ----------------
 *
 * E-func and E-stmt render the plan through the row today's site of that
 * shape renders with (the offset-skip function, the prefilter finds, the
 * generic row), selected by the composer's walk over the plan TRANSLATED into
 * that row's site: one term per compare (a SET term per lone position, a RUN
 * term per C-run or C-pin stretch), the stop's term the scanned one, every
 * term REQUIRED, ascending. Such a site's semantics are the plan's exactly
 * where every tested position is CORE (a term reading outside the subject
 * fails, as a core position does), a full-set position is only the bounded
 * range's end (`end_back`), and its empty range is the plan's: `legacy_ok`. */

typedef struct {
    mf_site  site;
    uint8_t  run[MF_MAX_TERM][MF_WSPAN_POS];
    uint8_t  mask[MF_MAX_TERM][MF_WSPAN_POS];
} wf_legacy;

/* 1 iff the plan translates into a legacy site with the plan's semantics;
 * *eb its `end_back`. */
static int legacy_ok(const wf_dec *d, const struct wf_plan *w, unsigned *eb)
{
    int32_t t = 0, tlo = 0;
    int terms = 0, neg_only = 1;
    for (unsigned i = 0; i < w->n; i++) {
        if (!w->core[i]) return 0;
        if (full(w->set[i])) continue;      /* the stop's own set, the whole alphabet */
        if (!terms || w->off[i] > t) t = w->off[i];
        if (!terms || w->off[i] < tlo) tlo = w->off[i];
        terms = 1;
        if (w->off[i] >= 0) neg_only = 0;
    }
    if (!terms) return 0;
    /* one term per compare at most: bounded by the positions, so a plan of
       more positions than a predicate holds terms stays the floor's */
    unsigned np = 0;
    for (unsigned i = 0; i < w->n; i++) np += !full(w->set[i]);
    if (np > MF_MAX_TERM) return 0;
    /* the bound past the terms is the range's end (`end_back`), at 1 only;
       inside the terms the core terms imply it; below them none expresses it */
    *eb = 0;
    if (w->ncore && w->clo < tlo) return 0;
    if (w->ncore && w->chi > t) {
        if (neg_only || w->chi > 1) return 0;
        *eb = (unsigned)w->chi;
    }
    /* the empty range: legacy reads-below `lo > n`, else `lo + eb >= n` */
    int legacy_rb = neg_only && !*eb;
    if (d->s->empty == MF_EMPTY_NOP || d->s->empty == MF_EMPTY_EXCLUDED) {
        if (legacy_rb ? w->hy_set : !w->hy_set || (unsigned)w->hy != *eb) return 0;
    }
    return 1;
}

/* The bytes and mask of the RUN term over plan positions [from, to). */
static void run_bytes(const struct wf_plan *w, unsigned from, unsigned to,
                      uint8_t *run, uint8_t *mask, int *exact)
{
    *exact = 1;
    for (unsigned i = from; i < to; i++) {
        int a, b;
        if (shape(w->set[i], &a, &b) == 2) {
            run[i - from] = (uint8_t)a;
            mask[i - from] = (uint8_t)~(a ^ b);
            *exact = 0;
        } else {
            run[i - from] = (uint8_t)a;
            mask[i - from] = 0xFF;
        }
    }
}

static void translate(const wf_dec *d, const struct wf_plan *w, unsigned eb, wf_legacy *L)
{
    const mf_site *s = d->s;
    const wf_alt *m = &d->a[d->ch];
    mf_site *t = &L->site;
    memset(L, 0, sizeof *L);
    /* the frame, as stated */
    t->abi = MF_SITE_ABI;
    t->form = s->form;
    t->op = s->op;
    t->handoff = s->handoff;
    t->empty = s->empty;
    t->end_back = (uint8_t)eb;
    t->use = s->use;
    t->on_miss_leaves = s->on_miss_leaves;
    t->span_lo = s->span_lo;
    t->span_hi = s->span_hi;
    t->cand_ppm_lo = s->cand_ppm_lo;
    t->cand_ppm_hi = s->cand_ppm_hi;
    t->policy = s->policy;
    t->denies = s->denies;
    t->opts = s->opts;
    t->decl_point = s->decl_point;
    t->body = s->body;
    t->site_kind = s->site_kind;
    t->ret_pred = MF_NO_PRED;
    mf_pred *p = &t->pred;
    p->need = MF_REQUIRED;
    p->fn_ref = s->pred.fn_ref;         /* the FUNC name: a frame fact (§0)    */
    p->plan_hint = MF_NO_PRED;
    int below = 1;
    /* the terms: each plan compare (pterm) and the stop, ascending */
    for (unsigned i = 0; i < w->n;) {
        if (full(w->set[i])) { i++; continue; }
        unsigned j = i + 1;
        int grouped = 0;
        if (in_plan(d, w->off[i])) {
            unsigned pi = 0;
            while (d->poff[pi] != w->off[i]) pi++;
            while (j < w->n && in_plan(d, w->off[j])) {
                unsigned pj = 0;
                while (d->poff[pj] != w->off[j]) pj++;
                if (d->pterm[pj] != d->pterm[pi]) break;
                j++;
            }
            grouped = j - i >= 2;
        }
        mf_term *tm = &p->term[p->nterm];
        tm->offset = w->off[i];
        tm->need = MF_REQUIRED;
        tm->ppm_lo = 0;
        tm->ppm_hi = MF_PPM_FULL;
        if (grouped) {
            int exact;
            tm->kind = MF_T_RUN;
            tm->run_len = j - i;
            run_bytes(w, i, j, L->run[p->nterm], L->mask[p->nterm], &exact);
            tm->run = L->run[p->nterm];
            tm->mask = exact ? NULL : L->mask[p->nterm];
        } else {
            tm->kind = MF_T_SET;
            memcpy(tm->set, w->set[i], 32);
            tm->table_ref = offer_at(m->alt, w->off[i], w->set[i]);
        }
        if (m->has_stop && m->stop >= w->off[i] && m->stop < w->off[j - 1] + 1) {
            p->plan_hint = p->nterm;
            p->plan_pos = (uint16_t)(m->stop - w->off[i]);
        }
        if (w->off[j - 1] >= 0) below = 0;
        p->nterm++;
        i = j;
    }
    /* the scanned RUN term's ranking (RQ-2): its positions by PICK's cube
       mass, ties to the higher position, as pcrec_find_run_rank */
    if (p->plan_hint != MF_NO_PRED && p->term[p->plan_hint].kind == MF_T_RUN) {
        const mf_term *tm = &p->term[p->plan_hint];
        unsigned n = tm->run_len;
        for (unsigned k = 0; k < n; k++) {
            unsigned i = n - 1 - k, j = k;
            uint8_t cube[32];
            memset(cube, 0, 32);
            unsigned msk = tm->mask ? tm->mask[i] : 0xFFu, f = ~msk & 0xFFu;
            for (unsigned b = f;; b = (b - 1) & f) {
                cube[(tm->run[i] | b) >> 3] |= (uint8_t)(1u << ((tm->run[i] | b) & 7));
                if (!b) break;
            }
            uint32_t c = kit_set_sum(d->rate, cube);
            while (j > 0 && p->rank_ppm[j - 1] > c) {
                p->rank_ppm[j] = p->rank_ppm[j - 1];
                p->rank_pos[j] = p->rank_pos[j - 1];
                j--;
            }
            p->rank_ppm[j] = c;
            p->rank_pos[j] = (uint16_t)i;
        }
        p->rank_n = (uint8_t)n;
    }
    /* span 0's class (MF_SITE_ABI 18): a context stop where every tested
       position lies below the candidate (each is core: a read outside the
       subject fails its term, the one rule the rows render), else span 0 */
    p->span_class = below ? MF_SPAN_CONTEXT : MF_SPAN_BOUNDED;
}

/* ---- TABLE E: the frame (window_site.md §2.6) ------------------------------ */

/* E-find's id: its Table E row's deny, its arm's name, its refusals. */
#define WF_FIND_ID "window-search"
/* D-hors's id: its Table D row's deny. */
#define WF_HORS_ID "window-skip"

/* E-find's setup (wf_find_decide), computed ONCE per selection before Table
 * E walks, read by its predicate and its prepare: Tables D and B over the
 * plan's stop. */
typedef struct {
    int         holds;      /* E-find renders this plan                      */
    size_t      drow;       /* Table D's row (D_HORS, D_ONE)                 */
    int32_t     wlo, whi;   /* D-hors's window                               */
    fd_form     pick;       /* D-one: Table B's pick, its deciding row and   */
    const char *brow;       /* its renderer (wf_brows)                       */
    size_t      bren;
    wf_legacy  *fn;         /* B-fn: the plan as the function's predicate    */
} wf_fx;

typedef struct {
    const wf_dec         *d;
    struct wf_plan       *w;
    const mf_hooks       *def;
    unsigned              gphases;
    wf_legacy            *L;        /* the translation's storage, wf_prepare's */
    const wf_fx          *fx;       /* E-find's setup                          */
} wf_ex;

/* E-func / E-stmt hold where the plan translates with its own semantics
 * (legacy_ok) AND today's rows serve the translation in this frame (the
 * composer's walk, the finder's routed pick included, asked quietly): a
 * frame today's PF rows never meet (ON_MISS, AT_N, a NOP that does not
 * leave, ...) is E-find's or E-generic's. A REPORT site is never translated:
 * the composer refuses REPORT stated in terms (compose.c select_arm). */
static int e_legacy_holds(const void *x)
{
    const wf_ex *e = x;
    unsigned eb;
    if (e->d->s->site_kind == MF_SK_REPORT || !legacy_ok(e->d, e->w, &eb)) return 0;
    translate(e->d, e->w, eb, e->L);
    return kit_legacy_serves(e->d->art, &e->L->site, e->def, e->gphases);
}

/* E-FIND (D172 S3; the kit manager's R1 ruling): the family's own
 * find-then-verify text on the floor's candidate loop, wherever the frame
 * is STMT/ASSIGN (its contract) and its setup renders the plan: a STOP
 * (Table A chose one, its set short of every byte) that Table D resumes by
 * D-hors, or whose find Table B decides and one of B's renderers renders
 * (wf_find_decide). Keyed on no consumer kind: REPORT reaches it because
 * the legacy rows exclude REPORT, every other site only where no legacy
 * row serves its plan. */
static int e_find_holds(const void *x)
{
    const wf_ex *e = x;
    return e->fx->holds;
}

/* E-generic, the floor, serves every frame and plan but a REPORT site's:
 * there the floor's byte loop is COV, R-27's 10x loss to the default build
 * on literal cells, so a REPORT site E-find does not render (its deny
 * `window-search`, a frame E-find does not serve) is REFUSED, and the host keeps
 * its default (pcrec's C13 declines `cover`; window_site.md §5.2's deny row,
 * the kit manager's R2 ruling). */
static int e_generic_holds(const void *x)
{
    const wf_ex *e = x;
    return e->d->s->site_kind != MF_SK_REPORT;
}

static const gate_use use_e_none[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, 0, GATE_ALWAYS } };
#define WF_CT_E(name, row, forms, handoffs, floors) \
    static const gate_contract name = { "wfE", row, NU(use_e_none), { \
        WF_SERVES_REST [FLD_moved] = MF_ANY, \
        [FLD_alts] = MF_ANY, [FLD_entry] = MF_ANY, [FLD_span_start] = MF_ANY, \
        [FLD_core] = MF_ANY, [FLD_verify] = MF_ANY, [FLD_toffer] = MF_ANY, \
        [FLD_form] = (forms), [FLD_handoff] = (handoffs), [FLD_wfloor] = (floors), \
    } };
/* E-func: FUNC/RETURN with no expression floor (today's `static inline
   size_t`, D155's seam); E-stmt: STMT/ASSIGN or ON_MISS (today's PF block).
   The legacy row they hand the plan to states its own contract over the
   hooks (miss n, identifiers, ...) and the composer's walk declines it where
   it does not serve them, down to the generic row. */
WF_CT_E(ct_e_func, "E-func", CM(FUNC), CM(RETURN), CM(W_SUBJECT))
WF_CT_E(ct_e_stmt, "E-stmt", CM(STMT), CM(ASSIGN) | CM(ON_MISS), MF_ANY)

/* E-find's and the floor's contracts are their arms' (below). */
static const gate_contract wf_find_ct, wf_floor_ct;

enum { E_FUNC, E_STMT, E_FIND, E_GENERIC };
/* THE ORDER (the kit manager's R1 ruling): the legacy rows first, so every
 * site the legacy translation serves keeps today's bytes; E-find before the
 * floor, so S3's movers are exactly the sites the legacy rows decline that
 * reach E-find: REPORT (which they exclude) and, inside E-find, D-hors. */
static const struct {
    int (*holds)(const void *x);
    const gate_contract *ct;
    const char *opt;            /* its options.def deny, or NULL            */
} wf_erows[] = {
    [E_FUNC]    = { e_legacy_holds,  &ct_e_func,   NULL },
    [E_STMT]    = { e_legacy_holds,  &ct_e_stmt,   NULL },
    [E_FIND]    = { e_find_holds,    &wf_find_ct,  WF_FIND_ID },
    [E_GENERIC] = { e_generic_holds, &wf_floor_ct, NULL },
};
#define WF_NEROWS (sizeof wf_erows / sizeof wf_erows[0])

static const gate_contract *e_ct(size_t i) { return wf_erows[i].ct; }
static int e_holds(size_t i, const void *x) { return wf_erows[i].holds(x); }
static const char *e_opt(size_t i) { return wf_erows[i].opt; }
static const kit_table wf_etable = { "wfE", WF_NEROWS, e_ct, NULL, NULL, e_holds, e_opt };

/* ---- E-FIND's PLAN (wf_find_prepare): C-run's compares and Table D -------- */

/* 1 iff every position of `w` in [from, to) is core and a run position (one
 * member or a cube): such a stretch is ONE run compare (runcmp.c reads
 * exactly its bytes, so every byte must lie inside the subject). */
static int run_group_ok(const struct wf_plan *w, unsigned from, unsigned to)
{
    int a, b;
    for (unsigned i = from; i < to; i++)
        if (!w->core[i] || !shape(w->set[i], &a, &b)) return 0;
    return 1;
}

/* C-run's compares over `w`: a maximal stretch of plan positions sharing
 * one compare (the decision's `pterm`) becomes one RUN term where
 * run_group_ok holds (w->grp, w->nrun); every other position is lone (-1),
 * the stop included where C-stop dropped it. The grouping alone: the query
 * reads the class, which reads the count; the terms are build_runs'. */
_Static_assert(MF_MAX_TERM - 1 <= INT8_MAX, "a C-run term index (< MF_MAX_TERM) is an int8_t: w->grp[k] = (int8_t)nterm");
static void find_groups(const wf_dec *d, struct wf_plan *w)
{
    int key[WF_NPOS];
    for (unsigned i = 0; i < w->n; i++) {
        key[i] = -1;
        w->grp[i] = -1;
        for (unsigned k = 0; k < d->np; k++)
            if (d->poff[k] == w->off[i]) key[i] = d->pterm[k];
    }
    w->nrun = 0;
    for (unsigned i = 0; i < w->n;) {
        unsigned j = i + 1;
        while (key[i] >= 0 && j < w->n && key[j] == key[i] && w->off[j] == w->off[j - 1] + 1) j++;
        if (j - i >= 2 && run_group_ok(w, i, j) && w->nrun < MF_MAX_TERM) {
            for (unsigned k = i; k < j; k++) w->grp[k] = (int8_t)w->nrun;
            w->nrun++;
        }
        i = j;
    }
}

/* C-run's RUN terms (w->runs, runcmp.c's input), one per group find_groups
 * formed, in the art's arena: the define's alone. 0, or -1 out of memory. */
static int build_runs(const mf_art *art, struct wf_plan *w)
{
    w->runs = art->a->alloc(art->a->u, sizeof *w->runs);
    if (!w->runs) return -1;
    memset(w->runs, 0, sizeof *w->runs);
    w->runs->need = MF_REQUIRED;
    for (unsigned i = 0; i < w->n;) {
        unsigned j = i + 1;
        if (w->grp[i] < 0) { i = j; continue; }
        while (j < w->n && w->grp[j] == w->grp[i]) j++;
        mf_term *t = &w->runs->term[w->grp[i]];
        uint8_t *run = art->a->alloc(art->a->u, j - i);
        uint8_t *mask = art->a->alloc(art->a->u, j - i);
        if (!run || !mask) return -1;
        int exact;
        run_bytes(w, i, j, run, mask, &exact);
        t->kind = MF_T_RUN;
        t->offset = w->off[i];
        t->need = MF_REQUIRED;
        t->ppm_hi = MF_PPM_FULL;
        t->run_len = j - i;
        t->run = run;
        t->mask = exact ? NULL : mask;
        w->runs->nterm++;
        i = j;
    }
    return 0;
}

/* D-hors's WINDOW: the core of the first verify-YES span of the chosen
 * alternative whose core holds the stop (window_site.md §2.5: "skip by the
 * window's end, the stop span's core"); *lo and *hi its least and largest
 * offsets; 0 where none. */
static int hors_window(const wf_dec *d, int32_t *lo, int32_t *hi)
{
    const wf_alt *m = &d->a[d->ch];
    for (unsigned i = 0; i < m->alt->nspan; i++) {
        const mf_wspan *sp = &m->alt->spans[i];
        if (sp->verify != MF_VERIFY_YES || !sp->core_len) continue;
        int32_t a = sp->start + sp->core_lo, b = a + sp->core_len - 1;
        if (m->stop < a || m->stop > b) continue;
        *lo = a;
        *hi = b;
        return 1;
    }
    return 0;
}

/* D-hors's shift table: sh[b] the least t >= 1 with b in the set the text
 * TESTS at offset whi - t (every byte where an offset is untested), else the
 * window's length: a candidate c + u, 0 < u < sh[b], would need b at its
 * own offset whi - u, which no tested set there holds. */
_Static_assert(MF_MAX_SPAN_POS < 256, "a D-hors shift (at most a window's length) is a uint8_t: sh[b] = (uint8_t)t");
static void hors_table(const struct wf_plan *w, int32_t wlo, int32_t whi, uint8_t sh[256])
{
    for (unsigned b = 0; b < 256; b++) {
        int32_t t = 1;
        for (; whi - t >= wlo; t++) {
            int tested = 0, in = 0;
            for (unsigned i = 0; i < w->n; i++)
                if (w->off[i] == whi - t) { tested = 1; in = in_set(w->set[i], b); }
            if (!tested || in) break;
        }
        sh[b] = (uint8_t)t;
    }
}

/* ---- TABLE D: the resume (window_site.md §2.5) ----------------------------
 *
 * A kit_table on the one walk (code review r1 C7), first match, asked on
 * E-find's text only (a legacy row's own text resumes at c + 1, as today,
 * and so does the floor, which has no find to replace). Its walk input is
 * the decision, the plan and D-hors's window (`wf_dx`, computed before the
 * walk: the predicates only read). Each row carries its actions: its
 * plan's preparation here, its text in E-FIND's TEXT (wf_d_text), so no
 * other code asks which row holds (code review r2 R2-7). */
typedef struct {
    const wf_dec         *d;
    const struct wf_plan *w;
    int                   hw;           /* hors_window found one          */
    int32_t               wlo, whi;
} wf_dx;

/* D-hors: the stop set's mass is at least HORS_MIN and its window (the
 * stop span's core, hors_window) has two positions or more, the last at an
 * offset >= 0 (the probe reads inside the hoisted bound: the window's core
 * is the plan's, so its last offset is at most the bound's). The probe is
 * the window's LAST position; hors_table its shift. */
static int d_hors_holds(const void *x)
{
    const wf_dx *dx = x;
    if (!dx->hw || dx->whi - dx->wlo < 1 || dx->whi < 0) return 0;
    return kit_set_mass(dx->d->rate, dx->w->set[dx->w->stop_ix]) >= COST(HORS_MIN);
}

/* D-one, the floor's resume: holds wherever it is asked. */
static int d_one_holds(const void *x)
{
    (void)x;
    return 1;
}

/* D-hors's plan: the probe at the window's last offset and the shift table
 * over the window. */
static void d_hors_prepare(struct wf_plan *w, const wf_fx *fx)
{
    w->hl = fx->whi;
    hors_table(w, fx->wlo, fx->whi, w->sh);
}

/* A Table-D row's contract: D-hors's window is a stated core (`core`); D-one
 * reads nothing. Both are asked only on E-find's frame, whose contract is
 * its arm's (below). */
#define WF_CT_D(name, row, cores) \
    static const gate_contract name = { "wfD", row, NU(use_nothing), { \
        WF_SERVES_LEGACY WF_SERVES_WINDOW \
        [FLD_entry] = MF_ANY, [FLD_core] = (cores), \
    } };
WF_CT_D(ct_d_hors, "D-hors", CM(CORED))
WF_CT_D(ct_d_one,  "D-one",  MF_ANY)

enum { D_HORS, D_ONE };
static const struct {
    int (*holds)(const void *x);
    const gate_contract *ct;
    const char *opt;            /* its options.def deny, or NULL             */
    uint8_t     finds;          /* its text finds the stop (Table B); D-hors
                                   probes the window's end instead           */
    void (*prepare)(struct wf_plan *w, const wf_fx *fx);    /* or NULL       */
    const char *path;           /* the path id's suffix                      */
    const char *basis;
} wf_drows[] = {
    [D_HORS] = { d_hors_holds, &ct_d_hors, WF_HORS_ID, 0, d_hors_prepare, "+hors",
                 "job 581 (r27b_report.md RESULT): HRS wins hex8 2-6x on real and no-hit "
                 "text; HORS_MIN PROVISIONAL (plan_cost.def)" },
    [D_ONE]  = { d_one_holds,  &ct_d_one,  NULL, 1, NULL, "",
                 "the floor (today's): c + 1" },
};
#define WF_NDROWS (sizeof wf_drows / sizeof wf_drows[0])

static const gate_contract *d_ct(size_t i) { return wf_drows[i].ct; }
static int d_holds(size_t i, const void *x) { return wf_drows[i].holds(x); }
static const char *d_opt(size_t i) { return wf_drows[i].opt; }
static const kit_table wf_dtable = { "wfD", WF_NDROWS, d_ct, NULL, NULL, d_holds, d_opt };

/* ---- TABLE B's RENDERERS: the FIND slot's pick in E-find's text -----------
 *
 * Table B is the finder's FIND slot (fd_find): it DECIDES the stop's find
 * (D1, D1c, D1w, PAIR, R7w, ...). These rows decide nothing about it: first
 * match over the pick and the plan, each renders the pick it names, and a
 * pick no row names (an unbuilt form: V1, W64, A3, NONE) leaves E-find with
 * no text for the plan. The text is in E-FIND's TEXT, below. */
typedef struct {
    const wf_dec         *d;
    const struct wf_plan *w;
    const mf_hooks       *def;
    fd_form               pick;
    wf_legacy            *fn;       /* B-fn's translation, where it holds    */
} wf_bx;

/* B-fn: the pick is PAIR and the plan IS the offset-skip function's
 * predicate (legacy_ok with no range end beyond the terms; one RUN term
 * holding the stop's cube, ofs_fn_serves: the function's BODY walk takes
 * it), AND that walk takes fn-pair: the FIND slot's pick and the BODY
 * slot's agree, so B-fn never renders another method under PAIR's name
 * (where they would not, B-pair renders the pick). Then fn-pair renders
 * it, the SIMD rows over fn-pair with it (D155: a SIMD-on artifact adds
 * only guarded rungs over the SIMD-off text, so PAIR's SIMD-off text is the
 * function's at every layer). */
static int b_fn_holds(const void *x)
{
    const wf_bx *b = x;
    unsigned eb;
    if (b->pick != FF_PAIR || !legacy_ok(b->d, b->w, &eb) || eb) return 0;
    translate(b->d, b->w, 0, b->fn);
    const mf_pred *p = &b->fn->site.pred;
    int k, lo, hi, two;
    if (p->plan_hint == MF_NO_PRED) return 0;
    ofs_fn_scan(p, &k, &lo, &hi);
    return hi >= 0 && ofs_fn_serves(b->d->art, &b->fn->site, b->def, p, &two) && two;
}
static int b_pair_holds(const void *x)   { return ((const wf_bx *)x)->pick == FF_PAIR; }
static int b_memchr_holds(const void *x)
{
    const wf_bx *b = x;
    return b->pick == FF_LIBC || b->pick == FF_LIBC_BACK;
}
static int b_walk_holds(const void *x)   { return ((const wf_bx *)x)->pick == FF_WALK; }

enum { B_FN, B_PAIR, B_MEMCHR, B_WALK };
static const struct {
    const char *row;
    int (*holds)(const void *x);
    uint8_t     libc;           /* its text calls memchr                     */
    const char *basis;
} wf_brows[] = {
    [B_FN]     = { "B-fn",     b_fn_holds,     1,
                   "PAIR, the plan the offset-skip function's predicate: fn_rows[] BODY "
                   "fn-pair and its PREFIX SIMD rows (vrun) under -fmemfn-simd" },
    [B_PAIR]   = { "B-pair",   b_pair_holds,   1,
                   "PAIR elsewhere (any two bytes, a cube outside a run term included): "
                   "fn-pair's two memchr streams (ofs_pair_text) at the stop's offset" },
    [B_MEMCHR] = { "B-memchr", b_memchr_holds, 1,
                   "LIBC (D1) or LIBC_BACK (D1c): memchr for the stop's byte, a stop below "
                   "the candidate raising C first" },
    [B_WALK]   = { "B-walk",   b_walk_holds,   0,
                   "WALK (R7w, D1w): C advanced while the stop's byte is outside its set "
                   "(C-table or C-own)" },
};
#define WF_NBROWS (sizeof wf_brows / sizeof wf_brows[0])

/* E-FIND's SETUP: Table D, then (D-one) Table B and its renderer, into
 * `fx`. `quiet` 0 is the define's record of the selection E-find made (the
 * walks traced and counted); the setup itself runs quietly, before Table E
 * walks. 0, or -1 out of memory. */
static int wf_find_decide(const mf_art *art, const wf_dec *d, const struct wf_plan *w,
                          const mf_hooks *def, int quiet, wf_fx *fx)
{
    const wf_alt *m = &d->a[d->ch];
    wf_legacy *fn = fx->fn;
    memset(fx, 0, sizeof *fx);
    fx->fn = fn;
    fx->drow = WF_NDROWS;
    fx->bren = WF_NBROWS;
    /* a full-set stop (A-parked's k0 of every byte) is no find: C-bound's
       case, the floor's */
    if (!m->has_stop || w->stop_ix < 0 || full(w->set[w->stop_ix])) return 0;
    const mf_site *s = d->s;
    wf_facts f = { s, m->alt };
    gate_in in = { s, def, NULL, NULL, &f };
    gate_tctx tc = { art, "wfD", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
    gate_verdict why = { 0, 0 };
    wf_dx dx = { d, w, 0, 0, 0 };
    dx.hw = hors_window(d, &dx.wlo, &dx.whi);
    fx->drow = kit_walk(&wf_dtable, 0, &in, MF_PH_DEFINE, 0, &dx, &tc, &why);
    if (fx->drow >= WF_NDROWS) return 0;
    fx->wlo = dx.wlo;
    fx->whi = dx.whi;
    if (!wf_drows[fx->drow].finds) {
        fx->holds = 1;
        return 0;
    }
    fd_stop st = { w->set[w->stop_ix], w->off[w->stop_ix] };
    if (!fd_find(art, s, def, &st, quiet, &fx->pick, &fx->brow)) return 0;
    if (fx->pick == FF_PAIR && !fx->fn) {
        fx->fn = art->a->alloc(art->a->u, sizeof *fx->fn);
        if (!fx->fn) return -1;
    }
    wf_bx bx = { d, w, def, fx->pick, fx->fn };
    for (fx->bren = 0; fx->bren < WF_NBROWS; fx->bren++)
        if (wf_brows[fx->bren].holds(&bx)) break;
    fx->holds = fx->bren < WF_NBROWS;
    return 0;
}

/* E-find's plan from its setup: B (the pick, its row and renderer; B-fn's
 * translated site), the stop's role, C-run's compares (the terms at the
 * define), D-hors's probe and shift table, and the text's libc and include
 * bounds. 0, or -1 out of memory. */
static int wf_find_prepare(const mf_art *art, const wf_dec *d, struct wf_plan *w,
                           const wf_fx *fx, int build)
{
    w->row = &wf_find_arm;
    w->pick = fx->pick;
    w->brow = fx->brow;
    w->bren = (uint8_t)fx->bren;
    w->drow = (uint8_t)fx->drow;
    w->stop_alone = !in_plan(d, d->a[d->ch].stop);
    if (fx->bren == B_FN) {
        w->fsite = &fx->fn->site;
        w->libc = 1;
        w->includes = MF_INC_STRING_H;
        return 0;
    }
    find_groups(d, w);
    if (build && build_runs(art, w)) return -1;
    if (wf_drows[fx->drow].prepare) wf_drows[fx->drow].prepare(w, fx);
    /* memchr where B calls it (no B row: D-hors's probe); a run compare's
       memcmp row and its words' memcpy loads (runcmp.c) */
    w->libc = (uint8_t)((fx->bren < WF_NBROWS && wf_brows[fx->bren].libc) || w->nrun);
    w->includes = w->libc ? MF_INC_STRING_H : 0;
    return 0;
}

/* The room for wf_prepare's refusal: its REPORT text is 176 bytes and its
 * frame text a 34-byte head before gate_describe's description, which
 * truncates to the room left. UNMEASURED DEFAULT: ample, not derived (no
 * shared bound exists; compose.c's own buffers are 200). */
enum { WF_WHY_MAX = 320 };

/* PHASE 2's selection for a window site: the decision, E-find's setup, then
 * Table E (kit.h). */
int wf_prepare(const mf_art *art, const mf_site *s, const mf_hooks *def,
               unsigned gphases, int quiet, const mf_site **legacy,
               const struct wf_plan **plan, const char **path, const char **why)
{
    *legacy = NULL;
    *plan = NULL;
    *path = NULL;
    *why = NULL;
    wf_dec *d = art->a->alloc(art->a->u, sizeof *d);
    struct wf_plan *w = art->a->alloc(art->a->u, sizeof *w);
    char *pid = art->a->alloc(art->a->u, sizeof d->path);
    /* the legacy translation (~5 KB) is the art's too, not a stack local of
       e_legacy_holds (R-28); every translate() rewrites it whole */
    wf_legacy *L = art->a->alloc(art->a->u, sizeof *L);
    wf_fx *fx = art->a->alloc(art->a->u, sizeof *fx);
    if (!d || !w || !pid || !L || !fx) { *why = "out of memory"; return -1; }
    decide(art, s, quiet, d);
    plan_of(d, def, w);
    fx->fn = NULL;
    if (wf_find_decide(art, d, w, def, 1, fx)) { *why = "out of memory"; return -1; }
    wf_facts f = { s, d->a[d->ch].alt };
    gate_in in = { s, def, NULL, NULL, &f };
    gate_tctx tc = { art, "wfE", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
    gate_verdict v = { 0, 0 };
    wf_ex e = { d, w, def, gphases, L, fx };
    size_t r = kit_walk(&wf_etable, 0, &in, gphases, 0, &e, &tc, &v);
    if (r >= WF_NEROWS) {
        /* no row: a REPORT site E-find does not render (E-generic declines
           REPORT), or a frame only a contract leaves with none (a stated
           `moved`, an unstated hook a row uses) */
        char *buf = art->a->alloc(art->a->u, WF_WHY_MAX);
        if (!buf) { *why = "out of memory"; return -1; }
        if (s->site_kind == MF_SK_REPORT && !(v.r1 | v.r2))
            snprintf(buf, WF_WHY_MAX, "no Table E row serves this REPORT site: E-find does "
                     "not render it (denied `" WF_FIND_ID "`, no stop, or no FIND form) and "
                     "the floor serves no REPORT site (the kit manager's R2 ruling)");
        else {
            snprintf(buf, WF_WHY_MAX, "no Table E row serves this frame: ");
            gate_describe(buf + strlen(buf), WF_WHY_MAX - strlen(buf), &v, &in);
        }
        *why = buf;
        return -1;
    }
    /* the define records E-find's selection (Tables D and B, traced) */
    if (r == E_FIND && !quiet && wf_find_decide(art, d, w, def, 0, fx)) {
        *why = "out of memory";
        return -1;
    }
    if (r == E_FIND && wf_find_prepare(art, d, w, fx, !quiet)) {
        *why = "out of memory";
        return -1;
    }
    snprintf(pid, sizeof d->path, "%s%s", d->path,
             r == E_FIND && fx->drow < WF_NDROWS ? wf_drows[fx->drow].path : "");
    *path = pid;
    if (r == E_FIND || r == E_GENERIC) {
        *plan = w;
        return 0;
    }
    unsigned eb;
    legacy_ok(d, w, &eb);
    translate(d, w, eb, L);
    *legacy = &L->site;
    return 0;
}

/* ---- THE PARTS (window_site.md §1.2's pre-check row; the kit manager's wsc3
 * ruling 3: window facts PER PART) ---------------------------------------------
 *
 * A pre-check (ALL_PRESENT) site's FUNC part is a candidate definition of its
 * own: precheck.c renders it as the offset-skip function (FUNC/RETURN, miss
 * `n`), so a part's window facts ride its `mf_pred` and the family decides
 * each part as that FIND site (`wf_part_site`). On every art the part's
 * plan, translated into today's part shape (one RUN term, the stop its scan:
 * E-func's legacy translation), replaces the part's terms; the composite
 * itself stays precheck's. */

/* 1 iff part predicate `p` states window facts. */
static int part_states(const mf_pred *p)
{
    return WF_STATES(p);
}

/* 1 iff a pre-check part of `s` states window facts (kit.h). */
int wf_has_parts(const mf_site *s)
{
    for (unsigned i = 0; s->preds && i < s->npred; i++)
        if (part_states(&s->preds[i])) return 1;
    return 0;
}

/* Part `i` of `s` as the FIND site the family decides (kit.h). */
void wf_part_site(const mf_site *s, unsigned i, mf_site *out)
{
    const mf_pred *p = &s->preds[i];
    memset(out, 0, sizeof *out);
    out->abi = s->abi;
    out->form = MF_FORM_FUNC;
    out->op = MF_OP_FIND;
    out->handoff = MF_H_RETURN;
    out->empty = MF_EMPTY_MISS;
    out->use = MF_USE_POSITION;
    out->body = MF_BODY_ONESHOT;
    out->site_kind = s->site_kind;
    out->policy = s->policy;
    out->denies = s->denies;
    out->opts = s->opts;
    out->ret_pred = MF_NO_PRED;
    out->pred = *p;
    out->pred.nalt = 0;
    out->pred.alts = NULL;
    out->pred.wfloor = 0;
    out->nalt = p->nalt;
    out->alts = p->alts;
    out->wfloor = p->wfloor;
}

/* NULL iff every part's window statement is one the family describes
 * (kit.h). */
const char *wf_parts_check(const mf_site *s)
{
    if (part_states(&s->pred))
        return "`pred` states a part's window facts (mf_pred's `nalt`/`alts`/`wfloor` are a "
               "pre-check FUNC part's; a site states its own on mf_site)";
    for (unsigned i = 0; s->preds && i < s->npred; i++) {
        if (!part_states(&s->preds[i])) continue;
        if (s->op != MF_OP_ALL_PRESENT || !s->preds[i].fn_ref)
            return "a `preds[]` entry states window facts but is no FUNC part (`fn_ref`) of "
                   "an ALL_PRESENT site";
        mf_site ps;
        wf_part_site(s, i, &ps);
        const char *why = wf_check(&ps, 1);
        if (why) return why;
    }
    return NULL;
}

/* `s` with each stating part's plan translated into today's part shape
 * (kit.h). */
int wf_parts_prepare(const mf_art *art, const mf_site *s, const mf_hooks *def, int quiet,
                     const mf_site **out, const char **why)
{
    mf_site *t = art->a->alloc(art->a->u, sizeof *t);
    mf_pred *np = art->a->alloc(art->a->u, s->npred * sizeof *np);
    if (!t || !np) { *why = "out of memory"; return -1; }
    *t = *s;
    memcpy(np, s->preds, s->npred * sizeof *np);
    t->preds = np;
    /* the part's frame: precheck.c calls the offset-skip function, miss `n` */
    mf_hooks hd = def ? *def : (mf_hooks){ 0 };
    if (!hd.miss) hd.miss = MF_MISS_N;
    for (unsigned i = 0; i < s->npred; i++) {
        if (!part_states(&s->preds[i])) continue;
        mf_site ps;
        const mf_site *leg;
        const struct wf_plan *plan;
        const char *pid;
        wf_part_site(s, i, &ps);
        if (wf_prepare(art, &ps, &hd, MF_PH_DEFINE, quiet, &leg, &plan, &pid, why)) return -1;
        if (!leg) {
            *why = "a pre-check part's plan renders through no legacy row (the family's "
                   "floor renders a whole site, never a part)";
            return -1;
        }
        mf_pred *q = &np[i];
        q->nterm = leg->pred.nterm;
        memcpy(q->term, leg->pred.term, sizeof q->term);
        q->need = leg->pred.need;
        q->plan_hint = leg->pred.plan_hint;
        q->plan_pos = leg->pred.plan_pos;
        q->rank_n = leg->pred.rank_n;
        memcpy(q->rank_pos, leg->pred.rank_pos, sizeof q->rank_pos);
        memcpy(q->rank_ppm, leg->pred.rank_ppm, sizeof q->rank_ppm);
        q->nalt = 0;
        q->alts = NULL;
        q->wfloor = 0;
    }
    *out = t;
    return 0;
}

/* ---- THE FLOOR ROW (E-generic; window_site.md §2 "floor: generic") ---------
 *
 * A byte loop over the candidates in [lo, n], each tested at every plan
 * position (the stop's included: the floor has no find). The loop's own
 * condition is the ONE hoisted core bound's upper half (`c + chi < n`, the
 * largest core offset), its first conjunct the lower half (`c >= |clo|`, or
 * `c >= F + |clo|` under an expression floor); a core position is then a
 * plain membership test. Every other position takes the THREE-WAY guard:
 * off the subject it passes, inside [0, F) it is pcrec's edge (the candidate
 * is not covered: the test fails), else membership. A table pcrec offers for
 * a position's set is read through `table_name` (C-table), else the kit's
 * own range test (C-own). The resume is Table D's. Every name is
 * `<prefix>_mf<handle>_*`, as the generic row's. The text is GNU C.
 *
 * THE SHARED PIECES (code review r1 C9): the floor and E-find write the same
 * statement frame (wf_frame: ON_MISS, or ASSIGN with NOP's guard and the
 * on_miss test), the same statement expression's head and tail (wf_open,
 * wf_cand, wf_close) and the same candidate test (wf_test_to: the bound's
 * lower half, then every position, a C-run stretch as one compare). */

typedef struct {
    mf_art               *art;
    const struct wf_plan *w;
    const mf_hooks       *h;
    const char           *S, *N, *LO, *FL, *C, *F, *MISS;
    const char           *Q, *B, *SH;   /* E-find's: the memchr's result, the
                                           probed byte, the shift table      */
    const char           *HA, *HB, *WA, *WB, *E; /* B-pair's two frontiers,
                                           their look-ahead widths and a
                                           look-ahead's end (kit.h ofs_pair) */
    const char           *FN;           /* B-fn's offset-skip function       */
    unsigned              used;     /* PARAM_* the text reads                  */
} wf_rc;

static const char *wf_nm(mf_art *art, uint32_t handle, const char *suffix)
{
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "%s_mf%u%s", art->prefix, handle, suffix);
    return b.p ? b.p : "mf";
}

static void wf_rc_init(wf_rc *rc, mf_art *art, uint32_t handle, const mf_hooks *h)
{
    memset(rc, 0, sizeof *rc);
    rc->art = art;
    rc->w = art->sites[handle - 1].wplan;
    rc->h = h;
    rc->S = wf_nm(art, handle, "_s");
    rc->N = wf_nm(art, handle, "_n");
    rc->LO = wf_nm(art, handle, "_lo");
    rc->FL = wf_nm(art, handle, "_fl");
    rc->C = wf_nm(art, handle, "_c");
    rc->F = wf_nm(art, handle, "_f");
    rc->MISS = wf_nm(art, handle, "_miss");
    rc->Q = wf_nm(art, handle, "_q");
    rc->B = wf_nm(art, handle, "_b");
    rc->SH = wf_nm(art, handle, "_sh");
    rc->HA = wf_nm(art, handle, "_ha");
    rc->HB = wf_nm(art, handle, "_hb");
    rc->WA = wf_nm(art, handle, "_wa");
    rc->WB = wf_nm(art, handle, "_wb");
    rc->E = wf_nm(art, handle, "_e");
    rc->FN = wf_nm(art, handle, "_ofsskip");
}

/* Writes `b`'s text to sink `o`: 0, or -1 (out of memory) recorded. */
static int wf_put(mf_art *art, mf_sink *o, kb *b)
{
    if (b->oom) return kit_fail(art, "window family: out of memory");
    if (b->p) o->puts(o->u, b->p);
    return 0;
}

/* `C + k`, `C - k` or `C`. */
static void wf_at(kb *b, const char *c, int32_t k)
{
    if (k > 0)      kb_printf(b, "%s + %d", c, k);
    else if (k < 0) kb_printf(b, "%s - %d", c, -k);
    else            kb_puts(b, c);
}

/* Position i's membership test of the byte `bx` (C text): C-table or C-own. */
static int wf_member_of(wf_rc *rc, kb *b, unsigned i, const char *bx)
{
    const struct wf_plan *w = rc->w;
    if (w->table[i]) {
        const char *tbl = rc->h && rc->h->table_name
                        ? rc->h->table_name(rc->h->u, w->table[i]) : NULL;
        if (!tbl || !*tbl)
            return kit_fail(rc->art, "window floor: no table name for the offered table %u "
                            "(`table_name`)", w->table[i]);
        kb_printf(b, "%s[%s]", tbl, bx);
        rc->used |= PARAM_S;
        return 0;
    }
    if (kit_set_test(b, w->set[i], bx)) rc->used |= PARAM_S;
    return 0;
}

/* Position i's membership test of its byte, `S[C + off]`. */
static int wf_member(wf_rc *rc, kb *b, unsigned i)
{
    kb byte;
    kb_init(&byte, rc->art->a);
    kb_printf(&byte, "%s[", rc->S);
    wf_at(&byte, rc->C, rc->w->off[i]);
    kb_puts(&byte, "]");
    return wf_member_of(rc, b, i, byte.p ? byte.p : "0");
}

/* THE HOISTED CORE BOUND's upper half, the candidate loop's condition:
 * `C + chi < N` (the largest core offset), or `C <= N` with none >= 0. */
static void wf_bound(const wf_rc *rc, kb *cond)
{
    const struct wf_plan *w = rc->w;
    if (w->ncore && w->chi >= 0) {
        kb_puts(cond, rc->C);
        if (w->chi) kb_printf(cond, " + %d", w->chi);
        kb_printf(cond, " < %s", rc->N);
    } else {
        kb_printf(cond, "%s <= %s", rc->C, rc->N);
    }
}

/* Its lower half, the test's first conjunct where a core offset is < 0
 * (`C >= |clo|`, or `C >= F + |clo|`): 1 iff written. */
static int wf_lower(wf_rc *rc, kb *t)
{
    const struct wf_plan *w = rc->w;
    if (!w->ncore || w->clo >= 0) return 0;
    kb_printf(t, "%s >= ", rc->C);
    if (w->wfloor == MF_WFLOOR_EXPR) { kb_printf(t, "%s + ", rc->FL); rc->used |= PARAM_FL; }
    kb_printf(t, "%d", -w->clo);
    return 1;
}

/* Position i's test at C: a core position by membership (the bound placed
 * it inside the subject), any other by the THREE-WAY guard: off the subject
 * it passes, inside [0, F) it is pcrec's edge (fails), else membership. */
static int wf_pos_test(wf_rc *rc, kb *t, unsigned i)
{
    int32_t d = rc->w->off[i];
    int expr = rc->w->wfloor == MF_WFLOOR_EXPR;
    if (rc->w->core[i]) return wf_member(rc, t, i);
    if (d >= 0) {
        /* off the subject past n passes; [0, F) lies below lo <= c */
        kb_puts(t, "(");
        wf_at(t, rc->C, d);
        kb_printf(t, " >= %s || ", rc->N);
        if (wf_member(rc, t, i)) return -1;
        kb_puts(t, ")");
        return 0;
    }
    kb_printf(t, "(%s < %d || ", rc->C, -d);
    if (expr) {
        kb_printf(t, "(%s >= %s + %d && ", rc->C, rc->FL, -d);
        rc->used |= PARAM_FL;
    }
    if (wf_member(rc, t, i)) return -1;
    kb_puts(t, expr ? "))" : ")");
    return 0;
}

/* THE CANDIDATE TEST at C into `t`: the bound's lower half (where `lower`;
 * E-find raises C past it once, before its loop: wf_raise), then every plan
 * position but the lone index `skip` (-1: none) in ascending offset, a C-run
 * stretch (E-find's `grp`) as ONE run compare at its first position. A run
 * compare is the sink's (runcmp.c writes C-string literals), so where one is
 * met the text so far goes to `o` first and `t` starts again; the floor
 * forms none (its `grp` is -1 throughout) and passes no sink. */
static int wf_test_to(wf_rc *rc, kb *t, mf_sink *o, int skip, int lower)
{
    const struct wf_plan *w = rc->w;
    mf_art *art = rc->art;
    kb_puts(t, "(");
    int first = !(lower && wf_lower(rc, t));
    for (unsigned i = 0; i < w->n; i++) {
        if ((int)i == skip) continue;
        if (w->grp[i] >= 0 && i && w->grp[i - 1] == w->grp[i]) continue;
        if (!first) kb_puts(t, " && ");
        first = 0;
        if (w->grp[i] < 0) {
            if (wf_pos_test(rc, t, i)) return -1;
            continue;
        }
        /* C-run: one compare of the stretch, every position core */
        if (!o) return kit_fail(art, "window family: a run compare with no sink");
        kb base;
        kb_init(&base, art->a);
        kb_printf(&base, "%s + ", rc->S);
        wf_at(&base, rc->C, w->off[i]);
        if (base.oom || wf_put(art, o, t)) return kit_fail(art, "window family: out of memory");
        if (run_cmp_render(art, &w->runs->term[w->grp[i]], base.p, 0, o)) return -1;
        kb_init(t, art->a);
    }
    kb_puts(t, first ? "1)" : ")");
    return 0;
}

/* The floor's test and its loop condition (the bound's upper half). */
static int wf_test(wf_rc *rc, kb *t, kb *cond)
{
    rc->used |= PARAM_N | PARAM_LO;
    wf_bound(rc, cond);
    return wf_test_to(rc, t, NULL, -1, 1);
}

/* The statement expression's head: `({ ` and the hooks as locals, the
 * subject where `s` is read and the floor's F where `fl` is. */
static void wf_open(const wf_rc *rc, kb *e, int s, int fl)
{
    const mf_hooks *h = rc->h;
    kb_puts(e, "({ ");
    if (s) kb_printf(e, "const unsigned char *%s = (const unsigned char *)(%s); ", rc->S, h->s);
    kb_printf(e, "size_t %s = %s; size_t %s = %s; ", rc->N, h->n, rc->LO, h->lo);
    if (fl) kb_printf(e, "size_t %s = %s; ", rc->FL, h->floor);
}

/* The candidate loop's state: the candidate C from LO, the found flag F. */
static void wf_cand(const wf_rc *rc, kb *e)
{
    kb_printf(e, "size_t %s = %s; int %s = 0; ", rc->C, rc->LO, rc->F);
}

/* Its tail: the first candidate or `miss` (`want_value`), else whether one
 * exists. */
static void wf_close(const wf_rc *rc, kb *e, int want_value)
{
    if (want_value) kb_printf(e, "%s ? %s : (%s); })", rc->F, rc->C, kit_miss(rc->h));
    else            kb_printf(e, "%s; })", rc->F);
}

/* The resume both loops share: Table D's D-one, the floor's C + 1. */
static void d_one_next(const wf_rc *rc, kb *b)
{
    kb_printf(b, "%s++", rc->C);
}

/* The floor's search as one statement expression over the hooks. */
static int wf_floor_expr(wf_rc *rc, mf_sink *o, int want_value)
{
    kb t, cond, e;
    kb_init(&t, rc->art->a);
    kb_init(&cond, rc->art->a);
    kb_init(&e, rc->art->a);
    if (wf_test(rc, &t, &cond)) return -1;
    wf_open(rc, &e, rc->used & PARAM_S, rc->used & PARAM_FL);
    wf_cand(rc, &e);
    kb_printf(&e, "for (; %s; ", cond.p);
    d_one_next(rc, &e);
    kb_printf(&e, ") if %s { %s = 1; break; } ", t.p, rc->F);
    wf_close(rc, &e, want_value);
    return wf_put(rc->art, o, &e);
}

/* THE EMPTY RANGE (wf_plan's `hy`): no candidate can hold a verify-YES core
 * position at or past n; with none at offset >= 0, lo > n. */
static void wf_nonempty(const wf_rc *rc, kb *b)
{
    const struct wf_plan *w = rc->w;
    if (!w->hy_set)   kb_printf(b, "(%s) <= (%s)", rc->h->lo, rc->h->n);
    else if (!w->hy)  kb_printf(b, "(%s) < (%s)", rc->h->lo, rc->h->n);
    else              kb_printf(b, "(%s) + %d < (%s)", rc->h->lo, w->hy, rc->h->n);
}

/* Refuses a use missing a hook the family's text reads: `s`, `n`, `lo`, and
 * `floor` under an expression floor. 0, or -1 recorded. */
static int wf_need(mf_art *art, const mf_hooks *h, const site_rec *r)
{
    if (!h || !h->s || !h->n || !h->lo)
        return kit_fail(art, "window floor: a use needs the `s`, `n` and `lo` hooks");
    if (r->site.wfloor == MF_WFLOOR_EXPR && !h->floor)
        return kit_fail(art, "window floor: an expression floor needs the `floor` hook");
    return 0;
}

/* THE STATEMENT FRAME, the floor's and E-find's (`who` names the row in a
 * refusal): ON_MISS, `if ([nonempty && ]!found) { on_miss }`; ASSIGN,
 * `result = value;` then the on_miss test, under NOP's nonempty guard. The
 * search is `expr`'s statement expression. */
static int wf_frame(wf_rc *rc, const mf_site *s, const char *who,
                    int (*expr)(wf_rc *rc, mf_sink *o, int want_value), mf_sink *o)
{
    mf_art *art = rc->art;
    const mf_hooks *h = rc->h;
    const char *ind = h->indent ? h->indent : "";
    int nop = s->empty == MF_EMPTY_NOP;
    kb ne, b;
    kb_init(&ne, art->a);
    kb_init(&b, art->a);
    wf_nonempty(rc, &ne);
    const char *nep = ne.p ? ne.p : "1";
    if (s->handoff == MF_H_ON_MISS) {
        if (!h->on_miss) return kit_fail(art, "%s: ON_MISS needs the `on_miss` hook", who);
        kb_printf(&b, "%sif (%s%s!", ind, nop ? nep : "", nop ? " && " : "");
        if (wf_put(art, o, &b) || expr(rc, o, 0)) return -1;
        kb_init(&b, art->a);
        kb_printf(&b, ") {\n%s    %s\n%s}\n", ind, h->on_miss, ind);
        return wf_put(art, o, &b);
    }
    if (!h->result || !kit_miss(h))
        return kit_fail(art, "%s: ASSIGN needs the `result` and `miss` hooks", who);
    if (nop && h->result_decl)
        return kit_fail(art, "%s: a NOP ASSIGN cannot declare its result", who);
    const char *in = ind;
    if (nop) {
        kb deeper;
        kb_init(&deeper, art->a);
        kb_printf(&b, "%sif (%s) {\n", ind, nep);
        kb_printf(&deeper, "%s    ", ind);
        in = deeper.p ? deeper.p : ind;
    }
    kb_printf(&b, "%s%s%s = ", in, h->result_decl ? h->result_decl : "", h->result);
    if (wf_put(art, o, &b) || expr(rc, o, 1)) return -1;
    kb_init(&b, art->a);
    kb_puts(&b, ";\n");
    if (h->on_miss)
        kb_printf(&b, "%sif (%s == (%s)) {\n%s    %s\n%s}\n", in, h->result, kit_miss(h), in,
                  h->on_miss, in);
    if (nop) kb_printf(&b, "%s}\n", ind);
    return wf_put(art, o, &b);
}

static const char *const wf_param_decl[] = {
    "const unsigned char *%s", "size_t %s", "size_t %s", "size_t %s", "size_t %s",
};

/* The floor's define: on a FUNC site, its `static inline size_t` function
 * (the candidate loop, its parameters the hooks its text reads). */
static int wf_floor_define(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    if (r->site.form != MF_FORM_FUNC) return 0;
    if (!h || !h->fn_name)
        return kit_fail(art, "window floor: a FUNC site needs the fn_name hook");
    const char *fn = h->fn_name(h->u, r->site.pred.fn_ref);
    if (!fn || !*fn)
        return kit_fail(art, "window floor: fn_name gave no name for fn_ref %u",
                        r->site.pred.fn_ref);
    wf_rc rc;
    wf_rc_init(&rc, art, handle, h);
    rc.used = PARAM_MISS;
    kb t, cond, f;
    kb_init(&t, art->a);
    kb_init(&cond, art->a);
    kb_init(&f, art->a);
    if (wf_test(&rc, &t, &cond)) return -1;
    const char *pname[] = { rc.S, rc.N, rc.LO, rc.FL, rc.MISS };
    kb_printf(&f, "static inline size_t %s(", fn);
    int any = 0;
    for (unsigned i = 0; i < 5; i++) {
        if (!(rc.used & (1u << i))) continue;
        if (any) kb_puts(&f, ", ");
        kb_printf(&f, wf_param_decl[i], pname[i]);
        any = 1;
    }
    kb_printf(&f, ")\n{\n    for (size_t %s = %s; %s; ", rc.C, rc.LO, cond.p);
    d_one_next(&rc, &f);
    kb_printf(&f, ")\n        if %s return %s;\n    return %s;\n}\n\n", t.p, rc.C, rc.MISS);
    r->fn = fn;
    r->params = rc.used;
    return kit_flush(art, &f, out, "mf_define");
}

/* The floor's use: its search in the statement frame, or on a FUNC site the
 * call of the function its define wrote. */
static int wf_floor_use(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    if (wf_need(art, h, r)) return -1;
    if (r->site.form != MF_FORM_FUNC) {
        wf_rc rc;
        wf_rc_init(&rc, art, handle, h);
        return wf_frame(&rc, &r->site, "window floor", wf_floor_expr, out);
    }
    kb b;
    kb_init(&b, art->a);
    const char *arg[] = { h->s, h->n, h->lo, h->floor, kit_miss(h) };
    const char *hook[] = { "s", "n", "lo", "floor", "miss" };
    kb_printf(&b, "%s(", r->fn);
    int any = 0;
    for (unsigned i = 0; i < 5; i++) {
        if (!(r->params & (1u << i))) continue;
        if (!arg[i])
            return kit_fail(art, "window floor: the call needs the `%s` hook", hook[i]);
        if (any) kb_puts(&b, ", ");
        kb_printf(&b, i == 0 ? "(const unsigned char *)(%s)" : "(%s)", arg[i]);
        any = 1;
    }
    kb_puts(&b, ")");
    return kit_flush(art, &b, out, "mf_use");
}

/* ---- E-FIND's TEXT (D172 S3; window_site.md §2 phase 2) ---------------------
 *
 * The floor's candidate loop with the stop's FIND at its head, in the
 * floor's STMT frame (wf_frame; E-find's contract is STMT/ASSIGN), its
 * search one statement expression:
 *
 *   ({ S, N, LO[, FL]; size_t C = LO; int F = 0;[ B's state;][ RAISE;]
 *      for (;;) { B; if (!(BOUND)) break; if (TEST) { F = 1; break; } C++; }
 *      F ? C : miss; })
 *
 *   RAISE  where a core offset is < 0: C raised to the bound's lower half
 *          (`|clo|`, or F + |clo| under an expression floor), ONCE: every
 *          resume only moves C forward, so the TEST drops the lower half
 *          and a stop below the candidate reads at or past max(F, 0).
 *
 *   B      the FIND of the stop d*: Table B's pick, by its renderer row
 *          (wf_brows). B-memchr (LIBC, D1; LIBC_BACK, D1c): one `memchr`
 *          for the stop's byte from C + d*, a miss leaving the loop.
 *          B-walk (WALK, R7w or D1w): C advanced while the byte at C + d*
 *          lies inside the subject and outside the stop's set (C-table or
 *          C-own). B-pair (PAIR): fn-pair's two `memchr` streams, one per
 *          byte of the stop's two-member set, each kept as its frontier
 *          (`ha`, `hb`, raised to C + d* once it passes them) and searched
 *          in bounded look-aheads, the lower frontier first (kit.h's
 *          ofs_pair); C becomes the nearer hit less d*, a miss on both
 *          leaving the loop. A stop below the candidate
 *          (d* < 0, a FAILS before-side; never PAIR's) is a core offset, so
 *          RAISE placed C + d* at or past max(F, 0). Each way C becomes the
 *          first candidate at or past C whose stop byte holds.
 *   BOUND  the floor's hoisted core bound, upper half (`C + chi < N`, or
 *          `C <= N` where no core offset is >= 0); the stop is a core
 *          position, so a find past the subject fails it too.
 *   TEST   the floor's test less the stop where C-stop dropped it (B proved
 *          it): wf_test_to, a C-run stretch as ONE run compare (runcmp.c's
 *          rows).
 *   C++    D-one.
 * Under D-HORS (Table D) B is replaced: BOUND first, then the window's last
 * position `hl` probed into `b`; a byte outside its tested set resumes at
 * C + sh[b] at once, and so does a candidate whose TEST fails (TEST less the
 * probed position, which the probe proved). sh[] is a file-scope table the
 * define writes.
 * Under B-FN (PAIR, where the plan IS the offset-skip function's predicate)
 * B, C and D-one are that function's (ofsskip.c: fn-pair's body, and its
 * PREFIX SIMD rows under -fmemfn-simd), defined at file scope as
 * `<prefix>_mf<handle>_ofsskip` (pcrec's FUNC suffix for that function, the
 * one D155's routing rule reads); the expression is its call, `n` read as
 * the miss. Every name is `<prefix>_mf<handle>_*`, as the floor's. */

/* `w`'s index of offset `o`, or -1. */
static int plan_ix(const struct wf_plan *w, int32_t o)
{
    for (unsigned i = 0; i < w->n; i++) if (w->off[i] == o) return (int)i;
    return -1;
}

/* The declaration `const void *Q = P < N ? memchr(S + P, byte, N - P) : 0;`,
 * P = `p` (C + d). */
static void wf_b_search(const wf_rc *rc, kb *b, const char *p, int32_t d, int byte)
{
    kb_printf(b, "const void *%s = %s < %s ? memchr(%s + %s, %d, %s - %s%s%s) : 0; ",
              rc->Q, p, rc->N, rc->S, p, byte, rc->N, d ? "(" : "", p, d ? ")" : "");
}

/* B-memchr (LIBC, LIBC_BACK). */
static int wf_b_memchr(wf_rc *rc, kb *b, const char *p, int32_t d)
{
    const struct wf_plan *w = rc->w;
    int a, x;
    shape(w->set[w->stop_ix], &a, &x);
    kb_puts(b, "{ ");
    wf_b_search(rc, b, p, d, a);
    kb_printf(b, "if (!%s) break; %s = (size_t)((const unsigned char *)%s - %s)",
              rc->Q, rc->C, rc->Q, rc->S);
    if (d > 0)      kb_printf(b, " - %d", d);
    else if (d < 0) kb_printf(b, " + %d", -d);
    kb_puts(b, "; } ");
    rc->art->includes |= MF_INC_STRING_H;
    return mf_art_note_libc(rc->art, "memchr");
}

/* B-walk (WALK). */
static int wf_b_walk(wf_rc *rc, kb *b, const char *p, int32_t d)
{
    (void)d;
    kb_printf(b, "while (%s < %s && !(", p, rc->N);
    if (wf_member(rc, b, (unsigned)rc->w->stop_ix)) return -1;
    kb_printf(b, ")) %s++; ", rc->C);
    return 0;
}

/* B-pair (PAIR): the PAIR leapfrog (ofsskip.c's ofs_pair_text, fn-pair's
 * own text) over the stop's two bytes, on one line of the loop: a search
 * position past the subject leaves first (no candidate's stop lies there),
 * then C is the nearer hit less d*. */
static int wf_b_pair(wf_rc *rc, kb *b, const char *p, int32_t d)
{
    const struct wf_plan *w = rc->w;
    int m[2];
    two(w->set[w->stop_ix], m);
    const ofs_pair t = { rc->S, rc->N, rc->HA, rc->HB, rc->WA, rc->WB, rc->E, rc->Q, rc->C, p,
                         "break", "", "", " " };
    kb_printf(b, "if (%s >= %s) break; ", p, rc->N);
    ofs_pair_text(b, &t, m, d);
    rc->art->includes |= MF_INC_STRING_H;
    return mf_art_note_libc(rc->art, "memchr");
}

/* The loop renderers of Table B's rows, in wf_brows' order (B-fn renders
 * the function instead: wf_find_fn). */
static int (*const wf_b_text[])(wf_rc *rc, kb *b, const char *p, int32_t d) = {
    [B_FN] = NULL, [B_PAIR] = wf_b_pair, [B_MEMCHR] = wf_b_memchr, [B_WALK] = wf_b_walk,
};
_Static_assert(sizeof wf_b_text / sizeof wf_b_text[0] == WF_NBROWS,
               "every Table B renderer row has its text (B-fn's is the function)");

/* B: the stop's FIND by its renderer row. */
static int wf_find_b(wf_rc *rc, kb *b)
{
    const struct wf_plan *w = rc->w;
    int32_t d = w->off[w->stop_ix];
    kb at;
    kb_init(&at, rc->art->a);
    wf_at(&at, rc->C, d);
    return wf_b_text[w->bren](rc, b, at.p ? at.p : rc->C, d);
}

/* RAISE (the header's): C to the bound's lower half, before the loop, where
 * a core offset is < 0. */
static void wf_raise(wf_rc *rc, kb *b)
{
    const struct wf_plan *w = rc->w;
    if (!w->ncore || w->clo >= 0) return;
    if (w->wfloor == MF_WFLOOR_EXPR) {
        kb_printf(b, "if (%s < %s + %d) %s = %s + %d; ", rc->C, rc->FL, -w->clo, rc->C, rc->FL,
                  -w->clo);
        rc->used |= PARAM_FL;
    } else {
        kb_printf(b, "if (%s < %d) %s = %d; ", rc->C, -w->clo, rc->C, -w->clo);
    }
}

/* 1 iff E-find's text reads F (an expression floor's `floor` hook): RAISE
 * (a core offset below the candidate, the stop's included) or a non-core
 * position below it (its edge guard). The stop and the probe are core, so
 * no position the TEST skips reads F. */
static int wf_find_reads_fl(const struct wf_plan *w)
{
    if (w->wfloor != MF_WFLOOR_EXPR) return 0;
    if (w->ncore && w->clo < 0) return 1;
    for (unsigned i = 0; i < w->n; i++)
        if (!w->core[i] && w->off[i] < 0) return 1;
    return 0;
}

/* B-fn's expression: the function's call, its `n` the miss. */
static int wf_find_fn(wf_rc *rc, mf_sink *o)
{
    mf_hooks hh = *rc->h;
    kb b;
    kb_init(&b, rc->art->a);
    wf_open(rc, &b, 1, 0);
    kb_printf(&b, "size_t %s = ", rc->C);
    if (wf_put(rc->art, o, &b)) return -1;
    hh.s = rc->S;
    hh.n = rc->N;
    hh.lo = rc->LO;
    if (ofs_fn_call(rc->art, &hh, &rc->w->fsite->pred, rc->FN, o)) return -1;
    kb_init(&b, rc->art->a);
    kb_printf(&b, "; %s < %s ? %s : (%s); })", rc->C, rc->N, rc->C, kit_miss(rc->h));
    return wf_put(rc->art, o, &b);
}

/* D-hors's loop head: the bound (chi >= hl >= 0: d_hors_holds), then the
 * probe of the window's last position into B, a byte outside its tested
 * set resuming at once; *skip the probed position where the test may drop
 * it (a lone position the probe proved). */
static int d_hors_head(wf_rc *rc, kb *b, const char *bound, int *skip)
{
    const struct wf_plan *w = rc->w;
    int ih = plan_ix(w, w->hl);
    kb_printf(b, "if (!(%s)) break; ", bound);
    kb_printf(b, "unsigned char %s = %s[", rc->B, rc->S);
    wf_at(b, rc->C, w->hl);
    kb_puts(b, "]; ");
    if (ih >= 0) {
        kb_puts(b, "if (!(");
        if (wf_member_of(rc, b, (unsigned)ih, rc->B)) return -1;
        kb_printf(b, ")) { %s += %s[%s]; continue; } ", rc->C, rc->SH, rc->B);
    }
    *skip = ih >= 0 && w->grp[ih] < 0 ? ih : -1;
    return 0;
}

/* D-one's loop head: Table B's find, then the bound; *skip the stop where
 * C-stop dropped it from the test (B proved it). */
static int d_one_head(wf_rc *rc, kb *b, const char *bound, int *skip)
{
    if (wf_find_b(rc, b)) return -1;
    kb_printf(b, "if (!(%s)) break; ", bound);
    *skip = rc->w->stop_alone ? rc->w->stop_ix : -1;
    return 0;
}

/* D-hors's resume: C by the shift of the probed byte. */
static void d_hors_next(const wf_rc *rc, kb *b)
{
    kb_printf(b, "%s += %s[%s]", rc->C, rc->SH, rc->B);
}

/* D-hors's file-scope text: the shift table. */
static int d_hors_define(mf_art *art, const wf_rc *rc, mf_sink *out)
{
    if (out->cmt_open && out->cmt_open(out->u, MF_CMT_NONESSENTIAL)) {
        out->puts(out->u, "The window search's skip table: from a byte at the window's last\n"
                          " * position, the distance to the next candidate that can hold it.");
        if (out->cmt_close) out->cmt_close(out->u);
    }
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "static const unsigned char %s[256] = {", rc->SH);
    for (unsigned x = 0; x < 256; x++) kb_printf(&b, "%s%u", x ? ", " : " ", rc->w->sh[x]);
    kb_puts(&b, " };\n");
    return kit_flush(art, &b, out, "mf_define");
}

/* Table D's TEXT, in wf_drows' order: the loop's head, its resume, and the
 * row's file-scope text (or NULL). */
static const struct {
    int  (*head)(wf_rc *rc, kb *b, const char *bound, int *skip);
    void (*next)(const wf_rc *rc, kb *b);
    int  (*define)(mf_art *art, const wf_rc *rc, mf_sink *out);
} wf_d_text[] = {
    [D_HORS] = { d_hors_head, d_hors_next, d_hors_define },
    [D_ONE]  = { d_one_head,  d_one_next,  NULL },
};
_Static_assert(sizeof wf_d_text / sizeof wf_d_text[0] == WF_NDROWS,
               "every Table D row has its text");

/* E-find's search as one statement expression: the candidate loop with
 * Table D's head (B's find and the bound, or D-hors's probe), the test less
 * the position the head proved, and Table D's resume; B-fn's is the
 * function's call instead (wf_find_fn). Its frame is ASSIGN alone (its
 * contract), so the value is always wanted. */
static int wf_find_expr(wf_rc *rc, mf_sink *o, int want_value)
{
    const struct wf_plan *w = rc->w;
    mf_art *art = rc->art;
    (void)want_value;
    if (w->bren == B_FN) return wf_find_fn(rc, o);
    kb b, bound;
    kb_init(&b, art->a);
    kb_init(&bound, art->a);
    wf_bound(rc, &bound);
    if (bound.oom || !bound.p) return kit_fail(art, WF_FIND_ID ": out of memory");
    wf_open(rc, &b, 1, wf_find_reads_fl(w));
    wf_cand(rc, &b);
    if (w->bren == B_PAIR) {
        const ofs_pair t = { .ha = rc->HA, .hb = rc->HB, .wa = rc->WA, .wb = rc->WB };
        ofs_pair_decl(&b, &t);
        kb_puts(&b, " ");
    }
    wf_raise(rc, &b);
    kb_puts(&b, "for (;;) { ");
    int skip;
    if (wf_d_text[w->drow].head(rc, &b, bound.p, &skip)) return -1;
    kb_puts(&b, "if ");
    if (wf_test_to(rc, &b, o, skip, 0) || wf_put(art, o, &b)) return -1;
    kb_init(&b, art->a);
    kb_printf(&b, " { %s = 1; break; } ", rc->F);
    wf_d_text[w->drow].next(rc, &b);
    kb_puts(&b, "; } ");
    wf_close(rc, &b, 1);
    return wf_put(art, o, &b);
}

/* E-find's define: at file scope, B-fn's function (its run compare's word
 * loads first, as the offset-skip site's), else the run compares' word loads
 * (runcmp.c) and Table D's row's own text (D-hors's shift table). */
static int wf_find_define(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    const struct wf_plan *w = r->wplan;
    if (kit_sink_ok(art, out, WF_FIND_ID)) return -1;
    wf_rc rc;
    wf_rc_init(&rc, art, handle, h);
    if (w->bren == B_FN)
        return run_cmp_prepare(art, &w->fsite->pred, out) ||
               ofs_fn_define_at(art, handle, w->fsite, h, &w->fsite->pred, rc.FN, out) ? -1 : 0;
    if (w->runs->nterm && run_cmp_prepare(art, w->runs, out)) return -1;
    return wf_d_text[w->drow].define ? wf_d_text[w->drow].define(art, &rc, out) : 0;
}

/* E-find's use: its search in the floor's statement frame (wf_frame). */
static int wf_find_use(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    if (wf_need(art, h, r) || kit_sink_ok(art, out, WF_FIND_ID)) return -1;
    wf_rc rc;
    wf_rc_init(&rc, art, handle, h);
    return wf_frame(&rc, &r->site, WF_FIND_ID, wf_find_expr, out);
}

/* The family rows' applicability: every site the family selected them for
 * (Table E chose; their contracts are the gate's). */
static int wf_floor_applies(const mf_site *s, const mf_hooks *def)
{
    (void)s;
    (void)def;
    return 1;
}

/* The form class of the text the family row renders for the plan (kit.h). */
void wf_plan_class(const struct wf_plan *w, mf_class *out)
{
    memset(out, 0, sizeof *out);
    out->v = MF_CLASS_V;
    out->exists = 1;
    /* the libc and include bounds of the text the family row renders for
       this plan (wf_find_prepare; the floor's own compares need neither) */
    out->libc_free = !w->libc;
    out->includes = w->includes;
    memset(out->proven, 0xFF, sizeof out->proven);
    /* R-25: every position the text tests, at every candidate it yields (an
       off-subject position is the core rule's, window_site.md §1.4) */
    for (unsigned i = 0; i < w->n; i++) {
        int32_t d = w->off[i];
        if (d < MF_PROOF_LO || d >= MF_MAX_FWD) continue;
        for (unsigned x = 0; x < 32; x++) out->proven[d - MF_PROOF_LO][x] &= w->set[i][x];
    }
    memcpy(out->proven0, out->proven[0 - MF_PROOF_LO], sizeof out->proven0);
    memcpy(out->proven_prev, out->proven[-1 - MF_PROOF_LO], sizeof out->proven_prev);
}

/* 1 iff the plan's text reads a table pcrec offered (kit.h). */
int wf_plan_reads_table(const struct wf_plan *w)
{
    return w->reads_table;
}

/* E-find's Table B renderer row for the plan, NULL where no B row renders
 * (the floor, or D-hors's probe, which finds no stop). */
const char *wf_plan_brow(const struct wf_plan *w)
{
    return w->row == &wf_find_arm && w->bren < WF_NBROWS ? w->brow : NULL;
}

/* The family row that renders the plan: E-find's arm or the floor's. */
const arm *wf_plan_row(const struct wf_plan *w)
{
    return w->row;
}

/* The floor's contract: what wf_floor_use/define read. It serves every class
 * of every field it does not read; it cannot tell a moved candidate from an
 * unmoved one, so a stated `moved` declines it (the generic row's reading). */
static const gate_use wf_floor_uses[] = {
    { CM(STMT) | CM(FUNC), CM(ASSIGN) | CM(ON_MISS) | CM(RETURN), MF_PH_USE,
      FM(s) | FM(n) | FM(lo), GATE_ALWAYS },
    { CM(STMT), CM(ASSIGN), MF_PH_USE, FM(result) | FM(miss), GATE_ALWAYS },
    { CM(STMT), CM(ON_MISS), MF_PH_USE, FM(on_miss), GATE_ALWAYS },
    { CM(FUNC), CM(RETURN), MF_PH_USE, FM(miss), GATE_ALWAYS },
    { CM(FUNC), MF_ANY, MF_PH_DEFINE, FM(fn_name) | FM(fn_ref), GATE_ALWAYS },
    /* an expression floor's F: the three-way guard and the lower bound */
    { MF_ANY, MF_ANY, MF_PH_USE, FM(floor), GATE_WHEN(CM(W_EXPR), wfloor) },
};
static const gate_contract wf_floor_ct = { "wfE", "E-generic", NU(wf_floor_uses), {
    WF_SERVES_FRAME WF_SERVES_REST WF_SERVES_WINDOW
    [FLD_entry] = MF_ANY, [FLD_core] = MF_ANY,
    [FLD_moved] = 0,                    /* the generic row's reading (PR-2, R2) */
} };

const arm wf_floor_arm = {
    "wf-floor",
    0,
    wf_floor_applies,
    wf_floor_define,
    wf_floor_use,
    &wf_floor_ct,
    NULL,           /* no deny: the family's total fallback (no REPORT site;
                       no byte of a default artifact, wsc6's sweep) */
    1,              /* C-table: an offered table, named by `table_name` */
    0,              /* its compares are its own: no header */
    0,              /* plain loops: no C-library call */
    ARM_TESTS_EVERY,
};

/* E-find's contract: what wf_find_use/define read, in the one frame it
 * renders (STMT/ASSIGN); a stated `moved` declines it as it does the floor
 * (neither can tell a moved candidate from an unmoved one). */
static const gate_use wf_find_uses[] = {
    { CM(STMT), CM(ASSIGN), MF_PH_USE, FM(s) | FM(n) | FM(lo) | FM(result) | FM(miss),
      GATE_ALWAYS },
    { MF_ANY, MF_ANY, MF_PH_USE, FM(floor), GATE_WHEN(CM(W_EXPR), wfloor) },
};
static const gate_contract wf_find_ct = { "wfE", "E-find", NU(wf_find_uses), {
    WF_SERVES_REST WF_SERVES_WINDOW
    [FLD_form] = CM(STMT), [FLD_handoff] = CM(ASSIGN),
    [FLD_entry] = MF_ANY, [FLD_core] = MF_ANY,
    [FLD_moved] = 0,
} };

const arm wf_find_arm = {
    WF_FIND_ID,
    0,
    wf_floor_applies,
    wf_find_define,
    wf_find_use,
    &wf_find_ct,
    WF_FIND_ID,     /* its deny is Table E's row's (wf_erows[E_FIND]) */
    1,              /* C-table: an offered table, named by `table_name` */
    MF_INC_STRING_H,    /* its widest text: memchr (B-memchr, B-pair, B-fn) and a run
                           compare's memcmp/memcpy; a plan's own bounds are its
                           (wf_find_prepare, wf_plan_class) */
    1,              /* likewise: B's memchr, runcmp's memcmp row */
    ARM_TESTS_EVERY,
};

