# 2026-11-27: the owner's proposal "skipping steps in a path is available when there is exactly one path possible
# from the start to any end label visible from that start": a census of every printed program's dotted reads by
# how predfix111's walker (WALK111, the label-kind table) resolves them today. Prints; asserts nothing.
import io, contextlib, collections, sys
M = 'docs/dev/lanes/predfix111_evidence/predfix111_model.py'
buf = io.StringIO(); ns = {'__name__': '__main__', '__file__': M}
sys.argv = [M]
try:
    with contextlib.redirect_stdout(buf): exec(compile(open(M).read(), M, 'exec'), ns)
except SystemExit: pass
except FileNotFoundError as x: print("model stopped late (its scratch dir, after the sweep):", x)
print('model last line:', buf.getvalue().strip().splitlines()[-1])
keys = list(ns['NEW_T111'].keys())
print('printed programs (keys):', len(keys), '| a key looks like:', repr(keys[0])[:200])
c = collections.Counter(); ex = collections.defaultdict(list)
for k in keys:
    e = k[0]; b = ['%s := %s' % (x[0], x[1]) for x in k[1]]
    for path, _, _ in ns['reads_of'](e):
        if len(path) < 2: continue
        try: v = ns['walk_v'](e, b, '.'.join(path))
        except Exception as x: v = ('crash', type(x).__name__)
        how = v[3] if v[0] == 'legal' else v[0]
        c[how] += 1
        if len(ex[how]) < 12: ex[how].append('%s  [%s]  %s' % ('.'.join(path), e[:90], '; '.join(b)[:120]))
for h, n in c.most_common():
    print(n, h); [print('     ', x) for x in ex[h]]
