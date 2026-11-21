import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check1 import *  # noqa
out.clear()
LOOP = ('h',)
def sh(prog, x, parse):  # searched: some span passes
    return any(holds(prog, r) for r in spans(x, parse))
# D4: adding a condition through a named program used twice: `q & !(q & c)`, q := t2 [& d]
c = P(Cond([('h', None), ('m', None)], late))
for dname, d in [('(h: >20)', P(Cond([('h', None)], gt(20)))), ('(h = 0: <10)', P(Cond([('h', '0')], lt(10))))]:
    for mode in ('whole', 'searched'):
        def prog(x, extra):
            q = extra
            if mode == 'whole':
                r = pT2(x); return holds(q, r) and not holds(q + [c], r)
            return sh(q, x, pT2) and not sh(q + [c], x, pT2)
        before = set(x for x in POOL_T2 if prog(x, []))
        after = set(x for x in POOL_T2 if prog(x, [d]))
        adm = sorted(after - before, key=lambda s: (len(s), s))
        rep(f'D4 q & !(q & late), add {dname} to q, {mode}: admitted', (len(adm), adm[:3]))
# the same through when(c, p) with x := q: (x & c & p) | (x & !(x & c)), p := (m: <45)
p = P(Cond([('m', None)], lt(45)))
for mode in ('whole', 'searched'):
    def wprog(x, extra):
        if mode == 'whole':
            r = pT2(x); return holds(extra + [c, p], r) or (holds(extra, r) and not holds(extra + [c], r))
        return sh(extra + [c, p], x, pT2) or (sh(extra, x, pT2) and not sh(extra + [c], x, pT2))
    d = P(Cond([('h', None)], gt(20)))
    before = set(x for x in POOL_T2 if wprog(x, [])); after = set(x for x in POOL_T2 if wprog(x, [d]))
    adm = sorted(after - before, key=lambda s: (len(s), s))
    rep(f'D4w when(late, (m:<45)) over x := t2 [& (h:>20)], {mode}: admitted', (len(adm), adm[:3]))
# D5: two spellings of the empty set under A2 / plain / some, RZ
hRZ = lambda dd, S: Cond([('h', dd)], S, LOOP)
empt1 = lambda v, env: v.isdigit() and int(v) < 0              # `<0`, empty as written
empt2 = lambda v, env: v.isdigit() and int(v) < int(dollar(env, 'k')) and int(dollar(env, 'k')) == 0 and False  # never
emptk = lambda v, env: v.isdigit() and int(v) < int(dollar(env, 'k'))    # `<$k`: empty where k = 0
for nm, S in [('<0', empt1), ('<$k', emptk)]:
    w = [x for x in POOL_RZ if all_A2(hRZ(None, S), pRZ(x)) == T and (nm == '<0' or x[0] == '0')]
    rep(f'D5 RZ A2 all((h: {nm})) holds [where the set is empty]', (len(w), w[:3]))
print('\n'.join(out))
out.clear()
cw = Cond([('h', None), ('m', None)], late); pw = Cond([('m', None)], lt(45))
def casewhen(r):  # per row: case when c then p else true
    return (plain(cw, r) != T) or (plain(pw, r) == T)
body = set(x for x in POOL_T2 if sh([c, p], x, pT2) or (sh([], x, pT2) and not sh([c], x, pT2)))
cw_s = set(x for x in POOL_T2 if any(casewhen(r) for r in spans(x, pT2)))
cw_w = set(x for x in POOL_T2 if casewhen(pT2(x)))
body_w = set(x for x in POOL_T2 if (holds([c, p], pT2(x)) or not holds([c], pT2(x))))
d = sorted(cw_s ^ body, key=lambda s: (len(s), s))
rep('D6 when body vs case-when, whole differ', len(cw_w ^ body_w))
rep('D6 when body vs case-when, searched (body, casewhen, differ, first)', (len(body), len(cw_s), len(d), d[:3]))
print('\n'.join(out))
