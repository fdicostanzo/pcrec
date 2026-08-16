/* cand_shiftand.c -- blockwise Shift-And: the same literal match expressed as
 * scalar bitmap algebra over ONE wide window, instead of k shifted vector
 * loads per block.
 *
 * ---------------------------------------------------------------------------
 * The idea
 * ---------------------------------------------------------------------------
 *
 * The per-position AND-chain used by every other candidate here (cand_gen.c,
 * cand_alt.c, ...) is a load-shifting scheme: to test whether the needle
 * starts at each of 32 consecutive positions it loads 32 bytes at hay+i+j for
 * every needle position j, so that lane l of load j holds the byte that
 * position j would have to match if the needle started at i+l. The shift that
 * aligns "position j" with "start l" is performed by the ADDRESS, and it costs
 * one 32-byte load per needle position: k loads per 32 bytes of haystack.
 *
 * Shift-And performs the same alignment, but in scalar registers, after the
 * comparison. The window is loaded exactly ONCE:
 *
 *     v0 = 32 bytes at hay+i        (window bytes 0..31)
 *     v1 = 32 bytes at hay+i+32     (window bytes 32..63)
 *
 * For needle position j with byte c_j, compare that SAME window against the
 * broadcast of c_j and collapse the two lane masks into one 64-bit equality
 * bitmap:
 *
 *     m_j bit p  ==  (hay[i + p] == c_j),  p in 0..63
 *
 * Now "the needle starts at window offset l" is the conjunction
 *
 *     for all j:  hay[i + l + j] == c_j
 *              == bit (l + j) of m_j
 *              == bit l of (m_j >> j)
 *
 * so the whole block of 64 candidate starts is settled by one AND-reduction:
 *
 *     starts = m_0 & (m_1 >> 1) & (m_2 >> 2) & ... & (m_{k-1} >> (k-1))
 *
 * Bit l of `starts` set means the needle begins at hay + i + l. The right
 * shift by j is the exact scalar analogue of loading at hay+i+j -- the vector
 * version shifts the DATA past a fixed comparison point, this one shifts the
 * RESULT. Same alignment, different place in the pipeline.
 *
 * ---------------------------------------------------------------------------
 * Why bother: what the trade actually is
 * ---------------------------------------------------------------------------
 *
 * Per 64 bytes of haystack scanned, the AND-chain form issues 2*k loads; this
 * form issues 2. Everything else moves into the ALU and the scalar domain:
 * k*2 vpcmpeqb, k*2 vpmovmskb, and k-1 scalar shift+AND pairs. On Zen 1 (two
 * 128-bit load pipes, so a 32-byte load already occupies a port for two
 * cycles) the load ports are the scarce resource for long needles, and k=16
 * turns into 32 loads per 64 bytes in the AND-chain form versus 2 here. The
 * movemask results are also cheap to keep: a vpmovmskb is one uop and its
 * result lands in a GPR where the shifts are free-ish, whereas the vector form
 * must keep k live ymm values or re-load.
 *
 * The second, less obvious property is the one that motivated writing this at
 * all: **the work is completely content-independent**. There is no early exit,
 * no "stop AND-ing once the mask is zero" test. Every window costs exactly the
 * same. The AND-chain matchers with the `_mm256_testz_si256` early-out are
 * fast on random text precisely because the chain dies after one or two
 * positions -- and that is a data-dependent branch. Feed them a haystack whose
 * text is a periodic near-prefix of the needle (the pathological input that
 * drove k=16 down to 0.18x of memmem) and the early exit never fires, the
 * branch predictor thrashes, and the chain runs to full length on every block.
 * Shift-And cannot degrade that way because it never had the shortcut: its
 * worst case is its average case. It trades peak throughput on friendly input
 * for a flat profile across all input.
 *
 * ---------------------------------------------------------------------------
 * Bounds: the trustworthy-start mask and the overlap step
 * ---------------------------------------------------------------------------
 *
 * A window covers hay[i .. i+63] and nothing else. A start at offset l is only
 * decidable from this window if the whole needle fits inside it:
 *
 *     l + k - 1 <= 63   <=>   l <= 64 - k
 *
 * so only the low 64-k+1 bits of `starts` mean anything, and the result is
 * masked with ((1ull << (64 - k + 1)) - 1). (The AND-reduction already forces
 * those high bits to zero -- m_{k-1} >> (k-1) has its top k-1 bits clear, and
 * 64-(k-1) is exactly 64-k+1 -- so the mask is arithmetically redundant. It is
 * written out anyway because the *reason* those bits are junk is a property of
 * the window, not an accident of the last shift, and a reader checking the
 * bounds should not have to re-derive it.)
 *
 * The starts that were discarded are not lost: the loop advances by
 * 64 - (k - 1) bytes rather than 64, so the next window begins exactly at the
 * first offset this one could not decide. Consecutive windows therefore
 * overlap by k-1 bytes and together cover every start position exactly once in
 * increasing order. Combined with __builtin_ctzll picking the lowest set bit
 * within a window, the first nonzero result gives the LEFTMOST match overall.
 *
 * The loop condition is `i + 64 <= n`: the window must be entirely inside the
 * buffer, since both loads are unconditional. Note this is a stricter bound
 * than the AND-chain form's, so more of the haystack falls to the scalar tail
 * (up to 63 bytes rather than up to 31+k); the tail runs from wherever the
 * vector loop stopped, while i + k <= n, and is byte-for-byte the same
 * memcmp loop the other candidates use.
 *
 * Contract, identical to every other candidate: never reads at or past hay+n
 * nor before hay, returns NULL without touching memory when n < k.
 */

#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* One needle byte's equality bitmap over the 64-byte window held in (v0, v1).
 *
 * Bit p of the result is set iff window byte p equals the byte broadcast in c.
 * The (uint32_t) cast before widening is load-bearing: _mm256_movemask_epi8
 * returns int, and a set bit 31 would otherwise sign-extend and smear ones
 * across the whole upper half. */
static inline __attribute__((always_inline)) uint64_t
sa_eqmap(__m256i v0, __m256i v1, __m256i c)
{
    const uint64_t lo = (uint32_t)_mm256_movemask_epi8(_mm256_cmpeq_epi8(v0, c));
    const uint64_t hi = (uint32_t)_mm256_movemask_epi8(_mm256_cmpeq_epi8(v1, c));
    return lo | (hi << 32);
}

/* ---- "backfire", k = 8 ------------------------------------------------- */

/* Eight positions, eight DISTINCT bytes (b, a, c, k, f, i, r, e), so there is
 * nothing to dedup: eight broadcasts, eight equality bitmaps, seven shifted
 * ANDs. Window step is 64 - 7 = 57.
 *
 * Per 57 bytes of progress: 2 loads, 16 cmpeq, 16 movemask, 7 shift+AND. The
 * AND-chain matcher for the same needle spends 8 loads per 32 bytes -- about
 * 14 loads over the same span -- so this is a 7x reduction in load-port
 * pressure paid for with scalar ALU work that runs in parallel with it. */
const char *find_backfire_shiftand(const char *hay, size_t n);

const char *find_backfire_shiftand(const char *hay, size_t n)
{
    enum {
        K    = 8,
        STEP = 64 - (K - 1),          /* 57 */
    };
    /* Low 64-K+1 = 57 bits: the starts whose needle fits in the window. */
    const uint64_t start_mask = (1ull << (64 - K + 1)) - 1;

    if (n < (size_t)K) {
        return NULL;
    }

    /* All broadcasts hoisted: they are loop invariants and, being set1 of a
     * literal, GCC materialises each as a single vpbroadcastb from .rodata
     * outside the loop. */
    const __m256i cb = _mm256_set1_epi8('b');
    const __m256i ca = _mm256_set1_epi8('a');
    const __m256i cc = _mm256_set1_epi8('c');
    const __m256i ck = _mm256_set1_epi8('k');
    const __m256i cf = _mm256_set1_epi8('f');
    const __m256i ci = _mm256_set1_epi8('i');
    const __m256i cr = _mm256_set1_epi8('r');
    const __m256i ce = _mm256_set1_epi8('e');

    size_t i = 0;
    /* Highest byte touched is i+63; i+64<=n keeps the whole window in range. */
    for (; i + 64 <= n; i += STEP) {
        /* The window, loaded once and reused by all eight comparisons. */
        const __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i));
        const __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 32));

        /* One equality bitmap per needle position, over the SAME window. */
        const uint64_t m0 = sa_eqmap(v0, v1, cb);
        const uint64_t m1 = sa_eqmap(v0, v1, ca);
        const uint64_t m2 = sa_eqmap(v0, v1, cc);
        const uint64_t m3 = sa_eqmap(v0, v1, ck);
        const uint64_t m4 = sa_eqmap(v0, v1, cf);
        const uint64_t m5 = sa_eqmap(v0, v1, ci);
        const uint64_t m6 = sa_eqmap(v0, v1, cr);
        const uint64_t m7 = sa_eqmap(v0, v1, ce);

        /* Align each position's bitmap back to the START it constrains, then
         * intersect. Unconditional: no early exit, by design. */
        uint64_t starts = m0;
        starts &= m1 >> 1;
        starts &= m2 >> 2;
        starts &= m3 >> 3;
        starts &= m4 >> 4;
        starts &= m5 >> 5;
        starts &= m6 >> 6;
        starts &= m7 >> 7;
        starts &= start_mask;

        if (starts) {
            return hay + i + __builtin_ctzll(starts);
        }
    }

    /* Scalar tail over whatever the window loop could not cover, plus the
     * final k-1 undecided starts of the last window (the STEP advance leaves
     * i pointing at exactly the first of them). */
    for (; i + (size_t)K <= n; i++) {
        if (memcmp(hay + i, "backfire", K) == 0) {
            return hay + i;
        }
    }
    return NULL;
}

/* ---- "incomprehensible", k = 16 ---------------------------------------- */

/* i n c o m p r e h e n s i b l e
 * 0 1 2 3 4 5 6 7 8 9 ...
 *
 * Sixteen positions but only TWELVE distinct bytes: 'i' recurs at positions
 * 0 and 12, 'n' at 1 and 10, 'e' at 7, 9 and 15. The equality bitmap m_j
 * depends only on the window and on the BYTE, never on the position -- the
 * position enters solely through the shift applied afterwards. So a repeated
 * byte's bitmap is computed once and reused under a different shift:
 *
 *     m_i is used as (m_i >> 0) and (m_i >> 12)
 *     m_n is used as (m_n >> 1) and (m_n >> 10)
 *     m_e is used as (m_e >> 7), (m_e >> 9) and (m_e >> 15)
 *
 * That drops 32 cmpeq + 32 movemask down to 24 + 24 while the AND-reduction
 * stays at its full 15 terms. This is exactly the CSE a needle-to-code
 * generator performs: it keys the bitmap cache on the byte value, emits one
 * compare per distinct byte in the needle, and then emits one shift+AND per
 * position. The saving grows with needle redundancy -- an alphabet-limited
 * needle (DNA, hex, base64) caps the compare count at the alphabet size no
 * matter how long the needle is, which is the property that makes the scalar
 * form scale where the load-shifting form does not.
 *
 * Note that the shared-bitmap trick has NO analogue in the AND-chain form:
 * there the expensive part is the load at hay+i+j, which differs per position
 * even when the byte does not, so repeated bytes buy nothing.
 *
 * Window step is 64 - 15 = 49, and only the low 49 bits of the result name a
 * start whose sixteen bytes lie inside the window. */
const char *find_k16_shiftand(const char *hay, size_t n);

const char *find_k16_shiftand(const char *hay, size_t n)
{
    enum {
        K    = 16,
        STEP = 64 - (K - 1),          /* 49 */
    };
    const uint64_t start_mask = (1ull << (64 - K + 1)) - 1;

    if (n < (size_t)K) {
        return NULL;
    }

    /* Twelve broadcasts, one per DISTINCT needle byte, all hoisted. */
    const __m256i ci = _mm256_set1_epi8('i');
    const __m256i cn = _mm256_set1_epi8('n');
    const __m256i cc = _mm256_set1_epi8('c');
    const __m256i co = _mm256_set1_epi8('o');
    const __m256i cm = _mm256_set1_epi8('m');
    const __m256i cp = _mm256_set1_epi8('p');
    const __m256i cr = _mm256_set1_epi8('r');
    const __m256i ce = _mm256_set1_epi8('e');
    const __m256i ch = _mm256_set1_epi8('h');
    const __m256i cs = _mm256_set1_epi8('s');
    const __m256i cb = _mm256_set1_epi8('b');
    const __m256i cl = _mm256_set1_epi8('l');

    size_t i = 0;
    for (; i + 64 <= n; i += STEP) {
        const __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i));
        const __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 32));

        /* Twelve bitmaps, not sixteen. */
        const uint64_t mi = sa_eqmap(v0, v1, ci);
        const uint64_t mn = sa_eqmap(v0, v1, cn);
        const uint64_t mc = sa_eqmap(v0, v1, cc);
        const uint64_t mo = sa_eqmap(v0, v1, co);
        const uint64_t mm = sa_eqmap(v0, v1, cm);
        const uint64_t mp = sa_eqmap(v0, v1, cp);
        const uint64_t mr = sa_eqmap(v0, v1, cr);
        const uint64_t me = sa_eqmap(v0, v1, ce);
        const uint64_t mh = sa_eqmap(v0, v1, ch);
        const uint64_t ms = sa_eqmap(v0, v1, cs);
        const uint64_t mb = sa_eqmap(v0, v1, cb);
        const uint64_t ml = sa_eqmap(v0, v1, cl);

        /* Sixteen shifted terms drawn from those twelve bitmaps; the shift is
         * the needle position, so a reused bitmap appears at each position
         * where its byte occurs. */
        uint64_t starts = mi;          /*  0: i */
        starts &= mn >>  1;            /*  1: n */
        starts &= mc >>  2;            /*  2: c */
        starts &= mo >>  3;            /*  3: o */
        starts &= mm >>  4;            /*  4: m */
        starts &= mp >>  5;            /*  5: p */
        starts &= mr >>  6;            /*  6: r */
        starts &= me >>  7;            /*  7: e  (reuse 1/3) */
        starts &= mh >>  8;            /*  8: h */
        starts &= me >>  9;            /*  9: e  (reuse 2/3) */
        starts &= mn >> 10;            /* 10: n  (reuse 2/2) */
        starts &= ms >> 11;            /* 11: s */
        starts &= mi >> 12;            /* 12: i  (reuse 2/2) */
        starts &= mb >> 13;            /* 13: b */
        starts &= ml >> 14;            /* 14: l */
        starts &= me >> 15;            /* 15: e  (reuse 3/3) */
        starts &= start_mask;

        if (starts) {
            return hay + i + __builtin_ctzll(starts);
        }
    }

    for (; i + (size_t)K <= n; i++) {
        if (memcmp(hay + i, "incomprehensible", K) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
