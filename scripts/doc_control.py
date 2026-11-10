#!/usr/bin/env python3
"""doc_control.py -- the per-EXTENT control for the decisions split
([DOC-INDEX] unit 1.0; design docs/design/doc_index_format.md §2.2, §5.2;
appendix B).

Reads the OLD decisions file, the committed owner table
(docs/dev/doc_index/decisions_owners.tsv) and a CONVERTED pair (index +
details), and fails on each wrong-split class. It derives what each piece
must hold from the table and the old file only, never from the converter's
output (§5.1 question 2).

Clauses (each failure line names its clause):
  (i)    the distinct id set is equal: old entries, index lines, details
  (ii)   BIJECTION: per owner, the `### Dn.aN` headings == the table's new_ids;
         the `####` note headings == the note rows; no foreign heading
  (iii)  EXTENTS, byte-exact with blank lines: each row's extent (minus its
         marker line if heading-form) == the text under its new heading
         (minus heading and `(was:)`); each entry's body (its old region
         minus every extent in it, minus its heading) == the text between its
         `## ` heading and its first `### Dn.a` heading. Pieces trim only
         leading/trailing blank lines; the body's runs between removed
         extents join with one blank line
  (iv)   HEADINGS: `## ` text after the slug == the old heading text (D98's
         wrap joined, D98 only); `###` == the table's date/who/title; `####`
         == the note's old_label; `(was:)` == old_label
  (v)    FORMS: exactly one `(was:)` per heading-form (or second-of-two)
         row, right under its heading, none elsewhere; 0 `rulings:` blocks
  (vi)   per-owner multiset of non-blank lines (the coarser check)
  (pre)  every non-blank line of the old preamble survives in the index or
         details preamble
  (hash) each row's extent_hash still describes the old file (a stale
         table is refused before any comparison is trusted)

Usage:
  doc_control.py --old OLD --index IDX --details DET [--table T] [--witnesses]
  doc_control.py --witnesses-table [--table T]   (the named witnesses, table side)
  doc_control.py --selftest                      (appendix B's plants P1-P21)
Every run ends with one `doc_control: DONE rc=N` line. stdlib only; run -I.
"""
import argparse
import collections
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEF_TABLE = 'docs/dev/doc_index/decisions_owners.tsv'
COLUMNS = ['census_rev', 'old_line', 'old_end', 'extent_hash', 'old_label',
           'class', 'owner', 'owner_src', 'old_number', 'new_id', 'date',
           'who', 'title', 'cites', 'note']
JOINED = {98}           # the declared heading-wrap join (appendix A): D98 only
HEADING_FORM = ('h2', 'h3', 'h4', 'note')
ENTRY_OLD = re.compile(r'^## D([0-9]+)\b')
ADD_LABEL = re.compile(r'^## D[0-9]+ (?:[A-Z]+ )?(?:addendum|ADDENDUM|Addendum)\b')
ENTRY_NEW = re.compile(r'^## (D[0-9]+) (\S+) — (.*)$')
ADD_HEAD = re.compile(r'^### (D[0-9]+)\.a([0-9]+(?:\.[0-9]+)?[a-z]?) — (.*)$')
ANY_ADD_HEAD = re.compile(r'^### D[0-9]+\.a')
INDEX_LINE = re.compile(r'^- (D[0-9]+) ')


def read_table(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        head = None
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#'):
                continue
            p = ln.split('\t')
            if head is None:
                head = p
                if head != COLUMNS:
                    raise SystemExit('doc_control: table header %r' % head)
                continue
            rows.append(dict(zip(COLUMNS, p)))
    return rows


def trim(ls):
    a, b = 0, len(ls)
    while a < b and not ls[a].strip():
        a += 1
    while b > a and not ls[b - 1].strip():
        b -= 1
    return ls[a:b]


def hash_of(ls):
    return hashlib.sha256(''.join(l + '\n' for l in ls).encode('utf-8')).hexdigest()[:12]


def num_key(n):
    m = re.match(r'^([0-9]+)(?:\.([0-9]+))?([a-z]?)$', n)
    return (int(m.group(1)), int(m.group(2) or 0), m.group(3))


# --- the old side -----------------------------------------------------------

def parse_old(lines):
    """entries: id -> dict(head=[line idx..], text=heading text, region=(a,b));
    preamble: lines before the first entry heading."""
    heads = []
    for i, l in enumerate(lines):
        m = ENTRY_OLD.match(l)
        if m and not ADD_LABEL.match(l):
            heads.append((i, int(m.group(1))))
    entries = collections.OrderedDict()
    for k, (i, n) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        hl = [i]
        if n in JOINED:
            j = i + 1
            while j < end and lines[j].strip():
                hl.append(j)
                j += 1
        text = ' '.join(lines[j].strip() if j != i else lines[j] for j in hl)
        m = re.match(r'^## D[0-9]+(?: — | -- |: )?(.*)$', text)
        did = 'D%d' % n
        if did in entries:
            raise SystemExit('doc_control: old file has two entry headings for %s' % did)
        entries[did] = dict(head=hl, text=m.group(1).strip(), region=(i, end))
    pre = lines[:heads[0][0]] if heads else lines
    return entries, pre


def expected(lines, table):
    """What the converted pair must hold, from the old file + the table."""
    entries, pre = parse_old(lines)
    problems = []
    rows = [r for r in table]
    in_extent = [None] * len(lines)
    for r in rows:
        a, b = int(r['old_line']) - 1, int(r['old_end'])
        ext = lines[a:b]
        if hash_of(ext) != r['extent_hash']:
            problems.append('(hash) row %s (%s): extent_hash %s != old file %s'
                            % (r['new_id'], r['old_label'][:40], r['extent_hash'], hash_of(ext)))
        for k in range(a, b):
            if in_extent[k] is not None:
                problems.append('(hash) rows %s and %s overlap at old line %d'
                                % (in_extent[k]['new_id'], r['new_id'], k + 1))
            in_extent[k] = r
        piece = ext[1:] if r['class'] in HEADING_FORM else ext
        r['_piece'] = trim(piece)
        r['_marker'] = ext[0]
    bodies = {}
    for did, e in entries.items():
        a, b = e['region']
        runs, cur = [], []
        for k in range(a, b):
            if k in e['head']:
                continue
            if in_extent[k] is not None:
                if cur:
                    runs.append(cur)
                cur = []
                continue
            cur.append(lines[k])
        if cur:
            runs.append(cur)
        body = []
        for run in (trim(x) for x in runs):
            if not run:
                continue
            if body:
                body.append('')
            body.extend(run)
        bodies[did] = body
    return entries, pre, bodies, rows, problems


# --- the converted side -----------------------------------------------------

def parse_details(dl):
    """entries: id -> dict(slug, text, body=[...], adds={num: dict}), order."""
    out = collections.OrderedDict()
    pre = []
    cur = None
    add = None
    note = None
    stray = []
    for i, l in enumerate(dl):
        m = ENTRY_NEW.match(l)
        if l.startswith('## '):
            if not m:
                stray.append('(i) details line %d: a `## ` heading off the grammar: %r' % (i + 1, l[:70]))
                cur = None
                add = None
                note = None
                continue
            did = m.group(1)
            if did in out:
                stray.append('(i) details: two `## %s` headings' % did)
            cur = dict(slug=m.group(2), text=m.group(3), body=[], adds=collections.OrderedDict(),
                       foreign=[], line=i + 1)
            out[did] = cur
            add = None
            note = None
            continue
        if cur is None:
            pre.append(l)
            continue
        ma = ADD_HEAD.match(l)
        if ma:
            num = ma.group(2)
            if ma.group(1) != did_of(cur, out):
                cur['foreign'].append('%s.a%s' % (ma.group(1), num))
            key = '%s.a%s' % (ma.group(1), num)
            if key in cur['adds']:
                key = key + '#dup%d' % i
            add = dict(id=key, head=ma.group(3), lines=[], notes=collections.OrderedDict(), line=i + 1)
            cur['adds'][key] = add
            note = None
            continue
        if ANY_ADD_HEAD.match(l):
            stray.append('(ii) details line %d: an addendum heading off the grammar: %r' % (i + 1, l[:70]))
        if add is not None and l.startswith('#### '):
            note = dict(head=l[5:], lines=[])
            add['notes'].setdefault(l[5:], []).append(note)
            continue
        if note is not None:
            note['lines'].append(l)
        elif add is not None:
            add['lines'].append(l)
        else:
            cur['body'].append(l)
    return out, pre, stray


def did_of(cur, out):
    for k, v in out.items():
        if v is cur:
            return k
    return None


def heading_for(r):
    d = r['date'][len('inherit:'):] if r['date'].startswith('inherit:') else r['date']
    who = '' if r['who'] == '-' else ', ' + r['who']
    return '%s%s: %s' % (d, who, r['title'])


def was_for(r):
    if 'second of two' in r['note']:
        return '(was: "%s", second of two)' % r['old_label']
    if r['class'] in ('h2', 'h3', 'h4'):
        return '(was: "%s")' % r['old_label']
    return None


def control(old_lines, idx_lines, det_lines, table):
    """Returns a list of failure lines, each led by its clause."""
    entries, pre, bodies, rows, problems = expected(old_lines, table)
    det, dpre, stray = parse_details(det_lines)
    problems += stray
    # (i) ids
    old_ids = set(entries)
    idx_ids = set()
    for l in idx_lines:
        m = INDEX_LINE.match(l)
        if m:
            idx_ids.add(m.group(1))
    det_ids = set(det)
    for name, got in (('index', idx_ids), ('details', det_ids)):
        for x in sorted(old_ids - got, key=lambda s: int(s[1:])):
            problems.append('(i) %s lacks %s' % (name, x))
        for x in sorted(got - old_ids, key=lambda s: int(s[1:])):
            problems.append('(i) %s has %s, not an old entry' % (name, x))
    # (pre) the old preamble survives
    have = collections.Counter(l for l in dpre + [l for l in idx_lines if not INDEX_LINE.match(l)] if l.strip())
    for l in pre:
        if l.strip():
            if have[l] <= 0:
                problems.append('(pre) old preamble line lost: %r' % l[:70])
            have[l] -= 1
    by_owner = collections.defaultdict(list)
    for r in rows:
        by_owner[r['owner']].append(r)
    # (ii) bijection, (iii) extents, (iv) headings, (v) forms
    was_lines = 0
    rulings_blocks = 0
    for did, e in det.items():
        for l in e['body']:
            if l.startswith('(was: '):
                was_lines += 1
                problems.append('(v) %s body carries a (was:) line: %r' % (did, l[:60]))
            if l.strip() == 'rulings:' or l.startswith('rulings:'):
                rulings_blocks += 1
        if did in entries:
            if e['text'] != entries[did]['text']:
                problems.append('(iv) %s heading text %r != old %r' % (did, e['text'][:60], entries[did]['text'][:60]))
            if not re.match(r'^(-|[a-z0-9]+(-[a-z0-9]+){1,3})$', e['slug']):
                problems.append('(iv) %s slug %r off the grammar' % (did, e['slug']))
            got = trim(e['body'])
            if got != bodies[did]:
                problems.append('(iii) %s body differs from its old region minus extents%s'
                                % (did, first_diff(bodies[did], got)))
        for f in e['foreign']:
            problems.append('(ii) %s holds a foreign addendum heading %s' % (did, f))
        want = {r['new_id']: r for r in by_owner.get(did, []) if r['class'] != 'note'}
        got_ids = [k for k in e['adds'] if k.startswith(did + '.a') and '#dup' not in k]
        for k in e['adds']:
            if '#dup' in k:
                problems.append('(ii) %s: duplicate heading %s' % (did, k.split('#')[0]))
        for k in sorted(set(want) - set(got_ids)):
            problems.append('(ii) %s lacks addendum heading %s' % (did, k))
        for k in sorted(set(got_ids) - set(want)):
            problems.append('(ii) %s has addendum heading %s with no table row' % (did, k))
        for k in got_ids:
            if k not in want:
                continue
            r = want[k]
            a = e['adds'][k]
            if a['head'] != heading_for(r):
                problems.append('(iv) %s heading %r != table %r' % (k, a['head'][:70], heading_for(r)[:70]))
            ls = list(a['lines'])
            w = was_for(r)
            lead = [x for x in ls if x.strip()][:1]
            if w is not None:
                if not lead or not lead[0].startswith('(was: '):
                    problems.append('(v) %s lacks its (was:) line' % k)
                else:
                    if lead[0] != w:
                        problems.append('(iv) %s (was:) %r != old_label' % (k, lead[0][:70]))
                    ls = ls[ls.index(lead[0]) + 1:]
                    was_lines += 1
            for x in ls:
                if x.startswith('(was: '):
                    problems.append('(v) %s carries a (was:) line it should not: %r' % (k, x[:60]))
                    was_lines += 1
                if x.startswith('rulings:'):
                    rulings_blocks += 1
            got = trim(ls)
            if got != r['_piece']:
                problems.append('(iii) %s text differs from its extent (old %s-%s)%s'
                                % (k, r['old_line'], r['old_end'], first_diff(r['_piece'], got)))
            # notes inside this addendum
            nwant = [n for n in by_owner.get(did, []) if n['class'] == 'note'
                     and n['new_id'].split('#')[0] == k]
            nlabels = collections.Counter(n['old_label'] for n in nwant)
            nghost = collections.Counter({h: len(v) for h, v in a['notes'].items()})
            if nlabels != nghost:
                problems.append('(ii) %s note headings %s != table %s'
                                % (k, sorted(nghost.elements()), sorted(nlabels.elements())))
            for n in nwant:
                lst = a['notes'].get(n['old_label'], [])
                kk = sum(1 for m in nwant[:nwant.index(n)] if m['old_label'] == n['old_label'])
                if kk < len(lst) and trim(lst[kk]['lines']) != n['_piece']:
                    problems.append('(iii) %s text differs from its extent%s'
                                    % (n['new_id'], first_diff(n['_piece'], trim(lst[kk]['lines']))))
        for k, a in e['adds'].items():
            if a['notes'] and not any(n['class'] == 'note' and n['new_id'].split('#')[0] == k
                                      for n in by_owner.get(did, [])):
                problems.append('(ii) %s has `####` headings with no note row' % k)
    for did in by_owner:
        if did not in det:
            problems.append('(ii) table owner %s has no details entry' % did)
    want_was = sum(1 for r in rows if was_for(r) is not None)
    if was_lines != want_was:
        problems.append('(v) %d (was:) lines, the table makes %d' % (was_lines, want_was))
    if rulings_blocks:
        problems.append('(v) %d rulings: block(s) in unit 1 (0 allowed)' % rulings_blocks)
    # (vi) per-owner multiset of non-blank lines
    for did in entries:
        old = collections.Counter(l for l in bodies[did] if l.strip())
        for r in by_owner.get(did, []):
            old.update(l for l in r['_piece'] if l.strip())
        new = collections.Counter()
        e = det.get(did)
        if e:
            new.update(l for l in e['body'] if l.strip())
            for a in e['adds'].values():
                new.update(l for l in a['lines'] if l.strip() and not l.startswith('(was: '))
                for lst in a['notes'].values():
                    for n in lst:
                        new.update(l for l in n['lines'] if l.strip())
        if old != new:
            miss = list((old - new).elements())[:1]
            extra = list((new - old).elements())[:1]
            problems.append('(vi) %s non-blank line multiset differs (lost %r, gained %r)'
                            % (did, miss[0][:50] if miss else None, extra[0][:50] if extra else None))
    return problems


def first_diff(a, b):
    for k in range(max(len(a), len(b))):
        x = a[k] if k < len(a) else '<end>'
        y = b[k] if k < len(b) else '<end>'
        if x != y:
            return ': piece line %d want %r got %r' % (k + 1, x[:50], y[:50])
    return ''


# --- named witnesses (appendix B, unit 1 acceptance) -----------------------

def rng(owner, a, b, extra=()):
    return ['%s.a%d' % (owner, k) for k in range(a, b + 1)] + ['%s.a%s' % (owner, x) for x in extra]


# (witness, owner, exact non-note new_ids, entries that must hold none of them,
#  extra predicate name)
WITNESSES = [
    ('D47', 'D47', rng('D47', 1, 4), ['D48'], 'd47'),
    ('D89 in D94', 'D89', rng('D89', 1, 4), ['D94'], 'd89'),
    ('D122', 'D122', rng('D122', 1, 4), ['D123'], 'plainlabel'),
    ('D123', 'D123', rng('D123', 1, 8, ['3a']), ['D124'], 'plainlabel'),
    ('D162 a4', 'D162', rng('D162', 1, 5), ['D167'], 'dup4'),
    ('D155 a4.1', 'D155', rng('D155', 1, 5, ['4.1']), [], 'order'),
    ('D166 a1.1', 'D166', rng('D166', 1, 3, ['1.1']), ['D167'], 'order'),
    ('D58', 'D58', rng('D58', 1, 2), ['D96', 'D154'], 'h2was'),
    ('D84', 'D84', rng('D84', 1, 3), [], 'd84'),
    ('D147', 'D147', rng('D147', 1, 16), ['D149', 'D155', 'D159'], 'order'),
    ('D45', 'D45', rng('D45', 1, 4), [], 'd45'),
    ('D168', 'D168', rng('D168', 1, 3), [], 'd168'),
    ('D163', 'D163', rng('D163', 1, 12), ['D167'], 'order'),
    ('D26', 'D26', rng('D26', 1, 3), [], 'd26'),
]


def witnesses_table(table):
    """The named witnesses, asserted on the owner table (census side)."""
    bad = []
    by = collections.defaultdict(list)
    for r in table:
        by[r['owner']].append(r)
    for name, owner, ids, _, extra in WITNESSES:
        rs = [r for r in by[owner] if r['class'] != 'note']
        got = sorted((r['new_id'] for r in rs), key=lambda s: num_key(s.split('.a')[1]))
        if sorted(ids, key=lambda s: num_key(s.split('.a')[1])) != got:
            bad.append('%s: new_ids %s != %s' % (name, got, ids))
            continue
        get = {r['new_id']: r for r in rs}
        if extra == 'd47':
            ok = ([get['D47.a%d' % k]['class'] for k in (1, 2, 3, 4)] == ['h2', 'h2', 'bold', 'bold']
                  and 'LANDED NOTE' in get['D47.a4']['old_label']
                  and get['D47.a3']['old_label'].startswith('RULING-5 ADDENDUM'))
        elif extra == 'd89':
            ok = (all(get['D89.a%d' % k]['owner_src'] == 'ruled' for k in (2, 3, 4))
                  and get['D89.a1']['owner_src'] == 'label')
        elif extra == 'plainlabel':
            ok = all(r['class'] == 'plain' for r in rs)
        elif extra == 'dup4':
            ok = (get['D162.a4']['old_number'] == '4' and get['D162.a5']['old_number'] == '4'
                  and 'second of two' in get['D162.a5']['note']
                  and int(get['D162.a4']['old_line']) < int(get['D162.a5']['old_line']))
        elif extra == 'h2was':
            ok = all(r['class'] == 'h2' for r in rs)
        elif extra == 'd84':
            ok = [get['D84.a%d' % k]['old_number'] for k in (1, 2, 3)] == ['-', '2', '3']
        elif extra == 'd45':
            ok = [get['D45.a%d' % k]['old_number'] for k in (2, 3, 4)] == ['second', 'third', 'fourth']
        elif extra == 'd168':
            notes = [r for r in by[owner] if r['class'] == 'note']
            ok = sorted(r['new_id'] for r in notes) == ['D168.a3#1', 'D168.a3#2']
        elif extra == 'd26':
            ok = (all(get['D26.a%d' % k]['old_number'] == '-' for k in (1, 2, 3))
                  and get['D26.a1']['date'] < get['D26.a2']['date'] < get['D26.a3']['date']
                  and get['D26.a3']['class'] == 'h3')
        else:
            ok = True
        if not ok:
            bad.append('%s: its %s property fails' % (name, extra))
    if not any(r['owner'] == 'D147' and r['new_id'] == 'D147.a1' and r['old_number'] == '-' for r in table):
        bad.append('D147: a1 is not the unnumbered marker')
    return bad


def witnesses_converted(det_lines, table, old_lines):
    """The named witnesses on a converted details file."""
    det, _, _ = parse_details(det_lines)
    by = {r['new_id']: r for r in table}
    bad = []
    for name, owner, ids, none_in, extra in WITNESSES:
        e = det.get(owner)
        if not e:
            bad.append('%s: no details entry %s' % (name, owner))
            continue
        got = [k for k in e['adds'] if '#' not in k]
        if sorted(got) != sorted(ids):
            bad.append('%s: %s holds %s, want %s' % (name, owner, got, ids))
        keys = [num_key(k.split('.a')[1]) for k in got]
        if keys != sorted(keys):
            bad.append('%s: addenda out of C6 order %s' % (name, got))
        for h in none_in:
            he = det.get(h)
            if not he:
                continue
            text = set(l for l in he['body'] if l.strip())
            for a in he['adds'].values():
                text.update(l for l in a['lines'] if l.strip())
            for k in ids:
                r = by.get(k)
                if r and r.get('_piece') is None:
                    a, b = int(r['old_line']) - 1, int(r['old_end'])
                    r['_piece'] = trim(old_lines[a:b][1:] if r['class'] in HEADING_FORM else old_lines[a:b])
                if r and any(l in text for l in r['_piece'] if l.strip() and len(l) > 20):
                    bad.append('%s: %s holds text of %s' % (name, h, k))
                    break
        if extra == 'd47':
            d48 = det.get('D48')
            if d48:
                d48text = set(l for l in d48['body'] if l.strip() and len(l) > 20)
                if any(l in d48text for a in e['adds'].values() for l in a['lines']) or \
                        any(l in d48text for l in e['body']):
                    bad.append('D47: D47 prints D48 text')
        if extra == 'plainlabel':
            for k in ids:
                a = e['adds'].get(k)
                r = by.get(k)
                if a and r:
                    first = [l for l in a['lines'] if l.strip()][:1]
                    if not first or not first[0].startswith(r['old_label'].split(' (')[0]):
                        bad.append('%s: %s does not keep its plain label as its first body line' % (name, k))
        if extra == 'd168':
            a = e['adds'].get('D168.a3')
            if not a or sum(len(v) for v in a['notes'].values()) != 2:
                bad.append('D168: D168.a3 lacks its two `####` notes')
        if extra == 'd26':
            a = e['adds'].get('D26.a3')
            if not a or not any(l.startswith('(was: ') for l in a['lines']):
                bad.append('D26: a3 lacks its (was:) line')
        if extra == 'dup4':
            a = e['adds'].get('D162.a5')
            if not a or not any(l.startswith('(was: ') and l.endswith(', second of two)') for l in a['lines']):
                bad.append('D162 a4: the second a4 lacks `(was: "...", second of two)`')
    return bad


# --- selftest: appendix B's plants over a toy original ----------------------

def fixture_dir():
    return os.path.join(ROOT, 'tests', 'doc_lint', 'fixtures', 'doc_control')


def load_fixture(name):
    with open(os.path.join(fixture_dir(), name), encoding='utf-8') as f:
        t = f.read()
    return t.split('\n')[:-1] if t.endswith('\n') else t.split('\n')


def plant(lines, fn):
    out = fn(list(lines))
    assert out != lines, 'plant changed nothing'
    return out


def idx_of(ls, start):
    for i, l in enumerate(ls):
        if l.startswith(start):
            return i
    raise AssertionError('fixture line %r not found' % start)


def move(ls, src_prefix, dst_prefix, after=True):
    i = idx_of(ls, src_prefix)
    x = ls.pop(i)
    j = idx_of(ls, dst_prefix)
    ls.insert(j + 1 if after else j, x)
    return ls


def sub(ls, prefix, new):
    i = idx_of(ls, prefix)
    ls[i] = new(ls[i]) if callable(new) else new
    return ls


# (id, what, mutation over the CORRECT details, clauses that must fire,
#  target: 'details' | 'table')
PLANTS = [
    ('P1', 'an addendum under the wrong owner (table right)',
     lambda d: move_block(d, '### D2.a3 ', '## D3 ', into_end=True), {'ii'}),
    ('P2', 'a body line moved to another entry',
     lambda d: move(d, 'D2 body para.', 'D3 body.'), {'iii'}),
    ('P3', 'the first line of an addendum moved to the next',
     lambda d: move(d, '**D3 addendum 2 (2026-01-08):** two-liner first.', '**D3 addendum 3 (2026-01-09):**', after=True),
     {'iii'}),
    ('P3b', 'NON-first lines moved between two addenda of one owner',
     lambda d: move(d, 'two-liner second.', 'line two of a3'), {'iii'}),
    ('P4', 'an addendum line moved into its owner body',
     lambda d: move(d, 'Addendum two body line 2.', 'D2 body para.'), {'iii'}),
    ('P5', 'a line dropped', lambda d: [l for l in d if l != 'Body one line B.'], {'iii'}),
    ('P6', 'a line duplicated',
     lambda d: dup(d, 'Under the body heading.'), {'iii'}),
    ('P7', 'a fence dropped plus a fence duplicated in one owner',
     lambda d: fence_swap(d), {'iii'}),
    ('P8', 'a body heading dropped', lambda d: [l for l in d if l != '### 1. A body heading'], {'iii'}),
    ('P9', 'a body heading moved to another entry',
     lambda d: move(d, '### 1. A body heading', 'D3 body.'), {'iii'}),
    ('P10', 'an entry title rewritten',
     lambda d: sub(d, '## D1 ', lambda l: l.replace('first entry', 'first entry, retitled')), {'iv'}),
    ('P11', "D98's join applied to another heading",
     lambda d: join_d4(d), {'iii', 'iv'}),
    ('P12', 'a body line rewritten into (was:) form',
     lambda d: sub(d, 'Body one line A.', '(was: "Body one line A.")'), {'iii', 'v'}),
    ('P13', 'a body line rewritten into rulings: form',
     lambda d: sub(d, 'Body one line A.', 'rulings: Body one line A.'), {'iii', 'v'}),
    ('P14', 'a blank line dropped (two paragraphs merge)',
     lambda d: drop_blank_after(d, 'Body one line A.'), {'iii'}),
    ('P15', 'two lines reordered inside an entry',
     lambda d: swap_next(d, 'line two of a3'), {'iii'}),
    ('P16', "an addendum heading's date or title differs from the table",
     lambda d: sub(d, '### D2.a2 ', lambda l: l.replace('2026-01-04', '2026-01-05')), {'iv'}),
    ('P17', 'an invented ### D2.a1 heading inside a body',
     lambda d: insert_after(d, 'Body one line B.', ['', '### D2.a1 — 2026-01-03, Frank: inline one']), {'ii'}),
    ('P17b', 'a real addendum split by an invented ### D3.a4',
     lambda d: insert_after(d, 'line two of a3', ['### D3.a4 — 2026-01-09: invented']), {'ii', 'iii'}),
    ('P18', 'an extra (was:) line with a false label',
     lambda d: insert_after(d, '### D3.a1 ', ['(was: "D3 addendum one")']), {'v'}),
    ('P19', 'a rulings: block written in unit 1',
     lambda d: insert_after(d, '## D3 ', ['rulings:', 'r1* the toy rule']), {'v'}),
    ('P21', 'a one-line addendum (followed directly by the next marker) moved',
     lambda d: move(d, '**D3 addendum 1 (2026-01-07):** one-liner.', '**D3 addendum 2 (2026-01-08):** two-liner first.'),
     {'iii'}),
]


def move_block(d, head_prefix, dst_prefix, into_end=False):
    i = idx_of(d, head_prefix)
    j = i + 1
    while j < len(d) and not d[j].startswith(('## ', '### D')):
        j += 1
    blk = d[i:j]
    del d[i:j]
    k = idx_of(d, dst_prefix) + 1
    while into_end and k < len(d) and not d[k].startswith('## '):
        k += 1
    d[k:k] = blk
    return d


def dup(d, prefix):
    i = idx_of(d, prefix)
    d.insert(i + 1, d[i])
    return d


def fence_swap(d):
    # the opening fence dropped, the closing one duplicated: same multiset
    i = idx_of(d, '```')
    del d[i]
    j = idx_of(d, '```')
    d.insert(j, '```')
    return d


def join_d4(d):
    # the D98 rule (heading + its following non-blank lines) run on D4,
    # whose body starts right under its old heading
    i = idx_of(d, '## D4 ')
    j = i + 1
    while not d[j].strip():
        j += 1
    d[i] = d[i] + ' ' + d[j].strip()
    del d[j]
    return d


def drop_blank_after(d, prefix):
    i = idx_of(d, prefix)
    assert not d[i + 1].strip()
    del d[i + 1]
    return d


def swap_next(d, prefix):
    i = idx_of(d, prefix)
    d[i], d[i + 1] = d[i + 1], d[i]
    return d


def insert_after(d, prefix, new):
    i = idx_of(d, prefix)
    d[i + 1:i + 1] = new
    return d


def clauses(problems):
    out = set()
    for p in problems:
        m = re.match(r'^\(([a-z]+)\)', p)
        if m:
            out.add(m.group(1))
    return out


def selftest():
    sys.path.insert(0, HERE)
    import doc_census as dc
    old = load_fixture('toy_old.md')
    idx = load_fixture('toy_index.md')
    det = load_fixture('toy_details.md')
    rul = []
    head = None
    for ln in load_fixture('toy_rulings.tsv'):
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('\t')
        if head is None:
            head = p
        else:
            rul.append(dict(zip(head, p)))
    _, rows, prob = dc.derive(old, rul, 'toy')
    fails = []

    def expect(ok, what):
        print('selftest: %s %s' % ('ok  ' if ok else 'MISS', what))
        if not ok:
            fails.append(what)
    expect(not prob, 'toy table derives clean (%s)' % prob)
    table = [{c: r[c] for c in COLUMNS} for r in rows]
    base = control(old, idx, det, [dict(r) for r in table])
    expect(not base, 'GREEN: the correct toy conversion passes every clause%s'
           % ('' if not base else ' -- ' + '; '.join(base[:4])))
    for pid, what, fn, want in PLANTS:
        got = clauses(control(old, idx, plant(det, fn), [dict(r) for r in table]))
        ok = want <= got
        expect(ok, '%-4s RED by (%s)%s: %s' % (pid, ','.join(sorted(want)),
                                               '' if ok else ' -- fired only %s' % sorted(got), what))
    # (hash): a table row whose extent no longer matches the old file
    stale = [dict(r) for r in table]
    stale[0]['extent_hash'] = '000000000000'
    expect('hash' in clauses(control(old, idx, det, stale)), 'P3h  RED by (hash): a stale extent_hash in the table')
    # (i): an entry missing from the index
    got = clauses(control(old, [l for l in idx if not l.startswith('- D3 ')], det, [dict(r) for r in table]))
    expect('i' in got, 'Pi   RED by (i): an id missing from the index')
    # (pre): the old preamble dropped
    got = clauses(control(old, [l for l in idx if 'Preamble line' not in l],
                          [l for l in det if 'Preamble line' not in l], [dict(r) for r in table]))
    expect('pre' in got, 'Ppre RED by (pre): an old preamble line dropped')
    # P20 is the census's (doc_census.py --selftest)
    print('doc_control: selftest %d plant(s) + 3 extra, %d miss(es)' % (len(PLANTS), len(fails)))
    rc = 1 if fails else 0
    print('doc_control: DONE rc=%d' % rc)
    return rc


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        t = f.read()
    return t.split('\n')[:-1] if t.endswith('\n') else t.split('\n')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--old')
    ap.add_argument('--index')
    ap.add_argument('--details')
    ap.add_argument('--table', default=os.path.join(ROOT, DEF_TABLE))
    ap.add_argument('--witnesses', action='store_true')
    ap.add_argument('--witnesses-table', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--max', type=int, default=40)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    table = read_table(a.table)
    if a.witnesses_table:
        bad = witnesses_table(table)
        for b in bad:
            print('doc_control: WITNESS FAIL ' + b)
        print('doc_control: %d witness(es) on the table, %d failing' % (len(WITNESSES), len(bad)))
        print('doc_control: DONE rc=%d' % (1 if bad else 0))
        return 1 if bad else 0
    if not (a.old and a.index and a.details):
        ap.error('--old, --index and --details are required')
    old = read_lines(a.old)
    problems = control(old, read_lines(a.index), read_lines(a.details), table)
    if a.witnesses:
        problems += ['(witness) ' + b for b in witnesses_converted(read_lines(a.details), table, old)]
    for p in problems[:a.max]:
        print('doc_control: FAIL ' + p)
    if len(problems) > a.max:
        print('doc_control: ... %d more' % (len(problems) - a.max))
    by = collections.Counter(re.match(r'^\(([a-z]+)\)', p).group(1) for p in problems)
    print('doc_control: %d rows, %d failure(s) by clause: %s'
          % (len(table), len(problems), ', '.join('(%s) %d' % kv for kv in sorted(by.items())) or 'none'))
    rc = 1 if problems else 0
    print('doc_control: DONE rc=%d' % rc)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
