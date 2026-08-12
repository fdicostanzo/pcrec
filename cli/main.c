/* pcrec command-line interface.
 *
 *   pcrec [-p PREFIX] [-e ascii|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'
 *   pcrec -o - 'PATTERN'      self-contained C on stdout (no header file)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pcrec.h"
/* The syntax-query modes read the construct registry, which is internal: the
 * CLI and the test suite are its only consumers, so it is not part of the
 * public surface (see src/parse/syntax_dump.c). main.c touches no registry
 * type — it calls two functions that hand back finished text. */
#include "core/internal.h"

static void usage(FILE *f)
{
    fputs("usage: pcrec [options] -o OUT.c [--] 'PATTERN'\n"
          "  -o FILE        output C file; a matching header FILE with .h is\n"
          "                 also written. '-o -' prints self-contained C to\n"
          "                 stdout with no header file\n"
          "  -p PREFIX      symbol prefix for generated identifiers (default rx)\n"
          "  -e ENCODING    subject encoding: ascii (default) or utf8\n"
          "  -i             match case-insensitively (ASCII letters); folded\n"
          "                 into the automaton, no run-time cost\n"
          "  --emit-main    append a standalone main() (subject from argv[1])\n"
          "  -h, --help     this help\n"
          "\n"
          "syntax queries (no pattern, no -o):\n"
          "  --list-syntax     TSV of every non-base construct pcrec knows\n"
          "  --list-verbs      TSV of the (*VERB) names pcrec recognises\n"
          "  --explain SYNTAX  what pcrec knows about one construct, e.g. '\\\\v'\n"
          "  --flavour NAME    restrict either query to a flavour (only 'pcre2'\n"
          "                    exists today; a second one arrives with SR-7)\n"
          "  --count-groups [--] PATTERN\n"
          "                    parse only; print the number of capturing\n"
          "                    groups. A pattern pcrec refuses is refused\n"
          "                    here too, with the same diagnostic\n"
          "  --features LIST   enable feature modules for this invocation:\n"
          "                    comma-separated names from --list-syntax's\n"
          "                    module column, or 'all' or 'none' (default\n"
          "                    none). Composes with every mode. No module\n"
          "                    has an implementation yet, so enabling one\n"
          "                    changes no verdict today — the gate's state\n"
          "                    is visible via --probe-ask's answered_at\n"
          "  --probe-ask WANT [--] CONSTRUCT\n"
          "                    drive the construct's doorway ONCE at ask\n"
          "                    level WANT (claim|verdict|result) and report\n"
          "                    the parser cursor. TSV: doorway, want,\n"
          "                    answered_at, pos_before, pos_after, outcome,\n"
          "                    at, ep_set_certain, end, msg. The cursor rule\n"
          "                    (pos moves only under result) is what\n"
          "                    tests/spec_mod0's check06 compares here\n", f);
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
    int list_syntax = 0;
    const char *explain = NULL, *flavour = NULL;
    int list_verbs = 0;
    int count_groups = 0;
    const char *probe_want = NULL;
    const char *features = NULL;

    int no_more_opts = 0;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (!no_more_opts && !strcmp(a, "--")) no_more_opts = 1;
        else if (!no_more_opts && (!strcmp(a, "-h") || !strcmp(a, "--help"))) {
            usage(stdout);
            return 0;
        }
        else if (!no_more_opts && !strcmp(a, "--emit-main")) opt.emit_main = 1;
        else if (!no_more_opts && !strcmp(a, "-i")) opt.caseless = 1;
        else if (!no_more_opts && !strcmp(a, "--list-syntax")) list_syntax = 1;
        else if (!no_more_opts && !strcmp(a, "--list-verbs"))  list_verbs = 1;
        else if (!no_more_opts && !strcmp(a, "--count-groups")) count_groups = 1;
        else if (!no_more_opts && !strcmp(a, "--probe-ask")) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            probe_want = argv[++i];
        }
        else if (!no_more_opts && !strcmp(a, "--features")) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            features = argv[++i];
        }
        else if (!no_more_opts &&
                 (!strcmp(a, "--explain") || !strcmp(a, "--flavour"))) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[2] == 'e') explain = v; else flavour = v;
        }
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

    /* --count-groups is the one query that TAKES a pattern — it runs the real
     * parser (parse only, nothing emitted) and prints the running capture
     * count's end-of-parse value (§18.1; the channel tests/spec_mod0/check02
     * compares against libpcre2). A pattern pcrec refuses is refused here
     * with pcrec_compile's exact diagnostic — leftmost refusal, so a count is
     * never reported for a pattern whose constructs pcrec does not know. */
    /* --features installs the enabled set BEFORE anything consults the gate
     * (slice 9). It composes with every mode — a compile, --probe-ask,
     * --count-groups — because it is configuration, not a query; an unknown
     * module name is refused BY NAME rather than silently enabling nothing
     * (the --flavour rule). No module has ports yet, so today it changes no
     * verdict — only the probe channel's answered_at can see it (check07
     * holds the verdict-equivalence half). */
    if (features) {
        char ferr[256];
        if (pcrec_enabled_set_spec(features, ferr, sizeof ferr) != 0) {
            fprintf(stderr, "pcrec: --features: %s\n", ferr);
            return 1;
        }
    }

    /* --probe-ask drives ONE doorway call and reports the cursor — the
     * check06 channel (§18.2's cursor rule). The doorway REFUSING the
     * construct is a normal, reportable outcome here (exit 0, outcome
     * column says so): probing is not compiling. Only a channel that could
     * not run at all exits nonzero, so the check can tell "measured a
     * refusal" from "measured nothing". */
    if (probe_want) {
        if (list_syntax || list_verbs || explain || count_groups) {
            fprintf(stderr, "pcrec: --probe-ask is a separate query; use one\n");
            return 1;
        }
        if (outpath) {
            fprintf(stderr, "pcrec: --probe-ask takes no -o\n");
            return 1;
        }
        if (flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                            "--explain only\n");
            return 1;
        }
        if (!pattern) {
            fprintf(stderr, "pcrec: --probe-ask needs a construct\n");
            return 1;
        }
        /* Two NULLs with different causes (R20/MOD07-1): a port that RAISED
         * fills perr, and gets the compile path's own error shape rather
         * than the usage sentence below — the operator's command line is
         * fine, their pattern is not. */
        pcrec_error perr;
        char *line = pcrec_probe_ask(probe_want, pattern, &perr);
        if (!line && perr.msg[0]) {
            fprintf(stderr, "pcrec: --probe-ask: %s (pattern offset %zu)\n",
                    perr.msg, perr.pos);
            return 1;
        }
        if (!line) {
            fprintf(stderr, "pcrec: --probe-ask: WANT must be claim, verdict "
                            "or result, and the construct must reach a "
                            "doorway (start with '\\', '(?', '(*' or '[' — "
                            "except '(?:', which the base grammar answers "
                            "before any doorway is consulted)\n");
            return 1;
        }
        fputs(line, stdout);
        free(line);
        return 0;
    }

    if (count_groups) {
        if (list_syntax || list_verbs || explain) {
            fprintf(stderr, "pcrec: --count-groups is a separate query; use one\n");
            return 1;
        }
        if (outpath) {
            fprintf(stderr, "pcrec: --count-groups takes no -o\n");
            return 1;
        }
        if (flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                            "--explain only\n");
            return 1;
        }
        if (!pattern) {
            fprintf(stderr, "pcrec: --count-groups needs a pattern\n");
            return 1;
        }
        pcrec_error err;
        int n = pcrec_count_groups(pattern, &err);
        if (n < 0) {
            fprintf(stderr, "pcrec: %s (pattern offset %zu)\n", err.msg, err.pos);
            return 1;
        }
        printf("%d\n", n);
        return 0;
    }

    /* Syntax queries answer from the registry and compile nothing, so they take
     * neither a pattern nor -o. They are checked before the pattern/-o
     * requirement and reject a mixed invocation rather than silently ignoring
     * half of it. */
    if (list_syntax || explain || list_verbs) {
        if (list_syntax + list_verbs + (explain != NULL) > 1) {
            fprintf(stderr, "pcrec: --list-syntax, --list-verbs and --explain are "
                            "separate queries; use one\n");
            return 1;
        }
        if (pattern || outpath) {
            fprintf(stderr, "pcrec: %s takes no pattern and no -o\n",
                    list_syntax ? "--list-syntax" :
                    list_verbs  ? "--list-verbs"  : "--explain");
            return 1;
        }
        /* --list-verbs has no flavour axis: the verb tables record what libpcre2
         * accepts, and there is exactly one PCRE2. When SR-7 adds a flavour that
         * genuinely differs here, this is where it grows one. */
        if (list_verbs && flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                            "--explain only\n");
            return 1;
        }
        if (list_verbs) {
            char *v = pcrec_syntax_verbs();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        unsigned fl = 0;
        if (flavour && !(fl = pcrec_flavour_by_name(flavour))) {
            fprintf(stderr, "pcrec: unknown flavour '%s' (only 'pcre2' exists; "
                            "more arrive with SR-7)\n", flavour);
            return 1;
        }
        int ndissent = 0;
        pcrec_error eerr = { .msg = { 0 }, .pos = 0 };
        char *text = list_syntax ? pcrec_syntax_tsv(fl)
                                 : pcrec_syntax_explain(explain, fl, &ndissent,
                                                        &eerr);
        /* A DOORWAY THAT RAISED (R20/MOD07-1), not a query nothing matches:
         * an enabled module port parsed the query text for real and that
         * parse failed. Same shape a compile error gets, so an operator who
         * has seen one recognises the other. */
        if (!text && eerr.msg[0]) {
            fprintf(stderr, "pcrec: --explain: %s (pattern offset %zu)\n",
                    eerr.msg, eerr.pos);
            return 1;
        }
        if (!text) {
            /* --explain only; the TSV always has rows */
            fprintf(stderr, "pcrec: no construct matches '%s' — it is either "
                            "base syntax or not a construct pcrec knows\n",
                    explain);
            return 1;
        }
        fputs(text, stdout);
        free(text);
        /* EXIT 3 IS A DISSENT (MOD-0.7): --explain prints the registry's
         * declared attribution beside the live doorway's answer and compares
         * them per row. A disagreement is a DEFECT SURFACED, not a bad
         * question, and a script must be able to tell the two apart — exit 1
         * already means "your query could not be answered", and every other
         * misuse of this CLI is exit 1 too. The full answer still goes to
         * stdout; the failing rows carry `agree  DISSENT: <clause>: …`. */
        if (ndissent > 0) {
            fprintf(stderr, "pcrec: --explain: %d row%s DISAGREE with the live "
                            "doorway (see the 'agree' lines) — this is a pcrec "
                            "defect, not a bad query\n",
                    ndissent, ndissent == 1 ? "" : "s");
            return 3;
        }
        return 0;
    }
    if (flavour) {
        fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                        "--explain only\n");
        return 1;
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
