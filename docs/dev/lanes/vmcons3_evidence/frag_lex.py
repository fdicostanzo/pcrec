#!/usr/bin/env python3
"""A PROTOTYPE of rev 3's value-fragment lexer (the build writes it in C, in
src/gen/vm_stmt.c), run here over the OPAQUE fragments of real artifacts: the
memfn kit's windows inside a matcher body (the span advance and the literal
run compare). pcrec's own fragments are built from typed pieces; the kit's are
the ones nothing types, so they are the census population.

THE TEXT DOMAIN: C tokens outside comments and string/char literals (a
literal's bytes, which carry PATTERN bytes, are one opaque token).
Preprocessor lines are lexed too (every #if arm), and #define/#undef/#include/
#line refuse.

THE RULES (not a chosen token list: C's own classes, and the artifact's own
declaration lists):
  R1 control: no `goto`, no `return`, no `setjmp`/`longjmp`, no noreturn call
     (`abort`, `exit`, `__builtin_trap`, `__builtin_unreachable`). C confines
     `break`/`continue`/`switch` to the fragment's own statements (the matcher
     body has no loop or switch around a fragment), so they are allowed.
  R2 labels: no identifier that names a label of the matcher (`<p>_L<n>`,
     `<p>_fail`, `<p>_accept`): every label reference is a renderer's.
  R3 writes: an identifier of the MATCHER'S SCOPE (the frame's declarations:
     parameters and locals) may only be read: never followed, after any
     `[..]`/`.f`/`->f` chain, by an assignment operator or ++/--, never
     preceded by ++/--, never the operand of unary `&`. Exception: the
     fragment class's declared outputs (the span window: `<p>_span_cursor`).
  R4 names: every `<p>_`/`<P>_` identifier is a scope name, or a helper the
     artifact defines that is declared PURE in the helper table; anything
     else refuses (a helper with an effect would need a row).

usage: frag_lex.py PREFIX CLASS < fragment-text   (prints REFUSED/CLEAN + why)
or import it: lex(), check(text, prefix, scope, outputs)."""
import re, sys

KW_CONTROL = {'goto', 'return', 'setjmp', 'longjmp', 'abort', 'exit',
              '__builtin_trap', '__builtin_unreachable', '_Exit', 'quick_exit'}
ASSIGN = {'=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='}
INCDEC = {'++', '--'}
PUNCT = sorted(['<<=', '>>=', '->', '++', '--', '<<', '>>', '<=', '>=', '==', '!=',
                '&&', '||', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '##'],
               key=len, reverse=True)
# Helpers an artifact defines that a fragment may call: pure readers of their
# arguments (the build's helper table carries this column for EVERY helper the
# prologue writes; unknown = refused).
PURE_HELPERS = ['w2', 'w4', 'w8', 'decode', 'back_step', 'span_match',
                'span_match_caseless', 'PRUNE_TOO_SHORT', 'PRUNE_CLAMP_SPAN',
                'BACK_STEP_NONE', 'R_INTERNAL']
PURE_PATTERNS = [r'class_bitmap\d+', r'class_atom\d+', r'wcls\d+', r'cls\d+_[a-z0-9_]+', r'ofs[a-z0-9_]*',
                 r'mf_[a-z0-9_]+']

def lex(s):
    """C tokens of s: (kind, text). Comments dropped; string/char literals
    one token; preprocessor directive names as ('pp', name)."""
    toks, i, n, bol = [], 0, len(s), True
    while i < n:
        c = s[i]
        if c == '\n': bol = True; i += 1; continue
        if c in ' \t\r\\': i += 1; continue
        if s.startswith('//', i):
            j = s.find('\n', i); i = n if j < 0 else j; continue
        if s.startswith('/*', i):
            j = s.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        if c == '#' and bol:
            m = re.match(r'#\s*([a-z]+)', s[i:]); toks.append(('pp', m.group(1) if m else '')); i += m.end() if m else 1; bol = False; continue
        bol = False
        if c in '"\'':
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == '\\' else 1
            toks.append(('lit', s[i:j + 1])); i = j + 1; continue
        m = re.match(r'[A-Za-z_][A-Za-z0-9_]*', s[i:])
        if m: toks.append(('id', m.group(0))); i += m.end(); continue
        m = re.match(r'(0[xX][0-9a-fA-F]+|\d+)[uUlL]*', s[i:])
        if m: toks.append(('num', m.group(0))); i += m.end(); continue
        for p in PUNCT:
            if s.startswith(p, i): toks.append(('op', p)); i += len(p); break
        else:
            toks.append(('op', c)); i += 1
    return toks

def is_label(t, p):
    return re.fullmatch(r'%s_(L\d+|fail|accept)' % re.escape(p), t) is not None

def is_pure(t, p):
    for pre in (p + '_', p.upper() + '_'):
        if t.startswith(pre):
            rest = t[len(pre):]
            return rest in PURE_HELPERS or any(re.fullmatch(x, rest) for x in PURE_PATTERNS)
    return False

def check(text, p, scope, outputs):
    toks = lex(text)
    why = []
    for k, (kind, t) in enumerate(toks):
        if kind == 'pp' and t in ('define', 'undef', 'include', 'line'):
            why.append('R1 #%s' % t)
        if kind != 'id': continue
        if t in KW_CONTROL: why.append('R1 %s' % t); continue
        if is_label(t, p): why.append('R2 label %s' % t); continue
        if t in scope:
            if t in outputs: continue
            # after the name: skip [..], .f, ->f chains
            j = k + 1
            while j < len(toks):
                if toks[j] == ('op', '['):
                    d = 0
                    while j < len(toks):
                        if toks[j] == ('op', '['): d += 1
                        elif toks[j] == ('op', ']'):
                            d -= 1
                            if d == 0: break
                        j += 1
                    j += 1; continue
                if toks[j] in (('op', '.'), ('op', '->')) and j + 1 < len(toks):
                    j += 2; continue
                break
            nxt = toks[j][1] if j < len(toks) else ''
            prv = toks[k - 1] if k else ('', '')
            if nxt in ASSIGN or nxt in INCDEC:
                why.append('R3 write %s %s' % (t, nxt))
            elif prv[1] in INCDEC:
                why.append('R3 write %s%s' % (prv[1], t))
            elif prv == ('op', '&') and (k < 2 or toks[k - 2][0] == 'op' and toks[k - 2][1] not in (')', ']')):
                why.append('R3 address-of %s' % t)
            continue
        if t.startswith(p + '_') or t.startswith(p.upper() + '_'):
            if not is_pure(t, p): why.append('R4 unknown helper %s' % t)
    return why

if __name__ == '__main__':
    p = sys.argv[1]
    txt = sys.stdin.read()
    scope = set(sys.argv[3:]) if len(sys.argv) > 3 else set()
    w = check(txt, p, scope, {p + '_span_cursor'} if sys.argv[2] == 'span' else set())
    print('REFUSED ' + '; '.join(w) if w else 'CLEAN')
