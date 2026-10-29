#!/usr/bin/env python3
"""p910 P9 twins: hand edits of pcrec's own artifacts (scratch only).

For each pattern dir NAME-auto / NAME-vm (rx.c as pcrec emitted it), write
  NAME-autofind/  the hybrid's DFA prefilter: the idle-state skip runs at EVERY
                  seed state (not only state 0) and is the window FIND below
  NAME-vmfind/    forced VM: the start-set walk replaced by the window FIND
  NAME-vmfind0/   as vmfind without the look-behind term (kset terms only)
  NAME-vmfindm1/  as vmfind, walking on the look-behind term instead of offset 0
The window FIND is the scalar walk (the kit's default form for a set FIND):
  candidate c iff (c == 0 || s[c-1] is not \\w) && s[c+j] in S_j, j = 0..k-1
S_j are the per-offset sets of the leading keyword alternation (the kset_walk
fact's sets, printed by --emit-facts as sizes); the look-behind term is the
leading \\b's consequence when S_0 is all \\w bytes.
"""
import os, re, sys

KW = {
    'ctx': ['fail', 'abort', 'panic'],
    'level-context': ['ERROR', 'FATAL', 'CRIT'],
}

def sets(words):
    k = min(len(w) for w in words)
    return [sorted({w[j] for w in words}) for j in range(k)]

def table(name, members):
    v = [0] * 256
    for m in members:
        v[m if isinstance(m, int) else ord(m)] = 1
    rows = ',\n'.join('    ' + ','.join(str(x) for x in v[i:i + 32]) for i in range(0, 256, 32))
    return f'static const unsigned char {name}[256] = {{\n{rows}\n}};\n'

WORD = [b for b in range(256) if chr(b).isascii() and (chr(b).isalnum() or chr(b) == '_')]

def find_fn(words, behind, walk):
    S = sets(words)
    k = len(S)
    out = table('p9_word', WORD)
    for j, s in enumerate(S):
        out += table(f'p9_s{j}', s)
    terms = [f'p9_s{j}[s[c + {j}]]' for j in range(k)]
    out += f'/* window FIND: {k} kset terms{" + look-behind \\\\W term" if behind else ""}; walk on {walk} */\n'
    allt = " && ".join(terms)
    out += 'static inline size_t p9_find(const unsigned char *s, size_t n, size_t c)\n{\n'
    out += f'    if (n < {k}) return n;\n'
    out += f'    const size_t last = n - {k};   /* the last position a candidate may sit at */\n'
    if walk == 'm1':
        # walk on the look-behind term: the tight loop skips \w runs
        out += f'    if (c == 0) {{ if ({allt.replace("c + ", "0 + ")}) return 0; c = 1; }}\n'
        out += '    while (c <= last) {\n'
        out += '        size_t p = c - 1;\n'
        out += '        while (p < last && p9_word[s[p]]) p++;\n'
        out += '        if (p9_word[s[p]]) return n;\n'
        out += '        c = p + 1;\n'
        out += '        if (c > last) return n;\n'
        out += f'        if ({allt}) return c;\n'
        out += '        c++;\n'
        out += '    }\n    return n;\n}\n'
    else:
        out += '    while (c <= last) {\n'
        out += f'        while (c < last && !{terms[0]}) c++;\n'
        out += f'        if (!{terms[0]}) return n;\n'
        rest = []
        if behind: rest.append('(c == 0 || !p9_word[s[c - 1]])')
        rest += terms[1:]
        out += f'        if ({" && ".join(rest) if rest else "1"}) return c;\n'
        out += '        c++;\n'
        out += '    }\n    return n;\n}\n'
    return out

def patch_vm(src, fn):
    src = src.replace('static int rx_search_run(', fn + '\nstatic int rx_search_run(', 1)
    old = 'while (attempt_position < subject_length && !rx_start_set[subject[attempt_position]]) attempt_position++;'
    assert src.count(old) == 2
    return src.replace(old, 'attempt_position = p9_find(subject, subject_length, attempt_position);')

def patch_auto(src, fn):
    src = src.replace('static int rx_prefilter(', fn + '\nstatic int rx_prefilter(', 1)
    m = re.search(r'rx_forward_seed_state\[(\d+)\] = \{([^}]*)\}', src)
    seeds = sorted({int(x) for x in m.group(2).replace('\n', ' ').split(',') if x.strip()})
    cond = ' || '.join(f'forward_state == {s}' for s in seeds)
    old_head = 'if (forward_state == 0 && last_accept_position == (size_t)-1) {'
    assert src.count(old_head) == 1
    i = src.index(old_head)
    j = src.index('\n        }', i)
    new = (f'if (({cond}) && last_accept_position == (size_t)-1) {{\n'
           '            size_t skip_from = scan_position;\n'
           '            scan_position = p9_find(subject, subject_length, scan_position);\n'
           '            if (scan_position >= subject_length) { scan_position = subject_length; break; }\n'
           '            if (scan_position > skip_from) forward_state = rx_forward_seed_state[rx_forward_byte_class[subject[scan_position - 1]]];')
    return src[:i] + new + src[j:], seeds

def main(root):
    for d in sorted(os.listdir(root)):
        if not d.endswith('-auto'):
            continue
        name = d[:-5]
        words = KW['ctx'] if name.startswith('ctx') else KW[name]
        auto = open(os.path.join(root, d, 'rx.c')).read()
        vm = open(os.path.join(root, name + '-vm', 'rx.c')).read()
        outs = {}
        outs['autofind'], seeds = patch_auto(auto, find_fn(words, True, '0'))
        outs['vmfind'] = patch_vm(vm, find_fn(words, True, '0'))
        outs['vmfind0'] = patch_vm(vm, find_fn(words, False, '0'))
        outs['vmfindm1'] = patch_vm(vm, find_fn(words, True, 'm1'))
        for k, v in outs.items():
            od = os.path.join(root, f'{name}-{k}')
            os.makedirs(od, exist_ok=True)
            open(os.path.join(od, 'rx.c'), 'w').write(v)
            for h in os.listdir(os.path.join(root, d)):
                if h.endswith('.h'):
                    open(os.path.join(od, h), 'w').write(open(os.path.join(root, d, h)).read())
        print(name, 'seeds', seeds, 'sets', sets(words))

main(sys.argv[1])
