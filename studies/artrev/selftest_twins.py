#!/usr/bin/env python3
"""selftest_twins.py -- build the self-test's deliberately bad / slowed twins by
editing an arm dir created with `artrev.py twin NAME ARM --new`.

  selftest_twins.py ARMDIR KIND     KIND: wrong_end | wrong_cap | slow | simd:<which> | unchanged
Wrappers rename the artifact's own entry to a static `<p>_<fn>_real` and append
a replacement with the same signature, so the public ABI is untouched.
"""
import re
import sys

SIMD = {
    "include": '#include <immintrin.h>\n',
    "neon_include": '#include <arm_neon.h>\n',
    "builtin_ia32": 'static int artrev_x(void){ return __builtin_ia32_pause(), 0; }\n',
    "builtin_neon": 'static int artrev_x(void){ return __builtin_neon_vaddv_u8(0); }\n',
    "vector_size": 'typedef unsigned char artrev_v16 __attribute__((vector_size(16)));\n',
    "pragma_target": '#pragma GCC target("avx2")\n',
    "pragma_optimize": '#pragma GCC optimize("O3")\n',
    "attr_optimize": '__attribute__((optimize("O3"))) static int artrev_x(void){ return 0; }\n',
    "attr_target": '__attribute__((target("avx2"))) static int artrev_x(void){ return 0; }\n',
    "mm_call": 'static int artrev_x(void){ return _mm_movemask_epi8(_mm_setzero_si128()); }\n',
}


def rename(src, fn):
    pat = re.compile(r"\n((?:int|ptrdiff_t) )(rx_%s)\(" % fn)
    if not pat.search(src):
        sys.exit("no definition of rx_%s in the artifact" % fn)
    return pat.sub(lambda m: "\nstatic %s%s_real(" % (m.group(1), m.group(2)), src, count=1)


def main():
    d, kind = sys.argv[1], sys.argv[2]
    p = d + "/artifact.c"
    src = open(p).read()
    if kind == "unchanged":
        return
    if kind.startswith("simd:"):
        open(p, "w").write(src + "\n" + SIMD[kind[5:]])
        return
    if kind == "wrong_end":
        src = rename(src, "search")
        src += ("\nint rx_search(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*c)[2])\n"
                "{ int r = rx_search_real(s, n, f, c); if (r == 1 && c && c[0][1] > c[0][0]) c[0][1]--; return r; }\n")
    elif kind == "wrong_cap":
        src = rename(src, "match_caps")
        src += ("\nptrdiff_t rx_match_caps(const rx_ctx *ctx, ptrdiff_t (*c)[2])\n"
                "{ ptrdiff_t r = rx_match_caps_real(ctx, c); if (r >= 0 && c && RX_NCAPS > 1 && c[1][0] >= 0) c[1][0]++; return r; }\n")
    elif kind == "slow":
        src = rename(src, "search")
        src += ("\nint rx_search(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*c)[2])\n"
                "{ int r = rx_search_real(s, n, f, c); for (volatile int i = 0; i < 400; i++) ; return r; }\n")
    else:
        sys.exit("unknown kind " + kind)
    open(p, "w").write(src)


main()
