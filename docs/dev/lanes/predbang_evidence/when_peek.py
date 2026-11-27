import re, itertools
a = re.compile(r'(?=\d)\d\d|(?!\d)\w')            # today: when(peek(A), B, C)
b = re.compile(r'(?P<t>(?=\d))?+(?(t)\d\d|\w)')   # [t = peek(A)]?+ SEQ when((t: anything), B, C)
def fa(c, s):
    out, i = [], 0
    while i < len(s):
        m = c.match(s, i)
        if m and m.end() > i: out.append((m.group(), i)); i = m.end()
        else: i += 1
    return out
subj = '12 x 123 1x 7'
for n, c in (('today  when(peek(A), B, C)  (?=A)B|(?!A)C', a), ('label on the peek, possessive optional, a condition as the test', b)):
    print(n, '| WHOLE', ' '.join(f"{w} {'HOLDS' if c.fullmatch(w) else 'FAILS'}" for w in ['12','1','x']), '| SEARCHED x123', (fa(c,'x123') or [None])[0], '| FIND-ALL', subj, fa(c, subj))
n = d = 0
for L in range(0, 7):
    for tup in itertools.product('1x ', repeat=L):
        s = ''.join(tup); n += 1
        if fa(a, s) != fa(b, s) or bool(a.fullmatch(s)) != bool(b.fullmatch(s)): d += 1
print(f'{d} of {n} differ')
