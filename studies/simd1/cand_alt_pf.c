#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Prefiltered alternation: a cheap NECESSARY condition per block, then the
 * full per-branch evaluation only for blocks that survive it.
 *
 * These are the same patterns and the same matchers as cand_alt.c. The only
 * thing added is the filter; everything downstream of a surviving block is
 * byte-for-byte the same computation, so the two versions must agree on
 * every input. That is the whole safety argument, and it is worth stating
 * precisely before the code:
 *
 * THE CONDITION.  Let the branches be a_1..a_m with lengths k_1..k_m, and
 * let min_k = min k_a. For any offset j < min_k, EVERY branch has a member
 * set at position j -- the set of bytes that branch permits there (a single
 * byte for a literal position, a set for a character class). Define
 *
 *     unionclass_j = union over all branches a of members(a, j)
 *
 * If the alternation matches at position p, then some branch matches at p,
 * so hay[p+j] is in that branch's member set at j, hence in unionclass_j.
 * Contrapositive: hay[p+j] outside unionclass_j means NO branch can start at
 * p. So
 *
 *     F = AND over j < N of unionclass_j(v_j)        (N <= min_k)
 *
 * is a lane mask that is zero at every position where a match is impossible.
 * F = 0 for the whole block => no branch starts anywhere in the block =>
 * skip it. One vptest (_mm256_testz_si256) decides that for 32 positions.
 *
 * WHAT THE FILTER GIVES UP.  F is a per-position conjunction of UNIONS, not
 * a union of per-position conjunctions: it forgets which branch contributed
 * which byte. In "fred|bob|janet", the bytes 'f' then 'o' pass the depth-2
 * filter ('f' is in unionclass_0 via fred, 'o' is in unionclass_1 via bob)
 * even though no single branch permits that pair. The filter is therefore
 * one-sided -- it can say "definitely nothing here", never "definitely
 * something here". False positives cost only the full evaluation that the
 * unfiltered version would have done anyway; false negatives are impossible
 * by the argument above. Correctness never depends on the filter's
 * precision, only on its necessity.
 *
 * WHY IT IS NEARLY FREE -- the construction detail that makes or breaks
 * this.  The filter is NOT built from fresh comparisons. Every cmpeq in F
 * is a cmpeq the branch chains already have to perform: e_f = cmpeq(v0,'f')
 * is both a term of unionclass_0 and the first term of fred's AND-chain.
 * Those results are kept in named variables and reused verbatim when the
 * filter passes. So on a surviving block the filter's marginal cost is just
 * the OR tree plus one vptest -- a handful of cheap ALU ops on top of work
 * that was unavoidable. On a rejected block, the loads for v_N.. and every
 * chain's back half are never issued at all.
 *
 * Build the filter out of SEPARATE comparisons and this inverts: the
 * common case (rejection) still pays for them, and the uncommon case pays
 * for them twice. The reuse is the point, not an optimization detail.
 *
 * CHOOSING THE DEPTH N.  Deeper filters reject more (each extra position
 * multiplies the survival probability by roughly the density of that
 * position's union class) but consume more loads before the decision, and
 * they are capped at min_k -- position min_k does not exist for the
 * shortest branch, so there is no union class to test there. Note the
 * tension this creates in an alternation: one short branch caps the filter
 * depth for the entire pattern, and a branch set with a wide union at
 * position 0 (many distinct first bytes) filters poorly at depth 1. That is
 * exactly why pf1 and pf3 below exist as a pair -- same pattern, N = 1 vs.
 * N = 3, so the depth axis can be measured rather than argued about.
 *
 * The guard-page contract is unchanged from cand_alt.c: the vector bound is
 * still set by the LONGEST branch (v_{max_k-1} is loaded on surviving
 * blocks), the scalar tail is still bounded by the SHORTEST branch, and no
 * byte at or past hay+n, nor before hay, is ever read. Skipping loads makes
 * the filtered version touch strictly FEWER bytes than the unfiltered one,
 * so it cannot introduce an out-of-bounds read that cand_alt.c did not
 * already have.
 */

/* [0-9] as a lane mask -- the saturating-subtract range idiom, identical to
 * cand_alt.c's. Used here both as a branch term and as a member of the
 * union classes, which is the point of find_alt_mixed_pf below. */
static inline __m256i digit_mask(__m256i v, __m256i lo_zero, __m256i width9,
                                 __m256i zero)
{
    __m256i t = _mm256_sub_epi8(v, lo_zero);
    return _mm256_cmpeq_epi8(_mm256_subs_epu8(t, width9), zero);
}

/* fred|bob|janet|frederick with a DEPTH-1 filter.
 *
 * unionclass_0 = {'f'} u {'b'} u {'j'} u {'f'} = {'f','b','j'}, so
 *
 *     F = eq(v0,'f') | eq(v0,'b') | eq(v0,'j')
 *
 * and a block whose 32 first-bytes contain none of those three characters
 * is discarded having loaded exactly ONE vector. The three eq results are
 * the first terms of fred's, bob's and janet's chains respectively (and
 * frederick's, which continues fred's), so nothing computed for the filter
 * is thrown away when the block survives.
 *
 * This is the classic "first-byte prefilter" generalized from one literal
 * to a branch set: the union is over branches instead of being a singleton,
 * and it degrades gracefully -- more branches means a wider unionclass_0
 * and a higher survival rate, but never a wrong answer. */
const char *find_alt_names_pf1(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

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
    /* Bound unchanged from find_alt_names: v8 is loaded on surviving
     * blocks, so the loop must still stop where i+8+31 < n. */
    for (; i + 32 + 8 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));

        /* The three first-position compares, named because the branch
         * chains below consume them again. */
        __m256i e_f = _mm256_cmpeq_epi8(v0, bf); /* fred[0], frederick[0] */
        __m256i e_b = _mm256_cmpeq_epi8(v0, bb); /* bob[0] */
        __m256i e_j = _mm256_cmpeq_epi8(v0, bj); /* janet[0] */

        __m256i F = _mm256_or_si256(_mm256_or_si256(e_f, e_b), e_j);
        if (_mm256_testz_si256(F, F)) {
            continue; /* no branch can start anywhere in these 32 positions */
        }

        /* Survivor: the remaining eight shifted views, loaded only now. */
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));
        __m256i v6 = _mm256_loadu_si256((const __m256i *)(hay + i + 6));
        __m256i v7 = _mm256_loadu_si256((const __m256i *)(hay + i + 7));
        __m256i v8 = _mm256_loadu_si256((const __m256i *)(hay + i + 8));

        /* branch: fred -- starts from e_f, the filter's own term */
        __m256i mf = _mm256_and_si256(e_f, _mm256_cmpeq_epi8(v1, br));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v2, be));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v3, bd));

        /* branch: frederick, continuing the completed fred mask */
        __m256i mfk = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v4, be));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v5, br));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v6, bi));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v7, bc));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v8, bk));

        /* branch: bob -- starts from e_b */
        __m256i mb = _mm256_and_si256(e_b, _mm256_cmpeq_epi8(v1, bo));
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v2, bb));

        /* branch: janet -- starts from e_j */
        __m256i mj = _mm256_and_si256(e_j, _mm256_cmpeq_epi8(v1, ba));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v2, bn));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v3, be));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v4, bt));

        __m256i m = _mm256_or_si256(_mm256_or_si256(mf, mfk),
                                    _mm256_or_si256(mb, mj));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    /* Tail bounded by the SHORTEST branch, exactly as in find_alt_names --
     * the filter is a vector-loop device and has no business here, where
     * fewer than 32 positions remain and each is checked directly. */
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

/* fred|bob|janet|frederick with a DEPTH-3 filter -- the maximum legal depth
 * for this pattern, since min_k = 3 ("bob").
 *
 *     unionclass_0 = {'f','b','j'}      (fred/frederick, bob, janet)
 *     unionclass_1 = {'r','o','a'}
 *     unionclass_2 = {'e','b','n'}
 *     F = (e_f|e_b|e_j) & (e_r1|e_o1|e_a1) & (e_e2|e_b2|e_n2)
 *
 * Nine compares, all nine of which are terms the branch chains need:
 * fred/frederick supply the 'f','r','e' column, bob the 'b','o','b' column,
 * janet the 'j','a','n' column. When the filter passes, every one of the
 * nine registers is AND-ed straight into a branch mask; the chains then add
 * only their positions at offset >= 3.
 *
 * Depth 3 cannot be exceeded here without breaking necessity: "bob" has no
 * position 3, so there is no unionclass_3 that all branches satisfy, and
 * AND-ing in a fourth term built only from fred/janet/frederick would
 * reject blocks in which "bob" really does match. The filter's depth is a
 * property of the SHORTEST branch even though the loop bound is a property
 * of the longest -- the two ends of the length distribution constrain
 * different things, and conflating them is how a filtered alternation
 * starts missing matches. */
const char *find_alt_names_pf3(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

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
    for (; i + 32 + 8 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));

        /* position 0: fred/frederick, bob, janet */
        __m256i e_f  = _mm256_cmpeq_epi8(v0, bf);
        __m256i e_b  = _mm256_cmpeq_epi8(v0, bb);
        __m256i e_j  = _mm256_cmpeq_epi8(v0, bj);
        /* position 1 */
        __m256i e_r1 = _mm256_cmpeq_epi8(v1, br);
        __m256i e_o1 = _mm256_cmpeq_epi8(v1, bo);
        __m256i e_a1 = _mm256_cmpeq_epi8(v1, ba);
        /* position 2 */
        __m256i e_e2 = _mm256_cmpeq_epi8(v2, be);
        __m256i e_b2 = _mm256_cmpeq_epi8(v2, bb);
        __m256i e_n2 = _mm256_cmpeq_epi8(v2, bn);

        __m256i u0 = _mm256_or_si256(_mm256_or_si256(e_f, e_b), e_j);
        __m256i u1 = _mm256_or_si256(_mm256_or_si256(e_r1, e_o1), e_a1);
        __m256i u2 = _mm256_or_si256(_mm256_or_si256(e_e2, e_b2), e_n2);
        __m256i F  = _mm256_and_si256(_mm256_and_si256(u0, u1), u2);
        if (_mm256_testz_si256(F, F)) {
            continue; /* three loads consumed, six loads and 12 ANDs skipped */
        }

        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));
        __m256i v6 = _mm256_loadu_si256((const __m256i *)(hay + i + 6));
        __m256i v7 = _mm256_loadu_si256((const __m256i *)(hay + i + 7));
        __m256i v8 = _mm256_loadu_si256((const __m256i *)(hay + i + 8));

        /* Each chain's first three positions ARE the filter's terms; only
         * the tail of each chain is new work. */
        __m256i mf = _mm256_and_si256(_mm256_and_si256(e_f, e_r1), e_e2);
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v3, bd));

        __m256i mfk = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v4, be));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v5, br));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v6, bi));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v7, bc));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v8, bk));

        /* bob is exactly three positions long, so its mask is finished the
         * moment the filter terms are AND-ed together -- a branch of length
         * min_k adds no work at all beyond the filter. */
        __m256i mb = _mm256_and_si256(_mm256_and_si256(e_b, e_o1), e_b2);

        __m256i mj = _mm256_and_si256(_mm256_and_si256(e_j, e_a1), e_n2);
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v3, be));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v4, bt));

        __m256i m = _mm256_or_si256(_mm256_or_si256(mf, mfk),
                                    _mm256_or_si256(mb, mj));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

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

/* bob|[0-9]{5}|ted with a DEPTH-3 filter -- min_k = 3 ("bob", "ted"), so
 * depth 3 again, but now the union classes are MIXED-ENCODING.
 *
 *     unionclass_0 = {'b'} u [0-9] u {'t'}
 *     unionclass_1 = {'o'} u [0-9] u {'e'}
 *     unionclass_2 = {'b'} u [0-9] u {'d'}
 *
 * A union class does not have to be expressible as one idiom. Each member
 * set is computed however that set is cheapest -- cmpeq for the literal
 * bytes, the saturating-subtract range idiom for [0-9] -- and the results
 * are OR-ed, because all of them are just lane masks by the time they meet.
 * The filter is agnostic to how its inputs were produced; that is what lets
 * literal branches and class branches share one filter at all.
 *
 * The digit masks d0,d1,d2 illustrate the reuse rule as sharply as the
 * literals do: they are simultaneously three-fifths of the [0-9]{5} branch
 * and one term of each of the three union classes. Note also that a class
 * branch WIDENS the union -- [0-9] contributes ten members to every one of
 * the three positions -- so this filter is inherently less selective than
 * pf3's, which draws on three literal branches only. Selectivity is a
 * property of the pattern, not of the technique. */
const char *find_alt_mixed_pf(const char *hay, size_t n)
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
    /* Bound unchanged from find_alt_mixed: v4 is loaded on survivors. */
    for (; i + 32 + 4 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));

        /* class terms of the first three union classes, and simultaneously
         * positions 0..2 of the [0-9]{5} branch */
        __m256i d0 = digit_mask(v0, lo_zero, width9, zero);
        __m256i d1 = digit_mask(v1, lo_zero, width9, zero);
        __m256i d2 = digit_mask(v2, lo_zero, width9, zero);

        /* literal terms, and simultaneously the bob and ted chains */
        __m256i e_b0 = _mm256_cmpeq_epi8(v0, bb); /* bob[0] */
        __m256i e_t0 = _mm256_cmpeq_epi8(v0, bt); /* ted[0] */
        __m256i e_o1 = _mm256_cmpeq_epi8(v1, bo); /* bob[1] */
        __m256i e_e1 = _mm256_cmpeq_epi8(v1, be); /* ted[1] */
        __m256i e_b2 = _mm256_cmpeq_epi8(v2, bb); /* bob[2] */
        __m256i e_d2 = _mm256_cmpeq_epi8(v2, bd); /* ted[2] */

        __m256i u0 = _mm256_or_si256(_mm256_or_si256(e_b0, e_t0), d0);
        __m256i u1 = _mm256_or_si256(_mm256_or_si256(e_o1, e_e1), d1);
        __m256i u2 = _mm256_or_si256(_mm256_or_si256(e_b2, e_d2), d2);
        __m256i F  = _mm256_and_si256(_mm256_and_si256(u0, u1), u2);
        if (_mm256_testz_si256(F, F)) {
            continue;
        }

        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i d3 = digit_mask(v3, lo_zero, width9, zero);
        __m256i d4 = digit_mask(v4, lo_zero, width9, zero);

        /* branch: bob and branch: ted are complete from filter terms alone,
         * both being exactly min_k long. */
        __m256i mb = _mm256_and_si256(_mm256_and_si256(e_b0, e_o1), e_b2);
        __m256i mt = _mm256_and_si256(_mm256_and_si256(e_t0, e_e1), e_d2);

        /* branch: [0-9]{5} -- d0..d2 reused, only d3,d4 are new */
        __m256i md = _mm256_and_si256(_mm256_and_si256(d0, d1),
                                      _mm256_and_si256(d2, d3));
        md = _mm256_and_si256(md, d4);

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
