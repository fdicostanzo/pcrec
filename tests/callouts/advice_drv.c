/* tests/callouts/advice_drv.c — the fire-count driver of the `once` advice
 * check (advice_check.py; docs/spec/match_api.md §11.8¶3).
 *
 * Linked with one artifact compiled `-p rx` whose sites bind
 * `rx_callout_x` (the counted site) and `rx_callout_y`, checks that always
 * pass. Reads one subject per stdin
 * line (hex) and prints, per subject, the most fires any one ATTEMPT made
 * (`rx_match` anchored at every start, 0 through the subject's length):
 *     fires <max>
 * A `once` site the compiler accepted must never print more than 1. */
#include <stdio.h>
#include <string.h>

#include "a.h"

static int fires;

static ptrdiff_t co_pass(const rx_ctx *c)
{
    (void)c;
    fires++;
    return 0;
}

/* Another check site, passing; its fires are not the `once` site's. */
static ptrdiff_t co_other(const rx_ctx *c)
{
    (void)c;
    return 0;
}

const rx_callout_ref rx_callout_x = { co_pass, NULL };
const rx_callout_ref rx_callout_y = { co_other, NULL };

int main(void)
{
    static char line[1 << 12];
    static unsigned char s[1 << 11];
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (const char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2) {
            unsigned v;
            if (sscanf(h, "%2x", &v) != 1) break;
            s[n++] = (unsigned char)v;
        }
        int most = 0;
        for (size_t p = 0; p <= n; p++) {
            const rx_ctx c = { .subject = s, .len = n, .pos = p };
            fires = 0;
            (void)rx_match(&c);
            if (fires > most) most = fires;
        }
        printf("fires %d\n", most);
    }
    return 0;
}
