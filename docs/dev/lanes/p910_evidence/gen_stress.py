import random, sys
# answer-identity stress subjects for the P9 twins: keywords, near-miss keywords,
# both context sets, random words and separators (\n included), seeded.
def gen(path, kws, ctxs, seed, n):
    r = random.Random(seed)
    near = [k[:-1] for k in kws] + ['x' + k for k in kws] + [k + 'x' for k in kws] + [k[1:] for k in kws]
    near += [c[:-1] for c in ctxs] + [c + 's' for c in ctxs]
    seps = [' ', ' ', ' ', '\n', ', ', '-', '_', '.', ':', '\t', '  ']
    alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    out = []
    size = 0
    while size < n:
        x = r.random()
        if x < 0.06: w = r.choice(kws)
        elif x < 0.12: w = r.choice(ctxs)
        elif x < 0.25: w = r.choice(near)
        else: w = ''.join(r.choice(alpha) for _ in range(r.randint(1, 12)))
        s = r.choice(seps) if r.random() < 0.97 else ''.join(r.choice(alpha) for _ in range(r.randint(50, 400)))
        out.append(w + s); size += len(w) + len(s)
    open(path, 'wb').write(''.join(out).encode())
d = sys.argv[1]
gen(d + '/stress-ctx.bin', ['fail', 'abort', 'panic'], ['disk', 'memory', 'socket', 'quota'], 1, 1 << 20)
gen(d + '/stress-lvl.bin', ['ERROR', 'FATAL', 'CRIT'], ['timeout', 'timed out', 'refused', 'denied', 'unreachable'], 2, 1 << 20)
open(d + '/edge-ctx.bin', 'wb').write(b'fail disk')
open(d + '/edge-lvl.bin', 'wb').write(b'CRIT denied')
