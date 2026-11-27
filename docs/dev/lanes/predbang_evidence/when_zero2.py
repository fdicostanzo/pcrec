import re, itertools
forms = [
 ("today, bare test: when(A, B, C) is AB|(?!A)C", r'\d\d\d|(?!\d)\w'),
 ("when((0: A), A SEQ B, C), 0 the match so far (empty where the call stands first; never an A)", r'(?!)\d\d\d|\w'),
 ("when((0: A), A SEQ B, C), the test read as 'A matches from here': (?=A)AB|(?!A)C", r'(?=\d)\d\d\d|(?!\d)\w'),
]
def fa(c, s):
    out, i = [], 0
    while i < len(s):
        m = c.match(s, i)
        if m and m.end() > i: out.append((m.group(), i)); i = m.end()
        else: i += 1
    return out
subj = '12 x 123 1x 7'
cs = [(n, re.compile(p)) for n, p in forms]
for n, c in cs:
    print(n, '\n    WHOLE', ' '.join(f"{w} {'HOLDS' if c.fullmatch(w) else 'FAILS'}" for w in ['123','x','1']), '| SEARCHED 123', (fa(c,'123') or [None])[0], '| FIND-ALL', subj, fa(c, subj))
for n, c in cs[1:]:
    t = d = 0
    for L in range(0, 7):
        for tup in itertools.product('1x ', repeat=L):
            s = ''.join(tup); t += 1
            if fa(cs[0][1], s) != fa(c, s) or bool(cs[0][1].fullmatch(s)) != bool(c.fullmatch(s)): d += 1
    print('today  against ', n.split(':')[0][:60], f': {d} of {t} differ')
