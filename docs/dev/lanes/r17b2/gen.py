#!/usr/bin/env python3
# r17b2 scratch: the GENERATED set space (hex of set[32] per line, family tag
# second), every family with its complements. Fixed seed.
import random, sys
R = random.Random(20261012)
FULL = (1 << 256) - 1
def hx(b): return b.to_bytes(32, 'little').hex()
def cube(m, v): return sum(1 << x for x in range(256) if x & m == v & m)
def arc(l, w): return sum(1 << ((l + j) & 255) for j in range(w))
out = {}
def emit(fam, b):
    for s, f in ((b, fam), (FULL & ~b, 'not-' + fam)):
        if 0 < s < FULL: out.setdefault(s, f)
fams = sys.argv[1].split(',') if len(sys.argv) > 1 else ['all']
want = lambda f: 'all' in fams or f in fams
if want('single'):
    for x in range(256): emit('single', 1 << x)
if want('pair'):
    for a in range(256):
        for b in range(a + 1, 256): emit('pair', 1 << a | 1 << b)
CUBES = [(m, v) for m in range(256) for v in range(256) if v & ~m == 0]
if want('cube'):
    for m, v in CUBES: emit('cube', cube(m, v))
if want('range'):
    for l in range(256):
        for h in range(l, 256): emit('range', arc(l, h - l + 1))
if want('arc'):
    for l in range(256):
        for w in range(1, 256): emit('arc', arc(l, w))
if want('nearcube'):
    for _ in range(200000):
        m, v = R.choice(CUBES); s = cube(m, v) ^ (1 << R.randrange(256)); emit('near-cube', s)
def rterm():
    if R.random() < 0.5:
        m = R.randrange(256); return cube(m, R.randrange(256) & m)
    return arc(R.randrange(256), R.randrange(1, 129))
if want('union'):
    for _ in range(100000):
        s = 0
        for _ in range(R.randrange(2, 9)): s |= rterm()
        emit('union', s)
if want('g2union'):          # G2's own shape: cubes with >= 4 cared low bits, arcs <= 12
    for _ in range(100000):
        s = 0
        for _ in range(R.randrange(2, 9)):
            if R.random() < 0.5:
                m = R.randrange(256) | 0x0F; s |= cube(m, R.randrange(256) & m)
            else: s |= arc(R.randrange(256), R.randrange(1, 13))
        emit('g2union', s)
if want('scattered'):
    for _ in range(30000):
        s = 0
        for _ in range(R.randrange(3, 13)): s |= 1 << R.randrange(256)
        emit('scattered', s)
if want('near'):             # near the corpus: every FIND set, one member toggled; two, sampled
    base = [int.from_bytes(bytes.fromhex(l.split()[0]), 'little') for l in open(sys.argv[2])]
    for b in base:
        for x in range(256): emit('near1', b ^ (1 << x))
        for _ in range(200): emit('near2', b ^ (1 << R.randrange(256)) ^ (1 << R.randrange(256)))
for s, f in out.items(): print(hx(s), f)
