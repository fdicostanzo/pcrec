import re, itertools
# 2026-11-27: `~X` the complement (a set or a pattern, filter-only), `!` the logical not of a test.
# A run that prints; it asserts nothing.
ST = [None] + [str(d) for d in range(10)]          # a label's states: absent, or one digit
S = lambda v: int(v) < 5
T = lambda v: int(v) >= 3
comp = lambda f: (lambda v: not f(v))              # ~set: every text outside it
ent  = lambda f: (lambda v: v is not None and f(v))   # (a: set)   present and in
opt  = lambda f: (lambda v: v is None or f(v))        # (a ?: set) absent or in
print('1. entries, 11 states of h')
print('  (h: ~<5)  vs "present and outside":', sum(ent(comp(S))(v) != (v is not None and not S(v)) for v in ST), 'of 11 differ')
print('  (h ?: ~<5) vs "absent or outside":  ', sum(opt(comp(S))(v) != (v is None or not S(v)) for v in ST), 'of 11 differ')
print('  !(h: <5)  vs (h ?: ~<5):            ', sum((not ent(S)(v)) != opt(comp(S))(v) for v in ST), 'of 11 differ')
print('  !(h ?: <5) vs (h: ~<5):             ', sum((not opt(S)(v)) != ent(comp(S))(v) for v in ST), 'of 11 differ')
print('  !(h: <5)  vs (h: ~<5):              ', sum((not ent(S)(v)) != ent(comp(S))(v) for v in ST), 'of 11 differ (the absent state)')
def at(s, i, f, whole=False):
    for pat in (r'(?P<h>\d)x', r'(?P<h>)x'):
        m = re.compile(pat).match(s, i)
        if m and f(m.group('h') or None) and (not whole or m.end() == len(s)): return m
def fa(s, f):
    out, i = [], 0
    while i < len(s):
        m = at(s, i, f)
        if m: out.append(f'{m.group()}@{i}'); i = m.end()
        else: i += 1
    return out
for n, f in [('/(?<h>\\d)?x/ & (h: ~<5) ', ent(comp(S))), ('/(?<h>\\d)?x/ & (h ?: ~<5)', opt(comp(S))), ('/(?<h>\\d)?x/ & !(h: <5) ', lambda v: not ent(S)(v))]:
    print(' ', n, '| WHOLE', ' '.join(f"{w} {'HOLDS' if at(w,0,f,True) else 'FAILS'}" for w in ['x','3x','7x']),
          '| SEARCHED', (fa('7x 3x x', f) or [None])[0], '| FIND-ALL', fa('7x 3x x', f))
print('2. records, 121 states of (a, b), S = <5, T = >=3')
P = list(itertools.product(ST, ST))
neither = lambda a, b: ent(comp(S))(a) and ent(comp(T))(b)
print('  (a: ~S, b: ~T) vs "a present outside S and b present outside T":',
      sum(neither(a, b) != (a is not None and not S(a) and b is not None and not T(b)) for a, b in P), 'of 121 differ')
print('  (a: ~S, b: ~T) vs !(a: S, b: T):', sum(neither(a, b) != (not (ent(S)(a) and ent(T)(b))) for a, b in P), 'of 121 differ')
print('  !(a: S, b: T) vs (a ?: ~S) | (b ?: ~T):', sum((not (ent(S)(a) and ent(T)(b))) != (opt(comp(S))(a) or opt(comp(T))(b)) for a, b in P), 'of 121 differ')
print('  (a: S, b: ~T) holds in', sum(ent(S)(a) and ent(comp(T))(b) for a, b in P), 'of 121 states (5 values of a times 3 of b = 15)')
print('3. patterns: A & ~B, the stretch of A that B does not match whole')
def paths(A, s, i):                                  # A's paths at i in PCRE order (greedy first), by end
    seen = []
    for j in range(len(s), i - 1, -1):
        if re.compile(A).fullmatch(s, i, j): seen.append(j)
    return seen
def match(s, i, A, keep):
    for j in paths(A, s, i):
        if keep(s[i:j]): return j
def run(A, keep, whole, subj):
    out, i = [], 0
    while i < len(subj):
        j = match(subj, i, A, keep)
        if j is not None and j > i: out.append(f'{subj[i:j]}@{i}'); i = j
        else: i += 1
    w = ' '.join(f"{x} {'HOLDS' if match(x, 0, A, keep) == len(x) else 'FAILS'}" for x in whole)
    return f'WHOLE {w} | SEARCHED {(out or [None])[0]} | FIND-ALL {out}'
fm = lambda B: (lambda t: re.fullmatch(B, t) is not None)
nB = comp(fm(r'7\d*'))
print('  /\\d+/ & ~/7\\d*/ :', run(r'\d+', nB, ['123', '712'], '7 12 77 37'))
print('  /\\d+/ & ~/7\\d*/ & ~/\\d*2/ :', run(r'\d+', lambda t: nB(t) and comp(fm(r'\d*2'))(t), ['123', '712', '12'], '7 12 77 37'))
W = [''.join(p) for n in range(7) for p in itertools.product('71x', repeat=n)]
B, C = fm(r'7[17]*'), fm(r'[17]*1')
print('  ~B & ~C vs ~(B | C), as filters:', sum((comp(B)(w) and comp(C)(w)) != comp(lambda t: B(t) or C(t))(w) for w in W), 'of', len(W), 'strings differ')
print('  ~~B vs B, as filters:', sum(comp(comp(B))(w) != B(w) for w in W), 'of', len(W), 'strings differ')
print('  C | ~B vs ~(B & ~C), as filters:', sum((C(w) or comp(B)(w)) != comp(lambda t: B(t) and comp(C)(t))(w) for w in W), 'of', len(W), 'strings differ')
print('4. the two words part: "x" seq !^/\\d/  against  "x" seq ^~/\\d/  (a stretch ahead that is not one digit)')
d = 0
for w in W:
    for i in range(len(w)):
        if w[i] != 'x': continue
        notahead = re.compile(r'x(?![17])').match(w, i) is not None
        ahead_comp = any(not re.fullmatch(r'[17]', w[i+1:j]) for j in range(i + 1, len(w) + 1))   # some stretch ahead outside the set
        d += notahead != ahead_comp
print('  differ at', d, 'of', sum(w.count('x') for w in W), 'positions of x (the empty stretch is always outside /\\d/)')
