#!/usr/bin/env python3
"""tests/memfn/routing_shape.py -- C18's ROUTING leg: the shape every
offset-skip/pre-check function takes in an emitted artifact since R4e'.0b
([MEMFN] R-11; integration.md §R4.9.2.5/§R4.9.2.6; D155 item 6 and
addendum 1). Read by libc_census.py (C11, `make test-memfn-stamps`) over its
whole corpus population; `--selftest` runs the planted controls alone.

THE RULE (Frank, D155 addendum 1): "A function that does work never contains
#if. A selector function's whole body may be the #if chain, one call per
arm, and nothing else." For an artifact's text it checks:
  routed     every FUNC (a file-scope `static inline size_t` whose name ends
             in one of pcrec's FUNC suffixes, _reqrun, _reqrun_whole,
             _ofsskip) has its helper `<fn>__body`, with the FUNC's own
             parameter list, defined ABOVE it;
  selector   the FUNC's whole body is either the one line
             `    return <fn>__body(<its parameters>);` or a chain of
             conditional directives with exactly one such call per arm, the
             callee `<fn>__body` or a level helper `<fn>__<token>`, and the
             `#else` arm's call `<fn>__body` (floor rule (c));
  no #if     no OTHER function body holds a conditional directive
             (#if/#ifdef/#ifndef/#elif/#else/#endif).
It returns (number of FUNCs, [violation, ...]).

THE INDEPENDENT CONTROL (docs/dev/learnings.md §3): the rule is read from
the ruling's text, never from the kit's renderer (memfn/src/ofsskip.c): this
file shares no code with it, and a pin re-pinned over a work-bearing
selector (tests/memfn/pins/arms.tsv is a change detector, not a rule) still
reads red here. The FUNC population is named by pcrec's FUNC suffixes, a
NAME filter (coding_guide.md §5 item 4): what it cannot see is a FUNC whose
name ends otherwise, which is why C11's floor on `funcs` is a literal the
FUNC census of the same population must reach (K35).
"""
import re
import sys

FUNC_SUFFIXES = ('_reqrun_whole', '_reqrun', '_ofsskip')
HEAD = re.compile(r'^static inline size_t (\w+)\(const unsigned char \*subject, size_t n, size_t pos'
                  r'((?:, const unsigned char \*\w+)*)\)$')
ANY_HEAD = re.compile(r'^[A-Za-z_][^;{}]*\b(\w+)\s*\([^;]*\)\s*$')
COND = re.compile(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b')
CALL = re.compile(r'^    return (\w+)\((.*)\);$')


def bodies(lines):
    """[(name or None, head line index, [body lines])] for every brace-at-
    column-0 function body: a `{` line opens one (a `{ ... }` line is a whole
    one-line body), a `}` line closes it."""
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('{'):
            head = lines[i - 1] if i else ''
            m = ANY_HEAD.match(head)
            name = m.group(1) if m else None
            if ln.rstrip().endswith('}') and ln.strip() != '{':
                out.append((name, i - 1, [ln[1:].rstrip()[:-1]]))
                i += 1
                continue
            j = i + 1
            while j < len(lines) and not lines[j].startswith('}'):
                j += 1
            out.append((name, i - 1, lines[i + 1:j]))
            i = j + 1
            continue
        i += 1
    return out


def check(text):
    lines = text.split('\n')
    heads = {}
    for i, ln in enumerate(lines):
        m = HEAD.match(ln)
        if m:
            heads.setdefault(m.group(1), []).append((i, m.group(2)))
    funcs = [n for n in heads if n.endswith(FUNC_SUFFIXES)]
    bad = []
    selector_at = set()
    for fn in sorted(funcs):
        if len(heads[fn]) != 1:
            bad.append('%s defined %d times' % (fn, len(heads[fn])))
            continue
        at, tparams = heads[fn][0]
        selector_at.add(at)
        helper = heads.get(fn + '__body')
        if not helper:
            bad.append('%s is not routed: no %s__body' % (fn, fn))
            continue
        if helper[0][0] > at:
            bad.append('%s__body is defined below %s' % (fn, fn))
        if helper[0][1] != tparams:
            bad.append('%s__body does not take %s\'s parameters' % (fn, fn))
        args = 'subject, n, pos' + ''.join(', ' + t for t in re.findall(r'\*(\w+)', tparams))
        why = selector_body(fn, body_at(lines, at), args)
        if why:
            bad.append('%s: %s' % (fn, why))
    for name, at, body in bodies(lines):
        if at in selector_at:
            continue
        for ln in body:
            if COND.match(ln):
                bad.append('%s holds a directive: %s' % (name or '(a function)', ln.strip()))
                break
    return len(funcs), bad


def body_at(lines, head):
    if head + 1 >= len(lines) or lines[head + 1] != '{':
        return None
    j = head + 2
    while j < len(lines) and not lines[j].startswith('}'):
        j += 1
    return lines[head + 2:j]


def selector_body(fn, body, args):
    """None when `body` is a selector's whole body, else why not."""
    if body is None:
        return 'its body does not open with a `{` line'
    if not body:
        return 'its body is empty'

    def call(ln, last):
        m = CALL.match(ln)
        if not m:
            return 'a line that is not one call: %r' % ln.strip()
        if m.group(2) != args:
            return 'a call that does not forward its parameters: %r' % ln.strip()
        if last and m.group(1) != fn + '__body':
            return 'the last arm calls %s, not %s__body' % (m.group(1), fn)
        if m.group(1) != fn + '__body' and not re.match(re.escape(fn) + r'__\w+$', m.group(1)):
            return 'a call to %s, which is not one of its helpers' % m.group(1)
        return None

    if len(body) == 1:
        return call(body[0], True)
    # the #if chain: #if, call, (#elif, call)*, #else, call, #endif
    want = 'if'
    for k, ln in enumerate(body):
        m = COND.match(ln)
        if want in ('if', 'cond'):
            if not m or (want == 'if' and m.group(1) != 'if') or \
               (want == 'cond' and m.group(1) not in ('elif', 'else')):
                return 'the chain is not #if/#elif/#else: %r' % ln.strip()
            seen_else = m.group(1) == 'else'
            want = 'call'
        elif want == 'call':
            why = call(ln, seen_else)
            if why:
                return why
            want = 'endif' if seen_else else 'cond'
        elif want == 'endif':
            if not m or m.group(1) != 'endif' or k != len(body) - 1:
                return 'the chain does not end at its #else arm\'s #endif'
            return None
    return 'the chain has no #else arm and #endif'


# ---- the planted controls ----------------------------------------------------

HELPER = ('static inline size_t rx_reqrun__body(const unsigned char *subject, size_t n, size_t pos)\n'
          '{\n    while (pos < n) { if (subject[pos] == 97) return pos; pos++; }\n    return n;\n}\n\n')
SELECTOR = ('static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)\n'
            '{\n    return rx_reqrun__body(subject, n, pos);\n}\n\n')
CHAIN = ('static inline size_t rx_reqrun__w16(const unsigned char *subject, size_t n, size_t pos)\n'
         '{\n    return rx_reqrun__body(subject, n, pos);\n}\n\n'
         'static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)\n'
         '{\n#if defined(__SSE2__)\n    return rx_reqrun__w16(subject, n, pos);\n'
         '#else\n    return rx_reqrun__body(subject, n, pos);\n#endif\n}\n\n')
CONTROLS = [
    # (name, text, expect a violation)
    ('routed', HELPER + SELECTOR, False),
    ('the D155 chain', HELPER + CHAIN, False),
    ('no FUNC at all', 'static int f(int x)\n{\n    return x;\n}\n', False),
    ('unrouted (the old shape)', HELPER.replace('rx_reqrun__body', 'rx_reqrun'), True),
    ('selector does work', HELPER + SELECTOR.replace('    return', '    pos++;\n    return'), True),
    ('selector drops a parameter', HELPER + SELECTOR.replace('(subject, n, pos)', '(subject, n, 0)'), True),
    ('helper below the selector', SELECTOR + HELPER, True),
    ('#if in a work body', HELPER.replace('{\n    while', '{\n#if 1\n    while').replace(
        '    return n;\n', '    return n;\n#endif\n') + SELECTOR, True),
    ('chain arm does work', HELPER + CHAIN.replace('#else\n    return', '#else\n    pos++;\n    return'), True),
    ('chain #else calls a level', HELPER + CHAIN.replace('#else\n    return rx_reqrun__body',
                                                       '#else\n    return rx_reqrun__w16'), True),
]


def selftest():
    """[(name, ok)]: each control's verdict against its expectation."""
    out = []
    for name, text, expect in CONTROLS:
        n, why = check(text)
        out.append((name, bool(why) == expect, why))
    return out


if __name__ == '__main__':
    bad = 0
    for name, ok, why in selftest():
        print('%s: control %s%s' % ('PASS' if ok else 'FAIL', name, '' if ok else ' (%s)' % why))
        bad += not ok
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            n, why = check(open(path, encoding='utf-8', errors='surrogateescape').read())
            print('%s: %d FUNC(s)%s' % (path, n, ''.join('\n  ' + w for w in why)))
            bad += bool(why)
    sys.exit(1 if bad else 0)
