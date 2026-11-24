#!/usr/bin/env python3
# ents.py FILE.c : list every top-level entity (kind, name, start, end, static?) of a C file.
# Comments and string/char literals are blanked first (line structure kept), so braces inside
# emitted C text do not count. Kinds: fn, proto, table (array object), obj, struct, enum, typedef, macro.
import re, sys

def blank(src):
    out = []; i = 0; n = len(src); st = None
    while i < n:
        c = src[i]
        if st is None:
            if src.startswith('/*', i): st = 'c'; out.append('  '); i += 2; continue
            if src.startswith('//', i): st = 'l'; out.append('  '); i += 2; continue
            if c == '"': st = 's'; out.append('"'); i += 1; continue
            if c == "'": st = 'q'; out.append("'"); i += 1; continue
            out.append(c); i += 1; continue
        if st == 'c':
            if src.startswith('*/', i): st = None; out.append('  '); i += 2; continue
            out.append('\n' if c == '\n' else ' '); i += 1; continue
        if st == 'l':
            if c == '\n': st = None; out.append('\n')
            else: out.append(' ')
            i += 1; continue
        if st in 'sq':
            q = '"' if st == 's' else "'"
            if c == '\\' and i + 1 < n:
                out.append('  ' if src[i+1] != '\n' else ' \n'); i += 2; continue
            if c == q: st = None; out.append(q); i += 1; continue
            out.append('\n' if c == '\n' else ' '); i += 1; continue
    return ''.join(out)

def entities(path):
    raw = open(path).read()
    L = blank(raw).split('\n')
    R = raw.split('\n')
    ents = []; i = 0; n = len(L)
    while i < n:
        l = L[i]
        if not l.strip(): i += 1; continue
        if l.startswith('#'):
            j = i
            while L[j].rstrip().endswith('\\'): j += 1
            m = re.match(r'#\s*define\s+([A-Za-z_]\w*)', l)
            if m: ents.append(('macro', m.group(1), i+1, j+1, False))
            i = j + 1; continue
        if l[0] in ' \t':  # stray continuation
            i += 1; continue
        mi = re.match(r'^([A-Z_][A-Z_0-9]*)\(\s*([a-z_]\w*)', l)
        if mi and l.rstrip().endswith(')'):
            ents.append(('inst', mi.group(2), i+1, i+1, True)); i += 1; continue
        me = re.match(r'^enum\s*\{([^}]*)\}\s*;', l)
        if me:
            for nm in re.findall(r'([A-Z_][A-Z_0-9]*)\s*(?:=[^,]*)?(?:,|$)', me.group(1)):
                ents.append(('enumr', nm, i+1, i+1, False))
            i += 1; continue
        # gather until depth 0 and a terminator
        depth = 0; j = i; text = ''
        while j < n:
            t = L[j]; text += t + '\n'
            depth += t.count('{') + t.count('(') + t.count('[') - t.count('}') - t.count(')') - t.count(']')
            s = t.rstrip()
            if depth == 0 and (s.endswith(';') or s.endswith('}')):
                break
            j += 1
        flat = ' '.join(text.split())
        static = flat.startswith('static')
        kind = None; name = None
        hdr = flat.split('{')[0]
        if re.match(r'^typedef\b', flat):
            kind = 'typedef'
            m = re.search(r'\b([A-Za-z_]\w*)\s*(\[[^\]]*\])?\s*;\s*$', flat) or re.search(r'\(\s*\*\s*([A-Za-z_]\w*)\s*\)', flat)
            name = m.group(1) if m else '?'
        elif re.match(r'^(enum)\b[^=(]*\{', flat) and not re.search(r'\}\s*[A-Za-z_]\w*\s*(\[[^\]]*\])*\s*=', flat):
            kind = 'enum'; m = re.match(r'^enum\s+([A-Za-z_]\w*)', flat); name = m.group(1) if m else '(anon)'
        elif re.match(r'^(struct|union)\s+[A-Za-z_]\w*\s*\{', flat) and re.search(r'\}\s*;\s*$', flat):
            kind = 'struct'; name = re.match(r'^(?:struct|union)\s+([A-Za-z_]\w*)', flat).group(1)
        elif re.match(r'^(struct|union)\s+[A-Za-z_]\w*\s*;$', flat):
            kind = 'fwd'; name = re.match(r'^(?:struct|union)\s+([A-Za-z_]\w*)', flat).group(1)
        else:
            # function definition: header has '(' and body '{', no '=' before '('
            m = re.match(r'^[^=;{]*?\b([A-Za-z_]\w*)\s*\(', hdr)
            if m and '{' in flat and '=' not in flat.split('(')[0] and not re.search(r'\]\s*=', hdr):
                kind = 'fn'; name = m.group(1)
            elif m and flat.endswith(';') and '{' not in flat and '=' not in flat.split('(')[0]:
                kind = 'proto'; name = m.group(1)
            else:
                m2 = re.search(r'\}\s*([A-Za-z_]\w*)\s*((\[[^\]]*\])*)\s*=', flat)
                m3 = re.match(r'^[^=]*?\b([A-Za-z_]\w*)\s*((\[[^\]]*\])*)\s*(=|;)', flat)
                mm = m2 or m3
                if mm:
                    name = mm.group(1); kind = 'table' if mm.group(2) else 'obj'
                    if kind == 'obj' and '=' not in flat and flat.startswith('static'):
                        kind = 'proto'   # a tentative/forward object declaration
                else:
                    kind = '?'; name = flat[:40]
        if kind == 'enum':
            body = flat[flat.index('{')+1:flat.rindex('}')]
            for nm in re.findall(r'([A-Z_][A-Z_0-9]*)\s*(?:=[^,]*)?(?:,|$)', body):
                ents.append(('enumr', nm, i+1, j+1, False))
            if name != '(anon)': ents.append((kind, name, i+1, j+1, static))
        else:
            ents.append((kind, name, i+1, j+1, static))
        i = j + 1
    return ents, L

if __name__ == '__main__':
    ents, _ = entities(sys.argv[1])
    for k, nm, a, b, s in ents:
        print(f'{a}\t{b}\t{k}\t{"S" if s else "X"}\t{nm}')
