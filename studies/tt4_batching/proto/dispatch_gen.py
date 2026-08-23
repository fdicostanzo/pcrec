#!/usr/bin/env python3
"""studies/tt4_batching/proto/dispatch_gen.py — [TT-4.1] Stage B dispatcher.

Emits a small C driver that reproduces tests/harness/driver.c's protocol
(decode escapes, call rx_search, print "match S E [S E ...]" / "nomatch" /
"steps"/"frames", same exit codes 0/2/3) but SELECTS which matcher to call
by an integer index (argv[1]), out of a batch of N distinctly-prefixed
matchers (rx0000_search, rx0001_search, ...) compiled into the same binary
-- shapes (A) link-batching and (B) TU-batching both need this; shape (C),
the one-shot baseline, links driver.c itself unmodified against exactly one
matcher and never sees this file.

Usage: dispatch_gen.py PREFIX [PREFIX ...] > dispatch.c
   or: dispatch_gen.py --manifest manifest.tsv > dispatch.c
"""
import sys
import argparse

DECODE_C = r'''
static int hexval(unsigned char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static unsigned char *decode(const char *src, size_t *out_len) {
    size_t srclen = strlen(src);
    unsigned char *buf = malloc(srclen > 0 ? srclen : 1);
    if (!buf) { fprintf(stderr, "dispatch: out of memory\n"); return NULL; }
    size_t o = 0;
    for (size_t i = 0; i < srclen; ) {
        if (src[i] == '\\' && i + 1 < srclen) {
            char c = src[i + 1];
            switch (c) {
                case '"': buf[o++] = '"'; i += 2; break;
                case '\\': buf[o++] = '\\'; i += 2; break;
                case 'n': buf[o++] = '\n'; i += 2; break;
                case 't': buf[o++] = '\t'; i += 2; break;
                case 'r': buf[o++] = '\r'; i += 2; break;
                case 'f': buf[o++] = '\f'; i += 2; break;
                case 'v': buf[o++] = '\v'; i += 2; break;
                case 'x':
                    if (i + 3 < srclen + 1 && isxdigit((unsigned char)src[i+2]) && isxdigit((unsigned char)src[i+3])) {
                        int hi = hexval((unsigned char)src[i+2]), lo = hexval((unsigned char)src[i+3]);
                        buf[o++] = (unsigned char)((hi << 4) | lo);
                        i += 4;
                    } else {
                        fprintf(stderr, "dispatch: malformed \\x escape\n");
                        free(buf); return NULL;
                    }
                    break;
                default:
                    fprintf(stderr, "dispatch: unknown escape \\%c\n", c);
                    free(buf); return NULL;
            }
        } else {
            buf[o++] = (unsigned char)src[i++];
        }
    }
    *out_len = o;
    return buf;
}

static int parse_startpos(const char *s, size_t *out) {
    if (!s || !*s) return -1;
    size_t v = 0;
    for (const char *q = s; *q; q++) {
        if (*q < '0' || *q > '9') return -1;
        v = v * 10 + (size_t)(*q - '0');
    }
    *out = v;
    return 0;
}
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=None)
    ap.add_argument("prefixes", nargs="*")
    args = ap.parse_args()

    prefixes = list(args.prefixes)
    if args.manifest:
        with open(args.manifest) as f:
            header = f.readline()
            for line in f:
                prefixes.append(line.split("\t", 1)[0])

    if not prefixes:
        print("dispatch_gen.py: no prefixes given", file=sys.stderr)
        sys.exit(2)

    out = []
    out.append('#include <ctype.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n')
    for p in prefixes:
        out.append(f'#include "{p}.h"\n')
    out.append(DECODE_C)
    out.append('int main(int argc, char **argv) {\n')
    out.append('    if (argc != 3 && argc != 4) {\n')
    out.append('        fprintf(stderr, "usage: %s <index> <subject> [startpos]\\n", argc > 0 ? argv[0] : "dispatch");\n')
    out.append('        return 2;\n    }\n')
    out.append('    int index = atoi(argv[1]);\n')
    out.append('    size_t startpos = 0;\n')
    out.append('    if (argc == 4 && parse_startpos(argv[3], &startpos) != 0) return 2;\n')
    out.append('    size_t len = 0;\n    unsigned char *buf = decode(argv[2], &len);\n    if (!buf) return 2;\n')
    out.append('    int found;\n')
    out.append('    switch (index) {\n')
    for i, p in enumerate(prefixes):
        up = p.upper()
        out.append(f'    case {i}: {{\n')
        out.append(f'        ptrdiff_t caps[{up}_NCAPS][2];\n')
        out.append(f'        found = {p}_search(buf, len, startpos, caps);\n')
        out.append('        if (found == 1) {\n')
        out.append('            printf("match");\n')
        out.append(f'            for (int k = 0; k < {up}_NCAPS; k++) printf(" %td %td", caps[k][0], caps[k][1]);\n')
        out.append('            printf("\\n");\n')
        out.append('        } else if (found == 0) {\n')
        out.append('            printf("nomatch\\n");\n')
        out.append('        } else {\n')
        out.append('            printf("%s\\n", found == PCREC_ERR_STEPS ? "steps" : "frames");\n')
        out.append('            free(buf); return 3;\n        }\n')
        out.append('        break;\n    }\n')
    out.append('    default:\n')
    out.append(f'        fprintf(stderr, "dispatch: index %d out of range [0,{len(prefixes)})\\n", index);\n')
    out.append('        free(buf); return 2;\n')
    out.append('    }\n')
    out.append('    free(buf);\n    return 0;\n}\n')

    sys.stdout.write("".join(out))

if __name__ == "__main__":
    main()
