#!/usr/bin/env python3
"""lossreview/misc: 300 small synthetic subjects for T2's identity (the bench's
utf8 subjects hold few sigma matches): random strings over sigma forms, Latin-1,
CJK, emoji, newline and space, 0..40 characters.  synth_sigma.py OUTDIR"""
import random, sys
r = random.Random(7)
chars = ['Σ', 'σ', 'ς', 'a', 'é', '日', '😀', 'Ε', 'ο', '\n', ' ', 'z']
for i in range(300):
    s = ''.join(r.choice(chars) for _ in range(r.randint(0, 40)))
    open('%s/s%03d.bin' % (sys.argv[1], i), 'wb').write(s.encode())
