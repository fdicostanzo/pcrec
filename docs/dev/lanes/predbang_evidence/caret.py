import re, itertools
# when(T, B, C) := T SEQ B | ^!T SEQ C ; A := \d, B := \d\d, C := \w
pairs = [
 ("when(^A, B, C): (?=A)B|(?!(?=A))C  against  (?=A)B|(?!A)C", r'(?=\d)\d\d|(?!(?=\d))\w', r'(?=\d)\d\d|(?!\d)\w'),
 ("when(^!A, B, C): (?!A)B|(?!(?!A))C  against  (?!A)B|(?=A)C", r'(?!\d)\w\w|(?!(?!\d))\w', r'(?!\d)\w\w|(?=\d)\w'),
]
def fa(c, s):
    out, i = [], 0
    while i < len(s):
        m = c.match(s, i)
        if m and m.end() > i: out.append((m.group(), i)); i = m.end()
        else: i += 1
    return out
subj = '12 x 123 1x xy'
for n, p, q in pairs:
    a, b = re.compile(p), re.compile(q)
    print(n); print('    WHOLE', ' '.join(f"{w} {'HOLDS' if a.fullmatch(w) else 'FAILS'}" for w in ['12','1','x','xy']), '| SEARCHED', subj, (fa(a,subj) or [None])[0], '| FIND-ALL', fa(a, subj))
    t = d = 0
    for L in range(0, 7):
        for tup in itertools.product('1x ', repeat=L):
            s = ''.join(tup); t += 1
            if fa(a, s) != fa(b, s) or bool(a.fullmatch(s)) != bool(b.fullmatch(s)): d += 1
    print(f'    {d} of {t} differ')
