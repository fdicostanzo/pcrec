/* (a) SERIAL TRY -- today's vm_alt (src/gen/emit_vm.c): try branches in
 * source order, first that matches wins. This IS the oracle: it is
 * trivially leftmost-first because it tries branches in preference order
 * and stops at the first success, exactly as the charter states.
 *
 * Cost: tries == number of branches attempted before success (or `n` on a
 * total miss) -- one "try" per push/fail/pop/dispatch round-trip vm_alt
 * would spend. verify_bytes == number of byte-class membership tests
 * performed across all attempted branches (mismatches fail fast: a branch
 * whose first byte does not admit subject[pos] costs exactly 1). */
#ifndef ALT_DISPATCH_ALGO_SERIAL_H
#define ALT_DISPATCH_ALGO_SERIAL_H
#include "common.h"

Answer serial_try(const BranchSet *bs, const unsigned char *subj, size_t slen,
                   size_t pos, Cost *cost);

#endif
