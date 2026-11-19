import re, sys
rev = open(sys.argv[1]).read().split('\n')
rec = open(sys.argv[2]).read()


def norm(s):
    s = s.replace('\\"', '"')
    return re.sub(r'\s+', ' ', s).strip()


recn = norm(rec)
ranges = [(360, 1019), (1020, 1769), (1884, 1949), (2548, 2857), (3490, 3726), (4559, 5779)]
for a, b in ranges:
    lines = rev[a - 1:b]
    text = '\n'.join(lines)
    starts = [0]
    for l in lines:
        starts.append(starts[-1] + len(l) + 1)
    for m in re.finditer(r'"([^"]{12,700}?)"', text, re.S):
        q = norm(m.group(1))
        if len(q.split()) < 3:
            continue
        ln = a + max(i for i, s in enumerate(starts) if s <= m.start())
        ctx = norm(text[max(0, m.start() - 200):m.start()])
        if q in recn:
            st = 'OK'
        else:
            parts = [p.strip() for p in re.split(r'\.\.\.|…', q) if len(p.strip()) > 6]
            if parts and all(norm(p) in recn for p in parts):
                st = 'OK-ELLIPSIS'
            else:
                st = 'MISS'
        if st == 'MISS' or '-v' in sys.argv:
            print(f'{ln}\t{st}\t{q[:220]}\t<<{ctx[-140:]}')
