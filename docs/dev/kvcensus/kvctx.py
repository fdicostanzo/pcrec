"""kvcensus: the CONTEXT shapes of a pattern's text (docs/dev/kvcensus.md §4).

A pattern is a context site when, after its leading option groups (`(?i)`),
it OPENS with zero-width context items (`\\b`, `\\B`, `(?<=X)`, `(?<!X)`) or
ENDS with them (`\\b`, `\\B`, `(?=X)`, `(?!X)`), and has no top-level `|`
(else the item binds one alternative only). The census strips the items and
compiles the BODY to ask what the body's language and machine say.

An item is EXPRESSIBLE as per-position sets (D161 add. 16) when:
  (?<=X) / (?=X)   X is a fixed-BYTE-width product (single characters,
                   classes and `{n}` only), absent byte FAILS it
  (?<!X) / (?!X)   X is ONE position (its complement set), absent SATISFIES
  \\b / \\B          decided by the adjacent body position's set S (S_0 for a
                   leading item, S_k-1 for a trailing one on a fixed-width
                   body): S inside \\w or outside it makes the item a one-byte
                   set on the far side; S straddling \\w is a disjunction
`expressible()` takes that adjacent set; this module only reads text.
"""
import re

META = set(b"\\[](){}|*+?.^$")


def _parens(p):
    """open index -> close index, or None on a construct this reader declines."""
    st, m, i, cls = [], {}, 0, False
    while i < len(p):
        c = p[i]
        if c == 0x5c:
            if p[i + 1:i + 2] in (b"Q", b"E"):
                return None
            i += 2
            continue
        if cls:
            if c == 0x5d:
                cls = False
            i += 1
            continue
        if c == 0x5b:
            cls = True
            i += 1
            if p[i:i + 1] == b"^":
                i += 1
            if p[i:i + 1] == b"]":
                i += 1
            continue
        if c == 0x28:
            st.append(i)
        elif c == 0x29:
            if not st:
                return None
            m[st.pop()] = i
        i += 1
    return None if st or cls else m


def _toplevel_alt(p, pm):
    depth, i, cls = 0, 0, False
    while i < len(p):
        c = p[i]
        if c == 0x5c:
            i += 2; continue
        if cls:
            if c == 0x5d: cls = False
            i += 1; continue
        if c == 0x5b:
            cls = True; i += 1
            if p[i:i + 1] == b"^": i += 1
            if p[i:i + 1] == b"]": i += 1
            continue
        if c == 0x28: depth += 1
        elif c == 0x29: depth -= 1
        elif c == 0x7c and depth == 0: return True
        i += 1
    return False


def product_width(x, utf8):
    """fixed BYTE width of X when X is a product of single positions, else None."""
    i, w, last = 0, 0, 0
    while i < len(x):
        c = x[i]
        if c == 0x5c:
            e = x[i + 1:i + 2]
            if e in (b"d", b"w", b"s"):
                n = 1
            elif e in (b"D", b"W", b"S"):
                if utf8: return None
                n = 1
            elif e == b"x":
                m = re.match(rb"\\x([0-9a-fA-F]{2})", x[i:])
                if not m: return None
                n = 1; i += 2
            elif e and not e.isalnum():
                n = 1
            else:
                return None
            i += 2
        elif c == 0x5b:
            j = i + 1
            if x[j:j + 1] == b"^":
                if utf8: return None
                j += 1
            if x[j:j + 1] == b"]": j += 1
            while j < len(x) and x[j] != 0x5d:
                if x[j] == 0x5c: j += 1
                elif x[j] >= 0x80 and utf8: return None
                j += 1
            if j >= len(x): return None
            n = 1; i = j + 1
        elif c == 0x2e:
            if utf8: return None
            n = 1; i += 1
        elif c in META:
            return None
        else:
            if c >= 0x80 and utf8:
                n = 1; i += 1
                while i < len(x) and 0x80 <= x[i] < 0xC0:
                    n += 1; i += 1
            else:
                n = 1; i += 1
        m = re.match(rb"\{(\d+)\}", x[i:])
        if m:
            n *= int(m.group(1)); i += m.end()
        elif x[i:i + 1] in (b"*", b"+", b"?", b"{"):
            return None
        w += n
        last = n
    return w


def parse(p):
    """-> dict(prefix, lead, trail, body, why) or None (not a context site)."""
    pm = _parens(p)
    if pm is None:
        return dict(why="unparsed")
    i, pre = 0, b""
    while True:
        m = re.match(rb"\(\?[a-zA-Z^-]*\)", p[i:])
        if not m: break
        if b"x" in m.group(0): return dict(why="extended")
        pre += m.group(0); i += m.end()
    lead = []
    while i < len(p):
        if p[i:i + 2] in (b"\\b", b"\\B"):
            lead.append((p[i + 1:i + 2].decode(), None)); i += 2; continue
        m = re.match(rb"\(\?<([=!])", p[i:])
        if m and i in pm:
            lead.append(("lb" + ("+" if m.group(1) == b"=" else "-"), p[i + 4:pm[i]]))
            i = pm[i] + 1
            continue
        break
    j = len(p)
    trail = []
    while j > i:
        if p[j - 2:j] in (b"\\b", b"\\B") and (j < 3 or p[j - 3] != 0x5c):
            trail.insert(0, (p[j - 1:j].decode(), None)); j -= 2; continue
        if p[j - 1] == 0x29:
            o = [k for k, v in pm.items() if v == j - 1]
            if o and o[0] >= i:
                m = re.match(rb"\(\?([=!])", p[o[0]:])
                if m:
                    trail.insert(0, ("la" + ("+" if m.group(1) == b"=" else "-"), p[o[0] + 3:j - 1]))
                    j = o[0]
                    continue
        break
    body = p[i:j]
    if not lead and not trail:
        return None
    if _toplevel_alt(p[len(pre):], pm):
        return dict(why="toplevel-alt", lead=lead, trail=trail)
    if not body:
        return dict(why="empty-body", lead=lead, trail=trail)
    return dict(why="", prefix=pre, lead=lead, trail=trail, body=pre + body)


def expressible(item, adj, utf8, wset):
    """-> (ok, absent_satisfies, set_size) for one context item; `adj` is the
    body position's byte set next to it (None when unknown)."""
    kind, x = item
    if kind in ("b", "B"):
        if adj is None:
            return False, None, 0
        inside, outside = adj <= wset, not (adj & wset)
        if not (inside or outside):
            return False, None, 0
        # \b next to a word byte: the far side must be non-word (absent ok)
        far_word = outside if kind == "b" else inside
        return True, not far_word, len(wset) if far_word else 256 - len(wset)
    w = product_width(x, utf8)
    if kind in ("lb+", "la+"):
        return (w is not None and w > 0), False, w or 0
    return (w == 1), True, 1


def strip_anchors(p):
    """START/END anchors around a pattern with no top-level `|`: the
    attempt-engine patterns (`^`, `\\A`, `\\G`, `(?m)^`) have no table, so the
    census reads the language from the origin off the BODY. -> (lead, trail,
    body) with lead in {'^', 'A', 'G', ''} and trail in {'$', 'z', 'Z', ''},
    or None when there is nothing to strip or the shape declines."""
    pm = _parens(p)
    if pm is None:
        return None
    i, pre = 0, b""
    while True:
        m = re.match(rb"\(\?[a-zA-Z^-]*\)", p[i:])
        if not m: break
        if b"x" in m.group(0): return None
        pre += m.group(0); i += m.end()
    lead = ""
    if p[i:i + 1] == b"^":
        lead, i = "^", i + 1
    elif p[i:i + 2] in (b"\\A", b"\\G"):
        lead, i = p[i + 1:i + 2].decode(), i + 2
    j, trail = len(p), ""
    if j > i and p[j - 1:j] == b"$" and (j < 2 or p[j - 2] != 0x5c):
        trail, j = "$", j - 1
    elif j - i >= 2 and p[j - 2:j] in (b"\\z", b"\\Z") and (j < 3 or p[j - 3] != 0x5c):
        trail, j = p[j - 1:j].decode(), j - 2
    if not lead and not trail:
        return None
    if _toplevel_alt(p[len(pre):], pm):
        return None
    return lead, trail, pre + p[i:j]
