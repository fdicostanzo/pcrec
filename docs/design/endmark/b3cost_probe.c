/* B3 cost probe (lane b3cost, 2026-10-12): the reverse machine at the TAGGED
 * size.  A D77 instrument, never wired into the build, COUNTS ONLY.
 *
 * Links libpcrec.a; per row it parses a pattern as compile.c does up to the
 * NFA build (parse, altcls, discharge_atomic, postresolve, lower_enc), builds
 * the REVERSE NFA and the minimized reverse DFA (pcrec_build_min_dfa, the same
 * call compile.c makes), and reports the state count d->n.
 *
 * Row: id <TAB> enc <TAB> hex(today X$) <TAB> hex(untagged X\n?\z)
 *          <TAB> hex(tag0 X\z) <TAB> hex(tag1 X\n\z)
 *
 * The TAGGED machine is the product of the tag-0 and tag-1 machines: a tagged
 * subset state is the set of (NFA state, tag) pairs, tag 0 and tag 1 threads
 * evolve independently, so the pair (S0, S1) of the two machines' subset states
 * IS it, and its accept info is the pair (acc0, acc1) (the mark distance set).
 * The product is Moore-minimized with that output.  CONTROL: the same product
 * minimized with output acc0|acc1 must equal the untagged machine.
 *
 *    gcc -O1 -Ilib -Isrc docs/design/endmark/b3cost_probe.c build/libpcrec.a \
 *        -o build/scratch/b3cost_probe
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

typedef struct {
    int ok;            /* built, one atom, no ctx */
    int n;             /* d->n: pcrec's own minimized count */
    int ncls;
    Dfa d;
} M;

static void build(const char *pat, int enc, M *m, int se)
{
    memset(m, 0, sizeof *m);
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
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
        if (root) root = pcrec_altcls(cx, root);
        if (root) root = pcrec_discharge_atomic(cx, root);
        if (root) { pcrec_callgraph_build(cx, root); pcrec_facts_seal_e1(cx, root); pcrec_select_engine(cx, root); }
        if (root) pcrec_postresolve(cx, root);
        if (root) root = pcrec_lower_enc(cx, root);
        if (root) {
            pcrec_build_nfa(cx, root, &cx->job->rnfa, true, false);
            pcrec_build_min_dfa(cx, &cx->job->rnfa, &cx->job->rdfa, false, true,
                                PCREC_MAX_DFA_STATES_TABLE, cx->job->rnfa.start, false);
            if (se) pcrec_scanedge_dfa(cx, &cx->job->rdfa, false, false);
            if (!cx->job->rdfa.overflowed) {
                m->d = cx->job->rdfa;
                m->n = m->d.n;
                m->ncls = m->d.ncls;
                m->ok = 1;
            }
        }
    }
}

static int view_of(const Dfa *d)
{
    const DState *s = &d->st[d->s0];
    return s->endvar >= 0 ? s->endvar : s->eolvar >= 0 ? s->eolvar : d->s0;
}

/* product, Moore.  mode 0 = tagged (acc0,acc1), mode 1 = OR.  Returns the
 * minimized state count, dead (-1,-1) excluded; *reach = reachable product
 * states before minimization; *trim = count after merging every state whose
 * future language is empty into the dead one. */
static int product(const M *A, const M *B, int mode, int cap, int *reach, int *trim, int *ncolumns)
{
    int pa[256], cc = 0, nrep = 0;
    int ca[256], cb[256], rep[256];
    /* joint classes */
    for (int b = 0; b < 256; b++) {
        int a = A->d.clsmap[b], c = B->d.clsmap[b], f = -1;
        for (int i = 0; i < nrep; i++) if (ca[i] == a && cb[i] == c) { f = i; break; }
        if (f < 0) { ca[nrep] = a; cb[nrep] = c; rep[nrep] = b; f = nrep++; }
        pa[b] = f;
    }
    (void)pa; (void)cc; (void)rep;
    int jat_a[256], jat_b[256], nj = 0;   /* joint context atoms: distinct (atomA, atomB) over bytes */
    for (int b = 0; b < 256; b++) {
        int x = A->d.natoms > 1 ? A->d.catom[b] : 0, y = B->d.natoms > 1 ? B->d.catom[b] : 0, f = 0;
        for (int i = 0; i < nj; i++) if (jat_a[i] == x && jat_b[i] == y) { f = 1; break; }
        if (!f) { jat_a[nj] = x; jat_b[nj] = y; nj++; }
    }
    int nsz = 1024, n = 0;
    int *sa = malloc(sizeof(int) * nsz), *sb = malloc(sizeof(int) * nsz);
    int *tr = malloc(sizeof(int) * (size_t)nsz * nrep);
    /* hash by linear probe on a small map */
    size_t hc = 1 << 16; int *h = malloc(sizeof(int) * hc);
    for (size_t i = 0; i < hc; i++) h[i] = -1;
    int overflow = 0;
#define FIND(x, y, out)                                                          \
    do {                                                                         \
        size_t k = ((size_t)((x) + 1) * 1000003u + (size_t)((y) + 1) * 7919u) & (hc - 1); \
        while (h[k] >= 0 && !(sa[h[k]] == (x) && sb[h[k]] == (y))) k = (k + 1) & (hc - 1); \
        if (h[k] < 0) {                                                          \
            if (n >= cap) { overflow = 1; (out) = 0; }                           \
            else {                                                               \
                if (n >= nsz) { nsz *= 2; sa = realloc(sa, sizeof(int) * nsz); sb = realloc(sb, sizeof(int) * nsz); \
                                tr = realloc(tr, sizeof(int) * (size_t)nsz * nrep); } \
                if ((size_t)(n + 1) * 2 > hc) { fprintf(stderr, "hash full\n"); exit(3); } \
                sa[n] = (x); sb[n] = (y); h[k] = n; (out) = n++;                 \
            }                                                                    \
        } else (out) = h[k];                                                     \
    } while (0)
    int st1, st2, st3, st4;
    {
        for (int k = -1; k < nj; k++) {
            int xa = k < 0 ? A->d.s0 : A->d.s1u[jat_a[k]], xb = k < 0 ? B->d.s0 : B->d.s1u[jat_b[k]];
            if (xa < 0 || xb < 0) continue;
            FIND(xa, xb, st1);
            const DState *pa = &A->d.st[xa], *pb = &B->d.st[xb];
            int va = pa->endvar >= 0 ? pa->endvar : pa->eolvar >= 0 ? pa->eolvar : -1;
            int vb = pb->endvar >= 0 ? pb->endvar : pb->eolvar >= 0 ? pb->eolvar : -1;
            if (va >= 0 && vb >= 0) FIND(va, vb, st2);
        }
    }
    (void)st3; (void)st4;
    for (int i = 0; i < n && !overflow; i++) {
        for (int c = 0; c < nrep; c++) {
            int x = sa[i] < 0 ? -1 : A->d.st[sa[i]].tr[ca[c]];
            int y = sb[i] < 0 ? -1 : B->d.st[sb[i]].tr[cb[c]];
            int t = -1;
            if (x >= 0 || y >= 0) { FIND(x, y, t); }
            tr[(size_t)i * nrep + c] = t;
        }
    }
    if (overflow) { free(sa); free(sb); free(tr); free(h); return -1; }
    *reach = n;
    /* outputs */
    int *part = malloc(sizeof(int) * (n + 1)), *np = malloc(sizeof(int) * (n + 1));
    {
        for (int i = 0; i < n; i++) {
            int o = 0;
            for (int a = 0; a < nj; a++) {
                int a0 = sa[i] >= 0 && A->d.st[sa[i]].up[jat_a[a]].accept;
                int a1 = sb[i] >= 0 && B->d.st[sb[i]].up[jat_b[a]].accept;
                o = o * 4 + (mode == 0 ? (a0 | a1 << 1) : (a0 | a1));
            }
            part[i] = o;
        }
    }
    part[n] = -7;   /* dead sink: its own block id below */
    int nb = 0;
    /* renumber so ids are dense; dead gets id of "no accept" with all-dead row,
     * handled by treating target -1 as index n */
    for (;;) {
        /* signature = (part[i], part[tr...]) */
        int nn = 0;
        int *key = malloc(sizeof(int) * (size_t)(n + 1) * (nrep + 1));
        int *ids = malloc(sizeof(int) * (n + 1));
        for (int i = 0; i <= n; i++) {
            int *k = key + (size_t)i * (nrep + 1);
            k[0] = part[i];
            for (int c = 0; c < nrep; c++) {
                int t = i == n ? n : tr[(size_t)i * nrep + c];
                k[c + 1] = t < 0 ? part[n] : part[t];
            }
        }
        size_t kc = 1;
        while (kc < (size_t)(n + 1) * 2) kc <<= 1;
        int *kt = malloc(sizeof(int) * kc);
        for (size_t q = 0; q < kc; q++) kt[q] = -1;
        for (int i = 0; i <= n; i++) {
            const int *ki = key + (size_t)i * (nrep + 1);
            unsigned long long hv = 1469598103934665603ull;
            for (int c = 0; c <= nrep; c++) hv = (hv ^ (unsigned)ki[c]) * 1099511628211ull;
            size_t q = (size_t)(hv >> 7) & (kc - 1);
            int f = -1;
            while (kt[q] >= 0) {
                int j = kt[q];
                if (!memcmp(key + (size_t)ids[j] * (nrep + 1), ki, sizeof(int) * (nrep + 1))) { f = j; break; }
                q = (q + 1) & (kc - 1);
            }
            if (f < 0) { ids[nn] = i; kt[q] = nn; f = nn++; }
            np[i] = f;
        }
        free(kt);
        free(key); free(ids);
        int same = (nn == nb);
        memcpy(part, np, sizeof(int) * (n + 1));
        if (same && nn == nb) { nb = nn; break; }
        nb = nn;
    }
    /* count blocks among real states (exclude the dead sink's block if no real state shares it) */
    int *seen = calloc(nb + 1, sizeof(int));
    int cnt = 0, shared = 0;
    for (int i = 0; i < n; i++) if (!seen[part[i]]) { seen[part[i]] = 1; cnt++; }
    for (int i = 0; i < n; i++) if (part[i] == part[n]) shared++;
    *trim = cnt - (seen[part[n]] ? 1 : 0);   /* the dead block merged out */
    (void)shared;
    /* byte classes of the minimized machine: distinct columns over the blocks */
    if (ncolumns) {
        int nd = 0;
        int *col = malloc(sizeof(int) * (size_t)(n + 1) * nrep);
        for (int c = 0; c < nrep; c++)
            for (int i = 0; i < n; i++) {
                int t = tr[(size_t)i * nrep + c];
                col[(size_t)c * (n + 1) + i] = t < 0 ? part[n] : part[t];
            }
        for (int c = 0; c < nrep; c++) {
            int dup = 0;
            for (int e = 0; e < c && !dup; e++)
                if (!memcmp(col + (size_t)c * (n + 1), col + (size_t)e * (n + 1), sizeof(int) * n)) dup = 1;
            if (!dup) nd++;
        }
        *ncolumns = nd;
        free(col);
    }
    free(sa); free(sb); free(tr); free(h); free(part); free(np); free(seen);
    return cnt;
}

static char *unhex(const char *hex)
{
    size_t hn = strlen(hex) / 2;
    char *pat = malloc(hn + 1);
    for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v; }
    pat[hn] = 0;
    return pat;
}

int main(void)
{
    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) { fprintf(stderr, "features: %s\n", err); return 2; }
    printf("id\tstatus\ttoday\tuntagged\tt0\tt1\tcls_today\tcls_untag\ttag_reach\ttag_min\ttag_trim\tor_reach\tor_min\tor_trim\tncls_tag\ttoday_post\tuntag_post\n");
    char *line = NULL; size_t capn = 0; ssize_t got;
    while ((got = getline(&line, &capn, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        char *f[6]; int nf = 0;
        for (char *p = line; nf < 6; ) { f[nf++] = p; char *t = strchr(p, '\t'); if (!t) break; *t = 0; p = t + 1; }
        if (nf < 6) continue;
        int enc = strcmp(f[1], "utf8") == 0 ? PCREC_ENC_UTF8 : PCREC_ENC_BYTE;
        M m[4];
        for (int i = 0; i < 4; i++) { char *p = unhex(f[2 + i]); build(p, enc, &m[i], 0); free(p); }
        M post[2];
        for (int i = 0; i < 2; i++) { char *p = unhex(f[2 + i]); build(p, enc, &post[i], 1); free(p); }
        int allok = 1, st = 0;
        for (int i = 0; i < 4; i++) { if (m[i].n == 0) allok = 0; if (m[i].ok < 0) st = 1; }
        if (!allok) { printf("%s\tbuild-failed\t%d\t%d\t%d\t%d\n", f[0], m[0].n, m[1].n, m[2].n, m[3].n); fflush(stdout); continue; }
        if (0) {
            printf("%s\tunmodelled(ctx)\t%d\t%d\t%d\t%d\n", f[0], m[0].n, m[1].n, m[2].n, m[3].n); fflush(stdout); continue;
        }
        int r1, t1, r2, t2, nct = 0;
        int tag = product(&m[2], &m[3], 0, 30000, &r1, &t1, &nct);
        int orr = product(&m[2], &m[3], 1, 30000, &r2, &t2, NULL);
        printf("%s\tok\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n", f[0], m[0].n, m[1].n, m[2].n, m[3].n,
               m[0].ncls, m[1].ncls, tag < 0 ? -1 : r1, tag, tag < 0 ? -1 : t1, orr < 0 ? -1 : r2, orr, orr < 0 ? -1 : t2, nct, post[0].n, post[1].n);
        fflush(stdout);
    }
    return 0;
}
