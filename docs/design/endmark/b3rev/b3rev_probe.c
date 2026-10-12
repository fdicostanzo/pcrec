/* b3rev probe (lane b3rev, 2026-10-12): every machine a B3 artifact would
 * carry, at its real size, before AND after the scan-edge pass.  A D77
 * instrument, never wired into the build; COUNTS ONLY.
 *
 * Links libpcrec.a and a probe-local copy of src/opt/scanedge.c whose two
 * accept readers (`acc_of`, `end_acc_of`) compare VALUES instead of truth
 * (b3rev's S3 fix: the distance set IS the accept value), renamed so both
 * passes link side by side:
 *
 *   sed -e 's/accept != 0; }/accept; }/' \
 *       -e 's/pcrec_scanedge_dfa(/b3rev_scanedge_fixed(/' \
 *       -e 's/pcrec_state_view_invariant(/b3rev_state_view_invariant(/g' \
 *       src/opt/scanedge.c > build/scratch/b3rev/scanedge_fixed.c
 *   gcc -O1 -Ilib -Isrc -c build/scratch/b3rev/scanedge_fixed.c -o build/scratch/b3rev/sef.o
 *   gcc -O1 -Ilib -Isrc docs/design/endmark/b3rev/b3rev_probe.c build/scratch/b3rev/sef.o \
 *       build/libpcrec.a -o build/scratch/b3rev/b3rev_probe
 *
 * Row (stdin): id enc hex(today X$) hex(untagged X\n?\z) hex(t0 X\z) hex(t1 X\n\z) hex(G X\G)
 *   where G replaces every path-final `$`/`\Z` by `\G`, a node kind no rev-end
 *   pattern carries (end_pin declines `\G`); the probe patches each N_GSTART
 *   of the FORWARD NFA into the lowered tail with its own accepts:
 *       SPLIT(t1 = CLASS{\n} -> END -> ACC1,  t2 = END -> ACC0)
 *   (greedy `\n?`; a path-final `$`'s continuation is epsilon-only to the
 *   accept, so ending the tail in a fresh accept is the same language and
 *   priority).  A thread that reaches ACC1 crossed the mark one byte before
 *   the end (d = 1); ACC0 and every other accept (an unmarked `\z` arm, S5)
 *   is d = 0.
 *
 * REVERSE (b3cost's model, extended): today X$ and untagged X\n?\z are
 * pcrec's own machines (minimized, then scan-edge); TAGGED is the Moore-
 * minimized product of tag0 X\z and tag1 X\n\z with the per-(state, context
 * atom) distance set as output, the ABSENT atom (subject start, the startpos
 * boundary) included.  TIE-CAPABLE = some reachable (state, atom) carries
 * both distances.  The product is then rebuilt as a pcrec `Dfa` with the set
 * as each atom's accept VALUE and run through both scan-edge passes.
 * CONTROLS: product with OR output == pcrec's untagged count; the OR-valued
 * rebuild through the shipped pass == pcrec's untagged post-scan-edge count.
 *
 * FORWARD and ANCHORED (D164 add. 4): today's (X$) and the lowered untagged
 * (patched G) machines are pcrec's own; the TAGGED machine is the Moore-
 * minimization of pcrec's UNMINIMIZED lowered machine with each END view's
 * winning distance `b` as an extra output, `b` computed by a priority
 * epsilon-closure over pcrec's own NFA from each state's pre-set (the
 * closure D3's accept-pruning runs).  CONTROLS: the closure's accept bit ==
 * pcrec's END-view accept on every state; the Moore count with `b` ignored
 * == pcrec_minimize_dfa's count; pre-sets reaching one state agree on `b`.
 *
 * MARK_PRIO (endmark.md §2.3, S7): the UNPRUNED anchored machine of the
 * patched NFA (pcrec_build_dfa, prune off, root anch_start), and at each
 * state's END the accepting distances in priority order: const c / none /
 * state-dependent; its state count is the fact's cost.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

void b3rev_scanedge_fixed(Ctx *cx, Dfa *d, bool prefilter_reseeds, bool end_is_exit);

#define CAP PCREC_MAX_DFA_STATES_TABLE

/* ------------------------------------------------------------ the pipeline */

typedef struct {
    Ctx *cx;
    Ast *root;
} Front;

static int front(const char *pat, int enc, Front *f)
{
    memset(f, 0, sizeof *f);
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
    cx->err = calloc(1, sizeof *cx->err);
    f->cx = cx;
    if (setjmp(cx->jb) != 0) { if (getenv("B3REV_DEBUG")) fprintf(stderr, "front: %s\n", cx->err->msg); return 0; }
    pcrec_parse_mods_init(cx);
    Ast *root = pcrec_parse_info(cx, NULL);
    if (root) root = pcrec_altcls(cx, root);
    if (root) root = pcrec_discharge_atomic(cx, root);
    if (root) { pcrec_callgraph_build(cx, root); pcrec_facts_seal_e1(cx, root); pcrec_select_engine(cx, root); }
    if (root) pcrec_postresolve(cx, root);
    if (root) root = pcrec_lower_enc(cx, root);
    if (root) pcrec_facts_seal_e2(cx, root);
    f->root = root;
    return root != NULL;
}

/* -------------------------------------------------- generic Moore minimizer */

/* n states, nsym symbols, tr[i*nsym+c] (-1 dead), out[i]; the dead sink is
 * state n with its own output.  Returns the block count among real states
 * with the dead block merged out; part[0..n] receives the blocks. */
static int moore(int n, int nsym, const int *tr, const long long *out, int *part)
{
    long long *o = malloc(sizeof(long long) * (n + 1));
    memcpy(o, out, sizeof(long long) * n);
    o[n] = -7;
    /* initial partition by output */
    {
        long long *seen = malloc(sizeof(long long) * (n + 1));
        int ns = 0;
        for (int i = 0; i <= n; i++) {
            int k = 0;
            while (k < ns && seen[k] != o[i]) k++;
            if (k == ns) seen[ns++] = o[i];
            part[i] = k;
        }
        free(seen);
    }
    int nb = -1;
    int *np = malloc(sizeof(int) * (n + 1));
    int kl = nsym + 1;
    int *key = malloc(sizeof(int) * (size_t)(n + 1) * kl);
    int *ids = malloc(sizeof(int) * (n + 1));
    size_t kc = 1;
    while (kc < (size_t)(n + 1) * 2) kc <<= 1;
    int *kt = malloc(sizeof(int) * kc);
    for (;;) {
        for (int i = 0; i <= n; i++) {
            int *k = key + (size_t)i * kl;
            k[0] = part[i];
            for (int c = 0; c < nsym; c++) {
                int t = i == n ? n : tr[(size_t)i * nsym + c];
                k[c + 1] = t < 0 ? part[n] : part[t];
            }
        }
        for (size_t q = 0; q < kc; q++) kt[q] = -1;
        int nn = 0;
        for (int i = 0; i <= n; i++) {
            const int *ki = key + (size_t)i * kl;
            unsigned long long hv = 1469598103934665603ull;
            for (int c = 0; c < kl; c++) hv = (hv ^ (unsigned)ki[c]) * 1099511628211ull;
            size_t q = (size_t)(hv >> 7) & (kc - 1);
            int f = -1;
            while (kt[q] >= 0) {
                int j = kt[q];
                if (!memcmp(key + (size_t)ids[j] * kl, ki, sizeof(int) * kl)) { f = j; break; }
                q = (q + 1) & (kc - 1);
            }
            if (f < 0) { ids[nn] = i; kt[q] = nn; f = nn++; }
            np[i] = f;
        }
        memcpy(part, np, sizeof(int) * (n + 1));
        if (nn == nb) break;
        nb = nn;
    }
    free(kt); free(key); free(ids); free(np); free(o);
    int *seen = calloc(nb + 1, sizeof(int));
    int cnt = 0;
    for (int i = 0; i < n; i++) if (!seen[part[i]]) { seen[part[i]] = 1; cnt++; }
    int r = cnt - (seen[part[n]] ? 1 : 0);
    free(seen);
    return r;
}

/* Rebuild a minimized machine as a pcrec `Dfa` (for the scan-edge pass):
 * blocks of `part` over n states; tr in old ids (nsym = ncls + 2: the eol
 * and end view columns, already resolved); accv[i*natoms + a] the accept
 * value; starts in old ids.  The dead block (part[n]) becomes -1. */
static Dfa rebuild(int n, int ncls, const int *tr, const int *accv, int natoms,
                   const int *part, int s0, const int *s1, int ns1, const uint8_t *clsmap)
{
    Dfa d;
    memset(&d, 0, sizeof d);
    int nb = 0;
    for (int i = 0; i <= n; i++) if (part[i] + 1 > nb) nb = part[i] + 1;
    int *seq = malloc(sizeof(int) * nb), *rep = malloc(sizeof(int) * nb);
    for (int b = 0; b < nb; b++) { seq[b] = -1; rep[b] = -1; }
    int dead = part[n], m = 0;
    for (int i = 0; i < n; i++) {
        int b = part[i];
        if (b == dead || seq[b] >= 0) continue;
        seq[b] = m++; rep[b] = i;
    }
    seq[dead] = -1;
    d.n = d.cap = m;
    d.st = calloc(m ? m : 1, sizeof(DState));
    d.ncls = ncls;
    memcpy(d.clsmap, clsmap, 256);
    d.natoms = natoms;
    int nsym = ncls + 2;
    for (int b = 0; b < nb; b++) {
        if (seq[b] < 0) continue;
        int i = rep[b];
        DState *s = &d.st[seq[b]];
        s->tr = malloc(sizeof(int) * ncls);
        for (int c = 0; c < ncls; c++) {
            int t = tr[(size_t)i * nsym + c];
            s->tr[c] = t < 0 ? -1 : seq[part[t]];
        }
        int v = tr[(size_t)i * nsym + ncls], e = tr[(size_t)i * nsym + ncls + 1];
        int pv = v < 0 ? part[i] : part[v], pe = e < 0 ? pv : part[e];
        s->eolvar = pv == part[i] ? -1 : seq[pv];
        s->endvar = pe == pv ? -1 : seq[pe];
        s->up = calloc(natoms, sizeof(DView));
        for (int a = 0; a < natoms; a++) s->up[a].accept = (uint8_t)accv[(size_t)i * natoms + a];
        s->scan_next = -1;
    }
    d.s0 = s0 < 0 ? -1 : seq[part[s0]];
    for (int a = 0; a < PCREC_MAX_CTX_ATOMS; a++) {
        int x = a < ns1 ? s1[a] : (ns1 ? s1[0] : s0);
        d.s1u[a] = d.s1g[a] = x < 0 ? -1 : seq[part[x]];
    }
    free(seq); free(rep);
    return d;
}

static int scanedge_count(Dfa d, int fixed, bool end_is_exit)
{
    Ctx *cx = calloc(1, sizeof *cx);
    pcrec_options *o = calloc(1, sizeof *o);
    pcrec_default_options(o);
    cx->opt = o;
    cx->arena.cx = cx;
    /* the pass reallocs nothing it does not own; copy the state array */
    DState *st = malloc(sizeof(DState) * (d.n ? d.n : 1));
    memcpy(st, d.st, sizeof(DState) * d.n);
    for (int i = 0; i < d.n; i++) {
        st[i].tr = malloc(sizeof(int) * d.ncls);
        memcpy(st[i].tr, d.st[i].tr, sizeof(int) * d.ncls);
    }
    d.st = st;
    if (setjmp(cx->jb) != 0) return -2;
    if (fixed) b3rev_scanedge_fixed(cx, &d, false, end_is_exit);
    else pcrec_scanedge_dfa(cx, &d, false, end_is_exit);
    return d.n;
}

/* ------------------------------------------------------------- reverse side */

typedef struct {
    int ok, n, post, ncls;
    Dfa d;
} M;

static void build_rev(const char *pat, int enc, M *m)
{
    memset(m, 0, sizeof *m);
    Front f;
    if (!front(pat, enc, &f)) return;
    Ctx *cx = f.cx;
    if (setjmp(cx->jb) != 0) return;
    pcrec_build_nfa(cx, f.root, &cx->job->rnfa, true, false);
    pcrec_build_min_dfa(cx, &cx->job->rnfa, &cx->job->rdfa, false, true, CAP, cx->job->rnfa.start, false);
    if (cx->job->rdfa.overflowed) return;
    m->d = cx->job->rdfa;
    m->n = m->d.n;
    m->ncls = m->d.ncls;
    m->ok = 1;
    m->post = scanedge_count(m->d, 0, false);
}

/* today's `revend_nl_last` (src/gen/emit_dfa.c), verbatim in effect */
static int nl_last(const Dfa *d)
{
    int stack[8], n = 0, seen[8], ns = 0;
    int cls = d->clsmap['\n'];
    if (d->s0 < 0 || d->s0 >= d->n) return 0;
    stack[n++] = d->s0;
    while (n > 0) {
        int st = stack[--n], dup = 0;
        for (int k = 0; k < ns; k++) dup |= seen[k] == st;
        if (dup || ns == 8) continue;
        seen[ns++] = st;
        if (d->st[st].tr[cls] >= 0) return 1;
        if (d->st[st].eolvar >= 0 && n < 8) stack[n++] = d->st[st].eolvar;
        if (d->st[st].endvar >= 0 && n < 8) stack[n++] = d->st[st].endvar;
    }
    return ns == 8;
}

typedef struct {
    int reach, tag_min, or_min, ncols;
    int tie_pairs;     /* reachable (state, atom) with both distances */
    int tie_states;    /* reachable states with a tie under SOME atom */
    int tie_classdep;  /* ... but not under every atom (S2's shape) */
    int tie_absent;    /* ... a tie under the ABSENT atom (start boundary) */
    int post_fixed, post_unfixed, post_or;
} Prod;

/* The tagged reverse product (b3cost's construction): joint byte classes,
 * joint context atoms (+ the absent atom), start pairs and their views. */
static int product(const M *A, const M *B, Prod *P)
{
    memset(P, 0, sizeof *P);
    int ca[256], cb[256], nrep = 0;
    uint8_t jcls[256];
    for (int b = 0; b < 256; b++) {
        int a = A->d.clsmap[b], c = B->d.clsmap[b], f = -1;
        for (int i = 0; i < nrep; i++) if (ca[i] == a && cb[i] == c) { f = i; break; }
        if (f < 0) { ca[nrep] = a; cb[nrep] = c; f = nrep++; }
        jcls[b] = (uint8_t)f;
    }
    int ja[PCREC_MAX_CTX_ATOMS * PCREC_MAX_CTX_ATOMS + 1], jb[PCREC_MAX_CTX_ATOMS * PCREC_MAX_CTX_ATOMS + 1], nj = 0;
    /* atom 0 of each side is the absent side's context (internal.h): listed first */
    ja[nj] = 0; jb[nj] = 0; nj++;
    for (int b = 0; b < 256; b++) {
        int x = A->d.natoms > 1 ? A->d.catom[b] : 0, y = B->d.natoms > 1 ? B->d.catom[b] : 0, f = 0;
        for (int i = 0; i < nj; i++) if (ja[i] == x && jb[i] == y) { f = 1; break; }
        if (!f) { ja[nj] = x; jb[nj] = y; nj++; }
    }
    int nsym = nrep + 2;
    int nsz = 1024, n = 0;
    int *sa = malloc(sizeof(int) * nsz), *sb = malloc(sizeof(int) * nsz);
    int *tr = malloc(sizeof(int) * (size_t)nsz * nsym);
    size_t hc = 1 << 17;
    int *h = malloc(sizeof(int) * hc);
    for (size_t i = 0; i < hc; i++) h[i] = -1;
    int overflow = 0;
#define FIND(x, y, out)                                                                  \
    do {                                                                                 \
        size_t k = ((size_t)((x) + 1) * 1000003u + (size_t)((y) + 1) * 7919u) & (hc - 1); \
        while (h[k] >= 0 && !(sa[h[k]] == (x) && sb[h[k]] == (y))) k = (k + 1) & (hc - 1); \
        if (h[k] < 0) {                                                                  \
            if (n >= CAP) { overflow = 1; (out) = 0; }                                   \
            else {                                                                       \
                if (n >= nsz) { nsz *= 2; sa = realloc(sa, sizeof(int) * nsz);           \
                                sb = realloc(sb, sizeof(int) * nsz);                     \
                                tr = realloc(tr, sizeof(int) * (size_t)nsz * nsym); }    \
                if ((size_t)(n + 1) * 2 > hc) { fprintf(stderr, "hash full\n"); exit(3); } \
                sa[n] = (x); sb[n] = (y); h[k] = n;                                      \
                for (int q_ = 0; q_ < nsym; q_++) tr[(size_t)n * nsym + q_] = -1;        \
                (out) = n++;                                                             \
            }                                                                            \
        } else (out) = h[k];                                                             \
    } while (0)
    int s0p = -1, s1p[PCREC_MAX_CTX_ATOMS * PCREC_MAX_CTX_ATOMS + 1], ns1 = 0;
    for (int k = -1; k < nj; k++) {
        int xa = k < 0 ? A->d.s0 : A->d.s1u[ja[k]], xb = k < 0 ? B->d.s0 : B->d.s1u[jb[k]];
        if (xa < 0 || xb < 0) continue;
        int st, vs;
        FIND(xa, xb, st);
        if (overflow) break;
        if (k < 0) s0p = st; else s1p[ns1++] = st;
        const DState *pa = &A->d.st[xa], *pb = &B->d.st[xb];
        int va = pa->endvar >= 0 ? pa->endvar : pa->eolvar;
        int vb = pb->endvar >= 0 ? pb->endvar : pb->eolvar;
        if (va >= 0 || vb >= 0) {
            FIND(va >= 0 ? va : xa, vb >= 0 ? vb : xb, vs);
            if (overflow) break;
            tr[(size_t)st * nsym + nrep + 1] = vs;     /* the seed's view */
        }
    }
    for (int i = 0; i < n && !overflow; i++) {
        for (int c = 0; c < nrep; c++) {
            int x = sa[i] < 0 ? -1 : A->d.st[sa[i]].tr[ca[c]];
            int y = sb[i] < 0 ? -1 : B->d.st[sb[i]].tr[cb[c]];
            int t = -1;
            if (x >= 0 || y >= 0) { FIND(x, y, t); }
            tr[(size_t)i * nsym + c] = t;
        }
    }
    if (overflow) { free(sa); free(sb); free(tr); free(h); return -1; }
    P->reach = n;
    long long *out = malloc(sizeof(long long) * n);
    int *accv = malloc(sizeof(int) * (size_t)n * nj), *acco = malloc(sizeof(int) * (size_t)n * nj);
    for (int i = 0; i < n; i++) {
        long long o = 0, oo = 0;
        int any = 0, all = 1;
        for (int a = 0; a < nj; a++) {
            int a0 = sa[i] >= 0 && A->d.st[sa[i]].up[ja[a] < A->d.natoms ? ja[a] : 0].accept;
            int a1 = sb[i] >= 0 && B->d.st[sb[i]].up[jb[a] < B->d.natoms ? jb[a] : 0].accept;
            int v = a0 | a1 << 1;
            accv[(size_t)i * nj + a] = v;
            acco[(size_t)i * nj + a] = a0 | a1;
            o = o * 4 + v;
            oo = oo * 2 + (a0 | a1);
            if (v == 3) { P->tie_pairs++; any = 1; if (a == 0) P->tie_absent++; } else all = 0;
        }
        if (any) { P->tie_states++; if (!all) P->tie_classdep++; }
        out[i] = o;
        (void)oo;
    }
    int *part = malloc(sizeof(int) * (n + 1));
    P->tag_min = moore(n, nsym, tr, out, part);
    P->ncols = 0;
    {
        int nd = 0;
        int *col = malloc(sizeof(int) * (size_t)(n + 1) * nrep);
        for (int c = 0; c < nrep; c++)
            for (int i = 0; i < n; i++) {
                int t = tr[(size_t)i * nsym + c];
                col[(size_t)c * (n + 1) + i] = t < 0 ? part[n] : part[t];
            }
        for (int c = 0; c < nrep; c++) {
            int dup = 0;
            for (int e = 0; e < c && !dup; e++)
                if (!memcmp(col + (size_t)c * (n + 1), col + (size_t)e * (n + 1), sizeof(int) * n)) dup = 1;
            if (!dup) nd++;
        }
        P->ncols = nd;
        free(col);
    }
    Dfa t = rebuild(n, nrep, tr, accv, nj, part, s0p, s1p, ns1, jcls);
    P->post_fixed = scanedge_count(t, 1, false);
    P->post_unfixed = scanedge_count(t, 0, false);
    for (int i = 0; i < n; i++) {
        long long oo = 0;
        for (int a = 0; a < nj; a++) oo = oo * 2 + acco[(size_t)i * nj + a];
        out[i] = oo;
    }
    int *part2 = malloc(sizeof(int) * (n + 1));
    P->or_min = moore(n, nsym, tr, out, part2);
    Dfa u = rebuild(n, nrep, tr, acco, nj, part2, s0p, s1p, ns1, jcls);
    P->post_or = scanedge_count(u, 0, false);
    free(sa); free(sb); free(tr); free(h); free(out); free(accv); free(acco); free(part); free(part2);
    return 0;
}

/* ------------------------------------------------------- forward / anchored */

typedef struct {
    int ok, unmodelled;
    int min, post;            /* pcrec's own: minimized, after scan edge */
} PM;

/* today's forward + anchored (X$), pcrec's own */
static void build_fwd_today(const char *pat, int enc, PM *f, PM *a)
{
    memset(f, 0, sizeof *f); memset(a, 0, sizeof *a);
    Front fr;
    if (!front(pat, enc, &fr)) return;
    Ctx *cx = fr.cx;
    if (setjmp(cx->jb) != 0) { if (getenv("B3REV_DEBUG")) fprintf(stderr, "fwd: %s\n", cx->err->msg); return; }
    pcrec_build_nfa(cx, fr.root, &cx->job->nfa, false, false);
    if (pcrec_nfa_has_bot(&cx->job->nfa)) { if (getenv("B3REV_DEBUG")) fprintf(stderr, "fwd: bot\n"); return; }
    pcrec_nfa_wrap_unanchored(cx, &cx->job->nfa);
    pcrec_facts_seal_e3(cx);
    pcrec_build_min_dfa(cx, &cx->job->nfa, &cx->job->dfa, true, false, CAP, cx->job->nfa.start, false);
    f->min = cx->job->dfa.n; f->ok = 1;
    f->post = scanedge_count(cx->job->dfa, 0, true);
    pcrec_build_min_dfa(cx, &cx->job->nfa, &cx->job->adfa, true, false, CAP, cx->job->nfa.anch_start, true);
    if (!cx->job->adfa.overflowed) {
        a->min = cx->job->adfa.n; a->ok = 1;
        a->post = scanedge_count(cx->job->adfa, 0, true);
    }
}

typedef struct {
    int ok, unmodelled;
    int umin, upost;          /* pcrec's own lowered untagged machine */
    int unmin;                /* pcrec_build_dfa states before minimization */
    int model_untag;          /* CONTROL: == umin */
    int acc_mismatch;         /* CONTROL: closure accept != pcrec END accept */
    int b_conflict;           /* pre-sets reaching one END state disagree on b */
    int tag_min;              /* Moore with b */
    int tag_post_fixed, tag_post_unfixed, untag_post_model;
    int b1_states;            /* END states whose winner is d = 1 */
} TM;

static Nfa *g_nfa;
static uint8_t *g_acc1;
static int g_unmod;
static int *g_seen, g_stamp;

/* priority closure at the subject END from one node: -1 no accept, else the
 * distance of the first accept (D3: stop at the first).  `all` collects
 * every accept's distance in order instead (the unpruned walk, mark_prio). */
static int endclo(int x, int *dl, int *nd)
{
    while (x >= 0) {
        if (g_seen[x] == g_stamp) return -1;
        g_seen[x] = g_stamp;
        const NState *s = &g_nfa->st[x];
        switch (s->k) {
        case N_ACCEPT: {
            int d = g_acc1[x] ? 1 : 0;
            if (dl) { dl[(*nd)++] = d; return -1; }
            return d;
        }
        case N_CLASS: return -1;
        case N_SPLIT: { int r = endclo(s->t1, dl, nd); if (r >= 0) return r; x = s->t2; break; }
        case N_EPS: case N_END: case N_EOL: case N_EOL_M: case N_CSTART: x = s->t1; break;
        default: g_unmod = 1; return -1;   /* BOT, BOT_M, CTX, GSTART: not modelled */
        }
    }
    return -1;
}

static int endclo_set(const int *pre, int np, int *dl, int *nd)
{
    g_stamp++;
    if (nd) *nd = 0;
    for (int i = 0; i < np; i++) {
        int r = endclo(pre[i], dl, nd);
        if (r >= 0) return r;
    }
    return -1;
}

/* the patched NFA: every N_GSTART becomes the lowered tail */
static void patch(Nfa *nfa)
{
    int g = 0;
    for (int i = 0; i < nfa->n; i++) if (nfa->st[i].k == N_GSTART) g++;
    int nn = nfa->n + 5 * g;
    NState *st = calloc(nn, sizeof(NState));
    memcpy(st, nfa->st, sizeof(NState) * nfa->n);
    g_acc1 = calloc(nn, 1);
    int at = nfa->n;
    for (int i = 0; i < nfa->n; i++) {
        if (st[i].k != N_GSTART) continue;
        int c = at++, e1 = at++, a1 = at++, e0 = at++, a0 = at++;
        st[i].k = N_SPLIT; st[i].t1 = c; st[i].t2 = e0; st[i].loop = 0; st[i].exit_is_t2 = 0;
        st[c].k = N_CLASS; memset(st[c].cls, 0, 32); st[c].cls['\n' >> 3] |= 1 << ('\n' & 7); st[c].t1 = e1; st[c].t2 = -1;
        st[e1].k = N_END; st[e1].t1 = a1; st[e1].t2 = -1;
        st[a1].k = N_ACCEPT; st[a1].t1 = st[a1].t2 = -1; g_acc1[a1] = 1;
        st[e0].k = N_END; st[e0].t1 = a0; st[e0].t2 = -1;
        st[a0].k = N_ACCEPT; st[a0].t1 = st[a0].t2 = -1;
    }
    nfa->st = st;
    nfa->n = nn;
    nfa->cap = nn;
}

static int resolve_end(const Dfa *d, int i)
{
    int v = d->st[i].eolvar < 0 ? i : d->st[i].eolvar;
    return d->st[i].endvar < 0 ? v : d->st[i].endvar;
}

/* the tagged model over an UNMINIMIZED pruned machine `d` rooted at `root` */
static void tagged_model(const Dfa *d, int root, TM *t)
{
    int n = d->n;
    int **pre = calloc(n, sizeof(int *));
    int *npre = calloc(n, sizeof(int));
    int *bq = malloc(sizeof(int) * (n + 1)), qh = 0, qt = 0;
    int *endb = malloc(sizeof(int) * n);       /* b of state i's END view, -2 unknown */
    for (int i = 0; i < n; i++) endb[i] = -2;
    int nat = d->natoms;
    if (nat > 1 || d->clsctx) { t->unmodelled = 1; }
    int starts[1 + PCREC_MAX_CTX_ATOMS], nst = 0;
    starts[nst++] = d->s0;
    for (int a = 0; a < nat; a++) starts[nst++] = d->s1u[a];
    for (int k = 0; k < nst; k++) {
        int s = starts[k];
        if (s < 0 || pre[s]) continue;
        pre[s] = malloc(sizeof(int)); pre[s][0] = root; npre[s] = 1;
        bq[qt++] = s;
    }
    int *buf = malloc(sizeof(int) * (g_nfa->n + 1));
    while (qh < qt) {
        int i = bq[qh++];
        /* the END output from this pre-set */
        int e = resolve_end(d, i);
        int r = endclo_set(pre[i], npre[i], NULL, NULL);
        int acc = d->st[e].up[0].accept != 0;
        if ((r >= 0) != acc) t->acc_mismatch++;
        if (r >= 0) {
            if (endb[e] == -2) endb[e] = r;
            else if (endb[e] != r) t->b_conflict++;
        }
        const DView *v = &d->st[i].up[0];
        for (int c = 0; c < d->ncls; c++) {
            int to = d->st[i].tr[c];
            if (to < 0) continue;
            int rb = d->rep[c], m = 0;
            for (int k = 0; k < v->nlist; k++) {
                const NState *s = &g_nfa->st[v->list[k]];
                if (s->k == N_CLASS && (s->cls[rb >> 3] >> (rb & 7) & 1)) buf[m++] = s->t1;
            }
            if (!pre[to]) {
                pre[to] = malloc(sizeof(int) * (m ? m : 1));
                memcpy(pre[to], buf, sizeof(int) * m);
                npre[to] = m;
                bq[qt++] = to;
            } else {
                int e2 = resolve_end(d, to);
                int r2 = endclo_set(buf, m, NULL, NULL);
                if (r2 >= 0) {
                    if (endb[e2] == -2) endb[e2] = r2;
                    else if (endb[e2] != r2) t->b_conflict++;
                }
            }
        }
    }
    free(buf);
    /* Moore: symbols = classes + eol + end (resolved like the minimizer) */
    int nsym = d->ncls + 2;
    int *tr = malloc(sizeof(int) * (size_t)n * nsym);
    long long *out = malloc(sizeof(long long) * n);
    int *accv = malloc(sizeof(int) * n), *acc1v = malloc(sizeof(int) * n);
    for (int i = 0; i < n; i++) {
        for (int c = 0; c < d->ncls; c++) tr[(size_t)i * nsym + c] = d->st[i].tr[c];
        int v = d->st[i].eolvar < 0 ? i : d->st[i].eolvar;
        int e = d->st[i].endvar < 0 ? v : d->st[i].endvar;
        tr[(size_t)i * nsym + d->ncls] = v == i ? -1 : v;
        tr[(size_t)i * nsym + d->ncls + 1] = e == v ? -1 : e;
        long long a = 0;
        for (int u = 0; u < nat; u++) a = a * 2 + (d->st[i].up[u].accept != 0);
        accv[i] = d->st[i].up[0].accept != 0;
        int b = endb[i] >= 0 ? endb[i] : 0;
        acc1v[i] = accv[i] ? (1 << b) : 0;
        if (accv[i] && b == 1) t->b1_states++;
        out[i] = a;
    }
    int *part = malloc(sizeof(int) * (n + 1));
    /* the dead-column convention: a resolved view equal to self is -1 above,
     * which moore() maps to the dead block; use explicit self instead */
    for (int i = 0; i < n; i++) {
        if (tr[(size_t)i * nsym + d->ncls] < 0) tr[(size_t)i * nsym + d->ncls] = i;
        int v = tr[(size_t)i * nsym + d->ncls];
        if (tr[(size_t)i * nsym + d->ncls + 1] < 0) tr[(size_t)i * nsym + d->ncls + 1] = v;
    }
    t->model_untag = moore(n, nsym, tr, out, part);
    int s1[PCREC_MAX_CTX_ATOMS];
    for (int a = 0; a < nat; a++) s1[a] = d->s1u[a];
    Dfa um = rebuild(n, d->ncls, tr, accv, 1, part, d->s0, s1, nat, d->clsmap);
    t->untag_post_model = scanedge_count(um, 0, true);
    for (int i = 0; i < n; i++) out[i] = out[i] * 4 + (accv[i] ? (endb[i] >= 0 ? endb[i] : 0) + 1 : 0);
    t->tag_min = moore(n, nsym, tr, out, part);
    Dfa tm = rebuild(n, d->ncls, tr, acc1v, 1, part, d->s0, s1, nat, d->clsmap);
    t->tag_post_fixed = scanedge_count(tm, 1, true);
    t->tag_post_unfixed = scanedge_count(tm, 0, true);
    for (int i = 0; i < n; i++) free(pre[i]);
    free(pre); free(npre); free(bq); free(endb); free(tr); free(out); free(accv); free(acc1v); free(part);
}

typedef struct {
    int ok, states, cls;      /* cls: 0 none, 1 const0, 2 const1, 3 state-dependent */
    int multi;                /* END states with >= 2 distinct distances */
} MP;

static void mp_eval(const int *pre, int np, int *dl, MP *mp, int *firsts)
{
    int nd;
    endclo_set(pre, np, dl, &nd);
    int has0 = 0, has1 = 0;
    for (int k = 0; k < nd; k++) { if (dl[k]) has1 = 1; else has0 = 1; }
    if (has0 && has1) { mp->multi++; *firsts |= 1 << dl[0]; }
}

/* The END distances in priority order, asked of EVERY pre-set that reaches a
 * state (pcrec interns by closure list, so one state stands for pre-sets
 * that differ only in threads already past their last byte). */
static void mark_prio(const Dfa *d, int root, MP *mp)
{
    int n = d->n;
    char *vis = calloc(n, 1);
    int *bq = malloc(sizeof(int) * (n + 1)), qh = 0, qt = 0;
    int firsts = 0;   /* bit c: some multi-distance END pre-set picks c first */
    int *buf = malloc(sizeof(int) * (g_nfa->n + 1));
    int *dl = malloc(sizeof(int) * (g_nfa->n + 1));
    int r0 = root;
    mp_eval(&r0, 1, dl, mp, &firsts);
    for (int k = -1; k < d->natoms; k++) {
        int s = k < 0 ? d->s0 : d->s1u[k];
        if (s >= 0 && !vis[s]) { vis[s] = 1; bq[qt++] = s; }
    }
    while (qh < qt) {
        int i = bq[qh++];
        const DView *v = &d->st[i].up[0];
        for (int c = 0; c < d->ncls; c++) {
            int to = d->st[i].tr[c];
            if (to < 0) continue;
            int rb = d->rep[c], m = 0;
            for (int k = 0; k < v->nlist; k++) {
                const NState *st = &g_nfa->st[v->list[k]];
                if (st->k == N_CLASS && (st->cls[rb >> 3] >> (rb & 7) & 1)) buf[m++] = st->t1;
            }
            mp_eval(buf, m, dl, mp, &firsts);
            if (!vis[to]) { vis[to] = 1; bq[qt++] = to; }
        }
    }
    mp->cls = firsts == 0 ? 0 : firsts == 1 ? 1 : firsts == 2 ? 2 : 3;
    free(vis); free(bq); free(buf); free(dl);
}

static void build_lowered(const char *gpat, int enc, TM *tf, TM *ta, MP *mp)
{
    memset(tf, 0, sizeof *tf); memset(ta, 0, sizeof *ta); memset(mp, 0, sizeof *mp);
    for (int pass = 0; pass < 5; pass++) {
        Front fr;
        if (!front(gpat, enc, &fr)) return;
        Ctx *cx = fr.cx;
        if (setjmp(cx->jb) != 0) { if (getenv("B3REV_DEBUG")) fprintf(stderr, "low pass %d: %s\n", pass, cx->err->msg); continue; }
        pcrec_build_nfa(cx, fr.root, &cx->job->nfa, false, false);
        patch(&cx->job->nfa);
        if (pcrec_nfa_has_bot(&cx->job->nfa)) { if (getenv("B3REV_DEBUG")) fprintf(stderr, "low: bot\n"); return; }
        pcrec_nfa_wrap_unanchored(cx, &cx->job->nfa);
        pcrec_facts_seal_e3(cx);
        g_nfa = &cx->job->nfa;
        free(g_seen); g_seen = calloc(g_nfa->n, sizeof(int)); g_stamp = 0;
        g_unmod = 0;
        Nfa *nfa = &cx->job->nfa;
        switch (pass) {
        case 0:   /* forward, pcrec's own minimized + post */
            pcrec_build_min_dfa(cx, nfa, &cx->job->dfa, true, false, CAP, nfa->start, false);
            tf->umin = cx->job->dfa.n; tf->upost = scanedge_count(cx->job->dfa, 0, true); tf->ok = 1;
            break;
        case 1:   /* forward unminimized -> the tagged model */
            pcrec_build_dfa(cx, nfa, &cx->job->dfa, true, false, CAP, nfa->start, false);
            tf->unmin = cx->job->dfa.n;
            tagged_model(&cx->job->dfa, nfa->start, tf);
            tf->unmodelled |= g_unmod;
            break;
        case 2:
            cx->job->adfa.optional = true;
            pcrec_build_min_dfa(cx, nfa, &cx->job->adfa, true, false, CAP, nfa->anch_start, true);
            if (cx->job->adfa.overflowed) break;
            ta->umin = cx->job->adfa.n; ta->upost = scanedge_count(cx->job->adfa, 0, true); ta->ok = 1;
            break;
        case 3:
            pcrec_build_dfa(cx, nfa, &cx->job->adfa, true, false, CAP, nfa->anch_start, true);
            if (cx->job->adfa.overflowed) { ta->ok = 0; break; }
            ta->unmin = cx->job->adfa.n;
            tagged_model(&cx->job->adfa, nfa->anch_start, ta);
            ta->unmodelled |= g_unmod;
            break;
        case 4:   /* mark_prio: the unpruned anchored machine */
            pcrec_build_dfa(cx, nfa, &cx->job->adfa, false, false, CAP, nfa->anch_start, true);
            if (cx->job->adfa.overflowed) { mp->ok = -1; mp->states = -1; break; }
            mp->states = cx->job->adfa.n;
            mark_prio(&cx->job->adfa, nfa->anch_start, mp);
            mp->ok = g_unmod ? -2 : 1;
            break;
        }
    }
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
    printf("id\tstatus\tnl_last\t"
           "r_today\tr_today_post\tr_untag\tr_untag_post\tr_reach\tr_tag\tr_or\tr_ncols\t"
           "tie_pairs\ttie_states\ttie_classdep\ttie_absent\tr_tag_post\tr_tag_post_unfixed\tr_or_post\t"
           "f_today\tf_today_post\ta_today\ta_today_post\t"
           "f_umin\tf_upost\tf_unmin\tf_model\tf_accmis\tf_bconf\tf_tag\tf_tag_post\tf_tag_post_unfixed\tf_model_post\tf_unmod\tf_b1\t"
           "a_ok\ta_umin\ta_upost\ta_unmin\ta_model\ta_accmis\ta_bconf\ta_tag\ta_tag_post\ta_tag_post_unfixed\ta_model_post\ta_unmod\t"
           "mp_ok\tmp_states\tmp_cls\tmp_multi\n");
    char *line = NULL; size_t capn = 0; ssize_t got;
    while ((got = getline(&line, &capn, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        char *f[7]; int nf = 0;
        for (char *p = line; nf < 7; ) { f[nf++] = p; char *t = strchr(p, '\t'); if (!t) break; *t = 0; p = t + 1; }
        if (nf < 7) continue;
        int enc = strcmp(f[1], "utf8") == 0 ? PCREC_ENC_UTF8 : PCREC_ENC_BYTE;
        char *pt = unhex(f[2]), *pu = unhex(f[3]), *p0 = unhex(f[4]), *p1 = unhex(f[5]), *pg = unhex(f[6]);
        M today, untag, t0, t1;
        build_rev(pt, enc, &today); build_rev(pu, enc, &untag);
        build_rev(p0, enc, &t0); build_rev(p1, enc, &t1);
        if (!today.ok || !untag.ok || !t0.ok || !t1.ok) {
            printf("%s\trev-build-failed\n", f[0]); fflush(stdout); continue;
        }
        Prod P;
        int pr = product(&t0, &t1, &P);
        PM ft, at;
        build_fwd_today(pt, enc, &ft, &at);
        TM tf, ta;
        MP mp;
        build_lowered(pg, enc, &tf, &ta, &mp);
        printf("%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t"
               "%d\t%d\t%d\t%d\t"
               "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t"
               "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t"
               "%d\t%d\t%d\t%d\n",
               f[0], pr < 0 ? "tag-overflow" : "ok", nl_last(&today.d),
               today.n, today.post, untag.n, untag.post, P.reach, pr < 0 ? -1 : P.tag_min, P.or_min, P.ncols,
               P.tie_pairs, P.tie_states, P.tie_classdep, P.tie_absent, P.post_fixed, P.post_unfixed, P.post_or,
               ft.ok ? ft.min : -1, ft.ok ? ft.post : -1, at.ok ? at.min : -1, at.ok ? at.post : -1,
               tf.ok ? tf.umin : -1, tf.upost, tf.unmin, tf.model_untag, tf.acc_mismatch, tf.b_conflict, tf.tag_min,
               tf.tag_post_fixed, tf.tag_post_unfixed, tf.untag_post_model, tf.unmodelled, tf.b1_states,
               ta.ok, ta.umin, ta.upost, ta.unmin, ta.model_untag, ta.acc_mismatch, ta.b_conflict, ta.tag_min,
               ta.tag_post_fixed, ta.tag_post_unfixed, ta.untag_post_model, ta.unmodelled,
               mp.ok, mp.states, mp.cls, mp.multi);
        fflush(stdout);
        free(pt); free(pu); free(p0); free(p1); free(pg);
    }
    return 0;
}
