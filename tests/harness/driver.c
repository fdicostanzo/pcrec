/*
 * driver.c — runs a single generated matcher against one subject string.
 *
 * Usage: t <subject>
 *   <subject> is the inner text of a .rxt `m`/`n` line's double-quoted
 *   subject, with surrounding quotes already stripped by run.sh but its
 *   escapes (\" \\ \n \t \r \f \v \xHH) still encoded as literal
 *   backslash sequences — this program decodes them.
 *
 * Prints exactly one line to stdout:
 *   "match %zu %zu\n"   (rx_search found a match: start, end)
 *   "nomatch\n"         (rx_search found no match)
 * and exits 0. On a malformed escape in argv[1], prints a message to
 * stderr and exits 2.
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

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s <subject>\n", argc > 0 ? argv[0] : "t");
        return 2;
    }

    size_t len = 0;
    unsigned char *buf = decode(argv[1], &len);
    if (!buf) return 2;

    rx_span m;
    int found = rx_search(buf, len, 0, &m);
    if (found) {
        printf("match %zu %zu\n", m.start, m.end);
    } else {
        printf("nomatch\n");
    }

    free(buf);
    return 0;
}
