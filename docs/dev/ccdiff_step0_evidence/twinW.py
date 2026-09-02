#!/usr/bin/env python3
"""TWIN W -- ELIDE THE DEAD WORKING STORAGE ON A FRAMELESS ARTIFACT.

A more surgical alternative to twin V.  When the artifact pushes no resume
frame and trails no slot, `rx_run_buffers storage` is never read or written,
yet every un-suffixed entry declares it as a local.  Those arrays are what
make gcc's `-fstack-protector-strong` instrument the entry, and they are most
of its 152-byte frame.  Emitting the entry with a NULL/0 binding instead
removes both, and needs no inlining decision from the compiler at all.

Only legal when frameless -- exactly [CC-CLANG]'s `has_push`.
"""
import re, sys
src = open(sys.argv[1]).read()
if 'goto *' in src:
    open(sys.argv[2], 'w').write(src); print('framed: unchanged'); sys.exit()
n = 0
pat = re.compile(
    r'( *)rx_run_buffers storage;([^\n]*)\n'
    r'( *)rx_run_state_bind\(&run, storage\.frames, RX_RESUME_FRAMES,\n'
    r' *storage\.trail,  RX_TRAIL_FRAMES\);')
def sub(m):
    global n; n += 1
    i = m.group(1)
    return (i + '/* [twinW] frameless: this artifact pushes no resume frame and\n'
            + i + '   trails no slot, so the buffers are never read. Declaring them\n'
            + i + '   costs a 152-byte frame and a stack-protector canary per call. */\n'
            + i + 'rx_run_state_bind(&run, (void *)0, 0, (void *)0, 0);')
src, k = pat.subn(sub, src)
open(sys.argv[2], 'w').write(src)
print('storage elided at %d entries' % k)
