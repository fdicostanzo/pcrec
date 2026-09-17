/* studies/lim2_m2/lim2_m2.c -- [LIM-2]/dfamin M2, the dominance-prize
 * measurement. Lane dfam12, 2026-09-16.
 *
 * WHAT THIS MEASURES. docs/dev/dfa_online_minimization_study.md §3.7/§5.2
 * M2: how much would candidate B's Tier-1 dominated-position pruning win,
 * using the study's own named "deliberately illegitimate stand-in" for the
 * general simulation preorder -- "drop a position when an earlier copy of
 * the same unrolled repeat is present in the list" (§3.7's "one tempting
 * shortcut", explicitly sanctioned there for SIZING the win, never as a
 * landing). The stand-in is implemented as a real, measurement-only edit to
 * this worktree's src/ir/nfa.c (tags each X{m,n} tail-loop copy's NFA nodes
 * with (probe_rep_id, probe_copy_idx)) and src/ir/dfa.c (probe_m2_prune,
 * applied to a closure's position list the instant it is built, BEFORE
 * intern()'s K7 charge / dhash / view_same ever see it) -- gated on
 * getenv("PCREC_PROBE_M2") so ONE binary drives both the baseline and the
 * pruned measurement. See docs/dev/dfamin_m1m2.md for the disposition (does
 * this land, and how the approximation is stated).
 *
 * This binary runs the SAME pipeline prefix studies/lim2_m1/lim2_m1.c's
 * measure_raw() already established works for this purpose (parse ->
 * altcls -> discharge_atomic -> callgraph_build -> select_engine ->
 * postresolve -> [pcrec_artifact_has_dfa_scan gate] -> build_nfa ->
 * nfa_has_bot gate -> nfa_wrap_unanchored -> build_dfa -> minimize_dfa),
 * under DEFAULT options, and reports for EACH pattern, in ONE process (so
 * the mode -- on or off -- is fixed for the whole run by the environment):
 *
 *   raw_n           dfa.n after pcrec_build_dfa (this run's mode)
 *   min_n           dfa.n after pcrec_minimize_dfa on that same raw machine
 *   subset_elems    cx.subset_elems -- the K7 charge, sum(nlist) over every
 *                   interned view that was not an alias of an earlier one
 *   probe_total     pcrec_probe_m2_total (0 if PCREC_PROBE_M2 is unset)
 *   probe_dropped   pcrec_probe_m2_dropped (0 if PCREC_PROBE_M2 is unset)
 *
 * Run this binary TWICE -- once with PCREC_PROBE_M2 unset (baseline) and
 * once with PCREC_PROBE_M2=1 (pruned) -- and diff raw_n/min_n/subset_elems
 * per pattern id (run_m2.sh does this). A single process cannot do both,
 * because probe_m2_enabled() in src/ir/dfa.c caches getenv() in a function-
 * static on first call -- correct for this binary's own use (one mode per
 * process, matching every other axis flag in this tree) and NOT something
 * this harness works around, since working around it would mean re-reading
 * getenv() per pattern, which is not what the shipped mechanism (were it
 * ever to ship) would do either.
 *
 * SCOPE: forward machine only, matching lim2_m1.c's and lim2_census.c's own
 * precedent. No timing is taken anywhere in this file -- this lane's brief
 * is explicit that M2 makes no timing claim (D77; a mechanism is not built
 * here, only sized). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"

/* [PROBE-M2] declared in src/ir/dfa.c; not part of the public API, read
 * directly the way lim2_m1.c/lim2_census.c already read Ctx/Dfa fields. */
extern long long pcrec_probe_m2_dropped;
extern long long pcrec_probe_m2_total;

static bool measure_raw(const char *pat, Dfa *out_dfa, Ctx *cx_out,
                         bool *skip_no_dfa, bool *skip_bot)
{
    pcrec_options defo;
    pcrec_default_options(&defo);

    memset(cx_out, 0, sizeof *cx_out);
    cx_out->pat = pat;
    cx_out->patlen = strlen(pat);
    cx_out->opt = &defo;
    cx_out->want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
    cx_out->first_cap_pos = (size_t)-1;
    cx_out->first_vmonly_pos = (size_t)-1;
    cx_out->arena.cx = cx_out;
    cx_out->job = calloc(1, sizeof(Job));
    if (!cx_out->job) { fprintf(stderr, "FAIL: oom\n"); exit(2); }

    *skip_no_dfa = false; *skip_bot = false;
    bool ok = false;
    if (setjmp(cx_out->jb) == 0) {
        pcrec_parse_mods_init(cx_out);
        Ast *root = pcrec_parse(cx_out);
        root = pcrec_altcls(cx_out, root);
        root = pcrec_discharge_atomic(cx_out, root);
        pcrec_callgraph_build(cx_out, root);
        pcrec_select_engine(cx_out, root);
        pcrec_postresolve(cx_out, root);

        if (pcrec_artifact_has_dfa_scan(cx_out)) {
            pcrec_build_nfa(cx_out, root, &cx_out->job->nfa, false, false);
            if (!nfa_has_bot(&cx_out->job->nfa)) {
                nfa_wrap_unanchored(cx_out, &cx_out->job->nfa);
                pcrec_build_dfa(cx_out, &cx_out->job->nfa, &cx_out->job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx_out->job->nfa.start, false);
                *out_dfa = cx_out->job->dfa;
                ok = true;
            } else {
                *skip_bot = true;
            }
        } else {
            *skip_no_dfa = true;
        }
    } else {
        ok = false; /* refused (a cap fired) */
    }
    return ok;
}

static void free_ctx(Ctx *cx)
{
    if (cx->job) {
        free(cx->job->nfa.st);
        free(cx->job->rnfa.st);
        free(cx->job->rdfa.st); free(cx->job->rdfa.tab);
        free(cx->job->adfa.st); free(cx->job->adfa.tab);
        free(cx->job);
    }
    arena_free(&cx->arena);
}

static long g_seen = 0, g_refused = 0, g_no_dfa = 0, g_bot = 0, g_ok = 0;

static void do_one(const char *id, const char *pat, FILE *out)
{
    g_seen++;
    Dfa raw; Ctx cx; bool skip_no_dfa, skip_bot;
    long long t0 = pcrec_probe_m2_total, d0 = pcrec_probe_m2_dropped;
    if (!measure_raw(pat, &raw, &cx, &skip_no_dfa, &skip_bot)) {
        if (skip_no_dfa) g_no_dfa++;
        else if (skip_bot) g_bot++;
        else {
            g_refused++;
            fprintf(stderr, "REFUSED %s: overflowed=%d why=\"%s\" subset_elems=%lld\n",
                    id, cx.dfa_overflowed, cx.dfa_overflow_why, cx.subset_elems);
        }
        free_ctx(&cx);
        return;
    }
    long raw_n = raw.n;
    long long subset_elems = cx.subset_elems;
    long long probe_total = pcrec_probe_m2_total - t0;
    long long probe_dropped = pcrec_probe_m2_dropped - d0;

    pcrec_minimize_dfa(&cx, &cx.job->dfa);
    long min_n = cx.job->dfa.n;

    fprintf(out, "%s\t%ld\t%ld\t%lld\t%lld\t%lld\n",
            id, raw_n, min_n, subset_elems, probe_total, probe_dropped);
    g_ok++;
    free(cx.job->dfa.st); free(cx.job->dfa.tab);
    free_ctx(&cx);
}

static void trim_nl(char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == '\n' || s[n - 1] == '\r')) s[--n] = 0;
}

/* Force-file reader: every `pattern <PAT>` line in a .rxt file, matching
 * lim2_m1.c's do_rxt_file() line-prefix convention. `features` lines are
 * IGNORED here (unlike lim2_m1.c) -- this population is all base-grammar
 * patterns (K18/K25/counterk/classes never need a --features spec), and a
 * pattern this binary cannot parse under base grammar shows up honestly as
 * g_refused rather than silently compiling under an assumed feature set. */
static void do_rxt_file(const char *path, FILE *out)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); exit(2); }
    static char line[65536];
    int lineno = 0;
    while (fgets(line, sizeof line, f)) {
        lineno++;
        trim_nl(line);
        if (strncmp(line, "pattern ", 8) != 0) continue;
        char id[600];
        snprintf(id, sizeof id, "%s:%d", path, lineno);
        do_one(id, line + 8, out);
    }
    fclose(f);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s FILE.rxt [FILE.rxt ...]\n", argv[0]);
        return 2;
    }
    for (int i = 1; i < argc; i++)
        do_rxt_file(argv[i], stdout);

    fprintf(stderr, "== [LIM-2]/dfamin M2 summary (mode=%s) ==\n",
            getenv("PCREC_PROBE_M2") ? "PRUNED" : "baseline");
    fprintf(stderr, "  pattern lines seen : %ld\n", g_seen);
    fprintf(stderr, "  refused            : %ld\n", g_refused);
    fprintf(stderr, "  no DFA route       : %ld\n", g_no_dfa);
    fprintf(stderr, "  ENG_ATTEMPT (bot)  : %ld\n", g_bot);
    fprintf(stderr, "  measured (rows)    : %ld\n", g_ok);
    return 0;
}
