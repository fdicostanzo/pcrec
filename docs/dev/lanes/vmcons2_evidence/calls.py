import re, sys
# Print every body-buffer print call: line, function, and the concatenated
# string literals of its format (first argument after the buffer).
text = open(sys.argv[1]).read()
funcs = [l.rstrip('\n').split('\t') for l in open(sys.argv[2])]
funcs = [(f, int(a), int(b)) for f, a, b in funcs]
lines_at = [0]
for i, ch in enumerate(text):
    if ch == '\n': lines_at.append(i + 1)
import bisect
def line_of(off): return bisect.bisect_right(lines_at, off)
def fn_of(n):
    for f, a, b in funcs:
        if a <= n <= b: return f
    return '<file>'
BODY = {'b', 'v->b', 'bb', 't'}
pat = re.compile(r'\b(pcrec_sb_(?:printf|puts|putc|cmt_open|cmt_close|text|textn|row))\s*\(')
def strip_comments(s):
    return re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for m in pat.finditer(text):
    # skip if inside a comment line
    ls = text.rfind('\n', 0, m.start()) + 1
    pre = text[ls:m.start()].strip()
    if pre.startswith('*') or pre.startswith('/*') or pre.startswith('//'): continue
    # balanced parens
    i = m.end(); depth = 1; instr = False; esc = False
    while depth and i < len(text):
        c = text[i]
        if instr:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == '(': depth += 1
            elif c == ')': depth -= 1
        i += 1
    args = strip_comments(text[m.end():i - 1])
    buf = args.split(',', 1)[0].strip()
    if buf not in BODY: continue
    lits = re.findall(r'"((?:[^"\\]|\\.)*)"', args)
    fmt = ''.join(lits).replace('\\n', '⏎')
    n = line_of(m.start())
    print('%d\t%s\t%s\t%s' % (n, fn_of(n), m.group(1)[9:], fmt[:200]))
