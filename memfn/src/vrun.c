/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec docs/design/memfn/probes/twins/tb_r4b.c 631771b7 (`f_ffl`,
 *   the R-1 hand twin of twins.md T-B; pcrec's own text, 0BSD, D145 addendum
 *   1): its block loop, lane mask and overlapped final block, transcribed
 *   to emitted text (memfn/PROVENANCE.md). No third-party text: the vector
 *   operations are the compiler's documented intrinsics (`<emmintrin.h>`,
 *   `<immintrin.h>`), named, not copied.
 *
 * memfn/src/vrun.c — THE FIRST SIMD ROWS, `vrun-w16` and `vrun-w32` (R4e'
 * batch 1, request R-13; docs/design/memfn/integration.md §R4.9.2.4,
 * §R4.9.2.5, §R4.9.3, §R4.9.7). PREFIX rows of ofsskip.c's `fn_rows[]`:
 * each renders ONE guarded per-level helper, `<fn>__w16` / `<fn>__w32`,
 * beside the FUNC's scalar helper `<fn>__body` (D155). The seam writes the
 * guard, the `#include`, the helper's head and the selector; a row writes
 * only its helper's body (this file). SIMD layer: rendered only where pcrec
 * has not set MF_P_PORTABLE_ONLY (`-fmemfn-simd`), each row deniable by its
 * own `--memfn=no-vrun-w16` / `no-vrun-w32` (options.def).
 *
 * THE SITE (APPLIES, §R4.9.2.4's row table). The FUNC's predicate is ONE
 * RUN term of length 2..VRUN_MAX_RUN, at offset >= 0, and it is its site's
 * ONLY predicate (a pre-check composite with one predicate: no lead, no
 * set rest, no whole run; or the offset-skip site's own). OVER: the BODY
 * row the seam chose is `fn-pair` ([r9fu]: the twin R-1 timed; `fn-memchr`
 * is filed with its cells, §R4.9.7.1). REACH: the site's proven span is not
 * shorter than VW + T (walk test 3, §R4.9.3).
 *
 * THE FORM (R-1's `ffl`, without the lead): the candidate filter is the
 * scanned position KA (the predicate's `plan_pos`, the cube `fn-pair`
 * scans), `(s[c + KA] & M) == V` for VW candidates at once: one unaligned
 * load at `i + KA`, an AND with the broadcast mask, a bytewise compare with
 * the broadcast byte, a movemask. Each set lane, lowest first, is verified
 * by the BODY's own run compare (runcmp.c, the row the walk picks; [r9 C-12]:
 * the `denies` class reaches it as it reaches the floor), and the first
 * that verifies is returned: the leftmost candidate >= `pos` whose whole run
 * holds, THE CONTRACT ofsskip.c's header states. Blocks ascend; past the
 * last whole block, ONE overlapped final block ends at `n - T`, its lanes
 * below the next untested candidate masked off.
 *
 * SECOND FILTER POSITION (KB): R-1's form ANDs a second position's compare
 * (D157, amending Q-R9-3 (a): pcrec states the site's candidate positions
 * rarest first with their rates, `rank_n`/`rank_pos`/`rank_ppm`, request
 * RQ-2; the distance rule choosing KB from them is the kit's). RQ-2 is NOT
 * built, so no site states a ranking and the filter is KA alone. The kit
 * picks no KB of its own yet (Q-R9-3's (b)/(c) were rejected): adding it is
 * RQ-2's MF_SITE_ABI bump, a distance rule, and one more `and` in `cmask`
 * below.
 *
 * OVER-READ / BOUNDARY ARGUMENT (the kit reads only [pos, n)):
 *   - R = VW + T (T = the predicate's highest read, the BODY loop guard's
 *     `maxk`). Below it the entry test falls through, so the vector body
 *     never runs a partial block (§R4.9.3).
 *   - A whole block at i (i + R <= n) loads [i + KA, i + KA + VW): KA <= T,
 *     so its highest byte is <= i + T + VW - 1 < n; i starts at pos.
 *   - The final block f = n - R >= pos (the entry test) loads [f + KA,
 *     f + KA + VW), highest <= n - 1. It is taken when the loop exits with
 *     i + T < n (a candidate is left) and then f < i < f + VW, so the lane
 *     shift i - f is 1..VW - 1 (never the register width: no UB).
 *   - A candidate c is a lane of a block at base b with b + R <= n, so
 *     c + T <= b + VW - 1 + T <= n - 1: the run compare's reads [c + off,
 *     c + T] lie inside the subject.
 *
 * D149, every constant of the form:
 *   VW         DERIVED: the level's register width (levels.def).
 *   T, R       DERIVED: T the predicate's highest read, R = VW + T, the
 *              smallest span one whole block reads (a correctness bound).
 *   the loop   UNMEASURED DEFAULT: 1x (one block per iteration). The 2x and
 *              4x unrolls and the w16-over-scalar / w32-over-w16 cut-overs
 *              above R are tier-U sweeps owed in RQ-4's slot (§R4.9.5 item
 *              10); until then nothing but the derived R is written.
 *   VRUN_MAX_RUN  CHOSEN shape bound (32), not a tuning constant: the
 *              guarded text holds one run compare, whose text grows with
 *              the run's length, and Q-R9-9 (RULED (a)) bounds each row's
 *              guarded bytes by a CONSTANT; a longer run is the filed list's.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

#define VRUN_MAX_RUN 32

/* The level's intrinsic spellings: the only per-level text of the form. */
typedef struct {
    const char *type, *set1, *load, *and_, *eq, *mmask;
} vrun_ops;

static const vrun_ops ops_of[MF_NLEVEL] = {
    [LV_X86_W16] = { "__m128i", "_mm_set1_epi8", "_mm_loadu_si128", "_mm_and_si128",
                     "_mm_cmpeq_epi8", "_mm_movemask_epi8" },
    [LV_X86_W32] = { "__m256i", "_mm256_set1_epi8", "_mm256_loadu_si256", "_mm256_and_si256",
                     "_mm256_cmpeq_epi8", "_mm256_movemask_epi8" },
};

/* T: the highest byte offset from the candidate any term reads (ofsskip.c's
 * `maxk`, [r9 C-1]: defined once, the same derivation). */
static uint32_t vrun_t(const mf_pred *p)
{
    int t = 0;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *m = &p->term[i];
        int last = m->offset + (m->kind == MF_T_RUN ? (int)m->run_len : 1) - 1;
        if (last > t) t = last;
    }
    return (uint32_t)t;
}

static uint32_t reach_w16(const mf_site *s, const mf_pred *p)
{
    (void)s;
    return 16 + vrun_t(p);
}

static uint32_t reach_w32(const mf_site *s, const mf_pred *p)
{
    (void)s;
    return 32 + vrun_t(p);
}

/* The site shape both rows take (the module comment's APPLIES). */
static int vrun_applies(const mf_site *s, const mf_pred *p)
{
    if (p->nterm != 1 || p->plan_hint != 0) return 0;
    const mf_term *t = &p->term[0];
    if (t->kind != MF_T_RUN || t->offset < 0 || t->run_len < 2 ||
        t->run_len > VRUN_MAX_RUN)
        return 0;
    if (s->op == MF_OP_ALL_PRESENT) return s->npred == 1 && s->preds == p;
    return s->op == MF_OP_FIND && &s->pred == p;
}

/* One block's candidate mask at `base` (C text): `(unsigned)MOVEMASK(EQ(
 * AND(LOAD(subject + base + KA), ma), va))`, the AND elided at an exact KA. */
static void cmask(mf_sink *o, const vrun_ops *v, const char *base, int ka, int exact)
{
    kit_out(o, "(unsigned)%s(%s(", v->mmask, v->eq);
    if (!exact) kit_out(o, "%s(", v->and_);
    kit_out(o, "%s((const %s *)(subject + %s", v->load, v->type, base);
    if (ka) kit_out(o, " + %d", ka);
    o->puts(o->u, "))");
    if (!exact) o->puts(o->u, ", ma)");
    o->puts(o->u, ", va))");
}

/* The helper's body: the entry test, the block loop, the closing brace. Its
 * verify is the BODY's run compare; the compare's RUN_WORDS count is not
 * taken here (the stamp counts unbracketed text only, §R4.9.2.4). */
static int vrun_render(mf_art *art, const mf_hooks *h, const fn_in *x,
                       const mf_formdecl *d, const char *fall, mf_sink *o)
{
    (void)h;
    const mf_level *lv = kit_level(d->level);
    const vrun_ops *v = &ops_of[d->level];
    const mf_term *t = &x->p->term[0];
    int ka = x->k, mask = t->mask ? t->mask[ka - t->offset] : 0xFF;
    int val = t->run[ka - t->offset], exact = mask == 0xFF;
    unsigned vw = lv->vw, tt = vrun_t(x->p), r = vw + tt;

    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\n", r, fall);
    kit_out(o, "    const %s ", v->type);
    if (!exact) kit_out(o, "ma = %s((char)%d), ", v->set1, mask);
    kit_out(o, "va = %s((char)%d);\n", v->set1, val);
    o->puts(o->u, "    size_t i = pos;\n"
                  "    for (;;) {\n"
                  "        unsigned m;\n");
    kit_out(o,    "        if (i + %u <= n) {\n"
                  "            m = ", r);
    cmask(o, v, "i", ka, exact);
    kit_out(o, ";\n"
                  "        } else {\n"
                  "            if (i + %u >= n) return n;\n"
                  "            size_t f = n - %u;\n"
                  "            m = ", tt, r);
    cmask(o, v, "f", ka, exact);
    o->puts(o->u, " & (~0u << (i - f));\n"
                  "            i = f;\n"
                  "        }\n"
                  "        while (m) {\n"
                  "            size_t cand = i + (size_t)__builtin_ctz(m);\n"
                  "            if (");
    long long words = art->words;
    int rc = run_cmp_render(art, t, "subject + cand", t->offset, o);
    art->words = words;
    if (rc) return -1;
    kit_out(o, ") return cand;\n"
                  "            m &= m - 1;\n"
                  "        }\n"
                  "        i += %u;\n"
                  "    }\n"
                  "}\n", vw);
    return 0;
}

#define VRUN_INSN (MF_I_LOADU | MF_I_AND | MF_I_CMPEQ | MF_I_MOVEMASK | \
                   MF_I_BROADCAST | MF_I_CTZ)

static const char *const vrun_over[] = { "fn-pair", NULL };
static const char *const vrun_w32_rungs[] = { "vrun-w16", NULL };
static const char *const vrun_no_rungs[] = { NULL };

/* MEASURED (G2's SIMD family, memfn/tests/run_g2_simd.py, 2026-10-09, gcc
 * 15.2), each row rendered ALONE (the other denied): the worst case, site 1
 * of g2_simd_gen.c (a 32-byte run of three-digit masks compared byte by
 * byte under MF_D_RUN_OVERLAP), is 2,383 bytes at w16 and 2,413 at w32;
 * both rendered, 4,784. */
#define VRUN_W16_GUARDED_MAX 2400
#define VRUN_W32_GUARDED_MAX 2500

/* guarded_max: the bound on the guarded bytes ONE rendering of the row
 * writes per FUNC (Q-R9-9, D155 item 9): its helper block (the `#if` line,
 * the `#include` line, the helper) and its selector arm (its `#if`/`#elif`
 * line and call) plus the selector's shared `#else`/`#endif` lines, all at
 * the longest FUNC name pcrec writes and a run of VRUN_MAX_RUN masked bytes.
 * MEASURED, not chosen: the maximum over G2's SIMD family (its two
 * constructed worst cases included), rounded UP to the next 100 bytes;
 * tests/memfn/simd_bounds.tsv states the same numbers, G2 holds every
 * rendering of its space to them and `make test-memfn-guarded` every pcrec
 * artifact. */
const mf_formdecl vrun_w16_decl = {
    "vrun-w16", "vrun", LV_X86_W16, vrun_over, vrun_no_rungs, VRUN_INSN,
    reach_w16, VRUN_W16_GUARDED_MAX, vrun_applies, vrun_render,
};

/* vrun-w32 names vrun-w16 as its rung: where both render, the w32 helper
 * falls through to the w16 helper (the ladder w32 -> w16 -> scalar). */
const mf_formdecl vrun_w32_decl = {
    "vrun-w32", "vrun", LV_X86_W32, vrun_over, vrun_w32_rungs, VRUN_INSN,
    reach_w32, VRUN_W32_GUARDED_MAX, vrun_applies, vrun_render,
};

/* ---- the contracts ([MEMFN-ROWCON]; walk test 2) -------------------------
 *
 * A PREFIX row's text is the BODY's function under a level guard: it reads
 * what the BODY reads, so it serves what the BODY serves (it never widens a
 * site's contract, §R4.9.2.3 "Row contracts"), with two differences:
 * `policy`, where it serves only NONE and SIZE (a SIMD row is DECLINED at
 * -fno-memfn-simd, PORTABLE, and on an in-loop site, INLOOP; SIZE is served
 * until R4d's D103 diff rules the SIMD x tune cell, [r9 F-12]), and
 * `table_ref`, NONE only (its one RUN term names no table). */
#define VRUN_SERVES \
    [FLD_form]            = MF_ANY,                   /* the calling arm's */ \
    [FLD_op]              = MF_ANY,                   /* the calling arm's; vrun_applies */ \
    [FLD_handoff]         = MF_ANY,                   /* any handoff (§R4.9.2.4) */ \
    [FLD_reverse]         = CM(NO),                   /* the blocks ascend */ \
    [FLD_empty]           = MF_ANY,                   /* the entry test falls to the body */ \
    [FLD_end_back]        = MF_ANY,                   /* the calling arm's: reads to n */ \
    [FLD_pred]            = MF_ANY,                   /* the walk's input */ \
    [FLD_preds]           = MF_ANY,                   /* the walk's input */ \
    [FLD_ret_pred]        = MF_ANY,                   /* the calling arm's */ \
    [FLD_guard_by_caller] = MF_ANY,                   /* bounds its own reads */ \
    [FLD_on_miss_leaves]  = MF_ANY,                   /* the calling arm's */ \
    [FLD_span_hi]         = MF_ANY,                   /* REACH is the walk's test 3 */ \
    [FLD_denies]          = CM(NONE) | CM(RUN_OVERLAP), /* the verify is the run compare's */ \
    [FLD_fn_ref]          = MF_ANY,                   /* the calling arm names it */ \
    [FLD_table_ref]       = CM(NONE),                 /* one RUN term: no table */ \
    [FLD_s]               = MF_ANY,                   /* its own `subject` */ \
    [FLD_n]               = MF_ANY,                   /* its own `n` */ \
    [FLD_lo]              = MF_ANY,                   /* its own `pos` */ \
    [FLD_floor]           = 0,                        /* reads nothing below `pos` */ \
    [FLD_result]          = MF_ANY,                   /* not read */ \
    [FLD_result_decl]     = MF_ANY,                   /* not read */ \
    [FLD_miss]            = MF_ANY,                   /* returns its `n`, as the body */ \
    [FLD_on_miss]         = MF_ANY,                   /* not read */ \
    [FLD_step]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_more]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_peek]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count]           = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count_start]     = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count_by_caller] = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_on_cand]         = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_on_cand_reach]   = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_member]          = MF_ANY,                   /* not read */ \
    [FLD_table_name]      = MF_ANY,                   /* not read */ \
    [FLD_fn_name]         = MF_ANY,                   /* the calling arm names it */ \
    [FLD_note]            = MF_ANY,                   /* not read */ \
    [FLD_note_tag]        = MF_ANY,                   /* not read */ \
    [FLD_indent]          = MF_ANY,                   /* not read: file scope */ \
    [FLD_comment_tier]    = MF_ANY,                   /* not read: no comment */ \
    [FLD_policy]          = CM(NONE) | CM(SIZE),      /* SIMD layer: never PORTABLE, never INLOOP */

const gate_contract vrun_w16_ct = {
    "fn", "vrun-w16", NULL, 0, {
    VRUN_SERVES
}};

const gate_contract vrun_w32_ct = {
    "fn", "vrun-w32", NULL, 0, {
    VRUN_SERVES
}};

#undef VRUN_SERVES
