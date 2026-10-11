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
 * the broadcast byte, a movemask; at w32, where the ranking gives a second
 * position KB (below), its compare is ANDed in before the movemask. Each
 * set lane, lowest first, is verified
 * by the BODY's own run compare (runcmp.c, the row the walk picks; [r9 C-12]:
 * the `denies` class reaches it as it reaches the floor) less the positions
 * the mask proved (VERIFY TRIM, below), and the first that verifies is
 * returned: the leftmost candidate >= `pos` whose whole run holds, THE
 * CONTRACT ofsskip.c's header states. Blocks ascend; past the
 * last whole block, ONE overlapped final block ends at `n - T`, its lanes
 * below the next untested candidate masked off.
 *
 * SECOND FILTER POSITION (KB): the kit's reading of pcrec's ranking (D157:
 * `rank_n`/`rank_pos`/`rank_ppm`, the RUN term's positions ordered by
 * pcrec's prior rate, rarest first; request RQ-2). KB is the FIRST ranked
 * position other than KA, and its compare is ANDed with KA's before the
 * movemask (R-1's `ffl`: `vmask(vand(eq_KA, eq_KB))`). No KB (KA alone,
 * R-13's filter) at a level that reads one position (w16, below), or where
 * the ranking states none: rank_n 0 (no facts), or every ranked position is
 * KA (rank_n 1). The ranking's ORDER is the only
 * fact read; its rates are not (a rate threshold would be a tuning constant
 * with no measurement behind it). compose.c's `rank_ok` refuses a ranking
 * that is not distinct positions of the scanned RUN term, so every entry
 * read here is one.
 *   - KA stays the first position: it is the BODY's scanned cube (pcrec's
 *     `plan_pos`), the position R-1's four timed cells all filtered on.
 *     Observed (rq2_report.md §1-2), pcrec's `rank_pos[0]` IS KA on every
 *     PRE and OFS predicate of the corpus, so KB is then `rank_pos[1]`.
 *   - HOW MANY: per level, the level's `npos` (ops_of[]). RULED (D147
 *     addendum 16, Q-R14-1): two at w32, one at w16. MEASURED-UNOFFICIAL
 *     (slot21, dev box zen4, after R-14's trimmed and padded verify): KB at
 *     w16 won throughput 133 / lost 59 against KA alone, while w32's KB
 *     still won 190 / lost 18 (docs/dev/lanes/r14p_report.md). The w16
 *     helper reads KA alone wherever it renders: standalone (vrun-w16) and
 *     as vrun-w32's rung (the w32 helper falls through to it). The pair is
 *     the form R-1 timed (tb_r4b.c `ffl`); three positions have not been
 *     timed. The deny `--memfn=no-vrun-kb` renders KA alone at every level;
 *     the official verdict is the bench's on the target hardware (D144
 *     addendum 4).
 *   - DISTANCE: none required beyond KB != KA (the level, not the distance,
 *     decides whether KB is read). DERIVED for correctness:
 *     every ranked position lies in the run, so KB <= T and its load sits
 *     inside the reach R already derived for KA (below). Whether a FAR KB
 *     beats the rarer near one (adjacent bytes co-occur, so the product of
 *     their rates overstates the pair's rarity; D157 "Revisit when", the
 *     joint rates [OPT-REQPOS] measured) is UNMEASURED and has no variant:
 *     a distance threshold would be a new constant, built when the
 *     DEFAULT-vs-deny reading shows the pair losing to KA alone.
 *   - The answers are exact whichever positions are read: the verify
 *     covers every run position the mask did not (VERIFY TRIM).

 * VERIFY TRIM (request R-14, D147 addendum 15). A set lane has already
 * passed `(s[c + K] & M) == V` at KA, and at KB where the mask reads one:
 * the run compare's own test of those positions, under the same mask. The
 * verify therefore compares only the OTHER positions (runcmp.c's
 * `run_cmp_render_trim`: the row the whole run's walk picks, at its word
 * width, the proven positions and those an earlier word compared made
 * don't-cares, a word left with none not loaded). Where nothing is left
 * (a two-byte run read at both positions, or every other position a
 * don't-care), the lowest set lane IS the answer and the loop returns it
 * with no verify. DERIVED: dropping a position the filter tested under the
 * same mask cannot change an answer. The scalar `__body` is unchanged: its
 * `memchr` stream proves KA's two members only. The deny `no-vrun-trim`
 * verifies the whole run (R-13's and rankuse's verify byte for byte), the
 * arm R-14's re-timing measures the trim against.

 * PADDED VERIFY (R-14 follow-up, Frank 2026-10-11: a verify costs loads and
 * branches, not bytes). The run compare's words never read past the run, so
 * a run of 3 or 5-7 bytes is two overlapping words (two loads, two
 * branches). In the MAIN path it is ONE word of the next width up (4 or 8),
 * masked to 0x00 past the run's end and at the proven positions (runcmp.c's
 * `run_cmp_render_pad`): one load, one branch. Re-comparing a proven byte
 * would cost nothing inside the word, but zeroing it costs nothing either.
 *   - THE MARGIN. A main block at i is taken when i + R + E <= n. Its lane
 *     j's candidate c = i + j has its run end at c + T, so the bytes
 *     readable past the run are n - 1 - (c + T) >= (VW - 1 - j) + E. The
 *     block loop alone (E = 0) leaves lane VW - 1 NO byte past the run: the
 *     loop's `i + R <= n` guarantees bytes ahead of the LOW lanes only. So
 *     the main guard holds E = P - L more (P the padded width, E <= 3:
 *     L 3 -> 1, 5 -> 3, 6 -> 2, 7 -> 1), and the padded compare is given
 *     `over` = E, the bytes the guard guarantees at the top lane.
 *   - THE FINAL BLOCK keeps the trimmed compare. A block the main guard no
 *     longer takes but that still lies inside the subject (n - R - E < i <=
 *     n - R) is final with f = i (nothing masked); then the overlapped
 *     block at n - R as before. Each reads only [pos, n).
 *   - WHERE NOT: the deny `no-vrun-pad` (the text above, byte for byte);
 *     L in {2, 4, 8} (the words form is one word already), L > 8 (one word
 *     does not cover it; a vector verify would, the report's note);
 *     MF_D_RUN_OVERLAP (the walk picks no words-form row); nothing left to
 *     verify. The scalar `__body` is unchanged.

 * OVER-READ / BOUNDARY ARGUMENT (the kit reads only [pos, n)):
 *   - R = VW + T (T = the predicate's highest read, the BODY loop guard's
 *     `maxk`). Below it the entry test falls through, so the vector body
 *     never runs a partial block (§R4.9.3).
 *   - A whole block at i (i + R <= n) loads [i + K, i + K + VW) for K in
 *     {KA, KB} ({KA} at w16): K <= T, so its highest byte is <= i + T + VW - 1 < n; K >=
 *     0 (the term's offset is >= 0, APPLIES) and i starts at pos.
 *   - The final block f = n - R >= pos (the entry test) loads [f + K,
 *     f + K + VW), highest <= n - 1. It is taken when the loop exits with
 *     i + T < n (a candidate is left) and then f < i < f + VW, so the lane
 *     shift i - f is 1..VW - 1 (never the register width: no UB).
 *   - A candidate c is a lane of a block at base b with b + R <= n, so
 *     c + T <= b + VW - 1 + T <= n - 1: the run compare's reads [c + off,
 *     c + T] lie inside the subject. The padded compare's reads end at
 *     c + T + E, and its block has b + R + E <= n (PADDED VERIFY's margin).
 *   - With E > 0 a final block at f = i < n - R (clamped) loads as a whole
 *     block does (i + R <= n), and the lane shift i - f is 0..VW - 1.
 *
 * D149, every constant of the form:
 *   VW         DERIVED: the level's register width (levels.def).
 *   T, R       DERIVED: T the predicate's highest read, R = VW + T, the
 *              smallest span one whole block reads (a correctness bound).
 *   the loop   UNMEASURED DEFAULT: 1x (one block per iteration). The 2x and
 *              4x unrolls and the w16-over-scalar / w32-over-w16 cut-overs
 *              above R are tier-U sweeps owed in RQ-4's slot (§R4.9.5 item
 *              10); until then nothing but the derived R is written.
 *   the trim   DERIVED (VERIFY TRIM above); its word width is the whole
 *              run's, the one helper run_cmp_prepare declared ahead of the
 *              FUNC outside any guard (a narrower helper would need a
 *              declaration the SIMD-off text lacks: the floor rule).
 *   E, P       DERIVED: P the smallest of 4, 8 covering the run, E = P - L
 *              the bytes the padded word reads past it (a correctness bound
 *              on the main guard, PADDED VERIFY); the padded form itself is
 *              DERIVED to cost one load and one branch where the words form
 *              costs two, and its deny `no-vrun-pad` is the arm a re-timing
 *              measures it against.
 *   KB         RULED (D147 addendum 16): two positions at w32 (KB the first
 *              ranked other than KA), one at w16 (the level's `npos`), no
 *              distance rule (SECOND FILTER POSITION above); its deny
 *              `no-vrun-kb` renders KA alone at every level.
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

/* The level's intrinsic spellings and how many filter positions it reads:
 * the only per-level text and choice of the form. `npos` is 1 (KA alone) or
 * 2 (KA and KB); KB at w32 only is D147 addendum 16 (SECOND FILTER POSITION). */
typedef struct {
    const char *type, *set1, *load, *and_, *eq, *mmask;
    int npos;
} vrun_ops;

static const vrun_ops ops_of[MF_NLEVEL] = {
    [LV_X86_W16] = { "__m128i", "_mm_set1_epi8", "_mm_loadu_si128", "_mm_and_si128",
                     "_mm_cmpeq_epi8", "_mm_movemask_epi8",
                     1 /* KA alone, D147 addendum 16 */ },
    [LV_X86_W32] = { "__m256i", "_mm256_set1_epi8", "_mm256_loadu_si256", "_mm256_and_si256",
                     "_mm256_cmpeq_epi8", "_mm256_movemask_epi8",
                     2 /* KA and KB */ },
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

/* KB, the second filter position as a read offset from the candidate (the
 * module comment's SECOND FILTER POSITION): the first ranked position that
 * is not KA, or -1 for none (a level reading KA alone, no ranking, the
 * ranking is KA alone, or its deny `no-vrun-kb`). */
static int vrun_kb(const fn_in *x, const vrun_ops *v)
{
    const mf_pred *p = x->p;
    if (v->npos < 2) return -1;
    if (kit_opt_denied(x->site->opts, "vrun-kb")) return -1;
    for (unsigned i = 0; i < p->rank_n; i++) {
        int k = p->term[0].offset + p->rank_pos[i];
        if (k != x->k) return k;
    }
    return -1;
}

/* One position's compare at `base` (C text): `EQ(AND(LOAD(subject + base
 * + k), m<c>), v<c>)`, the AND elided at an exact position. */
static void cpos(mf_sink *o, const vrun_ops *v, const char *base, int k, int exact, char c)
{
    kit_out(o, "%s(", v->eq);
    if (!exact) kit_out(o, "%s(", v->and_);
    kit_out(o, "%s((const %s *)(subject + %s", v->load, v->type, base);
    if (k) kit_out(o, " + %d", k);
    o->puts(o->u, "))");
    if (!exact) kit_out(o, ", m%c)", c);
    kit_out(o, ", v%c)", c);
}

/* One block's candidate mask at `base` (C text): `(unsigned)MOVEMASK(<KA's
 * compare>)`, or with a KB `(unsigned)MOVEMASK(AND(<KA's>, <KB's>))`. */
static void cmask(mf_sink *o, const vrun_ops *v, const char *base, int ka, int exact_a,
                  int k2, int exact_b)
{
    kit_out(o, "(unsigned)%s(", v->mmask);
    if (k2 >= 0) kit_out(o, "%s(", v->and_);
    cpos(o, v, base, ka, exact_a, 'a');
    if (k2 >= 0) {
        o->puts(o->u, ", ");
        cpos(o, v, base, k2, exact_b, 'b');
        o->puts(o->u, ")");
    }
    o->puts(o->u, ")");
}

/* The broadcast constants of one position (`m<c>` only where masked). */
static void bcast(mf_sink *o, const vrun_ops *v, int mask, int val, char c)
{
    if (mask != 0xFF) kit_out(o, "m%c = %s((char)%d), ", c, v->set1, mask);
    kit_out(o, "v%c = %s((char)%d)", c, v->set1, val);
}

/* The run positions the filter proved, as indices into the run: KA always,
 * KB when the mask reads it; `np` gets their count, 0 under the deny
 * `no-vrun-trim` (the verify is then the whole run, as before R-14). */
static unsigned vrun_proven(const fn_in *x, int k2, int proven[2])
{
    if (kit_opt_denied(x->site->opts, "vrun-trim")) return 0;
    int off = x->p->term[0].offset;
    unsigned np = 0;
    proven[np++] = x->k - off;
    if (k2 >= 0) proven[np++] = k2 - off;
    return np;
}

/* E, the bytes past the run's end the main path's verify reads (PADDED
 * VERIFY, the module comment): the padded compare's need, or 0 where it is
 * not used (its deny `no-vrun-pad`, a run it does not apply to, or nothing
 * left to verify); -1 on a refusal. */
static int vrun_pad(mf_art *art, const fn_in *x, const int *proven, unsigned np)
{
    const mf_term *t = &x->p->term[0];
    if (kit_opt_denied(x->site->opts, "vrun-pad")) return 0;
    if (np && run_cmp_trim_none(t, proven, np)) return 0;
    return run_cmp_pad_over(art, t);
}

/* One block's verify loop behind `ind`: each set lane, lowest first, by the
 * padded compare where `over` is nonzero (the main path's margin, E), else
 * by the run compare less the proven positions; where nothing is left, the
 * lowest set lane is the answer. The compare's RUN_WORDS count is not taken
 * here (the stamp counts unbracketed text only, §R4.9.2.4). */
static int vrun_verify(mf_art *art, const mf_term *t, const int *proven, unsigned np,
                       unsigned over, const char *ind, mf_sink *o)
{
    if (np && run_cmp_trim_none(t, proven, np)) {
        kit_out(o, "%sif (m) return i + (size_t)__builtin_ctz(m);\n", ind);
        return 0;
    }
    kit_out(o, "%swhile (m) {\n"
               "%s    size_t cand = i + (size_t)__builtin_ctz(m);\n"
               "%s    if (", ind, ind, ind);
    long long words = art->words;
    int rc = over ? run_cmp_render_pad(art, t, "subject + cand", t->offset, over, o)
           : np ? run_cmp_render_trim(art, t, "subject + cand", t->offset, proven, np, o)
                : run_cmp_render(art, t, "subject + cand", t->offset, o);
    art->words = words;
    if (rc) return -1;
    kit_out(o, ") return cand;\n"
               "%s    m &= m - 1;\n"
               "%s}\n", ind, ind);
    return 0;
}

/* The helper's body: the entry test, the block loop, the closing brace. Its
 * verify is the BODY's run compare less the positions the mask proved
 * (VERIFY TRIM, the module comment); where the padded compare is used
 * (PADDED VERIFY), the main path verifies by it and holds E more bytes,
 * and the final block verifies by the trimmed compare. */
static int vrun_render(mf_art *art, const mf_hooks *h, const fn_in *x,
                       const mf_formdecl *d, const char *fall, mf_sink *o)
{
    (void)h;
    const mf_level *lv = kit_level(d->level);
    const vrun_ops *v = &ops_of[d->level];
    const mf_term *t = &x->p->term[0];
    int ka = x->k, k2 = vrun_kb(x, v);
    int ma = t->mask ? t->mask[ka - t->offset] : 0xFF, va = t->run[ka - t->offset];
    int mb = k2 < 0 ? 0xFF : t->mask ? t->mask[k2 - t->offset] : 0xFF;
    int vb = k2 < 0 ? 0 : t->run[k2 - t->offset];
    unsigned vw = lv->vw, tt = vrun_t(x->p), r = vw + tt;
    int proven[2];
    unsigned np = vrun_proven(x, k2, proven);
    int e = vrun_pad(art, x, proven, np);
    if (e < 0) return -1;

    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\n", r, fall);
    kit_out(o, "    const %s ", v->type);
    bcast(o, v, ma, va, 'a');
    if (k2 >= 0) {
        o->puts(o->u, ", ");
        bcast(o, v, mb, vb, 'b');
    }
    o->puts(o->u, ";\n");
    if (e && run_cmp_pad_decl(art, t, proven, np, "    ", o)) return -1;
    o->puts(o->u, "    size_t i = pos;\n"
                  "    for (;;) {\n"
                  "        unsigned m;\n");
    kit_out(o,    "        if (i + %u <= n) {\n"
                  "            m = ", r + (unsigned)e);
    cmask(o, v, "i", ka, ma == 0xFF, k2, mb == 0xFF);
    if (e) {
        /* the main path's own verify, then the final block below it: a
           block at i < n - R the main guard no longer takes is final
           (f = i, nothing masked) */
        o->puts(o->u, ";\n");
        if (vrun_verify(art, t, proven, np, (unsigned)e, "            ", o)) return -1;
        kit_out(o, "            i += %u;\n"
                   "            continue;\n"
                   "        }\n"
                   "        if (i + %u >= n) return n;\n"
                   "        size_t f = n - %u;\n"
                   "        if (f > i) f = i;\n"
                   "        m = ", vw, tt, r);
        cmask(o, v, "f", ka, ma == 0xFF, k2, mb == 0xFF);
        o->puts(o->u, " & (~0u << (i - f));\n"
                      "        i = f;\n");
    } else {
        kit_out(o, ";\n"
                      "        } else {\n"
                      "            if (i + %u >= n) return n;\n"
                      "            size_t f = n - %u;\n"
                      "            m = ", tt, r);
        cmask(o, v, "f", ka, ma == 0xFF, k2, mb == 0xFF);
        o->puts(o->u, " & (~0u << (i - f));\n"
                      "            i = f;\n"
                      "        }\n");
    }
    if (vrun_verify(art, t, proven, np, 0, "        ", o)) return -1;
    kit_out(o, "        i += %u;\n"
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
 * byte under MF_D_RUN_OVERLAP, filtered on two masked positions since lane
 * rankuse's KB), is 2,661 bytes at w16 and 2,721 at w32; both rendered,
 * 5,370 (R-13's KA-only filter measured 2,383 / 2,413 / 4,784). Those are
 * the whole-run verify's, `no-vrun-trim`; the trimmed verify (R-14, lane
 * r14b, 2026-10-11) writes 2,583 / 2,643 / 5,214 there, so the bound, the
 * larger of the two arms, did not move. The padded verify (lane r14p) is
 * rendered for runs of 3 or 5-7 bytes only, far below that site's text; G2
 * takes the alone maximum over all four trim x pad arms. Since R-16 (lane
 * r16b, D147 addendum 16) the w16 helper reads KA alone at every arm: its
 * alone maximum is 2,383 again (w32 2,721, unchanged; `vrun@w32+w16` 4,975
 * over G2's space), so the w16 bound is re-pinned to 2,400. */
#define VRUN_W16_GUARDED_MAX 2400
#define VRUN_W32_GUARDED_MAX 2800

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
