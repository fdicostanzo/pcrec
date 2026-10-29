"""p1dsg2: crossover subjects with a word-length axis and a hit-succeeds arm (review r1 MEAS-3/4).
~4 MB of WLEN-byte words over a mask-email class subset; a fraction q of the words is followed by
'@ ' (a landmark hit whose suffix FAILS) or, in the succeed arm, by '@ab.cd ' (a hit that MATCHES);
the rest by ' '. Usage: python3 -I xo_subjects.py OUTDIR"""
import random, sys
cls = 'abcdefghijklmnopqrstuvwxyz0123456789._'
for wlen in (2, 8, 32):
    for arm, tail in (('fail', '@ '), ('ok', '@ab.cd ')):
        for q in (1.0, 0.5, 0.25, 0.1, 0.03, 0.01, 0.001):
            random.seed(5)
            out = []; n = 0
            while n < 4_000_000:
                w = ''.join(random.choice(cls) for _ in range(wlen))
                w += tail if random.random() < q else ' '
                out.append(w); n += len(w)
            open('%s/w%d_%s_q%g.txt' % (sys.argv[1], wlen, arm, q), 'w').write(''.join(out))
