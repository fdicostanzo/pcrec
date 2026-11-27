import re, itertools
# model: A := \d+ ; paths at a start in PCRE order (greedy: longest first); a filter judges the stretch whole
def paths(s, i):
    j = i
    while j < len(s) and s[j].isdigit(): j += 1
    return [s[i:k] for k in range(j, i, -1)]
def fm(p): return lambda t: re.fullmatch(p, t) is not None
B, C = fm(r'7\d*'), fm(r'\d*3')
forms = {
 'A & !B & !C':        lambda t: (not B(t)) and (not C(t)),
 'A &! (B | C)':       lambda t: not (B(t) or C(t)),
 'A & !(0:B) & !(0:C)':lambda t: (not B(t)) and (not C(t)),   # same sentence, the condition spelling
 'A & (C | !B)':       lambda t: C(t) or not B(t),
 'A &! (B &! C)':      lambda t: not (B(t) and not C(t)),
}
def first(s, i, f):
    for t in paths(s, i):
        if f(t): return t
def whole(s, f): return 'HOLDS' if any(t == s and f(t) for t in paths(s, 0)) else 'FAILS'
def findall(s, f):
    out, i = [], 0
    while i < len(s):
        t = first(s, i, f)
        if t: out.append((t, i)); i += len(t)
        else: i += 1
    return out
subj = '7 73 37 77 12 713'
for n, f in forms.items():
    print(n, '| WHOLE', ' '.join(f'{w} {whole(w, f)}' for w in ['12', '7', '73', '713']),
          '| SEARCHED', (findall(subj, f) or [None])[0], '| FIND-ALL', findall(subj, f))
# exhaustive: every subject over {1,3,7,space} up to length 6
def diff(a, b):
    n = d = 0
    for L in range(0, 7):
        for tup in itertools.product('137 ', repeat=L):
            s = ''.join(tup); n += 1
            if findall(s, forms[a]) != findall(s, forms[b]) or whole(s, forms[a]) != whole(s, forms[b]): d += 1
    return f'{a}  against  {b}: {d} of {n} differ'
print(diff('A & !B & !C', 'A &! (B | C)'))
print(diff('A & (C | !B)', 'A &! (B &! C)'))
print(diff('A & !B & !C', 'A & (C | !B)'))
