#!/usr/bin/env python3
"""studies/specnum/repoint.py -- ONE-TIME: rewrite the tree's `match_api.md#anchor`
citations (lane specclean's form) to the numbered form `match_api.md §N¶k`
(lane specnum), using anchor_map.tsv (old semantic <a id> -> new label/anchor).

  repoint.py [--apply]     dry run by default; prints each changed line

Rules (the same for every tracked text file, minus EXCLUDE):
  * `...match_api.md#SEM` inside a markdown link target  -> `...match_api.md#ANCHOR`
  * `match_api.md#SEM` elsewhere                         -> `match_api.md §LABEL`
  * a bare `#SEM` on a line that names match_api         -> `§LABEL`
  * then `§S (`§S¶k`)`-style redundancy collapses to `§S¶k`.
"""
import re
import subprocess
import sys

EXCLUDE = ('studies/specclean/', 'studies/specnum/', 'docs/spec/match_api.md',
           'docs/dev/lanes/specclean_report.md', 'docs/dev/history/match_api_record.md')

amap = {}
for l in open('studies/specnum/anchor_map.tsv', encoding='utf-8'):
    a, lab, anc, kind = l.rstrip('\n').split('\t')
    amap[a] = (lab, anc)
IDS = '|'.join(sorted((re.escape(i) for i in amap), key=len, reverse=True))
FILEREF = re.compile(r'(match_api(?:\.md)?)#(' + IDS + r')(?![\w-])')
BARE = re.compile(r'(?<![\w/&#.-])#(' + IDS + r')(?![\w-])')
# redundancy: "§S ... §S¶k" where both name the same section
S = r'(\d+(?:\.\d+)*[a-z]?)'
RED = [
    re.compile(r"§" + S + r"((?:'s)?)\s*\(`?§" + S + r"(¶\d+[a-z]?)?`?\)"),
    re.compile(r"§" + S + r"((?:'s)?),\s*`?§" + S + r"(¶\d+[a-z]?)?`?"),
    re.compile(r"§" + S + r"((?:'s)?)\s+`§" + S + r"(¶\d+[a-z]?)?`"),
    re.compile(r"§" + S + r"((?:'s)?) §" + S + r"(¶\d+[a-z]?)?(?![\w.])"),
]


def collapse(line):
    for rx in RED:
        def sub(m):
            g1, g3 = m.group(1), m.group(3)
            if not (g1 == g3 or g3.startswith(g1 + '.')):
                return m.group(0)   # names a section outside the cited one: keep both
            return '§%s%s%s' % (g3, m.group(4) or '', m.group(2))
        # "'s" goes after the full label
        line = rx.sub(sub, line)
    return line


def rewrite(line, ctx=False):
    def f1(m):
        lab, anc = amap[m.group(2)]
        # markdown link target?  ](...match_api.md#SEM)
        pre = line[:m.start()]
        if re.search(r'\]\([^)\s]*$', pre):
            return '%s#%s' % (m.group(1), anc)
        return '%s §%s' % (m.group(1), lab)
    new = FILEREF.sub(f1, line)
    if 'match_api' in new or ctx:
        new = BARE.sub(lambda m: '§' + amap[m.group(1)][0], new)
    return collapse(new) if new != line else line


def main():
    apply = '--apply' in sys.argv
    files = subprocess.run(['git', 'ls-files', '-z'], capture_output=True).stdout.split(b'\0')
    nfiles = nlines = 0
    left = []
    for f in files:
        f = f.decode()
        if not f or f.startswith(EXCLUDE):
            continue
        try:
            text = open(f, encoding='utf-8').read()
        except Exception:
            continue
        out = []
        changed = False
        lines = text.split('\n')
        for n, line in enumerate(lines, 1):
            ctx = any('match_api' in x for x in lines[max(0, n - 4):n - 1])
            new = rewrite(line, ctx)
            if new != line:
                changed = True
                nlines += 1
                if not apply:
                    print('%s:%d:\n  - %s\n  + %s' % (f, n, line.strip()[:230], new.strip()[:230]))
            out.append(new)
            if BARE.search(new):
                left.append('%s:%d: %s' % (f, n, new.strip()[:160]))
        if changed:
            nfiles += 1
            if apply:
                open(f, 'w', encoding='utf-8').write('\n'.join(out))
    print('changed lines %d in %d files' % (nlines, nfiles), file=sys.stderr)
    print('\nBARE #SEM LEFT (line names no match_api):', file=sys.stderr)
    for x in left:
        print('  ' + x, file=sys.stderr)


main()
