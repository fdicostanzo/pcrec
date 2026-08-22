/* tests/backrefs/bref_entries.c — the THREE entry points side by side.
 *
 * `<prefix>_search`, `<prefix>_match` and `<prefix>_match_caps` are three
 * different promises and a `.rxt` block drives only the first. For this
 * module the difference is not decorative: the anchored entries pass
 * `ctx->len` as their length ceiling rather than a prefilter window, and this
 * module forces the prefilter OFF entirely (§7.1), so the three must agree by
 * construction — which is a claim worth checking precisely because nothing
 * else in the tree can see it.
 *
 * THE MATCH-HERE ORACLE IS `\G(?:PAT)` (wave D's trick, reused): libpcre2 has
 * no anchored mode, but `\G` is true iff the match position equals the
 * startpos, so its answer for the wrapped pattern IS the match-here answer
 * for the bare one.
 *
 * PROTOCOL: `<subject-file>\t<startpos>` on stdin; per line, three
 * TAB-separated fields in the order search / match / match_caps, each in
 * bref_batch.c's own format. `_match` returns a LENGTH (or a negative
 * sentinel), so it is rendered as `match <pos> <pos+len>` to make the three
 * columns comparable without the caller parsing two vocabularies.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

int main(void)
{
    char line[8192];
    unsigned char buf[1 << 16];

    while (fgets(line, sizeof line, stdin)) {
        char *tab = strchr(line, '\t');
        size_t n, sp;
        FILE *f;
        ptrdiff_t caps[RX_NCAPS][2];
        ptrdiff_t r;
        rx_ctx ctx;
        int found, g;

        if (!tab) { fprintf(stderr, "bref_entries: malformed input\n"); return 2; }
        *tab++ = '\0';
        sp = (size_t)strtoul(tab, NULL, 10);
        f = fopen(line, "rb");
        if (!f) { perror(line); return 2; }
        n = fread(buf, 1, sizeof buf, f);
        fclose(f);

        for (g = 0; g < RX_NCAPS; g++) caps[g][0] = caps[g][1] = PCREC_UNSET;
        found = rx_search(buf, n, sp, caps);
        if (found == 1) {
            printf("match %td %td", caps[0][0], caps[0][1]);
            for (g = 1; g < RX_NCAPS; g++)
                printf(" %td %td", caps[g][0], caps[g][1]);
        } else if (found == 0) printf("nomatch");
        else printf("giveup %d", found);

        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        r = rx_match(&ctx);
        printf("\t");
        if (r >= 0) printf("match %zu %td", sp, (ptrdiff_t)sp + r);
        else if (r == -1) printf("nomatch");
        else printf("giveup %td", r);

        for (g = 0; g < RX_NCAPS; g++) caps[g][0] = caps[g][1] = PCREC_UNSET;
        r = rx_match_caps(&ctx, caps);
        printf("\t");
        if (r >= 0) {
            printf("match %zu %td", sp, (ptrdiff_t)sp + r);
            for (g = 1; g < RX_NCAPS; g++)
                printf(" %td %td", caps[g][0], caps[g][1]);
        } else if (r == -1) printf("nomatch");
        else printf("giveup %td", r);
        printf("\n");
    }
    return 0;
}
