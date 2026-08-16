/* bcast_gen.h -- X-macro template for per-position broadcast matchers.
 *
 * This is the seed of a needle -> function generator: instead of hand-writing
 * one AVX2 kernel per needle, a caller instantiates the template once per
 * pattern and GCC specialises the generic body down to straight-line code.
 *
 * Instantiation protocol (repeatable within one translation unit):
 *
 *     #define GEN_FN    find_gen_wolf
 *     #define GEN_K     4
 *     #define GEN_SETS  { "w", "o", "l", "f" }
 *     #define GEN_FOLD  1              // optional, see below
 *     #include "bcast_gen.h"
 *
 * GEN_SETS lists, per pattern position, the members allowed at that position
 * as a string of 1..4 bytes; no member may be NUL. The header defines a
 * non-static
 *
 *     const char *GEN_FN(const char *hay, size_t n);
 *
 * returning the first position where every pattern position matches, or NULL.
 * It never reads at or past hay+n, never before hay, and returns NULL without
 * touching memory when n < GEN_K. All four macros are #undef'd on the way out.
 *
 * GEN_FOLD == 1 selects the case-reduced strategy: every set must then be a
 * single member and already lowercase-folded (the instantiation site
 * guarantees this), and the haystack block is folded A..Z -> a..z before a
 * single compare. Non-alphabetic bytes are left untouched, so digit and
 * punctuation positions still compare exactly -- this is deliberately not a
 * blind | 0x20.
 *
 * The generic engines below are always_inline and take k plus the set table by
 * value/pointer, so with a literal GEN_K and a file-scope-const set table GCC
 * at -O3 fully unrolls the position loop and constant-folds every set1_epi8
 * into an immediate broadcast.
 */

/* ---- one-time part: the generic engines ------------------------------- */
#ifndef BCAST_GEN_ONCE_H
#define BCAST_GEN_ONCE_H

#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

/* Member bytes are embedded in the table entry rather than pointed to.
 * With `static const char *const sets_[]` GCC never specialised the generic
 * loops: the pointer indirection hid the string contents, so the compiled
 * code re-broadcast members from memory and tested NUL terminators at
 * runtime (~3x slower). A flat char array in the initializer keeps the
 * bytes visible to constant propagation. String literals still initialise
 * it, so GEN_SETS instantiation syntax is unchanged. */
typedef char bg_set[8];

/* Mask of lanes in the 32-byte block at p whose byte is a member of set. */
static inline __attribute__((always_inline)) __m256i
bg_class_mask(const char *p, const char *set)
{
    const __m256i v = _mm256_loadu_si256((const __m256i *)p);
    __m256i m = _mm256_cmpeq_epi8(v, _mm256_set1_epi8(set[0]));
    /* 1..4 members; the trip count folds away once set[] is known. */
#pragma GCC unroll 4
    for (int t = 1; set[t] != '\0'; t++) {
        m = _mm256_or_si256(m, _mm256_cmpeq_epi8(v, _mm256_set1_epi8(set[t])));
    }
    return m;
}

/* Scalar membership test used by the tail loop. */
static inline __attribute__((always_inline)) int
bg_class_has(const char *set, unsigned char c)
{
    for (int t = 0; set[t] != '\0'; t++) {
        if ((unsigned char)set[t] == c) {
            return 1;
        }
    }
    return 0;
}

/* Fold A..Z to lowercase, leave every other byte alone. 'A'-1 and 'Z'+1 are
 * both positive, so the two signed compares bracket exactly 0x41..0x5A and
 * high-bit bytes (which compare as negative) are never touched. */
static inline __attribute__((always_inline)) __m256i
bg_fold_block(__m256i v)
{
    const __m256i is_upper =
        _mm256_and_si256(_mm256_cmpgt_epi8(v, _mm256_set1_epi8('A' - 1)),
                         _mm256_cmpgt_epi8(_mm256_set1_epi8('Z' + 1), v));
    return _mm256_or_si256(v, _mm256_and_si256(is_upper, _mm256_set1_epi8(0x20)));
}

static inline __attribute__((always_inline)) char
bg_fold_byte(char c)
{
    return (c >= 'A' && c <= 'Z') ? (char)(c | 0x20) : c;
}

/* Generic per-position broadcast AND-chain over byte classes. */
static inline __attribute__((always_inline)) const char *
bg_search(const char *hay, size_t n, int k, const bg_set *sets)
{
    if (n < (size_t)k) {
        return NULL;
    }

    size_t i = 0;
    /* Position j loads 32 bytes at hay+i+j, so the highest byte touched in an
     * iteration is i+(k-1)+31; i+32+(k-1)<=n keeps every load in [hay,hay+n). */
    for (; i + 32 + (size_t)(k - 1) <= n; i += 32) {
        __m256i m = bg_class_mask(hay + i, sets[0]);
#pragma GCC unroll 32
        for (int j = 1; j < k; j++) {
            m = _mm256_and_si256(m, bg_class_mask(hay + i + j, sets[j]));
            /* Long needles: stop loading once no lane can still match. Short
             * ones are cheaper without the test, and it folds away for them. */
            if (k > 4 && _mm256_testz_si256(m, m)) {
                break;
            }
        }
        /* A lane that survived all k positions is a confirmed match; an early
         * exit leaves m zero, so the same movemask covers both cases. */
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + (size_t)k <= n; i++) {
        int j = 0;
        for (; j < k; j++) {
            if (!bg_class_has(sets[j], (unsigned char)hay[i + j])) {
                break;
            }
        }
        if (j == k) {
            return hay + i;
        }
    }
    return NULL;
}

/* Generic case-folded variant: one member per position, already lowercase. */
static inline __attribute__((always_inline)) const char *
bg_search_fold(const char *hay, size_t n, int k, const bg_set *sets)
{
    if (n < (size_t)k) {
        return NULL;
    }

    size_t i = 0;
    /* Same bound as bg_search: highest byte touched is i+(k-1)+31. */
    for (; i + 32 + (size_t)(k - 1) <= n; i += 32) {
        __m256i m = _mm256_cmpeq_epi8(
            bg_fold_block(_mm256_loadu_si256((const __m256i *)(hay + i))),
            _mm256_set1_epi8(sets[0][0]));
#pragma GCC unroll 32
        for (int j = 1; j < k; j++) {
            const __m256i v =
                bg_fold_block(_mm256_loadu_si256((const __m256i *)(hay + i + j)));
            m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v, _mm256_set1_epi8(sets[j][0])));
            if (k > 4 && _mm256_testz_si256(m, m)) {
                break;
            }
        }
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + (size_t)k <= n; i++) {
        int j = 0;
        for (; j < k; j++) {
            if (bg_fold_byte(hay[i + j]) != sets[j][0]) {
                break;
            }
        }
        if (j == k) {
            return hay + i;
        }
    }
    return NULL;
}

#endif /* BCAST_GEN_ONCE_H */

/* ---- per-instantiation part ------------------------------------------- */
#if !defined(GEN_FN) || !defined(GEN_K) || !defined(GEN_SETS)
#error "bcast_gen.h requires GEN_FN, GEN_K and GEN_SETS to be defined"
#endif

const char *GEN_FN(const char *hay, size_t n);

const char *GEN_FN(const char *hay, size_t n)
{
    static const bg_set sets_[GEN_K] = GEN_SETS;
#if defined(GEN_FOLD) && GEN_FOLD
    return bg_search_fold(hay, n, GEN_K, sets_);
#else
    return bg_search(hay, n, GEN_K, sets_);
#endif
}

#undef GEN_FN
#undef GEN_K
#undef GEN_SETS
#ifdef GEN_FOLD
#undef GEN_FOLD
#endif
