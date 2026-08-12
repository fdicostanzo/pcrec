/* pc4_check.c — PC-4 (MOD-0.3e), the SEMANTIC differential: the libpcre2
 * side and the comparator. PC-3 proved every registry row names a REAL
 * construct; PC-4 is the check PC-3 explicitly is not — it compares what a
 * produced construct MATCHES, cell by cell, against the live oracle
 * (R8/C4-2: "PC-3 compares compile VERDICTS only and calls none of the
 * match API it already links"). It exists because module `classes` gave
 * pcrec semantics that CAN differ.
 *
 * THE COMPARISON. run_pc4.sh compiles every generated pattern with
 * `pcrec --features classes` (plus -i on the caseless block) and runs the
 * accepted ones — via pc4_driver, one process per pattern — over the shared
 * subject set (pc4_subjects.h, embedded by BOTH sides). This program
 * compiles the same patterns with libpcre2 (PCRE2_CASELESS on the caseless
 * block — the first time `-i` has ever met an external oracle in this
 * repository) and compares:
 *   - compile VERDICT class per pattern (accept vs refuse, both directions:
 *     an over-acceptance and an over-rejection both fail, naming the cell);
 *   - for both-accept patterns, match/nomatch AND exact span for every
 *     subject (leftmost search from startpos 0 — the startpos axis stays
 *     with the corpus, which drives it through `ms`/`ns` lines).
 *
 * POPULATIONS ARE PREDICTED, NOT COPIED (the MOD-0.2 floors rule), and the
 * space is deterministic so the assertions are EXACT counts, not floors:
 *     273 patterns  =  11 esc constructs x 6 shapes (66)
 *                    + 28 posix spellings x 6 shapes (168)
 *                    + 39 caseless bare forms
 *     41 refusals   =  [x\N9] [^\Nz] (2) + [0-<esc>] (11) + [0-<posix>] (28)
 *     232 accepted  =  273 - 41
 *     62,872 cells  =  232 x 271 subjects
 * A count that comes out differently is a FAILURE to be understood, never
 * re-pinned from output (the generator and these numbers move in the same
 * change or not at all).
 *
 * mlimit (a PCRE2 backtracking-budget stop) is not a verdict; on this
 * backtrack-free pattern space it is asserted ZERO rather than skipped.
 *
 * Usage: pc4_check <patterns.tsv> <results-dir>
 *        pc4_check --probe-oracle   (exit 0 iff libpcre2 loads; the runner
 *                                    uses this to skip LOUDLY before paying
 *                                    for the gcc sweep)
 * patterns.tsv: <id>\t<i-flag 0|1>\t<pattern>, ids dense from 0.
 * results-dir:  per id, a file `<id>` holding either the single line
 *               REFUSED or PC4_NSUBJ verdict lines from pc4_driver. */

/* pcre2_abi.h FIRST: it defines _GNU_SOURCE (dlinfo) and must do so before
 * any libc header locks the feature macros — the same order PC-3 uses. */
#include "pcre2_abi.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pc4_subjects.h"

#define PCRE2_CASELESS_OPT 0x00000008u

static Pcre2Abi abi;
static int failures;

static void fail(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    fputs("FAIL: pc4: ", stdout);
    vprintf(fmt, ap);
    fputc('\n', stdout);
    fflush(stdout);
    va_end(ap);
    failures++;
}

/* render a pattern for a diagnostic without dumping raw control bytes */
static const char *shown(const char *pat)
{
    return pat; /* generator emits printable ASCII patterns only */
}

int main(int argc, char **argv)
{
    char why[256];

    if (argc == 2 && strcmp(argv[1], "--probe-oracle") == 0)
        return pcre2_abi_load(&abi, why, sizeof why) == PCRE2_ABI_OK ? 0 : 2;

    if (argc != 3) {
        fprintf(stderr, "usage: pc4_check <patterns.tsv> <results-dir>\n");
        return 2;
    }
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: pc4: %s\n", why);
        return 2;
    }

    FILE *pf = fopen(argv[1], "r");
    if (!pf) { fprintf(stderr, "pc4_check: cannot open %s\n", argv[1]); return 2; }

    long npat = 0, accepted_both = 0, refuse_agree = 0;
    long cells = 0, mlimits = 0;
    char line[512];

    while (fgets(line, sizeof line, pf)) {
        int id, iflag;
        char pat[400];
        if (sscanf(line, "%d\t%d\t%399[^\n]", &id, &iflag, pat) != 3) {
            fail("unparseable patterns.tsv line: %s", line);
            continue;
        }
        npat++;

        /* the pcrec side's verdict/results file */
        char rpath[512];
        snprintf(rpath, sizeof rpath, "%s/%d", argv[2], id);
        FILE *rf = fopen(rpath, "r");
        if (!rf) {
            fail("pattern %d '%s': no result file — the sweep lost a "
                 "pattern, which must never read as a pass", id, shown(pat));
            continue;
        }
        char rline[256];
        int pcrec_refused = 0;
        long fpos = ftell(rf);
        if (fgets(rline, sizeof rline, rf) &&
            strncmp(rline, "REFUSED", 7) == 0)
            pcrec_refused = 1;
        else
            fseek(rf, fpos, SEEK_SET);

        /* the libpcre2 side */
        int err = 0; PCRE2_SIZE eoff = 0;
        pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat),
                                         iflag ? PCRE2_CASELESS_OPT : 0,
                                         &err, &eoff, NULL);
        if (!code && pcrec_refused) { refuse_agree++; fclose(rf); continue; }
        if (!code && !pcrec_refused) {
            fail("pattern %d '%s'%s: pcrec ACCEPTS what libpcre2 refuses "
                 "(err %d) — an over-acceptance", id, shown(pat),
                 iflag ? " (-i)" : "", err);
            fclose(rf); continue;
        }
        if (code && pcrec_refused) {
            fail("pattern %d '%s'%s: pcrec REFUSES what libpcre2 compiles "
                 "— an over-rejection", id, shown(pat), iflag ? " (-i)" : "");
            abi.code_free(code); fclose(rf); continue;
        }

        accepted_both++;
        pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
        unsigned char one;
        for (int si = 0; si < (int)PC4_NSUBJ; si++) {
            size_t slen;
            const unsigned char *s = pc4_subject(si, &one, &slen);
            if (!fgets(rline, sizeof rline, rf)) {
                fail("pattern %d '%s': result file truncated at subject %d",
                     id, shown(pat), si);
                break;
            }
            int rc = abi.match(code, s, slen, 0, 0, md, NULL);
            if (rc < -1) { mlimits++; continue; }
            cells++;
            if (rc >= 0) {
                PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
                char want[64];
                snprintf(want, sizeof want, "match %zu %zu",
                         (size_t)ov[0], (size_t)ov[1]);
                if (strncmp(rline, want, strlen(want)) != 0)
                    fail("pattern %d '%s'%s subject %d: pcrec says %.*s, "
                         "libpcre2 says %s", id, shown(pat),
                         iflag ? " (-i)" : "", si,
                         (int)strcspn(rline, "\n"), rline, want);
            } else {
                if (strncmp(rline, "nomatch", 7) != 0)
                    fail("pattern %d '%s'%s subject %d: pcrec says %.*s, "
                         "libpcre2 says nomatch", id, shown(pat),
                         iflag ? " (-i)" : "", si,
                         (int)strcspn(rline, "\n"), rline);
            }
        }
        abi.match_data_free(md);
        abi.code_free(code);
        fclose(rf);
    }
    fclose(pf);

    /* the predicted populations, exact */
    if (npat != 273)
        fail("population: %ld patterns, 273 predicted — the generator and "
             "this number move in the same change or not at all", npat);
    if (refuse_agree != 41)
        fail("population: %ld refusal agreements, 41 predicted", refuse_agree);
    if (accepted_both != 232)
        fail("population: %ld both-accepted patterns, 232 predicted",
             accepted_both);
    if (cells != 232L * (long)PC4_NSUBJ)
        fail("population: %ld compared cells, %ld predicted", cells,
             232L * (long)PC4_NSUBJ);
    if (mlimits != 0)
        fail("%ld mlimit cells on a backtrack-free space — not a verdict, "
             "and not expected here", mlimits);

    printf("pc4: %ld patterns (%ld both-accepted, %ld refusal agreements), "
           "%ld match cells compared, %ld disagreements\n",
           npat, accepted_both, refuse_agree, cells, (long)failures);
    if (failures == 0)
        printf("PASS: pc4 semantic differential — produced sets match "
               "libpcre2 cell-for-cell, including the -i axis\n");
    return failures ? 1 : 0;
}
