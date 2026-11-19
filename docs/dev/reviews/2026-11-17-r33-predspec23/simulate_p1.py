import sys; sys.path.insert(0, '.')
from ev import *
t2 = Pat(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
R = lambda h, m: (int(h), int(m)) >= (9, 30)
late = joint(['h', 'm'], {}, R)
q = Prog(t2, ('c', late))
def show(name, prog, texts):
    for x in texts: print(' ', name, 'on', repr(x), fmt(*prog.both(x)))
show('D1 t2&!q', Prog(t2, ('diff', q)), ['9:15', '9:30', '9:30 1'])
show('D10 /a/&/b/', Prog('a', ('and', Prog('b'))), ['ab'])
show('D11 t2&contains(t2&!q)', Prog(t2, ('contains', Prog(t2, ('diff', q)))), ['9:30'])
A = Pat(r"a(?<h>\d)|b(?<k>\d)|c")
show('D12', Prog(A, ('c', test('h', S('<', 5), '0')), ('c', test('k', S('<', 5)))), ['a3', 'b3', 'c'])
show('D13', Prog(A, ('c', test('h', S('<', 5))), ('c', test('k', S('<', 5)))), ['b3'])
show('D2', Prog(r"\d+", ('diff', Prog('0+'))), ['0', '0 7'])
show('D3 NOT late', Prog(t2, ('c', NOT(late))), ['9', '9:15', '9:30'])
show('D4 !R', Prog(t2, ('c', joint(['h', 'm'], {}, lambda h, m: not R(h, m)))), ['9', '9:15', '9:30'])
show('D5 !contains', Prog(t2, ('ncontains', q)), ['9:15', '9:30', '9:30 1'])
show('D6 text.none', Prog(t2, ('textnone', q)), ['9:15', '9:30', '9:30 1'])
AB = Pat(r"(?:(?<a>\d)?\/)(?<b>\d)")
def gt_dollar_a(row):   # (b: >$a), $a real label
    a = row.val('a'); b = row.val('b')
    if a is None or b is None: return U
    return T if int(b) > int(a) else F
gt_dollar_a.names = ['b']
rec = AND(test('a', S('<', 10), '0'), gt_dollar_a)
show('D7 record', Prog(AB, ('c', rec)), ['/5', '2/5', 'x/5'])
jt = joint(['a', 'b'], {'a': '0'}, lambda a, b: int(a) < 10 and int(b) > int(a))
show('D8 joint', Prog(AB, ('c', jt)), ['/5', '2/5', 'x/5'])
X = Pat(r"(?<h>\d)?x")
show('D9 two defaults', Prog(X, ('c', test('h', S('<', 5), '0')), ('c', test('h', S('>', 7), '9'))), ['3x', 'a x', 'x'])
