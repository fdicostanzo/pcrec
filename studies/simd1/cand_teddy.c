#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Two prefilters for an EIGHT-branch literal alternation:
 *
 *     fred | bob | janet | frederick | alice | megan | carol | dave
 *
 * lengths 4, 3, 5, 9, 5, 5, 5, 4 -- so min_k = 3 ("bob") and max_k = 9
 * ("frederick"). As always the two ends of the length distribution
 * constrain different things: min_k caps how DEEP a necessary-condition
 * filter may look, max_k sets the vector loop bound and the largest read
 * done during verification.
 *
 * The point of the file is to put two different prefilter architectures on
 * the same pattern:
 *
 *   find_alt8_union -- the cand_alt_pf.c idea (a per-position UNION class,
 *       AND-ed across positions) scaled from 3 branches to 8, with each
 *       union class encoded as a shufti nibble table instead of an OR chain
 *       of cmpeqs. Position-wise: it answers "could ANY branch start here",
 *       having forgotten which branch wanted which byte.
 *
 *   find_alt8_teddy -- Hyperscan's Teddy, simplified. Same shuffle-based
 *       machinery, but each table entry carries a BITMASK OF BRANCHES rather
 *       than a yes/no membership bit, and the per-position results are AND-ed
 *       as bitmasks. Position-wise it answers "WHICH branches could start
 *       here", which is strictly more information for the same instruction
 *       count -- and that information is what lets the survivor path verify
 *       one or two branches instead of evaluating all eight.
 *
 * Both are one-sided in the usual way: they may say "maybe" where there is
 * no match (verification then rejects), never "no" where there is one.
 *
 * BOUNDS CONTRACT (guard-page enforced, identical in both functions):
 *   - fn(hay, n) returns the leftmost position where ANY branch matches, or
 *     NULL; n < 3 returns NULL without touching hay.
 *   - the vector loop runs while i + 32 + 8 <= n, so every load in the block
 *     -- including hay+i+8 in the union version's evaluation and every
 *     verification memcmp of up to max_k = 9 bytes at hay+i+31 -- stays
 *     inside [hay, hay+n). (i+31+8 = i+39 <= n-1 is exactly the bound.)
 *   - the scalar tail resumes at the loop's exit i and runs while i + 3 <= n
 *     (min_k), checking each branch only when i + k_b <= n.
 *   - nothing is ever read at or past hay+n, nor before hay.
 */

/* The branch set, hardcoded once and shared by every verification path in
 * this file. Index order IS the Teddy bucket order below: bucket bit b is
 * 1 << b, so alt8_str[b] / alt8_len[b] decode a bucket bit directly. */
static const char *const alt8_str[8] = {
    "fred", "bob", "janet", "frederick", "alice", "megan", "carol", "dave",
};
static const size_t alt8_len[8] = { 4, 3, 5, 9, 5, 5, 5, 4 };

/* ------------------------------------------------------------------ */
/* 1. Union-class prefilter, depth 3, shufti-encoded                   */
/* ------------------------------------------------------------------ */

/* The three union classes, read off the branch list column by column.
 * Column j of the eight branches, then deduplicated:
 *
 *   pos 0:  fred f | bob b | janet j | frederick f | alice a | megan m
 *           | carol c | dave d          ->  C0 = {f,b,j,a,m,c,d}   (7)
 *   pos 1:  fred r | bob o | janet a | frederick r | alice l | megan e
 *           | carol a | dave a          ->  C1 = {r,o,a,l,e}       (5)
 *   pos 2:  fred e | bob b | janet n | frederick e | alice i | megan g
 *           | carol r | dave v          ->  C2 = {e,b,n,i,g,r,v}   (7)
 *
 * F = C0(v0) & C1(v1) & C2(v2) is zero at every position where no branch can
 * begin, so testz(F) skipping the block is safe. Depth 3 is the ceiling:
 * "bob" has no position 3, so any deeper term would reject blocks where bob
 * genuinely matches.
 *
 * WHY SHUFTI AND NOT OR-CHAINS HERE. cand_alt_pf.c builds its union classes
 * from cmpeqs that the branch chains then reuse verbatim, which is what makes
 * that filter nearly free. At three branches the classes are 3 members wide
 * and that accounting is unbeatable. At eight branches the same construction
 * costs 7+5+7 = 19 cmpeqs plus 16 ORs plus 2 ANDs = 37 ops on EVERY block,
 * including the overwhelming majority that are rejected. Shufti prices each
 * class at a flat 8 ops (mask, shuffle, shift, mask, shuffle, and, cmpeq,
 * xor) regardless of how many members it has: 24 + 2 ANDs = 26 ops per block,
 * and it does not grow as branches are added -- only the tables change.
 *
 * The trade is real and worth naming: the shufti results are NOT per-branch
 * compares, so a surviving block cannot reuse them and must issue all its
 * cmpeqs fresh. Rejection is the common case in a prefilter, so paying more
 * on survivors to pay less on rejects is the right side of the trade -- but
 * it is a trade, not a free win, and it inverts if the filter passes often.
 *
 * TABLE DERIVATION, by hand, byte by byte. Every member is lowercase ASCII,
 * so every high nibble is 6 or 7; bytes >= 0x80 land in high nibbles 8..15
 * where the hi table is zero, so they are non-members for free.
 *
 *   C0: f=0x66 lo=6 hi=6 | b=0x62 lo=2 hi=6 | j=0x6a lo=a hi=6
 *       a=0x61 lo=1 hi=6 | m=0x6d lo=d hi=6 | c=0x63 lo=3 hi=6
 *       d=0x64 lo=4 hi=6
 *     lo_c0[1]=lo_c0[2]=lo_c0[3]=lo_c0[4]=lo_c0[6]=lo_c0[a]=lo_c0[d]=0x40
 *     hi_c0[6]=0x40, all else 0.
 *     Exact: a byte passes iff hi==6 and lo in {1,2,3,4,6,a,d}, i.e. iff it
 *     is one of 0x61,0x62,0x63,0x64,0x66,0x6a,0x6d = a,b,c,d,f,j,m.
 *
 *   C1: r=0x72 lo=2 hi=7 | o=0x6f lo=f hi=6 | a=0x61 lo=1 hi=6
 *       l=0x6c lo=c hi=6 | e=0x65 lo=5 hi=6
 *     lo_c1[1]=0x40 (a), lo_c1[2]=0x80 (r), lo_c1[5]=0x40 (e),
 *     lo_c1[c]=0x40 (l), lo_c1[f]=0x40 (o); hi_c1[6]=0x40, hi_c1[7]=0x80.
 *     Exact: 'b'=0x62 gets lo 0x80 & hi 0x40 = 0; 'q'=0x71 gets 0x40 & 0x80
 *     = 0. The two high-nibble bits keep the 6-row and the 7-row disjoint.
 *
 *   C2: e=0x65 lo=5 hi=6 | b=0x62 lo=2 hi=6 | n=0x6e lo=e hi=6
 *       i=0x69 lo=9 hi=6 | g=0x67 lo=7 hi=6 | r=0x72 lo=2 hi=7
 *       v=0x76 lo=6 hi=7
 *     lo_c2[2]=0x40|0x80=0xc0 (b and r share low nibble 2),
 *     lo_c2[5]=0x40 (e), lo_c2[6]=0x80 (v), lo_c2[7]=0x40 (g),
 *     lo_c2[9]=0x40 (i), lo_c2[e]=0x40 (n); hi_c2[6]=0x40, hi_c2[7]=0x80.
 *     Exact: 'f'=0x66 gets lo 0x80 & hi 0x40 = 0; 'u'=0x75 gets 0x40 & 0x80
 *     = 0; 'b' keeps only 0x40 and 'r' only 0x80 out of the shared 0xc0.
 */
static const uint8_t lo_c0[16] = {
    0x00, 0x40, 0x40, 0x40, 0x40, 0x00, 0x40, 0x00,
    0x00, 0x00, 0x40, 0x00, 0x00, 0x40, 0x00, 0x00,
};
static const uint8_t hi_c0[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
static const uint8_t lo_c1[16] = {
    0x00, 0x40, 0x80, 0x00, 0x00, 0x40, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x40,
};
static const uint8_t hi_c1[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x80,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
static const uint8_t lo_c2[16] = {
    0x00, 0x00, 0xc0, 0x00, 0x00, 0x40, 0x80, 0x40,
    0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00,
};
static const uint8_t hi_c2[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x80,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

/* One shufti class test, returning a full 0x00/0xff lane mask so the three
 * classes can be AND-ed like any other lane mask.
 *
 * The high nibble of every byte in one op: shift right by 4 in 16-bit lanes,
 * then mask to 4 bits -- the bits that leak in from the neighbouring byte
 * land above the mask (see cand_shufti.c). The AND of the two lookups is
 * nonzero exactly when some member shares both nibbles with the byte; the
 * xor turns "cmpeq(t,0)" (a NOT-member mask) into a member mask. */
static inline __m256i shufti_class(__m256i v, __m256i lo_v, __m256i hi_v,
                                   __m256i nib, __m256i zero, __m256i ones)
{
    __m256i lo = _mm256_shuffle_epi8(lo_v, _mm256_and_si256(v, nib));
    __m256i hn = _mm256_and_si256(_mm256_srli_epi16(v, 4), nib);
    __m256i hi = _mm256_shuffle_epi8(hi_v, hn);
    __m256i t  = _mm256_and_si256(lo, hi);
    return _mm256_xor_si256(_mm256_cmpeq_epi8(t, zero), ones);
}

const char *find_alt8_union(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

    /* pshufb shuffles within each 128-bit lane independently, so both lanes
     * need an identical copy of every 16-byte table. */
    const __m256i lo_c0_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)lo_c0));
    const __m256i hi_c0_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)hi_c0));
    const __m256i lo_c1_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)lo_c1));
    const __m256i hi_c1_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)hi_c1));
    const __m256i lo_c2_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)lo_c2));
    const __m256i hi_c2_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)hi_c2));

    const __m256i nib  = _mm256_set1_epi8(0x0f);
    const __m256i zero = _mm256_setzero_si256();
    const __m256i ones = _mm256_set1_epi8((char)0xff);

    const __m256i ba = _mm256_set1_epi8('a');
    const __m256i bb = _mm256_set1_epi8('b');
    const __m256i bc = _mm256_set1_epi8('c');
    const __m256i bd = _mm256_set1_epi8('d');
    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bf = _mm256_set1_epi8('f');
    const __m256i bg = _mm256_set1_epi8('g');
    const __m256i bi = _mm256_set1_epi8('i');
    const __m256i bj = _mm256_set1_epi8('j');
    const __m256i bk = _mm256_set1_epi8('k');
    const __m256i bl = _mm256_set1_epi8('l');
    const __m256i bm = _mm256_set1_epi8('m');
    const __m256i bn = _mm256_set1_epi8('n');
    const __m256i bo = _mm256_set1_epi8('o');
    const __m256i br = _mm256_set1_epi8('r');
    const __m256i bt = _mm256_set1_epi8('t');
    const __m256i bv = _mm256_set1_epi8('v');

    size_t i = 0;
    /* v8 is loaded on surviving blocks (frederick[8]), so the bound is set
     * by max_k = 9, not by the filter depth. */
    for (; i + 32 + 8 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));

        __m256i u0 = shufti_class(v0, lo_c0_v, hi_c0_v, nib, zero, ones);
        __m256i u1 = shufti_class(v1, lo_c1_v, hi_c1_v, nib, zero, ones);
        __m256i u2 = shufti_class(v2, lo_c2_v, hi_c2_v, nib, zero, ones);
        __m256i F  = _mm256_and_si256(_mm256_and_si256(u0, u1), u2);
        if (_mm256_testz_si256(F, F)) {
            continue; /* no branch can start at any of these 32 positions */
        }

        /* Survivor: the six deeper views, and the full eight-branch
         * evaluation. The filter's outputs are membership masks over unions,
         * not per-branch compares, so none of them can be folded into a
         * chain -- every cmpeq below is new work. That is the cost side of
         * the shufti trade described above. */
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));
        __m256i v6 = _mm256_loadu_si256((const __m256i *)(hay + i + 6));
        __m256i v7 = _mm256_loadu_si256((const __m256i *)(hay + i + 7));
        __m256i v8 = _mm256_loadu_si256((const __m256i *)(hay + i + 8));

        /* fred: f r e d */
        __m256i mf = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bf),
                                      _mm256_cmpeq_epi8(v1, br));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v2, be));
        mf = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v3, bd));

        /* frederick: fred's completed mask is its four-byte prefix, so the
         * chain continues rather than restarting. */
        __m256i mfk = _mm256_and_si256(mf, _mm256_cmpeq_epi8(v4, be));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v5, br));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v6, bi));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v7, bc));
        mfk = _mm256_and_si256(mfk, _mm256_cmpeq_epi8(v8, bk));

        /* bob: b o b */
        __m256i mb = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bb),
                                      _mm256_cmpeq_epi8(v1, bo));
        mb = _mm256_and_si256(mb, _mm256_cmpeq_epi8(v2, bb));

        /* janet: j a n e t */
        __m256i mj = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bj),
                                      _mm256_cmpeq_epi8(v1, ba));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v2, bn));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v3, be));
        mj = _mm256_and_si256(mj, _mm256_cmpeq_epi8(v4, bt));

        /* alice: a l i c e */
        __m256i ma = _mm256_and_si256(_mm256_cmpeq_epi8(v0, ba),
                                      _mm256_cmpeq_epi8(v1, bl));
        ma = _mm256_and_si256(ma, _mm256_cmpeq_epi8(v2, bi));
        ma = _mm256_and_si256(ma, _mm256_cmpeq_epi8(v3, bc));
        ma = _mm256_and_si256(ma, _mm256_cmpeq_epi8(v4, be));

        /* megan: m e g a n */
        __m256i mm = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bm),
                                      _mm256_cmpeq_epi8(v1, be));
        mm = _mm256_and_si256(mm, _mm256_cmpeq_epi8(v2, bg));
        mm = _mm256_and_si256(mm, _mm256_cmpeq_epi8(v3, ba));
        mm = _mm256_and_si256(mm, _mm256_cmpeq_epi8(v4, bn));

        /* carol: c a r o l */
        __m256i mc = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bc),
                                      _mm256_cmpeq_epi8(v1, ba));
        mc = _mm256_and_si256(mc, _mm256_cmpeq_epi8(v2, br));
        mc = _mm256_and_si256(mc, _mm256_cmpeq_epi8(v3, bo));
        mc = _mm256_and_si256(mc, _mm256_cmpeq_epi8(v4, bl));

        /* dave: d a v e */
        __m256i mv = _mm256_and_si256(_mm256_cmpeq_epi8(v0, bd),
                                      _mm256_cmpeq_epi8(v1, ba));
        mv = _mm256_and_si256(mv, _mm256_cmpeq_epi8(v2, bv));
        mv = _mm256_and_si256(mv, _mm256_cmpeq_epi8(v3, be));

        __m256i m = _mm256_or_si256(
            _mm256_or_si256(_mm256_or_si256(mf, mfk), _mm256_or_si256(mb, mj)),
            _mm256_or_si256(_mm256_or_si256(ma, mm), _mm256_or_si256(mc, mv)));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            /* Lowest set bit is the lowest lane, hence the leftmost match in
             * this block; blocks are visited in ascending order. */
            return hay + i + __builtin_ctz(mask);
        }
    }

    /* Tail bounded by the SHORTEST branch; each branch is checked only where
     * it fits. Order within a position is irrelevant -- the answer is a
     * position, not a branch identity. */
    for (; i + 3 <= n; i++) {
        for (int b = 0; b < 8; b++) {
            if (i + alt8_len[b] <= n &&
                memcmp(hay + i, alt8_str[b], alt8_len[b]) == 0) {
                return hay + i;
            }
        }
    }
    return NULL;
}

/* ------------------------------------------------------------------ */
/* 2. Teddy, depth 2, one bucket per branch                            */
/* ------------------------------------------------------------------ */

/* TEDDY, THE MECHANISM.
 *
 * Teddy replaces "is this byte in the union class" with "which branches want
 * this byte HERE". Branches are assigned to buckets; with only 8 branches
 * every branch gets its own bucket, so bucket bit b == branch b == 1 << b
 * and there is no bucket sharing to reason about (Hyperscan shares buckets
 * when it has more literals than bits, at the price of extra verification).
 *
 * For each offset o in {0,1} there are two 16-byte tables:
 *
 *     lo_o[l] = OR of (1 << b) over branches b with (branch_b[o] & 15) == l
 *     hi_o[h] = OR of (1 << b) over branches b with (branch_b[o] >> 4) == h
 *
 * and for a vector of haystack bytes v,
 *
 *     bucketmask_o(v) = shuffle(lo_o, v & 0x0f) & shuffle(hi_o, (v >> 4) & 0x0f)
 *
 * produces, per lane, a BYTE of candidate bucket bits: bit b survives only if
 * branch b's offset-o byte agrees with this byte in BOTH nibbles. Nibbles do
 * not determine a byte on their own, so in general a byte can pick up bits
 * from branches it does not actually match -- two branches whose offset-o
 * bytes share a low nibble with one and a high nibble with the other create a
 * spurious bit. Those false positives are the price of the flat instruction
 * count and are removed by verification, never by the filter.
 *
 * Then
 *
 *     cand = bucketmask_0(v0) & bucketmask_1(v1)      (v1 = load at hay+i+1)
 *
 * so bit b of lane l is set only if branch b's first two bytes both agree
 * with hay[i+l], hay[i+l+1]. Every branch here is at least 3 bytes long, so
 * this is a necessary condition for every branch: cand == 0 for the whole
 * block means no branch starts anywhere in it, and testz skips it.
 *
 * The difference from find_alt8_union above is entirely in what survives.
 * The union filter says "something might start in this block" and pays for
 * all eight branch chains to find out. Teddy says "branch 5 might start at
 * lane 17" and pays for one memcmp of five bytes. Same shuffles, same AND,
 * same testz -- but the bits carry identity, and identity is what turns
 * verification from vector-width work into a couple of scalar compares.
 *
 * TABLE DERIVATION, by hand.
 *   bucket bits: fred=0x01 bob=0x02 janet=0x04 frederick=0x08
 *                alice=0x10 megan=0x20 carol=0x40 dave=0x80
 *
 *   offset 0 bytes: f(fred) b(bob) j(janet) f(frederick) a(alice) m(megan)
 *                   c(carol) d(dave)
 *     f=0x66 lo=6 hi=6 -> bits 0x01|0x08 = 0x09 (fred and frederick share it)
 *     b=0x62 lo=2 hi=6 -> 0x02
 *     j=0x6a lo=a hi=6 -> 0x04
 *     a=0x61 lo=1 hi=6 -> 0x10
 *     m=0x6d lo=d hi=6 -> 0x20
 *     c=0x63 lo=3 hi=6 -> 0x40
 *     d=0x64 lo=4 hi=6 -> 0x80
 *   giving lo_0[1]=0x10, lo_0[2]=0x02, lo_0[3]=0x40, lo_0[4]=0x80,
 *   lo_0[6]=0x09, lo_0[a]=0x04, lo_0[d]=0x20, rest 0; and since every
 *   offset-0 byte has high nibble 6, hi_0[6] = 0xff (all eight buckets) and
 *   every other hi_0 entry is 0.
 *
 *   offset 1 bytes: r(fred) o(bob) a(janet) r(frederick) l(alice) e(megan)
 *                   a(carol) a(dave)
 *     r=0x72 lo=2 hi=7 -> 0x01|0x08 = 0x09
 *     o=0x6f lo=f hi=6 -> 0x02
 *     a=0x61 lo=1 hi=6 -> janet 0x04 | carol 0x40 | dave 0x80 = 0xc4
 *     l=0x6c lo=c hi=6 -> 0x10
 *     e=0x65 lo=5 hi=6 -> 0x20
 *   giving lo_1[1]=0xc4, lo_1[2]=0x09, lo_1[5]=0x20, lo_1[c]=0x10,
 *   lo_1[f]=0x02, rest 0; hi_1[6] = 0x02|0x04|0x10|0x20|0x40|0x80 = 0xf6
 *   (o,a,l,e,a,a), hi_1[7] = 0x01|0x08 = 0x09 (both r's), rest 0.
 *
 *   Cross-check of the collision behaviour, which is the part worth getting
 *   wrong loudly rather than quietly: 'b'=0x62 at offset 1 picks lo_1[2]=0x09
 *   and hi_1[6]=0xf6, AND = 0x00 -- correct, no branch has 'b' at offset 1
 *   even though 'r' shares its low nibble. 'q'=0x71 picks lo_1[1]=0xc4 and
 *   hi_1[7]=0x09, AND = 0x00 -- correct. 'a'=0x61 picks 0xc4 & 0xf6 = 0xc4 =
 *   janet|carol|dave, exactly right. For THIS branch set the two nibble rows
 *   happen to stay disjoint, so cand carries no spurious bits at all and its
 *   set bits are precisely the branches whose 2-byte prefix matches; the
 *   verification below does not rely on that and would be correct anyway.
 *
 *   Bytes >= 0x80 have high nibble 8..15, where both hi tables are zero, so
 *   they contribute no bucket bits.
 */
static const uint8_t teddy_lo0[16] = {
    0x00, 0x10, 0x02, 0x40, 0x80, 0x00, 0x09, 0x00,
    0x00, 0x00, 0x04, 0x00, 0x00, 0x20, 0x00, 0x00,
};
static const uint8_t teddy_hi0[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
static const uint8_t teddy_lo1[16] = {
    0x00, 0xc4, 0x09, 0x00, 0x00, 0x20, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x02,
};
static const uint8_t teddy_hi1[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf6, 0x09,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

/* Per-lane byte of candidate bucket bits. Unlike shufti_class this returns
 * the raw AND of the two lookups, not a 0/0xff mask -- the individual bits
 * are the whole point. */
static inline __m256i bucketmask(__m256i v, __m256i lo_v, __m256i hi_v,
                                 __m256i nib)
{
    __m256i lo = _mm256_shuffle_epi8(lo_v, _mm256_and_si256(v, nib));
    __m256i hn = _mm256_and_si256(_mm256_srli_epi16(v, 4), nib);
    __m256i hi = _mm256_shuffle_epi8(hi_v, hn);
    return _mm256_and_si256(lo, hi);
}

const char *find_alt8_teddy(const char *hay, size_t n)
{
    if (n < 3) { /* shortest branch is "bob" */
        return NULL;
    }

    const __m256i lo0_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)teddy_lo0));
    const __m256i hi0_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)teddy_hi0));
    const __m256i lo1_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)teddy_lo1));
    const __m256i hi1_v = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)teddy_hi1));

    const __m256i nib  = _mm256_set1_epi8(0x0f);
    const __m256i zero = _mm256_setzero_si256();

    size_t i = 0;
    /* Only v0 and v1 are loaded, but verification memcmps up to 9 bytes from
     * hay+i+31, so the bound is still the max_k one: i + 32 + 8 <= n. */
    for (; i + 32 + 8 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));

        __m256i cand = _mm256_and_si256(bucketmask(v0, lo0_v, hi0_v, nib),
                                        bucketmask(v1, lo1_v, hi1_v, nib));
        if (_mm256_testz_si256(cand, cand)) {
            continue; /* no branch's 2-byte prefix occurs in this block */
        }

        /* Spill the candidate bytes so individual lanes can be decoded, and
         * build a bitmap of the occupied lanes: cmpeq against zero marks the
         * EMPTY lanes, so the complement of its movemask is the set of lanes
         * that named at least one branch. Almost always just one or two. */
        uint8_t cbuf[32];
        _mm256_storeu_si256((__m256i *)cbuf, cand);
        uint32_t occ = ~(uint32_t)_mm256_movemask_epi8(
            _mm256_cmpeq_epi8(cand, zero));

        /* Ascending lanes: the first lane that verifies is the leftmost match
         * in the block, and blocks are visited in ascending order, so this is
         * leftmost overall. Within one lane the branch order does not matter
         * -- "fred" and "frederick" verifying at the same lane both yield the
         * same position, and a position is all this returns. */
        while (occ) {
            uint32_t l = (uint32_t)__builtin_ctz(occ);
            occ &= occ - 1;

            size_t pos = i + l;
            uint8_t bits = cbuf[l];
            while (bits) {
                int b = __builtin_ctz(bits);
                bits = (uint8_t)(bits & (bits - 1));
                /* The i+32+8<=n bound already guarantees this fits, but the
                 * check is what makes the guarantee local and auditable. */
                if (pos + alt8_len[b] <= n &&
                    memcmp(hay + pos, alt8_str[b], alt8_len[b]) == 0) {
                    return hay + pos;
                }
            }
        }
    }

    for (; i + 3 <= n; i++) {
        for (int b = 0; b < 8; b++) {
            if (i + alt8_len[b] <= n &&
                memcmp(hay + i, alt8_str[b], alt8_len[b]) == 0) {
                return hay + i;
            }
        }
    }
    return NULL;
}
