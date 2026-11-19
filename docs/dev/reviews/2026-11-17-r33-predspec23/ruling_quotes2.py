import re, sys
rev = open(sys.argv[1]).read().split('\n')
rec = open(sys.argv[2]).read()
PH = '\x01'


def norm(s):
    s = s.replace('\\"', '"').replace(PH, '"')
    s = s.replace('`', '')
    return re.sub(r'\s+', ' ', s).strip()


recn = norm(rec)
ranges = [(360, 1019), (1020, 1769), (1884, 1949), (2548, 2857), (3490, 3726), (4559, 5779)]
odd = 0
for a, b in ranges:
    # paragraphs: table rows are their own units; others joined by blank lines
    units = []
    cur = []
    for i in range(a, b + 1):
        l = rev[i - 1]
        if l.startswith('|'):
            if cur:
                units.append(cur)
                cur = []
            units.append([(i, l)])
        elif not l.strip():
            if cur:
                units.append(cur)
                cur = []
        else:
            cur.append((i, l))
    if cur:
        units.append(cur)
    for u in units:
        text = '\n'.join(l for _, l in u).replace('\\"', PH)
        if text.count('"') % 2:
            odd += 1
            print(f'{u[0][0]}\tODD-QUOTES')
        for m in re.finditer(r'"([^"]*)"', text):
            q = norm(m.group(1))
            if len(q.split()) < 3:
                continue
            ln = u[0][0] + text[:m.start()].count('\n')
            ctx = norm(text[max(0, m.start() - 120):m.start()])
            if q in recn:
                st = 'OK'
            else:
                parts = [p.strip(' .') for p in re.split(r'\.\.\.|…', q) if len(p.strip()) > 6]
                st = 'OK-ELLIPSIS' if parts and all(norm(p) in recn for p in parts) else 'MISS'
            if st == 'MISS' or '-v' in sys.argv:
                print(f'{ln}\t{st}\t{q[:240]}\t<<{ctx[-90:]}')
