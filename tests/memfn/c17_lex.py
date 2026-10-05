"""C17's emitter reader: every string literal of a C source file, attributed to
the top-level definition that contains it.

THIS IS THE STATIC HALF'S ONLY VIEW OF AN EMITTER. pcrec's emitters spell the
generated program as C string literals, so "an emitter spells a search form"
means "a string literal inside that function's body matches a vocabulary
line". Comments of the EMITTER's own source are not emitted text and are
dropped here; comments the emitter WRITES into the artifact are string
literals and are kept (the vocabulary's regexes, not this reader, keep a
prose mention such as "one memchr() replaces the steps" from matching).

Adjacent literals separated only by whitespace or comments are joined into
one, as the C compiler joins them, so a form split across two source lines
("...memchr(" "subject + %s...") is seen whole. Its line is the first piece's.

Attribution: a `{` at file scope opens a definition. A header (the file-scope
text since the last `;`, `}` or directive) with a `=` names an initializer
(`static const Row rows[] = {` -> `rows`); else one with a `(` names a
function (the identifier before the first `(`); else it is a type body and
literals in it are attributed to `<type>`. A literal at file scope outside
any brace is attributed to the initializer it sits in. A literal on a
preprocessor line is attributed to `#define NAME` (or `#<directive>`).
"""

import re

_IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def _name_from_header(header):
    h = header.strip()
    if '=' in h:
        m = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\]\s*)*=', h)
        return m[-1] if m else '<init>'
    if '(' in h:
        m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', h)
        return m.group(1) if m else '<fn>'
    return '<type>'


def literals_by_function(path):
    """(definition_name, line, joined_literal_text) for every string literal
    (adjacent pieces joined) in `path`."""
    return scan(path)[0]


def definitions(path):
    """Every file-scope definition with a body in `path`: functions,
    initializers and (as `<type>`) type bodies."""
    return scan(path)[1]


def scan(path):
    """(literals, definition names) of `path`, in one pass."""
    with open(path, encoding='utf-8', errors='replace') as fh:
        src = fh.read()
    out = []
    i, n, line = 0, len(src), 1
    depth = 0
    header = []          # file-scope text since the last ; } or directive
    current = None       # name of the open file-scope definition
    at_line_start = True
    pending = None       # [name, line, text] of a literal still joinable
    defs = set()

    def flush():
        nonlocal pending
        if pending is not None:
            out.append(tuple(pending))
            pending = None

    while i < n:
        ch = src[i]
        if ch == '\n':
            line += 1
            at_line_start = True
            if depth == 0:
                header.append(ch)
            i += 1
            continue
        if ch in ' \t\r\f\v':
            if depth == 0:
                header.append(ch)
            i += 1
            continue
        # comments: invisible, and do not break literal joining
        if src.startswith('//', i):
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            j = n if j < 0 else j + 2
            line += src.count('\n', i, j)
            i = j
            continue
        # preprocessor line (with continuations)
        if ch == '#' and at_line_start:
            flush()
            j = i
            while True:
                k = src.find('\n', j)
                if k < 0:
                    k = n
                    break
                if src[k - 1] == '\\':
                    j = k + 1
                    continue
                break
            text = src[i:k]
            m = re.match(r'#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)', text)
            d = re.match(r'#\s*([A-Za-z_]+)', text)
            name = ('#define ' + m.group(1)) if m else ('#' + (d.group(1) if d else ''))
            for sm in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', text):
                out.append((name, line + text.count('\n', 0, sm.start()), sm.group(1)))
            line += text.count('\n')
            i = k
            continue
        at_line_start = False
        if ch == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == '\\' else 1
            text = src[i + 1:j]
            line += text.count('\n')  # only via line-continuation escapes
            if pending is not None:
                pending[2] += text
            else:
                if current is not None:
                    name = current
                else:
                    name = _name_from_header(''.join(header) + '=') \
                        if '=' in ''.join(header) else '<file>'
                pending = [name, line, text]
            i = j + 1
            continue
        flush()
        if ch == "'":
            j = i + 1
            while j < n and src[j] != "'":
                j += 2 if src[j] == '\\' else 1
            if depth == 0:
                header.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == '{':
            if depth == 0:
                current = _name_from_header(''.join(header))
                defs.add(current)
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                current = None
                header = []
        elif ch == ';' and depth == 0:
            header = []
        elif depth == 0:
            header.append(ch)
        i += 1
    flush()
    # a file-scope initializer with no brace (`static const char x[] = "...";`)
    # is a definition too: its literals carry its name.
    defs.update(name for name, _, _ in out if not name.startswith('#'))
    return out, defs
