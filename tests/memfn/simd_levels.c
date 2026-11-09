/* tests/memfn/simd_levels.c -- prints the kit's ISA levels (mf_levels(),
 * memfn/include/memfn.h; memfn/src/levels.def) and its CPU targets
 * (mf_targets(); memfn/src/targets.def) with their C text, one row per
 * line, tab-separated:
 *   level  token family needs header vw test_march stamp
 *   target name family features open close guard
 * where a target's family is "-" for the portable target, and open, close
 * (mf_target_c_of) and guard (its family's mf_family_c_of) are the kit's
 * declared C text in lowercase hex ("" when empty). The SIMD floor check
 * (simd_floor_check.py) reads it: the levels a target admits, and the ONLY
 * scaffolding spellings its lint accepts, taken from the kit's table rather
 * than a copy typed into the check. [MEMFN] R-13; re-aimed for the target
 * seam (U2+U3, lane u3floor). */
#include <stdio.h>
#include <string.h>

#include "memfn.h"

static void hex(const char *s)
{
    putchar('\t');
    for (; s && *s; s++)
        printf("%02x", (unsigned char)*s);
}

int main(void)
{
    size_t n = 0;
    const mf_level *lv = mf_levels(&n);
    for (size_t i = 0; i < n; i++) {
        /* the header's name, from the kit's spelling of the level's bit */
        const char *inc = mf_include_c(lv[i].includes), *lt = inc ? strchr(inc, '<') : NULL;
        int hl = lt && strchr(lt, '>') ? (int)(strchr(lt, '>') - lt - 1) : 0;
        printf("level\t%s\t%s\t%s\t%.*s\t%u\t%s\t%s\n", lv[i].token, lv[i].family, lv[i].needs,
               hl, lt ? lt + 1 : "", lv[i].vw, lv[i].test_march, lv[i].stamp);
    }
    const mf_target *t = mf_targets(&n);
    for (size_t i = 0; i < n; i++) {
        const mf_target_c *c = mf_target_c_of(&t[i]);
        const mf_family_c *f = t[i].family ? mf_family_c_of(t[i].family) : NULL;
        printf("target\t%s\t%s\t%s", t[i].name, t[i].family ? t[i].family->name : "-",
               t[i].features);
        hex(c ? c->region_open : NULL);
        hex(c ? c->region_close : NULL);
        hex(f ? f->guard : NULL);
        putchar('\n');
    }
    return 0;
}
