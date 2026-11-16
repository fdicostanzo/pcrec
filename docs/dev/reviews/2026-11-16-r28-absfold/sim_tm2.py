import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drills import *
H = lambda: G('h', Rep(D, 1, 2)); M = lambda: G('m', Seq(D, D))
T2 = Seq(H(), Rep(Seq(L(':'), M()), 0, 1))
LST = Rep(Seq(H(), Rep(Seq(L(':'), M()), 0, 1), L(',')), 0, None)
def ge(b): return lambda env: (lambda t: all(isnum(x) for x in t) and tuple(int(x) for x in t) >= b)
hs = [str(i) for i in range(10)] + ['%02d' % i for i in range(100)]
subs = [h for h in hs] + [h + ':' + '%02d' % m for h in hs for m in range(100)]
print('t2 subjects', len(subs))
forms = {'none': [('h',None,None),('m',None,None)], 'm?': [('h',None,None),('m','mark',None)],
         'm=0': [('h',None,None),('m','def','0')]}
for dom in ('ANY', 'GROUP'):
    res = {f: {} for f in forms}
    for s in subs:
        ctx = Ctx(T2, s, {'h': ANY, 'm': ANY} if dom == 'ANY' else {'h': hs, 'm': ['%02d' % i for i in range(100)]})
        for f, lab in forms.items():
            res[f][s] = joint(ctx, lab, ge((9, 30)))
    pr = lambda a, b: sum(res[a][s] != res[b][s] for s in subs)
    print(dom, 'none/m?', pr('none','m?'), 'none/m=0', pr('none','m=0'), 'm?/m=0', pr('m?','m=0'),
          [s for s in subs if res['m?'][s] != res['m=0'][s]])
    for s in ('9', '10', '11', '9:15', '9:45'):
        print('  ', s, [res[f][s] for f in forms])
lf = {'(h,m)': [('h',None,None),('m',None,None)], '(h,m?)': [('h',None,None),('m','mark',None)],
      '(h,m=0)': [('h',None,None),('m','def','0')], '(h?,m=0)': [('h','mark',None),('m','def','0')],
      '(h?,m?)': [('h','mark',None),('m','mark',None)]}
for s in ('', '10,', '9,', '9:45,', '10,9:15,'):
    ctx = Ctx(LST, s, {'h': ANY, 'm': ANY})
    print(repr(s), ''.join('H' if joint(ctx, lab, ge((9, 30))) else 'F' for lab in lf.values()))
