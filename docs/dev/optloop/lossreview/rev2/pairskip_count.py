#!/usr/bin/env python3
"""pairskip_count.py ART.c SUBJ... — C2's no-clock trigger count. For a DFA artifact
whose DFA-hat start set T is `rx_start_bytes` and whose leading `\\b` shows in
`rx_forward_seed_state` (seed state 0 for a byte class = the previous byte leaves
the machine at a boundary), count the BOUNDARY-PAIR candidates
    p : T[s[p]]  and  (p == 0  or  seed_state[class(s[p-1])] == 0)
i.e. the positions where `!(T[s[p]] & NW[s[p-1]])` would STOP a pair-skip loop,
and the T-only candidates (today's skip stops). Counts only; no clock."""
import re, sys
art, subs = sys.argv[1], sys.argv[2:]
t = open(art).read()
def arr(name):
    m = re.search(r'%s\[\d+\] = \{(.*?)\};' % re.escape(name), t, re.S)
    return [int(x) for x in re.findall(r'-?\d+', m.group(1))]
T = arr('rx_start_bytes'); seed = arr('rx_forward_seed_state'); bc = arr('rx_forward_byte_class')
nw = [1 if seed[bc[b]] == 0 else 0 for b in range(256)]       # previous byte leaves a boundary
tn = sum(T); print('T size', tn, ' prev-nonboundary bytes', 256 - sum(nw), ' seed', seed)
B = Tc = Pc = 0
for f in subs:
    s = open(f, 'rb').read(); n = len(s); B += n
    tc = pc = 0
    for p in range(n):
        if T[s[p]]:
            tc += 1
            if p == 0 or nw[s[p - 1]]: pc += 1
    Tc += tc; Pc += pc
print('bytes %d  T-stops %d (%.4f/B)  boundary-pair stops %d (%.4f/B)  pair/T %.3f' % (B, Tc, Tc / B, Pc, Pc / B, Pc / Tc if Tc else 0))
print('PAIRSTOPS=%d BYTES=%d' % (Pc, B))
