#include "algo_serial.h"

/* Returns true iff branch b matches subject[pos..) literally; counts the
 * byte-class tests it performs (fail-fast) into *vb. */
static bool branch_matches(const Branch *b, const unsigned char *subj,
                           size_t slen, size_t pos, long long *vb)
{
    if (pos + (size_t)b->len > slen) {
        /* Still charge the tests that would run before falling off the
         * end -- a real matcher discovers "not enough subject left" the
         * same way, by testing bytes until it runs out. */
        size_t avail = pos < slen ? slen - pos : 0;
        for (size_t k = 0; k < avail; k++) {
            (*vb)++;
            if (!bs_test(&b->seq[k], subj[pos + k])) return false;
        }
        return false;
    }
    for (int k = 0; k < b->len; k++) {
        (*vb)++;
        if (!bs_test(&b->seq[k], subj[pos + (size_t)k])) return false;
    }
    return true;
}

Answer serial_try(const BranchSet *bs, const unsigned char *subj, size_t slen,
                   size_t pos, Cost *cost)
{
    Answer a = { false, -1, 0 };
    for (int j = 0; j < bs->n; j++) {
        cost->tries++;
        if (branch_matches(&bs->br[j], subj, slen, pos, &cost->verify_bytes)) {
            a.hit = true;
            a.index = bs->br[j].index;
            a.match_len = bs->br[j].len;
            return a;
        }
    }
    return a;
}
