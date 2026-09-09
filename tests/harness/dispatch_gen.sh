# tests/harness/dispatch_gen.sh — [TT-4M] STEP 2c HARNESS_BATCH's dispatch.c
# generator. Sourced by run.sh; defines ONE function, gen_dispatch_c.
#
# Ported from studies/tt4m_batchrun/dispatch_gen.py (the STEP 1/2a prototype),
# not re-derived: same DECODE_C shape (byte-identical to driver.c's decode(),
# including the R55-6 fix for a trailing lone backslash), same give-up-word
# switch (steps/frames/work/recurse/internal, falling back to "giveup %d" for
# an unnamed negative code — driver.c's own fallback), same argv shape
# (`<index> <subject> [startpos]`), same DEFAULT-ROUTE-ONLY scope limit
# (docs/design/tt4m_harness_batching.md item 2 / R55-1's third exclusion: a
# block carrying a routed cell never reaches a batch, so nothing here needs
# to model `_search_in`/`_match_in`). Kept in bash rather than python so
# run.sh's own dependency profile (bash + gcc, no python3) does not grow for
# an opt-in axis.
#
# gen_dispatch_c PREFIX [PREFIX ...] — writes dispatch.c to STDOUT. The
# selector is an ARGV INDEX into the prefix list IN THE ORDER GIVEN (the same
# order the caller compiled them in) — kept by-name-lookup-compatible for
# [V-E]'s later implement-then-replace (the design note's item 2): the
# call site always asks for "the Nth member of this batch", and whether that
# resolves through this hand-rolled `switch` or a generated array indexing
# later is invisible to run.sh.

gen_dispatch_c() {
    local -a prefixes=("$@")
    local p up i n="${#prefixes[@]}"

    printf '#include <ctype.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n'
    for p in "${prefixes[@]}"; do
        printf '#include "%s.h"\n' "$p"
    done

    # DECODE_C, transliterated from dispatch_gen.py's own DECODE_C constant.
    cat <<'DISPATCH_DECODE_EOF'

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
        if (src[i] == '\\' && i + 1 >= srclen) {
            fprintf(stderr, "dispatch: trailing backslash in subject\n");
            free(buf);
            return NULL;
        }
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
DISPATCH_DECODE_EOF

    printf 'int main(int argc, char **argv) {\n'
    printf '    if (argc != 3 && argc != 4) {\n'
    printf '        fprintf(stderr, "usage: %%s <index> <subject> [startpos]\\n", argc > 0 ? argv[0] : "dispatch");\n'
    printf '        return 2;\n    }\n'
    printf '    int index = atoi(argv[1]);\n'
    printf '    size_t startpos = 0;\n'
    printf '    if (argc == 4 && parse_startpos(argv[3], &startpos) != 0) return 2;\n'
    printf '    size_t len = 0;\n    unsigned char *buf = decode(argv[2], &len);\n    if (!buf) return 2;\n'
    printf '    int found;\n'
    printf '    switch (index) {\n'
    for i in "${!prefixes[@]}"; do
        p="${prefixes[$i]}"
        up="$(printf '%s' "$p" | LC_ALL=C tr '[:lower:]' '[:upper:]')"
        printf '    case %d: {\n' "$i"
        printf '        ptrdiff_t caps[%s_NCAPS][2];\n' "$up"
        printf '        found = %s_search(buf, len, startpos, caps);\n' "$p"
        printf '        if (found == 1) {\n'
        printf '            printf("match");\n'
        printf '            for (int k = 0; k < %s_NCAPS; k++) printf(" %%td %%td", caps[k][0], caps[k][1]);\n' "$up"
        printf '            printf("\\n");\n'
        printf '        } else if (found == 0) {\n'
        printf '            printf("nomatch\\n");\n'
        printf '        } else {\n'
        printf '            const char *word = found == PCREC_ERR_STEPS    ? "steps"\n'
        printf '                              : found == PCREC_ERR_FRAMES   ? "frames"\n'
        printf '                              : found == PCREC_ERR_WORK     ? "work"\n'
        printf '                              : found == PCREC_ERR_RECURSE  ? "recurse"\n'
        printf '                              : found == PCREC_ERR_INTERNAL ? "internal"\n'
        printf '                              : NULL;\n'
        printf '            if (word) printf("%%s\\n", word); else printf("giveup %%d\\n", found);\n'
        printf '            free(buf); return 3;\n        }\n'
        printf '        break;\n    }\n'
    done
    printf '    default:\n'
    printf '        fprintf(stderr, "dispatch: index %%d out of range [0,%d)\\n", index);\n' "$n"
    printf '        free(buf); return 2;\n'
    printf '    }\n'
    printf '    free(buf);\n    return 0;\n}\n'
}
