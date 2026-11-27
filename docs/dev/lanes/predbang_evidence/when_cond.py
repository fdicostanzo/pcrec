import re, itertools
# A := \d (the test), B := \d\d (then), C := \w (else)
forms = {
 "today, bare test  when(A, B, C)            AB|(?!A)C":            r'\d\d\d|(?!\d)\w',
 "his form, 0 = A's stretch  A & when((0: A), B, C)  = A & B":      r'(?=(\d))(?=\d\d(?<=\1))(?!)|(?=\d\d\Z)(?!)\d' ,  # placeholder, replaced below
 "label + condition  [t = A]? SEQ when((t ?: nothing-fails), B, C)   (?<t>A)?(?(t)B|C)": r'(?P<t>\d)?(?(t)\d\d|\w)',
 "the same, possessive optional   (?<t>A)?+(?(t)B|C)":              r'(?P<t>\d)?+(?(t)\d\d|\w)',
 "plain alternation  (A SEQ B) | C":                                r'\d\d\d|\w',
}
def his(s, i, whole=False):
    # A & when((0: A), B, C), 0 read as A's stretch: A matches a stretch; the test (stretch in A) holds on every
    # such stretch; so then must match the same stretch whole
    m = re.compile(r'\d').match(s, i)
    if m and re.fullmatch(r'\d\d', m.group()) and (not whole or m.end() == len(s)): return m
def run(name, pat):
    if name.startswith('his'):
        at = his
    else:
        c = re.compile(pat)
        def at(s, i, whole=False):
            if whole: return c.fullmatch(s) if i == 0 else None
            return c.match(s, i)
    def findall(s):
        out, i = [], 0
        while i < len(s):
            m = at(s, i)
            if m and m.end() > i: out.append((m.group(), i)); i = m.end()
            else: i += 1
        return out
    return at, findall
res = {}
subj = '12 x 123 1x 7'
for n, p in forms.items():
    at, fa = run(n, p); res[n] = (at, fa)
    print(n, '\n    WHOLE', ' '.join(f"{w} {'HOLDS' if at(w,0,True) else 'FAILS'}" for w in ['12','123','x','1x']),
          '| SEARCHED x123', (fa('x123') or [None])[0], '| FIND-ALL', subj, fa(subj))
names = list(forms)
def diff(a, b):
    n = d = 0; ex = None
    for L in range(0, 7):
        for tup in itertools.product('1x ', repeat=L):
            s = ''.join(tup); n += 1
            A, B = res[a], res[b]
            if A[1](s) != B[1](s) or bool(A[0](s,0,True)) != bool(B[0](s,0,True)):
                d += 1; ex = ex or s
    return f'{d} of {n} differ' + (f' (first: {ex!r})' if ex else '')
for b in names[1:]:
    print('today  against ', b.split('  ')[0], ':', diff(names[0], b))
