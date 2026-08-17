/* tests/possessify/possdiff_driver.c — THE PRIMARY INSTRUMENT for [ENG-BREP]'s
 * possessification rung (eng_brep_design.md §5.1).
 *
 * WHY A pcrec-vs-pcrec DIFFERENTIAL IS THE STRONGEST CHECK AVAILABLE HERE, and
 * not merely a convenient one. Possessification's entire claim is that it
 * changes NO answer: the same pattern, compiled with the rewrite and compiled
 * with `-fno-possessify`, must agree on every subject. The denied build is not
 * an approximation of the semantics — it IS the shipped semantics, the code
 * that runs today — so this check needs no external oracle to have an opinion,
 * and ANY disagreement is a bug by construction rather than a question about
 * which engine is right. The three-way oracle sweep (§5.3) rides on top of
 * this; it does not replace it.
 *
 * It also dodges a measured hazard the oracles have here. U9
 * (docs/dev/upstream_issues.md): PCRE2 10.46 and python `re` disagree about
 * possessive bounded repeats of a GROUP — `a?(?:b){0,4}+a` on "a" is no-match
 * in PCRE2 and (0,1) in python and in fact — and that shape sits inside
 * exactly the family this row sweeps. Comparing pcrec against pcrec has no
 * such seam.
 *
 * WHAT IS COMPARED, and the last two are the ones a weaker check would drop:
 *
 *   1. the match SPAN;
 *   2. EVERY capture slot, all NCAPS pairs, including the ones the subject
 *      leaves unset — compared as ptrdiff_t pairs, never as strings. The R24
 *      soundness critic recorded this as latent blindness in the design lane's
 *      own probe, which compared substrings and so could not see two different
 *      offsets that spell the same bytes;
 *   3. the FAILURE SURFACE — a subject that exhausts the frame array or the
 *      step budget must produce the SAME outcome from both artifacts. This is
 *      what stops a strategy from passing by being quietly more forgiving than
 *      the ground truth. It is deliberately not "both fail somehow";
 *   4. both artifacts' own STAMPED capacities, printed by the harness from
 *      rx_info, so a strategy that changes the real limit without changing the
 *      stamp is visible.
 *
 * Usage: possdiff_driver < subjects   (one escaped subject per line, the same
 * escapes tests/harness/driver.c and tests/vm/vm_driver.c decode). Prints
 * nothing on agreement beyond a one-line tally; prints the disagreeing cell
 * and exits 1 on any divergence. Exit 2 is a malformed input line — a broken
 * instrument, never a finding.
 */

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Two artifacts, two prefixes, ONE translation unit. That is a real property
 * being exercised rather than a convenience: the fixed ABI types are emitted
 * under a prefix-INDEPENDENT include guard precisely so differently-prefixed
 * headers can share a TU (src/gen/CLAUDE.md, D44/A-2, and the R21 panel's
 * measurement that a per-prefix guard fails this exact case). */
#include "pa.h"
#include "pb.h"
#ifdef DIFF_REFEREE
/* [M4.6d] THE THIRD ARM, opt-in and used by tests/mrl/run_mrldiff.sh alone.
 *
 * `pc` is the SAME pattern built `--no-captures`, which selects the pure DFA
 * engine: a table-driven linear-time machine that MRL does not touch at all
 * and that always terminates. It is capture-blind, so it can referee the
 * SPAN and nothing else — which is exactly the quantity an over-large
 * minimum-remaining-length would delete, and exactly what neither of the two
 * main arms can supply when one of them has given up.
 *
 * IT LIVES IN THIS DRIVER rather than in a second executable so that it reads
 * the SAME decoded subject at the SAME start position as the cells it
 * referees. A separate referee would need its own copy of decode() above, and
 * a control that re-derives its own input from a second source is the failure
 * this project has recorded twice. */
#include "pc.h"
#endif

/* WHICH TWO BUILDS these are is the caller's business, not this file's. The
 * driver's whole content is "two artifacts of the same pattern must agree on
 * span, every slot and the failure surface", which is the same claim for every
 * member of D47.3's deny family — so the [ENG-BREP] rung-select suite
 * (tests/rungselect/) links this same driver with its own pair rather than
 * keeping a second copy of a comparison that would then have to be kept in
 * step. Only the words in the divergence report differ, and they come in
 * through these two defines. */
#ifndef DIFF_A_LABEL
#define DIFF_A_LABEL "possessified"
#endif
#ifndef DIFF_B_LABEL
#define DIFF_B_LABEL "-fno-possessify"
#endif

#if PA_NCAPS != PB_NCAPS
#error "the two builds disagree on the capture count: not the same pattern"
#endif

static int hexval(unsigned char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static unsigned char *decode(const char *src, size_t srclen, size_t *out_len)
{
    unsigned char *buf = malloc(srclen > 0 ? srclen : 1);
    if (!buf) return NULL;
    size_t n = 0;
    for (size_t i = 0; i < srclen; i++) {
        unsigned char c = (unsigned char)src[i];
        if (c != '\\') { buf[n++] = c; continue; }
        if (++i >= srclen) { free(buf); return NULL; }
        switch ((unsigned char)src[i]) {
        case 'n': buf[n++] = '\n'; break;
        case 't': buf[n++] = '\t'; break;
        case 'r': buf[n++] = '\r'; break;
        case 'f': buf[n++] = '\f'; break;
        case 'v': buf[n++] = '\v'; break;
        case '\\': buf[n++] = '\\'; break;
        case '"': buf[n++] = '"'; break;
        case 'x': {
            if (i + 2 >= srclen) { free(buf); return NULL; }
            int hi = hexval((unsigned char)src[i + 1]);
            int lo = hexval((unsigned char)src[i + 2]);
            if (hi < 0 || lo < 0) { free(buf); return NULL; }
            buf[n++] = (unsigned char)(hi * 16 + lo);
            i += 2;
            break;
        }
        default: free(buf); return NULL;
        }
    }
    *out_len = n;
    return buf;
}

/* One outcome, whatever kind it is. Keeping the error returns in the SAME
 * value space as the match makes "the failure surfaces agree" the same
 * comparison as "the spans agree" rather than a second, weaker one. */
static void describe(int r, const ptrdiff_t caps[][2], char *out, size_t osz)
{
    if (r == PA_ERR_STEPS)  { snprintf(out, osz, "err_steps");  return; }
    if (r == PA_ERR_FRAMES) { snprintf(out, osz, "err_frames"); return; }
    if (r != 1)             { snprintf(out, osz, "nomatch");    return; }
    size_t n = (size_t)snprintf(out, osz, "match");
    for (int k = 0; k < PA_NCAPS && n < osz; k++)
        n += (size_t)snprintf(out + n, osz - n, " %td,%td",
                              caps[k][0], caps[k][1]);
}

int main(void)
{
    char line[65536];
    long long cells = 0, diverged = 0;
#ifdef DIFF_A_MAY_ANSWER_MORE
    /* Declared under the same guard as its only writer and its only reader:
     * the other three suites build this driver -Wall -Wextra -Werror, and a
     * counter they never touch is -Wunused-variable there. */
    long long excused = 0;
#ifdef DIFF_REFEREE
    long long refereed = 0;
#endif
#endif

    while (fgets(line, sizeof line, stdin)) {
        size_t ll = strlen(line);
        while (ll && (line[ll - 1] == '\n' || line[ll - 1] == '\r')) ll--;
        line[ll] = 0;
        /* A line that is exactly "#" is a comment; an EMPTY line is a real
         * subject (the empty string), which is a cell the sweep must keep. */
        if (ll && line[0] == '#') continue;

        size_t len = 0;
        unsigned char *subj = decode(line, ll, &len);
        if (!subj) {
            fprintf(stderr, "possdiff: malformed subject line: %s\n", line);
            return 2;
        }

        /* Every start position, not just 0. A possessified loop that gets the
         * leftmost-first search wrong would still agree at startpos 0 on many
         * subjects; sweeping the starts is what makes the search entry's own
         * behaviour part of the comparison. */
        for (size_t sp = 0; sp <= len; sp++) {
            ptrdiff_t ca[PA_NCAPS][2], cb[PB_NCAPS][2];
            for (int k = 0; k < PA_NCAPS; k++) {
                ca[k][0] = ca[k][1] = -2;
                cb[k][0] = cb[k][1] = -2;
            }
            int ra = pa_search(subj, len, sp, ca);
            int rb = pb_search(subj, len, sp, cb);
            cells++;

            bool same = (ra == rb);
            if (same && ra == 1)
                for (int k = 0; k < PA_NCAPS; k++)
                    if (ca[k][0] != cb[k][0] || ca[k][1] != cb[k][1]) {
                        same = false;
                        break;
                    }
#ifdef DIFF_A_MAY_ANSWER_MORE
            /* THE ONE ASYMMETRY, opt-in and off by default.
             *
             * An optimization whose whole purpose is to turn a RESOURCE
             * REFUSAL into an ANSWER cannot be held to "the failure surfaces
             * are identical" -- that requirement, taken literally, forbids
             * the feature. [M4.6d]'s MRL pruning is exactly that case: it
             * removes positions from which nothing could have succeeded, so
             * a search that used to exhaust the step budget now completes,
             * and the differential saw `nomatch` against `err_steps` on 22 of
             * 202,458 cells. (run_possdiff.sh's own header records the same
             * tension one rung over, where possessification changes a loop's
             * FRAME requirement.)
             *
             * So arm A is allowed to ANSWER where arm B GAVE UP, and nothing
             * else moves. The reverse is still a divergence -- A giving up
             * where B answers is a regression, which is the direction that
             * matters. And two arms that both answer must still agree on the
             * span and every capture slot, which is the claim this driver
             * exists for and which is untouched: a give-up carries no
             * captures to compare, so no cell where the answers could differ
             * is excused by this branch.
             *
             * A cell that goes quiet this way is INVISIBLE to the sweep's
             * own count, which is why the suite enabling it also pins the
             * step budget: the exemption should be reached by a handful of
             * genuinely pathological cells, not by a budget so low that half
             * the corpus stops being compared. */
            if (!same && ra != PA_ERR_STEPS && ra != PA_ERR_FRAMES &&
                (rb == PA_ERR_STEPS || rb == PA_ERR_FRAMES)) {
                same = true;
                excused++;
#ifdef DIFF_REFEREE
                /* REFEREE THE EXCUSED CELL rather than taking it on trust.
                 * Arm A answered and arm B gave up, so the sweep has no
                 * second opinion on A's span — and the excused cells are by
                 * construction the ones where MRL did the MOST work, i.e.
                 * the least comfortable place to have none. The DFA arm has
                 * one. */
                {
                    ptrdiff_t cc[PC_NCAPS][2];
                    int rc = pc_search(subj, len, sp, cc);
                    int a_matched = (ra == 1);
                    int c_matched = (rc == 1);
                    refereed++;
                    if (a_matched != c_matched ||
                        (a_matched && (ca[0][0] != cc[0][0] ||
                                       ca[0][1] != cc[0][1]))) {
                        fprintf(stderr,
                                "REFEREE DIVERGENCE (excused cell) subject=%s"
                                " startpos=%zu\n"
                                "  " DIFF_A_LABEL ": %s\n"
                                "  --no-captures (pure DFA, MRL-free): %s\n",
                                line, sp,
                                a_matched ? "match" : "nomatch",
                                c_matched ? "match" : "nomatch");
                        if (a_matched && c_matched)
                            fprintf(stderr, "  spans: %td,%td vs %td,%td\n",
                                    ca[0][0], ca[0][1], cc[0][0], cc[0][1]);
                        same = false;   /* a real divergence after all */
                        excused--;
                    }
                }
#endif
            }
#endif
            if (!same) {
                char da[4096], db[4096];
                describe(ra, ca, da, sizeof da);
                describe(rb, cb, db, sizeof db);
                fprintf(stderr,
                        "DIVERGENCE subject=%s startpos=%zu\n"
                        "  " DIFF_A_LABEL ": %s\n"
                        "  " DIFF_B_LABEL ": %s\n",
                        line, sp, da, db);
                diverged++;
                if (diverged > 20) {
                    fprintf(stderr, "possdiff: too many divergences, stopping\n");
                    free(subj);
                    printf("cells %lld diverged %lld\n", cells, diverged);
#ifdef DIFF_A_MAY_ANSWER_MORE
                    printf("excused %lld\n", excused);
#endif
                    return 1;
                }
            }
        }
        free(subj);
    }

    printf("cells %lld diverged %lld\n", cells, diverged);
#ifdef DIFF_A_MAY_ANSWER_MORE
    /* COUNTED AND PRINTED, never silently swallowed. A cell the asymmetry
     * excuses is a cell this sweep did NOT compare, so it has to be visible or
     * the exemption can grow without anyone noticing — a differential whose
     * excused count drifts up is losing power one cell at a time, and "2 of
     * 202,458" is only reassuring while somebody re-reads the 2. The caller
     * asserts this number against a pinned expectation. */
    printf("excused %lld\n", excused);
#ifdef DIFF_REFEREE
    printf("refereed %lld\n", refereed);
#endif
#endif
    return diverged ? 1 : 0;
}
