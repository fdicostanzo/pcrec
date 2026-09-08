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
 *               REFUSED or PC4_NSUBJ verdict lines from pc4_driver — each
 *               either `match <s> <e>`, `nomatch`, or [K21-class fix,
 *               2026-08-15] `giveup steps`/`giveup frames` (a VM budget
 *               give-up, never a comparable verdict — see pc4_driver.c). */

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

/* ---- THE STANDING 1:n FOLD CHECK (S-U11) --------------------------------
 *
 * `docs/design/utf8_design.md` §4.1.1, ASK 3 RULED by Frank 2026-09-04. It is
 * the ONE check in this file whose SUBJECT IS libpcre2 rather than pcrec, and
 * that is exactly why it exists.
 *
 * WHAT IT DEFENDS. [M5.0]'s whole caseless lowering rests on one measured
 * fact: libpcre2 10.46 implements SIMPLE case folding and no one-to-many
 * folding at all (0 of 11 cells, `utf8_measurements/out/caseless.txt` §2). A
 * 1:n fold is a SEQUENCE, so its existence would force a caseless literal
 * into an alternation and a caseless class to hold something a set cannot
 * hold — not a tuning change, a different lowering. `src/core/fold.c` reads
 * `C` and `S` status lines only for the same reason, and `[FORM-CHAR]`
 * object (5) `utf8-full-fold` is NOT BUILT on the strength of this result.
 *
 * WHY A STANDING CHECK AND NOT A ONE-TIME MEASUREMENT. The failure would be
 * SILENT: a future libpcre2 that added full folding would simply start
 * matching cells pcrec answers `no` to, with nothing in this tree noticing,
 * because a measurement leaves no instrument behind.
 *
 * THE POPULATION IS THE ELEVEN MEASURED CELLS x BOTH OPTION WORDS = 22
 * ASSERTIONS, and the second arm is not padding: §4.1 measured `UTF|CASELESS`
 * and `UTF|CASELESS|UCP` separately, and a check that dropped the UCP arm
 * would stop watching the arm a full-folding implementation is likeliest to
 * reach first. Sabotage row S-U11's `SAB_REACH_POP` floor is 22 for that
 * reason; a floor of 11 would pass a check that had lost half its space.
 *
 * A CELL THAT STARTS MATCHING IS A RED, NOT A SKIP, and the diagnostic names
 * the DESIGN EVENT rather than the cell — a message saying only "cell 7
 * failed" makes the next reader rediscover what §4.1 is for. It lands here
 * rather than in stage 4's own suite because it has no dependency on any
 * pcrec code and could (and should) have run from stage 1. */

#define PCRE2_UTF_OPT 0x00080000u
#define PCRE2_UCP_OPT 0x00020000u

/* Every cell is an ANCHORED whole-subject match, so a partial match cannot be
 * misread as a successful fold. Bytes are OCTAL escapes throughout: a `\x`
 * escape has no digit-count limit in C and would glue onto a following literal
 * hex digit, where a three-digit octal escape self-terminates. */
static const struct { const char *name, *pat, *subj; } fold_1n_cells[] = {
    { "sharp s vs SS",        "^(?:\303\237)$",     "SS"                     },
    { "sharp s vs ss",        "^(?:\303\237)$",     "ss"                     },
    { "SS vs sharp s",        "^(?:SS)$",           "\303\237"               },
    { "ss vs sharp s",        "^(?:ss)$",           "\303\237"               },
    { "U+FB01 fi vs fi",      "^(?:\357\254\201)$", "fi"                     },
    { "fi vs U+FB01",         "^(?:fi)$",           "\357\254\201"           },
    { "U+FB03 ffi vs ffi",    "^(?:\357\254\203)$", "ffi"                    },
    { "U+0149 vs 'n",         "^(?:\305\211)$",     "\312\274n"              },
    { "U+01F0 vs j+caron",    "^(?:\307\260)$",     "j\314\214"              },
    { "U+1E96 vs h+line",     "^(?:\341\272\226)$", "h\314\261"              },
    { "U+0390 vs 3-cp form",  "^(?:\316\220)$",     "\316\271\314\210\314\201" }
};

/* Returns the number of ASSERTIONS made, so the caller can print the count
 * the sabotage row's reach floor is stated against. */
static long check_1n_fold(void)
{
    static const struct { const char *label; unsigned opts; } arms[] = {
        { "UTF|CASELESS",     PCRE2_UTF_OPT | PCRE2_CASELESS_OPT },
        { "UTF|CASELESS|UCP", PCRE2_UTF_OPT | PCRE2_CASELESS_OPT | PCRE2_UCP_OPT }
    };
    const size_t ncell = sizeof fold_1n_cells / sizeof fold_1n_cells[0];
    const size_t narm  = sizeof arms / sizeof arms[0];
    long asserted = 0;

    for (size_t a = 0; a < narm; a++) {
        for (size_t c = 0; c < ncell; c++) {
            int err = 0;
            PCRE2_SIZE eoff = 0;
            pcre2_code_8 *code = abi.compile(
                (PCRE2_SPTR)fold_1n_cells[c].pat,
                strlen(fold_1n_cells[c].pat), arms[a].opts, &err, &eoff, NULL);
            if (!code) {
                /* A cell that stops COMPILING is a red too: the space this
                 * check watches would silently shrink to nothing. */
                fail("1:n fold: cell '%s' [%s] no longer compiles (err %d) — "
                     "the standing check's own population is eroding",
                     fold_1n_cells[c].name, arms[a].label, err);
                continue;
            }
            pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
            int rc = abi.match(code, (PCRE2_SPTR)fold_1n_cells[c].subj,
                               strlen(fold_1n_cells[c].subj), 0, 0, md, NULL);
            abi.match_data_free(md);
            abi.code_free(code);
            asserted++;
            if (rc >= 0)
                fail("1:n fold: cell '%s' MATCHES under %s. libpcre2 has "
                     "gained 1:n case folding; docs/design/utf8_design.md "
                     "§4.1 and [FORM-CHAR] object (5) are invalidated — "
                     "a caseless class can no longer stay a class, and "
                     "src/core/fold.c's C/S-only subset is no longer the "
                     "oracle's whole behaviour. This is a D26 re-measurement "
                     "event, not a cell to re-pin",
                     fold_1n_cells[c].name, arms[a].label);
        }
    }
    /* THE POPULATION IS ASSERTED HERE, EXACTLY, and that is stronger than the
     * grep floor §8.2 proposes for sabotage row S-U11. That row's stated
     * hazard is a check that has silently lost the `PCRE2_UCP` arm, and a
     * floor counting occurrences of a STRING in this file cannot see the
     * difference between eleven cells over two arms and eleven over one. The
     * number the row is really about is the one this function actually made. */
    if (asserted != 22)
        fail("1:n fold: %ld assertions, 22 owed (11 measured cells x 2 option "
             "words) — the standing check's space has changed size, which is "
             "the S-U11 hazard rather than a count to re-pin", asserted);
    return asserted;
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

    /* [M5.0 stage 4 / S-U11] the standing 1:n fold check, run BEFORE the
     * differential's own work: its subject is the ORACLE, so it is the fact
     * every cell below is compared under. */
    long fold_asserts = check_1n_fold();
    printf("pc4: 1:n fold — %ld assertions (11 cells x 2 option words), "
           "%ld matching\n", fold_asserts, (long)failures);

    FILE *pf = fopen(argv[1], "r");
    if (!pf) { fprintf(stderr, "pc4_check: cannot open %s\n", argv[1]); return 2; }

    long npat = 0, accepted_both = 0, refuse_agree = 0;
    long cells = 0, mlimits = 0, pcrec_giveups = 0;
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
            /* [K21-class fix, 2026-08-15] pc4_driver.c's own give-up line
             * (see its header comment): rx_search returned a negative VM
             * budget sentinel for this subject, not a match or a no-match.
             * Symmetric to libpcre2's own give-up bucket below (mlimits):
             * NEITHER side's give-up is a comparable verdict, so this must
             * never fall through into the match/nomatch agreement check
             * as a fabricated match. Counted separately and asserted zero
             * — dormant on PC-4's DFA-only pattern space today. */
            if (strncmp(rline, "giveup", 6) == 0) { pcrec_giveups++; continue; }
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
    if (pcrec_giveups != 0)
        fail("%ld pcrec driver give-up cells (PCREC_ERR_STEPS/PCREC_ERR_FRAMES) "
             "— not a verdict, and not expected on PC-4's DFA-only pattern "
             "space [K21-class]", pcrec_giveups);

    printf("pc4: %ld patterns (%ld both-accepted, %ld refusal agreements), "
           "%ld match cells compared, %ld disagreements\n",
           npat, accepted_both, refuse_agree, cells, (long)failures);
    if (failures == 0)
        printf("PASS: pc4 semantic differential — produced sets match "
               "libpcre2 cell-for-cell, including the -i axis\n");
    return failures ? 1 : 0;
}
