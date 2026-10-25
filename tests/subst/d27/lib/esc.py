"""Byte-string escaping for the corpus TSVs.

Field escapes: \\\\ \\t \\n \\r \\0 \\xHH; every other byte is itself.
The literal field `<NULL>` (subjects only) means a NULL subject pointer.
"""


def unesc(s: str) -> bytes:
    out = bytearray()
    b = s.encode('utf-8')
    i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            d = chr(b[i + 1])
            if d == 'x':
                out.append(int(b[i + 2:i + 4].decode(), 16))
                i += 4
                continue
            out.append({'\\': 0x5C, 't': 9, 'n': 10, 'r': 13, '0': 0}[d])
            i += 2
            continue
        out.append(c)
        i += 1
    return bytes(out)


def esc(b: bytes) -> str:
    o = []
    for c in b:
        if c == 0x5C:
            o.append('\\\\')
        elif c == 9:
            o.append('\\t')
        elif c == 10:
            o.append('\\n')
        elif c == 13:
            o.append('\\r')
        elif c == 0:
            o.append('\\0')
        elif 0x20 <= c < 0x7F:
            o.append(chr(c))
        else:
            o.append('\\x%02x' % c)
    return ''.join(o)


def cstr(b: bytes) -> str:
    """A C string literal for arbitrary bytes (octal escapes, no trigraphs)."""
    o = ['"']
    for c in b:
        if c in (0x22, 0x5C, 0x3F) or c < 0x20 or c >= 0x7F:
            o.append('\\%03o' % c)
        else:
            o.append(chr(c))
    o.append('"')
    return ''.join(o)
