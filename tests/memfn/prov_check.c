/* tests/memfn/prov_check.c -- [MEMFN] the analysis object's seam layout,
 * reduced at span_pick.md unit 1g (MF_SITE_ABI 22) to `mf_akind.digest`'s
 * offset. R-24 (lane r24; MF_SITE_ABI 15) held mf_prov's layout and pcrec's
 * provenance stanza mapping here; both left the seam at 1g (D186 add. 2: the
 * kit is handed the payload and its digest, never their source).
 *
 * BUILD-ONLY: tests/memfn/run_finder.sh compiles it (-fsyntax-only,
 * -Werror) and never links or runs it. A reorder of mf_akind, or an insertion before `digest`, stops this
 * file compiling, which fails the section. */
#include <stddef.h>

#include "memfn.h"

#if __SIZEOF_POINTER__ == 8
_Static_assert(offsetof(mf_akind, digest) == 16, "mf_akind.digest moved");
#endif
