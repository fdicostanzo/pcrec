/* tests/code/octet.h — UC-1a's user header (docs/design/inline_c_requirements.md
 * UC-1a): a decimal digit run's value is at most 255. Named by the
 * `code-header c "octet.h"` head lines of this directory's .rxt files and
 * found by the harness's `-I` of the .rxt file's own directory. */
#ifndef TESTS_CODE_OCTET_H
#define TESTS_CODE_OCTET_H
#include <stddef.h>

static inline int octet_le255(const unsigned char *s, ptrdiff_t n)
{
    unsigned v = 0;
    for (ptrdiff_t i = 0; i < n; i++) v = v * 10 + (unsigned)(s[i] - '0');
    return v <= 255;
}

/* UC-1b's tail form: every one of groups 1..n holds an octet <= 255. */
static inline int all_le255(const unsigned char *s, const ptrdiff_t (*caps)[2],
                            int n)
{
    for (int g = 1; g <= n; g++)
        if (!octet_le255(s + caps[g][0], caps[g][1] - caps[g][0])) return 0;
    return 1;
}
#endif
