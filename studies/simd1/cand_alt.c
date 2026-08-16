#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Alternation by OR-ing per-branch lane masks.
 *
 * The composition principle, which is what these three functions exist to
 * show:
 *
 *   1. Every alternative compiles to the same shape as a single literal:
 *      a per-position AND-chain over the block's shifted loads, producing a
 *      lane mask whose set bits mean "this branch STARTS here".
 *   2. The shifted loads v0..v{max_k-1} are a property of the BLOCK, not of
 *      any one branch, so they are hoisted once and shared by all branches.
 *      Alternation therefore costs extra compares, not extra loads: adding a
 *      branch no longer than the longest one adds zero memory traffic.
 *   3. The block result is the OR of the branch masks. movemask + ctz then
 *      gives the leftmost position at which ANY branch starts, which is
 *      exactly leftmost-match-start semantics for the whole alternation.
 *      One ctz settles the priority question for free -- no per-branch
 *      scan order, no separate "which branch won" merge step.
 *
 * Two consequences for the loop bounds:
 *
 *   - The vector loop is bounded by the LONGEST branch, since v{max_k-1} is
 *      loaded unconditionally: i + 32 + (max_k - 1) <= n.
 *   - The scalar tail is bounded by the SHORTEST branch, i + min_k <= n,
 *      and re-checks each branch a only where i + k_a <= n. A short branch
 *      can legitimately match in the last few bytes of the haystack, where
 *      the vector loop could not reach without over-reading for the long
 *      branch. Getting this wrong is the classic alternation bug: bounding
 *      the tail by max_k silently drops "bob" at the very end of a buffer.
 *
 * Broadcast constants are deduped: one register per DISTINCT needle byte,
 * shared across branches and across positions within a branch.
 */

/* [0-9] as a lane mask, via the saturating-subtract range idiom documented
 * in cand_range.c: shift so '0' maps to 0, saturating-subtract the range
 * width, and the result is zero exactly for bytes in range. */
static inline __m256i digit_mask(__m256i v, __m256i lo_zero, __m256i width9,
                                 __m256i zero)
{
    __m256i t = _mm256_sub_epi8(v, lo_zero);
    return _mm256_cmpeq_epi8(_mm256_subs_epu8(t, width9), zero);
}

/* fred|bob|janet|frederick -- four literal branches, lengths 4/3/5/9.
 * min_k = 3 (bob), max_k = 9 (frederick).
 *
 * Subexpression sharing: "fred" is a prefix of "frederick", so the
 * frederick chain starts from the already-computed fred mask and only adds
 * its five remaining positions. A real engine discovers this by building a
 * trie over the branch set and emitting one AND per trie EDGE rather than
 * one per (branch, position) pair; here it is done by hand to show the
 * shape.
 *
 * Note also that frederick's mask is necessarily a SUBSET of fred's -- any
 * position starting "frederick" also starts "fred" -- so under
 * position-only semantics OR-ing it in cannot change the answer, and an
 * engine would prune the subsumed branch outright. It is computed and
 * OR-ed anyway because the point of this function is the sharing pattern,
 * not the (pattern-specific) pruning opportunity.
 */
const char *find_alt_names(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

    /* One broadcast per distinct byte across ALL branches: 'e' is needed at
     * fred[2], frederick[4] and janet[3] but is broadcast once; likewise
     * 'r' (fred[1], frederick[5]) and 'b' (bob[0], bob[2]). */
    const __m256i bf = _mm256_set1_epi8('f');
    const __m256i br = _mm256_set1_epi8('r');
    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bd = _mm256_set1_epi8('d');
    const __m256i bi = _mm256_set1_epi8('i');
    const __m256i bc = _mm256_set1_epi8('c');
    const __m256i bk = _mm256_set1_epi8('k');
    const __m256i bb = _mm256_set1_epi8('b');
    const __m256i bo = _mm256_set1_epi8('o');
    const __m256i bj = _mm256_set1_epi8('j');
    const __m256i ba = _mm256_set1_epi8('a');
    const __m256i bn = _mm256_set1_epi8('n');
    const __m256i bt = _mm256_set1_epi8('t');

    size_t i = 0;
    /* Highest byte touched this iteration is i+8+31, from the longest
     * branch's v8; i+32+8<=n keeps every load inside [hay, hay+n). */
    for (; i + 32 + 8 <= n; i += 32) {
        /* Loads are hoisted out of the branches: nine shifted views of the
         * same block, shared by all four alternatives. */
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));
        __m256i v6 = _mm256_loadu_si256((const __m256i *)(hay + i + 6));
        __m256i v7 = _mm256_loadu_si256((const __m256i *)(hay + i + 7));
        __m256i v8 = _mm256_loadu_si256((const __m256i *)(hay + i + 8));

        /* branch: fred */
        __m256i mf = _mm256_cmpeq_epi8(v0, bf);
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v1, br));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v2, be));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v3, bd));

        /* branch: frederick, continuing the completed fred mask */
        __m256i mfk = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v4, be));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v5, br));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v6, bi));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v7, bc));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v8, bk));

        /* branch: bob */
        __m256i mb = _mm256_cmpeq_epi8(v0, bb);
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v1, bo));
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v2, bb));

        /* branch: janet */
        __m256i mj = _mm256_cmpeq_epi8(v0, bj);
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v1, ba));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v2, bn));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v3, be));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v4, bt));

        /* The alternation itself: one OR tree, then one ctz. */
        __m256i m = _mm256_or_si256(_mm256_or_si256(mf, mfk),
                                    _mm256_or_si256(mb, mj));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    /* Tail bounded by the SHORTEST branch; each branch is length-guarded
     * individually. Branch order within one i is irrelevant -- the position
     * decides the answer, not which alternative reports it -- so any hit at
     * i returns immediately. */
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

/* bob|[0-9]{5}|ted -- literal branches mixed with a character-class branch,
 * lengths 3/5/3. min_k = 3, max_k = 5.
 *
 * The class branch is not special: {5} unrolls to five class tests at
 * offsets 0..4, each a lane mask, AND-ed together exactly like the literal
 * branches' cmpeq chains. Literal and class positions compose in the same
 * AND-chain because both produce a lane mask; only the way the mask is
 * computed differs (cmpeq vs. the range idiom). */
const char *find_alt_mixed(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branches are "bob" and "ted" */
        return NULL;
    }

    const __m256i zero    = _mm256_setzero_si256();
    const __m256i lo_zero = _mm256_set1_epi8('0');
    const __m256i width9  = _mm256_set1_epi8(9); /* '9' - '0' */
    const __m256i bb      = _mm256_set1_epi8('b');
    const __m256i bo      = _mm256_set1_epi8('o');
    const __m256i bt      = _mm256_set1_epi8('t');
    const __m256i be      = _mm256_set1_epi8('e');
    const __m256i bd      = _mm256_set1_epi8('d');

    size_t i = 0;
    /* Highest byte touched this iteration is i+4+31, from the longest
     * branch's v4; i+32+4<=n keeps every load inside [hay, hay+n). */
    for (; i + 32 + 4 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));

        /* branch: [0-9]{5} */
        __m256i d0 = digit_mask(v0, lo_zero, width9, zero);
        __m256i d1 = digit_mask(v1, lo_zero, width9, zero);
        __m256i d2 = digit_mask(v2, lo_zero, width9, zero);
        __m256i d3 = digit_mask(v3, lo_zero, width9, zero);
        __m256i d4 = digit_mask(v4, lo_zero, width9, zero);
        __m256i md = _mm256_and_si256(_mm256_and_si256(d0, d1),
                                      _mm256_and_si256(d2, d3));
        md = _mm256_and_si256(md, d4);

        /* branch: bob -- same shared v0..v2 the class branch used */
        __m256i mb = _mm256_cmpeq_epi8(v0, bb);
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v1, bo));
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v2, bb));

        /* branch: ted */
        __m256i mt = _mm256_cmpeq_epi8(v0, bt);
        mt = _mm256_and_si256(mt, _mm256_cmpeq_epi8(v1, be));
        mt = _mm256_and_si256(mt, _mm256_cmpeq_epi8(v2, bd));

        __m256i m = _mm256_or_si256(md, _mm256_or_si256(mb, mt));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 3 <= n; i++) {
        if (memcmp(hay + i, "bob", 3) == 0) {
            return hay + i;
        }
        if (memcmp(hay + i, "ted", 3) == 0) {
            return hay + i;
        }
        if (i + 5 <= n) {
            char c0 = hay[i], c1 = hay[i + 1], c2 = hay[i + 2];
            char c3 = hay[i + 3], c4 = hay[i + 4];
            if (c0 >= '0' && c0 <= '9' && c1 >= '0' && c1 <= '9' &&
                c2 >= '0' && c2 <= '9' && c3 >= '0' && c3 <= '9' &&
                c4 >= '0' && c4 <= '9') {
                return hay + i;
            }
        }
    }
    return NULL;
}

/* bob|[0-9]+|ted -- the unbounded-repetition branch is FREE.
 *
 * The contract here is leftmost match START only: the caller wants the
 * position, never the extent. Under those semantics [0-9]+ starts at i if
 * and only if hay[i] is a digit -- the repetition can always be satisfied
 * by the single first byte, and consuming more digits moves the END, which
 * nobody observes. So the whole branch compiles to ONE character-class
 * position: no inner loop, no counter, no backtracking, and no dependence
 * on how long the digit run actually is. '+' costs exactly what [0-9]
 * costs.
 *
 * This also shrinks the alternation's min_k to 1, which is what makes the
 * tail-bound rule above matter: the vector loop still stops max_k-1 = 2
 * bytes early for "bob"/"ted", but a lone trailing digit is a real match
 * and the scalar tail must run all the way to i + 1 <= n to find it. */
const char *find_alt_plus(const char *hay, size_t n)
{
    if (n < 1) { /* shortest branch is one digit */
        return NULL;
    }

    const __m256i zero    = _mm256_setzero_si256();
    const __m256i lo_zero = _mm256_set1_epi8('0');
    const __m256i width9  = _mm256_set1_epi8(9); /* '9' - '0' */
    const __m256i bb      = _mm256_set1_epi8('b');
    const __m256i bo      = _mm256_set1_epi8('o');
    const __m256i bt      = _mm256_set1_epi8('t');
    const __m256i be      = _mm256_set1_epi8('e');
    const __m256i bd      = _mm256_set1_epi8('d');

    size_t i = 0;
    /* Highest byte touched this iteration is i+2+31, from the longest
     * branch's v2; i+32+2<=n keeps every load inside [hay, hay+n). */
    for (; i + 32 + 2 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));

        /* branch: [0-9]+ -- a single class test on v0, nothing more */
        __m256i md = digit_mask(v0, lo_zero, width9, zero);

        /* branch: bob */
        __m256i mb = _mm256_cmpeq_epi8(v0, bb);
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v1, bo));
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v2, bb));

        /* branch: ted */
        __m256i mt = _mm256_cmpeq_epi8(v0, bt);
        mt = _mm256_and_si256(mt, _mm256_cmpeq_epi8(v1, be));
        mt = _mm256_and_si256(mt, _mm256_cmpeq_epi8(v2, bd));

        __m256i m = _mm256_or_si256(md, _mm256_or_si256(mb, mt));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 1 <= n; i++) {
        char c0 = hay[i];
        if (c0 >= '0' && c0 <= '9') { /* k = 1, never length-guarded away */
            return hay + i;
        }
        if (i + 3 <= n) {
            if (memcmp(hay + i, "bob", 3) == 0 ||
                memcmp(hay + i, "ted", 3) == 0) {
                return hay + i;
            }
        }
    }
    return NULL;
}
