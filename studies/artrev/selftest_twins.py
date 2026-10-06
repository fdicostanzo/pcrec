#!/usr/bin/env python3
"""selftest_twins.py -- build the self-test's deliberately bad / slowed twins by
editing an arm dir created with `artrev.py twin NAME ARM --new`.

  selftest_twins.py ARMDIR KIND     KIND: wrong_end | wrong_cap | slow | simd:<which> | unchanged
                                          | giveup_wrong | giveup_right | giveup_lost | start_early | start_early_loop
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


def rename_static(src, fn):
    """Rename `static <type> rx_<fn>(` to rx_<fn>_real( at its definition AND every call (a static
    internal has no ABI to preserve); returns the new text."""
    if not re.search(r"\nstatic int rx_%s\(" % fn, src):
        sys.exit("no static int rx_%s in the artifact" % fn)
    return re.sub(r"\brx_%s\(" % fn, "rx_%s_real(" % fn, src)


# the `_in` entry wrapped: what a twin does when the ORIGINAL would give up (-2..-5)
GIVEUP_SRC = {
    # answers WRONG (a fabricated match) in place of a give-up: the oracle must reject it
    "giveup_wrong": "if (r <= -2 && r >= -5) { if (c) { c[0][0] = 0; c[0][1] = 1; } return 1; } return r;",
    # answers RIGHT: retries the same search with the full stamped buffers (the permitted repair)
    "giveup_right": "if (r <= -2 && r >= -5) { r = rx_search_in_real(s, n, f, c, &artrev_full); } return r;",
    # gives up where the original ANSWERS: must FAIL
    "giveup_lost": "if (r >= 0 && b && b->nframes == 1) return -3; return r;",
}


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
    elif kind in GIVEUP_SRC:
        src = rename(src, "search_in")
        pre = ""
        if kind == "giveup_right":
            pre = ("\nstatic _Alignas(64) unsigned char artrev_fr[RX_RESUME_FRAMES * RX_RESUME_FRAME_SIZE + 64];\n"
                   "static _Alignas(64) unsigned char artrev_tr[RX_TRAIL_FRAMES * RX_TRAIL_FRAME_SIZE + 64];\n"
                   "static const rx_buffers artrev_full = { artrev_fr, RX_RESUME_FRAMES, artrev_tr, RX_TRAIL_FRAMES };\n"
)
        src += pre + ("\nint rx_search_in(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*c)[2], const rx_buffers *b)\n"
                      "{ int r = rx_search_in_real(s, n, f, c, b); %s }\n" % GIVEUP_SRC[kind])
    elif kind in ("start_early", "start_early_loop"):
        # the prefilter proposes a window start one byte EARLY.  `start_early` only when that start is
        # still after search_from (the verifying attempt fails and the next prefilter call corrects it:
        # answers identical, only the window differs); `start_early_loop` unconditionally (the rvA09
        # livelock: prefilter from s returns s-1, the attempt fails, attempt+1 = s, repeat).
        src = rename_static(src, "prefilter")
        cond = "w[0][0] > (ptrdiff_t)f" if kind == "start_early" else "w[0][0] > 0"
        src += ("\nstatic int rx_prefilter(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*w)[2])\n"
                "{ int r = rx_prefilter_real(s, n, f, w); if (r == 1 && %s) w[0][0]--; return r; }\n" % cond)
    else:
        sys.exit("unknown kind " + kind)
    open(p, "w").write(src)


main()
