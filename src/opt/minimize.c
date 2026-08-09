/* DFA minimization (plan M2.2): Moore-style partition refinement with
 * signature hashing. Two states merge iff they have the same accept bit and
 * equivalent transitions — including the EOL-view edge, which is treated as
 * one extra alphabet symbol (eolvar == -1 means "self", so states whose EOL
 * view is themselves refine correctly against states with a distinct view).
 *
 * Priority (leftmost-first) semantics are fully baked into the transition
 * structure by the time this runs, so behavior-preserving merging cannot
 * change any match result. Runs on every machine (attempt, forward,
 * reverse); shrinks emitted tables / label counts, which is both a code-size
 * and a cache win (compare case f motivated this).
 *
 * Pure computation: no ctx_fail paths, so plain malloc/free is safe here. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* signature of state i under partition `part`:
 * [ part(i), part(δ(i,0)), ..., part(δ(i,ncls-1)), part(δ(i,EOL)) ] */
static void state_sig(const Dfa *d, const int *part, int i, int *sig)
{
    const DState *s = &d->st[i];
    int k = 0;
    sig[k++] = part[i];
    for (int cl = 0; cl < d->ncls; cl++) {
        int t = s->tr[cl];
        sig[k++] = (t < 0) ? -1 : part[t];
    }
    int v = s->eolvar;
    sig[k++] = (v < 0) ? part[i] : part[v];
}

void pcrec_minimize_dfa(Ctx *cx, Dfa *d)
{
    int n = d->n;
    if (n <= 1) return;
    int siglen = d->ncls + 2;

    int *part = malloc((size_t)n * sizeof(int));
    int *newpart = malloc((size_t)n * sizeof(int));
    int *sig = malloc((size_t)siglen * sizeof(int));
    size_t hcap = 1;
    while (hcap < (size_t)n * 2) hcap *= 2;
    int *htab = malloc(hcap * sizeof(int));       /* -> state index (class rep) */
    int *keys = malloc((size_t)n * (size_t)siglen * sizeof(int));
    if (!part || !newpart || !sig || !htab || !keys) abort();

    int nparts = 0;
    {
        int accid[2] = { -1, -1 };
        for (int i = 0; i < n; i++) {
            int a = d->st[i].accept ? 1 : 0;
            if (accid[a] < 0) accid[a] = nparts++;
            part[i] = accid[a];
        }
    }

    for (;;) {
        memset(htab, -1, hcap * sizeof(int));
        int next = 0;
        for (int i = 0; i < n; i++) {
            state_sig(d, part, i, sig);
            uint32_t h = 2166136261u;
            for (int k = 0; k < siglen; k++) {
                h ^= (uint32_t)sig[k];
                h *= 16777619u;
            }
            size_t hi = h & (hcap - 1);
            for (;;) {
                int rep = htab[hi];
                if (rep < 0) {
                    htab[hi] = i;
                    memcpy(keys + (size_t)i * siglen, sig,
                           (size_t)siglen * sizeof(int));
                    newpart[i] = next++;
                    break;
                }
                if (memcmp(keys + (size_t)rep * siglen, sig,
                           (size_t)siglen * sizeof(int)) == 0) {
                    newpart[i] = newpart[rep];
                    break;
                }
                hi = (hi + 1) & (hcap - 1);
            }
        }
        int *tmp = part;
        part = newpart;
        newpart = tmp;
        if (next == nparts) break;   /* fixpoint */
        nparts = next;
    }

    if (nparts < n) {
        /* renumber classes by first occurrence, rebuild states compactly */
        int m = nparts;
        int *seq = malloc((size_t)m * sizeof(int));
        DState *ns = calloc((size_t)m, sizeof(DState));
        if (!seq || !ns) abort();
        memset(seq, -1, (size_t)m * sizeof(int));
        int next = 0;
        for (int i = 0; i < n; i++)
            if (seq[part[i]] < 0) seq[part[i]] = next++;

        for (int i = 0; i < n; i++) {
            int c = seq[part[i]];
            if (ns[c].tr) continue;   /* class already built from its rep */
            const DState *o = &d->st[i];
            ns[c].accept = o->accept;
            ns[c].nlist = 0;
            ns[c].list = NULL;
            ns[c].tr = arena_alloc(&cx->arena, (size_t)d->ncls * sizeof(int));
            for (int cl = 0; cl < d->ncls; cl++) {
                int t = o->tr[cl];
                ns[c].tr[cl] = (t < 0) ? -1 : seq[part[t]];
            }
            int v = o->eolvar;
            ns[c].eolvar = (v < 0 || part[v] == part[i]) ? -1 : seq[part[v]];
        }

        memcpy(d->st, ns, (size_t)m * sizeof(DState));
        d->n = m;
        if (d->s0 >= 0) d->s0 = seq[part[d->s0]];
        if (d->s1 >= 0) d->s1 = seq[part[d->s1]];
        free(seq);
        free(ns);
    }

    free(part);
    free(newpart);
    free(sig);
    free(htab);
    free(keys);
}
