/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md). The block loop and the overlapped final block
 *   follow vrun.c's (pcrec's own, D145 addendum 1); the compare-each-byte-
 *   and-OR idea is the textbook one (Rust memchr's memchr2/memchr3 among
 *   others: an idea, no text taken). The vector operations are the
 *   compiler's documented intrinsics, named, not copied.
 *
 * memfn/src/vany.c — A STANDALONE SIMD-LAYER KERNEL: "find the first
 * position in [pos, n) whose byte is any of K arbitrary bytes", K 2..3
 * (lane simdset, Frank's go to the kit 2026-10-29, step 2; it generalizes
 * plan row [MEMFN-PAIRSIMD], the arbitrary-pair two-compares-and-OR form,
 * which is the K = 2 case). K1's F2 (`mf_ref_find_any2/3`) states what it
 * answers.
 *
 * NOT ROUTED. No mf_site row, no fn_rows[]/fd_rows[] entry, no options.def
 * row: no pcrec site can reach it, so no pcrec byte moves and no deny exists
 * (a deny only where a caller can be slower). Its one entry is the
 * stand-alone product's `mf_kernel_find_any` (memfn.h), which the kit's G2
 * family `memfn/tests/run_g2_any.py` and, later, the measurement script
 * call. How a priced choice later offers it is an open question
 * (docs/dev/lanes/simdset_report.md), not decided by this file.
 *
 * THE TEXT, in the seam's shape (ofsskip.c, D155) so a later routing can
 * reuse it: `<fn>__body`, the scalar byte loop; one guarded helper
 * `<fn>__<stamp>` per requested level, ascending, each falling through to
 * the next lower rendered helper (else `__body`) on a span too short for
 * one block; then the selector `<fn>`, whose whole body is the `#if` chain,
 * top level first, `#else` the body. Every function is
 * `static inline size_t f(const unsigned char *subject, size_t n, size_t pos)`
 * and returns the least i in [pos, n) with subject[i] a member, else n.
 *
 * THE FORM, per level of register width VW: broadcast each DISTINCT member
 * once; per block, one unaligned load, one compare-equal per member, ORed,
 * one movemask; the lowest set lane is the answer. Blocks ascend from pos;
 * past the last whole block, ONE overlapped final block at n - VW. Its
 * lanes below the first unscanned position need no mask: they lie inside
 * the last whole block, which held no member (DERIVED, below).
 *
 * OVER-READ / BOUNDARY ARGUMENT (every function reads only [pos, n)):
 *   - The body reads subject[i] for pos <= i < n only.
 *   - A helper's entry test sends `pos >= n` and `n - pos < VW` to the
 *     fall-through, so below it n - pos >= VW and at least one whole block
 *     runs.
 *   - A whole block at i is taken while n - i >= VW (i <= n holds
 *     throughout, so the subtraction cannot wrap): it reads [i, i + VW),
 *     inside [pos, n) since i >= pos.
 *   - The loop exits with 0 <= n - i < VW. If i == n nothing is left. Else
 *     the final block reads [f, n), f = n - VW; f >= pos by the entry test.
 *     The previous whole block was [i - VW, i), and f >= i - VW, so the
 *     final block's lanes below i (j < i - f) lie in that block, which held
 *     no member: its lowest set lane is >= i, so it needs no mask.
 *   - Nothing is read at or past n, nothing below pos, on any path; the
 *     tail is never a partial vector load and there is no scalar tail loop
 *     at a level (spans shorter than VW go to the next level down).
 *   - Held by G2 (run_g2_any.py): guard pages at s + n and below s + pos,
 *     every length 0..2 VW + 9, every alignment, and plants that move each
 *     bound by one byte must FAULT.
 *
 * D149, every constant of the form:
 *   VW         DERIVED: the level's register width (levels.def).
 *   the entry cut-over (n - pos < VW -> the next level down)  DERIVED as a
 *              correctness bound: the smallest span one block reads. Whether
 *              the next level down or the body is faster somewhat above VW
 *              is UNMEASURED DEFAULT: no other cut-over is written.
 *   the loop   UNMEASURED DEFAULT: 1x (one block per iteration), unaligned
 *              loads from pos with no alignment prologue. A 2x/4x unroll
 *              (Rust memchr reads 4 vectors per iteration on long spans) and
 *              an aligned main loop are variants for the measurement card's
 *              first run, not built.
 *   K          CHOSEN shape bound (VANY_MAX_K 3): the charter's 2..3. A K
 *              past 3 is the set-find's territory (terms.c, the finder),
 *              where a compare per member stops being the obvious form.
 *   duplicates DERIVED: a repeated member is compared once (OR is
 *              idempotent), so `bytes` {a, a} renders a one-compare kernel.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

#define VANY_MAX_K 3

/* The level's intrinsic spellings: the only per-level text of the form. A
 * level levels.def gains without a row here is refused, never rendered. */
typedef struct {
    const char *type, *set1, *load, *or_, *eq, *mmask;
} vany_ops;

static const vany_ops ops_of[MF_NLEVEL] = {
    [LV_X86_W16] = { "__m128i", "_mm_set1_epi8", "_mm_loadu_si128", "_mm_or_si128",
                     "_mm_cmpeq_epi8", "_mm_movemask_epi8" },
    [LV_X86_W32] = { "__m256i", "_mm256_set1_epi8", "_mm256_loadu_si256", "_mm256_or_si256",
                     "_mm256_cmpeq_epi8", "_mm256_movemask_epi8" },
};

/* Writes a refusal into err[0..errn) and returns -1. */
static int vany_refuse(char *err, size_t errn, const char *fmt, ...)
    __attribute__((format(printf, 3, 4)));
static int vany_refuse(char *err, size_t errn, const char *fmt, ...)
{
    if (err && errn) {
        va_list ap;
        va_start(ap, fmt);
        vsnprintf(err, errn, fmt, ap);
        va_end(ap);
    }
    return -1;
}

/* The function head every rendered function shares, named `<fn><suffix>`. */
static void vany_head(mf_sink *o, const char *fn, const char *suffix)
{
    kit_out(o, "static inline size_t %s%s(const unsigned char *subject, size_t n, size_t pos)\n"
               "{\n", fn, suffix);
}

/* The scalar body: the plain byte loop over [pos, n), one test per member. */
static void vany_body(mf_sink *o, const char *fn, const uint8_t *m, unsigned k)
{
    vany_head(o, fn, "__body");
    o->puts(o->u, "    for (size_t i = pos; i < n; i++)\n"
                  "        if (");
    for (unsigned j = 0; j < k; j++)
        kit_out(o, "%ssubject[i] == %u", j ? " || " : "", m[j]);
    o->puts(o->u, ") return i;\n"
                  "    return n;\n"
                  "}\n\n");
}

/* One block's member mask at `at` (C text): `(unsigned)MOVEMASK(OR(EQ(x,
 * v0), EQ(x, v1)...))` over the block's load `x`. */
static void vany_mask(mf_sink *o, const vany_ops *v, const char *ind, const char *at,
                      unsigned k)
{
    kit_out(o, "%sconst %s x = %s((const %s *)(subject + %s));\n"
               "%sunsigned m = (unsigned)%s(",
            ind, v->type, v->load, v->type, at, ind, v->mmask);
    for (unsigned j = 0; j + 1 < k; j++) kit_out(o, "%s(", v->or_);
    for (unsigned j = 0; j < k; j++)
        kit_out(o, "%s%s(x, v%u)%s", j ? ", " : "", v->eq, j, j ? ")" : "");
    o->puts(o->u, ");\n");
}

/* One level's guarded helper `<fn>__<stamp>`: the guard, the level's
 * header, the entry test (falling to `fall`), the block loop and the final
 * block (the module comment's THE FORM). */
static void vany_level(mf_sink *o, const char *fn, unsigned lv, const char *fall,
                       const uint8_t *m, unsigned k)
{
    const mf_level *l = kit_level(lv);
    const vany_ops *v = &ops_of[lv];
    char suffix[32];
    snprintf(suffix, sizeof suffix, "__%s", l->stamp);
    if (o->simd_open && o->simd_close) o->simd_open(o->u, (int)lv);
    kit_out(o, "#if %s\n#include <%s>\n", l->guard, l->header);
    vany_head(o, fn, suffix);
    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\n"
               "    const %s ", l->vw, fall, v->type);
    for (unsigned j = 0; j < k; j++)
        kit_out(o, "%sv%u = %s((char)%u)", j ? ", " : "", j, v->set1, m[j]);
    kit_out(o, ";\n"
               "    size_t i = pos;\n"
               "    for (; n - i >= %u; i += %u) {\n", l->vw, l->vw);
    vany_mask(o, v, "        ", "i", k);
    kit_out(o, "        if (m) return i + (size_t)__builtin_ctz(m);\n"
               "    }\n"
               "    if (i == n) return n;\n"
               "    {\n");
    char at[32];
    snprintf(at, sizeof at, "(n - %u)", l->vw);
    vany_mask(o, v, "        ", at, k);
    kit_out(o, "        if (m) return n - %u + (size_t)__builtin_ctz(m);\n"
               "    }\n"
               "    return n;\n"
               "}\n"
               "#endif\n\n", l->vw);
    if (o->simd_open && o->simd_close) o->simd_close(o->u);
}

/* The selector `<fn>`: its whole body the `#if` chain over the rendered
 * levels, top level first, the body in the `#else` arm (D155). */
static void vany_selector(mf_sink *o, const char *fn, uint32_t levels)
{
    vany_head(o, fn, "");
    int first = 1;
    for (unsigned lv = MF_NLEVEL; lv-- > 0;) {
        if (!(levels & 1u << lv)) continue;
        kit_out(o, "#%s %s\n"
                   "    return %s__%s(subject, n, pos);\n",
                first ? "if" : "elif", kit_level(lv)->guard, fn, kit_level(lv)->stamp);
        first = 0;
    }
    if (!first) o->puts(o->u, "#else\n");
    kit_out(o, "    return %s__body(subject, n, pos);\n", fn);
    if (!first) o->puts(o->u, "#endif\n");
    o->puts(o->u, "}\n\n");
}

int mf_kernel_find_any(mf_sink *o, const char *fn, const uint8_t *bytes, unsigned k,
                       uint32_t levels, char *err, size_t errn)
{
    if (!o || !o->puts || !o->vprintf)
        return vany_refuse(err, errn, "find-any: the sink needs `puts` and `vprintf`");
    if (!fn || !kit_is_ident(fn) || strlen(fn) > 200)
        return vany_refuse(err, errn, "find-any: `fn` must be a C identifier of at most 200 bytes");
    if (!bytes || k < 2 || k > VANY_MAX_K)
        return vany_refuse(err, errn, "find-any: K must be 2..%d bytes, got %u", VANY_MAX_K, k);
    if (levels >> MF_NLEVEL)
        return vany_refuse(err, errn, "find-any: level bit %d is not a level (mf_levels() has %d)",
                           31 - __builtin_clz(levels), MF_NLEVEL);
    for (unsigned lv = 0; lv < MF_NLEVEL; lv++)
        if (levels & 1u << lv && !ops_of[lv].type)
            return vany_refuse(err, errn, "find-any: no form at level %s", kit_level(lv)->stamp);

    uint8_t m[VANY_MAX_K];
    unsigned nm = 0;
    for (unsigned j = 0; j < k; j++) {
        unsigned d = 0;
        while (d < nm && m[d] != bytes[j]) d++;
        if (d == nm) m[nm++] = bytes[j];
    }

    vany_body(o, fn, m, nm);
    char fall[256];
    snprintf(fall, sizeof fall, "%s__body", fn);
    for (unsigned lv = 0; lv < MF_NLEVEL; lv++) {
        if (!(levels & 1u << lv)) continue;
        vany_level(o, fn, lv, fall, m, nm);
        snprintf(fall, sizeof fall, "%s__%s", fn, kit_level(lv)->stamp);
    }
    vany_selector(o, fn, levels);
    return 0;
}
