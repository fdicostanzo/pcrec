/* ucd_tables.c — the Unicode property tables, and the ONLY file that knows
 * their layout ([DATA-PLAN] A1).  The interface is `ucd_tables.h`.
 *
 * THE FORMAT (written by `third_party/ucd-16.0.0/generate.py`, which is its
 * writer; this comment is its only description):
 *
 *   ucd_iv_blob   bytes.  One DISTINCT set after another, each a run of
 *                 delta-encoded LEB128 varints (7 bits per byte, low group
 *                 first, bit 7 set means another byte follows).  An interval
 *                 is two varints: `lo - prev_hi` then `hi - lo`, where
 *                 `prev_hi` is 0 before a set's first interval.  A set's
 *                 interval COUNT is not in the stream.
 *   ucd_set_off[] where each distinct set starts in the blob (byte offset).
 *   ucd_set_n[]   how many intervals each distinct set has.
 *   ucd_set_ck[], ucd_ck_lo[], ucd_ck_off[], ucd_ck_prev[]
 *                 SEARCH CHECKPOINTS, so a membership test need not decode a
 *                 whole set.  A set of n intervals has (n-1)/UCD_GEN_CK_STRIDE
 *                 checkpoints, one at each interval whose index is a multiple
 *                 of the stride (not 0): `ucd_set_ck[set]` is the index of the
 *                 set's first, and the checkpoint holds that interval's `lo`,
 *                 the byte offset in the blob where its varints start, and
 *                 the previous interval's `hi` (the delta base).  A set's
 *                 checkpoints are in increasing `lo` order.
 *   ucd_name_blob each distinct name once, NUL-terminated.
 *   ucd_row_*[]   one entry per row, parallel arrays: `name` is the offset of
 *                 the row's name in the name blob, `ns` its namespace mask,
 *                 `set` and `ci_set` the distinct-set indices to use normally
 *                 and under `-i`.  Rows with the same name share one name.
 *
 * COST: a set decodes in one forward pass, O(n), into arena memory, and only
 * when the caller wants it; a membership test binary-searches the checkpoints
 * and decodes at most one stride of intervals, so it is O(log n) as the
 * uncompressed table's binary search was.  Nothing is cached and no pointer
 * into the blob ever escapes.  A name lookup is a linear length+memcmp scan of
 * the rows, as the uncompressed table was.
 */

#include <string.h>

#include "ucd_tables.h"

#include "ucd_tables.inc"

_Static_assert(PCREC_UCD_NS_BARE == UCD_GEN_NS_BARE, "namespace numbering");
_Static_assert(PCREC_UCD_NS_SC   == UCD_GEN_NS_SC,   "namespace numbering");
_Static_assert(PCREC_UCD_NS_SCX  == UCD_GEN_NS_SCX,  "namespace numbering");
_Static_assert(PCREC_UCD_NS_BC   == UCD_GEN_NS_BC,   "namespace numbering");
_Static_assert(PCREC_UCD_NS_BLK  == UCD_GEN_NS_BLK,  "namespace numbering");
_Static_assert(PCREC_UCD_NS_AGE  == UCD_GEN_NS_AGE,  "namespace numbering");

static unsigned ucd_varint(const unsigned char **pp)
{
    const unsigned char *p = *pp;
    unsigned v = 0;
    int shift = 0;
    for (;;) {
        unsigned b = *p++;
        v |= (b & 0x7Fu) << shift;
        if (!(b & 0x80u)) break;
        shift += 7;
    }
    *pp = p;
    return v;
}

/* THE ONE INTERVAL CURSOR: a position in a set's varint stream. */
typedef struct {
    const unsigned char *p;
    unsigned prev;          /* the previous interval's hi: the delta base */
} UcdCur;

static unsigned ucd_set_count(unsigned set)
{
    return ucd_set_n[set];
}

static UcdCur ucd_cur_start(unsigned set)
{
    UcdCur c = { ucd_iv_blob + ucd_set_off[set], 0 };
    return c;
}

static void ucd_cur_next(UcdCur *c, unsigned *lo, unsigned *hi)
{
    *lo = c->prev + ucd_varint(&c->p);
    *hi = *lo + ucd_varint(&c->p);
    c->prev = *hi;
}

/* THE ONE ROW LOOKUP: the row named `name[0..len)` whose mask intersects
 * `ns`, or -1.  (The writer guarantees at most one such row for a one-bit
 * `ns`.) */
static long ucd_row_find(const char *name, size_t len, unsigned ns)
{
    for (size_t i = 0; i < UCD_GEN_NROWS; i++) {
        const char *k = ucd_name_blob + ucd_row_name[i];
        if (!(ucd_row_ns[i] & ns)) continue;
        if (strlen(k) != len || memcmp(k, name, len) != 0) continue;
        return (long)i;
    }
    return -1;
}

static const PcrecCpRange *ucd_decode(Arena *a, unsigned set, int *n)
{
    int cnt = (int)ucd_set_count(set);
    /* never NULL for a present set: an empty one is a real answer */
    PcrecCpRange *iv = pcrec_arena_alloc(a, (size_t)(cnt ? cnt : 1) * sizeof *iv);
    UcdCur c = ucd_cur_start(set);
    for (int i = 0; i < cnt; i++)
        ucd_cur_next(&c, &iv[i].lo, &iv[i].hi);
    *n = cnt;
    return iv;
}

/* Is `cp` in `set`?  Binary search over the set's checkpoints for the last
 * one at or below `cp`, then a short forward walk from it. */
static bool ucd_set_has(unsigned set, unsigned cp)
{
    unsigned n = ucd_set_count(set);
    unsigned nck = n ? (n - 1) / UCD_GEN_CK_STRIDE : 0;
    const unsigned base = ucd_set_ck[set];
    UcdCur c = ucd_cur_start(set);
    unsigned a = 0, b = nck;            /* first checkpoint with lo > cp */
    while (a < b) {
        unsigned m = a + (b - a) / 2;
        if (ucd_ck_lo[base + m] <= cp) a = m + 1;
        else b = m;
    }
    if (a > 0) {
        c.p = ucd_iv_blob + ucd_ck_off[base + a - 1];
        c.prev = ucd_ck_prev[base + a - 1];
    }
    for (unsigned j = a * UCD_GEN_CK_STRIDE; j < n; j++) {
        unsigned lo, hi;
        ucd_cur_next(&c, &lo, &hi);
        if (cp < lo) return false;     /* sorted: past the place it would be */
        if (cp <= hi) return true;
    }
    return false;
}

const PcrecCpRange *pcrec_ucd_row_set(Arena *a, size_t i, bool caseless,
                                      int *n)
{
    if (i >= UCD_GEN_NROWS) return NULL;
    return ucd_decode(a, caseless ? ucd_row_ci_set[i] : ucd_row_set[i], n);
}

bool pcrec_ucd_exists(const char *name, size_t len, unsigned ns)
{
    return ucd_row_find(name, len, ns) >= 0;
}

const PcrecCpRange *pcrec_ucd_find(Arena *a, const char *name, size_t len,
                                   unsigned ns, bool caseless, int *n)
{
    long i = ucd_row_find(name, len, ns);
    return i < 0 ? NULL : pcrec_ucd_row_set(a, (size_t)i, caseless, n);
}

int pcrec_ucd_contains(const char *normname, unsigned cp)
{
    long i = ucd_row_find(normname, strlen(normname), PCREC_UCD_NS_BARE);
    return i < 0 ? -1 : ucd_set_has(ucd_row_set[i], cp);
}

size_t pcrec_ucd_row_count(void)
{
    return UCD_GEN_NROWS;
}

const char *pcrec_ucd_row_name(size_t i, unsigned *ns)
{
    if (i >= UCD_GEN_NROWS) return NULL;
    if (ns) *ns = ucd_row_ns[i];
    return ucd_name_blob + ucd_row_name[i];
}

const char *pcrec_ucd_unicode_version(void)
{
    return UCD_GEN_VERSION;
}
