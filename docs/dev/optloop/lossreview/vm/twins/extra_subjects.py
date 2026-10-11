#!/usr/bin/env python3
"""lane lrvm: DISCRIMINATING extra subjects for the hand twins' answer check,
where the bench's own subjects carry few or no matches for the twinned
decision. Deterministic (seeded); written under OUTDIR as *.bin.
    python3 extra_subjects.py SET/PATTERN OUTDIR"""
import os, random, sys
sp, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
R = random.Random(20261011)
W = ('the of and a to in is it that was for on are as with his they at be this from '
     'have or by one had not but what all were when we there can an your which their').split()

def text(vocab, n, punct=' ,.;:\n\t()"\'-'):
    o = []
    while sum(map(len, o)) < n:
        o.append(R.choice(vocab)); o.append(R.choice(punct))
    return ''.join(o).encode()

subj = {}
if sp.endswith('ctx-lazy-64') or sp.split('/')[-1].startswith('ctx-'):
    kw = W + ['fail', 'abort', 'panic', 'disk', 'memory', 'socket', 'quota', 'failx', 'xabort', 'disks']
    for i in range(6):
        subj['words%d' % i] = text(kw, 4096)
    subj['letters_kw'] = b'qwertfailasdpanicdiskzx' * 50 + b' fail ' + b'y' * 70 + b' disk'
elif sp.endswith('moment-iso8601'):
    for i, s in enumerate(['2026-10-11', '2026-10-11T12:30', ' 2026-10-11T12:30:45.123+02:00',
                           '+002026-10-11', '2026-W41-6', '2026-284', '2026-10-11 12:30:45Z',
                           '20261011', '2026-10-11T12:30:45,5 Z', '2026-1-1', '    \t2026-10-11',
                           '2026-10-11x', '-2026-10-11']):
        subj['d%02d' % i] = s.encode()
elif sp.endswith('qnt-poss-quest'):
    subj['aa'] = text(W + ['aa', 'aaa', 'baab', 'aaaa', 'a'], 8192)
    subj['runs'] = b'a' * 33 + b'b' + b'aa' + b'ba' * 40 + b'aaa'
elif sp.endswith('grp-atomic-alt'):
    subj['abc'] = text(W + ['abc', 'ac', 'aac', 'abac', 'abcac', 'c', 'ab'], 8192)
elif sp.endswith('quoted-delim-match'):
    subj['q'] = text(W + ['"x"', "'y'", '"a\\"b"', "'it''s'", '"', "'", '\\"'], 8192)
    subj['head'] = b'"leading" then \'more\' and "un'
elif sp.endswith('balanced-parens-rec'):
    subj['p'] = text(W + ['(a)', '((b))', '(()', '())', '(x(y)z)', '(', ')'], 8192)
elif sp.endswith('bak-k-named'):
    subj['t'] = text(W + ['<a>x</a>', '<b>y</c>', '<em>q</em>', '</', '<', '<a></a>'], 8192)
elif sp.endswith('pwd-strength-chain'):
    al = 'abcxyzABCXYZ0123456789!@#$ \t\n_'
    for i in range(80):
        n = R.choice([4, 7, 8, 9, 12, 20, 64, 300])
        subj['p%02d' % i] = ''.join(R.choice(al) for _ in range(n)).encode()
    subj['long'] = (b'a' * 5000) + b'B1!' + (b'z' * 3000)
for k, v in subj.items():
    open(os.path.join(out, k + '.bin'), 'wb').write(v)
print(len(subj))
