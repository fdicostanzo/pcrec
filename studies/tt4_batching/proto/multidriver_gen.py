#!/usr/bin/env python3
"""studies/tt4_batching/proto/multidriver_gen.py — [TT-4.1] Stage A2
exec-cost prototype: emits a ONE-PATTERN driver that reads ALL its cases
from STDIN (one "subject<TAB>startpos" per line) and processes them in a
loop inside a SINGLE process, rather than tests/harness/driver.c's shape
of one process per case (which is what tests/harness/run.sh actually
does: a fresh `timeout ... "$bdir/t" "$subj" "$pos"` exec per m/n/ms/ns
line). Same decode/match/nomatch/steps/frames protocol and exit-code
conventions as driver.c, applied once per input line; overall process
exit status is 0 unless a line was malformed (matching driver.c's own
argv-parsing exit 2 for a bad line, reported per-line to stderr but not
fatal to the rest of the batch, since the point of this driver is
throughput, not being a stricter checker than the harness already is
elsewhere). A tiny, purpose-built copy -- NEVER tests/harness/driver.c
itself, which the harness's own correctness the census/bench code already
depends on staying untouched.

Usage: multidriver_gen.py PREFIX > drv.c   (compiled against PREFIX.h)
"""
import sys

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
    if (!buf) return NULL;
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
                    } else { free(buf); return NULL; }
                    break;
                default: free(buf); return NULL;
            }
        } else {
            buf[o++] = (unsigned char)src[i++];
        }
    }
    *out_len = o;
    return buf;
}
'''

def main():
    if len(sys.argv) != 2:
        print("usage: multidriver_gen.py PREFIX", file=sys.stderr)
        sys.exit(2)
    prefix = sys.argv[1]
    up = prefix.upper()

    out = []
    out.append('#include <ctype.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n')
    out.append(f'#include "{prefix}.h"\n')
    out.append(DECODE_C)
    out.append('int main(void) {\n')
    out.append('    char line[65536];\n')
    out.append('    while (fgets(line, sizeof(line), stdin)) {\n')
    out.append('        char *nl = strchr(line, \'\\n\'); if (nl) *nl = 0;\n')
    out.append('        char *tab = strchr(line, \'\\t\');\n')
    out.append('        if (!tab) { fprintf(stderr, "multidriver: malformed line: %s\\n", line); continue; }\n')
    out.append('        *tab = 0;\n')
    out.append('        const char *subj_raw = line;\n')
    out.append('        size_t startpos = (size_t)atol(tab + 1);\n')
    out.append('        size_t len = 0;\n')
    out.append('        unsigned char *buf = decode(subj_raw, &len);\n')
    out.append('        if (!buf) { fprintf(stderr, "multidriver: bad escape: %s\\n", subj_raw); continue; }\n')
    out.append(f'        ptrdiff_t caps[{up}_NCAPS][2];\n')
    out.append(f'        int found = {prefix}_search(buf, len, startpos, caps);\n')
    out.append('        if (found == 1) {\n')
    out.append('            printf("match");\n')
    out.append(f'            for (int k = 0; k < {up}_NCAPS; k++) printf(" %td %td", caps[k][0], caps[k][1]);\n')
    out.append('            printf("\\n");\n')
    out.append('        } else if (found == 0) {\n')
    out.append('            printf("nomatch\\n");\n')
    out.append('        } else {\n')
    out.append('            printf("%s\\n", found == PCREC_ERR_STEPS ? "steps" : "frames");\n')
    out.append('        }\n')
    out.append('        free(buf);\n')
    out.append('    }\n')
    out.append('    return 0;\n}\n')

    sys.stdout.write("".join(out))

if __name__ == "__main__":
    main()
