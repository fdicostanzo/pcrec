/* cand_sse.c -- 128-bit (SSE2 + SSSE3) ports of the AVX2 candidates.
 *
 * Every function here is a width-for-width port of an AVX2 twin elsewhere in
 * the tree: same algorithm, same idiom, same scalar tail, only the register
 * width differs. That is the point -- the A/B against the 256-bit versions
 * then measures vector width and nothing else.
 *
 * This file is compiled with -mssse3 -mno-avx -mno-avx2, so any 256-bit
 * intrinsic is a compile error rather than a silent VEX-encoded upgrade.
 * The SSSE3 ceiling has two consequences worth naming:
 *   - _mm_shuffle_epi8 (pshufb) is available, so shufti still works;
 *   - _mm_testz_si128 is SSE4.1 and is NOT available, so every early exit
 *     is spelled `_mm_movemask_epi8(m) == 0` instead. On a 128-bit mask that
 *     costs one pmovmskb + test rather than ptest, which is the same
 *     latency class; the AVX2 twins' vptest is not a width advantage.
 *
 * Bounds contract (guard-page enforced, identical to the AVX2 files):
 * position j of a k-byte pattern loads 16 bytes at hay+i+j, so the highest
 * byte an iteration touches is i+(k-1)+15, and the loop bound
 * i+16+(k-1) <= n keeps every load inside [hay, hay+n).
 *
 * movemask over 16 lanes yields a 16-bit value in an int; nonzero means some
 * lane survived, and __builtin_ctz gives the leftmost such lane.
 */

#include <tmmintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* ---- exact literal needles: per-position broadcast AND-chain ---------- */

/* Port of find_hello_avx2_bcast. Each needle byte gets its own broadcast
 * register; the duplicated 'l' reuses one register for both positions. */
const char *find_sse_hello(const char *hay, size_t n)
{
    if (n < 5) {
        return NULL;
    }

    const __m128i bh = _mm_set1_epi8('h');
    const __m128i be = _mm_set1_epi8('e');
    const __m128i bl = _mm_set1_epi8('l');
    const __m128i bo = _mm_set1_epi8('o');

    size_t i = 0;
    /* Highest byte touched this iteration is i+4+15; i+16+4<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 16 + 4 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));
        __m128i v3 = _mm_loadu_si128((const __m128i *)(hay + i + 3));
        __m128i v4 = _mm_loadu_si128((const __m128i *)(hay + i + 4));

        __m128i m = _mm_cmpeq_epi8(v0, bh);
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v1, be));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v2, bl));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v3, bl));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v4, bo));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 5 <= n; i++) {
        if (hay[i] == 'h' && memcmp(hay + i, "hello", 5) == 0) {
            return hay + i;
        }
    }
    return NULL;
}

/* Port of find_gen_wolf. k=4, so no early exit: at four positions the test
 * costs more than the two loads and two ANDs it could save. */
const char *find_sse_wolf(const char *hay, size_t n)
{
    static const char needle[4] = { 'w', 'o', 'l', 'f' };

    if (n < 4) {
        return NULL;
    }

    const __m128i bw = _mm_set1_epi8('w');
    const __m128i bo = _mm_set1_epi8('o');
    const __m128i bl = _mm_set1_epi8('l');
    const __m128i bf = _mm_set1_epi8('f');

    size_t i = 0;
    /* Highest byte touched this iteration is i+3+15. */
    for (; i + 16 + 3 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));
        __m128i v3 = _mm_loadu_si128((const __m128i *)(hay + i + 3));

        __m128i m = _mm_cmpeq_epi8(v0, bw);
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v1, bo));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v2, bl));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v3, bf));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 4 <= n; i++) {
        int j = 0;
        for (; j < 4; j++) {
            if (hay[i + j] != needle[j]) {
                break;
            }
        }
        if (j == 4) {
            return hay + i;
        }
    }
    return NULL;
}

/* Port of find_gen_backfire. k=8 with the early exit: from the second
 * position onward, a zero mask means no lane can still match, so the
 * remaining loads and ANDs are skipped.
 *
 * The positions are written out as straight-line code rather than as a loop
 * over a member table: GCC would not specialise such a loop here (the table
 * lookup hides the member bytes from constant propagation), so the emitted
 * code re-broadcast members from memory every iteration. */
const char *find_sse_backfire(const char *hay, size_t n)
{
    static const char needle[8] = { 'b', 'a', 'c', 'k', 'f', 'i', 'r', 'e' };

    if (n < 8) {
        return NULL;
    }

    const __m128i bb = _mm_set1_epi8('b');
    const __m128i ba = _mm_set1_epi8('a');
    const __m128i bc = _mm_set1_epi8('c');
    const __m128i bk = _mm_set1_epi8('k');
    const __m128i bf = _mm_set1_epi8('f');
    const __m128i bi = _mm_set1_epi8('i');
    const __m128i br = _mm_set1_epi8('r');
    const __m128i be = _mm_set1_epi8('e');

    size_t i = 0;
    /* Highest byte touched this iteration is i+7+15. */
    for (; i + 16 + 7 <= n; i += 16) {
        __m128i m = _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 0)), bb);

        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 1)), ba));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 2)), bc));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 3)), bk));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 4)), bf));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 5)), bi));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 6)), br));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 7)), be));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 8 <= n; i++) {
        int j = 0;
        for (; j < 8; j++) {
            if (hay[i + j] != needle[j]) {
                break;
            }
        }
        if (j == 8) {
            return hay + i;
        }
    }
    return NULL;
}

/* Port of find_gen_k16 ("incomprehensible"): the same unrolled chain and the
 * same per-position early exit, now sixteen positions deep. At this length
 * the exit almost always fires on position 1, so the steady-state cost is
 * two loads and one test per block regardless of k. */
const char *find_sse_k16(const char *hay, size_t n)
{
    static const char needle[16] = { 'i', 'n', 'c', 'o', 'm', 'p', 'r', 'e',
                                     'h', 'e', 'n', 's', 'i', 'b', 'l', 'e' };

    if (n < 16) {
        return NULL;
    }

    const __m128i bi = _mm_set1_epi8('i');
    const __m128i bn = _mm_set1_epi8('n');
    const __m128i bc = _mm_set1_epi8('c');
    const __m128i bo = _mm_set1_epi8('o');
    const __m128i bm = _mm_set1_epi8('m');
    const __m128i bp = _mm_set1_epi8('p');
    const __m128i br = _mm_set1_epi8('r');
    const __m128i be = _mm_set1_epi8('e');
    const __m128i bh = _mm_set1_epi8('h');
    const __m128i bs = _mm_set1_epi8('s');
    const __m128i bb = _mm_set1_epi8('b');
    const __m128i bl = _mm_set1_epi8('l');

    size_t i = 0;
    /* Highest byte touched this iteration is i+15+15. */
    for (; i + 16 + 15 <= n; i += 16) {
        __m128i m = _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 0)), bi);

        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 1)), bn));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 2)), bc));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 3)), bo));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 4)), bm));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 5)), bp));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 6)), br));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 7)), be));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 8)), bh));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 9)), be));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 10)), bn));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 11)), bs));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 12)), bi));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 13)), bb));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 14)), bl));
        if (!_mm_movemask_epi8(m)) { continue; }
        m = _mm_and_si128(m, _mm_cmpeq_epi8(_mm_loadu_si128((const __m128i *)(hay + i + 15)), be));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 16 <= n; i++) {
        int j = 0;
        for (; j < 16; j++) {
            if (hay[i + j] != needle[j]) {
                break;
            }
        }
        if (j == 16) {
            return hay + i;
        }
    }
    return NULL;
}

/* ---- case-insensitive by OR-ing the two case twins -------------------- */

/* Port of find_ci_hello_or: per position, or(cmpeq(v,lower), cmpeq(v,upper)),
 * then the usual AND across positions. The 'l'/'L' twin pair is broadcast
 * once and reused for both 'l' positions. */
const char *find_sse_ci_hello(const char *hay, size_t n)
{
    static const char lower[5] = { 'h', 'e', 'l', 'l', 'o' };
    static const char upper[5] = { 'H', 'E', 'L', 'L', 'O' };

    if (n < 5) {
        return NULL;
    }

    const __m128i bh = _mm_set1_epi8('h');
    const __m128i bH = _mm_set1_epi8('H');
    const __m128i be = _mm_set1_epi8('e');
    const __m128i bE = _mm_set1_epi8('E');
    const __m128i bl = _mm_set1_epi8('l');
    const __m128i bL = _mm_set1_epi8('L');
    const __m128i bo = _mm_set1_epi8('o');
    const __m128i bO = _mm_set1_epi8('O');

    size_t i = 0;
    /* Highest byte touched this iteration is i+4+15. */
    for (; i + 16 + 4 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));
        __m128i v3 = _mm_loadu_si128((const __m128i *)(hay + i + 3));
        __m128i v4 = _mm_loadu_si128((const __m128i *)(hay + i + 4));

        __m128i m = _mm_or_si128(_mm_cmpeq_epi8(v0, bh), _mm_cmpeq_epi8(v0, bH));
        m = _mm_and_si128(m, _mm_or_si128(_mm_cmpeq_epi8(v1, be), _mm_cmpeq_epi8(v1, bE)));
        m = _mm_and_si128(m, _mm_or_si128(_mm_cmpeq_epi8(v2, bl), _mm_cmpeq_epi8(v2, bL)));
        m = _mm_and_si128(m, _mm_or_si128(_mm_cmpeq_epi8(v3, bl), _mm_cmpeq_epi8(v3, bL)));
        m = _mm_and_si128(m, _mm_or_si128(_mm_cmpeq_epi8(v4, bo), _mm_cmpeq_epi8(v4, bO)));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 5 <= n; i++) {
        int j = 0;
        for (; j < 5; j++) {
            char c = hay[i + j];
            if (c != lower[j] && c != upper[j]) {
                break;
            }
        }
        if (j == 5) {
            return hay + i;
        }
    }
    return NULL;
}

/* ---- contiguous range via saturating subtract ------------------------- */

/* Port of find_rng_digits, pattern [0-9][0-9]px. For an inclusive range
 * [lo,hi]: t = v - lo wraps bytes below lo to large unsigned values, then a
 * saturating unsigned subtract of the width (hi-lo) clamps to zero exactly
 * when unsigned t <= hi-lo, and cmpeq against zero turns that into a lane
 * mask. SSE2 has no unsigned byte compare either, so the idiom is the same
 * one the AVX2 version uses -- only the register is narrower. */
const char *find_sse_rng_digits(const char *hay, size_t n)
{
    if (n < 4) {
        return NULL;
    }

    const __m128i zero    = _mm_setzero_si128();
    const __m128i lo_zero = _mm_set1_epi8('0');
    const __m128i width9  = _mm_set1_epi8(9); /* '9' - '0' */
    const __m128i bp      = _mm_set1_epi8('p');
    const __m128i bx      = _mm_set1_epi8('x');

    size_t i = 0;
    /* Highest byte touched this iteration is i+3+15. */
    for (; i + 16 + 3 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));
        __m128i v3 = _mm_loadu_si128((const __m128i *)(hay + i + 3));

        /* Position 0 and 1: '0'..'9' via saturating-subtract range test. */
        __m128i t0  = _mm_sub_epi8(v0, lo_zero);
        __m128i in0 = _mm_cmpeq_epi8(_mm_subs_epu8(t0, width9), zero);

        __m128i t1  = _mm_sub_epi8(v1, lo_zero);
        __m128i in1 = _mm_cmpeq_epi8(_mm_subs_epu8(t1, width9), zero);

        /* Position 2 and 3: plain literal bytes 'p' and 'x'. */
        __m128i m = _mm_and_si128(in0, in1);
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v2, bp));
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v3, bx));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 4 <= n; i++) {
        char c0 = hay[i];
        char c1 = hay[i + 1];
        if (c0 >= '0' && c0 <= '9' &&
            c1 >= '0' && c1 <= '9' &&
            hay[i + 2] == 'p' && hay[i + 3] == 'x') {
            return hay + i;
        }
    }
    return NULL;
}

/* ---- scattered set via pshufb (shufti) -------------------------------- */

/* Same tables as cand_shufti.c, for S = {a,e,i,o,u,0,3,6,9,_}: lo_tbl is
 * keyed by low nibble and holds a bit per member high nibble, hi_tbl[h] is
 * 1<<h. AND-ing the two lookups is nonzero exactly for members, since a
 * (lo,hi) pair determines the byte. See cand_shufti.c for the derivation. */
static const uint8_t sse_lo_tbl[16] = {
    0x08, 0x40, 0x00, 0x08, 0x00, 0xc0, 0x08, 0x00,
    0x00, 0x48, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60,
};
static const uint8_t sse_hi_tbl[16] = {
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

static int sse_is_scatter_member(char c)
{
    return memchr("aeiou0369_", c, 10) != NULL;
}

/* Port of find_shufti_scatter, pattern [aeiou0369_]zq.
 *
 * This is the one place where 128 bits is genuinely SIMPLER than 256: pshufb
 * shuffles within each 128-bit lane independently, so the AVX2 version has to
 * load the 16-byte table and then broadcast it into both lanes of a ymm
 * register to make the second lane look up the same table. At 128 bits the
 * register IS one lane, so a single _mm_loadu_si128 of the table is used
 * directly -- no lane duplication, and one fewer setup instruction. */
const char *find_sse_shufti(const char *hay, size_t n)
{
    if (n < 3) {
        return NULL;
    }

    const __m128i lo_tbl_v = _mm_loadu_si128((const __m128i *)sse_lo_tbl);
    const __m128i hi_tbl_v = _mm_loadu_si128((const __m128i *)sse_hi_tbl);

    const __m128i nibble_mask = _mm_set1_epi8(0x0f);
    const __m128i zero        = _mm_setzero_si128();
    const __m128i bz          = _mm_set1_epi8('z');
    const __m128i bq          = _mm_set1_epi8('q');

    size_t i = 0;
    /* Highest byte touched this iteration is i+2+15. */
    for (; i + 16 + 2 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));

        __m128i lo = _mm_shuffle_epi8(lo_tbl_v, _mm_and_si128(v0, nibble_mask));

        /* No per-byte shift exists, so the high nibble of every byte comes
         * from a 16-bit-lane shift right by 4 masked back to 4 bits: the bits
         * leaking in from the neighbouring byte land above the mask. Bytes
         * >= 0x80 land in hi nibble 8..15 where hi_tbl is zero, so they fall
         * out as non-members for free. */
        __m128i hi_nib = _mm_and_si128(_mm_srli_epi16(v0, 4), nibble_mask);
        __m128i hi = _mm_shuffle_epi8(hi_tbl_v, hi_nib);

        __m128i t = _mm_and_si128(lo, hi); /* nonzero byte == member */

        /* Position 1 and 2: plain literal bytes 'z' and 'q'. */
        __m128i m = _mm_cmpeq_epi8(v1, bz);
        m = _mm_and_si128(m, _mm_cmpeq_epi8(v2, bq));
        /* andnot(cmpeq(t,0), m) clears exactly the lanes where t is zero,
         * folding "position 0 is a member" into the chain without building a
         * separate not-equal mask. */
        m = _mm_andnot_si128(_mm_cmpeq_epi8(t, zero), m);

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    for (; i + 3 <= n; i++) {
        if (sse_is_scatter_member(hay[i]) && hay[i + 1] == 'z' && hay[i + 2] == 'q') {
            return hay + i;
        }
    }
    return NULL;
}

/* ---- prefiltered alternation ------------------------------------------ */

/* Port of find_alt_names_pf3: fred|bob|janet|frederick behind a depth-3
 * union-class filter.
 *
 *     unionclass_j = { branch[j] : branch in the alternation }, j < min_k = 3
 *
 * F = u0 & u1 & u2 is a necessary condition for any branch to match, and it
 * needs only three loads. When F is empty the block is dropped before the
 * other six loads and their AND chains are issued; when it survives, the eq
 * registers that built F are reused as the first three terms of each branch,
 * so the filter costs nothing extra on the hit path.
 *
 * The 128-bit filter is inherently less selective per block than the 256-bit
 * one only in the trivial sense that it covers half as many positions; the
 * per-byte survival rate is identical, which is exactly what makes this a
 * clean width A/B. */
const char *find_sse_alt_pf3(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

    const __m128i bf = _mm_set1_epi8('f');
    const __m128i br = _mm_set1_epi8('r');
    const __m128i be = _mm_set1_epi8('e');
    const __m128i bd = _mm_set1_epi8('d');
    const __m128i bi = _mm_set1_epi8('i');
    const __m128i bc = _mm_set1_epi8('c');
    const __m128i bk = _mm_set1_epi8('k');
    const __m128i bb = _mm_set1_epi8('b');
    const __m128i bo = _mm_set1_epi8('o');
    const __m128i bj = _mm_set1_epi8('j');
    const __m128i ba = _mm_set1_epi8('a');
    const __m128i bn = _mm_set1_epi8('n');
    const __m128i bt = _mm_set1_epi8('t');

    size_t i = 0;
    /* Highest byte touched this iteration is i+8+15, from the longest
     * branch's v8; i+16+8<=n keeps every load inside [hay, hay+n). */
    for (; i + 16 + 8 <= n; i += 16) {
        __m128i v0 = _mm_loadu_si128((const __m128i *)(hay + i + 0));
        __m128i v1 = _mm_loadu_si128((const __m128i *)(hay + i + 1));
        __m128i v2 = _mm_loadu_si128((const __m128i *)(hay + i + 2));

        /* position 0: fred/frederick, bob, janet */
        __m128i e_f  = _mm_cmpeq_epi8(v0, bf);
        __m128i e_b  = _mm_cmpeq_epi8(v0, bb);
        __m128i e_j  = _mm_cmpeq_epi8(v0, bj);
        /* position 1 */
        __m128i e_r1 = _mm_cmpeq_epi8(v1, br);
        __m128i e_o1 = _mm_cmpeq_epi8(v1, bo);
        __m128i e_a1 = _mm_cmpeq_epi8(v1, ba);
        /* position 2 */
        __m128i e_e2 = _mm_cmpeq_epi8(v2, be);
        __m128i e_b2 = _mm_cmpeq_epi8(v2, bb);
        __m128i e_n2 = _mm_cmpeq_epi8(v2, bn);

        __m128i u0 = _mm_or_si128(_mm_or_si128(e_f, e_b), e_j);
        __m128i u1 = _mm_or_si128(_mm_or_si128(e_r1, e_o1), e_a1);
        __m128i u2 = _mm_or_si128(_mm_or_si128(e_e2, e_b2), e_n2);
        __m128i F  = _mm_and_si128(_mm_and_si128(u0, u1), u2);
        /* No _mm_testz_si128 at SSSE3; movemask == 0 is the same test. */
        if (!_mm_movemask_epi8(F)) {
            continue; /* three loads consumed, six loads and 12 ANDs skipped */
        }

        __m128i v3 = _mm_loadu_si128((const __m128i *)(hay + i + 3));
        __m128i v4 = _mm_loadu_si128((const __m128i *)(hay + i + 4));
        __m128i v5 = _mm_loadu_si128((const __m128i *)(hay + i + 5));
        __m128i v6 = _mm_loadu_si128((const __m128i *)(hay + i + 6));
        __m128i v7 = _mm_loadu_si128((const __m128i *)(hay + i + 7));
        __m128i v8 = _mm_loadu_si128((const __m128i *)(hay + i + 8));

        /* Each chain's first three positions ARE the filter's terms; only
         * the tail of each chain is new work. */
        __m128i mf = _mm_and_si128(_mm_and_si128(e_f, e_r1), e_e2);
        mf = _mm_and_si128(mf, _mm_cmpeq_epi8(v3, bd));

        __m128i mfk = _mm_and_si128(mf, _mm_cmpeq_epi8(v4, be));
        mfk = _mm_and_si128(mfk, _mm_cmpeq_epi8(v5, br));
        mfk = _mm_and_si128(mfk, _mm_cmpeq_epi8(v6, bi));
        mfk = _mm_and_si128(mfk, _mm_cmpeq_epi8(v7, bc));
        mfk = _mm_and_si128(mfk, _mm_cmpeq_epi8(v8, bk));

        /* bob is exactly min_k long, so its mask is finished the moment the
         * filter terms are AND-ed together. */
        __m128i mb = _mm_and_si128(_mm_and_si128(e_b, e_o1), e_b2);

        __m128i mj = _mm_and_si128(_mm_and_si128(e_j, e_a1), e_n2);
        mj = _mm_and_si128(mj, _mm_cmpeq_epi8(v3, be));
        mj = _mm_and_si128(mj, _mm_cmpeq_epi8(v4, bt));

        __m128i m = _mm_or_si128(_mm_or_si128(mf, mfk),
                                 _mm_or_si128(mb, mj));

        int mask = _mm_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz((unsigned)mask);
        }
    }

    /* Tail bounded by the SHORTEST branch; each branch is length-guarded
     * individually, and any hit at i returns immediately. */
    for (; i + 3 <= n; i++) {
        if (i + 4 <= n && memcmp(hay + i, "fred", 4) == 0) {
            return hay + i;
        }
        if (memcmp(hay + i, "bob", 3) == 0) {
            return hay + i;
        }
        if (i + 5 <= n && memcmp(hay + i, "janet", 5) == 0) {
            return hay + i;
        }
        if (i + 9 <= n && memcmp(hay + i, "frederick", 9) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
