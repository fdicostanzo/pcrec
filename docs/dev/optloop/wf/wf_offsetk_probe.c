/* [WORD-FOLD] THE (?i) OFFSET-k DEGRADATION CENSUS — a throwaway analyzer.
 *
 * `docs/design/offset_k_skip.md` §3.4 already states the fact this probe
 * measures a POPULATION for: "case-folded literals | the fold pair, from the
 * parser's own bitmap | (?i)needle -> {Nn}{Ee}{Ee}{Dd}{Ll}{Ee}". A fold-pair
 * offset carries TWO bytes, so `memchr` (which needs exactly one) cannot
 * scan it, and today's selection (`pcrec_prefix_ksets`, `src/opt/
 * prefix_k.c`) can only pick a `k[j].count == 1` offset as its `scan`
 * member — `docs/dev/plan.md`'s `[WORD-FOLD]` row's own claim ("the DFA's
 * offset-k candidate-start skip DEGRADES TO NOTHING under (?i)") restated as
 * a measurable predicate: does EVERY offset the walk proves degrade to
 * `count > 1`, or does at least one CASE-INVARIANT offset survive (a digit,
 * punctuation or `_` position, which never folds)?
 *
 * This drives the REAL walk (`pcrec_prefix_ksets`), not a re-derivation of
 * it, over the REAL pipeline prefix up to NFA construction — parse + altcls
 * + discharge_atomic + callgraph_build + select_engine + postresolve +
 * lower_enc + build_nfa(forward, exact) + nfa_wrap_unanchored — matching
 * `src/core/compile.c`'s own order exactly (this project's own recorded
 * lesson, `reqpos_probe.c`'s header: "an analysis's answer is a property of
 * the tree at its own call site").
 *
 * `k0` (the offset-0 byte set) is passed as THE WHOLE ALPHABET — this probe
 * does not reconstruct `emit_dfa.c`'s `cand_from_escapes` DFA-start-state
 * derivation, which needs a built DFA this probe does not build. That is a
 * DECLARED SCOPE LIMIT, not a soundness gap in what is reported: `k[0]` is
 * simply not read below, and offsets `j >= 1` come entirely from the NFA
 * walk per `docs/design/offset_k_skip.md` §3 ("offsets >= 1 come from this
 * walk, offset 0 keeps coming from the DFA derivation"), unaffected by what
 * `k0` says.
 *
 * Build (never by `make`):
 *   gcc -O2 -Ilib -Isrc -o wf_offsetk_probe wf_offsetk_probe.c build/libpcrec.a
 * Input : one record per line, `id<TAB>hex-encoded pattern bytes`.
 * Output: one TSV row per record.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

int main(void)
{
    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    static uint8_t k0[256];
    memset(k0, 1, sizeof k0);

    printf("id\tstatus\tnwalk\tany_invariant\tfirst_invariant_k\t"
           "counts_csv\n");

    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        if (!got) continue;
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        const char *id = line, *hex = tab + 1;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) {
            unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v;
        }
        pat[hn] = 0;

        pcrec_options defo;
        pcrec_default_options(&defo);
        Ctx cx;
        memset(&cx, 0, sizeof cx);
        cx.pat = pat;
        cx.patlen = hn;
        cx.opt = &defo;
        cx.want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
        cx.first_cap_pos = (size_t)-1;
        cx.first_vmonly_pos = (size_t)-1;
        cx.arena.cx = &cx;
        cx.enabled_features = pcrec_enabled_mask();
        cx.job = calloc(1, sizeof(Job));
        if (!cx.job) { fprintf(stderr, "out of memory\n"); return 2; }

        volatile int ok = 0;
        PrefixKSets ks; memset(&ks, 0, sizeof ks);
        if (setjmp(cx.jb) == 0) {
            pcrec_parse_mods_init(&cx);
            Ast *root = pcrec_parse_info(&cx, NULL);
            if (root) root = pcrec_altcls(&cx, root);
            if (root) root = pcrec_discharge_atomic(&cx, root);
            if (root) {
                pcrec_callgraph_build(&cx, root);
                pcrec_select_engine(&cx, root);
                pcrec_postresolve(&cx, root);
                root = pcrec_lower_enc(&cx, root);
            }
            if (root) {
                pcrec_build_nfa(&cx, root, &cx.job->nfa, false, false);
                if (!pcrec_nfa_has_bot(&cx.job->nfa)) {
                    pcrec_nfa_wrap_unanchored(&cx, &cx.job->nfa);
                    pcrec_prefix_ksets(&cx, &cx.job->nfa, k0, &ks);
                    ok = 1;
                }
            }
        }

        if (!ok) {
            printf("%s\trefused-or-bot\t0\t0\t-1\t-\n", id);
        } else {
            int any_inv = 0, first_inv = -1;
            char counts[512]; size_t off = 0; counts[0] = 0;
            for (int j = 0; j < ks.nwalk && j < PCREC_PREFIX_K_MAX; j++) {
                if (j >= 1 && ks.k[j].count == 1 && first_inv < 0) {
                    any_inv = 1; first_inv = ks.k[j].k;
                }
                off += (size_t)snprintf(counts + off, sizeof(counts) - off,
                                       "%s%d", j ? "," : "", ks.k[j].count);
                if (off >= sizeof counts) break;
            }
            printf("%s\tok\t%d\t%d\t%d\t%s\n", id, ks.nwalk, any_inv,
                  first_inv, counts[0] ? counts : "-");
        }
        pcrec_arena_free(&cx.arena);
        free(cx.job);
        free(pat);
    }
    free(line);
    return 0;
}
