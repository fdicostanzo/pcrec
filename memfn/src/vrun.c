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
 * each renders ONE per-level helper, `<fn>__w16` / `<fn>__w32`,
 * beside the FUNC's scalar helper `<fn>__body` (D155). The seam writes the
 * `#include`, the helper's head and the selector; a row writes only its
 * helper's body (this file). SIMD layer: rendered only where the art's
 * stated target admits the row's level (unit U2; `-fmemfn-simd`), each row
 * deniable by its own `--memfn=no-vrun-w16` / `no-vrun-w32` (options.def).
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
static int vrun_applies(const fn_in *x, const mf_formdecl *d)
{
    (void)d;
    const mf_site *s = x->site;
    const mf_pred *p = x->p;
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

/* ---- THE INLINE ONE-MEMBER FINDER (lane mfind) ---------------------------
 *
 * D190's SEARCH piece whose STREAM is MASK ("continue through the current
 * block mask"): a find of ONE byte, every candidate it yields handed to the
 * site's own CHECK in place, a rejected candidate followed by the NEXT SET
 * LANE of the same block mask (clear the lowest, count the trailing zeros):
 * no call per hit, and no scanned byte compared twice (a COST claim: no
 * check counts it; review 2026-11-15 r2 F11). The offset-skip function is
 * its site (fn-memchr's: the scanned position is one byte `a` at offset
 * `k`), its check that function's VERIFY CHAIN (ofsskip.c, every term but
 * the scanned SET), so the answer is fn-memchr's: the leftmost candidate
 * >= `pos` whose every term holds, else `n` (THE CONTRACT, ofsskip.c).
 *
 * ONE RENDERER, mfind_text, for every form; a form is a row of `mfind_lv`:
 *   swar   SIMD-off, portable C: the BODY row `fn-mfind` (`<fn>__body`),
 *          8 lanes per block, a lane one byte of an unsigned long long, its
 *          mask bit the byte's bit 7 (lane shift 3);
 *   w16    SIMD-on, the PREFIX row `mfind-w16` (`<fn>__w16`, levels.def's
 *          LV_X86_W16), vrun's own intrinsic spellings (ops_of): broadcast,
 *          one unaligned load, one compare-equal, one movemask (lane shift 0);
 *   w32    the same at LV_X86_W32 (`mfind-w32`), its rung mfind-w16.
 * Each PREFIX helper falls through (D155) to the next lower rendered rung,
 * else to `<fn>__body`, the SWAR word, on a span too short for one block.
 *
 * THE SWAR MASK IS EXACT. With t = w ^ (0x01..01 * a), the 8 lanes' bytes
 * are 0 exactly where the subject byte is `a`, and
 *     m = ~(((t & 0x7f..7f) + 0x7f..7f) | t) & 0x80..80
 * has bit 7 of byte j set iff t's byte j is 0: (t_j & 0x7f) + 0x7f is at most
 * 0xfe, so NO CARRY leaves a byte, and its bit 7 is set iff t_j's low seven
 * bits are not all 0; OR t_j sets it iff t_j's bit 7 is 1. Every set bit is a
 * real hit, so the stream rejects nothing the mask invented. (The classic
 * (t - 0x01..01) & ~t & 0x80..80 is exact at its LOWEST set bit only: its
 * borrow sets a 0x01 byte above a 0x00 byte, a false lane the MASK stream
 * would hand the check; a one-shot find could use it, this stream cannot.)
 * The word is ONE 8-byte `memcpy` load, put in little-endian lane order
 * (byte j at bits 8j, so lane j is subject byte i + j) by a byte swap under
 * an ordinary `if` on the compiler's predefined `__BYTE_ORDER__`: a
 * constant the compiler folds away, never an `#if` (D155; no CPU fact). A
 * byte-by-byte assembly would need no swap, but gcc 15.2 -O2 does not fold
 * it into one load (measured here: eight byte loads and seven shifts).
 *
 * OVER-READ / BOUNDARY ARGUMENT (reads only [pos, n), by construction):
 *   - D = maxk - k >= 0 (maxk, the largest offset any term reads, is at
 *     least the scanned offset k). A candidate c is valid iff pos <= c and
 *     c + maxk < n (the guard every BODY row keeps), i.e. its scanned byte
 *     b = c + k lies in [pos + k, e), e = n - D. The entry test returns `n`
 *     (the body) or falls through (a helper) at pos + maxk >= n, so below
 *     it e > pos + k and nothing wraps.
 *   - A whole block at i is taken while e - i >= VW: it reads [i, i + VW),
 *     inside [pos + k, e). The body's spans shorter than one word take the
 *     byte loop over [pos + k, e); a helper's take the fall-through (its
 *     entry test: e - (pos + k) < VW).
 *   - The loop leaves with 0 <= e - i < VW. At i == e nothing is left. Else
 *     the FINAL block reads [f, e), f = e - VW >= pos + k (the entry test),
 *     with its lanes below i MASKED OFF: unlike vany's final block, a lane
 *     below i was a candidate of the previous block that the CHECK may have
 *     REJECTED: handing it over again costs a second check (the answer
 *     cannot move: the check is pure, so a re-handed lane is rejected
 *     again; a COST claim, which G2's plant S3153 pins as text, not as a
 *     count). The shift i - f is
 *     1..VW - 1 lanes (never the mask's width: no UB).
 *   - A candidate's check reads [c, c + maxk], c >= pos (offsets >= 0,
 *     ofs_fn_applies) and c + maxk < n: inside the subject.
 *   - Held by G2's one-member family (memfn/tests/run_g2_mfind.py): guard
 *     pages at s + n and below s + pos, every n 0..2 VW + 9, every alignment,
 *     plants that move a bound by one byte must FAULT.
 *
 * D149, every constant of the form:
 *   VW, the lane shift  DERIVED: the word's 8 bytes; the level's register
 *              width (levels.def); the mask's bits per lane.
 *   the masks  DERIVED: the exact zero-byte test above.
 *   the entry cut-over  DERIVED as a correctness bound (a span shorter than
 *              one block); whether the next level down or the byte loop is
 *              faster somewhat above it is UNMEASURED DEFAULT: no other
 *              cut-over is written.
 *   the loop   UNMEASURED DEFAULT: 1x (one block per iteration), unaligned
 *              loads from pos + k with no alignment prologue (vrun's and
 *              vany's shape); unrolls are the card's variants, not built.
 * Its card: memfn/data/cards/kit-grid.tsv ver 6, UNMEASURED; its form ids
 * formhash.c's mfind-swar / mfind-w16 / mfind-w32 (fn-memchr, the libc
 * memchr search and its restart stream on the same site: the BUNDLE
 * comparison, review 2026-11-15 r2 F6). */

/* One form's spellings. `level` LV_* for a SIMD row (its intrinsics are
 * ops_of[level]'s), MF_NLEVEL for the SWAR word. */
typedef struct {
    unsigned    level;
    unsigned    vw;          /* lanes (candidates) per block               */
    unsigned    shift;       /* log2 of a lane's bits in the mask          */
    const char *mtype;       /* the mask's C type                          */
    const char *ctz;         /* its count-trailing-zeros builtin           */
    const char *ones;        /* its all-ones constant                      */
} mfind_lv;

static const mfind_lv mfind_swar = {
    MF_NLEVEL, 8, 3, "unsigned long long", "__builtin_ctzll", "~0ull" };
static const mfind_lv mfind_simd[MF_NLEVEL] = {
    [LV_X86_W16] = { LV_X86_W16, 16, 0, "unsigned", "__builtin_ctz", "~0u" },
    [LV_X86_W32] = { LV_X86_W32, 32, 0, "unsigned", "__builtin_ctz", "~0u" },
};

/* The block's mask at `base` into `m`, `ind` its indent: the SWAR word's
 * exact test (THE SWAR MASK IS EXACT), or the level's one compare. */
static void mfind_mask(mf_sink *o, const mfind_lv *v, const char *ind, const char *base, int a)
{
    if (v->level == MF_NLEVEL) {
        kit_out(o, "%sunsigned long long w;\n"
                   "%smemcpy(&w, subject + %s, 8);\n"
                   "%sif (__BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__) w = __builtin_bswap64(w);\n"
                   "%sw ^= 0x%016llxull;\n"
                   "%sm = ~(((w & 0x7f7f7f7f7f7f7f7full) + 0x7f7f7f7f7f7f7f7full) | w)"
                   " & 0x8080808080808080ull;\n",
                ind, ind, base, ind, ind, 0x0101010101010101ull * (unsigned)a, ind);
        return;
    }
    const vrun_ops *x = &ops_of[v->level];
    kit_out(o, "%sm = (unsigned)%s(%s(%s((const %s *)(subject + %s)), va));\n",
            ind, x->mmask, x->eq, x->load, x->type, base);
}

/* THE TEXT (the module section's form), after the seam's head: the entry
 * test (the body: return `n`, or its short-span byte loop; a helper: fall
 * through to `fall`), the block loop, the final block, the MASK stream
 * handing each set lane to the verify chain, the closing brace. */
static int mfind_text(mf_art *art, const mf_hooks *h, const fn_in *x, const mfind_lv *v,
                      const char *fall, mf_sink *o)
{
    int k = x->k, maxk = x->maxk, d = maxk - k, a = x->a;
    if (k < 0 || d < 0 || a < 0)
        return kit_fail(art, "mfind: the scan is not one byte at an offset the guard covers");
    char at[32], e[32], back[32];
    if (k) snprintf(at, sizeof at, "pos + %d", k);
    else   snprintf(at, sizeof at, "pos");
    if (k) snprintf(back, sizeof back, " - %d", k);
    else   back[0] = '\0';
    if (d) snprintf(e, sizeof e, "n - %d", d);
    else   snprintf(e, sizeof e, "n");
    if (fall) {
        kit_out(o, "    if (pos + %d >= n || %s - %s%s%s < %u)\n    ", maxk, e, k ? "(" : "", at,
                k ? ")" : "", v->vw);
        if (ofs_fn_fall(art, h, x->p, fall, o)) return -1;
    } else {
        kit_out(o, "    if (pos + %d >= n) return n;\n", maxk);
    }
    kit_out(o, "    const size_t e = %s;\n"
               "    size_t i = %s;\n", e, at);
    if (!fall) {
        /* the body's span shorter than one word: the byte loop */
        kit_out(o, "    if (e - i < %u) {\n"
                   "        for (; i < e; i++)\n"
                   "            if (subject[i] == %d) {\n"
                   "                size_t cand = i%s;\n"
                   "                if (", v->vw, a, back);
        if (ofs_verify_chain(art, h, x, o)) return -1;
        o->puts(o->u, ") return cand;\n"
                      "            }\n"
                      "        return n;\n"
                      "    }\n");
    } else {
        const vrun_ops *ops = &ops_of[v->level];
        kit_out(o, "    const %s va = %s((char)%d);\n", ops->type, ops->set1, a);
    }
    kit_out(o, "    for (;;) {\n"
               "        %s m;\n"
               "        if (e - i >= %u) {\n", v->mtype, v->vw);
    mfind_mask(o, v, "            ", "i", a);
    kit_out(o, "        } else {\n"
               "            if (i == e) return n;\n"
               "            const size_t f = e - %u;\n", v->vw);
    mfind_mask(o, v, "            ", "f", a);
    if (v->shift) kit_out(o, "            m &= %s << ((i - f) << %u);\n", v->ones, v->shift);
    else          kit_out(o, "            m &= %s << (i - f);\n", v->ones);
    kit_out(o, "            i = f;\n"
               "        }\n"
               "        while (m) {\n"
               "            size_t cand = i + (size_t)(%s(m)", v->ctz);
    if (v->shift) kit_out(o, " >> %u", v->shift);
    kit_out(o, ")%s;\n", back);
    o->puts(o->u, ""
                  "            if (");
    /* a helper's chain is bracketed text: RUN_WORDS counts no compare in it
       (compose.c's rule, as vrun_verify keeps it; review 2026-11-15 r2 F3) */
    long long words = art->words;
    int rc = ofs_verify_chain(art, h, x, o);
    if (fall) art->words = words;
    if (rc) return -1;
    kit_out(o, ") return cand;\n"
               "            m &= m - 1;\n"
               "        }\n"
               "        i += %u;\n"
               "    }\n", v->vw);
    if (fall) o->puts(o->u, "}\n");
    else      o->puts(o->u, "}\n\n");
    return 0;
}

/* kit.h: the BODY row fn-mfind's text, the SWAR word (writes no libc call,
 * so notes none). */
int mfind_body(mf_art *art, const mf_hooks *h, const fn_in *x, mf_sink *o)
{
    return mfind_text(art, h, x, &mfind_swar, NULL, o);
}

/* A PREFIX row's helper: the level's form, falling through to `fall`. */
static int mfind_render(mf_art *art, const mf_hooks *h, const fn_in *x,
                        const mf_formdecl *d, const char *fall, mf_sink *o)
{
    return mfind_text(art, h, x, &mfind_simd[d->level], fall, o);
}

/* The derived reach (walk test 3): one block of scanned bytes past the
 * guard's maxk (the same correctness bound as vrun's VW + T). */
static uint32_t mfind_reach_w16(const mf_site *s, const mf_pred *p)
{
    (void)s;
    return 16 + vrun_t(p);
}

static uint32_t mfind_reach_w32(const mf_site *s, const mf_pred *p)
{
    (void)s;
    return 32 + vrun_t(p);
}

/* APPLIES: every predicate the BODY row fn-mfind took (OVER says so; the
 * scan is one byte by its predicate), on a FIND or a pre-check part, as
 * the body, whose helper FITS its declared guarded_max (ofs_fn_fits: the
 * verify chain is the body's own, as wide as the predicate, so a wider site
 * declines the row and keeps the body alone; review 2026-11-15 r2 F1). */
static int mfind_applies(const fn_in *x, const mf_formdecl *d)
{
    return ofs_fn_fits(x, d);
}

#define MFIND_INSN (MF_I_LOADU | MF_I_CMPEQ | MF_I_MOVEMASK | MF_I_BROADCAST | MF_I_CTZ)

static const char *const mfind_over[] = { "fn-mfind", NULL };
static const char *const mfind_w32_rungs[] = { "mfind-w16", NULL };

/* guarded_max (Q-R9-9): a BOUND BY CONSTRUCTION, the row's CAP (review
 * 2026-11-15 r2 F1): APPLIES renders the helper into a counting sink
 * (ofs_fn_fits) and declines the row where it would bracket more, so no
 * rendering passes it whatever the predicate (up to MF_MAX_TERM terms) or
 * the names. The values are CHOSEN shape bounds, not tuning constants:
 * they admit every site of G2's one-member family (its alone maximum, 1,299
 * w16 and 1,385 w32 over 44 generator seeds at 160 sites, lane mfind) with
 * headroom; a wider chain (`a.*\x7f[acegikmoqsuwy]{12}`, ~4 KB at w16)
 * keeps the SWAR body alone. Whether a wider helper pays is the card's
 * question, UNMEASURED. tests/memfn/simd_bounds.tsv states the same numbers
 * (pinned equal by tests/memfn/simd_guarded_check.py). */
#define MFIND_W16_GUARDED_MAX 1400
#define MFIND_W32_GUARDED_MAX 1500

const mf_formdecl mfind_w16_decl = {
    "mfind-w16", "mfind", LV_X86_W16, mfind_over, vrun_no_rungs, MFIND_INSN,
    mfind_reach_w16, MFIND_W16_GUARDED_MAX, mfind_applies, mfind_render,
};

const mf_formdecl mfind_w32_decl = {
    "mfind-w32", "mfind", LV_X86_W32, mfind_over, mfind_w32_rungs, MFIND_INSN,
    mfind_reach_w32, MFIND_W32_GUARDED_MAX, mfind_applies, mfind_render,
};

/* ---- the contracts ([MEMFN-ROWCON]; walk test 2) -------------------------
 *
 * A PREFIX row's text is the BODY's function under a level guard: it reads
 * what the BODY reads, so it serves what the BODY serves (it never widens a
 * site's contract, §R4.9.2.3 "Row contracts"), with two differences:
 * `policy`, where it serves only NONE and SIZE (a SIMD row is DECLINED on an
 * in-loop site, INLOOP; SIZE is served until R4d's D103 diff rules the SIMD
 * x tune cell, [r9 F-12]); `target`, which it USES and where it serves only a
 * target admitting its level (unit U2: an art that states no target, and the
 * portable target, render no SIMD row); and `table_ref`, NONE only (its one
 * RUN term names no table). */
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
    MF_SERVES_WINDOW_TODAY \
    [FLD_policy]          = CM(NONE) | CM(SIZE),      /* SIMD layer: never INLOOP */

/* Each row USES the art's target (unit U2): an art that states none
 * declines it (rule 1), and it serves every target but one that does not
 * admit its level (fields.def's NO_<level>). */
static const gate_use vrun_uses[] = {
    { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(target), GATE_ALWAYS },
};

const gate_contract vrun_w16_ct = {
    "fn", "vrun-w16", vrun_uses, 1, {
    VRUN_SERVES
    [FLD_table_ref]       = CM(NONE),                 /* one RUN term: no table */
    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W16),  /* a target admitting w16 */
}};

const gate_contract vrun_w32_ct = {
    "fn", "vrun-w32", vrun_uses, 1, {
    VRUN_SERVES
    [FLD_table_ref]       = CM(NONE),                 /* one RUN term: no table */
    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W32),  /* a target admitting w32 */
}};

/* The one-member finder's rows: vrun's contract, but the verify chain is
 * the BODY's (ofsskip.c verify_chain), so a multi-byte SET term reads
 * pcrec's table as the body does. */
const gate_contract mfind_w16_ct = {
    "fn", "mfind-w16", vrun_uses, 1, {
    VRUN_SERVES
    [FLD_table_ref]       = CM(NONE) | CM(REF),       /* ofs_verify_chain: a set's table */
    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W16),  /* admits w16 */
}};

const gate_contract mfind_w32_ct = {
    "fn", "mfind-w32", vrun_uses, 1, {
    VRUN_SERVES
    [FLD_table_ref]       = CM(NONE) | CM(REF),       /* ofs_verify_chain: a set's table */
    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W32),  /* admits w32 */
}};

#undef VRUN_SERVES
