/* b3meas machine dump (lane b3meas, 2026-10-12): the two TAG machines B3's
 * one walk is the product of, as tables.  A D77 instrument, never wired into
 * the build.  Links libpcrec.a and builds, exactly as ../b3cost_probe.c does
 * (the real parse/lowering pipeline, pcrec_build_min_dfa, no scan-edge pass),
 * the reverse machines of tag0 = X\z and tag1 = X\n\z, and prints them; gen.py
 * builds the tagged product, minimizes it and emits the twin's C.
 *
 * stdin rows: id <TAB> enc <TAB> hex(tag0) <TAB> hex(tag1)
 * stdout:     ROW id ok|fail, then per machine k in {0,1}:
 *             M k n ncls natoms clsctx s0 / CLS 256 / ACC n / TR n*ncls / EOL n / END n
 *
 *    gcc -O1 -Ilib -Isrc docs/design/endmark/b3meas/probe.c build/libpcrec.a \
 *        -o build/scratch/b3meas_probe
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

static int build(const char *pat, int enc, Dfa *out)
{
    Ctx *cx = calloc(1, sizeof *cx);
    pcrec_options *defo = calloc(1, sizeof *defo);
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->want_caps = false;
    cx->job = calloc(1, sizeof(Job));
    cx->arena.cx = cx;
    Ast *root = NULL;
    if (setjmp(cx->jb) != 0) return 0;
    pcrec_parse_mods_init(cx);
    root = pcrec_parse_info(cx, NULL);
    if (root) root = pcrec_altcls(cx, root);
    if (root) root = pcrec_discharge_atomic(cx, root);
    if (root) { pcrec_callgraph_build(cx, root); pcrec_facts_seal_e1(cx, root); pcrec_select_engine(cx, root); }
    if (root) pcrec_postresolve(cx, root);
    if (root) root = pcrec_lower_enc(cx, root);
    if (!root) return 0;
    pcrec_build_nfa(cx, root, &cx->job->rnfa, true, false);
    pcrec_build_min_dfa(cx, &cx->job->rnfa, &cx->job->rdfa, false, true,
                        PCREC_MAX_DFA_STATES_TABLE, cx->job->rnfa.start, false);
    if (cx->job->rdfa.overflowed) return 0;
    *out = cx->job->rdfa;
    return 1;
}

static char *unhex(const char *hex)
{
    size_t hn = strlen(hex) / 2;
    char *pat = malloc(hn + 1);
    for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v; }
    pat[hn] = 0;
    return pat;
}

static void dump(int k, const Dfa *d)
{
    printf("M %d %d %d %d %d %d\nCLS", k, d->n, d->ncls, d->natoms, (int)d->clsctx, d->s0);
    for (int b = 0; b < 256; b++) printf(" %d", d->clsmap[b]);
    printf("\nACC");
    for (int i = 0; i < d->n; i++) printf(" %d", (int)d->st[i].up[0].accept);
    printf("\nTR");
    for (int i = 0; i < d->n; i++) for (int c = 0; c < d->ncls; c++) printf(" %d", d->st[i].tr[c]);
    printf("\nEOL");
    for (int i = 0; i < d->n; i++) printf(" %d", d->st[i].eolvar);
    printf("\nEND");
    for (int i = 0; i < d->n; i++) printf(" %d", d->st[i].endvar);
    printf("\n");
}

int main(void)
{
    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) { fprintf(stderr, "features: %s\n", err); return 2; }
    char *line = NULL; size_t capn = 0; ssize_t got;
    while ((got = getline(&line, &capn, stdin)) > 0) {
        if (line[got - 1] == '\n') line[--got] = 0;
        char *f[4]; int nf = 0;
        for (char *p = line; nf < 4; ) { f[nf++] = p; char *t = strchr(p, '\t'); if (!t) break; *t = 0; p = t + 1; }
        if (nf < 4) continue;
        int enc = strcmp(f[1], "utf8") == 0 ? PCREC_ENC_UTF8 : PCREC_ENC_BYTE;
        Dfa m[2];
        int ok = 1;
        for (int i = 0; i < 2 && ok; i++) { char *p = unhex(f[2 + i]); ok = build(p, enc, &m[i]); free(p); }
        printf("ROW %s %s\n", f[0], ok ? "ok" : "fail");
        if (ok) { dump(0, &m[0]); dump(1, &m[1]); }
        fflush(stdout);
    }
    return 0;
}
