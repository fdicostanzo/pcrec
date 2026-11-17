import re
# own evaluator for V3 (when) on t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/, written from the note's text
T2 = re.compile(r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?')
D = '0123456789'
H12 = list(D) + [a + b for a in D for b in D]
POOL = H12 + [h + ':' + a + b for h in H12 for a in D for b in D]
assert len(POOL) == 11110
def rows(s, searched):
    if not searched:
        m = T2.fullmatch(s); return [m.groupdict()] if m else []
    out = []
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            m = T2.fullmatch(s[i:j])
            if m: out.append(m.groupdict())
    return out
def late(r):   # ((h, m): padded(>= (9, 30))): any NULL -> UNKNOWN (None)
    if r['h'] is None or r['m'] is None: return None
    return (int(r['h']), int(r['m'])) >= (9, 30)
def p(r):      # (m: <45)
    return None if r['m'] is None else int(r['m']) < 45
for searched in (False, True):
    body = cw = 0; first = None
    for s in POOL:
        rs = rows(s, searched)
        a = any(late(r) is True and p(r) is True for r in rs)            # x & c & p
        b = bool(rs) and not any(late(r) is True for r in rs)            # x & !(x & c), per SUBJECT (S1)
        B = a or b
        C = any((late(r) is True and p(r) is True) or late(r) is not True for r in rs)  # per-row case-when
        body += B; cw += C
        if B != C and first is None: first = s
    print('searched' if searched else 'whole', 'body', body, 'case-when', cw, 'differ', abs(body - cw), 'first', first)
# MODEL-4 hand case, x = /(?<d>\d)/ searched on '1 7', c = (d: <5), p = (d: "0")
rs = [{'d': ch} for ch in '1 7' if ch.isdigit()]
c = lambda r: int(r['d']) < 5; pp = lambda r: r['d'] == '0'
body = any(c(r) and pp(r) for r in rs) or (bool(rs) and not any(c(r) for r in rs))
cw = any((c(r) and pp(r)) or not c(r) for r in rs)
print('MODEL-4 `1 7`: body', body, 'case-when', cw)
