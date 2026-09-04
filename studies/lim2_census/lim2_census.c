/* studies/lim2_census/lim2_census.c — [LIM-2] ruling 1's census (manager,
 * docs/dev/lanes/lim2_rulings.md, 2026-09-04): "the acceptance is a CENSUS:
 * over the whole corpus (every DFA-route artifact) and the bench's altwide
 * set, record per machine the raw table size and the minimized table size;
 * the check ASSERTS that the margin exceeds the measured MAX forward shrink
 * by at least 2x (RED with the table otherwise) and prints the distribution."
 *
 * STATUS (RULING 7, 2026-09-04): the mechanism this census was built to
 * validate — `src/ir/dfa.c`'s projected-size bail, keyed on a margin
 * (`BAIL_KEEP_PCT`) against this exact shrink — is WITHDRAWN from pcrec.
 * The census's OWN measurement survives as this study: a real corpus
 * pattern shrinks 97.06% on minimization (population of 12,
 * corpus-plus-altwide), which means 2x that shrink (194.1 points) has no
 * representable value as a percent-of-raw-bytes margin in [0,100) — the
 * finding that withdrew the bail, and the input STUDY-1 (docs/dev/
 * dfa_online_minimization_study.md, main) cites for its N2/N1 successor
 * design. See README.md in this directory for the protocol and the
 * committed data (`census_data.tsv`).
 *
 * WHAT THIS MEASURES. For every corpus/altwide pattern whose FORWARD
 * table-engine machine's raw (pre-minimize) transition table crosses
 * `PREMUL_MAX_ENTRIES` (65,535 entries — the point past which the indexed
 * representation is the machine's guaranteed form for the rest of its own
 * raw construction, `pcrec_build_dfa`'s own comment), this binary measures
 * that machine's RAW indexed-form table byte count and its MINIMIZED
 * indexed-form byte count, and reports the shrink. Below that threshold a
 * pattern contributes nothing to the question (no representation is
 * "guaranteed" there) and is correctly excluded from the population this
 * binary reports.
 *
 * METHODOLOGY, AND WHERE IT IS AND IS NOT A "CONTROL SHARING A SOURCE WITH
 * WHAT IT CONTROLS" (docs/dev/learnings.md S3). This binary links
 * `libpcrec.a` and drives the SAME internal pipeline functions
 * `src/core/compile.c`'s D7 fast path calls, in the same order (parse ->
 * altcls -> discharge_atomic -> callgraph_build -> select_engine ->
 * postresolve -> [pcrec_artifact_has_dfa_scan gate] -> build_nfa ->
 * nfa_has_bot gate -> nfa_wrap_unanchored -> build_dfa with size_bail=false
 * (a plain, un-modified `pcrec_build_dfa` on main -- this study no longer
 * carries the withdrawn `size_bail`/`size_bail_headstart` parameters or the
 * `PREMUL_DEAD`/`PREMUL_MAX_ENTRIES` promotion to internal.h; both reverted
 * with the bail, so this file spells `PREMUL_MAX_ENTRIES` as its own local
 * `#define`, below) -> pcrec_minimize_dfa), under DEFAULT options (no
 * --engine forcing, no -fprefilter-collapse, matching the compile_driver's
 * own FIRST attempt, where the collapse conjunct is unconditionally false —
 * see compile.c's `pfc_wanted`). What is INDEPENDENT: this binary runs real
 * subset construction and real minimization on real patterns and observes
 * what the ALGORITHM does. What is SHARED, deliberately: the byte-width
 * formula (`dfa_bytes_indexed`, below) mirrors `emit_dfa.c`'s
 * `emit_tr_table`'s own text-per-cell layout — because the question is "how
 * many indexed-form bytes would this machine's table cost", which is
 * geometry, not a judgment call; sharing a ruler is not the "control shares
 * a source with what it controls" failure shape (docs/dev/learnings.md S3)
 * — sharing a VERDICT would be, and this study renders no verdict at all.
 *
 * `dfa_bytes_indexed` computes the INDEXED-ASSUMED byte count on BOTH sides
 * of minimization even where the minimized machine's own entries happen to
 * drop back at or under `PREMUL_MAX_ENTRIES` (which population
 * scan (b) below reports on explicitly, as its own finding) — so it
 * inlines the identical per-cell formula unconditionally. This is the
 * SAME formula in two places for a reason: one caller (`pcrec_
 * dfa_indexed_table_bytes`) needs "a safe number or none, for a live
 * decision downstream"; this one needs "the number regardless, for a
 * measurement".
 *
 * INPUT. Every argv entry is either a `.rxt` file (read `pattern`/`features`
 * directives, run.sh's grammar, one measurement per pattern block — the
 * per-block `features` line overrides `PCREC_DEFAULT_FEATURES`, matching
 * what an ordinary corpus compile actually sees) or a `.rx` file (bench
 * altwide's shape: the WHOLE file is one pattern, always under `--features
 * all`, matching that set's own build convention — CLAUDE.md in that
 * directory names it).
 *
 * OUTPUT. One TSV row per population member on stdout (`id\traw_n\traw_ncls\t
 * raw_bytes\tmin_n\tmin_bytes\tshrink_pct`), then a summary block on stderr.
 * `run_census.sh` in this directory captures both into the committed
 * `census_data.tsv` / `census_summary.txt`. This binary only measures and
 * reports; it renders no verdict. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"

/* [LIM-2] withdrawn (ruling 7): this threshold was promoted to
 * src/core/internal.h as `PREMUL_MAX_ENTRIES` for the bail's own use and
 * reverted with it. `src/gen/emit_dfa.c` still owns the RULE (`dfa_premul`,
 * "n * ncls <= 65535 disqualifies pre-multiplication") privately; this is
 * only the NUMBER, spelled here as this study's own local copy -- a second
 * literal 65535, on purpose, the same shape `tests/codegen/
 * run_premul_table.sh` already uses for the same reason (a second CHECK is
 * not a second DEFINITION, but a STUDY outside the tree sharing emit_dfa.c's
 * #define is not an option at all). */
#define PREMUL_MAX_ENTRIES 65535

static long n_files, n_rx_files, n_blocks, n_candidates, n_refused, n_no_dfa_route;
static long n_has_bot, n_population;
static double max_shrink_pct = -1.0;
static char  max_shrink_id[256];
/* (b) above: how often a machine's raw entries cross the threshold but its
 * MINIMIZED entries drop back at or under it -- the representation-ambiguous
 * edge this binary's header discusses. Reported, never asserted: as argued
 * there, the early bail can only ever fire while raw entries are still
 * ABOVE the threshold, so this population never reaches an actual
 * mismatched emission -- it is a geometry fact worth knowing, not a defect. */
static long n_repr_ambiguous;

/* mirrors emit_tr_table's own per-cell text layout (src/gen/emit_dfa.c):
 * " %d," per cell, an 8-byte "\n       " line break every 16 cells -- see
 * this file's own header for why this is a second, deliberate copy of
 * pcrec_dfa_indexed_table_bytes's inner loop rather than a call to it. */
static long dfa_bytes_indexed(const Dfa *d)
{
    long bytes = 0, k = 0;
    for (int i = 0; i < d->n; i++) {
        for (int c = 0; c < d->ncls; c++, k++) {
            int t = d->st[i].tr[c];
            int cellv = t < 0 ? -1 : t;
            int w = 1;
            int av = cellv < 0 ? -cellv : cellv;
            while (av >= 10) { av /= 10; w++; }
            if (cellv < 0) w++;
            if (k % 16 == 0) bytes += 8;
            bytes += 2 + w;
        }
    }
    return bytes;
}

/* ---- one pattern -----------------------------------------------------------
 *
 * Returns true and fills the population row iff this pattern's forward
 * table-engine machine reaches the regime the bail's margin governs. False
 * for every other outcome (refused, no DFA route, ENG_ATTEMPT/bot-anchored,
 * or simply too small to cross the threshold) -- ALL counted, in the
 * distinct counters above, so a population that quietly shrank to nothing
 * is visible rather than silently green (docs/dev/learnings.md S3's own
 * demand). */
static bool measure_one(const char *pat, const char *features,
                        long *raw_n, long *raw_ncls, long *raw_bytes,
                        long *min_n, long *min_bytes)
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

    bool ok = false;
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
                nfa_wrap_unanchored(&cx, &cx.job->nfa);
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx.job->nfa.start, false);
                long re = (long)cx.job->dfa.n * (long)cx.job->dfa.ncls;
                if (re > PREMUL_MAX_ENTRIES) {
                    *raw_n = cx.job->dfa.n;
                    *raw_ncls = cx.job->dfa.ncls;
                    *raw_bytes = dfa_bytes_indexed(&cx.job->dfa);
                    pcrec_minimize_dfa(&cx, &cx.job->dfa);
                    *min_n = cx.job->dfa.n;
                    long me = (long)cx.job->dfa.n * (long)cx.job->dfa.ncls;
                    if (me <= PREMUL_MAX_ENTRIES) n_repr_ambiguous++;
                    *min_bytes = dfa_bytes_indexed(&cx.job->dfa);
                    ok = true;
                } else {
                    n_candidates++;   /* reached the DFA route, too small */
                }
            } else {
                n_has_bot++;   /* ENG_ATTEMPT route -- the bail never applies */
            }
        } else {
            n_no_dfa_route++;   /* VM-only, no DFA/prefilter at all */
        }
    } else {
        n_refused++;   /* K7-class cap, a reject-tier pattern, etc. */
    }

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
    return ok;
}

static void record(const char *id, long raw_n, long raw_ncls, long raw_bytes,
                   long min_n, long min_bytes)
{
    n_population++;
    double shrink_pct = raw_bytes > 0
        ? 100.0 * (double)(raw_bytes - min_bytes) / (double)raw_bytes
        : 0.0;
    if (shrink_pct > max_shrink_pct) {
        max_shrink_pct = shrink_pct;
        snprintf(max_shrink_id, sizeof max_shrink_id, "%s", id);
    }
    printf("%s\t%ld\t%ld\t%ld\t%ld\t%ld\t%.3f\n",
           id, raw_n, raw_ncls, raw_bytes, min_n, min_bytes, shrink_pct);
}

/* ---- .rxt reading (run.sh's grammar; the one .rxt reader this file needs:
 * `pattern`, `features` -- the rest of the format is irrelevant here) ------ */

static void trim_nl(char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == '\n' || s[n - 1] == '\r')) s[--n] = 0;
}

typedef struct { char pat[65536]; char feats[512]; int line; bool have; } Block;

static void block_run(Block *b, const char *path, const char *default_features)
{
    long raw_n, raw_ncls, raw_bytes, min_n, min_bytes;
    const char *feats = b->feats[0] ? b->feats : default_features;
    char id[600];
    snprintf(id, sizeof id, "%s:%d", path, b->line);
    n_blocks++;
    if (measure_one(b->pat, feats, &raw_n, &raw_ncls, &raw_bytes, &min_n, &min_bytes))
        record(id, raw_n, raw_ncls, raw_bytes, min_n, min_bytes);
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
 * `--features all` -- see /home/duxevents/pcrec-bench/bench/altwide/
 * CLAUDE.md; this binary only ever READS there. */
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
    /* the file may carry one trailing newline; the .rx files are otherwise
     * single-line patterns (verified: no embedded newline reaches this
     * binary's `pattern` field size limit on the corpus in hand). */
    trim_nl(pat);

    long raw_n, raw_ncls, raw_bytes, min_n, min_bytes;
    if (measure_one(pat, "all", &raw_n, &raw_ncls, &raw_bytes, &min_n, &min_bytes))
        record(path, raw_n, raw_ncls, raw_bytes, min_n, min_bytes);
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

    fprintf(stderr, "== [LIM-2] census summary ==\n");
    fprintf(stderr, "  .rxt files                       : %ld\n", n_files);
    fprintf(stderr, "  .rx files (bench altwide)         : %ld\n", n_rx_files);
    fprintf(stderr, "  pattern blocks seen                : %ld\n", n_blocks);
    fprintf(stderr, "  refused / K7-class cap              : %ld\n", n_refused);
    fprintf(stderr, "  no DFA route at all (VM-only)       : %ld\n", n_no_dfa_route);
    fprintf(stderr, "  ENG_ATTEMPT route (bot; would-be bail N/A) : %ld\n", n_has_bot);
    fprintf(stderr, "  DFA route, below premul threshold   : %ld\n", n_candidates);
    fprintf(stderr, "  POPULATION (crossed the threshold)  : %ld\n", n_population);
    fprintf(stderr, "  representation-ambiguous after min. : %ld\n", n_repr_ambiguous);
    fprintf(stderr, "  MAX forward shrink                  : %.3f%% (%s)\n",
            max_shrink_pct < 0 ? 0.0 : max_shrink_pct,
            n_population ? max_shrink_id : "(empty population)");
    fprintf(stderr, "  required margin (2x max shrink)     : %.3fpts (representable range: [0,100))\n",
            (max_shrink_pct < 0 ? 0.0 : max_shrink_pct) * 2.0);

    return 0;   /* this binary reports; nothing here renders a verdict */
}
