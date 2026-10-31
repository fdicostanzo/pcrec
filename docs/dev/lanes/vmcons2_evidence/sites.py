import re, sys
src = open(sys.argv[1]).read().split('\n')
funcs = []
cur = None
for n, line in enumerate(src, 1):
    if line.startswith('{') and cur is None:
        j = n - 2
        while j >= 0 and not re.match(r'^[A-Za-z_].*\(', src[j]):
            j -= 1
        m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', src[j])
        cur = [m.group(1) if m else '?', n]
    elif line.startswith('}') and cur is not None:
        funcs.append((cur[0], cur[1], n)); cur = None
def fn_of(n):
    for f, a, b in funcs:
        if a <= n <= b: return f
    return '<file>'
call = re.compile(r'\b(pcrec_sb_[a-z_]+|vm_ev)\s*\(\s*([^,)]*)')
for n, line in enumerate(src, 1):
    s = line.strip()
    if s.startswith('*') or s.startswith('/*') or s.startswith('//'): continue
    for m in call.finditer(line):
        print('%d\t%s\t%s\t%s' % (n, fn_of(n), m.group(1), m.group(2).strip()))
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as o:
        for f, a, b in funcs: o.write('%s\t%d\t%d\n' % (f, a, b))
