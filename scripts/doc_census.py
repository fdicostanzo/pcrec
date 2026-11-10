#!/usr/bin/env python3
"""doc_census.py -- the decisions addendum census and its OWNER TABLE
([DOC-INDEX] unit 1.0; design docs/design/doc_index_format.md §2.2, §5.2;
appendix A and B).

Scans EVERY line of a decisions file, classifies each line that mentions an
addendum as a MARKER (its leading label names an addendum) or a MENTION, and
derives one owner-table row per marker: its EXTENT, extent hash, full old
label, class, owner, new `Dn.aN` id, date, who and title. Id-less markers,
ruled extents and ruled numbers come from the committed HAND RULINGS file;
the census never guesses an owner by position.

This script is independent of any converter (§5.1 question 2): the converter
copies rows, it never derives them, and doc_control.py checks a conversion
against this table.

Usage:
  doc_census.py [--file F | --rev SHA] [--rulings R] [--table T] MODE
  MODES
    --summary     counts by class (markers / mentions), then `doc_census: DONE`
    --list        one line per candidate: MARK|MENTION line class label [reason]
    --emit        write the owner table to --table (default the committed one)
    --check       gate: (a) id-less marker without a ruling, (b) a line-start
                  foreign `Dm ADDENDUM|addendum|add.` with no table row,
                  (c) an old heading in the new grammar, plus: the committed
                  table equals a fresh derivation (rows compared without
                  census_rev; a missing/extra/changed row fails), and every
                  ruling is used. Exit 1 on any failure.
    --selftest    fixture plants (P20 and the gate's own cases); exit 1 on miss

Every run ends with one `doc_census: DONE rc=N` line.
Run with `python3 -I` (stdlib only).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEF_FILE = 'docs/dev/decisions.md'
DEF_TABLE = 'docs/dev/doc_index/decisions_owners.tsv'
DEF_RULINGS = 'docs/dev/doc_index/decisions_owner_rulings.tsv'

COLUMNS = ['census_rev', 'old_line', 'old_end', 'extent_hash', 'old_label',
           'class', 'owner', 'owner_src', 'old_number', 'new_id', 'date',
           'who', 'title', 'cites', 'note']
RULING_COLUMNS = ['host', 'old_label', 'owner', 'number', 'old_end', 'title',
                  'date', 'reason']

# --- the scan (§5.2, appendix A) -------------------------------------------

PREFIX = re.compile(r'^(?P<q>> ?)?(?P<b>(?:- |\* |[0-9]+\. ))?(?P<s>\*\*|#{2,6} )?')
CANDIDATE = re.compile(r'addend|\bD[0-9]+ add\.', re.I)
ORD_WORDS = ['first', 'second', 'third', 'fourth', 'fifth']
ORDINAL = '|'.join(ORD_WORDS + [w.upper() for w in ORD_WORDS]
                   + [w.capitalize() for w in ORD_WORDS])
LABEL = re.compile(r'^(?:D[0-9]+ )?(?:[A-Z][A-Z0-9-]*[0-9] )?(?:(?:' + ORDINAL
                   + r') )?(?:addendum|ADDENDUM|Addendum)'
                   r'(?: [0-9]+(?:\.[0-9]+)?[a-z]?| [0-9]{4}-[0-9]{2}-[0-9]{2})?'
                   r'(?: note| NOTE)?(?:,.*)?$')
LABEL_PARTS = re.compile(r'^(?:D(?P<id>[0-9]+) )?(?:[A-Z][A-Z0-9-]*[0-9] )?'
                         r'(?:(?P<ord>' + ORDINAL + r') )?(?:addendum|ADDENDUM|Addendum)'
                         r'(?: (?P<dnum>[0-9]{4}-[0-9]{2}-[0-9]{2})| (?P<num>[0-9]+(?:\.[0-9]+)?[a-z]?))?'
                         r'(?P<note> note| NOTE)?')
CUT = re.compile(r' — | -- |\(|:')
ENTRY_HEAD = re.compile(r'^## D([0-9]+)\b')
FOREIGN = re.compile(r'^D([0-9]+) (?:ADDENDUM|addendum|add\.)')
NEW_GRAMMAR = re.compile(r'^(## D[0-9]+ (?:[a-z0-9]+(?:-[a-z0-9]+)*|-) — |### D[0-9]+\.a[0-9])')
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
WHO = {'frank': 'Frank', 'owner': 'owner', 'manager': 'manager', 'kit': 'kit'}


def classify(line):
    m = PREFIX.match(line)
    q, b, s = m.group('q'), m.group('b'), m.group('s')
    rest = line[m.end():]
    if s and s.startswith('#'):
        cls = 'h%d' % s.count('#')
    elif q:
        cls = 'quote'
    elif b and s == '**':
        cls = 'bullet-bold'
    elif s == '**':
        cls = 'bold'
    elif b:
        cls = 'bullet'
    else:
        cls = 'plain'
    return cls, rest, m.end()


def bold_span(lines, i, rest):
    """The bold span starting at `rest` (after its opening `**`), joined
    across its wrap; returns (span, line index where it closes, text after)."""
    parts = []
    j = i
    cur = rest
    while True:
        k = cur.find('**')
        if k >= 0:
            parts.append(cur[:k])
            return ' '.join(p.strip() for p in parts if p.strip()), j, cur[k + 2:]
        parts.append(cur)
        j += 1
        if j >= len(lines) or j - i > 6 or not lines[j].strip():
            return ' '.join(p.strip() for p in parts if p.strip()), i, ''
        cur = lines[j]


def first_group(text):
    """(start, end) of the first balanced (...) group in text, or None."""
    k = text.find('(')
    if k < 0:
        return None
    depth = 0
    for j in range(k, len(text)):
        if text[j] == '(':
            depth += 1
        elif text[j] == ')':
            depth -= 1
            if depth == 0:
                return k, j + 1
    return k, len(text)


def group_open(text):
    """True when text's first (...) group does not close within it."""
    k = text.find('(')
    if k < 0:
        return False
    depth = 0
    for ch in text[k:]:
        depth += (ch == '(') - (ch == ')')
        if depth == 0:
            return False
    return True


def groups(text):
    out = []
    pos = 0
    while True:
        g = first_group(text[pos:])
        if not g:
            return out
        out.append((pos + g[0], pos + g[1]))
        pos += g[1]
        if pos >= len(text):
            return out


def is_dw_group(content):
    items = [x.strip() for x in content.split(',')]
    if DATE.search(content) or re.search(r'\bsame (exchange|day|session)\b', content):
        return True
    return any(it.split(' ')[0].lower().rstrip("'s") in WHO for it in items[:2])


def scan(lines):
    """Every candidate line: dict(line, cls, label, marker, reason, ...)."""
    out = []
    host = None
    for i, line in enumerate(lines):
        m = ENTRY_HEAD.match(line)
        cls, rest, plen = classify(line)
        if m and not LABEL.match(CUT.split(line[3:], 1)[0].strip()):
            host = int(m.group(1))
        if not CANDIDATE.search(rest[:120]):
            continue
        c = dict(line=i + 1, cls=cls, host=host, raw=line)
        after = ''
        close = i
        if cls.startswith('h'):
            span = rest
        elif cls in ('bold', 'bullet-bold'):
            span, close, after = bold_span(lines, i, rest)
        else:
            # a plain label's (...) group may wrap: join until it closes
            span = rest
            while group_open(span[len(CUT.split(span, 1)[0]):]) and close + 1 < len(lines) \
                    and close - i < 6 and lines[close + 1].strip():
                close += 1
                span += ' ' + lines[close].strip()
        label = CUT.split(span, 1)[0].strip()
        c['label'] = label
        c['span'] = span
        c['after'] = after
        c['close'] = close
        if not LABEL.match(label):
            c['marker'] = False
            c['reason'] = 'leading label is not an addendum label'
        elif cls == 'plain' and not re.match(r'D[0-9]+ ', label):
            c['marker'] = False
            c['reason'] = 'plain line without a leading id (a wrapped sentence)'
        elif cls not in ('h2', 'h3', 'h4', 'bold', 'bullet-bold', 'plain'):
            c['marker'] = False
            c['reason'] = 'class %s carries no marker form' % cls
        else:
            c['marker'] = True
            c['reason'] = ''
        out.append(c)
    return out


# --- rows (appendix B) ------------------------------------------------------

def read_tsv(path, columns):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding='utf-8') as f:
        head = None
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#'):
                continue
            parts = ln.split('\t')
            if head is None:
                head = parts
                if head != columns:
                    raise SystemExit('doc_census: %s: header %r != %r' % (path, head, columns))
                continue
            if len(parts) != len(columns):
                raise SystemExit('doc_census: %s: row has %d fields: %r' % (path, len(parts), ln[:80]))
            rows.append(dict(zip(columns, parts)))
    return rows


def old_label_of(c):
    cls = c['cls']
    if cls.startswith('h'):
        return c['span'].strip()
    if cls in ('bold', 'bullet-bold'):
        return c['span'].strip()
    # plain: the label through its first (...) group
    span = c['span']
    lab = c['label']
    tail = span[len(lab):] if span.startswith(lab) else span
    g = first_group(tail)
    if g and not tail[:g[0]].strip(' —:-'):
        return (lab + tail[:g[1]]).strip()
    return lab


def ext_hash(lines, a, b):
    data = ''.join(l + '\n' for l in lines[a - 1:b])
    return hashlib.sha256(data.encode('utf-8')).hexdigest()[:12]


def heading_date(line):
    d = DATE.search(line)
    return d.group(0) if d else None


def num_key(n):
    m = re.match(r'^([0-9]+)(?:\.([0-9]+))?([a-z]?)$', n)
    return (int(m.group(1)), int(m.group(2) or 0), m.group(3))


def sentence(text):
    text = ' '.join(text.split())
    m = re.search(r'(?<![0-9])(?<!\b[A-Za-z])(?<!e\.g)(?<!i\.e)(?<!\bvs)(?<!\bcf)[.!?](?=\s|$)', text)
    return text[:m.end()] if m else text


def cut120(t):
    t = ' '.join(t.split())
    if len(t) <= 120:
        return t
    cut = t[:120]
    if t[120] != ' ' and ' ' in cut:
        cut = cut[:cut.rfind(' ')]
    return cut.rstrip() + '…'


def derive(lines, rulings, rev, cites=None):
    """Rows for every marker. Returns (rows, problems, used_rulings)."""
    cands = scan(lines)
    marks = [c for c in cands if c['marker']]
    problems = []
    rmap = {}
    for r in rulings:
        rmap.setdefault((r['host'], r['old_label']), []).append(r)
    used = set()
    entry_line = {}
    entry_date = {}
    for i, l in enumerate(lines):
        m = ENTRY_HEAD.match(l)
        if m and not LABEL.match(CUT.split(l[3:], 1)[0].strip()):
            entry_line.setdefault(int(m.group(1)), i + 1)
            entry_date.setdefault(int(m.group(1)), heading_date(' '.join(lines[i:i + 3]) if int(m.group(1)) == 98 else l))
    # extent ends: next marker or next `## ` heading
    starts = sorted(c['line'] for c in marks)
    h2s = [i + 1 for i, l in enumerate(lines) if l.startswith('## ')]
    rows = []
    seen_key = {}
    for c in marks:
        lab = old_label_of(c)
        hostid = 'D%d' % c['host'] if c['host'] is not None else '-'
        key = (hostid, lab)
        seen_key[key] = seen_key.get(key, 0) + 1
        rl = rmap.get(key, [])
        rul = rl[seen_key[key] - 1] if len(rl) >= seen_key[key] else None
        if rul:
            used.add((key, seen_key[key]))
        nxt = [s for s in starts if s > c['line']] + [h for h in h2s if h > c['line']] + [len(lines) + 1]
        end = min(nxt) - 1
        while end > c['line'] and not lines[end - 1].strip():
            end -= 1
        if rul and rul['old_end'] not in ('', '-'):
            m = re.match(r'^lines:([0-9]+)$', rul['old_end'])
            if not m:
                problems.append('ruling %s/%s: old_end %r is not lines:N' % (hostid, lab, rul['old_end']))
            else:
                end = c['line'] + int(m.group(1)) - 1
        p = LABEL_PARTS.match(c['label'])
        lid = p.group('id')
        note = bool(p.group('note'))
        if rul and rul['owner'] not in ('', '-'):
            owner = rul['owner']
            src = 'ruled' if (lid is None and owner != hostid) or (lid and owner != 'D' + lid) else (
                'enclosure' if lid is None else 'label')
            if lid and owner != 'D' + lid:
                problems.append('%s: ruling gives owner %s against the label id D%s' % (lab, owner, lid))
        elif lid:
            owner, src = 'D' + lid, 'label'
        else:
            owner, src = None, None
            problems.append('(a) id-less marker without a hand ruling: line %d in %s: %r' % (c['line'], hostid, lab))
        if p.group('num'):
            old_number = p.group('num')
        elif p.group('ord'):
            old_number = p.group('ord').lower()
        elif p.group('dnum'):
            old_number = p.group('dnum')
        else:
            old_number = '-'
        # the date/who group
        cut_at = len(c['label'])
        span = c['span'] if c['cls'] != 'plain' else lab
        tail = span[cut_at:] if span.startswith(c['label']) else span
        gtext = None
        rem = tail
        for (a, b) in groups(tail):
            inner = tail[a + 1:b - 1]
            if is_dw_group(inner):
                gtext = inner
                rem = tail[:a] + tail[b:]
                break
        date = None
        if p.group('dnum'):
            date = p.group('dnum')
        elif gtext and DATE.search(gtext):
            date = DATE.search(gtext).group(0)
        else:
            # a date right after the label, outside any group (`D11 addendum — 2026-08-09 (...)`)
            md = re.match(r'^\s*(?:—|--|,|:)?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\b', rem)
            if md:
                date = md.group(1)
                rem = rem[md.end():]
        ruled_date = bool(rul and rul['date'] not in ('', '-'))
        if ruled_date:
            date = rul['date']
        who = '-'
        if gtext:
            for it in [x.strip() for x in gtext.split(',')][:2]:
                w = it.split(' ')[0].rstrip("'s").lower() if it else ''
                if w in WHO:
                    who = WHO[w]
                    break
        # title (appendix B title rule)
        title = rem.strip(' \t—-:,.;')
        trule = 1
        if not title and not c['cls'].startswith('h'):
            trule = 2
            if c['cls'] in ('bold', 'bullet-bold'):
                after = c['after']
                j = c['close']
            else:
                after = c['span'][len(lab):] if c['span'].startswith(lab) else ''
                j = c['close']
            para = [after]
            k = j + 1
            while k < len(lines) and lines[k].strip() and not lines[k].startswith(('#', '- ', '* ', '> ')) \
                    and not re.match(r'^[0-9]+\. ', lines[k]):
                para.append(lines[k])
                k += 1
            title = sentence(' '.join(para)).strip(' \t—-:,')
        if not title:
            trule = 3
            if gtext:
                items = [x.strip() for x in re.split(r',|;| — ', gtext)]
                keep = [x for x in items if x and not re.match(r'^~?[0-9]{4}-[0-9]{2}-[0-9]{2}\b', x)
                        and x.split(' ')[0].rstrip("'s").lower() not in WHO
                        and 'session' not in x and not x.startswith('same ')]
                title = ', '.join(keep)
        if not title:
            trule = 4
            title = '(untitled)'
        if rul and rul['title'] not in ('', '-'):
            title = rul['title']
            trule = 'ruled'
        rows.append(dict(c=c, old_line=c['line'], old_end=end, label=lab, owner=owner, src=src,
                         old_number=old_number, note=note, date=date, who=who,
                         title=cut120(title), trule=trule, rul=rul, host=hostid, ruled_date=ruled_date,
                         ruled_end=bool(rul and rul['old_end'] not in ('', '-'))))
    # dates: inherit the nearest earlier dated marker of the same owner
    by_owner = {}
    for r in rows:
        if r['owner']:
            by_owner.setdefault(r['owner'], []).append(r)
    for owner, rs in by_owner.items():
        last = None
        for r in sorted(rs, key=lambda r: r['old_line']):
            if r['date']:
                last = r['date']
                r['date_col'] = r['date']
            else:
                d = last or entry_date.get(int(owner[1:]))
                r['date_col'] = 'inherit:%s' % d if d else '-'
                r['date'] = d
    # numbering (§2.2)
    for owner, rs in by_owner.items():
        taken = {}
        unnumbered = []
        dups = []
        for r in sorted(rs, key=lambda r: r['old_line']):
            if r['note']:
                continue
            n = None
            if r['rul'] and r['rul']['number'] not in ('', '-'):
                n = r['rul']['number']
                r['ruled_num'] = True
            elif re.match(r'^[0-9]', r['old_number']) and not DATE.match(r['old_number']):
                n = r['old_number']
            elif r['old_number'] in ORD_WORDS:
                n = str(ORD_WORDS.index(r['old_number']) + 1)
            if n is None:
                unnumbered.append(r)
            elif n in taken:
                dups.append(r)
            else:
                taken[n] = r
                r['num'] = n
        free = lambda: next(str(k) for k in range(1, 10000) if str(k) not in taken)
        for r in sorted(unnumbered, key=lambda r: (r['date'] or '9999', r['old_line'])):
            n = free()
            taken[n] = r
            r['num'] = n
        for r in dups:
            first = taken[r['old_number'] if r['old_number'] in taken else r.get('num', '')]
            n = free()
            taken[n] = r
            r['num'] = n
            r['dup_of'] = r['old_number']
        notes_on = {}
        for r in sorted(rs, key=lambda r: r['old_line']):
            if r['note']:
                base = r['old_number']
                notes_on[base] = notes_on.get(base, 0) + 1
                r['num'] = '%s#%d' % (base, notes_on[base])
    out = []
    for r in rows:
        cls = 'note' if r['note'] else r['c']['cls']
        notes = []
        if r['src'] == 'ruled' or r['src'] == 'enclosure':
            notes.append(r['rul']['reason'])
        elif r['rul'] and r['rul']['reason']:
            notes.append(r['rul']['reason'])
        if r.get('dup_of'):
            notes.append('second of two')
        if r['trule'] == 'ruled':
            notes.append('title ruled')
        if r['ruled_date']:
            notes.append('date ruled')
        new_id = '%s.a%s' % (r['owner'], r['num']) if r['owner'] and 'num' in r else '-'
        out.append({
            'census_rev': rev, 'old_line': str(r['old_line']), 'old_end': str(r['old_end']),
            'extent_hash': ext_hash(lines, r['old_line'], r['old_end']),
            'old_label': r['label'], 'class': cls, 'owner': r['owner'] or '-',
            'owner_src': r['src'] or '-', 'old_number': r['old_number'], 'new_id': new_id,
            'date': r.get('date_col', '-'), 'who': r['who'], 'title': r['title'],
            'cites': str(cites.get((r['owner'], r['old_number']), 0)) if cites is not None else '-',
            'note': '; '.join(n for n in notes if n) or '-',
            '_host': r['host'], '_trule': r['trule'],
        })
    for (key, lst) in rmap.items():
        for k in range(len(lst)):
            if (key, k + 1) not in used:
                problems.append('ruling unused (no marker %s in %s): %r' % (key[1], key[0], key[1]))
    return cands, out, problems


def gate(lines, cands, rows):
    """Gates (b) and (c) of §5.2; (a) is raised by derive()."""
    problems = []
    rowlines = {int(r['old_line']) for r in rows}
    host = None
    for i, line in enumerate(lines):
        m = ENTRY_HEAD.match(line)
        if m and not LABEL.match(CUT.split(line[3:], 1)[0].strip()):
            host = int(m.group(1))
        if NEW_GRAMMAR.match(line):
            problems.append('(c) line %d: an old heading already in the new grammar: %r' % (i + 1, line[:80]))
        cls, rest, _ = classify(line)
        f = FOREIGN.match(rest)
        if f and host is not None and int(f.group(1)) != host and (i + 1) not in rowlines:
            problems.append('(b) line %d: line-start D%s addendum inside D%d with no table row: %r'
                            % (i + 1, f.group(1), host, line[:80]))
    return problems


# --- tree cites (the `cites` column) ---------------------------------------

CITE = re.compile(r'\bD([0-9]+) (?:(' + ORDINAL + r') )?(?:add\.|addendum|ADDENDUM|Addendum)'
                  r'(?: ([0-9]+(?:\.[0-9]+)?[a-z]?|[0-9]{4}-[0-9]{2}-[0-9]{2})\b)?'
                  r'|\baddendum ([0-9]+(?:\.[0-9]+)?[a-z]?) of D([0-9]+)\b')


def tree_cites(root, rev):
    """Counts of (owner, old_number) cites in the tree at rev, minus the
    decisions file itself and docs/dev/doc_index/."""
    try:
        out = subprocess.run(['git', '-C', root, 'grep', '-I', '-h', '-o', '-E',
                              r'D[0-9]+ ([A-Za-z]+ )?(add\.|addendum|ADDENDUM|Addendum)( [0-9][0-9.a-z-]*)?|addendum [0-9][0-9.a-z]* of D[0-9]+',
                              rev, '--', '.', ':!' + DEF_FILE, ':!docs/dev/doc_index/'],
                             capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    counts = {}
    for ln in out.splitlines():
        m = CITE.search(ln)
        if not m:
            continue
        if m.group(5):
            key = ('D' + m.group(5), m.group(4))
        else:
            num = m.group(3)
            if num and not DATE.match(num):
                num = num.rstrip('.')
            key = ('D' + m.group(1), m.group(2).lower() if m.group(2) else (num or '-'))
        counts[key] = counts.get(key, 0) + 1
    return counts


# --- I/O --------------------------------------------------------------------

def load(args):
    if args.rev:
        txt = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (args.rev, DEF_FILE)],
                             capture_output=True, text=True, check=True).stdout
        rev = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short=9', args.rev],
                             capture_output=True, text=True, check=True).stdout.strip()
    else:
        with open(args.file, encoding='utf-8') as f:
            txt = f.read()
        rev = args.census_rev or subprocess.run(
            ['git', '-C', ROOT, 'rev-parse', '--short=9', 'HEAD'],
            capture_output=True, text=True).stdout.strip() or '-'
    return txt.split('\n')[:-1] if txt.endswith('\n') else txt.split('\n'), rev


def write_table(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(COLUMNS) + '\n')
        for r in rows:
            f.write('\t'.join(r[c] for c in COLUMNS) + '\n')


CMP = [c for c in COLUMNS if c not in ('census_rev', 'cites')]


def compare(committed, fresh):
    problems = []
    ck = {(r['old_label'], r['extent_hash']): r for r in committed}
    fk = {(r['old_label'], r['extent_hash']): r for r in fresh}
    for k, r in fk.items():
        if k not in ck:
            problems.append('marker with no table row: line %s %r (extent %s)' % (r['old_line'], k[0][:70], k[1]))
            continue
        c = ck[k]
        for col in CMP:
            if c[col] != r[col]:
                problems.append('row %r: %s committed %r, derived %r' % (k[0][:50], col, c[col][:60], r[col][:60]))
    for k, r in ck.items():
        if k not in fk:
            problems.append('table row with no marker: %r (extent %s)' % (k[0][:70], k[1]))
    if len(committed) != len(ck):
        problems.append('table has duplicate (old_label, extent_hash) keys')
    return problems


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--file', default=os.path.join(ROOT, DEF_FILE))
    ap.add_argument('--rev')
    ap.add_argument('--census-rev')
    ap.add_argument('--rulings', default=os.path.join(ROOT, DEF_RULINGS))
    ap.add_argument('--table', default=os.path.join(ROOT, DEF_TABLE))
    ap.add_argument('--no-cites', action='store_true')
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ('summary', 'list', 'emit', 'check', 'selftest', 'rulings-todo'):
        g.add_argument('--' + m, action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    lines, rev = load(args)
    rulings = read_tsv(args.rulings, RULING_COLUMNS)
    cites = None
    if args.emit and not args.no_cites:
        cites = tree_cites(ROOT, args.rev or 'HEAD')
    cands, rows, problems = derive(lines, rulings, rev, cites)
    if args.summary or args.list:
        mk = [c for c in cands if c['marker']]
        mn = [c for c in cands if not c['marker']]
        def by(xs):
            d = {}
            for x in xs:
                d[x['cls']] = d.get(x['cls'], 0) + 1
            return ', '.join('%s %d' % kv for kv in sorted(d.items()))
        print('candidates %d = markers %d + mentions %d' % (len(cands), len(mk), len(mn)))
        print('markers by class: %s' % by(mk))
        print('mentions by class: %s' % by(mn))
        print('id-less markers: %d' % sum(1 for c in mk if not re.match(r'D[0-9]+ ', c['label'])))
        if args.list:
            for c in cands:
                print('%s\t%d\t%s\tD%s\t%s\t%s' % ('MARK' if c['marker'] else 'MENTION', c['line'], c['cls'],
                                                c['host'], c['label'][:70], c['reason']))
    if args.rulings_todo:
        for r in rows:
            if r['owner'] == '-' or r['owner_src'] in ('ruled', 'enclosure'):
                print('%s\t%s\t%s\t%s' % (r['_host'], r['old_label'], r['old_line'], r['owner']))
    rc = 0
    if args.emit:
        if problems:
            for p in problems:
                print('doc_census: FAIL ' + p)
            rc = 1
        else:
            write_table(args.table, rows)
            print('doc_census: wrote %d rows to %s' % (len(rows), os.path.relpath(args.table, ROOT)))
    if args.check:
        problems += gate(lines, cands, read_tsv(args.table, COLUMNS))
        problems += compare(read_tsv(args.table, COLUMNS), rows)
        for p in problems:
            print('doc_census: FAIL ' + p)
        print('doc_census: check %d markers, %d mentions, %d table rows, %d problems'
              % (sum(1 for c in cands if c['marker']), sum(1 for c in cands if not c['marker']),
                 len(read_tsv(args.table, COLUMNS)), len(problems)))
        rc = 1 if problems else 0
    print('doc_census: DONE rc=%d' % rc)
    return rc


# --- selftest ---------------------------------------------------------------

FIXTURE = """# Decisions

## D121 — 2026-10-01 — toy entry one (Frank, 2026-10-01)

Body of D121.

D121 ADDENDUM 2 (2026-10-03, same exchange): second plain-line addendum.

## D122 — toy entry two (Frank, 2026-10-02)

Body of D122.

D122 ADDENDUM (2026-10-02, Frank): the first one.

D122 ADDENDUM 2 (same exchange): the second one.

ADDENDUM, is a wrapped sentence and no marker.

## D123 — toy entry three (owner, 2026-10-04)

Body of D123.

D122 ADDENDUM 4 (2026-10-05, same exchange): placed inside D123.

**Addendum 2 (2026-10-06):** an id-less one, ruled to D122.
"""

FIX_RULINGS = """host\told_label\towner\tnumber\told_end\ttitle\tdate\treason
D123\tAddendum 2 (2026-10-06):\tD122\t3\t-\t-\t-\tfixture ruling
"""


def selftest():
    import tempfile
    fails = []
    lines = FIXTURE.split('\n')[:-1]
    rul = []
    head = None
    for ln in FIX_RULINGS.strip('\n').split('\n'):
        p = ln.split('\t')
        if head is None:
            head = p
        else:
            rul.append(dict(zip(head, p)))
    cands, rows, problems = derive(lines, rul, 'fixture')
    def expect(cond, what):
        print('selftest: %s %s' % ('ok  ' if cond else 'MISS', what))
        if not cond:
            fails.append(what)
    expect(not problems, 'clean fixture derives with no problems (%s)' % problems)
    p20 = [r for r in rows if r['old_label'].startswith('D122 ADDENDUM 4')]
    expect(len(p20) == 1 and p20[0]['owner'] == 'D122' and p20[0]['_host'] == 'D123',
           'P20: plain-line D122 ADDENDUM 4 inside D123 is a row with owner D122')
    expect(any(not c['marker'] and c['raw'].startswith('ADDENDUM, is') for c in cands),
           'R2-13: the wrapped "ADDENDUM, is ..." line is a mention')
    expect(not gate(lines, cands, rows), 'gate (b) quiet with the full table')
    cut = [r for r in rows if r is not p20[0]]
    expect(any(p.startswith('(b) ') for p in gate(lines, cands, cut)),
           'P20: gate (b) fails when the D122 ADDENDUM 4 row is deleted')
    expect(any('marker with no table row' in p for p in compare(cut, rows)),
           'P20: --check reports the deleted row as a marker with no table row')
    _, _, pr = derive(lines, [], 'fixture')
    expect(any(p.startswith('(a) ') for p in pr), 'gate (a): the id-less marker without a ruling fails')
    lines_c = lines + ['## D124 slug-here — a converted heading', '### D124.a1 — 2026-10-07: x']
    cc, rc_, _ = derive(lines_c, rul, 'fixture')
    expect(sum(p.startswith('(c) ') for p in gate(lines_c, cc, rc_)) == 2,
           'gate (c): an old heading in the new grammar fails (## and ###)')
    ids = {r['old_label'][:16]: r['new_id'] for r in rows}
    expect(ids.get('D122 ADDENDUM (2') == 'D122.a1' and ids.get('D122 ADDENDUM 2 ') == 'D122.a2'
           and ids.get('D122 ADDENDUM 4 ') == 'D122.a4' and ids.get('Addendum 2 (2026') == 'D122.a3',
           'numbering: unnumbered -> a1, ruled number kept (%s)' % ids)
    inh = [r for r in rows if r['old_label'].startswith('D122 ADDENDUM 2')][0]
    expect(inh['date'] == 'inherit:2026-10-02', 'undated label inherits the earlier marker date (%s)' % inh['date'])
    d121 = [r for r in rows if r['owner'] == 'D121'][0]
    expect(d121['new_id'] == 'D121.a2' and d121['date'] == '2026-10-03', 'D121 numbered plain marker')
    rc = 1 if fails else 0
    print('doc_census: selftest %d miss(es)' % len(fails))
    print('doc_census: DONE rc=%d' % rc)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
