/* tests/codegen/searchpin_driver.c — [OPT-5] STEP 2's ANSWER differential.
 *
 * Two artifacts for ONE pattern, linked into one program: `on_*` built at the
 * default (axis J may select `pinned`) and `off_*` built under
 * `-fno-start-pinned` (the reverse pass, always). It drives BOTH at every
 * `startpos` from 0 to n+1 and compares, per call:
 *
 *     the VERDICT, caps[0][0] and caps[0][1] of `<p>_search`
 *     the return value of `<p>_match`
 *     the return value AND caps[0][0]/[0][1] of `<p>_match_caps`
 *
 * =====================================================================
 * WHY THIS IS A REAL CONTROL AND NOT A BUILD COMPARING ITSELF
 * =====================================================================
 * docs/dev/learnings.md §3. The `off` build recovers the match START by
 * walking an INDEPENDENTLY BUILT REVERSE AUTOMATON — the emitter's own note
 * on the pair is that "the two machines are independent and need not agree" —
 * where the `on` build writes `search_from` from a compile-time proof about
 * the FORWARD machine. The two derivations share nothing but the answer.
 *
 * =====================================================================
 * caps[0][0] IS READ EXPLICITLY, AND AT startpos > 0
 * =====================================================================
 * The elision moves `caps[0][0]` and nothing else — not the match/no-match
 * verdict, not the end, not the length. learnings §3 records that "offsets
 * were the blind field twice of three", so a sweep that compared only
 * verdicts or only lengths would be VACUOUS against every failure direction
 * in the design note's §3.4. And the absolute-offset trap (writing `0`
 * instead of `search_from`) is invisible to any single search at
 * `startpos == 0`, which is most of the corpus — hence every position.
 *
 * ONE FAILURE DIRECTION POINTS THE OTHER WAY and is why the VERDICT is
 * compared too: a dead seed state with P3's liveness conjunct dropped reports
 * a MATCH WHERE THERE IS NONE. A differential tuned entirely to "offsets are
 * the blind field" would not be looking for it.
 *
 * =====================================================================
 * THE C3 COUNTER
 * =====================================================================
 * The tally line reports `on_match_neg`, the number of calls on which the
 * DEFAULT build's `<prefix>_match` returned -1, and `on_match_neg_inrange`,
 * the subset of those at `startpos <= n`. On an artifact that is both
 * predicate-accepted and `RX_DFA_MATCH "search-filter"` the IN-RANGE count
 * must be ZERO: `<prefix>_search` returns 1 with `caps[0][0] == ctx->pos` on
 * every call it actually performs, so the fallback's
 * `found != 1 || caps[0][0] != ctx->pos` filter never fires and its
 * `return -1` is unreachable.
 *
 * THE TWO COUNTS ARE SEPARATE BECAUSE C3 AS WRITTEN IS TRUE ONLY IN RANGE,
 * and that is a finding rather than a nicety. `search_from > subject_length`
 * is disposed of by the emitted range guard's own `return 0` ABOVE the scan,
 * so at `startpos == n+1` the search returns 0 and `<prefix>_match` correctly
 * returns -1 — on a pinned artifact exactly as on any other. The design
 * note's "returns 1 on every call" omits that guard. The caller decides which
 * count to assert on; this file only counts.
 *
 * Usage: searchpin_driver < subjects   (one escaped subject per line, the
 * same escape vocabulary tests/harness/driver.c decodes). Prints a one-line
 * tally on agreement; prints the disagreeing cells and exits 1 on any
 * divergence, 2 on its own breakage.
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

static long cells = 0, bad = 0, on_match_neg = 0, on_match_neg_inrange = 0;

static void diverge(const char *what, size_t pos, const char *subj,
                    ptrdiff_t a, ptrdiff_t b)
{
    if (bad++ < 8)
        fprintf(stderr, "DIVERGE %s at startpos %zu on \"%s\": default=%td denied=%td\n",
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
            ptrdiff_t ca[ON_NCAPS][2], cb[ON_NCAPS][2];
            ptrdiff_t mca[ON_NCAPS][2], mcb[ON_NCAPS][2];
            rx_ctx ctx;
            int sa, sb, k;
            ptrdiff_t ma, mb, cra, crb;

            /* A KNOWN SENTINEL, not zero: `caps` is UNTOUCHED on a 0 or a
             * negative return (spec §3.1), and a zero fill would make an
             * untouched slot indistinguishable from a written [0,0) — which
             * is exactly the value the absolute-offset trap produces. */
            for (k = 0; k < ON_NCAPS; k++) {
                ca[k][0] = ca[k][1] = -7; cb[k][0] = cb[k][1] = -7;
                mca[k][0] = mca[k][1] = -7; mcb[k][0] = mcb[k][1] = -7;
            }

            sa = on_search(subj, n, pos, ca);
            sb = off_search(subj, n, pos, cb);
            cells++;
            if (sa != sb) diverge("search-verdict", pos, line, sa, sb);
            /* The offsets are compared UNCONDITIONALLY, not only when the
             * verdict is 1: on a 0 or negative return both must still hold
             * the sentinel, which is how an artifact that writes a span it
             * should not have written is caught. */
            if (ca[0][0] != cb[0][0]) diverge("search-caps[0][0]", pos, line, ca[0][0], cb[0][0]);
            if (ca[0][1] != cb[0][1]) diverge("search-caps[0][1]", pos, line, ca[0][1], cb[0][1]);

            memset(&ctx, 0, sizeof ctx);
            ctx.subject = subj; ctx.len = n; ctx.pos = pos;
            ma  = on_match(&ctx);          mb  = off_match(&ctx);
            cra = on_match_caps(&ctx, mca); crb = off_match_caps(&ctx, mcb);
            if (ma != mb) diverge("match", pos, line, ma, mb);
            if (cra != crb) diverge("match_caps", pos, line, cra, crb);
            if (mca[0][0] != mcb[0][0]) diverge("match_caps[0][0]", pos, line, mca[0][0], mcb[0][0]);
            if (mca[0][1] != mcb[0][1]) diverge("match_caps[0][1]", pos, line, mca[0][1], mcb[0][1]);
            if (ma < 0) { on_match_neg++; if (pos <= n) on_match_neg_inrange++; }
        }
    }
    printf("cells=%ld diverged=%ld on_match_neg=%ld on_match_neg_inrange=%ld\n",
           cells, bad, on_match_neg, on_match_neg_inrange);
    return bad ? 1 : 0;
}
