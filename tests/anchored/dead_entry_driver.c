/* tests/anchored/dead_entry_driver.c — drives `<prefix>_match` and
 * `<prefix>_match_caps` on the cells run_anchored_dead_entry.sh feeds it and
 * compares each answer with the expected length.
 *
 * Input, one cell per line: `<subject> <pos> <expected>`, where `<subject>`
 * is bytes with no space (`-` spells the empty subject) and `<expected>` is
 * the match length at exactly `pos`, or -1. Exits 0 when every cell agrees,
 * 1 on the first disagreement (printed), 2 on a malformed line or no cells.
 *
 * The subject is copied into a buffer sized EXACTLY to it, so a read past
 * either end of the subject is a read past the allocation — the kind of
 * read an AddressSanitizer build reports, which is the arm the script adds
 * when the compiler can build one.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "on.h"

int main(void)
{
    char line[256], subj[128];
    long pos, want;
    int cells = 0;

    while (fgets(line, sizeof line, stdin)) {
        if (line[0] == '\n' || line[0] == '#') continue;
        if (sscanf(line, "%127s %ld %ld", subj, &pos, &want) != 3) {
            fprintf(stderr, "malformed cell: %s", line);
            return 2;
        }
        size_t n = strcmp(subj, "-") ? strlen(subj) : 0;
        unsigned char *s = malloc(n ? n : 1);
        if (!s) return 2;
        memcpy(s, subj, n);

        rx_ctx ctx;
        memset(&ctx, 0, sizeof ctx);
        ctx.subject = s;
        ctx.len = n;
        ctx.pos = (size_t)pos;
        ptrdiff_t got = on_match(&ctx);
        ptrdiff_t caps[ON_NCAPS][2];
        ptrdiff_t gotc = on_match_caps(&ctx, caps);
        free(s);

        if (got != want || gotc != want) {
            printf("DISAGREE: subject \"%s\" pos %ld: _match %td, _match_caps %td, expected %ld\n",
                   n ? subj : "", pos, got, gotc, want);
            return 1;
        }
        if (want >= 0 && (caps[0][0] != pos || caps[0][1] != pos + want)) {
            printf("DISAGREE: subject \"%s\" pos %ld: _match_caps span [%td,%td), expected [%ld,%ld)\n",
                   n ? subj : "", pos, caps[0][0], caps[0][1], pos, pos + want);
            return 1;
        }
        cells++;
    }
    if (cells == 0) return 2;
    printf("cells %d\n", cells);
    return 0;
}
