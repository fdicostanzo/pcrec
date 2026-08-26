/*
 * tier_escalation_driver.c -- [OPT-1] STEP 3's counter: the tier-escalation
 * RATE over an exemplar subject file, run through tests/bench/tier_escalation.sh.
 *
 * docs/design/two_tier_entry.md section 7 names the follow-up this file is:
 * "how often real calls escalate is a MEASUREMENT nobody has ... a first cut
 * needs a driver and no profiler. The -D<PREFIX>_TEST_TIER_HOOK build already
 * counts escalations." tests/codegen/tier_driver.c already built that hook
 * into a two-source IDENTITY check (does the escalation SITE agree with the
 * boundary predicted through `_in`); this file reuses the same hook for a
 * different purpose -- counting over a real subject population instead of
 * cross-checking one specimen's synthetic depths -- so it does not duplicate
 * run_tiered_entry.sh's job.
 *
 * THE HOOK, restated (match_api.md section 5.3, section 10.9): built with
 * -DRX_TEST_TIER_HOOK, an artifact whose stamped default does not fit one
 * page calls `extern void rx_tier_escalated(void)` at its one escalation
 * site -- and ONLY there, RX_TIER_NOTE() right before the noinline `_deep`
 * call -- so counting calls to it here is counting real escalations, not a
 * proxy. Without the -D it is `((void)0)` and the artifact declares no
 * mutable state of its own (section 5.3), so this counter never touches the
 * artifact's binary text.
 *
 * TWO FORMS, matching pcrec-bench's bench/email adapter convention
 * (testees/pcrec/driver.c, testees/pcrec/CLAUDE.md "The MATCH regime uses a
 * SECOND artifact"):
 *
 *   search  -- rx_search(s, n, 0, caps) once per subject, unanchored, on the
 *              plain artifact. This is the "search_short" / throughput form.
 *   whole   -- rx_match_caps(&ctx, caps_out) once per subject, anchored at
 *              ctx.pos == 0, on a SEPARATE artifact compiled from
 *              `(?:PATTERN)\z` (the wrapper script builds it; pcrec has no
 *              native end-anchor). A return `r == (ptrdiff_t)n` is a
 *              whole-subject match; `0 <= r < n` is a strict-prefix match
 *              under leftmost-first anchoring and is reported `prefix`, not
 *              `match` -- same caveat testees/pcrec/CLAUDE.md documents,
 *              carried here so a `prefix` row is not misread as a bug.
 *
 * Subject list format: one `<id>\t<path>` pair per line (driver.c /
 * tier_driver.c's own convention), so the wrapper script hands it a plain
 * manifest-derived list with no reformatting.
 *
 * Prints one line per subject to stdout:
 *     row <id> <bytes> <escalated 0|1> <outcome>
 * where <outcome> is one of: match, nomatch, prefix, giveup:<code>.
 * Exit 0 on a clean run; 2 on a usage or I/O error (never on a give-up --
 * a give-up is a DATA point for this instrument, not a driver failure).
 *
 * Usage: tier_escalation_driver <search|whole> <id-path-list>
 * Build (mirrors tests/codegen/tier_driver.c's invocation):
 *   gcc -O2 -I<dir> -DRX_TEST_TIER_HOOK -o driver tier_escalation_driver.c <dir>/gen.c
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

#if !defined(RX_TEST_TIER_HOOK)
#error "tier_escalation_driver.c must be built with -DRX_TEST_TIER_HOOK, exactly like tests/codegen/tier_driver.c"
#endif

/* The artifact's escalation hook. Defined HERE, never in the artifact
 * (match_api.md section 5.3: no mutable state of the artifact's own). */
static unsigned long escalations;
void rx_tier_escalated(void);
void rx_tier_escalated(void) { escalations++; }

static unsigned char *slurp(const char *path, size_t *len_out)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "tier_escalation_driver: %s: %s\n", path, strerror(errno));
        return NULL;
    }
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return NULL; }
    if (fseek(f, 0, SEEK_SET) != 0) { fclose(f); return NULL; }
    unsigned char *buf = malloc((size_t)sz > 0 ? (size_t)sz : 1);
    if (!buf) { fclose(f); return NULL; }
    size_t got = sz > 0 ? fread(buf, 1, (size_t)sz, f) : 0;
    fclose(f);
    if (got != (size_t)sz) {
        fprintf(stderr, "tier_escalation_driver: %s: short read (%zu of %ld bytes)\n",
                path, got, sz);
        free(buf);
        return NULL;
    }
    *len_out = (size_t)sz;
    return buf;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s <search|whole> <id-path-list>\n",
                argc > 0 ? argv[0] : "tier_escalation_driver");
        return 2;
    }
    int whole;
    if      (strcmp(argv[1], "search") == 0) whole = 0;
    else if (strcmp(argv[1], "whole")  == 0) whole = 1;
    else { fprintf(stderr, "tier_escalation_driver: unknown form '%s' (want search|whole)\n", argv[1]); return 2; }

    FILE *lf = fopen(argv[2], "r");
    if (!lf) {
        fprintf(stderr, "tier_escalation_driver: %s: %s\n", argv[2], strerror(errno));
        return 2;
    }

    ptrdiff_t caps[RX_NCAPS][2];
    char line[8192];
    long nlines = 0;
    while (fgets(line, sizeof line, lf)) {
        nlines++;
        char *nl = strchr(line, '\n');
        if (nl) *nl = 0;
        if (!*line) continue;
        char *tab = strchr(line, '\t');
        if (!tab) {
            fprintf(stderr, "tier_escalation_driver: %s:%ld: no tab (want <id>\\t<path>)\n",
                    argv[2], nlines);
            fclose(lf);
            return 2;
        }
        *tab = 0;
        const char *id = line, *path = tab + 1;

        size_t len = 0;
        unsigned char *s = slurp(path, &len);
        if (!s) { fclose(lf); return 2; }

        escalations = 0;
        const char *outcome;
        char giveupbuf[32];

        if (!whole) {
            int r = rx_search(s, len, 0, caps);
            if (r == 1)      outcome = "match";
            else if (r == 0) outcome = "nomatch";
            else {
                snprintf(giveupbuf, sizeof giveupbuf, "giveup:%d", r);
                outcome = giveupbuf;
            }
        } else {
            rx_ctx ctx;
            ctx.subject = s;
            ctx.len = len;
            ctx.pos = 0;
            ctx.ncap = 0;
            ctx.caps = NULL;
            ctx.user = NULL;
            ptrdiff_t r = rx_match_caps(&ctx, caps);
            if (r == -1)      outcome = "nomatch";
            else if (r < -1) {
                snprintf(giveupbuf, sizeof giveupbuf, "giveup:%td", r);
                outcome = giveupbuf;
            } else if ((size_t)r == len) outcome = "match";
            else                          outcome = "prefix";
        }

        printf("row %s %zu %d %s\n", id, len, escalations > 0 ? 1 : 0, outcome);
        free(s);
    }
    fclose(lf);
    return 0;
}
