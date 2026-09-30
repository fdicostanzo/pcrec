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
 * BOTH CALLER-FACING ENTRY KINDS ARE SWEPT, `<prefix>_search` and
 * `<prefix>_match`, each with its own bucket line ([K73] added the second: the
 * DFA's unwrapped `_match` had no guard, and a search-only sweep could not
 * see it).
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

/* THE CONTRACT, written out here rather than asked of anything — the whole
 * reason this driver exists rather than a `.rxt` block. It must state the rule
 * `docs/spec/match_api.md` §3.1 promises, not the rule the backend happens to
 * implement, or the check can only ever confirm the compiler agrees with
 * itself.
 *
 * THREE CLAUSES, AND THE FIRST ONE IS A RULING. `p == 0` is a valid start
 * ALWAYS, even on a subject that begins with a continuation byte: no character
 * precedes offset 0, so a caller naming it cannot have pointed inside one, and
 * refusing it would turn §2.6/ASK 1's "an ill-formed sequence matches nothing,
 * with no error return" into "ill-formed input is an error". MEASURED as a
 * defect before it was a clause: without it the guard refused offset 0 on 21
 * oracle-verified cells of this corpus (`a` on the one-byte subject 0x80 among
 * them), found by wiring the axis into `make test-axes`.
 *
 * [K73] "valid start" here means NEVER REFUSED, which is all this predicate
 * is asked. Since K73 an offset 0 on a continuation byte is not where a match
 * is ATTEMPTED — the search moves on and the anchored entry answers no-match —
 * but that rule has no flag, so both arms agree there and the cell is SAME. */
static int is_boundary(const unsigned char *s, size_t n, size_t p)
{
    if (p == 0) return 1;              /* nothing precedes it to be inside of */
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

/* The bucket counts of ONE entry's sweep. */
typedef struct { long same, refused, other; } Buckets;

/* Classifies one cell into `b`, printing a defect line for OTHER. `ga`/`pa`
 * are the two arms' rendered answers and `gref`/`pref` whether each REFUSED
 * with the typed code. Returns 1 on a defect. */
static int classify(Buckets *b, const char *entry, const char *subj, size_t sp,
                    int bnd, int gref, int pref, const char *ga, const char *pa)
{
    if (gref) {
        /* A refusal is correct at a NON-boundary and only there, and the
         * permissive arm must still have answered — a refusal on both arms
         * would mean the flag did nothing. */
        if (bnd) {
            printf("OVER-FIRING %s subj=%s start=%zu: the guarded arm "
                   "REFUSED a position that IS a character boundary "
                   "(permissive arm said %s)\n", entry, subj, sp, pa);
            b->other++; return 1;
        }
        if (pref) {
            printf("LEAKED INTO THE DENY ARM %s subj=%s start=%zu: both "
                   "arms refused, so -fno-startpos-guard emitted a "
                   "guard it must not have\n", entry, subj, sp);
            b->other++; return 1;
        }
        b->refused++; return 0;
    }
    if (strcmp(ga, pa) == 0) {
        /* Agreement is correct at a boundary. At a NON-boundary it means the
         * guard did not fire where it must: the deleted-guard direction. */
        if (!bnd) {
            printf("GUARD MISSING %s subj=%s start=%zu: a MID-CHARACTER "
                   "position was answered (%s) instead of refused\n",
                   entry, subj, sp, ga);
            b->other++; return 1;
        }
        b->same++; return 0;
    }
    printf("DIVERGED WITHOUT A REFUSAL %s subj=%s start=%zu (boundary=%d): "
           "guarded=%s permissive=%s — the two arms must differ ONLY by the "
           "refusal\n", entry, subj, sp, bnd, ga, pa);
    b->other++; return 1;
}

int main(int argc, char **argv)
{
    unsigned char subj[512];
    Buckets sb = {0, 0, 0}, mb = {0, 0, 0};
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
            int bnd = is_boundary(subj, n, sp);
            int gr = g_search(subj, n, sp, gc);
            int pr = p_search(subj, n, sp, pc);

            answer(ga, sizeof ga, gr, gc);
            answer(pa, sizeof pa, pr, pc);
            rc_exit |= classify(&sb, "search", argv[a], sp, bnd,
                                gr == PCREC_ERR_STARTPOS,
                                pr == PCREC_ERR_STARTPOS, ga, pa);

            /* [K73] THE ANCHORED ENTRY, SWEPT THE SAME WAY. §3.1 promises
             * `<prefix>_match` carries the same guard; the search sweep above
             * could not see an anchored body that skipped it, and the DFA's
             * unwrapped form did, until K73's site survey found it. */
            rx_ctx gx = {0}, px = {0};
            gx.subject = px.subject = subj;
            gx.len = px.len = n;
            gx.pos = px.pos = sp;
            ptrdiff_t gm = g_match(&gx), pm = p_match(&px);
            snprintf(ga, sizeof ga, "%td", gm);
            snprintf(pa, sizeof pa, "%td", pm);
            rc_exit |= classify(&mb, "match", argv[a], sp, bnd,
                                gm == PCREC_ERR_STARTPOS,
                                pm == PCREC_ERR_STARTPOS, ga, pa);
        }
    }

    printf("buckets: same=%ld refused=%ld other=%ld\n",
           sb.same, sb.refused, sb.other);
    printf("match-buckets: same=%ld refused=%ld other=%ld\n",
           mb.same, mb.refused, mb.other);
    return rc_exit;
}
