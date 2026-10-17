/* tests/memfn/prov_check.c -- [MEMFN] R-24 (lane r24; MF_SITE_ABI 15): the
 * layout of mf_prov and pcrec's mapping of an answering block's provenance
 * stanza onto it (src/gen/memfn_sites.c pcrec_memfn_prov_stanza).
 *
 *   provchk BYTES TOKEN     BYTES is the stanza's `bytes` (decimal); TOKEN its
 *                           `fidelity` word, or `@none` for a block that
 *                           declares none (the mapping gets NULL).
 *                           Prints `RC<TAB>rc<TAB>fidelity<TAB>bytes<TAB>
 *                           source<TAB>digest` of an mf_prov pre-filled with
 *                           sentinels, so an untouched field reads as one.
 *
 * Run by tests/memfn/run_finder.sh and held by finder_check.py family L, which
 * writes every expectation (the enumerators, the closed token set read off
 * `pcrec --list-schema`). The static assertions below are the LAYOUT half:
 * the three fields B1 declared keep their offsets (LP64) and the two R-24
 * fields follow them, in the order the request names, with an UNSTATED zero
 * for fidelity. A reorder, a insertion before `digest` or a renumbered
 * enumerator stops this file compiling, which fails the section. */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen/memfn_sites.h"

#if __SIZEOF_POINTER__ == 8
_Static_assert(offsetof(mf_prov, source)   == 0,  "mf_prov.source moved");
_Static_assert(offsetof(mf_prov, bundle)   == 8,  "mf_prov.bundle moved");
_Static_assert(offsetof(mf_prov, digest)   == 16, "mf_prov.digest moved");
_Static_assert(offsetof(mf_prov, bytes)    == 24, "mf_prov.bytes is not appended after digest");
_Static_assert(offsetof(mf_prov, fidelity) == 32, "mf_prov.fidelity is not appended after bytes");
#endif
_Static_assert(MF_FID_UNSTATED == 0, "fidelity's zero must be UNSTATED");
_Static_assert(MF_FID_VERBATIM == 1 && MF_FID_ADAPTED == 2 && MF_FID_SYNTHESIZED == 3,
               "the fidelity enumerators were renumbered");

int main(int argc, char **argv)
{
    if (argc != 3) { fputs("usage: provchk BYTES TOKEN|@none\n", stderr); return 2; }
    mf_prov p;
    memset(&p, 0, sizeof p);
    p.source = MF_PROV_MEASURED;
    p.digest = 0x1234;
    p.bytes = 0xDEADBEEFULL;      /* sentinels: a refusal must leave them */
    p.fidelity = 0xEE;
    int rc = pcrec_memfn_prov_stanza(&p, strtoull(argv[1], NULL, 10),
                                     strcmp(argv[2], "@none") ? argv[2] : NULL);
    printf("RC\t%d\t%u\t%llu\t%u\t%llu\n", rc, (unsigned)p.fidelity,
           (unsigned long long)p.bytes, (unsigned)p.source,
           (unsigned long long)p.digest);
    return 0;
}
