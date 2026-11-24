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
 *   ucd_name_blob each distinct name once, NUL-terminated.
 *   ucd_row_*[]   one entry per row, parallel arrays: `name` is the offset of
 *                 the row's name in the name blob, `ns` its namespace mask,
 *                 `set` and `ci_set` the distinct-set indices to use normally
 *                 and under `-i`.  Rows with the same name share one name.
 *
 * DECODE COST: a set decodes in one forward pass, O(n), into arena memory;
 * nothing is cached, and no pointer into the blob ever escapes.  A name
 * lookup is a linear length+memcmp scan of the rows, as the uncompressed table
 * was.
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

static const PcrecCpRange *ucd_decode(Arena *a, unsigned set, int *n)
{
    int cnt = (int)ucd_set_n[set];
    /* never NULL for a present set: an empty one is a real answer */
    PcrecCpRange *iv = pcrec_arena_alloc(a, (size_t)(cnt ? cnt : 1) * sizeof *iv);
    const unsigned char *p = ucd_iv_blob + ucd_set_off[set];
    unsigned prev = 0;
    for (int i = 0; i < cnt; i++) {
        unsigned lo = prev + ucd_varint(&p);
        unsigned hi = lo + ucd_varint(&p);
        iv[i].lo = lo;
        iv[i].hi = hi;
        prev = hi;
    }
    *n = cnt;
    return iv;
}

const PcrecCpRange *pcrec_ucd_row_set(Arena *a, size_t i, bool caseless,
                                      int *n)
{
    if (i >= UCD_GEN_NROWS) return NULL;
    return ucd_decode(a, caseless ? ucd_row_ci_set[i] : ucd_row_set[i], n);
}

const PcrecCpRange *pcrec_ucd_find(Arena *a, const char *name, size_t len,
                                   unsigned ns, bool caseless, int *n)
{
    for (size_t i = 0; i < UCD_GEN_NROWS; i++) {
        const char *k = ucd_name_blob + ucd_row_name[i];
        if (!(ucd_row_ns[i] & ns)) continue;
        if (strlen(k) != len || memcmp(k, name, len) != 0) continue;
        return pcrec_ucd_row_set(a, i, caseless, n);
    }
    return NULL;
}

int pcrec_ucd_contains(const char *normname, unsigned cp)
{
    size_t len = strlen(normname);
    for (size_t i = 0; i < UCD_GEN_NROWS; i++) {
        const char *k = ucd_name_blob + ucd_row_name[i];
        if (!(ucd_row_ns[i] & PCREC_UCD_NS_BARE)) continue;
        if (strlen(k) != len || memcmp(k, normname, len) != 0) continue;
        unsigned set = ucd_row_set[i];
        const unsigned char *p = ucd_iv_blob + ucd_set_off[set];
        unsigned prev = 0;
        for (unsigned j = 0; j < ucd_set_n[set]; j++) {
            unsigned lo = prev + ucd_varint(&p);
            unsigned hi = lo + ucd_varint(&p);
            if (cp < lo) return 0;     /* sorted: past the place it would be */
            if (cp <= hi) return 1;
            prev = hi;
        }
        return 0;
    }
    return -1;
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
