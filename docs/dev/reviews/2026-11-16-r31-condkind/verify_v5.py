import re, itertools
T2 = re.compile(r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?')
D = '0123456789'
H12 = list(D) + [a + b for a in D for b in D]
POOL = H12 + [h + ':' + a + b for h in H12 for a in D for b in D]
def rows(rx, s, searched):
    if not searched:
        m = rx.fullmatch(s); return [m.groupdict()] if m else []
    return [m.groupdict() for i in range(len(s)) for j in range(i + 1, len(s) + 1) for m in [rx.fullmatch(s[i:j])] if m]
def late(r):
    if r['h'] is None or r['m'] is None: return None
    return (int(r['h']), int(r['m'])) >= (9, 30)
def prog(s, searched, extra):   # q & !(q & c), q := t2 [& extra]; complement per SUBJECT (source-row)
    q = [r for r in rows(T2, s, searched) if extra(r) is True]
    return bool(q) and not any(late(r) is True for r in q)
none = lambda r: True
gt20 = lambda r: None if r['h'] is None else int(r['h']) > 20
for searched in (False, True):
    adm = [s for s in POOL if prog(s, searched, gt20) and not prog(s, searched, none)]
    print('SIMULATE-4', 'searched' if searched else 'whole', 'q & !(q & late), add (h: >20) to q: admitted', len(adm), adm[:2])
# SIMULATE-3: RZ (h = 0: <5) whole vs searched (a2: default fills the LEFT JOIN row)
RZ_RX = re.compile(r'(?P<k>\d)(?P<rest>(?:;\d)*)')
RZ = [k + ''.join(';' + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
def rz_rows(s, searched):
    spans = [s] if not searched else [s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)]
    out = []
    for t in spans:
        m = RZ_RX.fullmatch(t)
        if m: out.append([x for x in m.group('rest').split(';') if x])
    return out
def h0lt5(hs): return all(int(h) < 5 for h in (hs or ['0']))
for searched in (False, True):
    print('SIMULATE-3 RZ (h = 0: <5)', 'searched' if searched else 'whole', sum(1 for s in RZ if any(h0lt5(hs) for hs in rz_rows(s, searched))))
