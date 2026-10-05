/* memfn R4b (R-1): the fused scan+verify on the POST-HANDOFF build.
 *
 * Question (memfn/docs/requests.md R-1; integration.md §15.5, §21.1): does a
 * PORTABLE fused pair-filter gate (`swar`) beat the gate pcrec emits at
 * abi 61 (`emit`), in both regimes (R4d's trigger, the SIMD-off reading);
 * and does the vector fused form (`ffl`) beat `swar`, the current best
 * scalar (D147, the SIMD-on reading)?
 *
 * PIN: pcrec main d4d9ed90, abi 61 (nothing under src/ cli/ lib/ changed
 * since f116cff5, the T3 handoff). The emitted gate is copied VERBATIM:
 * gates_d4d9ed90/<cell>_def.inc is the artifact's rx_reqrun definition (and
 * the rx_wN helper in front of it), byte for byte; <cell>_use.txt is the
 * entry's pre-check lines. gates_sync.sh re-emits at a pin and diffs both.
 * The wrappers below are the use lines with ONE substitution: `return 0;`
 * (no match) becomes `return subject_length;` (the gate's miss value), and
 * union-select's use line, which discards the position, returns the call's
 * value. twins.md §3.1's 8a41efd2 copy (tb_run.c) is RETIRED as comparator:
 * its rx_reqrun texts are unchanged at abi 61, but userpass's site gained
 * the set-leads `memchr('=')` pre-check (K82 (A), abi 60).
 *
 * The function every variant computes is the composite site's (one site,
 * §15.5: an optional LEAD byte, then the window RUN):
 *
 *   gate(s, n, pos) = n                    if LEAD and no s[j] == LEAD, pos <= j < n
 *                   = the first c >= pos with c + L <= n and
 *                     (s[c+j] & M[j]) == V[j] for every j < L,
 *                   else n
 *
 * Cells (bench pattern; run, scan offset KA, second filter offset KB, lead):
 *   us  union-select  (?i)union.*?select.*?from  SELECT@4 C/c, T@5   none (no-DFA route)
 *   up  userpass      (?:username|USERNAME|...)  USER@0  U/u, R@3    '=' (set-leads)
 *   mi  mod-i         (?i)cat                    CAT@0   C/c, T@2    none (handoff)
 *   cn  cls-n-uc      it\Nm                      it@0    i,   t@1    'm' (set-leads, K85)
 * Caseless letters mask 0xDF against the upper case; cls-n-uc is exact.
 *
 * Variants:
 *   emit   the abi-61 gate, verbatim (two memchr streams per caseless run,
 *          memchr + memcmp for the exact one; the lead's one-shot memchr)
 *   emit2  emit again, a second timed instance of the same code: the
 *          base-vs-base FLOOR (D144 addendum 1), measured the same way
 *   nosl   cls-n-uc only: the `-fno-req-set-lead` artifact's gate (the run
 *          alone, the three memchr lines gone): K85's off arm. It computes
 *          a DIFFERENT function (no lead clause) and is checked as such
 *   swar   NEW, the scalar-layer candidate: 64-bit words, plain C, a
 *          pair filter (KA AND KB, exact zero-byte detection) + the masked
 *          run compare, the lead OR-accumulated in the same pass
 *   ffl    twins.md T-B's vector fused form (vec.h: SSE2, AVX2, NEON),
 *          carried with per-byte masks and the same lead accumulation
 *   byte   the scalar byte loop (timed for scale only)
 *
 * Regimes (ns, min of REPEATS loops >= 50 ms each, spread %):
 *   THROUGHPUT  gate:  one call from 0 on the whole subject
 *               sweep: call, restart at hit + 1, to the end (find-all)
 *   PER-CALL    short: one call from 0 on each of the capability set's 75
 *                      short subjects (1..93 B; ns per subject)
 *               pc16/pc64/pc256/pc1k: one call from 0 on each of up to 256
 *                      consecutive chunks of the cell's t-64k of that
 *                      length (the 16 B..1 KiB ladder R-1 names; ns per call)
 *
 * Correctness (--check [--subjects=DIR]), before any timing counts: every
 * variant's whole sweep against ref() -- a naive per-position, per-byte
 * loop sharing no code with any variant -- on a GENERATED set (n 0..129,
 * alignments 0..15, a planted run at every offset and none, the lead absent
 * / only at n-1 / only at 0 / random, near-miss filler), guard pages at both
 * ends, random fuzz and, with --subjects, every real subject; then the
 * PLANTED variants (one defect each) must FAIL it. Exit 0 iff every real
 * variant passes and every planted one is caught.
 */
#include "vec.h"

/* ---- the cells, as compile-time constants ---------------------------------
 * CELL(L, V, M, KA, KB, LEAD): run length, run bytes (masked), masks, the
 * emitted scan offset, the second filter offset, the lead byte or -1. */
#define CELL_us 6, "SELECT", "\337\337\337\337\337\337", 4, 5, -1
#define CELL_up 4, "USER", "\337\337\337\337", 0, 3, '='
#define CELL_mi 3, "CAT", "\337\337\337", 0, 2, -1
#define CELL_cn 2, "it", "\377\377", 0, 1, 'm'

/* ---- emit: the abi-61 gates, verbatim (pcrec d4d9ed90, -p rx) ------------- */

#define rx_w4 us_rx_w4
#define rx_reqrun us_rx_reqrun
#include "gates_d4d9ed90/us_def.inc"
#undef rx_w4
#undef rx_reqrun
#define rx_w4 up_rx_w4
#define rx_reqrun up_rx_reqrun
#include "gates_d4d9ed90/up_def.inc"
#undef rx_w4
#undef rx_reqrun
#define rx_w2 mi_rx_w2
#define rx_reqrun mi_rx_reqrun
#include "gates_d4d9ed90/mi_def.inc"
#undef rx_w2
#undef rx_reqrun
#define rx_reqrun cn_rx_reqrun
#include "gates_d4d9ed90/cn_def.inc"
#undef rx_reqrun

/* the use lines (<cell>_use.txt), `return 0;` -> `return subject_length;` */
INL size_t emit_us(const unsigned char *subject, size_t subject_length, size_t search_from)
{
    return us_rx_reqrun(subject, subject_length, search_from);
}
INL size_t emit_up(const unsigned char *subject, size_t subject_length, size_t search_from)
{
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 61, subject_length - search_from))
        return subject_length;
    size_t handoff_position = up_rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return subject_length;
    return handoff_position;
}
INL size_t emit_mi(const unsigned char *subject, size_t subject_length, size_t search_from)
{
    size_t handoff_position = mi_rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return subject_length;
    return handoff_position;
}
INL size_t emit_cn(const unsigned char *subject, size_t subject_length, size_t search_from)
{
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 109, subject_length - search_from))
        return subject_length;
    size_t handoff_position = cn_rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return subject_length;
    return handoff_position;
}
/* -fno-req-set-lead: the same artifact without the three memchr lines */
INL size_t nosl_cn(const unsigned char *subject, size_t subject_length, size_t search_from)
{
    size_t handoff_position = cn_rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return subject_length;
    return handoff_position;
}

/* ---- shared by swar/ffl/byte ------------------------------------------------ */

/* the masked compare of the whole run at p (L 1..8): one or two overlapping
 * words, the emitted compare's own shape */
INL int run_eq(const uint8_t *p, int L, const char *V, const char *M)
{
    if (L >= 4) {
        uint32_t a, b, ma, mb, va, vb;
        memcpy(&a, p, 4), memcpy(&b, p + L - 4, 4);
        memcpy(&ma, M, 4), memcpy(&mb, M + L - 4, 4);
        memcpy(&va, V, 4), memcpy(&vb, V + L - 4, 4);
        return (a & ma) == va && (b & mb) == vb;
    }
    if (L >= 2) {
        uint16_t a, b, ma, mb, va, vb;
        memcpy(&a, p, 2), memcpy(&b, p + L - 2, 2);
        memcpy(&ma, M, 2), memcpy(&mb, M + L - 2, 2);
        memcpy(&va, V, 2), memcpy(&vb, V + L - 2, 2);
        return (a & ma) == va && (b & mb) == vb;
    }
    return (p[0] & (uint8_t)M[0]) == (uint8_t)V[0];
}

/* the pair filter IS the run when the run is two bytes and the filter's
 * offsets are both of them (the zero-byte masks below are exact) */
#define PAIR_IS_RUN(L, KA, KB) ((L) == 2 && (KA) != (KB))

/* lead present in s[from, n)? (libc memchr: a scalar-layer call, Q50) */
INL int lead_in(const uint8_t *s, size_t from, size_t n, int LEAD)
{
    return from < n && memchr(s + from, LEAD, n - from) != NULL;
}

/* byte: the plain byte loop, every byte compared one at a time */
INL size_t f_byte(const uint8_t *s, size_t n, size_t pos, int L, const char *V,
                  const char *M, int KA, int KB, int LEAD)
{
    (void)KB;
    for (size_t c = pos; c + (size_t)L <= n; c++) {
        if ((s[c + KA] & (uint8_t)M[KA]) != (uint8_t)V[KA]) continue;
        int j = 0;
        while (j < L && (s[c + j] & (uint8_t)M[j]) == (uint8_t)V[j]) j++;
        if (j < L) continue;
        if (LEAD < 0) return c;
        for (size_t k = pos; k < n; k++)
            if (s[k] == (uint8_t)LEAD) return c;
        return n;
    }
    return n;
}

/* ---- swar: the portable fused pair-filter scan + verify --------------------
 *
 * One 64-bit word holds eight CANDIDATE positions c = i..i+7. For a block at
 * i the kernel loads the word at i + KA and the word at i + KB, masks each
 * with its offset's byte mask, XORs with the run byte, and marks the bytes
 * that are now zero (zbytes: EXACT, no borrow between bytes, so a marked
 * byte is a true match). The AND of the two marks is the pair filter; each
 * surviving lane, lowest first, is verified with run_eq and the first that
 * verifies is the run's leftmost occurrence. Blocks are taken two at a time
 * (16 candidates, one branch), then one, then ONE overlapped final block
 * ending at n whose lanes before i are masked off (they were tested).
 *
 * The lead is OR-accumulated in the same pass: zbytes(word at i ^ LEAD) for
 * every block, so when a candidate verifies at c the bytes [pos, cov) have
 * been looked at, cov being the end of the current block. If the lead was
 * seen, c is the answer; if not, the rest [cov, n) is searched once with
 * memchr (lead_in) and the answer is c or n. No run in [pos, n) returns n
 * without the lead mattering, as the emitted gate's value does.
 *
 * OVER-READ / BOUNDARY ARGUMENT -- the kernel reads ONLY bytes in [pos, n);
 * no page-boundary or alignment assumption is needed (ASan exact-size
 * allocations and both guard pages pass, --check):
 *   - Spans with n - pos < 8 + T (T = L - 1) take f_byte: reads [pos, n).
 *   - Every word load is ld64(s + x) for x in {i, i + KA, i + KB} (or the
 *     same at f), reading [x, x + 8). KA, KB <= T. The 2x loop runs while
 *     i + 16 + T <= n, so its highest byte is i + 8 + KB + 7 <= i + 15 + T
 *     < n; the 1x loop runs while i + 8 + T <= n: highest i + 7 + T < n.
 *     i starts at pos and only grows: lowest byte pos.
 *   - Final block: f = n - T - 8. pos + 8 + T <= n gives f >= pos; its
 *     highest byte is f + T + 7 = n - 1. The loops exit with
 *     f < i <= f + 8 (i - f = 8 would need f + 8 + L <= n, false), so the
 *     lane mask's shift 8 * (i - f) is 8..56 and the block adds exactly the
 *     candidates [i, n - T) the loops did not cover; when i + L > n there
 *     are none and the block is skipped.
 *   - A candidate c = base + k (k <= 7) of a block satisfies
 *     base + 7 + T <= n - 1, so run_eq's reads [c, c + L) end at <= n - 1.
 *   - The lead's coverage is contiguous: the loops cover [pos, i) in
 *     steps, the final block [f, f + 8) with f < i, so cov = f + 8 after
 *     it; lead_in reads [cov, n).
 * Endianness: lanes are numbered from the low byte, so ld64 is a
 * little-endian load (a byte swap on a big-endian target). */
INL uint64_t ld64(const uint8_t *p)
{
    uint64_t w;
    memcpy(&w, p, 8);
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    w = __builtin_bswap64(w);
#endif
    return w;
}
#define B8(x) (0x0101010101010101ull * (uint8_t)(x))
/* 0x80 in every byte of x that is zero, 0 elsewhere: exact */
INL uint64_t zbytes(uint64_t x)
{
    const uint64_t k = B8(0x7F);
    return ~(((x & k) + k) | x | k);
}

/* PLANT (0 in every real variant; --check's planted defects): 1 = the final
 * block's guard off by one (misses a hit at n - L when it is the only lane
 * left), 2 = the lead's rest search stops one byte short of n */
INL size_t f_swar(const uint8_t *s, size_t n, size_t pos, int L, const char *V,
                  const char *M, int KA, int KB, int LEAD, int PLANT)
{
    const size_t T = (size_t)L - 1;
    if (pos >= n || n - pos < 8 + T) return f_byte(s, n, pos, L, V, M, KA, KB, LEAD);
    const uint64_t ma = B8(M[KA]), va = B8(V[KA]), mb = B8(M[KB]), vb = B8(V[KB]);
    const uint64_t vl = B8(LEAD);
    uint64_t seen = 0;
#define CAND(p) (zbytes((ld64((p) + KA) & ma) ^ va) & zbytes((ld64((p) + KB) & mb) ^ vb))
#define LEADZ(p) (LEAD < 0 ? 0 : zbytes(ld64(p) ^ vl))
#define TRY(mk, base, cov)                                                            \
    do {                                                                              \
        uint64_t mm_ = (mk);                                                          \
        while (mm_) {                                                                 \
            size_t c_ = (base) + ((size_t)__builtin_ctzll(mm_) >> 3);                 \
            if (PAIR_IS_RUN(L, KA, KB) || run_eq(s + c_, L, V, M))                    \
                return LEAD < 0 || seen || lead_in(s, (cov), n - (PLANT == 2), LEAD) ? c_ : n; \
            mm_ &= mm_ - 1;                                                           \
        }                                                                             \
    } while (0)
    size_t i = pos;
    for (; i + 16 + T <= n; i += 16) {
        uint64_t m0 = CAND(s + i), m1 = CAND(s + i + 8);
        seen |= LEADZ(s + i) | LEADZ(s + i + 8);
        if (m0 | m1) {
            TRY(m0, i, i + 16);
            TRY(m1, i + 8, i + 16);
        }
    }
    for (; i + 8 + T <= n; i += 8) {
        uint64_t m = CAND(s + i);
        seen |= LEADZ(s + i);
        TRY(m, i, i + 8);
    }
    if (i + L + (PLANT == 1) <= n) {
        size_t f = n - T - 8;
        seen |= LEADZ(s + f);
        TRY(CAND(s + f) & (~0ull << (8 * (i - f))), f, f + 8);
    }
    return n;
#undef CAND
#undef LEADZ
#undef TRY
}

/* ---- ffl: the vector fused form (twins.md T-B), carried --------------------
 * tb_run.c's f_fused(ALL = 0) with per-byte masks and the lead accumulated
 * as in swar (a vector OR of the block's offset-0 compare, read only when a
 * candidate verifies). Loads reach VW + T past i; every load stays in
 * [pos, n) by the same argument as swar's with 8 -> VW. PLANT 1 as swar's. */
INL size_t f_ffl(const uint8_t *s, size_t n, size_t pos, int L, const char *V,
                 const char *M, int KA, int KB, int LEAD, int PLANT)
{
    const size_t T = (size_t)L - 1;
    if (pos >= n || n - pos < VW + T) return f_byte(s, n, pos, L, V, M, KA, KB, LEAD);
    const vu8 MA = vdup((uint8_t)M[KA]), VA = vdup((uint8_t)V[KA]);
    const vu8 MB = vdup((uint8_t)M[KB]), VB = vdup((uint8_t)V[KB]);
    const vu8 VL = vdup((uint8_t)LEAD), Z = vdup(0);
    vu8 seen = Z;
#define CMASK(p)                                                              \
    (vmask(vand(veq(vand(vload((p) + KA), MA), VA),                           \
                veq(vand(vload((p) + KB), MB), VB))) & VMASK_ONE)
#define LEADV(p) (LEAD < 0 ? Z : veq(vload(p), VL))
#define TRY(mk, base, cov)                                                    \
    do {                                                                      \
        uint64_t mm_ = (mk);                                                  \
        while (mm_) {                                                         \
            size_t c_ = (base) + vfirst(mm_);                                 \
            if (PAIR_IS_RUN(L, KA, KB) || run_eq(s + c_, L, V, M))            \
                return LEAD < 0 || vmask(seen) || lead_in(s, (cov), n, LEAD) ? c_ : n; \
            mm_ &= mm_ - 1;                                                   \
        }                                                                     \
    } while (0)
    size_t i = pos;
    for (; i + 2 * VW + T <= n; i += 2 * VW) {
        uint64_t m0 = CMASK(s + i), m1 = CMASK(s + i + VW);
        seen = vor(seen, vor(LEADV(s + i), LEADV(s + i + VW)));
        if (m0 | m1) {
            TRY(m0, i, i + 2 * VW);
            TRY(m1, i + VW, i + 2 * VW);
        }
    }
    for (; i + VW + T <= n; i += VW) {
        uint64_t m = CMASK(s + i);
        seen = vor(seen, LEADV(s + i));
        TRY(m, i, i + VW);
    }
    if (i + L + (PLANT == 1) <= n) {
        size_t f = n - T - VW;
        seen = vor(seen, LEADV(s + f));
        TRY(CMASK(s + f) & lane_from(i - f), f, f + VW);
    }
    return n;
#undef CMASK
#undef LEADV
#undef TRY
}

/* ---- the variant table ------------------------------------------------------ */

#define GEN(C)                                                                             \
    INL size_t k_##C##_emit(const uint8_t *s, size_t n, size_t p) { return emit_##C(s, n, p); } \
    INL size_t k_##C##_emit2(const uint8_t *s, size_t n, size_t p) { return emit_##C(s, n, p); } \
    INL size_t k_##C##_swar(const uint8_t *s, size_t n, size_t p) { return f_swar(s, n, p, CELL_##C, 0); } \
    INL size_t k_##C##_ffl(const uint8_t *s, size_t n, size_t p) { return f_ffl(s, n, p, CELL_##C, 0); } \
    INL size_t k_##C##_byte(const uint8_t *s, size_t n, size_t p) { return f_byte(s, n, p, CELL_##C); } \
    INL size_t k_##C##_Ptail(const uint8_t *s, size_t n, size_t p) { return f_swar(s, n, p, CELL_##C, 1); } \
    __attribute__((unused)) INL size_t k_##C##_Plead(const uint8_t *s, size_t n, size_t p) { return f_swar(s, n, p, CELL_##C, 2); } \
    INL size_t k_##C##_Pffltail(const uint8_t *s, size_t n, size_t p) { return f_ffl(s, n, p, CELL_##C, 1); }
GEN(us) GEN(up) GEN(mi) GEN(cn)
INL size_t k_cn_nosl(const uint8_t *s, size_t n, size_t p) { return nosl_cn(s, n, p); }

/* X(cell, variant, kind): kind 0 = real (timed, must pass), 1 = no-lead
 * real (cn's nosl: checked against ref without the lead), 2 = PLANTED (never
 * timed, must FAIL). Plead only where there is a lead to plant against. */
#define KERNELS(X)                                                            \
    X(us, emit, 0) X(us, emit2, 0) X(us, swar, 0) X(us, ffl, 0) X(us, byte, 0) \
    X(up, emit, 0) X(up, emit2, 0) X(up, swar, 0) X(up, ffl, 0) X(up, byte, 0) \
    X(mi, emit, 0) X(mi, emit2, 0) X(mi, swar, 0) X(mi, ffl, 0) X(mi, byte, 0) \
    X(cn, emit, 0) X(cn, emit2, 0) X(cn, nosl, 1) X(cn, swar, 0) X(cn, ffl, 0) X(cn, byte, 0) \
    X(us, Ptail, 2) X(up, Ptail, 2) X(mi, Ptail, 2) X(cn, Ptail, 2)          \
    X(up, Plead, 2) X(cn, Plead, 2)                                           \
    X(us, Pffltail, 2) X(up, Pffltail, 2) X(mi, Pffltail, 2) X(cn, Pffltail, 2)

/* a timed list: subjects ss[k] of length sn[k] */
struct tctx { const uint8_t *const *ss; const size_t *sn; int ns; long hits; };

/* gate: one call from 0 per subject; sweep: restart at hit + 1 to the end */
#define TIMER(C, V, K)                                                        \
    OOL static double tg_##C##_##V(const void *ctx, long reps)                \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        long tot = 0;                                                         \
        size_t acc = 0;                                                       \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++)                                       \
            for (int k = 0; k < c->ns; k++) {                                 \
                const uint8_t *s = c->ss[k];                                  \
                __asm__ volatile("" : "+r"(s));                               \
                size_t h = k_##C##_##V(s, c->sn[k], 0);                       \
                acc += h;                                                     \
                tot += h < c->sn[k];                                          \
            }                                                                 \
        double t1 = now_ns();                                                 \
        __asm__ volatile("" : : "r"(acc), "r"(tot));                          \
        c->hits = c->ns == 1 ? (long)(acc / (size_t)reps) : tot / reps;       \
        return t1 - t0;                                                       \
    }                                                                         \
    OOL static double ts_##C##_##V(const void *ctx, long reps)                \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        long tot = 0;                                                         \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++)                                       \
            for (int k = 0; k < c->ns; k++) {                                 \
                const uint8_t *s = c->ss[k];                                  \
                __asm__ volatile("" : "+r"(s));                               \
                size_t n = c->sn[k], p = 0;                                   \
                for (;;) {                                                    \
                    size_t h = k_##C##_##V(s, n, p);                          \
                    if (h >= n) break;                                        \
                    tot++;                                                    \
                    p = h + 1;                                                \
                }                                                             \
            }                                                                 \
        double t1 = now_ns();                                                 \
        __asm__ volatile("" : : "r"(tot));                                    \
        c->hits = tot / reps;                                                 \
        return t1 - t0;                                                       \
    }
KERNELS(TIMER)

struct kern {
    const char *cell, *var;
    int kind;
    size_t (*fn)(const uint8_t *, size_t, size_t);
    tbody tg, ts;
};
#define ROW(C, V, K) { #C, #V, K, k_##C##_##V, tg_##C##_##V, ts_##C##_##V },
static const struct kern kerns[] = { KERNELS(ROW) };
#define NK (int)(sizeof kerns / sizeof kerns[0])

/* the cell's constants as data, for ref() and the generator: the SAME
 * literals as CELL_*, re-stated (emit, which derives from pcrec's text and
 * not from these, is what catches a wrong row here) */
struct cellc { const char *name; int L; const char *V, *M; int KA, KB, LEAD; };
static const struct cellc cells[] = {
    { "us", 6, "SELECT", "\337\337\337\337\337\337", 4, 5, -1 },
    { "up", 4, "USER", "\337\337\337\337", 0, 3, '=' },
    { "mi", 3, "CAT", "\337\337\337", 0, 2, -1 },
    { "cn", 2, "it", "\377\377", 0, 1, 'm' },
};
static const struct cellc *cell_of(const char *name)
{
    for (size_t x = 0; x < sizeof cells / sizeof cells[0]; x++)
        if (!strcmp(cells[x].name, name)) return &cells[x];
    abort();
}

/* ---- correctness -------------------------------------------------------------
 * ref(): the definition, read literally -- the lead clause by a backward
 * byte loop, the run by a per-position, per-byte loop. Shares no code with
 * any variant (no run_eq, no word loads, no memchr). */
static size_t ref(const struct cellc *cc, int uselead, const uint8_t *s, size_t n, size_t pos)
{
    if (uselead && cc->LEAD >= 0) {
        size_t j = n;
        while (j > pos && s[j - 1] != (uint8_t)cc->LEAD) j--;
        if (j == pos) return n;
    }
    for (size_t c = pos; c + (size_t)cc->L <= n; c++) {
        int ok = 1;
        for (int j = 0; j < cc->L; j++)
            if ((s[c + j] & (uint8_t)cc->M[j]) != (uint8_t)cc->V[j]) ok = 0;
        if (ok) return c;
    }
    return n;
}

struct tally { long calls, hits, bad, faults; };
static struct tally g_t[64];
static int g_print = 20;

static void sweep_check(int x, const uint8_t *s, size_t n, size_t pos0, const char *what,
                        size_t a, size_t b)
{
    const struct kern *k = &kerns[x];
    const struct cellc *cc = cell_of(k->cell);
    size_t p = pos0;
    for (;;) {
        size_t want = ref(cc, k->kind != 1, s, n, p), got = k->fn(s, n, p);
        g_t[x].calls++;
        g_t[x].hits += want < n;
        if (got != want) {
            if (g_t[x].bad++ == 0 && k->kind != 2 && g_print-- > 0)
                printf("BAD %s/%s %s n=%zu a=%zu b=%zu pos=%zu got=%zu want=%zu\n",
                       k->cell, k->var, what, n, a, b, p, got, want);
            return;
        }
        if (want >= n) return;
        p = want + 1;
    }
}
OOL static void sweep_guarded(int x, const uint8_t *s, size_t n, const char *what, size_t a)
{
    if (sigsetjmp(g_jb, 1) == 0)
        sweep_check(x, s, n, 0, what, a, 0);
    else {
        g_t[x].faults++;
        if (kerns[x].kind != 2 && g_print-- > 0)
            printf("FAULT %s/%s %s n=%zu a=%zu\n", kerns[x].cell, kerns[x].var, what, n, a);
    }
}

/* filler: the run's bytes in either case, a byte equal to a run byte only
 * under its mask's 0x20 bit, a run byte ^ 0x80, the run's prefix, noise;
 * never the lead unless asked (lead modes below place it) */
static uint8_t filler(const struct cellc *cc, uint64_t r, int allow_lead)
{
    uint8_t b;
    unsigned j = (unsigned)(r >> 3) % (unsigned)cc->L;
    switch (r & 7) {
    case 0: case 1: case 2: b = (uint8_t)(cc->V[j] | ((r >> 8) & 1 ? 0x20 : 0)); break;
    case 3: b = (uint8_t)((r >> 3) & 0xFF); break;
    case 4: b = (uint8_t)(cc->V[j] ^ 0x80); break;
    case 5: b = (uint8_t)(cc->V[j] ^ 0x20); break;
    default: b = (uint8_t)('a' + (r >> 9) % 26); break;
    }
    if (!allow_lead && cc->LEAD >= 0 && b == (uint8_t)cc->LEAD) b ^= 1;
    return b;
}
/* the run, each byte's masked-off bits set at random (caseless: either case) */
static void plant(const struct cellc *cc, uint8_t *s, uint64_t r)
{
    for (int j = 0; j < cc->L; j++)
        s[j] = (uint8_t)(cc->V[j] | (~(uint8_t)cc->M[j] & ((r >> j) & 1 ? 0x20 : 0)));
}

/* lead modes: 0 absent, 1 only at n-1, 2 only at 0, 3 random (dense) */
static void fill(const struct cellc *cc, uint8_t *s, size_t n, size_t h, int mode)
{
    for (size_t i = 0; i < n; i++) s[i] = filler(cc, rng(), mode == 3);
    if (h + (size_t)cc->L <= n) plant(cc, s + h, rng());
    if (cc->LEAD >= 0 && n) {
        if (mode == 1) s[n - 1] = (uint8_t)cc->LEAD;
        if (mode == 2) s[0] = (uint8_t)cc->LEAD;
    }
}

static int subj_check(const char *dir);

static int check(const char *dir)
{
    const size_t NMAX = 129;
    for (size_t ci = 0; ci < sizeof cells / sizeof cells[0]; ci++) {
        const struct cellc *cc = &cells[ci];
        int modes = cc->LEAD >= 0 ? 4 : 1;
        rng_state = 0x9E3779B97F4A7C15ull + ci;
        /* generated: every n, alignment, run offset (h == n: none), lead mode */
        for (size_t n = 0; n <= NMAX; n++)
            for (size_t al = 0; al < 16; al++) {
                uint8_t *blk = malloc(al + n ? al + n : 1), *s = blk + al; /* exact: ASan sees s[n] */
                for (size_t h = 0; h <= n; h++)
                    for (int mode = 0; mode < modes; mode++) {
                        fill(cc, s, n, h, mode);
                        for (int x = 0; x < NK; x++) {
                            if (strcmp(kerns[x].cell, cc->name)) continue;
                            sweep_check(x, s, n, 0, "gen", al, h);
                            if (h & 1) sweep_check(x, s, n, h / 2, "gen-pos", al, h);
                        }
                    }
                free(blk);
            }
        /* guard pages: the span flush against an unmapped page at either end */
        for (size_t n = 0; n <= NMAX; n++)
            for (int side = 0; side < 2; side++)
                for (size_t off = 0; off < (side ? 16u : 1u); off++)
                    for (int mode = 0; mode < modes; mode++) {
                        uint8_t *s = side ? gstart(off) : gend(n);
                        fill(cc, s, n, n >= (size_t)cc->L ? n - (size_t)cc->L : n, mode);
                        for (int x = 0; x < NK; x++)
                            if (!strcmp(kerns[x].cell, cc->name))
                                sweep_guarded(x, s, n, side ? "gstart" : "gend", off);
                    }
        /* fuzz: longer spans, several runs */
        for (int t = 0; t < 3000; t++) {
            size_t n = (size_t)(rng() % 700);
            uint8_t *s = malloc(n + 1);
            fill(cc, s, n, n, (int)(rng() % (unsigned)modes));
            for (int q = (int)(rng() % 6); q > 0; q--)
                if (n >= (size_t)cc->L) plant(cc, s + rng() % (n - (size_t)cc->L + 1), rng());
            for (int x = 0; x < NK; x++)
                if (!strcmp(kerns[x].cell, cc->name)) sweep_check(x, s, n, 0, "fuzz", (size_t)t, 0);
            free(s);
        }
    }
    int rc = dir ? subj_check(dir) : 0;
    long rb = 0, pc = 0, pm = 0;
    printf("check (" VISA "): variant, calls, ref hits, bad, faults\n");
    for (int x = 0; x < NK; x++) {
        const struct kern *k = &kerns[x];
        int caught = g_t[x].bad + g_t[x].faults > 0;
        printf("  %-2s %-9s %9ld %8ld %7ld %3ld  %s\n", k->cell, k->var, g_t[x].calls,
               g_t[x].hits, g_t[x].bad, g_t[x].faults,
               k->kind == 2 ? (caught ? "PLANTED, CAUGHT" : "PLANTED, MISSED <-- the check is blind")
                            : (caught ? "WRONG" : "ok"));
        if (k->kind == 2) pc++, pm += !caught;
        else rb += caught;
    }
    printf("check (" VISA "): real variants wrong: %ld; planted %ld, missed %ld%s\n", rb, pc, pm,
           dir ? "; real subjects included" : "");
    return rc || rb || pm;
}

/* ---- subjects -------------------------------------------------------------- */

struct subj { const char *name; uint8_t *b; size_t n; };
static struct subj g_sub[8];
static int g_nsub;
static const uint8_t *g_ss[256];
static size_t g_sn[256];
static int g_nshort;

static void load_subjects(const char *dir)
{
    static const char *const names[] = { "cap/t-64k", "cap/t-1m", "syn/t-64k", "syn/t-256k", "syn/t-1m" };
    char path[4096];
    for (size_t q = 0; q < sizeof names / sizeof names[0]; q++) {
        snprintf(path, sizeof path, "%s/%s.bin", dir, names[q]);
        g_sub[g_nsub].name = names[q];
        g_sub[g_nsub].b = slurp(path, &g_sub[g_nsub].n);
        g_nsub++;
    }
    size_t sl;
    snprintf(path, sizeof path, "%s/short.bin", dir);
    uint8_t *sb = slurp(path, &sl);
    for (size_t o = 0; o + 4 <= sl && g_nshort < 256;) {
        uint32_t len;
        memcpy(&len, sb + o, 4);
        uint8_t *cp = malloc(len + 1); /* each in its own allocation, exact */
        memcpy(cp, sb + o + 4, len);
        g_ss[g_nshort] = cp, g_sn[g_nshort++] = len;
        o += 4 + len;
    }
}
static const struct subj *subj_named(const char *name)
{
    for (int q = 0; q < g_nsub; q++)
        if (!strcmp(g_sub[q].name, name)) return &g_sub[q];
    abort();
}
/* the subjects each cell is timed on (the bench's own cells: K82's
 * capability cells on cap text, mod-i and cls-n-uc on syntax text) */
static const char *const *cell_subjects(const char *cell)
{
    static const char *const cap[] = { "cap/t-64k", "cap/t-1m", NULL };
    static const char *const syn[] = { "syn/t-64k", "syn/t-1m", NULL };
    static const char *const k85[] = { "syn/t-64k", "syn/t-256k", "syn/t-1m", NULL };
    return !strcmp(cell, "us") || !strcmp(cell, "up") ? cap : !strcmp(cell, "cn") ? k85 : syn;
}

static int subj_check(const char *dir)
{
    load_subjects(dir);
    printf("check: real subjects (the cell's throughput texts + 75 short), calls / ref hits / bad\n");
    for (int x = 0; x < NK; x++) {
        struct tally t0 = g_t[x];
        for (const char *const *sp = cell_subjects(kerns[x].cell); *sp; sp++) {
            const struct subj *sj = subj_named(*sp);
            sweep_check(x, sj->b, sj->n, 0, sj->name, 0, 0);
        }
        for (int k = 0; k < g_nshort; k++) sweep_check(x, g_ss[k], g_sn[k], 0, "short", (size_t)k, 0);
        printf("  %-2s %-9s %7ld %7ld %5ld\n", kerns[x].cell, kerns[x].var, g_t[x].calls - t0.calls,
               g_t[x].hits - t0.hits, g_t[x].bad - t0.bad);
    }
    return 0;
}

/* ---- timing ----------------------------------------------------------------- */

/* one row: cell var regime subject ns(min) spread% hits; machine-read by
 * tb_r4b_table.py */
static void row(const struct kern *k, const char *regime, const char *subject,
                tbody f, struct tctx *c, int per)
{
    double lo, hi;
    tmeasure(f, c, &lo, &hi);
    printf("R\t%s\t%s\t%s\t%s\t%.3f\t%.1f\t%ld\n", k->cell, k->var, regime, subject,
           lo / per, 100 * (hi / lo - 1), c->hits);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    guard_init(4096);
    const char *dir = NULL;
    int chk = 0;
    const char *only = NULL;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--check")) chk = 1;
        else if (!strncmp(argv[a], "--subjects=", 11)) dir = argv[a] + 11;
        else if (!strncmp(argv[a], "--cell=", 7)) only = argv[a] + 7;
        else if (!strcmp(argv[a], "--quick")) g_min_loop_ns = 5e6;
        else { fprintf(stderr, "unknown argument %s\n", argv[a]); return 2; }
    }
    if (chk) return check(dir);
    if (!dir) {
        fprintf(stderr, "usage: tb_r4b --check [--subjects=DIR] | --subjects=DIR [--cell=C] [--quick]\n");
        return 2;
    }
    load_subjects(dir);
    printf("# memfn R4b tb_r4b (fused scan+verify, post-handoff abi 61, pin d4d9ed90), vec=%s VW=%d\n",
           VISA, VW);
    printf("# R cell var regime subject ns spread%% hits; ns = min of %d loops >= %.0f ms; "
           "gate/short/pc*: ns per call, sweep: ns per find-all\n", REPEATS, g_min_loop_ns / 1e6);
    static const size_t ladder[] = { 16, 64, 256, 1024 };
    for (int x = 0; x < NK; x++) {
        const struct kern *k = &kerns[x];
        if (k->kind == 2 || (only && strcmp(only, k->cell))) continue;
        for (const char *const *sp = cell_subjects(k->cell); *sp; sp++) {
            const struct subj *sj = subj_named(*sp);
            const uint8_t *s1[1] = { sj->b };
            size_t n1[1] = { sj->n };
            struct tctx c = { s1, n1, 1, 0 };
            row(k, "gate", sj->name, k->tg, &c, 1);
            row(k, "sweep", sj->name, k->ts, &c, 1);
        }
        struct tctx c = { g_ss, g_sn, g_nshort, 0 };
        row(k, "short", "cap-short75", k->tg, &c, g_nshort);
        const struct subj *base = subj_named(cell_subjects(k->cell)[0]);
        for (size_t q = 0; q < sizeof ladder / sizeof ladder[0]; q++) {
            static const uint8_t *cs[256];
            static size_t cn[256];
            int m = 0;
            for (size_t o = 0; o + ladder[q] <= base->n && m < 256; o += ladder[q])
                cs[m] = base->b + o, cn[m++] = ladder[q];
            struct tctx cl = { cs, cn, m, 0 };
            char reg[16];
            snprintf(reg, sizeof reg, "pc%zu", ladder[q]);
            row(k, reg, base->name, k->tg, &cl, m);
        }
    }
    printf("# END tb_r4b\n");
    return 0;
}
