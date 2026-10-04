import sys, io, contextlib, re, itertools
src = open(sys.argv[1]).read().replace('\nmain()\n', '\n')
sys.argv = ['x', '/Users/fdicostanzo/pcrec/worktrees/findb4', 'subj', 'linux']
g = {}; exec(compile(src, 'm', 'exec'), g)
def decisions():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): g['main']()
    out = {}; cell = None
    for ln in buf.getvalue().splitlines():
        m = re.match(r'== (\S+)', ln)
        if m: cell = m.group(1); continue
        m = re.match(r'  (\w+) .*M=0: .* -> (\S+)\s+\| M=occ', ln)
        if m: out[(cell, m.group(1))] = m.group(2)
    return out
base = decisions(); E0 = dict(g['E']); C0 = dict(g['CST'])
print('base decisions:', len(base))
for kf, ks, kb, ke in itertools.product((0.5, 2), (0.5, 2), (0.5, 2), (0.5, 2)):
    g['CST'].update(f=C0['f']*kf, s=C0['s']*ks, beta=C0['beta']*kb)
    for k in E0: g['E'][k] = E0[k]*ke
    d = decisions(); flips = [k for k in base if d[k] != base[k]]
    print('f x%-3s s x%-3s beta x%-3s E x%-3s flips %2d %s' % (kf, ks, kb, ke, len(flips), ' '.join('%s/%s:%s->%s' % (c, s_, base[(c, s_)], d[(c, s_)]) for c, s_ in flips)))
