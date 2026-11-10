#!/usr/bin/env python3
"""doc_cites.py -- the cite resolver for the decisions split ([DOC-INDEX]
unit 1.0; design docs/design/doc_index_format.md §5.2 "Cite resolver", G4,
§2.4 C13; appendix C).

Finds every decisions cite in the tree (outside the exemption set) and
resolves it through the OWNER TABLE (docs/dev/doc_index/decisions_owners.tsv,
scripts/doc_census.py) to a set of table rows (their `new_id`s) or to an
entry `Dn`.  A cite that resolves to nothing is DANGLING.

Cite forms (appendix C; `form` column):
  addendum  `Dn addendum|add.|ADDENDUM [ordinal] [k|k.m|3a|YYYY-MM-DD]`
            (unnumbered = every row of Dn with old_number `-`)
  of        `addendum k of Dn`
  newid     `Dn.ak[.m][#c]` (the post-conversion grammar), resolved by new_id
  dotted    `Dn.k` -- a ruling number in the body; needs Dn to exist
  bare      `Dn` -- needs Dn to exist
Out of scope until units 2/3: Kn, Un, [TAG]; `decisions.md:N` line cites
(appendix E rewrites or exempts them).

  doc_cites.py [--root R] [--table T] MODE
  MODES
    --summary          counts by form, dangling by form, the 10 commonest dangling
    --inbound ID       every cite resolving to ID (an owner-table `new_id` or `Dn`),
                       with the citing line's host entry when it is in decisions.md
    --emit-baseline    write dangling_before.tsv and resolution_before.tsv
    --check            fail on a NEW dangling cite, a baseline row that now
                       resolves or is gone (the baseline only shrinks), or a
                       cite key whose resolution differs from resolution_before.tsv
    --selftest         plants: renumbered addendum, new dangling cite, moved owner,
                       shrunken baseline; each must be caught
Every run ends with one `doc_cites: DONE rc=N` line.  Run with `python3 -I`.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doc_census as dc  # noqa: E402  (parsing, table columns and ordinals are the census's)

ROOT = dc.ROOT
INDEX_DIR = 'docs/dev/doc_index'
DEF_DANGLING = INDEX_DIR + '/dangling_before.tsv'
DEF_RESOLVED = INDEX_DIR + '/resolution_before.tsv'

# appendix E's declared exemption set (C8/C13 share it)
EXEMPT = ('docs/dev/dev_journal.md', 'docs/dev/plan_completed.md', 'docs/dev/reviews/',
          'docs/dev/lanes/', 'docs/dev/history/', 'studies/', 'memfn/', 'docs/dev/doc_index/',
          'pcrec-bench/')
EXEMPT_KEEP = ('memfn/docs/requests.md',)
# the committed baselines and the fixture trees carry cites by design
SKIP_PARTS = ('/fixtures/',)

NUM = r'[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]+(?:\.[0-9]+)?[a-z]?'
RE_ADD = re.compile(r'\bD([0-9]+) (?:(' + dc.ORDINAL + r') )?(?:add\.|addendum|ADDENDUM|Addendum)'
                    r'(?: (' + NUM + r')\b)?')
RE_OF = re.compile(r'\baddendum (' + NUM + r') of D([0-9]+)\b')
RE_NEWID = re.compile(r'\bD([0-9]+)\.a([0-9]+(?:\.[0-9]+|[a-z])?)(#[0-9]+)?(?![0-9A-Za-z])')
RE_DOT = re.compile(r'\bD([0-9]+)\.([0-9]+(?:\.[0-9]+)?)\b')
RE_BARE = re.compile(r'\bD([1-4][0-9]{2}|[1-9][0-9]?)\b')  # not D0 / D04 / D800 (hex, registers)
FORMS = ('addendum', 'of', 'newid', 'dotted', 'bare')


def exempt(path):
    if path in EXEMPT_KEEP:
        return False
    return path.startswith(EXEMPT) or any(p in '/' + path for p in SKIP_PARTS)


def tree_files(root):
    if os.path.isdir(os.path.join(root, '.git')) or os.path.isfile(os.path.join(root, '.git')):
        out = subprocess.run(['git', '-C', root, 'ls-files', '-z'], capture_output=True,
                             timeout=60).stdout.decode('utf-8', 'replace')
        files = [f for f in out.split('\0') if f]
    else:
        files = []
        for d, _, fs in os.walk(root):
            for f in fs:
                files.append(os.path.relpath(os.path.join(d, f), root))
    return sorted(f for f in files if not exempt(f))


class Index:
    """The owner table plus the entry set, for resolving."""

    def __init__(self, rows, entries):
        self.rows = rows
        self.entries = entries
        self.by_owner = {}
        self.by_id = {}
        for r in rows:
            self.by_owner.setdefault(r['owner'], []).append(r)
            self.by_id.setdefault(r['new_id'], []).append(r)

    def resolve_add(self, dn, ordw, num):
        """(rowset, key) for an addendum-form cite; rowset is a sorted tuple of new_ids."""
        rows = self.by_owner.get('D' + dn, [])
        if ordw:
            w = ordw.lower()
            hit = [r for r in rows if r['old_number'].lower() == w]
            if not hit and w in dc.ORD_WORDS:
                k = dc.ORD_WORDS.index(w) + 1
                hit = [r for r in rows if r['new_id'] == 'D%s.a%d' % (dn, k)]
            key = 'D%s a:%s' % (dn, w)
        elif num:
            if dc.DATE.fullmatch(num):
                hit = [r for r in rows if r['date'] == num or r['old_number'] == num]
            else:
                hit = [r for r in rows if r['old_number'] == num]
                if not hit:
                    hit = [r for r in rows if r['new_id'] == 'D%s.a%s' % (dn, num)]
            key = 'D%s a:%s' % (dn, num)
        else:
            hit = [r for r in rows if r['old_number'] == '-']
            key = 'D%s a:-' % dn
        return tuple(sorted(r['new_id'] for r in hit)), key

    def resolve_newid(self, dn, tail, note):
        nid = 'D%s.a%s%s' % (dn, tail, note or '')
        if nid in self.by_id:
            return (nid,), nid
        if not note:  # D168.a3 names the family D168.a3#1, #2 too
            fam = tuple(sorted(i for i in self.by_id if i.startswith(nid + '#')))
            if fam:
                return fam, nid
        return (), nid

    def entry_set(self, dn):
        return ('D' + dn,) if ('D' + dn) in self.entries else ()


def cites_of_line(line, ix):
    """[(form, text, key, rowset)] for one line; spans never double count."""
    out = []
    taken = []

    def free(m):
        return not any(m.start() < e and s < m.end() for s, e in taken)

    def add(m, form, text, key, rs):
        taken.append((m.start(), m.end()))
        out.append((form, text, key, rs))
    for m in RE_OF.finditer(line):
        rs, _ = ix.resolve_add(m.group(2), None, m.group(1))
        add(m, 'of', m.group(0), 'D%s a:%s' % (m.group(2), m.group(1)), rs)
    for m in RE_ADD.finditer(line):
        if free(m):
            rs, key = ix.resolve_add(m.group(1), m.group(2), (m.group(3) or '').rstrip('.') or None)
            add(m, 'addendum', m.group(0), key, rs)
    for m in RE_NEWID.finditer(line):
        if free(m):
            rs, key = ix.resolve_newid(m.group(1), m.group(2), m.group(3))
            add(m, 'newid', m.group(0), key, rs)
    for m in RE_DOT.finditer(line):
        if free(m):
            add(m, 'dotted', m.group(0), 'D' + m.group(1), ix.entry_set(m.group(1)))
    for m in RE_BARE.finditer(line):
        if free(m):
            add(m, 'bare', m.group(0), 'D' + m.group(1), ix.entry_set(m.group(1)))
    return out


def load_index(root, table):
    rows = dc.read_tsv(table, dc.COLUMNS)
    entries = set('D' + r['owner'][1:] for r in rows)
    fn = os.path.join(root, dc.DEF_FILE)
    host = {}  # line -> entry for decisions.md hosting
    if os.path.isfile(fn):
        h = None
        with open(fn, encoding='utf-8') as f:
            for i, ln in enumerate(f, 1):
                m = dc.ENTRY_HEAD.match(ln)
                if m:
                    h = 'D' + m.group(1)
                    entries.add(h)
                host[i] = h
    return Index(rows, entries), host


def collect(root, table):
    """All cites: list of dicts file, line, form, text, key, rows."""
    ix, host = load_index(root, table)
    markers = {int(r['old_line']) for r in ix.rows}
    out = []
    for path in tree_files(root):
        try:
            with open(os.path.join(root, path), 'rb') as f:
                data = f.read()
        except OSError:
            continue
        if b'\0' in data:
            continue
        for n, line in enumerate(data.decode('utf-8', 'replace').split('\n'), 1):
            if path == dc.DEF_FILE and n in markers:
                continue  # a marker line is a heading, not a cite
            for form, text, key, rs in cites_of_line(line, ix):
                out.append({'file': path, 'line': n, 'form': form, 'text': text, 'key': key,
                            'rows': rs, 'host': host.get(n) if path == dc.DEF_FILE else None})
    return out, ix


def reason(c):
    if c['form'] in ('addendum', 'of', 'newid'):
        return 'no owner-table row for ' + c['key']
    return 'no entry ' + c['key']


def dangling(cites):
    return [c for c in cites if not c['rows']]


# --- baselines --------------------------------------------------------------

DCOLS = ['file', 'line', 'form', 'cite', 'reason']
RCOLS = ['key', 'rows']


def write_dangling(path, cites):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(DCOLS) + '\n')
        for c in sorted(dangling(cites), key=lambda c: (c['file'], c['line'], c['text'])):
            f.write('\t'.join([c['file'], str(c['line']), c['form'], c['text'], reason(c)]) + '\n')


def resolution_map(cites):
    """key -> rowset for cites that resolve, addendum-shaped forms only (the table's job)."""
    m = {}
    for c in cites:
        if c['rows'] and c['form'] in ('addendum', 'of', 'newid'):
            m[c['key']] = c['rows']
    return m


def write_resolved(path, cites):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(RCOLS) + '\n')
        for k, rs in sorted(resolution_map(cites).items()):
            f.write('%s\t%s\n' % (k, ','.join(rs)))


def read_rows(path, cols):
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    return [dict(zip(cols, ln.split('\t'))) for ln in lines[1:] if ln]


def check(cites, dpath, rpath):
    """Problems vs the committed baselines."""
    problems = []
    base = {}
    for r in read_rows(dpath, DCOLS):
        base[(r['file'], r['form'], r['cite'])] = base.get((r['file'], r['form'], r['cite']), 0) + 1
    now = {}
    first = {}
    for c in dangling(cites):
        k = (c['file'], c['form'], c['text'])
        now[k] = now.get(k, 0) + 1
        first.setdefault(k, c['line'])
    for k, n in now.items():
        if n > base.get(k, 0):
            problems.append('NEW dangling cite %r (%s) in %s:%d x%d: %s'
                            % (k[2], k[1], k[0], first[k], n - base.get(k, 0),
                               'no row/entry resolves it; add its row or name it id-less'))
    for k, n in base.items():
        if now.get(k, 0) < n:
            problems.append('baseline row %r (%s) in %s now resolves or is gone x%d: delete it from %s'
                            % (k[2], k[1], k[0], n - now.get(k, 0), os.path.basename(dpath)))
    want = {r['key']: r['rows'] for r in read_rows(rpath, RCOLS)}
    have = {k: ','.join(rs) for k, rs in resolution_map(cites).items()}
    for k, rs in want.items():
        if k not in have:
            if not any(c['key'] == k for c in cites):
                continue  # the last cite of this key left the tree: nothing changed
            problems.append('resolution changed: %s was %s, now unresolved' % (k, rs))
        elif have[k] != rs:
            problems.append('resolution changed: %s was %s, now %s' % (k, rs, have[k]))
    return problems


# --- modes ------------------------------------------------------------------

def summary(cites):
    by = {}
    dg = {}
    for c in cites:
        by[c['form']] = by.get(c['form'], 0) + 1
        if not c['rows']:
            dg[c['form']] = dg.get(c['form'], 0) + 1
    print('cites %d in %d files' % (len(cites), len({c['file'] for c in cites})))
    for f in FORMS:
        print('  %-9s %6d  dangling %5d' % (f, by.get(f, 0), dg.get(f, 0)))
    print('dangling total %d' % sum(dg.values()))
    cnt = {}
    for c in dangling(cites):
        cnt[(c['form'], c['text'])] = cnt.get((c['form'], c['text']), 0) + 1
    for (form, text), n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
        print('  commonest dangling: %5d  %-9s %s' % (n, form, text))


def inbound(cites, ident, ix):
    n = 0
    for c in cites:
        if ident in c['rows'] or (ident == c['key'] and c['form'] in ('bare', 'dotted')):
            n += 1
            print('%s:%d\t%s\t%s\t%s' % (c['file'], c['line'], c['form'], c['text'],
                                         ('in ' + c['host']) if c['host'] else ''))
    print('doc_cites: %d cite(s) of %s' % (n, ident))
    return 0


# --- selftest ---------------------------------------------------------------

TOY_ROWS = [
    ('D5', '1', 'D5.a1', '2026-01-01'), ('D5', '2', 'D5.a2', '2026-01-02'),
    ('D5', '-', 'D5.a3', '2026-01-03'), ('D6', '1', 'D6.a1', '2026-02-01'),
]


def toy_table(rows):
    cols = dc.COLUMNS
    out = ['\t'.join(cols)]
    for n, (owner, num, nid, date) in enumerate(rows):
        r = dict.fromkeys(cols, '-')
        r.update(census_rev='toy', old_line=str(1000 + n), old_end=str(1000 + n), extent_hash='h%d' % n,
                 old_label='%s addendum %s' % (owner, num), **{'class': 'bold'}, owner=owner,
                 owner_src='label', old_number=num, new_id=nid, date=date, cites='0')
        out.append('\t'.join(r[c] for c in cols))
    return '\n'.join(out) + '\n'


def selftest():
    import tempfile
    base = os.environ.get('PCREC_TMPDIR') or os.path.join('/var/tmp', 'pcrec-' + (os.environ.get('USER') or 'u'))
    os.makedirs(base, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='doc_cites.', dir=base)
    fails = []

    def expect(cond, what):
        print('selftest: %s %s' % ('ok  ' if cond else 'MISS', what))
        if not cond:
            fails.append(what)
    # built from pieces so this file's own text holds no live cite
    A = ' addendum '
    root = os.path.join(tmp, 'tree')
    os.makedirs(os.path.join(root, 'docs/dev'))
    os.makedirs(os.path.join(root, 'docs/dev/lanes'))

    def put(name, text):
        p = os.path.join(root, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
    put('docs/dev/decisions.md', '## D5 the five\nbody\n## D6 the six\nbody\n')
    put('docs/a.md', 'see D5' + A + '2 and D5' + A + '\nalso D6 add. 1, D5.3, D6.a1 and' + A + '1 of D5\n')
    put('docs/dev/lanes/x.md', 'D77' + A + '9 exempt (lanes)\n')
    tbl = os.path.join(tmp, 'owners.tsv')
    dbl = os.path.join(tmp, 'dangling.tsv')
    rsv = os.path.join(tmp, 'resolved.tsv')

    def run(rows=TOY_ROWS):
        with open(tbl, 'w', encoding='utf-8') as f:
            f.write(toy_table(rows))
        return collect(root, tbl)[0]
    cites = run()
    by = {(c['form'], c['text']): c for c in cites}
    expect(all(c['rows'] for c in cites if c['file'] == 'docs/a.md'), 'clean toy tree: every cite resolves')
    expect(not any(c['file'].startswith('docs/dev/lanes/') for c in cites), 'lanes/ is exempt')
    expect(by[('addendum', 'D5' + A.rstrip() )]['rows'] == ('D5.a3',),
           'unnumbered alias -> the old_number "-" row only')
    expect(by[('dotted', 'D5.3')]['rows'] == ('D5',), 'dotted Dn.k resolves to the entry')
    expect(by[('of', 'addendum 1 of D5')]['rows'] == ('D5.a1',), '"addendum k of Dn" resolves like Dn addendum k')
    write_dangling(dbl, cites)
    write_resolved(rsv, cites)
    expect(not check(cites, dbl, rsv), 'check is green against its own baselines')
    # plant 1: a renumbered addendum (same marker, new id)
    ren = [(o, n, 'D5.a9' if i == 'D5.a2' else i, d) for o, n, i, d in TOY_ROWS]
    pr = check(run(ren), dbl, rsv)
    expect(any('resolution changed' in p and 'D5 a:2' in p for p in pr), 'plant: renumbered addendum is caught')
    # plant 2: a new dangling cite
    put('docs/b.md', 'new D5' + A + '9 here\n')
    pr = check(run(), dbl, rsv)
    expect(any(p.startswith('NEW dangling') and 'D5' + A.rstrip() + ' 9' in p for p in pr), 'plant: a new dangling cite is caught')
    os.remove(os.path.join(root, 'docs/b.md'))
    # plant 3: a moved owner (the D6 addendum row now owned by D5)
    mv = [('D5' if (o, n) == ('D6', '1') else o, n, i, d) for o, n, i, d in TOY_ROWS]
    pr = check(run(mv), dbl, rsv)
    expect(any('resolution changed' in p for p in pr), 'plant: a moved owner is caught')
    # plant 4: the baseline only shrinks
    put('docs/c.md', 'fix D5' + A + '9 pending\n')
    cites = run()
    write_dangling(dbl, cites)
    write_resolved(rsv, cites)
    expect(not check(cites, dbl, rsv), 'baseline with a dangling cite is green')
    os.remove(os.path.join(root, 'docs/c.md'))
    pr = check(run(), dbl, rsv)
    expect(any('now resolves or is gone' in p for p in pr), 'plant: a baseline row whose cite is gone fails (shrinks only)')
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print('doc_cites: selftest %d miss(es)' % len(fails))
    rc = 1 if fails else 0
    print('doc_cites: DONE rc=%d' % rc)
    return rc


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--table', default=None)
    ap.add_argument('--dangling', default=None)
    ap.add_argument('--resolved', default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ('summary', 'emit-baseline', 'check', 'selftest'):
        g.add_argument('--' + m, action='store_true')
    g.add_argument('--inbound', dest='inbound_id', metavar='ID')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    table = args.table or os.path.join(args.root, dc.DEF_TABLE)
    dpath = args.dangling or os.path.join(args.root, DEF_DANGLING)
    rpath = args.resolved or os.path.join(args.root, DEF_RESOLVED)
    cites, ix = collect(args.root, table)
    rc = 0
    if args.summary:
        summary(cites)
    elif args.inbound_id:
        inbound(cites, args.inbound_id, ix)
    elif args.emit_baseline:
        write_dangling(dpath, cites)
        write_resolved(rpath, cites)
        print('doc_cites: wrote %d dangling rows, %d resolution keys'
              % (len(dangling(cites)), len(resolution_map(cites))))
    elif args.check:
        problems = check(cites, dpath, rpath)
        for p in problems:
            print('doc_cites: FAIL ' + p)
        print('doc_cites: check %d cites, %d dangling, %d problems'
              % (len(cites), len(dangling(cites)), len(problems)))
        rc = 1 if problems else 0
    print('doc_cites: DONE rc=%d' % rc)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
