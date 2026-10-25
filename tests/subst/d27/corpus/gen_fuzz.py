#!/usr/bin/env python3
"""Seeded random differential family 'fz': small patterns from a grammar,
templates over the groups each pattern declares, short subjects.
usage: gen_fuzz.py [N] [SEED]  -> d_fz.tsv beside this file."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from esc import esc  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 160
rnd = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 27)


class P:
    def __init__(self):
        self.ng = 0
        self.names = []


def atom(p, d):
    r = rnd.random()
    if d > 2 or r < 0.45:
        return rnd.choice(['a', 'b', 'c', '.', '[ab]', '[^a]', 'x', r'\n', r'\w', r'\d', '\\b', '^', '$'])
    if r < 0.65:
        p.ng += 1
        return '(' + alt(p, d + 1) + ')'
    if r < 0.75:
        p.ng += 1
        nm = rnd.choice(['n', 'm', 'nn', 'k1'])
        p.names.append(nm)
        return '(?<%s>' % nm + alt(p, d + 1) + ')'
    if r < 0.85:
        return '(?:' + alt(p, d + 1) + ')'
    if r < 0.92:
        return '(?=' + alt(p, d + 1) + ')'
    return '(?<=' + rnd.choice(['a', 'b', 'ab', '^', 'a|bc']) + ')'


def piece(p, d):
    a = atom(p, d)
    if a in ('^', '$', '\\b') or a.startswith('(?=') or a.startswith('(?<='):
        return a
    return a + rnd.choice(['', '', '', '*', '+', '?', '*?', '+?', '??', '{0,2}', '{2}'])


def seq(p, d):
    return ''.join(piece(p, d) for _ in range(rnd.randint(0 if d else 1, 3)))


def alt(p, d):
    return '|'.join(seq(p, d) for _ in range(rnd.choice([1, 1, 1, 2, 3])))


rows = []
seen = set()
while len(rows) < N:
    p = P()
    pat = alt(p, 0)
    names = sorted(set(p.names))
    if len(p.names) != len(names):
        pat = '(?J)' + pat
    if (pat, 0) in seen:
        continue
    seen.add((pat, 0))
    for _ in range(2):
        parts = []
        for _ in range(rnd.randint(1, 5)):
            r = rnd.random()
            if r < 0.3:
                parts.append(rnd.choice(['<', '>', '|', '-', '\\', '{', '}', 'Q']))
            elif r < 0.45:
                parts.append(rnd.choice(['$0', '${0}', '$$']))
            elif r < 0.8 and p.ng:
                k = rnd.randint(1, p.ng)
                parts.append(rnd.choice(['$%d' % k, '${%d}' % k]))
            elif names:
                nm = rnd.choice(names)
                parts.append(rnd.choice(['${%s}' % nm, '$%s|' % nm]))
            else:
                parts.append('$0')
        tpl = ''.join(parts)
        subj = ''.join(rnd.choice('aabbcx\n1') for _ in range(rnd.randint(0, 12)))
        rows.append((rnd.choice(['', '', '', '-i', '--engine=vm']), pat, tpl, rnd.choice(['empty', 'empty', 'error']),
                     rnd.choice(['all', 'all', '1', '2', '3']), subj))

D = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(D, 'd_fz.tsv'), 'w') as h:
    h.write('# seeded random family (gen_fuzz.py %d)\n' % N)
    for i, (fl, pat, tpl, un, lim, subj) in enumerate(rows):
        h.write('\t'.join(['fz-%03d' % i, 'fz', fl, esc(pat.encode()), esc(tpl.encode()), un, lim,
                           esc(subj.encode()), 'diff']) + '\n')
print('fz', len(rows))
