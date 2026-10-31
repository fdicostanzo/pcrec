"""Token census of emitted VM matcher bodies against the listing's events.

For each pattern: emit the C and the --emit-ir listing with the base
compiler, cut every matcher function body (rx_match_anchored and its
__match_notempty copy are the same text; the first is read), and count
statement tokens in the C against event rows in the listing. A token with
no event counterpart is a statement the event stream does not record.
Usage: python3 -I census.py PCREC PATTERNS.tsv OUTDIR
"""
import re, subprocess, sys, os, collections

pc, pats, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
TOK = [
    ('goto_L', r'goto rx_L\d+;'),
    ('goto_fail', r'goto rx_fail;'),
    ('SET', r'\bRX_SET\('),
    ('PUSH', r'\bRX_PUSH\('),
    ('CUT', r'\bRX_CUT\('),
    ('CALL', r'\bRX_CALL\('),
    ('CHECK', r'\bRX_TRAIL_CHECK\('),
    ('WORK', r'\bRX_CHARGE_WORK\('),
    ('slot_read', r'slot_values\['),
    ('cursor_write', r'\bscan_position\s*(=[^=]|\+=|\+\+|-=)'),
    ('local_write', r'\brx_(?:span_cursor|rv\d+_\w+|revdet_group_\w+(?:\[[^\]]*\])*)\s*(=[^=]|\+=|-=|\+\+|--)|\b(?:rx_rv\d+_\w+)\+\+'),
    ('run_write', r'\brun->(?:resume_depth|call_top|steps_left|callee_gave_up)\s*(=[^=]|\+=|-=)|--run->'),
    ('if_open', r'\bif \('),
    ('block_open', r'\{\s*$'),
    ('return', r'\breturn\b'),
    ('goto_star', r'goto \*'),
    ('switch', r'\bswitch \('),
]
EV = ['label', 'goto', 'fail', 'set', 'push', 'cut', 'call', 'return',
      'consume', 'assert', 'note', 'accept', 'island', 'callout']
rows = []
for line in open(pats):
    if not line.strip() or line.startswith('#'): continue
    name, flags, pat = line.rstrip('\n').split('\t')
    c = os.path.join(out, name + '.c')
    fl = flags.split()
    r1 = subprocess.run([pc, '-p', 'rx', *fl, '-o', c, '--pattern', pat],
                        capture_output=True, text=True, timeout=60)
    r2 = subprocess.run([pc, '-p', 'rx', *fl, '--emit-ir', '--pattern', pat],
                        capture_output=True, text=True, timeout=60)
    if r1.returncode or r2.returncode:
        rows.append((name, 'COMPILE-FAIL', r1.stderr.strip()[:80]))
        continue
    src = open(c).read()
    m = re.search(r'_match_anchored\([^)]*\)\n\{\n(.*?)\nrx_accept:', src, re.S)
    if not m:
        rows.append((name, 'NO-BODY', ''))
        continue
    body = m.group(1)
    # the walk's part only: from the first label to the end
    body = body[body.find('goto rx_L0;'):]
    body = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
    body = re.sub(r'//[^\n]*', '', body)
    tc = collections.OrderedDict()
    for k, rx in TOK:
        tc[k] = sum(len(re.findall(rx, l)) for l in body.split('\n'))
    lst = r2.stdout
    prog = lst.split('#section program', 1)[1].split('#section', 1)[0]
    ec = collections.Counter()
    for l in prog.split('\n')[2:]:
        f = l.split('\t')
        if len(f) > 1 and f[1]: ec[f[1]] += 1
    nstmt = sum(1 for l in body.split('\n')
                if l.strip() and not re.match(r'^rx_L\d+:', l.strip()))
    rows.append((name, tc, ec, nstmt))
with open(os.path.join(out, 'census.tsv'), 'w') as o:
    hdr = ['pattern', 'body_lines'] + [k for k, _ in TOK] + ['ev_' + e for e in EV]
    o.write('\t'.join(hdr) + '\n')
    for r in rows:
        if isinstance(r[1], str):
            o.write('%s\t%s\t%s\n' % r); continue
        name, tc, ec, n = r
        o.write('\t'.join([name, str(n)] + [str(v) for v in tc.values()]
                          + [str(ec.get(e, 0)) for e in EV]) + '\n')
print(open(os.path.join(out, 'census.tsv')).read())
