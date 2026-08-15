/*
 * driver.c — runs a single generated matcher against one subject string.
 *
 * Usage: t <subject> [startpos]
 *   <subject> is the inner text of a .rxt `m`/`n`/`ms`/`ns` line's
 *   double-quoted subject, with surrounding quotes already stripped by
 *   run.sh but its escapes (\" \\ \n \t \r \f \v \xHH) still encoded as
 *   literal backslash sequences — this program decodes them.
 *   [startpos] is an optional non-negative decimal integer passed as
 *   rx_search's startpos argument; if omitted, startpos defaults to 0
 *   (the `m`/`n` directives always mean startpos 0; `ms`/`ns` pass it
 *   explicitly — see docs/testing.md).
 *
 * Prints exactly one line to stdout:
 *   "match %td %td [%td %td ...]\n"
 *                       (rx_search found a match: caps[0][0], caps[0][1] —
 *                        the whole-match span, [M4.4]/D44.2's caps-array
 *                        search signature — followed by caps[k][0]/caps[k][1]
 *                        for every k in [1, RX_NCAPS), [M4.5a]: today
 *                        RX_NCAPS is always 1 on a DFA-compiled artifact, so
 *                        the line is exactly "match %td %td\n" as before —
 *                        this is a superset, not a reshape. A .rxt `g`/`gp`
 *                        capture-expectation line picks its slot's pair out
 *                        of these fields by position; see docs/testing.md)
 *   "nomatch\n"         (rx_search found no match)
 * and exits 0. On a malformed escape in argv[1] or a malformed [startpos],
 * prints a message to stderr and exits 2.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

static int hexval(unsigned char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/*
 * Decode escapes from src into a freshly malloc'd buffer. *out_len is set
 * to the decoded length (tracked explicitly; the buffer may contain \0
 * bytes, so it must never be measured with strlen). Returns the buffer,
 * or NULL on a malformed escape (message already printed to stderr).
 */
static unsigned char *decode(const char *src, size_t *out_len) {
    size_t srclen = strlen(src);
    /* Decoded output is never longer than the source. */
    unsigned char *buf = malloc(srclen > 0 ? srclen : 1);
    if (!buf) {
        fprintf(stderr, "driver: out of memory\n");
        return NULL;
    }

    size_t n = 0;
    for (size_t i = 0; i < srclen; i++) {
        unsigned char c = (unsigned char)src[i];
        if (c != '\\') {
            buf[n++] = c;
            continue;
        }
        i++;
        if (i >= srclen) {
            fprintf(stderr, "driver: trailing backslash in subject\n");
            free(buf);
            return NULL;
        }
        unsigned char e = (unsigned char)src[i];
        switch (e) {
            case '"':  buf[n++] = '"';  break;
            case '\\': buf[n++] = '\\'; break;
            case 'n':  buf[n++] = '\n'; break;
            case 't':  buf[n++] = '\t'; break;
            case 'r':  buf[n++] = '\r'; break;
            case 'f':  buf[n++] = '\f'; break;
            case 'v':  buf[n++] = '\v'; break;
            case 'x': {
                if (i + 2 >= srclen) {
                    fprintf(stderr, "driver: incomplete \\x escape\n");
                    free(buf);
                    return NULL;
                }
                int hi = hexval((unsigned char)src[i + 1]);
                int lo = hexval((unsigned char)src[i + 2]);
                if (hi < 0 || lo < 0) {
                    fprintf(stderr, "driver: invalid \\x escape\n");
                    free(buf);
                    return NULL;
                }
                buf[n++] = (unsigned char)((hi << 4) | lo);
                i += 2;
                break;
            }
            default:
                fprintf(stderr, "driver: invalid escape '\\%c'\n", e);
                free(buf);
                return NULL;
        }
    }

    *out_len = n;
    return buf;
}

/*
 * Parse a startpos argument: must be all decimal digits (at least one),
 * fitting in a size_t. Returns 0 on success with *out set, -1 on a
 * malformed argument (message already printed to stderr).
 */
static int parse_startpos(const char *s, size_t *out) {
    if (!s || !*s) {
        fprintf(stderr, "driver: empty startpos argument\n");
        return -1;
    }
    size_t v = 0;
    for (const char *q = s; *q; q++) {
        if (*q < '0' || *q > '9') {
            fprintf(stderr, "driver: invalid startpos argument '%s'\n", s);
            return -1;
        }
        v = v * 10 + (size_t)(*q - '0');
    }
    *out = v;
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 2 && argc != 3) {
        fprintf(stderr, "usage: %s <subject> [startpos]\n", argc > 0 ? argv[0] : "t");
        return 2;
    }

    size_t startpos = 0;
    if (argc == 3 && parse_startpos(argv[2], &startpos) != 0) return 2;

    size_t len = 0;
    unsigned char *buf = decode(argv[1], &len);
    if (!buf) return 2;

    ptrdiff_t caps[RX_NCAPS][2];
    int found = rx_search(buf, len, startpos, caps);
    if (found) {
        printf("match");
        for (int k = 0; k < RX_NCAPS; k++) {
            printf(" %td %td", caps[k][0], caps[k][1]);
        }
        printf("\n");
    } else {
        printf("nomatch\n");
    }

    free(buf);
    return 0;
}
