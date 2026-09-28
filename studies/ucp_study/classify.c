/* classify.c -- which code points does each pattern match as a single
 * character, under PCRE2_UTF and under PCRE2_UTF|PCRE2_UCP?  Prints, per
 * (pattern, flags), the member count and the interval list (one line), so
 * two library versions can be diffed.  Patterns are read one per line from
 * stdin and anchored as ^(?:P)$ by the probe.  Surrogates are skipped. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>

static int enc(unsigned cp, unsigned char *b) {
    if (cp < 0x80) { b[0] = cp; return 1; }
    if (cp < 0x800) { b[0] = 0xC0 | cp >> 6; b[1] = 0x80 | (cp & 63); return 2; }
    if (cp < 0x10000) { b[0] = 0xE0 | cp >> 12; b[1] = 0x80 | ((cp >> 6) & 63);
                        b[2] = 0x80 | (cp & 63); return 3; }
    b[0] = 0xF0 | cp >> 18; b[1] = 0x80 | ((cp >> 12) & 63);
    b[2] = 0x80 | ((cp >> 6) & 63); b[3] = 0x80 | (cp & 63); return 4;
}

int main(void) {
    char line[512];
    static const struct { const char *name; uint32_t opt; } modes[] = {
        { "UTF", PCRE2_UTF }, { "UTF|UCP", PCRE2_UTF | PCRE2_UCP } };
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = 0;
        if (!line[0] || line[0] == '#') continue;
        char pat[600];
        snprintf(pat, sizeof pat, "^(?:%s)$", line);
        for (int m = 0; m < 2; m++) {
            int err; PCRE2_SIZE eo;
            pcre2_code *re = pcre2_compile((PCRE2_SPTR)pat, PCRE2_ZERO_TERMINATED,
                                           modes[m].opt, &err, &eo, NULL);
            if (!re) { printf("%s\t%s\tCOMPILE-ERROR %d\n", line, modes[m].name, err); continue; }
            pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
            unsigned long n = 0; long lo = -1; unsigned prev = 0;
            printf("%s\t%s\t", line, modes[m].name);
            char ivs[1 << 16]; size_t il = 0; ivs[0] = 0; int trunc = 0;
            for (unsigned cp = 0; cp <= 0x10FFFF; cp++) {
                if (cp >= 0xD800 && cp <= 0xDFFF) continue;
                unsigned char b[4]; int k = enc(cp, b);
                int hit = pcre2_match(re, b, k, 0, 0, md, NULL) >= 0;
                if (hit) { n++; if (lo < 0) lo = cp; prev = cp; }
                if ((!hit || cp == 0x10FFFF) && lo >= 0) {
                    unsigned hi = hit ? cp : prev;
                    if (!(cp == 0xE000 && prev == 0xD7FF && hit)) {
                        if (il < sizeof ivs - 40) il += snprintf(ivs + il, sizeof ivs - il, "%lX-%X,", lo, hi);
                        else trunc = 1;
                        lo = -1;
                    }
                }
            }
            printf("%lu\t%s%s\n", n, ivs, trunc ? "TRUNC" : "");
            pcre2_match_data_free(md); pcre2_code_free(re);
        }
    }
    return 0;
}
