/* src/gen/lmwalk.c — [LANDWALK] stage 1: the landmark walk's ADMISSION,
 * `lmwalk_conj[]` (docs/dev/lanes/p1dsg3_report.md rev 2 §Admission table,
 * with docs/dev/lanes/p1build_report.md's rev 3 fixes).
 *
 * The LOCATE row `landmark-walk` (src/gen/emit_dfa.c, between `cover` and
 * `composite`) finds each occurrence of a landmark L, a byte class at a
 * top-level concatenation position of a one-branch pattern R = P·L·Q, walks
 * the reverse machine of the cut P·L (ML, `Job.lmdfa`) back from it to the
 * smallest accepting position s*, and runs the anchored machine once there.
 * Sound where P can never consume a byte of L (row `exclusion`): every match
 * then reads, as its L, the first occurrence of L at or after its start, so a
 * start below s* of a match through that occurrence does not exist and a
 * match at a start above it would also match from s* (P·L·Q from s* with the
 * same occurrence). This file decides WHETHER and AT WHICH L; it emits
 * nothing.
 *
 * THE TABLE takes `CompConj`'s field set (id, name, phase, holds, reads),
 * over its own walk state (`LmSt`), `cover_conj[]`'s shape. Every PRE row is
 * walked per CANDIDATE: the choice rule (rev 2 §Selection rule) picks, among
 * the candidates every PRE row admits, the largest landmark margin, then the
 * leftmost; where none passes, the reason is the candidate whose first
 * failing row comes latest (ties leftmost). The POST row `machine` reads ML's
 * build, which the driver makes only where the PRE rows hold
 * (`pcrec_lmwalk_admits`), and is read live by the row's predicate. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "core/internal.h"
#include "core/findings.h"
#include "enc/enc.h"

/* the cost per hit the card prices before a set carries it: `k_hit`, rev 2
 * §Measurement card's intercept, in walked bytes. UNMEASURED default (D149,
 * memory pcrec-suspect-tuning-constants): [LANDWALK-CARD] measures it. */
#define LMWALK_K_HIT_UNMEASURED 10

/* What the rows read as they pass: the compile, the top-level elements, the
 * candidate under test and its prefix facts. */
typedef struct {
    Ctx         *cx;
    PcrecLmwalk *lw;
    Ast        **el;
    int          nel;
    int          at;            /* the candidate's position, -1 for none    */
    uint8_t      set[32];       /* its byte set L                           */
    Ast         *p;             /* the prefix P = el[0..at)                 */
    bool         nfa_done;      /* P's NFA built (g1, exclusion read it)    */
    unsigned     erased;
    uint8_t      alpha[32];     /* the bytes P's NFA can consume            */
    long long    margin;
    const char  *detail;
} LmSt;

static bool lm_has(const uint8_t s[32], int b) { return s[b >> 3] >> (b & 7) & 1; }

/* Flattens R's top-level concatenation into `el` (counted first, `el` NULL). */
static int lm_flatten(Ast *a, Ast **el, int n)
{
    if (a->k == A_CAT) return lm_flatten(a->r, el, lm_flatten(a->l, el, n));
    if (el) el[n] = a;
    return n + 1;
}

/* The left-nested A_CAT over `el[0..n)`: a fresh spine over shared
 * children, so the cut is a tree the NFA builder walks like any other. */
static Ast *lm_cat(Ctx *cx, Ast **el, int n)
{
    Ast *t = el[0];
    for (int i = 1; i < n; i++) {
        Ast *c = pcrec_ast_node(cx, A_CAT);
        c->l = t;
        c->r = el[i];
        t = c;
    }
    return t;
}

/* The most bytes `a` can consume, or -1 for unbounded (a construct the
 * walk's rows decline elsewhere answers -1, the declining direction). */
static long long lm_maxw(const Ast *a)
{
    long long l, r;
    switch (a->k) {
    case A_CLASS:  return 1;
    case A_WCLASS: return a->l ? lm_maxw(a->l) : -1;
    case A_CAT:
        l = lm_maxw(a->l); r = lm_maxw(a->r);
        return l < 0 || r < 0 ? -1 : l + r;
    case A_ALT:
        l = lm_maxw(a->l); r = lm_maxw(a->r);
        return l < 0 || r < 0 ? -1 : l > r ? l : r;
    case A_REP:
        if (a->u.rep.rmax < 0) return -1;
        l = lm_maxw(a->l);
        return l < 0 ? -1 : l * a->u.rep.rmax;
    case A_CAP:
    case A_ATOMIC: return a->l ? lm_maxw(a->l) : 0;
    case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART: case A_KRESET: case A_LOOK:
    case A_CALLOUT:
        return 0;
    case A_BREF: case A_CALL: case A_VAR:
        return -1;
    }
    return -1;
}

/* P's forward NFA (into `Job.lmnfa`, rebuilt per candidate): its erasures
 * and the bytes it can consume. */
static void lm_prefix_nfa(LmSt *st)
{
    Nfa *nfa = &st->cx->job->lmnfa;
    if (st->nfa_done) return;
    pcrec_build_nfa(st->cx, st->p, nfa, false, false);
    st->erased = nfa->erased;
    memset(st->alpha, 0, 32);
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_CLASS)
            for (int k = 0; k < 32; k++) st->alpha[k] |= nfa->st[i].cls[k];
    st->nfa_done = true;
}

/* ---- the conjuncts ---------------------------------------------------- */

/* 1 `finisher-dfa` (r5 SLOT-4): the FINISHER's route is CR_DFA, so a VM
 * hybrid's erased prefilter body (whose language is a superset) never
 * reaches the walk; `cover_conj[]` C1's function. */
static bool lc_finisher(LmSt *st) { return pcrec_cand_finisher_dfa(st->cx); }

/* 2 `anchored-A`: the anchored machine is built, the seed AT's taker
 * (`verify-at`); `-fno-anchored-dfa` and the `drop-anchored` rung decline
 * here. */
static bool lc_anchored(LmSt *st)
{
    return st->cx->job->anchored_ok && st->cx->job->adfa.n > 0;
}

/* 3 `branches`: one top-level branch ([MATCH-SPLIT] / [LANDWALK-ALLACC]
 * own the others). Ahead of `split` (rev 3's order, a deviation from rev 2's
 * row 6 recorded in the report): an alternation has no top-level
 * concatenation, so `split` would name it with the less precise reason. */
static bool lc_branches(LmSt *st) { return st->cx->job->lm_root->k != A_ALT; }

/* 4 `split`: the candidate exists: a byte class at a top-level concatenation
 * position, with a non-empty prefix. */
static bool lc_split(LmSt *st) { return st->at >= 1; }

/* Does `a` hold a node of kind `k` (through every child a walker owns)? */
static bool lm_has_kind(const Ast *a, AKind k)
{
    if (!a) return false;
    if (a->k == k) return true;
    switch (a->k) {
    case A_CAT: case A_ALT: return lm_has_kind(a->l, k) || lm_has_kind(a->r, k);
    case A_REP: case A_CAP: case A_ATOMIC: case A_WCLASS: case A_LOOK:
        return lm_has_kind(a->l, k);
    default: return false;
    }
}

/* 5 `g1`: P is regular-faithful, its NFA records no erasure (an atomic
 * group made transparent, a lookaround made epsilon, a counted repeat
 * collapsed): the reverse machine of P·L then states P exactly. And R reads
 * no position the walk moves: no `\G` (the verify runs from s*, and the
 * relocate moves `search_from`) and no `\K` (the answer's start is s*). */
static bool lc_g1(LmSt *st)
{
    lm_prefix_nfa(st);
    if (lm_has_kind(st->cx->job->lm_root, A_GSTART)) { st->detail = "gstart"; return false; }
    if (lm_has_kind(st->cx->job->lm_root, A_KRESET)) { st->detail = "kreset"; return false; }
    return st->erased == 0;
}

/* 6 `utf8-l0`: under an encoding with non-start bytes, every byte of L is
 * ASCII (a hit is then a character start, and no hit falls inside one). */
static bool lc_utf8(LmSt *st)
{
    const PcrecEnc *enc = pcrec_enc_by_id(st->cx->opt->encoding);
    if (!enc->start_cls) return true;
    for (int b = 0x80; b < 256; b++)
        if (lm_has(st->set, b)) return false;
    return true;
}

/* 7 `exclusion` (D151's strong arm): no byte of L is one P can consume, so
 * a match's L is the first occurrence at or after its start (rust #1354's
 * which-occurrence case is excluded; the arms `factor-free` and
 * `plain-shared` are held, unbuilt). */
static bool lc_exclusion(LmSt *st)
{
    lm_prefix_nfa(st);
    for (int k = 0; k < 32; k++)
        if (st->alpha[k] & st->set[k]) return false;
    return true;
}

/* 8 `next-landmark` (non-goal N2): NEXT's row in the world without the walk
 * (the counterfactual read, `pcrec_cand_lmwalk_next_cf`) does not already
 * start from a landmark: none of the run-pinned, offset-set and handoff rows. */
static const char *const lm_next_declines[] = {
    "run-pinned", "run-pinned-bounded", "offset-set", "offset-set-bounded", "handoff",
};

static bool lc_next(LmSt *st)
{
    PcrecLmwalk *lw = st->lw;
    if (!lw->cf_done) pcrec_cand_lmwalk_next_cf(st->cx, lw);
    for (size_t i = 0; i < sizeof lm_next_declines / sizeof lm_next_declines[0]; i++)
        if (!strcmp(lw->cf_tok, lm_next_declines[i])) {
            st->detail = lm_next_declines[i];
            return false;
        }
    return true;
}

/* 9 `rarity` (r5 SLOT-5): the landmark margin against the counterfactual
 * row's start set, K = ŵ + k_hit, ŵ = min(maxw(P), 1/(1 - mass(alphabet P)))
 * the expected walk. */
static bool lc_rarity(LmSt *st)
{
    Ctx *cx = st->cx;
    PcrecLmwalk *lw = st->lw;
    const uint32_t *rate = pcrec_find_byte_rate(cx);
    uint8_t set[256], alpha[256];
    for (int b = 0; b < 256; b++) {
        set[b] = lm_has(st->set, b);
        alpha[b] = lm_has(st->alpha, b);
    }
    unsigned long long h = pcrec_find_set_mass(rate, set);
    unsigned long long m = lw->cf_has_set ? pcrec_find_set_mass(rate, lw->cf_set) : 1000000u;
    unsigned long long pa = pcrec_find_set_mass(rate, alpha);
    long long w = pa >= 1000000u ? -1 : (long long)((1000000u + (1000000u - pa) - 1) / (1000000u - pa));
    long long mw = lm_maxw(st->p);
    if (w < 0 || (mw >= 0 && mw < w)) w = mw;
    if (w < 0) w = 1000000;   /* unbounded and certain: never admits */
    st->margin = pcrec_landmark_margin(h, m, w + LMWALK_K_HIT_UNMEASURED);
#ifdef PCREC_CAND_TRACE
    if (getenv("PCREC_LMWALK_TRACE"))
        fprintf(stderr, "LMWALK-RARITY\tat=%d\th=%llu\tm=%llu\tpa=%llu\tmaxw=%lld\tw=%lld\tmargin=%lld\n",
                st->at, h, m, pa, mw, w, st->margin);
#endif
    return st->margin > 0;
}

/* 10 `machine` (POST): ML built inside the DFA caps; an overflow is a
 * decline, never a refusal. */
static bool lc_machine(LmSt *st) { return st->cx->job->lm_built; }

typedef struct {
    const char *id;
    const char *name;
    CompPhase   phase;
    bool      (*holds)(LmSt *st);
    const CompRead *reads;
    int         nreads;
} LmConj;

/* the one selection read: NEXT on CAND_ROUTE_DFA, made in the world without
 * the walk (`cand_nodes[LOCATE]`'s `under`/`by`) */
static const CompRead lm_next_read[] = { { CAND_SLOT_NEXT, CAND_ROUTE_DFA } };

/* THE TABLE (rev 2 §Admission table, rev 3 order), read in order per
 * candidate; the first failing row is the `why`. */
static const LmConj lmwalk_conj[] = {
    { "finisher-dfa",  "the finisher's route is the DFA",                    CC_PRE,  lc_finisher,  NULL, 0 },
    { "anchored-A",    "the anchored machine is built (the seed's verify)", CC_PRE,  lc_anchored,  NULL, 0 },
    { "branches",      "one top-level branch",                              CC_PRE,  lc_branches,  NULL, 0 },
    { "split",         "a byte class at a top-level concat position with a non-empty prefix", CC_PRE, lc_split, NULL, 0 },
    { "g1",            "the prefix's NFA records no erasure",               CC_PRE,  lc_g1,        NULL, 0 },
    { "utf8-l0",       "byte encoding, or the landmark is ASCII",           CC_PRE,  lc_utf8,      NULL, 0 },
    { "exclusion",     "the prefix can consume no byte of the landmark",    CC_PRE,  lc_exclusion, NULL, 0 },
    { "next-landmark", "NEXT without the walk does not start from a landmark", CC_PRE, lc_next,    lm_next_read, 1 },
    { "rarity",        "the landmark margin against NEXT's start set is positive", CC_PRE, lc_rarity, lm_next_read, 1 },
    { "machine",       "the reverse machine of the cut fits the DFA caps",  CC_POST, lc_machine,   NULL, 0 },
};
enum { LM_NCONJ = (int)(sizeof lmwalk_conj / sizeof lmwalk_conj[0]) };

bool pcrec_lmwalk_conj_row(int i, const char **id, const char **phase, const char **desc)
{
    if (i < 0 || i >= LM_NCONJ) return false;
    *id = lmwalk_conj[i].id;
    *phase = lmwalk_conj[i].phase == CC_PRE ? "pre" : "post";
    *desc = lmwalk_conj[i].name;
    return true;
}

/* The PRE phase over candidate `at` (-1: none): the index of the first
 * failing row, or LM_NCONJ where every PRE row holds. */
static int lm_walk_pre(LmSt *st, int at)
{
    st->at = at;
    st->nfa_done = false;
    st->detail = NULL;
    st->margin = 0;
    if (at >= 1) {
        pcrec_cls_bits(st->cx, st->el[at], st->set);
        st->p = lm_cat(st->cx, st->el, at);
    }
    for (int i = 0; i < LM_NCONJ; i++) {
        if (lmwalk_conj[i].phase != CC_PRE) continue;
        if (!lmwalk_conj[i].holds(st)) return i;
    }
    return LM_NCONJ;
}

static bool lm_key_holds(const Job *job, const PcrecLmwalk *lw)
{
    return lw->key_ok == job->anchored_ok && lw->key_st == job->adfa.st &&
           lw->key_n == job->adfa.n && lw->key_fin == (int)job->fit.chosen &&
           lw->key_fst == job->dfa.st && lw->key_fn == job->dfa.n &&
           lw->key_ast == job->lm_root;
}

/* Asked before the driver's gate (a LOCATE selection made while the machines
 * are still being built): no decision yet, so the row declines at its POST
 * row, the build it has not seen. Never memoized. */
static const PcrecLmwalk lm_ungated = { .why = "machine" };

const PcrecLmwalk *pcrec_lmwalk(Ctx *cx)
{
    Job *job = cx->job;
    if (!job->lm_root) return &lm_ungated;
    if (job->lmwalk && lm_key_holds(job, job->lmwalk)) return job->lmwalk;
    PcrecLmwalk *lw = pcrec_arena_alloc(&cx->arena, sizeof *lw);
    memset(lw, 0, sizeof *lw);
    lw->key_ok = job->anchored_ok;
    lw->key_st = job->adfa.st;
    lw->key_n = job->adfa.n;
    lw->key_fin = (int)job->fit.chosen;
    lw->key_fst = job->dfa.st;
    lw->key_fn = job->dfa.n;
    lw->key_ast = job->lm_root;
    lw->at = -1;
    job->lmwalk = lw;

    LmSt st;
    memset(&st, 0, sizeof st);
    st.cx = cx;
    st.lw = lw;
    st.nel = lm_flatten(job->lm_root, NULL, 0);
    st.el = pcrec_arena_alloc(&cx->arena, (size_t)st.nel * sizeof *st.el);
    lm_flatten(job->lm_root, st.el, 0);

    /* THE CHOICE RULE: every candidate through the PRE rows; the passing one
     * with the largest margin, then the leftmost; else the latest failure
     * (ties leftmost). */
    int worst = -1, worst_at = -1, ncand = 0;
    const char *worst_detail = NULL;
    for (int at = 1; at < st.nel; at++) {
        if (st.el[at]->k != A_CLASS) continue;
        ncand++;
        int f = lm_walk_pre(&st, at);
        if (f == LM_NCONJ) {
            if (lw->at < 0 || st.margin > lw->margin) {
                lw->at = at;
                lw->margin = st.margin;
                memcpy(lw->set, st.set, 32);
                Ast *pl = pcrec_ast_node(cx, A_CAT);
                pl->l = st.p;
                pl->r = st.el[at];
                lw->pl = pl;
            }
            continue;
        }
        if (f > worst) { worst = f; worst_at = at; worst_detail = st.detail; }
    }
    if (!ncand) {
        worst = lm_walk_pre(&st, -1);
        worst_detail = st.detail;
    }
    (void)worst_at;
    if (lw->at < 0)
        lw->why = worst_detail ? pcrec_sb_fragf(&cx->arena, "%s/%s", lmwalk_conj[worst].id,
                                                worst_detail)
                               : lmwalk_conj[worst].id;
#ifdef PCREC_CAND_TRACE
    /* one record per decision, under its own switch (the CANDTRACE stream is
     * unchanged): the first failing row or the chosen position and margin */
    if (getenv("PCREC_LMWALK_TRACE"))
        fprintf(stderr, "LMWALK\t%s\tat=%d\tmargin=%lld\tnext=%s\n",
                lw->why ? lw->why : "admitted", lw->at, lw->margin,
                lw->cf_done ? lw->cf_tok : "-");
#endif
    return lw;
}

/* THE BUILD GATE (r7 FIX-4): the row's deny is tested FIRST, so under
 * `-fno-landmark-walk` and on every `drop-landmark-walk` retry no row runs
 * (no counterfactual fill, no trace record, no facts mark, no build). The
 * deny's BUILD reader, beside its one SELECTION reader (`cand_select`). */
bool pcrec_lmwalk_admits(Ctx *cx, struct Ast *root)
{
    if (pcrec_opt_has(cx->opt, PCREC_NO_LANDMARK_WALK)) return false;
    cx->job->lm_root = root;
    return pcrec_lmwalk(cx)->why == NULL;
}
