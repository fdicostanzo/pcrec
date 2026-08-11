/* probe_class_expect.c — MOD-0.1 slice 3: the values for the `class_expect`
 * column, measured from libpcre2, never reasoned from documentation.
 *
 * PREDICTOR, stated before the run: the 44 class-reachable rows (kind `esc`
 * or `class-bracket` in `pcrec --list-syntax`) will produce exactly the 44
 * row values pinned in tests/spec_mod0/class_expectations.inc — that file
 * was measured by the SPEC-MOD0 (D27) author with an independent
 * implementation, and this probe re-derives the numbers before they are
 * transcribed into src/parse/registry.c. A disagreement means one of the two
 * implementations is wrong and the column must not land until it is known
 * which.
 *
 * THE MEASUREMENT. For a row whose class body is S (the `syntax` field for
 * esc rows; the field minus its outer brackets for class-bracket rows, so
 * `[[:alpha:]]` probes `[:alpha:]` — the doorway's own position):
 *
 *   compile `^[S]$`      does not compile  -> "err N"     (PCRE2's number)
 *   census all 256 one-byte subjects        -> exactly 1  -> "char 0xNN"
 *                                           -> n          -> "set n"
 *
 * 8-bit, options = 0, non-UTF — the same terms as every other measurement in
 * this repository.
 *
 * Output: one `syntax<TAB>value` line per class-reachable row, then a count
 * line. Rows of other kinds are counted and NOT probed (`(` inside a class
 * is an ordinary member; the column carries no value for them).
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe_ce \
 *            tests/probes/probe_class_expect.c -ldl
 * Run:   build/pcrec --list-syntax > /var/tmp/syn.tsv
 *        /var/tmp/probe_ce /var/tmp/syn.tsv
 */

#include "pcre2_abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Pcre2Abi abi;

/* Compile ^[body]$ ; on success census the 256 single-byte subjects. */
static int census(const char *body, int *nmembers, int *only_byte)
{
    char pat[512];
    int err = 0;
    PCRE2_SIZE eoff = 0;

    snprintf(pat, sizeof pat, "^[%s]$", body);
    pcre2_code_8 *c = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                  &err, &eoff, NULL);
    if (!c) return err;

    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int n = 0, last = -1;
    for (int b = 0; b < 256; b++) {
        char sub = (char)b;
        if (abi.match(c, (PCRE2_SPTR)&sub, 1, 0, 0, md, NULL) >= 0) {
            n++;
            last = b;
        }
    }
    abi.match_data_free(md);
    abi.code_free(c);
    *nmembers = n;
    *only_byte = last;
    return 0;
}

int main(int argc, char **argv)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "FAIL: libpcre2 missing — %s\n", why);
        return 2;
    }
    if (argc < 2) {
        fprintf(stderr, "usage: probe_class_expect REGISTRY.tsv\n");
        return 2;
    }
    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", argv[1]); return 2; }

    char ver[64];
    pcre2_abi_version(&abi, ver, sizeof ver);
    printf("# oracle: libpcre2 %s\n", ver);

    char line[512];
    int nprobed = 0, nskipped = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        /* field 1 = kind, field 3 = syntax */
        char *save = NULL;
        char *kind = strtok_r(line, "\t", &save);
        strtok_r(NULL, "\t", &save);
        char *syntax = strtok_r(NULL, "\t", &save);
        if (!kind || !syntax) continue;

        int is_esc = !strcmp(kind, "esc");
        int is_bracket = !strcmp(kind, "class-bracket");
        if (!is_esc && !is_bracket) { nskipped++; continue; }

        char body[256];
        if (is_bracket) {
            /* `[[:alpha:]]` -> `[:alpha:]`: strip one bracket each side so the
             * construct sits at the class's own position, as the doorway sees
             * it. */
            size_t L = strlen(syntax);
            if (L < 2) { fprintf(stderr, "FAIL: bracket row '%s' too short\n", syntax); return 2; }
            snprintf(body, sizeof body, "%.*s", (int)(L - 2), syntax + 1);
        } else {
            snprintf(body, sizeof body, "%s", syntax);
        }

        int n = 0, only = -1;
        int e = census(body, &n, &only);
        if (e)           printf("%s\terr %d\n", syntax, e);
        else if (n == 1) printf("%s\tchar 0x%02x\n", syntax, only);
        else             printf("%s\tset %d\n", syntax, n);
        nprobed++;
    }
    fclose(f);
    printf("# probed %d class-reachable rows, skipped %d group/verb rows\n",
           nprobed, nskipped);
    return 0;
}
