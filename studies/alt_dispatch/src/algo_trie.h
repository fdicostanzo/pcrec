/* (c) SORTED TRIE WITH PRIORITY-TAGGED ACCEPTS -- src/ir/nfa.c:192's M2.8
 * trie (trie_build/trie_key), ported to this study's plain literal/ci
 * branch shape and to a QUERY walk rather than an NFA fragment.
 *
 * Construction groups branches by shared prefix (a maximal run of adjacent-
 * in-CONSTRUCTION classes, sorted so shared prefixes factor regardless of
 * branch order -- nfa.c's whole M2.8 point); every node that some branch
 * ends at exactly carries that branch's ORIGINAL alternation index as an
 * "accept". See docs/design/alt_dispatch_study.md for the exactness
 * argument (why the lowest-index accept collected along a walk is the
 * leftmost-first answer) and for what nfa.c's rule 2 (pairwise-disjoint
 * class runs) reduces to when every class is a singleton or a case-fold
 * pair -- vacuous, so this port never needs rule 2's multi-run machinery on
 * this study's real inputs. It is still IMPLEMENTED (a node whose children
 * classes are not pairwise disjoint is marked DECLINED rather than mis-
 * built) so a deliberately overlapping-class unit test can exercise the
 * boundary the charter asks about; see tests/.
 */
#ifndef ALT_DISPATCH_ALGO_TRIE_H
#define ALT_DISPATCH_ALGO_TRIE_H
#include "common.h"

typedef struct TrieNode TrieNode;

typedef struct {
    TrieNode *root;
    int nnodes;          /* construction: node count, a size proxy */
    long long nchildslots; /* total child-edge count across all nodes */
    int max_fanout;
} Trie;

Trie *trie_build_from(const BranchSet *bs);
void trie_free(Trie *t);
size_t trie_bytes(const Trie *t);

/* out_cand: caller-provided buffer of length cand_cap for the candidate
 * list (accept indices collected along the walk, ascending) -- what a VM's
 * continuation-backtracking would fall back through. *out_ncand is the true
 * count even if it exceeds cand_cap (the buffer just truncates). */
Answer trie_dispatch(const Trie *t, const BranchSet *bs,
                     const unsigned char *subj, size_t slen, size_t pos,
                     Cost *cost, int *out_cand, int cand_cap, int *out_ncand);

/* (e) VM-NATIVE TRIE WALK -- ruling R1 (Frank, 2026-09-03), the PRIMARY
 * candidate: the one the VM emitter would actually build. Reuses (c)'s
 * SAME trie (built once by trie_build_from; no separate construction cost)
 * plus one static per-node annotation, `subtree_min` -- the lowest original
 * branch index reachable at or below this node -- computed once after
 * `trie_build_from` returns. Walks the trie exactly like (c) but decides,
 * at every end node it passes, whether to COMMIT (push one resumable frame
 * and stop -- nothing deeper could ever beat this index) or DEFER (record
 * the index into a small ascending-index-ordered list and keep walking).
 * See docs/design/alt_dispatch_study.md's algorithm (e) section for the
 * exactness argument (why "commit iff this node's own index equals its
 * subtree_min" is safe) and cost model (cost->frames, cost->deferred_seen).
 */
Answer trie_dispatch_vm(const Trie *t, const BranchSet *bs,
                        const unsigned char *subj, size_t slen, size_t pos,
                        Cost *cost);

#endif
