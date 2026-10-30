#!/usr/bin/env python3
"""Every print call that writes a matcher body or its frame, with its FULL
format text. usage: calls3.py emit_vm.c > calls.tsv
Columns: line, function, op, buffer, format (string literals of the first
argument after the buffer, newlines as \\n; a non-literal argument as
<EXPR:...>). Body buffers: v->b and its aliases b/bb/t (rev 2's survey); the
frame: buffer c inside vm_emit_search_run_prologue."""
import re, sys
text = open(sys.argv[1]).read()
lines_at = [0] + [i + 1 for i, ch in enumerate(text) if ch == '\n']
import bisect
def line_of(off): return bisect.bisect_right(lines_at, off)
# functions: a line starting with '{' after a signature line
funcs = []
src = text.split('\n'); cur = None
for n, l in enumerate(src, 1):
    if l.startswith('{') and cur is None:
        j = n - 2
        while j >= 0 and not re.match(r'^[A-Za-z_].*\(', src[j]): j -= 1
        m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', src[j]); cur = [m.group(1) if m else '?', n]
    elif l.startswith('}') and cur is not None:
        funcs.append((cur[0], cur[1], n)); cur = None
def fn_of(n):
    for f, a, b in funcs:
        if a <= n <= b: return f
    return '<file>'
pat = re.compile(r'\b(pcrec_sb_(?:printf|puts|putc|cmt_open|cmt_close|splice|scaffold_open|scaffold_close))\s*\(')
def split_args(s):
    out, depth, instr, esc, cur = [], 0, False, False, ''
    for c in s:
        if instr:
            cur += c
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': instr = False
            continue
        if c == '"': instr = True; cur += c; continue
        if c in '([{': depth += 1
        if c in ')]}': depth -= 1
        if c == ',' and depth == 0: out.append(cur.strip()); cur = ''; continue
        cur += c
    if cur.strip(): out.append(cur.strip())
    return out
def strip_c_comments(s):
    # C comments OUTSIDE string literals only (a format may carry comment text)
    out, k, instr = [], 0, False
    while k < len(s):
        c = s[k]
        if instr:
            out.append(c)
            if c == '\\': out.append(s[k + 1]); k += 2; continue
            if c == '"': instr = False
            k += 1; continue
        if c == '"': instr = True; out.append(c); k += 1; continue
        if s.startswith('/*', k):
            e = s.find('*/', k + 2); k = (e + 2) if e >= 0 else len(s); continue
        if s.startswith('//', k):
            e = s.find('\n', k); k = e if e >= 0 else len(s); continue
        out.append(c); k += 1
    return ''.join(out)
for m in pat.finditer(text):
    ls = text.rfind('\n', 0, m.start()) + 1
    pre = text[ls:m.start()].strip()
    if pre.startswith('*') or pre.startswith('/*') or pre.startswith('//'): continue
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
    args = split_args(strip_c_comments(text[m.end():i - 1]))
    buf = args[0] if args else ''
    n = line_of(m.start()); f = fn_of(n)
    body = buf in ('v->b', 'b', 'bb', 't') and f not in ('vm_fields_join',)
    span = [k for k, l in enumerate(src, 1) if 'const size_t matcher_at = c->len;' in l]
    stop = [k for k, l in enumerate(src, 1) if 'vm_emit_guarded_matcher(v, matcher_at, guard_at);' in l]
    frame = (buf == 'c' and f == 'vm_emit_search_body' and span[0] <= n <= stop[0]) or \
            (buf == 'c' and f == 'vm_emit_guarded_matcher')
    if not (body or frame): continue
    a1 = args[1] if len(args) > 1 else ''
    if re.fullmatch(r'(\s*"(?:[^"\\]|\\.)*"\s*)+', a1, flags=re.S):
        fmt = ''.join(re.findall(r'"((?:[^"\\]|\\.)*)"', a1))
    else:
        fmt = '<EXPR:%s>' % re.sub(r'\s+', ' ', a1)[:60]
    print('%d\t%s\t%s\t%s\t%s' % (n, f, m.group(1)[9:], 'frame' if frame else buf, fmt))
