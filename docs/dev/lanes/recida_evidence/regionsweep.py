#!/usr/bin/env python3
"""regionsweep.py PATFILE OUTPREFIX BASEBIN[,BASEBIN...] [pcrec args...]   (lane recida, [RECID-A])

For every pattern in PATFILE compare the program region ('    goto rx_L0;' .. 'rx_accept:', the gate's
own extraction, -fcomments on both sides) of THIS tree's build/pcrec with each BASEBIN (a pcrec built
from some commit: archive + the Makefile's source list). Prints `<base> same N diff M` and writes the
differing patterns to OUTPREFIX.<basename>. Emission only: no gcc, one process."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
pats = [l for l in open(sys.argv[1], encoding='utf-8', errors='surrogateescape').read().split('\n') if l]
outprefix, bases, extra = sys.argv[2], sys.argv[3].split(','), sys.argv[4:]

def region(txt):
    out = []; on = False
    for l in txt.split('\n'):
        if l == '    goto rx_L0;': on = True
        if on:
            out.append(l)
            if l.startswith('rx_accept:'): break
    return out

def emit(binary, pb):
    return subprocess.run([binary, '--features', 'all', '-p', 'rx', '-fcomments'] + extra + ['-o', '-', '--pattern', pb],
                          capture_output=True).stdout.decode('utf-8', 'replace')

for base in bases:
    diff = []
    for p in pats:
        pb = p.encode('utf-8', 'surrogateescape')
        if region(emit(W + '/build/pcrec', pb)) != region(emit(base, pb)): diff.append(p)
    print(os.path.basename(base), 'same', len(pats) - len(diff), 'diff', len(diff))
    open(outprefix + '.' + os.path.basename(base), 'w', encoding='utf-8', errors='surrogateescape').write('\n'.join(diff) + ('\n' if diff else ''))
