/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/k1_ref.c — K1's reference functions: one plain byte loop per
 * primitive (requirements.md §1.3's F menu, tier A plus F7's run compare and,
 * since M7, F8's mismatch).
 * They define what each primitive answers. They are deliberately the most
 * obvious loop, never an optimized one: G2 uses them as its oracle, and an
 * oracle that shares a trick with what it checks checks nothing.
 */
#include "../include/memfn.h"

/* 1 iff byte b is a member of the 256-bit set. */
static int in_set(const uint8_t set[32], uint8_t b)
{
    return (set[b >> 3] >> (b & 7)) & 1;
}

size_t mf_ref_find_byte(const uint8_t *s, size_t n, uint8_t c)
{
    for (size_t i = 0; i < n; i++)
        if (s[i] == c) return i;
    return n;
}

size_t mf_ref_find_any2(const uint8_t *s, size_t n, uint8_t a, uint8_t b)
{
    for (size_t i = 0; i < n; i++)
        if (s[i] == a || s[i] == b) return i;
    return n;
}

size_t mf_ref_find_any3(const uint8_t *s, size_t n, uint8_t a, uint8_t b,
                        uint8_t c)
{
    for (size_t i = 0; i < n; i++)
        if (s[i] == a || s[i] == b || s[i] == c) return i;
    return n;
}

size_t mf_ref_find_in_set(const uint8_t *s, size_t n, const uint8_t set[32])
{
    for (size_t i = 0; i < n; i++)
        if (in_set(set, s[i])) return i;
    return n;
}

size_t mf_ref_skip_in_set(const uint8_t *s, size_t n, const uint8_t set[32])
{
    for (size_t i = 0; i < n; i++)
        if (!in_set(set, s[i])) return i;
    return n;
}

size_t mf_ref_find_literal(const uint8_t *s, size_t n, const uint8_t *lit,
                           size_t len)
{
    for (size_t i = 0; i + len <= n; i++)
        if (mf_ref_run_verify(s, n, i, lit, NULL, len)) return i;
    return n;
}

int mf_ref_run_verify(const uint8_t *s, size_t n, size_t pos,
                      const uint8_t *run, const uint8_t *mask, size_t len)
{
    if (pos > n || len > n - pos) return 0;
    for (size_t j = 0; j < len; j++) {
        uint8_t m = mask ? mask[j] : 0xFF;
        if ((s[pos + j] & m) != run[j]) return 0;
    }
    return 1;
}

size_t mf_ref_mismatch(const uint8_t *a, const uint8_t *b, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if (a[i] != b[i]) return i;
    return n;
}
