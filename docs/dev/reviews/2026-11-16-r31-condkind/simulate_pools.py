import re, itertools
D = '0123456789'
def row(cols, passes=None): return {'cols': cols, 'passes': passes}
# whole-value parsers: subject -> row or None.  Written per regex (PCRE's one reading).
def pA(s):   # /a(?<h>\d)|b(?<k>\d)|c/
    m = re.fullmatch(r'a(?P<h>\d)|b(?P<k>\d)|c', s)
    return row({'h': m['h'], 'k': m['k']}) if m else None
POOL_A = ['a'+d for d in D] + ['b'+d for d in D] + ['c']
def pAB(s):  # /(?<a>\d)?-(?<b>\d)/
    m = re.fullmatch(r'(?P<a>\d)?-(?P<b>\d)', s)
    return row({'a': m['a'], 'b': m['b']}) if m else None
POOL_AB = [a+'-'+b for a in D for b in D] + ['-'+b for b in D]
def pRZ(s):  # /(?<k>\d)(?:;(?<h>\d))*/
    m = re.fullmatch(r'(\d)((?:;\d)*)', s)
    if not m: return None
    return row({'k': m[1]}, [{'h': x} for x in m[2].split(';')[1:]])
POOL_RZ = [k + ''.join(';'+h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
def pRZ1(s): # /(?<k>\d)(?:;(?<h>\d))?/   (upper bound 1: a COLUMN, optional-as-loop's reading)
    m = re.fullmatch(r'(?P<k>\d)(?:;(?P<h>\d))?', s)
    return row({'k': m['k'], 'h': m['h']}) if m else None
def pRZanch(s): # /(?<k>\d)(?:;(?<h>\d)$)*/  (a loop that can run at most once: nested table)
    m = re.fullmatch(r'(\d)(?:;(\d)$)*', s)
    if not m: return None
    return row({'k': m[1]}, [] if m[2] is None else [{'h': m[2]}])
def pT2(s):  # /(?<h>\d{1,2})(?::(?<m>\d\d))?/
    m = re.fullmatch(r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?', s)
    return row({'h': m['h'], 'm': m['m']}) if m else None
H12 = list(D) + [a+b for a in D for b in D]
POOL_T2 = H12 + [h+':'+a+b for h in H12 for a in D for b in D]
def pJ(s):   # /(?<j>\d)(?<h>\d)?(?<k>\d)/
    m = re.fullmatch(r'(?P<j>\d)(?P<h>\d)?(?P<k>\d)', s)
    return row({'j': m['j'], 'h': m['h'], 'k': m['k']}) if m else None
POOL_J = [a+b for a in D for b in D] + [a+b+c for a in D for b in D for c in D]
def pLST(s): # /(?:(?<h>\d)(?::(?<m>\d))?,)*/
    if not re.fullmatch(r'(?:\d(?::\d)?,)*', s): return None
    ps = []
    for it in s.split(',')[:-1]:
        h, _, mm = it.partition(':'); ps.append({'h': h, 'm': mm if _ else None})
    return row({}, ps)
# occurrences(/(?<g>a)?b/): hits by finditer, a nested table of hits
def pOCC(s):
    return row({}, [{'g': m['g']} for m in re.finditer(r'(?P<g>a)?b', s)])
POOL_OCC = [''.join(t) for n in range(7) for t in itertools.product('ab', repeat=n)]
# SEARCHED mode (rev 22 s4.2/D196 read as: some span whose whole-value parse passes)
def spans(s, parse):
    out = []
    for i in range(len(s)+1):
        for j in range(i, len(s)+1):
            r = parse(s[i:j])
            if r is not None: out.append(r)
    return out
