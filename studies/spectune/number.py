#!/usr/bin/env python3
"""Lane spectune one-time numbering pass (adapted from studies/specnum/number.py,
mirroring tests/spec_history/specdoc.py's unit rule). IN OUT."""
import re, sys
sys.path.insert(0, sys.argv[3])
import specdoc
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
out = []; sec = '0'; k = {}; fence = False; after_fence = False; prev_blank = True; in_toc = False
for i, l in enumerate(L):
    if l.strip() == specdoc.TOC_BEGIN: in_toc = True; out.append(l); continue
    if l.strip() == specdoc.TOC_END: in_toc = False; prev_blank = False; out.append(l); continue
    if in_toc: out.append(l); continue
    if fence:
        if l.lstrip().startswith('```'): fence = False; after_fence = True
        out.append(l); continue
    if not l.strip(): prev_blank = True; out.append(l); continue
    m = specdoc.HEAD.match(l)
    if m and len(m.group(1)) >= 2:
        sec = m.group(2)
        out.append('<a id="%s"></a>' % specdoc.anchor_of(sec)); out.append(l)
        after_fence = False; prev_blank = False; continue
    if l.startswith('#') and re.match(r'#{1,6}\s', l): prev_blank = False; out.append(l); continue
    if l.startswith('```'): fence = True; out.append(l); continue
    if l.startswith('<!--') or l.startswith('|'): prev_blank = False; out.append(l); continue
    start = (prev_blank and not l.startswith(' ')) or bool(specdoc.ITEM.match(l))
    if after_fence and l[0].islower(): start = False
    after_fence = False; prev_blank = False
    if start:
        k[sec] = k.get(sec, 0) + 1
        lab = '<a id="%s"></a>[%s¶%d] ' % (specdoc.para_anchor_of(sec, k[sec]), sec, k[sec])
        mm = re.match(r'^((?:[-*]|\d+[.)])\s+|>\s+)', l)
        if mm: l = mm.group(1) + lab + l[mm.end():]
        else: l = lab + l
    out.append(l)
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
