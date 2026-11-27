import re
# /(?<h>\d)?x/ with one entry on h, S := <5 ; the four entry cells
P = re.compile(r'(?P<h>\d)?x')
S = lambda v: int(v) < 5
cells = {
 '(h: <5)   present and in':      lambda h: h is not None and S(h),
 '(h ?: <5) absent or in':        lambda h: h is None or S(h),
 '(h ! <5)  present and outside': lambda h: h is not None and not S(h),
 '(h ?! <5) absent or outside':   lambda h: h is None or not S(h),
}
def at(s, i, f, whole=False):
    # PCRE order: the optional group taken first, then skipped
    for pat in (r'(?P<h>\d)x', r'(?P<h>)x'):
        m = re.compile(pat).match(s, i)
        if m:
            h = m.group('h') or None
            if f(h) and (not whole or m.end() == len(s)): return m
def findall(s, f):
    out, i = [], 0
    while i < len(s):
        m = at(s, i, f)
        if m: out.append((m.group(), i)); i = m.end()
        else: i += 1
    return out
subj = '7x 3x x'
for n, f in cells.items():
    print(n, '| WHOLE', ' '.join(f"{w} {'HOLDS' if at(w,0,f,True) else 'FAILS'}" for w in ['x','3x','7x']),
          '| SEARCHED', (findall(subj, f) or [None])[0], '| FIND-ALL', findall(subj, f))
