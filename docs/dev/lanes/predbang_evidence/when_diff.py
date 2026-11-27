import re, itertools
# when(A, B, C): today AB|(?!A)C  against  (A SEQ B) | (C &! A)  and  (A SEQ B) | (C &! (A SEQ anything))
def mk(A, B, C):
    cA, cAB, cC = re.compile(A), re.compile(A + B), re.compile(C)
    today = re.compile(f'(?:{A})(?:{B})|(?!{A})(?:{C})')
    def t_at(s, i, whole=False):
        return today.fullmatch(s) if whole else today.match(s, i)
    def cpaths(s, i):
        # C's paths at i in PCRE order, as end offsets (enumerated by forcing each end)
        ends = []
        for e in range(len(s), i - 1, -1):
            if re.compile(f'(?:{C})').fullmatch(s, i, e): ends.append(e)
        return ends   # longest first: right for the greedy C used here
    def alt(filt):
        def at(s, i, whole=False):
            m = cAB.fullmatch(s) if whole else cAB.match(s, i)
            if m: return (i, m.end())
            for e in cpaths(s, i):
                if filt(s[i:e]) and (not whole or e == len(s)): return (i, e)
        return at
    d1 = alt(lambda t: not cA.fullmatch(t))            # C &! A
    d2 = alt(lambda t: not cA.match(t))                # C &! (A SEQ anything)
    t = lambda s, i, whole=False: (lambda m: (i, m.end()) if m else None)(t_at(s, i, whole))
    return {'today AB|(?!A)C': t, '(A SEQ B) | (C &! A)': d1, '(A SEQ B) | (C &! (A SEQ anything))': d2}
def fa(at, s):
    out, i = [], 0
    while i < len(s):
        m = at(s, i)
        if m and m[1] > i: out.append((s[i:m[1]], i)); i = m[1]
        else: i += 1
    return out
for A, B, C, wholes, subj in ((r'\d', r'\d\d', r'\w', ['123','x','1'], '12 x 123 1x 7'),
                              (r'\d', r'\d\d', r'\w+', ['123','1ab','ab'], '12 x 123 1x 7'),
                              (r'\d\d', r'x', r'\w', ['12x','1','x'], '12 1 12x x')):
    f = mk(A, B, C); print(f'A := {A}   B := {B}   C := {C}')
    for n, at in f.items():
        print('  ', n, '| WHOLE', ' '.join(f"{w} {'HOLDS' if at(w,0,True) else 'FAILS'}" for w in wholes), '| SEARCHED', subj, (fa(at,subj) or [None])[0], '| FIND-ALL', fa(at, subj))
    names = list(f)
    for b in names[1:]:
        t = d = 0
        for L in range(0, 7):
            for tup in itertools.product('1x ', repeat=L):
                s = ''.join(tup); t += 1
                if fa(f[names[0]], s) != fa(f[b], s) or bool(f[names[0]](s,0,True)) != bool(f[b](s,0,True)): d += 1
        print(f'   today  against  {b}: {d} of {t} differ')
