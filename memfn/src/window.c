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
 * each with its ENTRY; table offers; the floor; the frame), reachable ONLY on
 * an art previewing "window-family" (mf_preview). Nothing on a default art
 * reaches it, so no emitted byte moves at this commit.
 *
 *   phase 1 (DECISION, no text; mf_wdecide)
 *     A  the STOP per alternative (rows A-empty A-parked A-model A-mass
 *        A-floor), then the choice over alternatives (rows M-one MARGIN
 *        M-parked): one least-cost choice over (alternative, stop)
 *     C  the VERIFY PLAN of the chosen (alternative, stop): steps C-meet,
 *        C-yes / C-model / C-none, C-pin, C-stop, C-run, C-table / C-own,
 *        C-asc
 *   phase 2 (TEXT, in the frame pcrec states; mf_define on the preview art)
 *     B  how the stop is found: the finder's FIND slot (finder.c fd_rows[])
 *        and the offset-skip function's BODY/PREFIX slots (ofsskip.c), reached
 *        through the row E hands the plan to (no parallel table, see E)
 *     D  the resume: D-one, `c + 1` (D-hors lands at S3 with its own deny)
 *     E  the frame: E-func, E-stmt (the plan translated into the site today's
 *        row renders, selected by the composer's walk as ever, so its text is
 *        that row's), E-generic (the family's floor, below)
 *   floor: a byte loop over the plan under the core rule (window_site.md §2
 *   "floor: generic"), with ONE hoisted core bound per candidate and the
 *   THREE-WAY guard outside it.
 *
 * Every table is a `kit_table` on the one walk (kit_walk; Tables A, M, E) or
 * a declared row list read in step order (C, D, TIE); every cost row reads
 * ONE cost table, plan_cost.def. The decision reads no frame fact.
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

const char *wf_check(const mf_site *s, int frame)
{
    if (!s->nalt && !s->alts) {
        if (s->wfloor) return "`wfloor` stated on a site with no alternatives (`alts`)";
        return NULL;
    }
    if (!s->nalt || !s->alts) return "`nalt` and `alts` are stated together";
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

/* F0, the first one-position verify-YES span at offset 0, or -1. */
static int f0_of(const mf_walt *a)
{
    for (unsigned i = 0; i < a->nspan; i++)
        if (a->spans[i].len == 1 && a->spans[i].start == 0 &&
            a->spans[i].verify == MF_VERIFY_YES)
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
 * to the lower). */
static int a_mass_holds(const wf_x *x)
{
    const wf_alt *m = &x->d->a[x->ai];
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (m->p[k].present && m->p[k].core) return 1;
    return 0;
}

static void a_mass_choose(wf_x *x)
{
    wf_alt *m = &x->d->a[x->ai];
    int bk = -1;
    uint32_t bm = 0;
    for (unsigned k = 0; k < WF_NPOS; k++) {
        const wf_pos *p = &m->p[k];
        if (!p->present || !p->core) continue;
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
    [FLD_fold_kind] = MF_ANY, [FLD_stride] = MF_ANY, [FLD_window_stated] = MF_ANY, \
    [FLD_move_back] = MF_ANY, [FLD_overshoot] = MF_ANY, [FLD_decl_point] = MF_ANY, \
    [FLD_body] = MF_ANY, [FLD_prefix_stated] = MF_ANY, [FLD_exact_len] = MF_ANY, \
    [FLD_consumable_len] = MF_ANY, [FLD_ctx] = MF_ANY, [FLD_absent] = MF_ANY, \
    [FLD_consumable] = MF_ANY, [FLD_read_floor] = MF_ANY, [FLD_site_kind] = MF_ANY, \
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
      "no core position: the floor row" },
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
 * or C-yes; C-model or C-none; C-table or C-own). Two rows are applied
 * elsewhere and listed for the order: C-meet by `merge` (Table A reads the
 * meet) and C-table/C-own by `plan_of` (phase 2, where the hooks say whether
 * pcrec names its tables). */

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

/* R's MEMBER (the reply owns it, §2.3 [rev3.2 n4]): over R's EXACT positions
 * (its own set one member), the least mass, ties per the TIE table's stretch
 * row; and the stretch of exact positions around it. */
static void run_member(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    d->run_stated = m->run >= 0;
    if (!d->run_stated) return;
    const mf_wspan *r = &m->alt->spans[m->run];
    int bj = -1;
    uint32_t bm = 0;
    for (unsigned j = 0; j < r->len; j++) {
        if (count(r->set[j]) != 1) continue;
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
    unsigned lo = (unsigned)bj, hi = (unsigned)bj + 1;
    while (lo > 0 && count(r->set[lo - 1]) == 1) lo--;
    while (hi < r->len && count(r->set[hi]) == 1) hi++;
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
        if (m->p[k].present) plan_add(d, (int32_t)k + WF_LO);
}

/* C-yes: every verify-YES position (on a RESEED alternative, F0 at 0). */
static void c_yes(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    for (unsigned k = 0; k < WF_NPOS; k++)
        if (m->p[k].present && m->p[k].yes) plan_add(d, (int32_t)k + WF_LO);
}

/* C-model: A-model's greedy picks (prefix_k's `sel[]`). */
static void c_model(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    for (unsigned i = 0; i < m->npick; i++) plan_add(d, m->pick[i]);
}

static void c_none(wf_dec *d) { (void)d; }

/* C-pin: R becomes ONE compare where it is stated (two or more positions),
 * the stop IS its member, and the plan does not already test all of it
 * (`[code]`: pf_run_applies_common requires the member to EQUAL the scan).
 * On a PARKED alternative the plan then reads R: it re-seeds. */
static void c_pin(wf_dec *d)
{
    const wf_alt *m = chosen(d);
    if (!m->has_stop || !d->run_stated || d->run_len < 2 || m->stop != d->member) return;
    const mf_wspan *r = &m->alt->spans[m->run];
    int all = 1;
    for (unsigned j = 0; j < r->len; j++)
        if (r->start + (int32_t)j != m->stop && !in_plan(d, r->start + (int32_t)j)) all = 0;
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
    { 2, "C-model", c_model_holds, c_model,
      "on a RESEED alternative: plus prefix_k's greedy pick among the walked offsets" },
    { 2, "C-none",  c_none_holds,  c_none,  "otherwise no verify-NO position" },
    { 3, "C-pin",   c_stop_holds,  c_pin,
      "R becomes ONE compare when stated, the stop IS its member and the plan does not "
      "already test all of it; the stretch is the maximal run of exact positions around it" },
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

int wf_active(const mf_art *art)
{
    return art->preview && !strcmp(art->preview, "window-family");
}

const char *wf_preview_step(const char *step)
{
    return step && !strcmp(step, "window-family") ? "window-family" : NULL;
}

int mf_wdecide(const mf_art *art, const mf_site *site, mf_wreply *out)
{
    memset(out, 0, sizeof *out);
    /* the decision reads no frame fact (§0): only the window facts are held */
    if (art->err[0] || !wf_active(art) || site->abi != MF_SITE_ABI || !site->nalt ||
        wf_check(site, 0))
        return -1;
    wf_dec d;
    decide(art, site, 1, &d);
    reply_of(&d, out);
    return 0;
}

/* ---- TABLE D: the resume (window_site.md §2.5) ----------------------------
 *
 * D-one only at commit 1: D-hors moves bytes and lands at S3 with its own
 * deny. The row's `next` is the statement every candidate loop of the family
 * advances by (the floor's; a legacy row's own text resumes at c + 1, as
 * today). */
static const struct { const char *row, *next, *basis; } wf_drows[] = {
    { "D-one", "%s++", "the floor (today's): c + 1" },
};

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
        w->off[i] = offs[i];
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
    for (unsigned k = 0; k < WF_NPOS; k++) {
        const wf_pos *p = &m->p[k];
        int32_t o = (int32_t)k + WF_LO;
        if (p->present && p->yes && p->ycore && o >= 0 && (!w->hy_set || o > w->hy)) {
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
    int32_t t = 0, hp = 0;
    int terms = 0, fulls = 0, neg_only = 1;
    for (unsigned i = 0; i < w->n; i++) {
        if (!w->core[i]) return 0;
        if (full(w->set[i])) {
            if (!fulls || w->off[i] > hp) hp = w->off[i];
            fulls = 1;
            continue;
        }
        if (!terms || w->off[i] > t) t = w->off[i];
        terms = 1;
        if (w->off[i] >= 0) neg_only = 0;
    }
    if (!terms) return 0;
    /* one term per compare at most: bounded by the positions, so a plan of
       more positions than a predicate holds terms stays the floor's */
    unsigned np = 0;
    for (unsigned i = 0; i < w->n; i++) np += !full(w->set[i]);
    if (np > MF_MAX_TERM) return 0;
    *eb = 0;
    if (fulls) {
        /* a full-set position is the range's end only: past every term, at 1 */
        for (unsigned i = 0; i < w->n; i++)
            if (full(w->set[i]) && w->off[i] <= t) return 0;
        if (neg_only || hp > 1) return 0;
        *eb = (unsigned)hp;
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
    /* `consumer` retires at S2 (window_site.md §4); the old row's site states
       it, DERIVED from the kind: the candidate is the answer only on REPORT */
    t->consumer = s->site_kind == MF_SK_REPORT ? MF_C_RESULT : MF_C_ENGINE;
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
    /* span 0's class and window facts (MF_SITE_ABI 11, 18), stated as every
       old builder states them */
    int32_t dmin = p->term[0].offset;
    p->window_stated = 1;
    p->move_back = dmin;
    p->overshoot = 0;
    if (below) {
        p->span_class = MF_SPAN_CONTEXT;
        p->absent = MF_ABSENT_FAILS;            /* every tested position is core */
        p->consumable = MF_CONSUMABLE_NO;
    } else {
        p->span_class = MF_SPAN_BOUNDED;
        p->prefix_stated = MF_PREFIX_STATED;
    }
    for (unsigned k = 0; k < p->nterm; k++)
        if (p->term[k].offset < 0) t->read_floor = MF_FLOOR_SUBJECT;
}

/* ---- TABLE E: the frame (window_site.md §2.6) ------------------------------ */

typedef struct {
    const wf_dec         *d;
    const struct wf_plan *w;
    const mf_hooks       *def;
    unsigned              gphases;
} wf_ex;

/* E-func / E-stmt hold where the plan translates with its own semantics
 * (legacy_ok) AND today's rows serve the translation in this frame (the
 * composer's walk, the finder's routed pick included, asked quietly): a
 * frame today's PF rows never meet (ON_MISS, AT_N, a NOP that does not
 * leave, ...) is E-generic's. REPORT routes at S3 (window_site.md §5.2). */
static int e_legacy_holds(const void *x)
{
    const wf_ex *e = x;
    unsigned eb;
    if (e->d->s->site_kind == MF_SK_REPORT || !legacy_ok(e->d, e->w, &eb)) return 0;
    wf_legacy L;
    translate(e->d, e->w, eb, &L);
    return kit_legacy_serves(e->d->art, &L.site, e->def, e->gphases);
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

/* The floor arm's contract is E-generic's (wf_floor_ct, below). */
static const gate_contract wf_floor_ct;

static int e_true(const void *x)
{
    (void)x;
    return 1;
}

enum { E_FUNC, E_STMT, E_GENERIC };
static const struct {
    int (*holds)(const void *x);
    const gate_contract *ct;
} wf_erows[] = {
    [E_FUNC]    = { e_legacy_holds, &ct_e_func },
    [E_STMT]    = { e_legacy_holds, &ct_e_stmt },
    [E_GENERIC] = { e_true,         &wf_floor_ct },
};
#define WF_NEROWS (sizeof wf_erows / sizeof wf_erows[0])

static const gate_contract *e_ct(size_t i) { return wf_erows[i].ct; }
static int e_holds(size_t i, const void *x) { return wf_erows[i].holds(x); }
static const kit_table wf_etable = { "wfE", WF_NEROWS, e_ct, NULL, NULL, e_holds, NULL };

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
    if (!d || !w || !pid) { *why = "out of memory"; return -1; }
    decide(art, s, quiet, d);
    plan_of(d, def, w);
    memcpy(pid, d->path, sizeof d->path);
    *path = pid;
    wf_facts f = { s, d->a[d->ch].alt };
    gate_in in = { s, def, NULL, NULL, &f };
    gate_tctx tc = { art, "wfE", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
    gate_verdict v = { 0, 0 };
    wf_ex e = { d, w, def, gphases };
    size_t r = kit_walk(&wf_etable, 0, &in, gphases, 0, &e, &tc, &v);
    if (r >= WF_NEROWS) {
        /* E-generic is the table's last row: only its contract can leave a
           frame with none (a stated `moved`, an unstated hook it uses) */
        char *buf = art->a->alloc(art->a->u, 256);
        if (!buf) { *why = "out of memory"; return -1; }
        snprintf(buf, 256, "no Table E row serves this frame: ");
        gate_describe(buf + strlen(buf), 256 - strlen(buf), &v, &in);
        *why = buf;
        return -1;
    }
    if (r == E_GENERIC) {
        *plan = w;
        return 0;
    }
    unsigned eb;
    wf_legacy *L = art->a->alloc(art->a->u, sizeof *L);
    if (!L) { *why = "out of memory"; return -1; }
    legacy_ok(d, w, &eb);
    translate(d, w, eb, L);
    *legacy = &L->site;
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
 * `<prefix>_mf<handle>_*`, as the generic row's. The text is GNU C. */

typedef struct {
    mf_art               *art;
    const struct wf_plan *w;
    const mf_hooks       *h;
    const char           *S, *N, *LO, *FL, *C, *F, *MISS;
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
}

/* `C + k`, `C - k` or `C`. */
static void wf_at(kb *b, const char *c, int32_t k)
{
    if (k > 0)      kb_printf(b, "%s + %d", c, k);
    else if (k < 0) kb_printf(b, "%s - %d", c, -k);
    else            kb_puts(b, c);
}

/* Position i's membership test of its byte: C-table or C-own. */
static int wf_member(wf_rc *rc, kb *b, unsigned i)
{
    const struct wf_plan *w = rc->w;
    kb byte;
    kb_init(&byte, rc->art->a);
    kb_printf(&byte, "%s[", rc->S);
    wf_at(&byte, rc->C, w->off[i]);
    kb_puts(&byte, "]");
    const char *bx = byte.p ? byte.p : "0";
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

/* The candidate test at C: the hoisted bound's lower half, then every
 * position. Writes the loop condition (the bound's upper half) to `cond`. */
static int wf_test(wf_rc *rc, kb *t, kb *cond)
{
    const struct wf_plan *w = rc->w;
    int expr = w->wfloor == MF_WFLOOR_EXPR;
    int first = 1;
    rc->used |= PARAM_N | PARAM_LO;
    if (w->ncore && w->chi >= 0) {
        kb_puts(cond, rc->C);
        if (w->chi) kb_printf(cond, " + %d", w->chi);
        kb_printf(cond, " < %s", rc->N);
    } else {
        kb_printf(cond, "%s <= %s", rc->C, rc->N);
    }
    kb_puts(t, "(");
    if (w->ncore && w->clo < 0) {
        kb_printf(t, "%s >= ", rc->C);
        if (expr) { kb_printf(t, "%s + ", rc->FL); rc->used |= PARAM_FL; }
        kb_printf(t, "%d", -w->clo);
        first = 0;
    }
    for (unsigned i = 0; i < w->n; i++) {
        int32_t d = w->off[i];
        if (!first) kb_puts(t, " && ");
        first = 0;
        if (w->core[i]) {
            if (wf_member(rc, t, i)) return -1;
        } else if (d >= 0) {
            /* off the subject past n passes; [0, F) lies below lo <= c */
            kb_puts(t, "(");
            wf_at(t, rc->C, d);
            kb_printf(t, " >= %s || ", rc->N);
            if (wf_member(rc, t, i)) return -1;
            kb_puts(t, ")");
        } else {
            kb_printf(t, "(%s < %d || ", rc->C, -d);
            if (expr) {
                kb_printf(t, "(%s >= %s + %d && ", rc->C, rc->FL, -d);
                rc->used |= PARAM_FL;
            }
            if (wf_member(rc, t, i)) return -1;
            kb_puts(t, expr ? "))" : ")");
        }
    }
    kb_puts(t, first ? "1)" : ")");
    return 0;
}

/* The search as one statement expression over the hooks: its value the
 * first candidate or `miss` (`want_value`), else whether one exists. */
static int wf_expr(wf_rc *rc, kb *e, int want_value)
{
    const mf_hooks *h = rc->h;
    kb t, cond;
    kb_init(&t, rc->art->a);
    kb_init(&cond, rc->art->a);
    if (wf_test(rc, &t, &cond)) return -1;
    kb_puts(e, "({ ");
    if (rc->used & PARAM_S)
        kb_printf(e, "const unsigned char *%s = (const unsigned char *)(%s); ", rc->S, h->s);
    kb_printf(e, "size_t %s = %s; size_t %s = %s; ", rc->N, h->n, rc->LO, h->lo);
    if (rc->used & PARAM_FL) kb_printf(e, "size_t %s = %s; ", rc->FL, h->floor);
    kb_printf(e, "size_t %s = %s; int %s = 0; for (; %s; ", rc->C, rc->LO, rc->F, cond.p);
    kb_printf(e, wf_drows[0].next, rc->C);
    kb_printf(e, ") if %s { %s = 1; break; } ", t.p, rc->F);
    if (want_value) kb_printf(e, "%s ? %s : (%s); })", rc->F, rc->C, kit_miss(h));
    else            kb_printf(e, "%s; })", rc->F);
    return 0;
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

static int wf_need(mf_art *art, const mf_hooks *h, const site_rec *r)
{
    if (!h || !h->s || !h->n || !h->lo)
        return kit_fail(art, "window floor: a use needs the `s`, `n` and `lo` hooks");
    if (r->site.wfloor == MF_WFLOOR_EXPR && !h->floor)
        return kit_fail(art, "window floor: an expression floor needs the `floor` hook");
    return 0;
}

static int wf_stmt(mf_art *art, uint32_t handle, const mf_hooks *h, kb *b)
{
    site_rec *r = &art->sites[handle - 1];
    const mf_site *s = &r->site;
    wf_rc rc;
    wf_rc_init(&rc, art, handle, h);
    const char *ind = h->indent ? h->indent : "";
    int nop = s->empty == MF_EMPTY_NOP;
    kb ne;
    kb_init(&ne, art->a);
    wf_nonempty(&rc, &ne);
    if (s->handoff == MF_H_ON_MISS) {
        if (!h->on_miss) return kit_fail(art, "window floor: ON_MISS needs the `on_miss` hook");
        kb e;
        kb_init(&e, art->a);
        if (wf_expr(&rc, &e, 0)) return -1;
        kb_printf(b, "%sif (%s%s!%s) {\n%s    %s\n%s}\n", ind, nop ? ne.p : "",
                  nop ? " && " : "", e.p, ind, h->on_miss, ind);
        return 0;
    }
    if (!h->result || !kit_miss(h))
        return kit_fail(art, "window floor: ASSIGN needs the `result` and `miss` hooks");
    if (nop && h->result_decl)
        return kit_fail(art, "window floor: a NOP ASSIGN cannot declare its result");
    const char *in = ind;
    if (nop) {
        kb_printf(b, "%sif (%s) {\n", ind, ne.p);
        kb deeper;
        kb_init(&deeper, art->a);
        kb_printf(&deeper, "%s    ", ind);
        in = deeper.p ? deeper.p : ind;
    }
    kb e;
    kb_init(&e, art->a);
    if (wf_expr(&rc, &e, 1)) return -1;
    kb_printf(b, "%s%s%s = %s;\n", in, h->result_decl ? h->result_decl : "", h->result, e.p);
    if (h->on_miss)
        kb_printf(b, "%sif (%s == (%s)) {\n%s    %s\n%s}\n", in, h->result, kit_miss(h), in,
                  h->on_miss, in);
    if (nop) kb_printf(b, "%s}\n", ind);
    return 0;
}

static const char *const wf_param_decl[] = {
    "const unsigned char *%s", "size_t %s", "size_t %s", "size_t %s", "size_t %s",
};

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
    kb_printf(&f, wf_drows[0].next, rc.C);
    kb_printf(&f, ")\n        if %s return %s;\n    return %s;\n}\n\n", t.p, rc.C, rc.MISS);
    r->fn = fn;
    r->params = rc.used;
    return kit_flush(art, &f, out, "mf_define");
}

static int wf_floor_use(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    if (wf_need(art, h, r)) return -1;
    kb b;
    kb_init(&b, art->a);
    if (r->site.form == MF_FORM_FUNC) {
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
    } else if (wf_stmt(art, handle, h, &b)) {
        return -1;
    }
    return kit_flush(art, &b, out, "mf_use");
}

static int wf_floor_applies(const mf_site *s, const mf_hooks *def)
{
    (void)s;
    (void)def;
    return 1;
}

void wf_floor_class(const struct wf_plan *w, mf_class *out)
{
    memset(out, 0, sizeof *out);
    out->v = MF_CLASS_V;
    out->exists = 1;
    out->libc_free = 1;
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

int wf_plan_reads_table(const struct wf_plan *w)
{
    return w->reads_table;
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
    NULL,           /* no deny: the family's total fallback, reached only on a
                       preview art (no byte of a default artifact) */
    1,              /* C-table: an offered table, named by `table_name` */
    0,              /* its compares are its own: no header */
    0,              /* plain loops: no C-library call */
    ARM_TESTS_EVERY,
};
