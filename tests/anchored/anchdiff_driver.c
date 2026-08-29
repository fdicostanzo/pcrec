/* tests/anchored/anchdiff_driver.c — THE PRIMARY INSTRUMENT for [ENG-ABS]'s
 * anchored match-here form (docs/design/anchored_match_unwrapped.md §3).
 *
 * WHY A pcrec-vs-pcrec DIFFERENTIAL IS THE ONLY CHECK AVAILABLE HERE, and why
 * it had to be built rather than assumed. The row's whole claim is that
 * `<prefix>_match` reports the same length either way — its own anchored
 * machine run from `ctx->pos`, or the unanchored search with non-`ctx->pos`
 * starts rejected. The DENIED build is not an approximation of that: it IS the
 * shipped semantics, the code that ran before this row, and it derives its
 * answer from `<prefix>_search`, which every `.rxt` cell and both oracles
 * already verify. So this needs no external oracle to have an opinion.
 *
 * **AND NOTHING ELSE IN THE TREE ASKS THE QUESTION.** Measured before this
 * file was written: `tests/harness/driver.c` drives `<prefix>_search` for
 * every `m`/`n` cell and touches the anchored entries only as an `_in`-vs-
 * un-suffixed CROSS-CHECK — both sides of which are the same code path — and
 * `make test-axes` compares the corpus's SEARCH answers under each deny flag.
 * An anchored form that reported the wrong length would leave every one of
 * them green. That is the vacuity this file closes.
 *
 * WHAT IS COMPARED, per (pattern, subject, position):
 *
 *   1. `<prefix>_match`'s return — the matched length, or -1;
 *   2. `<prefix>_match_caps`'s return AND every one of its NCAPS capture
 *      pairs, compared as ptrdiff_t pairs and never as strings (R24's
 *      recorded blindness: two different offsets can spell the same bytes).
 *      The slots above 0 are the dead-group fill, which under the anchored
 *      form is written by `_match_caps` itself rather than inherited from
 *      `<prefix>_search` — so a missing fill is a divergence here;
 *   3. BOTH `_in` spellings, against the same expectations, because §10.2
 *      says each is its un-suffixed sibling in every respect;
 *   4. `<prefix>_search` itself, which this row does not touch and which must
 *      therefore agree byte for byte between the two builds — the arm that
 *      says a divergence above is about the ANCHORED entry rather than about
 *      the compiler having moved under both.
 *
 * EVERY POSITION FROM 0 TO n INCLUSIVE, plus n+1, and the two ends are the
 * cells the design's own argument turns on: `pos == n` is where the END view
 * is selected and where a zero-length match is reported, and `pos > n` is the
 * range guard whose two forms return different values from different
 * functions.
 *
 * Usage: anchdiff_driver < subjects   (one escaped subject per line, the same
 * escapes tests/harness/driver.c decodes). Prints a one-line tally on
 * agreement; prints the disagreeing cell and exits 1 on any divergence.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "on.h"
#include "off.h"

#if ON_NCAPS != OFF_NCAPS
#error "the two builds promise different capture counts -- they are not the same pattern"
#endif

/* tests/harness/driver.c's escape vocabulary, transcribed rather than
 * reinvented so a subject means the same thing in both files. */
static size_t unescape(const char *in, unsigned char *out, size_t cap)
{
    size_t n = 0;
    for (size_t i = 0; in[i] && n + 1 < cap; i++) {
        if (in[i] != '\\') { out[n++] = (unsigned char)in[i]; continue; }
        switch (in[++i]) {
        case 'n': out[n++] = '\n'; break;
        case 't': out[n++] = '\t'; break;
        case 'r': out[n++] = '\r'; break;
        case '0': out[n++] = '\0'; break;
        case '\\': out[n++] = '\\'; break;
        case '"': out[n++] = '"'; break;
        case 'x': {
            unsigned v = 0;
            if (sscanf(in + i + 1, "%2x", &v) != 1) return (size_t)-1;
            out[n++] = (unsigned char)v; i += 2; break;
        }
        case '\0': return (size_t)-1;
        default: out[n++] = (unsigned char)in[i]; break;
        }
    }
    return n;
}

static int cells = 0, bad = 0;

static void diverge(const char *what, size_t pos, const char *subj,
                    ptrdiff_t a, ptrdiff_t b)
{
    if (bad++ < 8)
        fprintf(stderr, "DIVERGE %s at pos %zu on \"%s\": default=%td denied=%td\n",
                what, pos, subj, a, b);
}

int main(void)
{
    char line[1 << 14];
    static unsigned char subj[1 << 13];

    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        while (L && (line[L-1] == '\n' || line[L-1] == '\r')) line[--L] = 0;
        size_t n = unescape(line, subj, sizeof subj);
        if (n == (size_t)-1) { fprintf(stderr, "malformed subject: %s\n", line); return 2; }

        for (size_t pos = 0; pos <= n + 1; pos++) {
            rx_ctx ctx;
            ptrdiff_t ca[ON_NCAPS][2], cb[ON_NCAPS][2];
            ptrdiff_t ma, mb, cra, crb, ia, ib, cia, cib;
            int k;

            memset(&ctx, 0, sizeof ctx);
            ctx.subject = subj; ctx.len = n; ctx.pos = pos;

            /* A KNOWN SENTINEL, not zero: `caps_out` is UNTOUCHED on every
             * negative return (spec §3.3), and a zero fill would make an
             * untouched slot indistinguishable from a written [0,0). */
            for (k = 0; k < ON_NCAPS; k++) { ca[k][0] = ca[k][1] = -7; cb[k][0] = cb[k][1] = -7; }

            ma  = on_match(&ctx);          mb  = off_match(&ctx);
            cra = on_match_caps(&ctx, ca); crb = off_match_caps(&ctx, cb);
            ia  = on_match_in(&ctx, NULL); ib  = off_match_in(&ctx, NULL);
            cia = on_match_caps_in(&ctx, ca, NULL);
            cib = off_match_caps_in(&ctx, cb, NULL);
            cells++;

            if (ma  != mb)  diverge("_match", pos, line, ma, mb);
            if (cra != crb) diverge("_match_caps", pos, line, cra, crb);
            if (ia  != ib)  diverge("_match_in", pos, line, ia, ib);
            if (cia != cib) diverge("_match_caps_in", pos, line, cia, cib);
            /* The two spellings must agree WITHIN a build too: §10.2 defines
             * the `_in` entry as its un-suffixed sibling, and this engine has
             * no storage a descriptor could change. */
            if (ma != ia)   diverge("_match vs _match_in (default build)", pos, line, ma, ia);
            if (mb != ib)   diverge("_match vs _match_in (denied build)", pos, line, mb, ib);
            if (cra != ma)  diverge("_match_caps vs _match (default build)", pos, line, cra, ma);
            if (crb != mb)  diverge("_match_caps vs _match (denied build)", pos, line, crb, mb);

            for (k = 0; k < ON_NCAPS; k++) {
                if (ca[k][0] != cb[k][0] || ca[k][1] != cb[k][1]) {
                    if (bad++ < 8)
                        fprintf(stderr, "DIVERGE caps slot %d at pos %zu on \"%s\":"
                                        " default=(%td,%td) denied=(%td,%td)\n",
                                k, pos, line, ca[k][0], ca[k][1], cb[k][0], cb[k][1]);
                }
            }
            /* THE ARM THAT SAYS THE DIVERGENCE IS ABOUT THE ANCHORED ENTRY.
             * This row does not touch `<prefix>_search`; if it moved, every
             * comparison above is about a different compiler rather than about
             * a different form. */
            {
                ptrdiff_t sa[ON_NCAPS][2], sb[ON_NCAPS][2];
                int fa, fb;
                size_t from = pos > n ? n : pos;
                for (k = 0; k < ON_NCAPS; k++) { sa[k][0] = sa[k][1] = -7; sb[k][0] = sb[k][1] = -7; }
                fa = on_search(subj, n, from, sa);
                fb = off_search(subj, n, from, sb);
                if (fa != fb) diverge("_search (this row must not touch it)", pos, line, fa, fb);
                else if (fa == 1)
                    for (k = 0; k < ON_NCAPS; k++)
                        if (sa[k][0] != sb[k][0] || sa[k][1] != sb[k][1])
                            diverge("_search caps (this row must not touch them)",
                                    pos, line, sa[k][0], sb[k][0]);
            }
        }
    }
    if (cells == 0) { fprintf(stderr, "anchdiff: ZERO cells compared\n"); return 2; }
    printf("cells %d divergences %d\n", cells, bad);
    return bad ? 1 : 0;
}
