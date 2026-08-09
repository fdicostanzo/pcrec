/* pcrec command-line interface.
 *
 *   pcrec [-p PREFIX] [-e ascii|utf8] [--emit-main] -o OUT.c 'PATTERN'
 *   pcrec -o - 'PATTERN'      self-contained C on stdout (no header file)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pcrec.h"

static void usage(FILE *f)
{
    fputs("usage: pcrec [options] -o OUT.c [--] 'PATTERN'\n"
          "  -o FILE        output C file; a matching header FILE with .h is\n"
          "                 also written. '-o -' prints self-contained C to\n"
          "                 stdout with no header file\n"
          "  -p PREFIX      symbol prefix for generated identifiers (default rx)\n"
          "  -e ENCODING    subject encoding: ascii (default) or utf8\n"
          "  --emit-main    append a standalone main() (subject from argv[1])\n"
          "  -h, --help     this help\n", f);
}

static const char *base_name(const char *path)
{
    const char *s = strrchr(path, '/');
    return s ? s + 1 : path;
}

static int write_file(const char *path, const char *text)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return -1; }
    fputs(text, f);
    if (fclose(f) != 0) { perror(path); return -1; }
    return 0;
}

int main(int argc, char **argv)
{
    pcrec_options opt;
    pcrec_default_options(&opt);
    const char *outpath = NULL;
    const char *pattern = NULL;

    int no_more_opts = 0;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (!no_more_opts && !strcmp(a, "--")) no_more_opts = 1;
        else if (!no_more_opts && (!strcmp(a, "-h") || !strcmp(a, "--help"))) {
            usage(stdout);
            return 0;
        }
        else if (!no_more_opts && !strcmp(a, "--emit-main")) opt.emit_main = 1;
        else if (!no_more_opts &&
                 (!strcmp(a, "-o") || !strcmp(a, "-p") || !strcmp(a, "-e"))) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[1] == 'o') outpath = v;
            else if (a[1] == 'p') opt.prefix = v;
            else {
                if (!strcmp(v, "ascii"))     opt.encoding = PCREC_ENC_ASCII;
                else if (!strcmp(v, "utf8")) opt.encoding = PCREC_ENC_UTF8;
                else { fprintf(stderr, "pcrec: unknown encoding '%s'\n", v); return 1; }
            }
        }
        else if (!no_more_opts && a[0] == '-' && a[1]) {
            fprintf(stderr, "pcrec: unknown option '%s' (use -- before a "
                            "pattern that starts with '-')\n", a);
            usage(stderr);
            return 1;
        }
        else if (!pattern) pattern = a;
        else { fprintf(stderr, "pcrec: exactly one pattern expected\n"); return 1; }
    }

    if (!pattern || !outpath) {
        fprintf(stderr, "pcrec: pattern and -o are required\n");
        usage(stderr);
        return 1;
    }

    int to_stdout = !strcmp(outpath, "-");
    char *hpath = NULL;
    if (!to_stdout) {
        size_t len = strlen(outpath);
        hpath = malloc(len + 3);
        if (!hpath) { perror("malloc"); return 1; }
        strcpy(hpath, outpath);
        if (len > 2 && !strcmp(hpath + len - 2, ".c")) strcpy(hpath + len - 2, ".h");
        else strcat(hpath, ".h");
        opt.header_name = base_name(hpath);
    }

    pcrec_output out;
    pcrec_error err;
    if (pcrec_compile(pattern, &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (pattern offset %zu)\n", err.msg, err.pos);
        free(hpath);
        return 1;
    }

    int rc = 0;
    if (to_stdout) {
        fputs(out.c_src, stdout);
    } else {
        if (write_file(outpath, out.c_src) != 0 ||
            write_file(hpath, out.h_src) != 0)
            rc = 1;
    }
    pcrec_output_free(&out);
    free(hpath);
    return rc;
}
