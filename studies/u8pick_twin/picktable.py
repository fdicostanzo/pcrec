#!/usr/bin/env python3
"""picktable.py CELLS_DIR SUBJ_DIR -- per cell and arm: the pre-check scan byte
(REQ_RUN's byte at its @idx; REQ_BYTE when no run) and the DFA prefilter's scan
byte(s), each with its total occurrence count over the seven subjects (= the
memchr STOPS an all-subject pass pays at minimum), against the literal's own
rarest byte (the oracle bound)."""
import os, re, sys
cd, sd = sys.argv[1], sys.argv[2]
S = ['t-64k', 't-256k', 't-1m', 't-64k-lat', 't-64k-cyr', 't-64k-cjk', 't-64k-asc']
data = b''.join(open('%s/%s.bin' % (sd, s), 'rb').read() for s in S)
cnt = [data.count(bytes([b])) for b in range(256)]
ARM = (('A', 'pa'), ('B', 'pb'), ('C', 'pc'))
print('cell\toracle_rarest(byte:stops)\tarm\tprecheck(byte:stops)\tprefilter_memchr(byte:stops ...)')
for c in sorted(os.listdir(cd)):
    t0 = open(os.path.join(cd, c, 'pb.c'), errors='replace').read()
    lit = None
    m = re.search(r'Pattern: (.*) \*/', open(os.path.join(cd, c, 'pb.h'), errors='replace').read())
    pat = m.group(1)
    lit = bytes(int(x, 16) if x else 0 for x in []) or None
    raw = re.sub(r'\\x([0-9a-f]{2})', lambda m: chr(int(m.group(1), 16)), pat).strip('^$')
    lb = raw.encode('latin-1')
    best = min(set(lb), key=lambda b: cnt[b])
    for a, p in ARM:
        t = open(os.path.join(cd, c, p + '.c'), errors='replace').read()
        rr = re.search(r'#define %s_REQ_RUN "([0-9a-f]*)@(\d+)"' % p.upper(), t)
        rb = re.search(r'#define %s_REQ_BYTE "(\d+)"' % p.upper(), t)
        if rr:
            h, i = rr.group(1), int(rr.group(2)); b = bytes.fromhex(h)[i] if i < len(h) // 2 else None
            pre = '%02x:%d' % (b, cnt[b]) if b is not None else '?'
        elif rb and rb.group(1) != 'none':
            b = int(rb.group(1)); pre = '%02x:%d' % (b, cnt[b])
        else: pre = '-'
        mc = []
        for m in re.finditer(r'memchr\(subject \+ [a-z_]+(?: \+ \d+)?, (\d+),', t):
            b = int(m.group(1)); mc.append('%02x:%d' % (b, cnt[b]))
        print('\t'.join([c, '%02x:%d' % (best, cnt[best]), a, pre, ' '.join(mc)]))
