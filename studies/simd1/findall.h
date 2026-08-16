#ifndef FINDALL_H
#define FINDALL_H

#include <stddef.h>
#include <stdint.h>

/* Find-all (pre-searcher) contract: report EVERY occurrence start, exact and
 * ascending, overlapping occurrences included.  Offsets are written to
 * out[0..cap-1]; the return value is the TOTAL number of occurrences found,
 * which may exceed cap (the excess are counted but not stored — callers size
 * cap from a density estimate and can detect truncation by count > cap).
 *
 * Memory contract is identical to match_fn (matcher.h): never read at or past
 * hay+n, never before hay; n shorter than the minimum match returns 0 without
 * touching memory.
 *
 * The same signature serves factor-pairing pre-searchers (e.g. "wolf" then a
 * gap of 0..64 bytes then "enzyme"): they emit the ascending starts of the
 * SECOND factor at positions where the pair constraint is satisfiable.
 */
typedef size_t (*findall_fn)(const char *hay, size_t n,
                             uint32_t *out, size_t cap);

#endif
