import re, itertools
a = re.compile(r'(?P<k>\d)(?:;(?P<h>\d)(?<=[0-4]))*')
b = re.compile(r'(?P<k>\d)(?:;(?P<h>[0-4]))*')
subs = [k + ''.join(';' + h for h in hs) for k in '0123456789' for n in range(3) for hs in itertools.product('0123456789', repeat=n)]
d = 0
for s in subs:
    ma, mb = a.fullmatch(s), b.fullmatch(s)
    if (ma is None) != (mb is None) or (ma and ma.groupdict() != mb.groupdict()): d += 1
print('subjects', len(subs), 'match/capture differences', d)
# (h?: 5..9, k: 3..7) on zero-pass subjects, F1, domain = the group's own regex vs any text
def dom(rx): return [t for t in [str(i) for i in range(10)] if re.fullmatch(rx, t)]
for name, grx in (('A group \\d', r'\d'), ('B group [0-4]', r'[0-4]')):
    D = dom(grx)
    hold = [k for k in '0123456789' if 3 <= int(k) <= 7 and any(5 <= int(x) <= 9 for x in D)]
    print(name, 'zero-pass subjects HOLDING under GROUP domain:', hold)
