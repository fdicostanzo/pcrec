/* tests/vm/vm_driver.c — runs ONE generated capture-delivering matcher
 * against one subject and prints every capture slot.
 *
 * Deliberately NOT tests/harness/driver.c: that one is the .rxt corpus's
 * driver, it prints caps[0] only, and the .rxt format's capture-expectation
 * columns are a SIBLING LANE's work ([M4.5a]). This lane validates its
 * emitter against python `re` through its own channel so the two can land
 * independently; the shared corpus over the shared format comes after both
 * merge. Nothing here is a second implementation of anything the harness
 * owns — it is a printf over the ABI.
 *
 * Usage: vm_driver <subject> [startpos]
 *   <subject> uses the same backslash escapes tests/harness/driver.c decodes
 *   (\" \\ \n \t \r \f \v \xHH), so a subject with NUL bytes or a newline can
 *   be passed as one argv element.
 *
 * Prints one line:
 *   "match S0 E0 S1 E1 ... Sk Ek"   (RX_NCAPS pairs, unset spelled -1 -1)
 *   "nomatch"
 *   "err_steps"  / "err_frames"     (the engine gave up, honestly)
 * and exits 0. A malformed argument exits 2.
 *
 * Also exercises <prefix>_match_caps at the reported start when
 * VM_CHECK_ANCHORED is defined, which is how the anchored entry gets covered
 * by the same cases rather than by a second corpus. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

static int hexval(unsigned char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static unsigned char *decode(const char *src, size_t *out_len)
{
    size_t srclen = strlen(src);
    unsigned char *buf = malloc(srclen > 0 ? srclen : 1);
    if (!buf) { fprintf(stderr, "vm_driver: out of memory\n"); return NULL; }
    size_t n = 0;
    for (size_t i = 0; i < srclen; i++) {
        unsigned char c = (unsigned char)src[i];
        if (c != '\\') { buf[n++] = c; continue; }
        if (++i >= srclen) {
            fprintf(stderr, "vm_driver: trailing backslash\n");
            free(buf);
            return NULL;
        }
        switch ((unsigned char)src[i]) {
        case 'n': buf[n++] = '\n'; break;
        case 't': buf[n++] = '\t'; break;
        case 'r': buf[n++] = '\r'; break;
        case 'f': buf[n++] = '\f'; break;
        case 'v': buf[n++] = '\v'; break;
        case '\\': buf[n++] = '\\'; break;
        case '"': buf[n++] = '"'; break;
        case 'x': {
            if (i + 2 >= srclen) {
                fprintf(stderr, "vm_driver: short \\x escape\n");
                free(buf);
                return NULL;
            }
            int hi = hexval((unsigned char)src[i + 1]);
            int lo = hexval((unsigned char)src[i + 2]);
            if (hi < 0 || lo < 0) {
                fprintf(stderr, "vm_driver: bad \\x escape\n");
                free(buf);
                return NULL;
            }
            buf[n++] = (unsigned char)(hi * 16 + lo);
            i += 2;
            break;
        }
        default:
            fprintf(stderr, "vm_driver: unknown escape \\%c\n", src[i]);
            free(buf);
            return NULL;
        }
    }
    *out_len = n;
    return buf;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: vm_driver <subject> [startpos]\n");
        return 2;
    }
    size_t len = 0;
    unsigned char *subj = decode(argv[1], &len);
    if (!subj) return 2;

    size_t startpos = 0;
    if (argc > 2) {
        char *end = NULL;
        unsigned long v = strtoul(argv[2], &end, 10);
        if (!end || *end) {
            fprintf(stderr, "vm_driver: bad startpos '%s'\n", argv[2]);
            free(subj);
            return 2;
        }
        startpos = (size_t)v;
    }

    ptrdiff_t caps[RX_NCAPS][2];
    for (int k = 0; k < RX_NCAPS; k++) caps[k][0] = caps[k][1] = -2;

    int r = rx_search(subj, len, startpos, caps);
    if (r == RX_ERR_STEPS)  { printf("err_steps\n");  free(subj); return 0; }
    if (r == RX_ERR_FRAMES) { printf("err_frames\n"); free(subj); return 0; }
    if (r != 1)             { printf("nomatch\n");    free(subj); return 0; }

    printf("match");
    for (int k = 0; k < RX_NCAPS; k++)
        printf(" %td %td", caps[k][0], caps[k][1]);
    printf("\n");

#ifdef VM_CHECK_ANCHORED
    /* The anchored capture-delivering entry must agree with the search entry
     * on every slot when asked at the search's own reported start — same
     * engine, same program, one fewer scan. A disagreement here is a bug in
     * the entry layering (§4.4's three layers), not in the program. */
    {
        ptrdiff_t acaps[RX_NCAPS][2];
        rx_ctx ctx;
        ctx.subject = subj;
        ctx.len = len;
        ctx.pos = (size_t)caps[0][0];
        ctx.ncap = 0;
        ctx.caps = NULL;
        ctx.user = NULL;
        for (int k = 0; k < RX_NCAPS; k++) acaps[k][0] = acaps[k][1] = -2;
        ptrdiff_t ar = rx_match_caps(&ctx, acaps);
        if (ar != caps[0][1] - caps[0][0]) {
            fprintf(stderr, "vm_driver: match_caps length %td != search %td\n",
                    ar, caps[0][1] - caps[0][0]);
            free(subj);
            return 3;
        }
        for (int k = 0; k < RX_NCAPS; k++)
            if (acaps[k][0] != caps[k][0] || acaps[k][1] != caps[k][1]) {
                fprintf(stderr, "vm_driver: match_caps slot %d (%td,%td) != "
                                "search (%td,%td)\n",
                        k, acaps[k][0], acaps[k][1], caps[k][0], caps[k][1]);
                free(subj);
                return 3;
            }
        /* and the capture-DROPPING export must agree on the length */
        ptrdiff_t mr = rx_match(&ctx);
        if (mr != ar) {
            fprintf(stderr, "vm_driver: match %td != match_caps %td\n", mr, ar);
            free(subj);
            return 3;
        }
    }
#endif

    free(subj);
    return 0;
}
