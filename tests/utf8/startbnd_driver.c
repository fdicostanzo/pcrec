/* tests/utf8/startbnd_driver.c — [K50]'s TWO-ARM DIFFERENTIAL driver.
 *
 * Two artifacts compiled from ONE pattern into ONE translation unit: `g_`
 * with the caller-startpos boundary guard (the default) and `p_` with
 * `-fno-startpos-guard` (utf8_design.md §2.6.1.1's ruled permissive
 * semantics). It sweeps EVERY startpos of every subject and classifies each
 * cell into exactly one of three buckets:
 *
 *   SAME      the two arms agree — expected at every character boundary,
 *             where the guard is transparent by construction;
 *   REFUSED   the guarded arm returned PCREC_ERR_STARTPOS and the permissive
 *             arm answered — expected at exactly the mid-character positions;
 *   OTHER     anything else, which is a defect however it is spelled.
 *
 * THE BOUNDARY PREDICATE IS COMPUTED HERE, INDEPENDENTLY OF THE COMPILER,
 * and that is the whole reason this driver exists rather than a `.rxt` block.
 * `is_boundary()` below is written from the ENCODING's definition (a position
 * is a boundary iff it is the end of the subject or its byte is not a UTF-8
 * continuation byte), not read out of the artifact — so the check controls
 * WHERE the arms diverge and not merely THAT they do. A driver that asked the
 * artifact where the boundaries were would be the control-shares-a-source-
 * with-its-subject failure this project keeps cataloguing
 * (docs/dev/learnings.md §3).
 *
 * NON-VACUITY IS THE DRIVER'S OWN JOB, not the caller's: it prints the three
 * bucket counts and the script fails on `refused == 0`. An empty divergence
 * population means a dead guard, and a differential that reports "no
 * disagreement" on a dead guard is exactly the check that certifies nothing.
 *
 * Exit codes: 0 clean, 1 a classification defect (details on stdout),
 * 2 usage. The bucket line is always printed, on every exit path that got as
 * far as sweeping.
 */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* THE CODE IS READ OUT OF THE ARTIFACT, never spelled here. Both headers
 * carry the shared `PCREC_RX_ABI_H` block, so the first include supplies
 * `PCREC_ERR_STARTPOS` and the second's copy is guarded away — which is the
 * cross-prefix composability property match_api.md §1/§2 promises, exercised
 * here rather than asserted. A driver with its own `-7` would be a second
 * spelling of the contract it is checking. */
#include "guarded.h"
#include "permissive.h"

#ifndef PCREC_ERR_STARTPOS
/* Kept so a build against an artifact that predates the code fails HERE, with
 * this sentence, rather than silently classifying every refusal as OTHER. */
#error "this artifact defines no PCREC_ERR_STARTPOS: it predates [K50]"
#endif

/* The encoding's own rule, written out here rather than asked of anything. */
static int is_boundary(const unsigned char *s, size_t n, size_t p)
{
    if (p >= n) return 1;              /* the end of the subject, and past it */
    return (s[p] & 0xC0) != 0x80;      /* not a continuation byte */
}

/* One arm's answer, rendered so two cells compare as strings. */
static void answer(char *out, size_t cap, int rc, ptrdiff_t caps[1][2])
{
    if (rc == 1) snprintf(out, cap, "(%td,%td)", caps[0][0], caps[0][1]);
    else         snprintf(out, cap, "rc=%d", rc);
}

/* Hex -> bytes, so a subject with ill-formed sequences survives argv. */
static size_t unhex(const char *h, unsigned char *out, size_t cap)
{
    size_t n = 0;
    for (; h[0] && h[1] && n < cap; h += 2) {
        char t[3];
        t[0] = h[0]; t[1] = h[1]; t[2] = 0;
        out[n++] = (unsigned char)strtoul(t, NULL, 16);
    }
    return n;
}

int main(int argc, char **argv)
{
    unsigned char subj[512];
    long same = 0, refused = 0, other = 0;
    int rc_exit = 0;

    if (argc < 2) {
        fprintf(stderr, "usage: startbnd_driver HEXSUBJECT...\n");
        return 2;
    }

    for (int a = 1; a < argc; a++) {
        size_t n = unhex(argv[a], subj, sizeof subj);
        /* A CONTINUATION BYTE PARKED AT s[n], and it is a detector rather than
         * hygiene. `startpos == n` is a character boundary and must be
         * ACCEPTED, but a guard spelled without its end-of-subject arm would
         * read `s[n]` to decide — undefined behaviour the matcher's own
         * contract forbids (match_api.md §3.1: "the matcher never reads
         * s[n]"), and in practice it reads whatever is there. With a zero byte
         * there such a guard ACCEPTS and this sweep sees nothing; with 0x80 it
         * REFUSES and the cell lands in OVER-FIRING. MEASURED: dropping the
         * `@P >= @N` arm from the utf8 backend's guard left this file 4/4
         * green before this line existed. */
        subj[n] = 0x80;
        for (size_t sp = 0; sp <= n; sp++) {
            ptrdiff_t gc[1][2], pc[1][2];
            char ga[64], pa[64];
            int gr = g_search(subj, n, sp, gc);
            int pr = p_search(subj, n, sp, pc);
            int bnd = is_boundary(subj, n, sp);

            answer(ga, sizeof ga, gr, gc);
            answer(pa, sizeof pa, pr, pc);

            if (gr == PCREC_ERR_STARTPOS) {
                /* A refusal is correct at a NON-boundary and only there, and
                 * the permissive arm must still have answered — a refusal on
                 * both arms would mean the flag did nothing. */
                if (bnd) {
                    printf("OVER-FIRING subj=%s start=%zu: the guarded arm "
                           "REFUSED a position that IS a character boundary "
                           "(permissive arm said %s)\n", argv[a], sp, pa);
                    other++; rc_exit = 1;
                } else if (pr == PCREC_ERR_STARTPOS) {
                    printf("LEAKED INTO THE DENY ARM subj=%s start=%zu: both "
                           "arms refused, so -fno-startpos-guard emitted a "
                           "guard it must not have\n", argv[a], sp);
                    other++; rc_exit = 1;
                } else {
                    refused++;
                }
            } else if (strcmp(ga, pa) == 0) {
                /* Agreement is correct at a boundary. At a NON-boundary it
                 * means the guard did not fire where it must: the deleted-
                 * guard direction. */
                if (!bnd) {
                    printf("GUARD MISSING subj=%s start=%zu: a MID-CHARACTER "
                           "position was answered (%s) instead of refused\n",
                           argv[a], sp, ga);
                    other++; rc_exit = 1;
                } else {
                    same++;
                }
            } else {
                printf("DIVERGED WITHOUT A REFUSAL subj=%s start=%zu "
                       "(boundary=%d): guarded=%s permissive=%s — the two "
                       "arms must differ ONLY by the refusal\n",
                       argv[a], sp, bnd, ga, pa);
                other++; rc_exit = 1;
            }
        }
    }

    printf("buckets: same=%ld refused=%ld other=%ld\n", same, refused, other);
    return rc_exit;
}
