/* tests/cli/simd_target_probe.c — [XARCH-DEV] P1's two oracles for
 * run_cli_tests.sh's CPU-target cases. Both read the KIT or the library, never
 * a token list of pcrec's own (tests/memfn C4: pcrec's tests name no token).
 *
 *   simd_target_probe kit TOKEN   prints the kit's own refusal of TOKEN as a
 *                                 target, then as a family, one per line
 *   simd_target_probe api FLAGS LIST
 *                                 compiles `abc` through pcrec_compile with
 *                                 pcrec_options.flags = FLAGS ("none", "no",
 *                                 "force") and memfn_simd = LIST ("-" = NULL);
 *                                 prints "rc=N" and the error text
 *   simd_target_probe text TOKEN DIR
 *                                 writes the kit's C text for target TOKEN
 *                                 (unit U3): DIR/guard (its family's guard,
 *                                 empty for no family), DIR/open, DIR/close
 *                                 (its region); exit 1 if TOKEN is no target */
#include <stdio.h>
#include <string.h>

#include "pcrec.h"
#include "../../memfn/include/memfn.h"

int main(int argc, char **argv)
{
    if (argc == 3 && !strcmp(argv[1], "kit")) {
        char e[256];
        e[0] = 0;
        (void)mf_target_parse(argv[2], strlen(argv[2]), e, sizeof e);
        puts(e);
        e[0] = 0;
        (void)mf_family_parse(argv[2], strlen(argv[2]), e, sizeof e);
        puts(e);
        return 0;
    }
    if (argc == 4 && !strcmp(argv[1], "api")) {
        pcrec_options o;
        pcrec_output out;
        pcrec_error err;
        pcrec_default_options(&o);
        if (!strcmp(argv[2], "no")) o.flags |= PCREC_NO_MEMFN_SIMD;
        else if (!strcmp(argv[2], "force")) o.flags |= PCREC_FORCE_MEMFN_SIMD;
        o.memfn_simd = strcmp(argv[3], "-") ? argv[3] : NULL;
        int rc = pcrec_compile("abc", &o, &out, &err);
        printf("rc=%d\n%s\n", rc, rc ? err.msg : "");
        if (rc == 0) pcrec_output_free(&out);
        return 0;
    }
    if (argc == 4 && !strcmp(argv[1], "text")) {
        const mf_target *t = mf_target_parse(argv[2], strlen(argv[2]), NULL, 0);
        if (!t) return 1;
        const char *text[3] = { t->family ? mf_family_c_of(t->family)->guard : "",
                                mf_target_c_of(t)->region_open,
                                mf_target_c_of(t)->region_close };
        static const char *const name[3] = { "guard", "open", "close" };
        for (int i = 0; i < 3; i++) {
            char path[4096];
            snprintf(path, sizeof path, "%s/%s", argv[3], name[i]);
            FILE *f = fopen(path, "w");
            if (!f) return 1;
            fputs(text[i], f);
            fclose(f);
        }
        return 0;
    }
    fprintf(stderr, "usage: simd_target_probe kit TOKEN | api FLAGS LIST | text TOKEN DIR\n");
    return 2;
}
