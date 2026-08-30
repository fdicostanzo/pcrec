/* definitions_oracle_check.c — [DD-11.3]'s comparator: the co-equal legs
 * (definitions_table.md §3 item 4 / the manager's [DD-11.3] brief) —
 * A==B (does the table's own resolved definition, compiled standalone,
 * agree with the row's own construct, compiled as shipped — read from
 * definitions_oracle_driver.c's per-cell results file) AND A==C (does the
 * row's own construct agree with libpcre2 — driven directly here, PC-4's
 * `pc4_check.c` own shape one table over).
 *
 * Usage: definitions_oracle_check <cells.tsv> <results-dir>
 *        definitions_oracle_check --probe-oracle
 *
 * cells.tsv: <id>\t<pattern_a>\t<pattern_b>\t<oracle_a>\t<description>,
 * ids dense from 0 (definitions_oracle_gen.c's own output).
 * results-dir: per id, a file `<id>` holding definitions_oracle_
 * driver.c's 2*DEFN_NSUBJ lines (`<idx>\ta <verdict>...` /
 * `<idx>\tb <verdict>...`, interleaved a-then-b per subject).
 *
 * `oracle_a` (r43-third-round follow-up, 2026-08-29, the DEFK_TEXTFN
 * rows joining the sweep): `-` means "use Pattern A as-is for the A==C
 * libpcre2 leg", every DEFK_STR/DEFK_BUILDER/DEF_IDENTITY/DEFK_ROW cell's
 * value. A real pattern text OVERRIDES what libpcre2 compiles for A==C
 * ONLY — Pattern A itself (what PCREC compiles, and what A==B compares)
 * is unchanged. This exists for the three UNBUILT DEFK_TEXTFN rows (`\c`,
 * `\o{}`, `\N{U+`): pcrec cannot compile their real spelling at all, so
 * the generator sets Pattern A to Pattern B repeated (a harmless
 * tautology for A==B) and puts the REAL spelling here instead, so A==C
 * still asks the meaningful question — "the textfn's decode and
 * libpcre2's agree on the byte" (the ruling's own words) — against a
 * construct pcrec has not shipped yet.
 *
 * WHAT A==B COMPARES: the WHOLE-MATCH verdict (match span, or nomatch, or
 * a give-up) only — never the full capture vector. Pattern A and Pattern
 * B can legitimately have DIFFERENT capture shapes (`(a)` vs `(?:a)`) and
 * still be the identical construct under D85's own definition ("a
 * construct standing for another construct expressible in core syntax");
 * the shared claim between them is the LANGUAGE and the MATCH POSITION,
 * not the capture layout. A give-up on either side is NOT a verdict
 * (K21's class, pc4_check.c's own precedent) and is asserted zero rather
 * than compared as if it meant something.
 *
 * WHAT A==C COMPARES: Pattern A (the row's own shipped construct) against
 * libpcre2's compile+match on the IDENTICAL subject, span for span —
 * PC-4's own comparison, one row over. Pattern B is not driven through
 * libpcre2 at all: it is core-syntax text whose OWN behaviour is exactly
 * what makes it a legal substitution, and A==B already ties it to
 * Pattern A; asking libpcre2 about it too would be a third comparison
 * this design does not need. */

#include "pcre2_abi.h"

#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "definitions_oracle_subjects.h"

static Pcre2Abi abi;
static int failures;
static int reported;
#define MAX_REPORTED 20

static void fail(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    if (reported < MAX_REPORTED) {
        fputs("FAIL: definitions-oracle: ", stdout);
        vprintf(fmt, ap);
        fputc('\n', stdout);
        reported++;
    } else if (reported == MAX_REPORTED) {
        printf("FAIL: definitions-oracle: (further failures suppressed, "
               "%d shown)\n", MAX_REPORTED);
        reported++;
    }
    fflush(stdout);
    failures++;
}

typedef struct { char tag; char verdict; ptrdiff_t start, end; } Verdict;

/* Parses ONE line of definitions_oracle_driver.c's own output shape:
 * "<idx>\t<tag> m <s> <e> ..." / "<idx>\t<tag> n" / "<idx>\t<tag> g <kind>".
 * Only the whole-match span is kept (see file header on why). */
static int parse_line(const char *line, int *idx, Verdict *v)
{
    char tag_c;
    char verdict_c;
    int n;
    if (sscanf(line, "%d\t%c %c%n", idx, &tag_c, &verdict_c, &n) != 3)
        return 0;
    v->tag = tag_c;
    v->verdict = verdict_c;
    v->start = v->end = -1;
    if (verdict_c == 'm') {
        if (sscanf(line + n, " %td %td", &v->start, &v->end) != 2)
            return 0;
    }
    return 1;
}

int main(int argc, char **argv)
{
    char why[256];

    if (argc == 2 && strcmp(argv[1], "--probe-oracle") == 0)
        return pcre2_abi_load(&abi, why, sizeof why) == PCRE2_ABI_OK ? 0 : 2;

    if (argc != 3) {
        fprintf(stderr, "usage: definitions_oracle_check <cells.tsv> "
                "<results-dir>\n");
        return 2;
    }
    /* A==B (the table's own self-consistency) needs no external oracle
     * and is NOT skippable; only A==C (below) is gated on libpcre2 being
     * loadable, PC-4/PC-3's own "a stranger's clone stays green" shape,
     * scoped to the ONE leg that actually needs it rather than the whole
     * comparison. */
    bool have_oracle = pcre2_abi_load(&abi, why, sizeof why) == PCRE2_ABI_OK;
    if (!have_oracle)
        fprintf(stderr, "SKIP: definitions-oracle: %s (A==C leg skipped; "
                "A==B still runs)\n", why);

    FILE *cf = fopen(argv[1], "r");
    if (!cf) {
        fprintf(stderr, "definitions_oracle_check: cannot open %s\n", argv[1]);
        return 2;
    }

    long ncells = 0, ab_cells = 0, ac_cells = 0;
    long ab_giveups = 0, ac_mlimits = 0;
    char line[1024];

    while (fgets(line, sizeof line, cf)) {
        int id;
        char pa[300], pb[300], oracle_a[300], desc[300];
        if (sscanf(line, "%d\t%299[^\t]\t%299[^\t]\t%299[^\t]\t%299[^\n]",
                   &id, pa, pb, oracle_a, desc) != 5) {
            fail("unparseable cells.tsv line: %s", line);
            continue;
        }
        ncells++;
        /* "-" means "use Pattern A as-is" -- see the file header. `ora`
         * is what the A==C leg below actually hands libpcre2; Pattern A
         * itself (`pa`) is untouched, still what pcrec compiled and still
         * what A==B compares. */
        const char *ora = (strcmp(oracle_a, "-") == 0) ? pa : oracle_a;

        char rpath[512];
        snprintf(rpath, sizeof rpath, "%s/%d", argv[2], id);
        FILE *rf = fopen(rpath, "r");
        if (!rf) {
            fail("cell %d '%s': no result file — the sweep lost a cell, "
                 "which must never read as a pass", id, desc);
            continue;
        }

        /* libpcre2 on `ora` (Pattern A, or the `oracle_a` override -- see
         * the file header) ONLY -- skipped entirely when the oracle did
         * not load, per the A==B/A==C split above. */
        pcre2_code_8 *code = NULL;
        pcre2_match_data_8 *md = NULL;
        if (have_oracle) {
            int err = 0; PCRE2_SIZE eoff = 0;
            code = abi.compile((PCRE2_SPTR)ora, strlen(ora), 0, &err, &eoff, NULL);
            if (!code)
                fail("cell %d '%s': oracle pattern '%s' -- libpcre2 refuses "
                     "(err %d) a construct this table's own row already "
                     "ships", id, desc, ora, err);
            md = code ? abi.match_data_create(2, NULL) : NULL;
        }

        char la[256], lb[256];
        for (int si = 0; si < (int)DEFN_NSUBJ; si++) {
            if (!fgets(la, sizeof la, rf) || !fgets(lb, sizeof lb, rf)) {
                fail("cell %d '%s': result file truncated at subject %d",
                     id, desc, si);
                break;
            }
            int idx_a, idx_b;
            Verdict va, vb;
            if (!parse_line(la, &idx_a, &va) || va.tag != 'a' ||
                !parse_line(lb, &idx_b, &vb) || vb.tag != 'b' ||
                idx_a != si || idx_b != si) {
                fail("cell %d '%s': malformed driver output at subject %d: "
                     "%.*s / %.*s", id, desc, si,
                     (int)strcspn(la, "\n"), la, (int)strcspn(lb, "\n"), lb);
                continue;
            }

            /* ---- A == B ---- */
            if (va.verdict == 'g' || vb.verdict == 'g') {
                ab_giveups++; /* not a verdict, K21's class */
            } else {
                ab_cells++;
                int agree = (va.verdict == vb.verdict) &&
                            (va.verdict != 'm' ||
                             (va.start == vb.start && va.end == vb.end));
                if (!agree) {
                    const char *va_txt = strchr(la, ' ') + 1;
                    const char *vb_txt = strchr(lb, ' ') + 1;
                    fail("cell %d '%s' subject %d: A==B disagreement -- "
                         "pattern A ('%s') says %.*s, pattern B ('%s') "
                         "says %.*s", id, desc, si, pa,
                         (int)strcspn(va_txt, "\n"), va_txt, pb,
                         (int)strcspn(vb_txt, "\n"), vb_txt);
                }
            }

            /* ---- A == C (libpcre2), only if A compiled ---- */
            if (code) {
                unsigned char one;
                size_t slen;
                const unsigned char *s = defn_subject(si, &one, &slen);
                int rc = abi.match(code, s, slen, 0, 0, md, NULL);
                if (rc < -1) {
                    ac_mlimits++;
                } else if (va.verdict != 'g') {
                    ac_cells++;
                    const char *va_txt = strchr(la, ' ') + 1;
                    if (rc >= 0) {
                        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
                        int c_agree = (va.verdict == 'm') &&
                                      va.start == (ptrdiff_t)ov[0] &&
                                      va.end == (ptrdiff_t)ov[1];
                        if (!c_agree)
                            fail("cell %d '%s' subject %d: A==C disagreement "
                                 "-- pcrec says %.*s, libpcre2 says match "
                                 "%zu %zu", id, desc, si,
                                 (int)strcspn(va_txt, "\n"), va_txt,
                                 (size_t)ov[0], (size_t)ov[1]);
                    } else {
                        if (va.verdict != 'n')
                            fail("cell %d '%s' subject %d: A==C disagreement "
                                 "-- pcrec says %.*s, libpcre2 says nomatch",
                                 id, desc, si,
                                 (int)strcspn(va_txt, "\n"), va_txt);
                    }
                }
            }
        }
        if (md) abi.match_data_free(md);
        if (code) abi.code_free(code);
        fclose(rf);
    }
    fclose(cf);

    if (ab_giveups != 0)
        fail("%ld A/B give-up cells -- not a verdict, and not expected on "
             "this table's DFA/VM-cheap pattern space", ab_giveups);
    if (ac_mlimits != 0)
        fail("%ld libpcre2 match-limit cells -- not a verdict, and not "
             "expected here", ac_mlimits);

    printf("definitions-oracle: %ld cells, %ld A==B comparisons, "
           "%ld A==C comparisons, %ld disagreements\n",
           ncells, ab_cells, ac_cells, (long)failures);
    if (failures == 0)
        printf("PASS: [DD-11.3] option-matrix self-oracle -- every "
               "resolved definition agrees with its row's shipped "
               "construct, and with libpcre2, cell for cell\n");
    return failures ? 1 : 0;
}
