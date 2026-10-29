"""p1dsg: the crossover sweep's subjects (crossover.txt): ~4 MB of 8-byte words over a mask-email
class subset, a fraction q of them followed by '@ ' (a landmark hit whose suffix fails), the rest by ' '.
Usage: python3 -I crossover_subjects.py OUTDIR"""
import random, sys
random.seed(5)
cls = 'abcdefghijklmnopqrstuvwxyz0123456789._'
for q in (1.0, 0.5, 0.25, 0.1, 0.03, 0.01, 0.001):
    out = []; n = 0
    while n < 4_000_000:
        w = ''.join(random.choice(cls) for _ in range(8))
        w += '@ ' if random.random() < q else ' '
        out.append(w); n += len(w)
    open('%s/q%g.txt' % (sys.argv[1], q), 'w').write(''.join(out))
