import re, sys
# For quotes found in the record, check that a nearby cited box-clock time names the entry that holds the quote.
rev = open(sys.argv[1]).read().split('\n')
recl = open(sys.argv[2]).read().split('\n')
PH = '\x01'


def norm(s):
    s = s.replace('\\"', '"').replace(PH, '"').replace('`', '')
    return re.sub(r'\s+', ' ', s).strip()


# record entries from line 1474 on, keyed by box clock in heading
entries = []
cur = None
for i, l in enumerate(recl, 1):
    m = re.match(r'\*\*2026-11-1[56] .*?box clock (\d\d:\d\d)', l)
    if l.startswith('**2026-11-'):
        t = m.group(1) if m else None
        if not t:
            m2 = re.search(r'box clock (\d\d:\d\d)', l + ' ' + (recl[i] if i < len(recl) else ''))
            t = m2.group(1) if m2 else '?'
        cur = [t, i, []]
        entries.append(cur)
    if cur:
        cur[2].append(l)
ents = [(t, ln, norm('\n'.join(b))) for t, ln, b in entries]
ranges = [(360, 1019), (1020, 1769), (1884, 1949), (2548, 2857), (3490, 3726), (4559, 5779)]
for a, b in ranges:
    units, cur = [], []
    for i in range(a, b + 1):
        l = rev[i - 1]
        if l.startswith('|'):
            if cur: units.append(cur); cur = []
            units.append([(i, l)])
        elif not l.strip():
            if cur: units.append(cur); cur = []
        else:
            cur.append((i, l))
    if cur: units.append(cur)
    for u in units:
        text = '\n'.join(l for _, l in u).replace('\\"', PH)
        for m in re.finditer(r'"([^"]*)"', text):
            q = norm(m.group(1))
            if len(q.split()) < 3:
                continue
            holders = [t for t, ln, e in ents if q in e]
            if not holders:
                continue
            ctx = text[max(0, m.start() - 110):m.start()]
            times = re.findall(r'(\d\d:\d\d)', ctx)
            if not times:
                continue
            near = times[-1]
            ln = u[0][0] + text[:m.start()].count('\n')
            flag = 'OK' if near in holders else 'TIME?'
            if flag != 'OK' or '-v' in sys.argv:
                print(f'{ln}\t{flag}\tcited {near}\tin {holders}\t{q[:120]}')
