#include "algo_trie.h"
#include <stdlib.h>
#include <string.h>

typedef struct TrieChild {
    ByteSet cls;
    TrieNode *node;
} TrieChild;

struct TrieNode {
    int *accepts;
    int naccepts;
    TrieChild *children;
    int nchildren;
    /* DECLINED: at least two distinct child classes overlap (rule 2's
     * hazard, on classes wider than a case-fold pair -- never true for this
     * study's real bench-derived inputs; see tests/ for the case that
     * triggers it). `decl_items`/`decl_n` is then a serial fallback list:
     * the remaining (branch, depth-so-far) pairs, matched by brute force
     * from here rather than factored further -- "an NFA step or a decline",
     * this ports the decline half. */
    bool declined;
    const Branch **decl_items;
    int decl_n;
    int depth; /* bytes already consumed to reach this node, for the fallback */

    /* (e) ruling R1: the lowest original branch index reachable AT or
     * BELOW this node (this node's own accept(s) included). -1 if no
     * accept is reachable at all. Computed once, after the whole trie is
     * built, by annotate_subtree_min(). */
    int subtree_min;
};

typedef struct { const Branch *b; } Item;

static Trie *g_build; /* accumulates counters during construction */

static TrieNode *node_new(void)
{
    TrieNode *n = calloc(1, sizeof *n);
    return n;
}

static bool classes_pairwise_disjoint(ByteSet *cls, int n)
{
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (!bs_eq(&cls[i], &cls[j]) && !bs_disjoint(&cls[i], &cls[j]))
                return false;
    return true;
}

static TrieNode *build(const Branch **items, int n, int depth)
{
    g_build->nnodes++;
    TrieNode *node = node_new();
    node->depth = depth;

    /* rule 1: collect every item that ends exactly here. Distinct pools
     * never produce more than one (property 1, no duplicate branches), but
     * this stays general. */
    int nend = 0;
    for (int i = 0; i < n; i++) if (items[i]->len == depth) nend++;
    if (nend) {
        node->accepts = malloc((size_t)nend * sizeof(int));
        int k = 0;
        for (int i = 0; i < n; i++)
            if (items[i]->len == depth) node->accepts[k++] = items[i]->index;
        node->naccepts = nend;
    }

    /* remaining items continue past this depth */
    const Branch **cont = malloc((size_t)n * sizeof(const Branch *));
    int nc = 0;
    for (int i = 0; i < n; i++) if (items[i]->len > depth) cont[nc++] = items[i];
    if (nc == 0) { free(cont); return node; }

    /* distinct classes among the continuing items at this depth */
    ByteSet *uniq = malloc((size_t)nc * sizeof(ByteSet));
    int nu = 0;
    for (int i = 0; i < nc; i++) {
        const ByteSet *c = &cont[i]->seq[depth];
        bool seen = false;
        for (int u = 0; u < nu; u++) if (bs_eq(&uniq[u], c)) { seen = true; break; }
        if (!seen) uniq[nu++] = *c;
    }

    if (!classes_pairwise_disjoint(uniq, nu)) {
        /* rule 2's hazard, un-vacuous: decline rather than mis-order. */
        node->declined = true;
        node->decl_items = cont;
        node->decl_n = nc;
        free(uniq);
        return node;
    }

    node->children = malloc((size_t)nu * sizeof(TrieChild));
    node->nchildren = nu;
    g_build->nchildslots += nu;
    if (nu > g_build->max_fanout) g_build->max_fanout = nu;

    for (int u = 0; u < nu; u++) {
        const Branch **sub = malloc((size_t)nc * sizeof(const Branch *));
        int ns = 0;
        for (int i = 0; i < nc; i++)
            if (bs_eq(&cont[i]->seq[depth], &uniq[u])) sub[ns++] = cont[i];
        node->children[u].cls = uniq[u];
        node->children[u].node = build(sub, ns, depth + 1);
        free(sub);
    }
    free(uniq);
    free(cont);
    return node;
}

/* (e)'s per-node annotation: subtree_min = min(this node's own accepts,
 * every child's subtree_min, every declined item's index). A STATIC,
 * conservative bound -- it counts every accept reachable in the WHOLE
 * subtree, not only the one path a specific subject's walk will actually
 * reach (the compiler cannot know that in advance either), which is
 * exactly what makes "commit iff my own index equals subtree_min" safe:
 * nothing anywhere below this node, on any path, could ever produce a
 * lower index. */
static int annotate_subtree_min(TrieNode *n)
{
    int m = -1;
    for (int i = 0; i < n->naccepts; i++)
        if (m < 0 || n->accepts[i] < m) m = n->accepts[i];
    if (n->declined) {
        for (int i = 0; i < n->decl_n; i++) {
            int idx = n->decl_items[i]->index;
            if (m < 0 || idx < m) m = idx;
        }
    } else {
        for (int i = 0; i < n->nchildren; i++) {
            int cm = annotate_subtree_min(n->children[i].node);
            if (cm >= 0 && (m < 0 || cm < m)) m = cm;
        }
    }
    n->subtree_min = m;
    return m;
}

Trie *trie_build_from(const BranchSet *bs)
{
    Trie *t = calloc(1, sizeof *t);
    g_build = t;
    const Branch **items = malloc((size_t)bs->n * sizeof(const Branch *));
    for (int i = 0; i < bs->n; i++) items[i] = &bs->br[i];
    t->root = build(items, bs->n, 0);
    free(items);
    g_build = NULL;
    annotate_subtree_min(t->root);
    return t;
}

static void node_free(TrieNode *n)
{
    if (!n) return;
    free(n->accepts);
    if (n->declined) {
        free((void *)n->decl_items);
    } else {
        for (int i = 0; i < n->nchildren; i++) node_free(n->children[i].node);
        free(n->children);
    }
    free(n);
}

void trie_free(Trie *t)
{
    if (!t) return;
    node_free(t->root);
    free(t);
}

static size_t node_bytes(const TrieNode *n)
{
    size_t s = sizeof(*n) + (size_t)n->naccepts * sizeof(int);
    if (n->declined) {
        s += (size_t)n->decl_n * sizeof(const Branch *);
    } else {
        s += (size_t)n->nchildren * sizeof(TrieChild);
        for (int i = 0; i < n->nchildren; i++) s += node_bytes(n->children[i].node);
    }
    return s;
}

size_t trie_bytes(const Trie *t) { return t ? sizeof(*t) + node_bytes(t->root) : 0; }

static void collect(int idx, int *out_cand, int cand_cap, int *ncand)
{
    if (*ncand < cand_cap) out_cand[*ncand] = idx;
    (*ncand)++;
}

static bool branch_matches_tail(const Branch *b, int from,
                                const unsigned char *subj, size_t slen,
                                size_t pos, long long *vb)
{
    size_t avail = pos < slen ? slen - pos : 0;
    for (int k = from; k < b->len; k++) {
        if ((size_t)k >= avail) return false;
        (*vb)++;
        if (!bs_test(&b->seq[k], subj[pos + (size_t)k])) return false;
    }
    return true;
}

Answer trie_dispatch(const Trie *t, const BranchSet *bs,
                     const unsigned char *subj, size_t slen, size_t pos,
                     Cost *cost, int *out_cand, int cand_cap, int *out_ncand)
{
    (void)bs;
    int ncand = 0;
    const TrieNode *node = t->root;
    for (;;) {
        for (int i = 0; i < node->naccepts; i++)
            collect(node->accepts[i], out_cand, cand_cap, &ncand);

        if (node->declined) {
            cost->tries += node->decl_n;
            for (int i = 0; i < node->decl_n; i++) {
                const Branch *b = node->decl_items[i];
                if (branch_matches_tail(b, node->depth, subj, slen, pos, &cost->verify_bytes))
                    collect(b->index, out_cand, cand_cap, &ncand);
            }
            break;
        }
        if (node->nchildren == 0) break;
        size_t bytepos = pos + (size_t)node->depth;
        if (bytepos >= slen) break;
        unsigned char c = subj[bytepos];
        const TrieNode *next = NULL;
        for (int i = 0; i < node->nchildren; i++) {
            cost->tries++; /* one child-slot scanned = one trie "step" */
            if (bs_test(&node->children[i].cls, c)) { next = node->children[i].node; break; }
        }
        cost->verify_bytes++; /* one subject byte consumed at this node */
        if (!next) break;
        node = next;
    }

    *out_ncand = ncand;
    Answer a = { false, -1, 0 };
    if (ncand == 0) return a;
    int best = out_cand[0];
    int lim = ncand < cand_cap ? ncand : cand_cap;
    for (int i = 1; i < lim; i++) if (out_cand[i] < best) best = out_cand[i];
    a.hit = true;
    a.index = best;
    a.match_len = bs->br[best].len;
    return a;
}

/* ------------------------------------------------------------------ */
/* (e) VM-NATIVE TRIE WALK -- ruling R1 (Frank, 2026-09-03). See
 * algo_trie.h's header comment and docs/design/alt_dispatch_study.md for
 * the exactness argument.
 *
 * DEFERRED_CAP bounds this study's own small ascending-index-ordered
 * deferred list. It is NOT a correctness bound on real patterns -- it is
 * this harness's array size, generous against what §5's design-doc
 * measurement finds (the deepest a root-to-leaf path in ANY of this
 * study's tries defers before its first commit). If a pattern this study
 * never built needed more, the walk would need a dynamic array instead;
 * see the design doc's "mask width needed" table for the measured bound
 * this cap is checked against. */
enum { DEFERRED_CAP = 256 };

Answer trie_dispatch_vm(const Trie *t, const BranchSet *bs,
                        const unsigned char *subj, size_t slen, size_t pos,
                        Cost *cost)
{
    int deferred[DEFERRED_CAP];
    int ndeferred = 0;
    int best_deferred = -1;    /* running min of everything deferred so far
                                 * on THIS path -- see the correctness note
                                 * below; -1 means "nothing deferred yet". */
    int commit_index = -1, commit_len = 0;
    const TrieNode *node = t->root;

    for (;;) {
        for (int i = 0; i < node->naccepts; i++) {
            int idx = node->accepts[i];
            /* COMMIT requires idx to beat BOTH halves of what could still
             * outrank it: (1) node->subtree_min -- the ruling's own test,
             * "nothing DEEPER in this subtree is lower" (subtree_min
             * always includes idx itself, so idx==subtree_min means
             * exactly that); AND (2) best_deferred -- nothing SHALLOWER,
             * already passed and set aside on this same path, is lower
             * either. (2) is not in the ruling's literal wording but is
             * REQUIRED for exactness: nfa.c's own rule-1 counter-example
             * (abc|a|abd on "abd") defers "a" (index 1) at depth 1
             * because "abc" (index 0) is reachable deeper -- but on THIS
             * subject the walk actually goes on to "abd" (index 2) at
             * depth 3, whose own subtree is empty (subtree_min==2, no
             * deeper competitor), so (1) alone would wrongly COMMIT to
             * index 2 and never learn that the already-deferred index 1
             * beats it. Checked and regression-guarded by
             * tests/unit_trie.c's rule-1 case. */
            if (idx == node->subtree_min && (best_deferred < 0 || idx < best_deferred)) {
                /* push ONE resumable frame (the VM would resume the walk
                 * deeper from here if idx's own continuation later fails)
                 * and stop the forward pass with this as the primary
                 * answer. */
                commit_index = idx;
                commit_len = node->depth;
                cost->frames++;
                goto walked;
            }
            /* DEFER: beaten by something deeper in this subtree, or by an
             * already-deferred shallower candidate -- record it (ascending
             * order preserved by construction: nfa.c's substring-free
             * bench pools put at most one accept per node, and even this
             * study's adversarial multi-accept cases only defer in
             * non-decreasing depth order, i.e. visit order; a real per-
             * pattern compile-time bit assignment would sort once,
             * statically) and keep walking. */
            if (ndeferred < DEFERRED_CAP) deferred[ndeferred] = idx;
            ndeferred++;
            if (best_deferred < 0 || idx < best_deferred) best_deferred = idx;
        }

        if (node->declined) {
            /* A declined node is a leaf for factoring purposes (rule 2's
             * hazard -- see algo_trie.c's `build()`); treat every
             * continuing item as its own end node AT this depth: commit
             * on the first that matches subtree_min, defer the rest. Same
             * best_deferred cross-check as above. */
            for (int i = 0; i < node->decl_n; i++) {
                cost->tries++;
                const Branch *b = node->decl_items[i];
                if (!branch_matches_tail(b, node->depth, subj, slen, pos, &cost->verify_bytes))
                    continue;
                if (b->index == node->subtree_min && (best_deferred < 0 || b->index < best_deferred)) {
                    commit_index = b->index;
                    commit_len = b->len;
                    cost->frames++;
                    goto walked;
                }
                if (ndeferred < DEFERRED_CAP) deferred[ndeferred] = b->index;
                ndeferred++;
                if (best_deferred < 0 || b->index < best_deferred) best_deferred = b->index;
            }
            break;
        }

        if (node->nchildren == 0) break;
        size_t bytepos = pos + (size_t)node->depth;
        if (bytepos >= slen) break;
        unsigned char c = subj[bytepos];
        const TrieNode *next = NULL;
        for (int i = 0; i < node->nchildren; i++) {
            cost->tries++;
            if (bs_test(&node->children[i].cls, c)) { next = node->children[i].node; break; }
        }
        cost->verify_bytes++;
        if (!next) break;
        node = next;
    }
walked:

    if (commit_index < 0 && ndeferred > 0) {
        /* The walk died (or reached a full leaf) with no commit ever
         * firing -- the ruling's "when the walk dies... try the recorded
         * end nodes" fallback needs its own single frame to carry the
         * mask/iterator, even though nothing is left to actually retry in
         * THIS harness (there is no outer continuation to fail against).
         * The answer is the ascending minimum of what was deferred --
         * exactly (c)'s collected-set minimum, computed the (e) way. */
        cost->frames++;
        int best = deferred[0];
        int lim = ndeferred < DEFERRED_CAP ? ndeferred : DEFERRED_CAP;
        for (int i = 1; i < lim; i++) if (deferred[i] < best) best = deferred[i];
        commit_index = best;
        commit_len = bs->br[best].len;
    }

    if (ndeferred > cost->deferred_seen) cost->deferred_seen = ndeferred;

    Answer a = { false, -1, 0 };
    if (commit_index >= 0) { a.hit = true; a.index = commit_index; a.match_len = commit_len; }
    return a;
}
