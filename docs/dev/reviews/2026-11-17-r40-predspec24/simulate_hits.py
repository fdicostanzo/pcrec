import re
def hits_prog_first(t, s, envelope_greedy=True):
    # hits(r) & some(n<100) & occurs.none(NOT n<100) with an unstated envelope: stretch t[s:e], e from longest
    ends = range(len(t), s-1, -1) if envelope_greedy else range(s, len(t)+1)
    for e in ends:
        h = re.findall(r'\d+', t[s:e])
        if h and all(int(x) < 100 and re.fullmatch(r'0|[1-9]\d*', x) for x in h):
            return t[s:e], s, h
    return None
def searched(t):
    for s in range(len(t)+1):
        r = hits_prog_first(t, s)
        if r: return r
print('SEARCHED x300 12 :', searched('x300 12'), '; subject committed hits:', re.findall(r'\d+', 'x300 12'))
print('SEARCHED 111 :', searched('111'), '; subject committed hits:', re.findall(r'\d+', '111'))
