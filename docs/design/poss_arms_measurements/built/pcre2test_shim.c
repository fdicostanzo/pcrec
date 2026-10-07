/* Minimal stand-in for `pcre2test -q` for the rev-2.1 generators' MEMBERSHIP
 * probes only (gen_a21.py / gen_a021.py `member()`): the box has libpcre2-8
 * 10.46 (the reference) but no pcre2test binary.  Input groups:
 *     "PATTERN"mod,mod      (mods among i, ucp, utf)
 *     \x{HEX}... subject    (\x{..} escapes; UTF-8 under utf, else a byte)
 *     <blank>
 * Output per group: " 0: <subject>" on a match, "No match" otherwise,
 * "Failed: <msg>" on a compile error.  Not a general pcre2test. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static int enc(unsigned c, int utf, unsigned char *o) {
    if (!utf || c < 0x80) { o[0] = (unsigned char)c; return 1; }
    if (c < 0x800) { o[0] = 0xC0 | (c >> 6); o[1] = 0x80 | (c & 63); return 2; }
    if (c < 0x10000) { o[0] = 0xE0 | (c >> 12); o[1] = 0x80 | ((c >> 6) & 63); o[2] = 0x80 | (c & 63); return 3; }
    o[0] = 0xF0 | (c >> 18); o[1] = 0x80 | ((c >> 12) & 63); o[2] = 0x80 | ((c >> 6) & 63); o[3] = 0x80 | (c & 63); return 4;
}
int main(void) {
    char line[8192]; pcre2_code *re = NULL; int utf = 0;
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = 0;
        if (!*line) continue;
        if (line[0] == '"') {
            char *q = strrchr(line, '"'); *q = 0; char *mods = q + 1;
            uint32_t opt = 0; utf = 0;
            for (char *t = strtok(mods, ","); t; t = strtok(NULL, ",")) {
                if (!strcmp(t, "i")) opt |= PCRE2_CASELESS;
                else if (!strcmp(t, "ucp")) opt |= PCRE2_UCP;
                else if (!strcmp(t, "utf")) { opt |= PCRE2_UTF; utf = 1; }
            }
            int ec; PCRE2_SIZE eo;
            if (re) pcre2_code_free(re);
            re = pcre2_compile((PCRE2_SPTR)line + 1, PCRE2_ZERO_TERMINATED, opt, &ec, &eo, NULL);
            if (!re) { printf("Failed: error %d at offset %zu\n", ec, (size_t)eo); }
            continue;
        }
        if (!re) continue;
        unsigned char sub[4096]; size_t n = 0;
        for (char *p = line; *p;) {
            if (!strncmp(p, "\\x{", 3)) { unsigned c = strtoul(p + 3, &p, 16); if (*p == '}') p++; n += enc(c, utf, sub + n); }
            else sub[n++] = (unsigned char)*p++;
        }
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        int rc = pcre2_match(re, sub, n, 0, 0, md, NULL);
        if (rc >= 0) { fputs(" 0: ", stdout); fwrite(sub, 1, n, stdout); putchar('\n'); }
        else puts("No match");
        pcre2_match_data_free(md);
    }
    return 0;
}
