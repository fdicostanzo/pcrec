/* vlbrev1 probe (vlbrev3 copy): stdin lines "pattern<TAB>subject[<TAB>startpos]"; argv[1] = c|m,
   argv[2] optional flags: "u" PCRE2_UTF, "i" PCRE2_UTF|PCRE2_MATCH_INVALID_UTF (pcrec's own
   ill-formed-subject reading, utf8_design.md §2.6), "x" decode \xNN escapes in the subject.
   c: compile verdict + maxlookbehind; m: every non-overlapping match from startpos with groups. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    int mode_m = argc > 1 && argv[1][0] == 'm';
    const char *fl = argc > 2 ? argv[2] : "";
    uint32_t opt = strchr(fl, 'u') ? PCRE2_UTF : 0;
    if (strchr(fl, 'i')) opt |= PCRE2_UTF | PCRE2_MATCH_INVALID_UTF;
    int hex = strchr(fl, 'x') != NULL;
    static char dec[70000];
    static char line[70000];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = 0;
        char *tab = strchr(line, '\t'); const char *subj = ""; size_t at = 0;
        if (tab) { *tab = 0; subj = tab + 1; char *t2 = strchr(tab + 1, '\t'); if (t2) { *t2 = 0; at = strtoul(t2 + 1, NULL, 10); } }
        int err; PCRE2_SIZE eo;
        pcre2_code *re = pcre2_compile((PCRE2_SPTR)line, PCRE2_ZERO_TERMINATED, opt, &err, &eo, NULL);
        printf("%s\t%s\t", line, subj);
        if (hex) {   /* decode \xNN in place into dec; the echo above keeps the escapes */
            size_t o = 0;
            for (const char *q = subj; *q; q++) {
                if (q[0] == '\\' && q[1] == 'x' && q[2] && q[3]) {
                    char h[3] = { q[2], q[3], 0 }; dec[o++] = (char)strtoul(h, NULL, 16); q += 3;
                } else dec[o++] = *q;
            }
            dec[o] = 0; subj = dec;
        }
        if (!re) { printf("REJECT %d\n", err); continue; }
        if (!mode_m) { uint32_t lb; pcre2_pattern_info(re, PCRE2_INFO_MAXLOOKBEHIND, &lb); printf("ACCEPT lb=%u\n", lb); pcre2_code_free(re); continue; }
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        size_t n = strlen(subj); int any = 0;
        while (at <= n) {
            int rc = pcre2_match(re, (PCRE2_SPTR)subj, n, at, 0, md, NULL);
            if (rc < 0) break;
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            printf("[");
            for (int g = 0; g < rc; g++) {
                if (g) printf(",");
                if (ov[2*g] == PCRE2_UNSET) printf("-"); else printf("%zu-%zu", ov[2*g], ov[2*g+1]);
            }
            printf("]"); any = 1;
            at = ov[1] > ov[0] ? ov[1] : ov[1] + 1;
        }
        if (!any) printf("nomatch");
        printf("\n");
        pcre2_match_data_free(md); pcre2_code_free(re);
    }
    return 0;
}
