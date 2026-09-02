#!/usr/bin/env python3
"""TWIN V -- ALWAYS-INLINE THE VM ENTRY CHAIN.

Clang inlines `rx_search` -> `rx_search_run` -> `rx_match_anchored` (and the
run-state helpers) into one function, and having done so proves the whole
`rx_run_state` / `rx_run_buffers` working storage dead on a frameless
artifact and deletes it.  gcc 15 at -O2 stops at the first call boundary:
`rx_search` materialises a 152-byte frame, initialises the storage binding,
pays a `-fstack-protector-strong` canary (Ubuntu's default; the arrays in the
frame are what trigger it) and CALLs `rx_search_run` out of line -- on every
search attempt, for storage the program never touches.

The spelling is an attribute on the emitted static helpers.  It is one
emitter site (`src/gen/emit_vm.c`'s function headers) and it is not
gcc-specific: clang already does this, so the attribute only constrains the
compiler that was not doing it.
"""
import re, sys
src = open(sys.argv[1]).read()
AI = '__attribute__((always_inline)) '
# gcc REFUSES always_inline on a function containing a computed goto (hard
# error, not a warning).  The matcher has one exactly when the artifact
# pushes a resume frame -- which is the SAME predicate the emitter already
# evaluates to decide whether to emit the pop-and-resume dispatch at all
# ([CC-CLANG]'s `has_push`, src/gen/emit_vm.c).  So the attribute rides a
# stamp pcrec already computes; it is not a new condition.
frameless = 'goto *' not in src
# Every emitted static helper EXCEPT the matcher: none of these can hold a
# computed goto, so the attribute is always legal, and this is exactly the
# set clang inlines on a framed artifact (measured: `rx_search_run` has no
# symbol in a clang build of bench/loglines `stack-frame`, `rx_match_anchored`
# does).  The matcher joins them only when the artifact is frameless.
fns = ['rx_run_state_bind', 'rx_run_state_init', 'rx_reset_for_next_attempt',
       'rx_report_captures', 'rx_search_run', 'rx_match_run',
       'rx_match_caps_run']
if frameless:
    fns += ['rx_match_anchored']
n = 0
for f in fns:
    pat = re.compile(r'^static (\w[\w ]*?) ' + f + r'\(', re.M)
    src, k = pat.subn(lambda m, f=f: 'static inline ' + AI + m.group(1) + ' ' + f + '(', src)
    n += k
open(sys.argv[2], 'w').write(src)
print('%s: always_inline applied to %d helpers' % ('FRAMELESS' if frameless else 'has-computed-goto', n))
