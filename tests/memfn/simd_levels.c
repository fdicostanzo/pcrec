/* tests/memfn/simd_levels.c -- prints the kit's ISA levels (mf_levels(),
 * memfn/include/memfn.h; memfn/src/levels.def) one per line, tab-separated:
 * token, guard, header, vw, test_march, stamp. The SIMD floor check
 * (simd_floor_check.py) reads it for C18's guard lint and C9-x86's levels;
 * a literal floor on the count is that check's (K35). [MEMFN] R-13. */
#include <stdio.h>

#include "memfn.h"

int main(void)
{
    size_t n = 0;
    const mf_level *lv = mf_levels(&n);
    for (size_t i = 0; i < n; i++)
        printf("%s\t%s\t%s\t%u\t%s\t%s\n", lv[i].token, lv[i].guard, lv[i].header,
               lv[i].vw, lv[i].test_march, lv[i].stamp);
    return 0;
}
