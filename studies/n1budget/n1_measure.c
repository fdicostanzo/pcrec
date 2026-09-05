/* studies/n1budget/n1_measure.c — [LIM-2] N1's own default-sizing measurement
 * (lane n1budget, 2026-09-04). MEASUREMENT ONLY: this binary and its Makefile
 * are never built or run by pcrec's top-level `make`/`make test`
 * (studies/CLAUDE.md's standing rule).
 *
 * WHAT THIS MEASURES, AND WHY. N1's charter (docs/dev/plan.md [LIM-2] row,
 * "N1 CHARTERED") requires the AUTO route's new DFA-construction-spend
 * budget to be "sized ABOVE every currently-compiling corpus artifact's
 * spend" in K7's own unit -- `Ctx.subset_elems` (src/core/internal.h),
 * the running total of NFA-state-list elements the priority subset
 * construction interns, already charged in src/ir/dfa.c's intern() and
 * already the quantity PCREC_MAX_SUBSET_ELEMS bounds. This binary drives
 * the SAME internal pipeline pcrec_compile's D7 fast path calls (modelled
 * directly on studies/lim2_census/lim2_census.c's own precedent and
 * methodology note) and reports, per pattern, the FINAL cx.subset_elems
 * value reached by a compile that does NOT refuse -- i.e. exactly the
 * population the new budget must not disturb.
 *
 * METHODOLOGY, matching lim2_census.c's own argument for why this is not
 * "a control sharing a source with what it controls" (docs/dev/learnings.md
 * S3): this binary runs REAL subset construction under DEFAULT options (no
 * --engine forcing, no -fprefilter-collapse -- compile_driver's own FIRST
 * attempt) and reads off a counter the compiler already maintains; it makes
 * no judgement about what the budget SHOULD be, only what today's population
 * SPENDS. The verdict (where the new limits.def row's default sits) is
 * written in the report that cites this data, not here.
 *
 * SCOPE. This binary builds the mandatory forward+reverse machines (the D7
 * fast path) exactly as lim2_census.c does, for EVERY pattern that reaches
 * the DFA route (not only those that cross lim2_census's own
 * PREMUL_MAX_ENTRIES threshold -- N1's question is the K7 charge, not the
 * emitted table's byte width, so there is no reason to exclude the smaller
 * population lim2_census's own question ignored). It ALSO builds the
 * OPTIONAL third machine ([ENG-ABS]'s anchored match-here form) for a
 * DFA-CHOSEN artifact, mirroring src/core/compile.c's own (static,
 * unexported) `build_anchored_dfa` inline rather than calling it -- so this
 * tool's MAX is the real total cx.subset_elems spend a corpus artifact pays
 * today under default (auto) options, forward route only (matching
 * lim2_census.c's and lim2_m1.c's own precedent: the reverse/anchored
 * machines built under `prune = false` for a REVERSE-rooted search are not
 * part of the D7 fast path and are out of scope here too).
 *
 * INPUT/OUTPUT shape: identical to lim2_census.c's (argv of .rxt/.rx files;
 * one TSV row per pattern block on stdout, a summary on stderr). Columns:
 * `id\troute\trefused\tsubset_elems\traw_n_fwd\traw_n_rev`. `route` is
 * `unanch` (D7 fast path, forward+reverse), `attempt` (ENG_ATTEMPT/bot,
 * where the mandatory build is forward-only against
 * PCREC_MAX_DFA_STATES_GOTO), or `none` (no DFA route at all, VM-only --
 * `subset_elems` is 0 and irrelevant). `refused` is 1 iff the compile hit
 * ANY ctx_fail (K7's own cap, or any other), in which case the row's
 * `subset_elems` is whatever had accumulated at the point of refusal (data,
 * not a claim that this pattern "compiles today" -- the summary's own MAX
 * OVER NON-REFUSED ROWS is the number the report actually wants). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"

static long n_files, n_rx_files, n_blocks, n_refused, n_unanch, n_attempt, n_none;
static long n_dfa_chosen_anchored_built;
static long long max_ok_subset_elems = -1;
static char max_ok_id[600];

/* ---- one pattern ----------------------------------------------------- */

static void measure_one(const char *pat, const char *features,
                         const char *id)
{
    char ferr[256];
    if (pcrec_enabled_set_spec(features, ferr, sizeof ferr) != 0) {
        fprintf(stderr, "FAIL: bad features spec '%s': %s\n", features, ferr);
        exit(2);
    }

    pcrec_options defo;
    pcrec_default_options(&defo);

    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.pat = pat;
    cx.patlen = strlen(pat);
    cx.opt = &defo;
    cx.want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
    cx.first_cap_pos = (size_t)-1;
    cx.first_vmonly_pos = (size_t)-1;
    cx.arena.cx = &cx;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }

    bool refused = false;
    const char *route = "none";
    long raw_n_fwd = 0, raw_n_rev = 0;

    if (setjmp(cx.jb) == 0) {
        pcrec_parse_mods_init(&cx);
        Ast *root = pcrec_parse(&cx);
        root = pcrec_altcls(&cx, root);
        root = pcrec_discharge_atomic(&cx, root);
        pcrec_callgraph_build(&cx, root);
        pcrec_select_engine(&cx, root);
        pcrec_postresolve(&cx, root);

        if (pcrec_artifact_has_dfa_scan(&cx)) {
            pcrec_build_nfa(&cx, root, &cx.job->nfa, false, false);
            if (!nfa_has_bot(&cx.job->nfa)) {
                route = "unanch";
                nfa_wrap_unanchored(&cx, &cx.job->nfa);
                pcrec_build_nfa(&cx, root, &cx.job->rnfa, true, false);
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx.job->nfa.start, false);
                pcrec_build_dfa(&cx, &cx.job->rnfa, &cx.job->rdfa, false, true,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx.job->rnfa.start, false);
                raw_n_fwd = cx.job->dfa.n;
                raw_n_rev = cx.job->rdfa.n;
                /* [ENG-ABS]'s optional third machine, mirrored from
                 * src/core/compile.c's own (static, unexported)
                 * build_anchored_dfa: built ONLY for a DFA-CHOSEN artifact,
                 * and it charges cx.subset_elems exactly as the two
                 * mandatory machines do (K7's comment: "the memory really
                 * was spent"). Included here so this tool's MAX is the real
                 * total spend a DFA-chosen corpus artifact pays today, not
                 * an under-count of it. */
                if (cx.job->fit.chosen == ENGM_DFA
                    && !(defo.flags & PCREC_NO_ANCHORED_DFA)) {
                    n_dfa_chosen_anchored_built++;
                    pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->adfa, true, false,
                                    PCREC_ANCHORED_MAX_STATES,
                                    cx.job->nfa.anch_start, true);
                }
            } else {
                route = "attempt";
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_GOTO,
                                cx.job->nfa.start, false);
                raw_n_fwd = cx.job->dfa.n;
            }
        }
    } else {
        refused = true;
        n_refused++;
    }

    if (!refused) {
        if (!strcmp(route, "unanch")) n_unanch++;
        else if (!strcmp(route, "attempt")) n_attempt++;
        else n_none++;
        if (cx.subset_elems > max_ok_subset_elems) {
            max_ok_subset_elems = cx.subset_elems;
            snprintf(max_ok_id, sizeof max_ok_id, "%s", id);
        }
    }

    printf("%s\t%s\t%d\t%lld\t%ld\t%ld\n",
           id, route, refused ? 1 : 0, (long long)cx.subset_elems,
           raw_n_fwd, raw_n_rev);

    free(cx.job->nfa.st);
    free(cx.job->rnfa.st);
    free(cx.job->dfa.st);
    free(cx.job->dfa.tab);
    free(cx.job->rdfa.st);
    free(cx.job->rdfa.tab);
    free(cx.job->adfa.st);
    free(cx.job->adfa.tab);
    free(cx.job);
    arena_free(&cx.arena);
}

/* ---- .rxt reading (run.sh's grammar, lim2_census.c's own precedent) --- */

static void trim_nl(char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == '\n' || s[n - 1] == '\r')) s[--n] = 0;
}

typedef struct { char pat[65536]; char feats[512]; int line; bool have; } Block;

static void block_run(Block *b, const char *path, const char *default_features)
{
    const char *feats = b->feats[0] ? b->feats : default_features;
    char id[600];
    snprintf(id, sizeof id, "%s:%d", path, b->line);
    n_blocks++;
    measure_one(b->pat, feats, id);
}

static void do_rxt_file(const char *path, const char *default_features)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); exit(2); }
    n_files++;

    static char line[65536];
    Block b; memset(&b, 0, sizeof b);
    int lineno = 0;

    while (fgets(line, sizeof line, f)) {
        lineno++;
        trim_nl(line);
        if (line[0] == '#' || line[0] == 0) continue;

        if (strncmp(line, "pattern ", 8) == 0) {
            if (b.have) block_run(&b, path, default_features);
            memset(&b, 0, sizeof b);
            size_t n = strlen(line + 8);
            if (n >= sizeof b.pat) n = sizeof b.pat - 1;
            memcpy(b.pat, line + 8, n);
            b.pat[n] = 0;
            b.line = lineno;
            b.have = true;
            continue;
        }
        if (!b.have) continue;
        if (strncmp(line, "features ", 9) == 0) {
            size_t n = strlen(line + 9);
            if (n >= sizeof b.feats) n = sizeof b.feats - 1;
            memcpy(b.feats, line + 9, n);
            b.feats[n] = 0;
        }
    }
    if (b.have) block_run(&b, path, default_features);
    fclose(f);
}

/* bench altwide's shape: one whole file is one pattern, always under
 * `--features all` -- lim2_census.c's own precedent. */
static void do_rx_file(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); exit(2); }
    n_rx_files++;
    n_blocks++;

    static char pat[65536];
    size_t got = fread(pat, 1, sizeof pat - 1, f);
    pat[got] = 0;
    fclose(f);
    trim_nl(pat);

    measure_one(pat, "all", path);
}

static bool ends_with(const char *s, const char *suffix)
{
    size_t ns = strlen(s), nsuf = strlen(suffix);
    return ns >= nsuf && strcmp(s + ns - nsuf, suffix) == 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s FILE.rxt|FILE.rx ...\n", argv[0]);
        return 2;
    }

    const char *deflt = PCREC_DEFAULT_FEATURES;

    for (int i = 1; i < argc; i++) {
        if (ends_with(argv[i], ".rxt"))
            do_rxt_file(argv[i], deflt);
        else if (ends_with(argv[i], ".rx"))
            do_rx_file(argv[i]);
        else {
            fprintf(stderr, "FAIL: unrecognised extension: %s\n", argv[i]);
            return 2;
        }
    }

    fprintf(stderr, "== [LIM-2] N1 default-sizing measurement ==\n");
    fprintf(stderr, "  .rxt files                  : %ld\n", n_files);
    fprintf(stderr, "  .rx files (bench altwide)    : %ld\n", n_rx_files);
    fprintf(stderr, "  pattern blocks seen           : %ld\n", n_blocks);
    fprintf(stderr, "  refused (any ctx_fail)         : %ld\n", n_refused);
    fprintf(stderr, "  route=unanch, not refused      : %ld\n", n_unanch);
    fprintf(stderr, "  route=attempt, not refused     : %ld\n", n_attempt);
    fprintf(stderr, "  route=none (VM-only), not refused : %ld\n", n_none);
    fprintf(stderr, "  DFA-chosen, anchored 3rd machine built : %ld\n",
            n_dfa_chosen_anchored_built);
    fprintf(stderr, "  MAX subset_elems over NON-REFUSED rows : %lld (%s)\n",
            max_ok_subset_elems < 0 ? 0 : max_ok_subset_elems,
            max_ok_subset_elems < 0 ? "(empty population)" : max_ok_id);

    return 0;   /* this binary reports; nothing here renders a verdict */
}
