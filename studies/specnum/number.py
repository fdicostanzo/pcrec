#!/usr/bin/env python3
"""studies/specnum/number.py -- ONE-TIME migration: give docs/spec/match_api.md
(as left by lane specclean, c2c11fa4) its hierarchical section and paragraph
numbers.  NOT a maintenance tool: after this runs, numbers are hand-kept under
the stability rule in docs/spec/CLAUDE.md (never renumbered; an insertion takes
a letter suffix).  Re-running it on a numbered document is refused.

  number.py IN.md OUT.md MAP.tsv

MAP.tsv (sem_id, label, anchor, kind) maps each old semantic <a id> to the
section/paragraph it labelled, for re-pointing citations.

Numbering rules (what the check in tests/spec_history/ re-derives):
  * a numbered heading keeps its number; the one unnumbered heading ("Finding
    every match") takes the next free child number of its parent.
  * a UNIT is one prose paragraph, one top-level list item, or one blockquote;
    units are numbered 1, 2, 3 ... within their innermost section, written
    `<section>¶<n>` ("3.2¶4"); the preamble (above the first section heading)
    is section 0.
  * a fenced code block or a table is part of the unit it follows (cited by
    that unit's number); one with no unit before it in its section belongs to
    the section itself.
  * anchors: section 3.2 -> s3-2, paragraph 3.2¶4 -> s3-2-p4.
"""
import re
import sys

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
NUMHEAD = re.compile(r'^(\d+(?:\.\d+)*)\.?\s+(.*)$')
ANCH = re.compile(r'^<a id="([^"]+)"></a>\s*$')
ITEM = re.compile(r'^([-*]|\d+[.)])\s')


def aid(num):
    return 's' + num.replace('.', '-')


def pid(num, k):
    return '%s-p%d' % (aid(num), k)


def main(inp, outp, mapp):
    L = open(inp, encoding='utf-8').read().split('\n')
    if any('¶' in l for l in L):
        sys.exit('already numbered')
    n = len(L)
    out = []          # output lines
    mp = []           # (sem_id, label, anchor, kind)
    # section stack: list of (level, number, child_counter)
    stack = []
    sec = '0'
    kcount = 0        # units in current section
    have_unit = False  # current section has a unit to attach to
    pending = []      # semantic anchor ids waiting for the next element
    fence = False
    after_fence = False   # the last element was a code block (a lowercase
                          # line after it continues that unit's sentence)
    i = 0
    prev_blank = True
    last_host = None  # label of the unit/section anchors would map to

    def child_number(level):
        # next free child number of the nearest shallower numbered section
        while stack and stack[-1][0] >= level:
            stack.pop()
        return stack[-1] if stack else None

    # first pass: collect existing numbered headings so unnumbered ones get a free number
    used = set()
    for l in L:
        m = HEAD.match(l)
        if m and m.group(1) != '#':
            mm = NUMHEAD.match(m.group(2))
            if mm:
                used.add(mm.group(1))

    while i < n:
        l = L[i]
        if fence:
            out.append(l)
            if l.lstrip().startswith('```'):
                fence = False
                after_fence = True
            i += 1
            continue
        if not l.strip():
            out.append(l)
            prev_blank = True
            i += 1
            continue
        # semantic anchor line: remember, drop (replaced below)
        m = ANCH.match(l)
        if m:
            pending.append(m.group(1))
            i += 1
            continue
        m = HEAD.match(l)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            if level == 1:
                out.append(l)
                prev_blank = False
                i += 1
                continue
            mm = NUMHEAD.match(text)
            if mm:
                num = mm.group(1)
                title = mm.group(2)
            else:
                # unnumbered: next free child number of the parent
                par = child_number(level)
                base = par[1]
                k = 1
                while '%s.%d' % (base, k) in used:
                    k += 1
                num = '%s.%d' % (base, k)
                used.add(num)
                title = text
                l = '%s %s %s' % (m.group(1), num, title)
            # maintain stack
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, num))
            depth_ok = num.count('.') + 1
            if mm and depth_ok != level - 1:
                sys.exit('heading level/number mismatch: %r' % l)
            after_fence = False
            sec = num
            kcount = 0
            have_unit = False
            a = aid(num)
            for s in pending:
                mp.append((s, num, a, 'section'))
            pending = []
            out.append('<a id="%s"></a>' % a)
            out.append(l)
            last_host = ('section', num)
            prev_blank = False
            i += 1
            continue
        if l.startswith('---') and not l.strip('-'):
            out.append(l)
            have_unit = False  # a rule ends the section's running text
            prev_blank = False
            i += 1
            continue
        if l.startswith('```'):
            # a code block at block level
            if have_unit:
                host = ('unit', sec, kcount)
            else:
                host = ('section', sec)
            for s in pending:
                mp.append((s, hostlabel(host), hostanchor(host), 'section' if host[0]=='section' else 'paragraph'))
            pending = []
            out.append(l)
            fence = True
            i += 1
            continue
        if l.startswith('<!--') or l.startswith('|'):
            # comment marker / table: attach to the previous unit
            if have_unit:
                host = ('unit', sec, kcount)
            else:
                host = ('section', sec)
            for s in pending:
                mp.append((s, hostlabel(host), hostanchor(host), 'section' if host[0]=='section' else 'paragraph'))
            pending = []
            out.append(l)
            prev_blank = False
            i += 1
            continue
        # prose / list item / quote line
        start_unit = False
        if prev_blank and not l.startswith(' '):
            start_unit = True
        elif ITEM.match(l):
            start_unit = True
        if after_fence and l[0].islower():
            start_unit = False
        after_fence = False
        if not start_unit:
            out.append(l)
            prev_blank = False
            i += 1
            continue
        kcount += 1
        have_unit = True
        lab = '%s¶%d' % (sec, kcount)
        a = pid(sec, kcount)
        for s in pending:
            mp.append((s, lab, a, 'paragraph'))
        pending = []
        tag = '<a id="%s"></a>[%s]' % (a, lab)
        mi = ITEM.match(l)
        if mi:
            head = l[:mi.end()]
            rest = l[mi.end():]
            out.append('%s%s %s' % (head, tag, rest))
        elif l.startswith('> '):
            out.append('> %s %s' % (tag, l[2:]))
        else:
            out.append('%s %s' % (tag, l))
        prev_blank = False
        i += 1
    if pending:
        sys.exit('dangling anchors at end: %r' % pending)
    open(outp, 'w', encoding='utf-8').write('\n'.join(out))
    with open(mapp, 'w', encoding='utf-8') as fh:
        for r in mp:
            fh.write('\t'.join(r) + '\n')


def hostlabel(h):
    return h[1] if h[0] == 'section' else '%s¶%d' % (h[1], h[2])


def hostanchor(h):
    return aid(h[1]) if h[0] == 'section' else pid(h[1], h[2])


if __name__ == '__main__':
    main(*sys.argv[1:4])
