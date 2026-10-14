#!/usr/bin/env python3
# r17b2 scratch: every 256-entry table set pcrec emits, from DENY-arm artifacts
# (byte-identical to the abi-76 reference, r17b census), corpus + bench.
# Writes find.txt (sets at a table WALK: the FIND sites the kit is asked about)
# and all.txt (every rx_*[256] table: a superset), hex of set[32], with counts.
import re, subprocess, sys, glob, os
from concurrent.futures import ThreadPoolExecutor
W, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, W + '/scripts')
import emit_sweep as es
PC = W + '/build/pcrec'
ARMS = {'byte': [], 'vm': ['--engine=vm'], 'utf8': ['-e', 'utf8'], 'utf8vm': ['-e', 'utf8', '--engine=vm'],
        'nostart': ['-fno-start-set'], 'noofs': ['-fno-offset-skip'], 'nohandoff': ['-fno-req-handoff'],
        'noreqrun': ['-fno-req-run'], 'minsize': ['--tune=min-size'], 'maxspeed': ['--tune=max-speed'],
        'comments': ['-fcomments']}
WALK = re.compile(rb'while \((\w+)( \+ 1)? < subject_length && !rx_(\w+)\[subject\[\1\]\]\) \1\+\+;')
TABLE = re.compile(rb'static const unsigned char rx_(\w+)\[256\] = \{([^}]*)\}')
def hexof(vals):
    b = bytearray(32)
    for i, v in enumerate(vals):
        if v: b[i >> 3] |= 1 << (i & 7)
    return b.hex()
def task(it):
    src, p, arm = it
    try:
        r = subprocess.run([PC, '-p', 'rx', '--features', 'all'] + ARMS[arm] + ['--memfn=no-pf-terms-mask', '-o', '-', '--pattern', p],
                           capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return src, arm, None, None
    if r.returncode: return src, arm, None, None
    a = r.stdout
    tabs = {m.group(1): hexof([int(v) for v in m.group(2).replace(b'\n', b' ').split(b',') if v.strip()]) for m in TABLE.finditer(a)}
    walks = [tabs[m.group(3)] for m in WALK.finditer(a) if m.group(3) in tabs]
    return src, arm, walks, list(tabs.values())
pats = [('corpus', p) for p in es.distinct_patterns(es.enumerate_corpus(PC, W, 30))]
for f in sorted(glob.glob('/home/pcrec/projects/pcrec-bench/bench/*/patterns/*.rx')):
    t = open(f, 'rb').read()
    if t.endswith(b'\n'): t = t[:-1]
    pats.append(('bench', t))
items = [(s, p if isinstance(p, bytes) else p.encode() if isinstance(p, str) else p, a) for s, p in pats for a in ARMS]
find, alls = {}, {}
with ThreadPoolExecutor(4) as ex:
    for src, arm, walks, tabs in ex.map(task, items):
        if walks is None: continue
        for h in walks: find.setdefault(h, set()).add(src + ':' + arm)
        for h in tabs: alls.setdefault(h, set()).add(src + ':' + arm)
for name, d in (('find', find), ('all', alls)):
    with open(os.path.join(OUT, name + '.txt'), 'w') as f:
        for h in sorted(d): f.write('%s %s\n' % (h, ','.join(sorted(d[h]))))
print('patterns', len(pats), 'find sets', len(find), 'all sets', len(alls),
      'bench-only find sets', sum(1 for h in find if all(x.startswith('bench') for x in find[h])))
