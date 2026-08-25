/* sr_driver.c -- the [DD-14.D27] blinded author's OWN test driver.
 *
 * Re-derived from docs/testing.md "The driver protocol" alone (the project's
 * own tests/harness/driver.c is denied to this author by D27 and was never
 * seen). Shape, per that document:
 *
 *     t <subject> [startpos]
 *
 * <subject> carries the .rxt file's escapes still encoded as literal
 * backslash sequences; this program decodes them into a byte buffer,
 * tracking length explicitly (a decoded subject may contain NUL, so strlen
 * is never used on the result). An invalid escape exits 2.
 *
 * On a match it prints `match` followed by every caps[k][0] caps[k][1] pair
 * for k in [0, RX_NCAPS); on no match `nomatch`; exit 0 either way. On a
 * typed give-up (a negative sentinel in [PCREC_ERR_FLOOR,-2]) it prints the
 * code's word -- steps/frames/work/recurse -- and exits 3; on the
 * below-the-floor PCREC_ERR_INTERNAL it prints `internal` and exits 3; an
 * unrecognized negative prints `giveup <N>` and exits 3.
 *
 * This driver exists so the author can ask two EXISTENCE questions D27
 * permits -- is this cell refused, and does this deep cell give up -- never
 * to source a match expectation, which only libpcre2 10.46 may do.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "gen.h"

static int hexval(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Decode the .rxt escape set, and ONLY that set: \" \\ \n \t \r \f \v \xHH. */
static size_t decode(const char *in, unsigned char *out) {
    size_t n = 0;
    for (const char *p = in; *p; ) {
        if (*p != '\\') { out[n++] = (unsigned char)*p++; continue; }
        p++;
        switch (*p) {
        case '"':  out[n++] = '"';  p++; break;
        case '\\': out[n++] = '\\'; p++; break;
        case 'n':  out[n++] = '\n'; p++; break;
        case 't':  out[n++] = '\t'; p++; break;
        case 'r':  out[n++] = '\r'; p++; break;
        case 'f':  out[n++] = '\f'; p++; break;
        case 'v':  out[n++] = '\v'; p++; break;
        case 'x': {
            int hi = hexval((unsigned char)p[1]);
            int lo = hi < 0 ? -1 : hexval((unsigned char)p[2]);
            if (lo < 0) {
                fprintf(stderr, "bad \\xHH escape\n");
                exit(2);
            }
            out[n++] = (unsigned char)(hi * 16 + lo);
            p += 3;
            break;
        }
        default:
            fprintf(stderr, "invalid escape \\%c\n", *p ? *p : '?');
            exit(2);
        }
    }
    return n;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: t <subject> [startpos]\n"); return 2; }
    size_t inlen = strlen(argv[1]);
    unsigned char *buf = malloc(inlen + 1);
    if (!buf) return 2;
    size_t len = decode(argv[1], buf);

    size_t startpos = 0;
    if (argc > 2) {
        char *end = NULL;
        long long v = strtoll(argv[2], &end, 10);
        if (!end || *end || v < 0) { fprintf(stderr, "bad startpos\n"); return 2; }
        startpos = (size_t)v;
    }

    ptrdiff_t caps[RX_NCAPS][2];
    int rc = rx_search(buf, len, startpos, caps);
    if (rc > 0) {
        fputs("match", stdout);
        for (int k = 0; k < RX_NCAPS; k++)
            printf(" %td %td", caps[k][0], caps[k][1]);
        putchar('\n');
        return 0;
    }
    if (rc == 0) { puts("nomatch"); return 0; }
    switch (rc) {
    case PCREC_ERR_STEPS:    puts("steps");    break;
    case PCREC_ERR_FRAMES:   puts("frames");   break;
    case PCREC_ERR_WORK:     puts("work");     break;
    case PCREC_ERR_RECURSE:  puts("recurse");  break;
    case PCREC_ERR_INTERNAL: puts("internal"); break;
    default: printf("giveup %d\n", rc); break;
    }
    return 3;
}
