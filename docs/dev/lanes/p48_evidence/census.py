#!/usr/bin/env python3
"""p48 census: every corpus pattern (+ an extra list) through the three
instrumented twins (tset = HEAD, tsingle = pre-[SCANEDGE-SET] singleton
sets, trelax = HEAD + the one-state relaxation), recording each machine's
stay skips and scan edges (P48 trace lines) and its seedhead bit.

usage: census.py TREE EXTRA_TSV OUT_TSV [JOBS]
"""
import os, subprocess, sys, tempfile, concurrent.futures as cf

S = '/var/tmp/pcrec-pcrec/scratch/p48'
TW = {'set': S + '/tset/build/pcrec', 'single': S + '/tsingle/build/pcrec',
      'relax': S + '/trelax/build/pcrec'}


def decode_escape(s):
    return s.encode('utf-8', 'surrogateescape').decode('unicode_escape').encode('latin-1').decode('utf-8', 'surrogateescape')


def corpus(tree, lister):
    pats = []
    for dp, dn, fn in os.walk(os.path.join(tree, 'tests')):
        for f in sorted(fn):
            if not f.endswith('.rxt'):
                continue
            p = os.path.join(dp, f)
            r = subprocess.run([lister, '--list-source', p], capture_output=True, timeout=60)
            if r.returncode:
                continue
            for line in r.stdout.decode('utf-8', 'surrogateescape').splitlines():
                if line.startswith('#') or not line.strip():
                    continue
                fl = line.split('\t')
                if len(fl) < 5 or fl[0] not in ('pattern', 'pattern-esc'):
                    continue
                pat = fl[4]
                if fl[0] == 'pattern-esc':
                    try:
                        pat = decode_escape(pat)
                    except Exception:
                        continue
                pats.append((os.path.relpath(p, tree), pat))
    return pats


def one(args):
    src, pat = args
    rows = []
    with tempfile.TemporaryDirectory(dir=S + '/tmp') as td:
        for arm, binp in TW.items():
            env = dict(os.environ, P48_TRACE='1')
            try:
                r = subprocess.run(['gnutimeout', '30', binp, '-p', 'rx', '--features', 'all',
                                    '-o', td + '/a.c', '--pattern', pat],
                                   capture_output=True, env=env, timeout=40)
            except subprocess.TimeoutExpired:
                rows.append((arm, 'TIMEOUT'))
                continue
            if r.returncode:
                rows.append((arm, 'FAIL'))
                continue
            eng = ''
            try:
                for l in open(td + '/a.c', errors='replace'):
                    if l.startswith('#define RX_ENGINE "'):
                        eng = l.split('"')[1]
                        break
            except OSError:
                pass
            tr = [l for l in r.stderr.decode('utf-8', 'replace').splitlines() if l.startswith('P48')]
            rows.append((arm, eng + '|' + ';'.join(x.replace('\t', ',') for x in tr)))
    return src, pat, rows


def main():
    tree, extra, out = sys.argv[1:4]
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    os.makedirs(S + '/tmp', exist_ok=True)
    pats = corpus(tree, TW['set'])
    for l in open(extra, errors='surrogateescape'):
        if l.strip():
            i, p = l.rstrip('\n').split('\t', 1)
            pats.append(('bench:' + i, p))
    seen, uniq = set(), []
    for s, p in pats:
        if p in seen:
            continue
        seen.add(p)
        uniq.append((s, p))
    print('patterns', len(pats), 'distinct', len(uniq), flush=True)
    with open(out, 'w') as fo, cf.ThreadPoolExecutor(jobs) as ex:
        for n, (src, pat, rows) in enumerate(ex.map(one, uniq)):
            for arm, v in rows:
                fo.write('%s\t%s\t%s\t%s\n' % (src, pat.encode('utf-8','surrogateescape').decode('latin-1').encode('unicode_escape').decode('ascii'), arm, v))
            if n % 500 == 0:
                print('done', n, flush=True)
    print('== p48 census COMPLETE:', len(uniq), 'patterns', flush=True)


main()
