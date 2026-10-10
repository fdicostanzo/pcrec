#!/usr/bin/env python3
"""stamps.py CELLS_DIR -- per cell and arm: the pre-check scan (REQ_BYTE /
REQ_RUN @idx), the DFA prefilter form and offsets, and every memchr(...)
byte emitted in the artifact (hex), read off the emitted C."""
import os, re, sys
d = sys.argv[1]
ARM = (('A', 'pa', 'byte'), ('B', 'pb', 'utf8'), ('C', 'pc', 'utf8+u8prior'), ('P', 'pd', 'utf8@c4c70f2c'))
print('cell\tarm\tenc\tREQ_BYTE\tREQ_RUN\tPREFILTER\tOFFSETS\tmemchr_bytes(k:byte)')
for c in sorted(os.listdir(d)):
    for a, p, enc in ARM:
        f = os.path.join(d, c, p + '.c')
        if not os.path.exists(f): continue
        t = open(f, errors='replace').read()
        def st(n):
            m = re.search(r'#define %s_%s "?([^"\n]*)"?' % (p.upper(), n), t); return m.group(1) if m else '?'
        mc = [('%s:%02x' % (m.group(1) or '0', int(m.group(2)))) for m in
              re.finditer(r'memchr\(subject \+ [a-z_]+(?: \+ (\d+))?, (\d+),', t)]
        print('\t'.join([c, a, enc, st('REQ_BYTE'), st('REQ_RUN'), st('DFA_PREFILTER'), st('DFA_PREFILTER_OFFSETS'), ' '.join(mc)]))
