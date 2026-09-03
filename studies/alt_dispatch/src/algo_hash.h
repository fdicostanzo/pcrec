/* (d) K-BYTE BLOCK HASH -- [OPT-ALTHASH]: hash the next k bytes into a
 * table over the branches' distinct k-byte prefixes; branches shorter than
 * k are handled at a per-byte (here: serial) path, matching the filed
 * row's soundness note (b): "states with an accept within k steps, and
 * positions with fewer than k bytes left, take the per-byte path."
 *
 * Table entries store the CONCRETE key bytes (not just the hash), so a
 * lookup is exact -- a miss really means "no branch has this k-prefix",
 * never a false accept. `ci` branches enumerate every concrete realization
 * of their k-byte prefix (up to 2^k for this study's fold-pair-only
 * classes) as separate keys mapping to the SAME branch, mirroring the
 * filed design note (b)'s VM-side requirement: "map a block to the first
 * branch in alternation order among those whose prefix matches." */
#ifndef ALT_DISPATCH_ALGO_HASH_H
#define ALT_DISPATCH_ALGO_HASH_H
#include "common.h"

typedef struct HashIdx HashIdx;

HashIdx *hash_build(const BranchSet *bs, int k);
void hash_free(HashIdx *hi);
size_t hash_bytes(const HashIdx *hi);
int hash_table_slots(const HashIdx *hi);
int hash_distinct_keys(const HashIdx *hi);

Answer hash_dispatch(const HashIdx *hi, const BranchSet *bs,
                     const unsigned char *subj, size_t slen, size_t pos,
                     Cost *cost);

#endif
