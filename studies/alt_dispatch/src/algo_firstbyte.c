#include "algo_firstbyte.h"
#include <stdlib.h>

struct FirstByteIndex {
    int *idx[256];   /* idx[b] = malloc'd array of branch indices sharing byte b at pos 0 */
    int cnt[256];
};

FirstByteIndex *fb_build(const BranchSet *bs)
{
    FirstByteIndex *fb = calloc(1, sizeof *fb);
    int caps[256] = {0};
    /* size pass */
    for (int j = 0; j < bs->n; j++) {
        const Branch *b = &bs->br[j];
        for (int c = 0; c < 256; c++)
            if (bs_test(&b->seq[0], (unsigned char)c)) caps[c]++;
    }
    for (int c = 0; c < 256; c++)
        if (caps[c]) fb->idx[c] = malloc((size_t)caps[c] * sizeof(int));
    for (int j = 0; j < bs->n; j++) {
        const Branch *b = &bs->br[j];
        for (int c = 0; c < 256; c++)
            if (bs_test(&b->seq[0], (unsigned char)c))
                fb->idx[c][fb->cnt[c]++] = j;
    }
    return fb;
}

void fb_free(FirstByteIndex *fb)
{
    if (!fb) return;
    for (int c = 0; c < 256; c++) free(fb->idx[c]);
    free(fb);
}

size_t fb_bytes(const FirstByteIndex *fb)
{
    size_t total = sizeof(*fb);
    for (int c = 0; c < 256; c++) total += (size_t)fb->cnt[c] * sizeof(int);
    return total;
}

static bool branch_matches(const Branch *b, const unsigned char *subj,
                           size_t slen, size_t pos, long long *vb)
{
    size_t avail = pos < slen ? slen - pos : 0;
    int lim = b->len < (int)avail ? b->len : (int)avail;
    for (int k = 0; k < lim; k++) {
        (*vb)++;
        if (!bs_test(&b->seq[k], subj[pos + (size_t)k])) return false;
    }
    return lim == b->len;
}

Answer fb_dispatch(const FirstByteIndex *fb, const BranchSet *bs,
                   const unsigned char *subj, size_t slen, size_t pos,
                   Cost *cost)
{
    Answer a = { false, -1, 0 };
    if (pos >= slen) return a;
    unsigned char c0 = subj[pos];
    const int *group = fb->idx[c0];
    int gn = fb->cnt[c0];
    int best = -1;
    for (int g = 0; g < gn; g++) {
        cost->tries++;
        int j = group[g];
        if (branch_matches(&bs->br[j], subj, slen, pos, &cost->verify_bytes)) {
            /* group is in ascending original-index order (stable build), so
             * the first success is already the leftmost-first winner --
             * matches vm_alt's own "first that matches wins" within the
             * narrowed candidate set. */
            best = j;
            break;
        }
    }
    if (best >= 0) {
        a.hit = true;
        a.index = bs->br[best].index;
        a.match_len = bs->br[best].len;
    }
    return a;
}
