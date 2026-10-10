/* docs/dev/optloop/et1twin/twin.c -- the REVERSE-INNER hand twin
 * (D151's tactic (b), the `handoff-rev` row's DFA hat) built around one
 * cell's UNMODIFIED artifacts:
 *
 *   rx.c    today's artifact for R = P.L.S (prefix rx): supplies the
 *           landmark scanner where it already emits one (rx_reqrun) and
 *           the ANCHORED forward finish (rx_match_caps)
 *   rxpl.c  pcrec's own artifact for `(?:P.L)\z` (prefix rxpl), which
 *           [OPT-REVEND] compiles to a pure reverse walk from the subject
 *           end: called with length j+|L| it IS the reverse DFA over P.L
 *           seeded at the landmark occurrence j, floored at search_from,
 *           recording the smallest accepting start s*(j)
 *
 * Per call:  for each occurrence j >= pos of L in increasing order: walk
 * P.L backwards from j+|L| to get s*(j); if non-empty, run the anchored
 * forward match at s*(j); a match is the answer, otherwise the next
 * occurrence (j+1: L may overlap itself). Exact under G1 (P regular),
 * G2 (P fixed-width or cannot consume every byte of L; for the sfx cell
 * the factor-free refinement, see the report) and G4 (S reads no capture
 * of P): docs/design/where_to_start.md §2.2.
 *
 * Cell knobs (build.sh): ET_LANDMARK(subject, n, pos) returns the start of
 * the first occurrence of L at or after pos, or n; ET_LLEN is |L|.       */
#include "rx.c"
#include "rxpl.c"

#if !defined(ET_LANDMARK) || !defined(ET_LLEN)
#error "build with -DET_LANDMARK=... -DET_LLEN=..."
#endif

#ifdef ET_LBYTE
/* the one-byte landmark scan for cells whose artifact emits none */
static inline size_t et_memchr_lm(const unsigned char *subject, size_t n, size_t pos)
{
    const void *q = pos < n ? memchr(subject + pos, ET_LBYTE, n - pos) : NULL;
    return q ? (size_t)((const unsigned char *)q - subject) : n;
}
#endif

int tw_search(const unsigned char *subject, size_t n, size_t search_from, ptrdiff_t (*caps)[2])
{
    if (search_from > n) return 0;
    size_t pos = search_from;
    for (;;) {
        size_t j = ET_LANDMARK(subject, n, pos);
        if (j >= n) return 0;
        ptrdiff_t start[RXPL_NCAPS][2];
#ifdef ET_PLANT_LO0
        /* failing-direction control: where_to_start.md §2.6's `lo0` mutant
         * (the walk accepts starts below search_from) */
        if (rxpl_search(subject, j + ET_LLEN, 0, start) == 1) {
#else
        if (rxpl_search(subject, j + ET_LLEN, search_from, start) == 1) {
#endif
            rx_ctx ctx = { .subject = subject, .len = n, .pos = (size_t)start[0][0] };
            ptrdiff_t len = rx_match_caps(&ctx, caps);
            if (len >= 0) return 1;
            if (len < -1) return (int)len;   /* a give-up propagates; none on the DFA route */
        }
        pos = j + 1;
    }
}
