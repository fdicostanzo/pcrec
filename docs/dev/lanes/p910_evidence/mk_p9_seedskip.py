#!/usr/bin/env python3
"""p910 P9 twin (A): DFA-local. Every SEED state (an idle state: only the
unanchored start thread live, one per look-behind context class) gets the skip
state 0 already has, over ITS OWN stay set read off the artifact's own
tables (bytes whose step leaves the machine in that seed). No pattern fact,
no FIND: the machine's own escapes. Writes NAME-autoseed/ from NAME-auto/."""
import os, re, sys
root = sys.argv[1]
for d in sorted(os.listdir(root)):
    if not d.endswith('-auto'): continue
    src = open(os.path.join(root, d, 'rx.c')).read()
    i = src.index('static int rx_prefilter(')
    def arr(name):
        m = re.search(r'%s\[(\d+)\] = \{([^}]*)\}' % name, src[i:])
        return [int(x) for x in m.group(2).replace('\n', ' ').split(',') if x.strip()]
    cls = arr('rx_forward_byte_class'); nxt = arr('rx_forward_next_state'); seeds = sorted(set(arr('rx_forward_seed_state')))
    extra = [s for s in seeds if s != 0]
    tabs, conds = '', ''
    for s in extra:
        stay = [1 if nxt[s + cls[b]] == s else 0 for b in range(256)]
        rows = ',\n'.join('    ' + ','.join(map(str, stay[k:k+32])) for k in range(0, 256, 32))
        tabs += f'static const unsigned char p9_seedstay{s}[256] = {{\n{rows}\n}};\n'
        conds += (f'        else if (forward_state == {s} && last_accept_position == (size_t)-1) {{\n'
                  f'            while (scan_position + 1 < subject_length && p9_seedstay{s}[subject[scan_position]]) scan_position++;\n'
                  f'        }}\n')
        print(d, 'seed', s, 'stays on', sum(stay), 'bytes')
    out = src[:i] + tabs + src[i:]
    j = out.index('        if (forward_state == 0 && last_accept_position == (size_t)-1) {')
    k = out.index('\n        }\n', j) + len('\n        }\n')
    out = out[:k] + conds + out[k:]
    # the original `else if` chain continues after our inserted branches
    od = os.path.join(root, d[:-5] + '-autoseed'); os.makedirs(od, exist_ok=True)
    open(os.path.join(od, 'rx.c'), 'w').write(out)
    for h in os.listdir(os.path.join(root, d)):
        if h.endswith('.h'): open(os.path.join(od, h), 'w').write(open(os.path.join(root, d, h)).read())
