#!/usr/bin/env python3
"""D164 census: path-final lookaheads / $ / \\Z / (?m)$ / \\z over the bench
and the corpus, what each such pattern gets today, and what the END_MARK
lowering would change.  COMPILE-SIDE ONLY (no subject matched, no clock read).

Populations: docs/dev/optloop/revend/census.py's builders, imported (bench
compiled as pcrec-auto does: --features all, -e utf8 on the utf8 set; corpus
blocks with their own encoding and -i).  Two instruments, cross-checked:
  PROBE  tail_probe.c: the lowering's own tail walk over the real parser's
         tree (endmark.md §1.2), plus the first VM-only node outside the
         tail lookaheads' own stamps.
  FACTS  `pcrec --emit-facts`: the shipped stamps (RX_ENGINE, _WHY,
         RX_DFA_SCAN, RX_VM_PREFILTER, end_pin) and, for rev-end artifacts
         pinned at `$`/`\\Z`, the emitted C (does it carry the tie code).
A row the probe calls "only a tail lookahead forces the VM" must read
RX_ENGINE "vm" in FACTS; the disagreements are counted.

    PCREC=build/pcrec PROBE=build/scratch/tail_probe \\
    BENCH=/home/pcrec/projects/pcrec-bench CORPUS=. OUT=build/scratch/emc \\
    python3 -I docs/design/endmark/census.py > docs/design/endmark/results/census.txt
"""
import collections, concurrent.futures as cf, importlib.util, os, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
spec = importlib.util.spec_from_file_location(
    'rv', os.path.join(REPO, 'docs', 'dev', 'optloop', 'revend', 'census.py'))
rv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rv)          # reads PCREC/PROBE/BENCH/CORPUS/OUT

PROBE = E['PROBE']
OUT = E['OUT']
JOBS = int(E.get('JOBS', '4'))


def probe(rows):
    inp = ''.join('%d\t%s\t%s\n' % (i, r['enc'],
                  (b'(?i)' + r['pat'] if r['icase'] else r['pat']).hex())
                  for i, r in enumerate(rows))
    res = subprocess.run(rv.NICE + [PROBE], input=inp.encode(), capture_output=True, timeout=3600)
    lines = res.stdout.decode().split('\n')
    hdr = lines[0].split('\t')
    out = {}
    for ln in lines[1:]:
        f = ln.split('\t')
        if len(f) < 2:
            continue
        d = dict(zip(hdr, f))
        out[int(f[0])] = d
    return out


def emitted_c(r, i):
    path = os.path.join(OUT, 'c%d.c' % i)
    cmd = rv.NICE + [rv.PCREC, '--features', 'all', '-o', path]
    if r['icase']:
        cmd.append('-i')
    if r['enc'] == 'utf8':
        cmd += ['-e', 'utf8']
    cmd += ['--pattern', r['pat']]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    if p.returncode != 0:
        return None
    try:
        txt = open(path, 'rb').read()
    finally:
        for ext in ('.c', '.h'):
            try:
                os.unlink(path[:-2] + ext)
            except OSError:
                pass
    return txt


def facts(r):
    """rv.facts' command; keeps every decision stamp and the end_pin fact."""
    cmd = rv.NICE + [rv.PCREC, '--emit-facts=' + r['enc'], '--features', 'all']
    if r['icase']:
        cmd.append('-i')
    if r['enc'] == 'utf8':
        cmd += ['-e', 'utf8']
    cmd += ['--pattern', r['pat']]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {'refused': 'timeout'}
    if p.returncode != 0:
        return {'refused': p.stderr.decode('utf8', 'replace').split('\n')[0][:120]}
    d, sect = {}, None
    for ln in p.stdout.decode('utf8', 'replace').split('\n'):
        if ln.startswith('#section'):
            sect = ln.split()[1]; continue
        if ln.startswith('#') or not ln:
            continue
        f = ln.split('\t')
        if sect == 'facts' and len(f) >= 7 and f[1] == 'end_pin':
            d['end_pin'] = f[6]
        elif sect == 'decisions' and len(f) >= 3:
            d[f[1].replace('RX_', '')] = f[2].strip('"')
    return d


def num(d, k):
    try:
        return int(d.get(k, '0'))
    except ValueError:
        return 0


def main():
    rows = rv.bench_pop() + rv.corpus_pop()
    pr = probe(rows)
    interest = [i for i, r in enumerate(rows)
                if pr.get(i, {}).get('status') == 'ok' and
                (num(pr[i], 'nlook') or num(pr[i], 'neol') or num(pr[i], 'nmeol') or
                 num(pr[i], 'nz') or num(pr[i], 'nneg') or num(pr[i], 'nctx'))]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        fx = dict(zip(interest, ex.map(lambda i: facts(rows[i]), interest)))
    revend_eol = [i for i in interest if fx[i].get('DFA_SCAN') == 'rev-end'
                  and num(pr[i], 'neol') > 0]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        ctext = dict(zip(revend_eol, ex.map(lambda i: emitted_c(rows[i], i), revend_eol)))

    print('# D164 census at %s' % subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'],
          capture_output=True, text=True).stdout.strip())
    pops = collections.Counter((r['pop'], r['enc']) for r in rows)
    ok = collections.Counter((rows[i]['pop'], rows[i]['enc']) for i in pr if pr[i].get('status') == 'ok')
    print('== populations: rows / parsed')
    for k in sorted(pops):
        print('  %-7s %-5s rows %5d parsed %5d' % (k[0], k[1], pops[k], ok[k]))

    def group(pred):
        c = collections.Counter()
        ids = collections.defaultdict(list)
        for i in interest:
            g = pred(i)
            if g:
                c[(rows[i]['pop'], g)] += 1
                ids[(rows[i]['pop'], g)].append(i)
        return c, ids

    # ---- 1. the tail kinds
    print('\n== path-final constructs (a pattern counts once per kind it carries)')
    for kind in ('nlook', 'nneg', 'neol', 'nmeol', 'nz', 'nctx'):
        c = collections.Counter(rows[i]['pop'] for i in interest if num(pr[i], kind))
        print('  %-6s bench %4d  corpus %5d' % (kind, c['bench'], c['corpus']))

    # ---- 2. tail positive lookahead: routing today and after
    def look_class(i):
        p, f = pr[i], fx[i]
        if not num(p, 'nlook'):
            return None
        if 'refused' in f:
            return 'refused-today'
        eng = f.get('ENGINE', '?')
        ov = p['other_vmonly']
        caps = num(p, 'ncap') > 0
        unb = num(p, 'nlook_unb') > 0
        call = num(p, 'ncall') > 0
        if eng == 'dfa':
            return 'dfa-today (??)'
        if call:
            return 'vm: call-bearing (decline)'
        if ov != '-':
            return 'vm: other VM-only construct (%s)' % ov
        if caps and unb:
            return 'vm: captures + unbounded Y (exact hybrid prefilter only)'
        if caps:
            return 'vm: captures (DFA under --no-captures; exact hybrid prefilter)'
        if unb:
            return 'vm: unbounded Y (exact hybrid prefilter; stays VM)'
        return 'VM -> DFA (only a bounded tail lookahead forced the VM)'
    c, ids = group(look_class)
    print('\n== patterns with a PATH-FINAL POSITIVE LOOKAHEAD (multi-character; one-character ones are A_CTX today)')
    for k in sorted(c):
        print('  %-7s %5d  %s' % (k[0], c[k], k[1]))
    for key in sorted(ids):
        if key[1].startswith('VM -> DFA'):
            ex = [rows[i]['id'] + '  ' + rows[i]['pat'].decode('latin-1')[:60] for i in ids[key][:12]]
            print('   e.g. (%s):' % key[0])
            for e in ex:
                print('      ' + e)
    shape = collections.Counter()
    for i in interest:
        if num(pr[i], 'nlook'):
            p = pr[i]
            s = ('unbounded' if num(p, 'nlook_unb') else
                 ('fixed L=%s' % p['look_cwmax'] if num(p, 'look_fixed') else
                  'bounded L<=%s' % p['look_cwmax']))
            shape[(rows[i]['pop'], s)] += 1
    print('  Y width (characters), patterns:')
    for k in sorted(shape):
        print('    %-7s %-14s %d' % (k[0], k[1], shape[k]))
    extra = collections.Counter()
    for i in interest:
        p = pr[i]
        if num(p, 'nlook'):
            for fl in ('look_cap', 'under_cap', 'under_atomic', 'look_vmonly'):
                if num(p, fl):
                    extra[(rows[i]['pop'], fl)] += 1
    print('  structure:', ', '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(extra.items())))

    # ---- 3. the probe-vs-facts cross-check
    dis = [i for i in ids.get(('bench', 'VM -> DFA (only a bounded tail lookahead forced the VM)'), []) +
           ids.get(('corpus', 'VM -> DFA (only a bounded tail lookahead forced the VM)'), [])
           if fx[i].get('ENGINE') != 'vm']
    print('  probe/facts disagreements on the VM -> DFA set: %d' % len(dis))

    # ---- 4. $ / \Z rev-end artifacts: what moves at B3
    print('\n== rev-end artifacts pinned at $ / \\Z (end_pin = eol): the B3 movers')
    cc = collections.Counter()
    tie = collections.Counter()
    for i in revend_eol:
        cc[rows[i]['pop']] += 1
        t = ctext.get(i)
        if t is None:
            tie[(rows[i]['pop'], 'emit-failed')] += 1
        elif b'revend_tie' in t:
            tie[(rows[i]['pop'], 'tie code emitted (nl_last)')] += 1
        else:
            tie[(rows[i]['pop'], 'no tie code')] += 1
    for k in sorted(cc):
        print('  %-7s %d artifacts' % (k, cc[k]))
    for k in sorted(tie):
        print('    %-7s %-30s %d' % (k[0], k[1], tie[k]))
    tiers = [rows[i]['id'] + '  ' + rows[i]['pat'].decode('latin-1')[:50]
             for i in revend_eol if ctext.get(i) and b'revend_tie' in ctext[i]]
    for e in tiers[:20]:
        print('      tie: ' + e)
    endpin = collections.Counter((rows[i]['pop'], fx[i].get('end_pin', '?'), fx[i].get('DFA_SCAN', '?'))
                                 for i in interest if num(pr[i], 'neol') and 'refused' not in fx[i])
    print('  every path-final-$ pattern by (end_pin fact, RX_DFA_SCAN):')
    for k in sorted(endpin):
        print('    %-7s %-6s %-22s %d' % (k[0], k[1], k[2], endpin[k]))
    ml = collections.Counter((rows[i]['pop'], fx[i].get('ENGINE', '?')) for i in interest
                             if num(pr[i], 'nmeol') and 'refused' not in fx[i])
    print('  path-final (?m)$ patterns by engine: ' + ', '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(ml.items())))
    neg = collections.Counter((rows[i]['pop'], fx[i].get('ENGINE', '?')) for i in interest
                              if num(pr[i], 'nneg') and 'refused' not in fx[i])
    print('  path-final NEGATIVE lookahead (never lowers) by engine: ' + ', '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(neg.items())))


if __name__ == '__main__':
    main()
