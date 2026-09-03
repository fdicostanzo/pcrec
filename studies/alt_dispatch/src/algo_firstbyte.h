/* (b) FIRST-BYTE GROUPING -- the cheap lever recorded on [ENG-ISL]: stable-
 * group branches by first byte, try only the group for the subject's byte,
 * in original order within the group.
 *
 * A `ci` branch's first position can admit two bytes, so it is stably
 * inserted into BOTH of its first byte's groups (in original index order
 * within each) -- one branch can appear in two groups, never more, since
 * this study's classes have at most 2 members (see common.h). This is
 * exactly the M2.8 trie's depth-1 fan-out with the deeper levels left
 * unfactored: it is 1-byte discrimination only. */
#ifndef ALT_DISPATCH_ALGO_FIRSTBYTE_H
#define ALT_DISPATCH_ALGO_FIRSTBYTE_H
#include "common.h"

typedef struct FirstByteIndex FirstByteIndex;

/* Construction cost is charged by the caller (wall time around this call). */
FirstByteIndex *fb_build(const BranchSet *bs);
void fb_free(FirstByteIndex *fb);
size_t fb_bytes(const FirstByteIndex *fb); /* table memory footprint */

Answer fb_dispatch(const FirstByteIndex *fb, const BranchSet *bs,
                   const unsigned char *subj, size_t slen, size_t pos,
                   Cost *cost);

#endif
