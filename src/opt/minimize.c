/* DFA minimization (plan M2.2): Moore-style partition refinement with
 * signature hashing. Two states merge iff they have the same accept bit and
 * equivalent transitions — including the EOL-view edge, which is treated as
 * one extra alphabet symbol (eolvar == -1 means "self", so states whose EOL
 * view is themselves refine correctly against states with a distinct view) —
 * and, since [M6.2] wave A, the END-view edge (`endvar`, `\z`'s view) as a
 * SECOND extra symbol. The two are not symmetric and the asymmetry is the
 * thing to hold on to: `eolvar == -1` means "self", `endvar == -1` means
 * "SAME AS THE EOL VIEW" (src/ir/dfa.c's make_state), so both edges are
 * RESOLVED through that chain before they enter a signature, and both are
 * re-canonicalized against the resolved target when the states are rebuilt.
 * Resolve them wrongly and minimization would either merge states that differ
 * only at `pos == n` or refuse to merge states that do not differ at all.
 *
 * BYTE-IDENTITY on `\z`-free patterns is preserved by construction, not by a
 * conditional: with no `\z` in the pattern every `endvar` is -1, so the
 * resolved end target EQUALS the resolved eol target at every state, and the
 * appended signature column is a duplicate of the one before it. A duplicated
 * column cannot change a partition, so the same states merge as before.
 *
 * Priority (leftmost-first) semantics are fully baked into the transition
 * structure by the time this runs, so behavior-preserving merging cannot
 * change any match result. Runs on every machine (attempt, forward,
 * reverse); shrinks emitted tables / label counts, which is both a code-size
 * and a cache win (compare case f motivated this).
 *
 * Pure computation: plain malloc/free, and the ONLY two ctx_fail paths are the
 * allocation-failure ones added by [M4.7b/K7], which free every live local
 * before they longjmp. Nothing else here leaves the function early, so no other
 * site has to think about ownership. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* signature of state i under partition `part`:
 * [ part(i), part(δ(i,0)), ..., part(δ(i,ncls-1)), part(δ(i,EOL)) ] */
static void state_sig(const Dfa *d, const int *part, int i, int *sig,
                      bool has_end)
{
    const DState *s = &d->st[i];
    int k = 0;
    sig[k++] = part[i];
    for (int cl = 0; cl < d->ncls; cl++) {
        int t = s->tr[cl];
        sig[k++] = (t < 0) ? -1 : part[t];
    }
    int v = (s->eolvar < 0) ? i : s->eolvar;
    sig[k++] = part[v];
    /* THE END COLUMN IS OMITTED ENTIRELY when no state has an END view, and
     * that is a COST decision with a proof rather than a shortcut: with every
     * `endvar` at -1 the column resolves to `part[v]`, a byte-for-byte
     * duplicate of the EOL column beside it, so the partition it produces is
     * identical either way. Keeping it would widen every signature by one int
     * on every state in every refinement ROUND, which on the chain shapes K25
     * already names (`[a-z]{0,30000}` — 30,001 states, O(n) rounds) is a
     * measurable share of the compile. Measured: the unconditional form put
     * that pattern 28% over tests/resource/'s CPU budget. */
    if (has_end) {
        int e = (s->endvar < 0) ? v : s->endvar;
        sig[k++] = part[e];
    }
}

void pcrec_minimize_dfa(Ctx *cx, Dfa *d)
{
    int n = d->n;
    if (n <= 1) return;
    bool has_end = false;
    for (int i = 0; i < n; i++)
        if (d->st[i].endvar >= 0) { has_end = true; break; }
    int siglen = d->ncls + 2 + (has_end ? 1 : 0);

    int *part = malloc((size_t)n * sizeof(int));
    int *newpart = malloc((size_t)n * sizeof(int));
    int *sig = malloc((size_t)siglen * sizeof(int));
    size_t hcap = 1;
    while (hcap < (size_t)n * 2) hcap *= 2;
    int *htab = malloc(hcap * sizeof(int));       /* -> state index (class rep) */
    int *keys = malloc((size_t)n * (size_t)siglen * sizeof(int));
    /* [M4.7b/K7] These five are the only allocations on the compile path the
     * Job does NOT own, so this is the only site where failing cleanly means
     * freeing by hand before the longjmp — everywhere else job_cleanup does it.
     * (Which is also why the file header's "no ctx_fail paths" note no longer
     * holds: there are exactly two, both here, both after their own cleanup.) */
    if (!part || !newpart || !sig || !htab || !keys) {
        free(part); free(newpart); free(sig); free(htab); free(keys);
        ctx_nomem(cx);
    }

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
            state_sig(d, part, i, sig, has_end);
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
        if (!seq || !ns) {
            free(seq); free(ns);
            free(part); free(newpart); free(sig); free(htab); free(keys);
            ctx_nomem(cx);
        }
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
            int v = (o->eolvar < 0) ? i : o->eolvar;
            int e = (o->endvar < 0) ? v : o->endvar;
            ns[c].eolvar = (part[v] == part[i]) ? -1 : seq[part[v]];
            /* against the EOL view, matching make_state's convention */
            ns[c].endvar = (part[e] == part[v]) ? -1 : seq[part[e]];
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
