#!/usr/bin/env python3
"""Census of the OPAQUE value fragments (memfn kit windows) in matcher bodies,
through the frag_lex.py prototype, plus the lexer's own sabotage rows.

usage: kit_census.py PREFIX ARTIFACT.c...
For each artifact: the matcher functions (`_match_anchored`, `__match_notempty`),
their scope (parameters + the frame's declarations), and two window classes:
  span: the kit's advance inside a SPAN block (after the cursor init, up to
        the block's closing brace); declared output: <p>_span_cursor;
  run:  the kit's run-compare expression (`if (scan_position + N <=
        subject_length && <KIT>) ...`); no outputs.
Prints one line per window and a total; exit 1 on any refusal."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frag_lex

def matchers(src, p):
    out = []
    for m in re.finditer(r'^static [^\n]*\b%s_(match_anchored|_match_notempty)\(([^)]*)\)\n\{\n' % p, src, re.M):
        start = m.end()
        end = src.find('\n}\n', start)
        params = {re.findall(r'([A-Za-z_]\w*)\s*$', a.strip())[0] for a in m.group(2).split(',') if a.strip()}
        out.append((m.group(1), params, src[start:end]))
    return out

def scope_of(body, p, params):
    head = body[:body.find('    goto %s_L0;' % p)]
    names = set(params)
    for stmt in re.split(r';', head):
        m = re.search(r'([A-Za-z_]\w*)\s*(\[[^\]]*\])*\s*=', stmt)
        if m and not stmt.strip().startswith('(void)'): names.add(m.group(1))
    return names

def windows(body, p):
    ws = []
    for m in re.finditer(r'\n        %s_span_cursor = scan_position;\n(.*?)\n    \}\n' % p, body, re.S):
        ws.append(('span', m.group(1)))
    for m in re.finditer(r'\n    if \(scan_position \+ \d+ <= subject_length && (.*?)\) (goto %s_L\d+;|\{ scan_position)' % p, body, re.S):
        ws.append(('run', m.group(1)))
    return ws

def main():
    p = sys.argv[1]
    n = bad = 0
    seen = {}
    for f in sys.argv[2:]:
        src = open(f).read()
        for name, params, body in matchers(src, p):
            scope = scope_of(body, p, params)
            for cls, w in windows(body, p):
                n += 1
                why = frag_lex.check(w, p, scope, {p + '_span_cursor'} if cls == 'span' else set())
                key = (cls, re.sub(r'\d+', 'N', w))
                seen[key] = seen.get(key, 0) + 1
                if why:
                    bad += 1
                    print('REFUSED\t%s\t%s\t%s\t%s' % (os.path.basename(f), name, cls, '; '.join(why)))
    print('# windows: %d (distinct shapes %d), refused: %d' % (n, len(seen), bad))
    for (cls, shape), k in sorted(seen.items(), key=lambda x: -x[1])[:12]:
        print('#  %4d  %-4s %s' % (k, cls, shape.replace('\n', ' ')[:150]))
    # The lexer's own sabotage rows: each must refuse (or, for the
    # literal/comment/compare rows, must NOT refuse: FIX-1, FIX-5 (i)/(ii)).
    scope = {'scan_position', 'slot_values', 'run', 'ctx', 'subject',
             'subject_length', p + '_span_cursor', p + '_rv0_iteration'}
    rows = [
        ('goto in a kit window', 'x && ({ goto %s_L3; 1; })' % p, True),
        ('return in a kit window', 'x || (return 1)', True),
        ('label name, no goto', 'x == (long)&&%s_L3' % p, True),
        ('cursor write', '(scan_position = 3) > 0', True),
        ('cursor ++', 'scan_position++ < 3', True),
        ('slot write', '(slot_values[2] = 0) == 0', True),
        ('local write (an LSET in a fragment, FIX-6 mirror)', '(%s_rv0_iteration = 0) == 0' % p, True),
        ('address of the cursor', 'f(&scan_position)', True),
        ('run-state write', '(--run->steps_left) > 0', True),
        ('unknown helper', '%s_mystery(subject)' % p, True),
        ('#define in a window', '\n#define X 1\nx', True),
        ('noreturn call', 'x || (__builtin_trap(), 0)', True),
        ('pattern bytes in a literal (FIX-1)', 'rx_w2(subject + scan_position) == rx_w2("\\?{") && !memcmp(s, "x}\\"return", 9)', False),
        ('return in comment text (FIX-5 i)', 'x /* the call returned; continue here */ && y // returns\n', False),
        ('== is a read (FIX-5 ii)', 'scan_position == 0 && run->resume_depth == 0', False),
        ('span output write allowed', '%s_span_cursor += 1' % p, False),
    ]
    rbad = 0
    for name, txt, want in rows:
        why = frag_lex.check(txt, p, scope, {p + '_span_cursor'} if 'span output' in name else set())
        ok = bool(why) == want
        rbad += not ok
        print('# sabotage %-50s %s %s' % (name, 'DETECTED' if why else 'clean', 'ok' if ok else 'WRONG'))
    print('# result: %s' % ('CENSUS CLEAN, SABOTAGES AS EXPECTED' if bad == 0 and rbad == 0 else 'RED'))
    sys.exit(1 if bad or rbad else 0)

main()
