#!/usr/bin/env python3
"""b3cost (lane b3cost, 2026-10-12): the rev-end reverse machine at the TAGGED
size (D164 add. 3's owed measurement).  COUNTS ONLY: no subject is matched, no
clock is read.

Population: the rev-end artifacts with a path-final non-multiline `$`/`\\Z`
(census.py's `revend_eol`: tail_probe neol > 0 and RX_DFA_SCAN == rev-end),
bench (pcrec-bench, read-only) and corpus separately.
Per artifact, four reverse machines (b3cost_probe.c, real pcrec pipeline):
  today     X$           pcrec's reverse DFA; CONTROL against the emitted C
  untagged  X\\n?\\z      the mark's reverse walk without tags (the proxy,
                         also compiled by the CLI: emitted states/bytes)
  tagged    X\\z x X\\n\\z  the product of the two tag machines, Moore-minimized
                         with output (acc0, acc1); CONTROL: the same product
                         with output acc0|acc1 must equal `untagged`.

    PCREC=build/pcrec PROBE=build/scratch/tail_probe B3PROBE=build/scratch/b3cost_probe \\
    BENCH=/home/pcrec/projects/pcrec-bench CORPUS=. OUT=build/scratch/b3 \\
    python3 -I docs/design/endmark/census/b3cost.py > docs/design/endmark/results/b3cost.txt
"""
import collections, concurrent.futures as cf, importlib.util, os, re, statistics, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
spec = importlib.util.spec_from_file_location('cost', os.path.join(HERE, 'cost.py'))
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)
rv = cost.rv
import census as ec                      # docs/design/endmark/census.py
B3PROBE = E['B3PROBE']
JOBS = int(E.get('JOBS', '6'))
MARK = b'()(?:\\n)?\\z'


def variants(pat):
    new, cnt = cost.rewrite(pat)
    if not cnt or new is None or new.count(MARK) != cnt:
        return None
    return dict(untagged=new.replace(MARK, b'(?:\\n)?\\z'),
                t0=new.replace(MARK, b'\\z'), t1=new.replace(MARK, b'\\n\\z'), nrep=cnt)


def emit(pat, r, tag):
    d = cost.compile_(pat, r['enc'], r['icase'], False, os.path.join(rv.OUT, 'cc'), tag)
    if d is None:
        return None
    m = d['m'].get('reverse')
    if m is None:
        return dict(scan=d['DFA_SCAN'], states=None)
    return dict(scan=d['DFA_SCAN'], states=m['states'], ncls=m['ncls'], bytes=m['bytes'],
                arrays=m['arrays'], tie=d['revend_tie'], engine=d['ENGINE'])


def reverse_arrays(pat, r, tag):
    """per-array (name, count, elemsize) of the emitted reverse role"""
    path = os.path.join(rv.OUT, 'cc', tag + '.c')
    cmd = rv.NICE + [rv.PCREC, '--features', 'all', '-o', path]
    if r['icase']: cmd.append('-i')
    if r['enc'] == 'utf8': cmd += ['-e', 'utf8']
    cmd += ['--pattern', pat]
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    if p.returncode: return None
    txt = open(path, 'rb').read()
    for ext in ('.c', '.h'):
        try: os.unlink(path[:-2] + ext)
        except OSError: pass
    out = []
    for m in cost.ARR.finditer(txt):
        if m.group(2) == b'reverse':
            out.append((m.group(3).decode(), int(m.group(4)), cost.SIZE.get(m.group(1), 4)))
    return out


def tagged_bytes(arrs_u, S_u, C_u, S_t, C_t):
    """emitted untagged-proxy reverse bytes rescaled to (S_t, C_t): next_state
    scales with S*C, per-state tables (is_accepting, *_view) with S, the rest
    (byte_class[256], scan tables) stay."""
    tot = 0
    for name, cnt, sz in arrs_u:
        if name == 'next_state':
            tot += S_t * C_t * sz
        elif name == 'is_accepting' or name.endswith('_view'):
            tot += S_t * sz
        else:
            tot += cnt * sz
    return tot


def work(job):
    i, r = job
    out = dict(i=i)
    v = variants(r['pat'])
    if v is None:
        out['skip'] = 'unrewritable'
        return out
    out['v'] = v
    out['today_e'] = emit(r['pat'], r, 'o%d' % i)
    out['untag_e'] = emit(v['untagged'], r, 'u%d' % i)
    out['untag_arrs'] = reverse_arrays(v['untagged'], r, 'ua%d' % i)
    return out


def probe_rows(rows, items):
    inp = ''
    for it in items:
        v, r = it['v'], rows[it['i']]
        pre = b'(?i)' if r['icase'] else b''
        inp += '\t'.join([str(it['i']), r['enc'], (pre + r['pat']).hex(), (pre + v['untagged']).hex(),
                          (pre + v['t0']).hex(), (pre + v['t1']).hex()]) + '\n'
    res = subprocess.run(rv.NICE + [B3PROBE], input=inp.encode(), capture_output=True, timeout=7200)
    lines = res.stdout.decode().split('\n')
    hdr = lines[0].split('\t')
    out = {}
    for ln in lines[1:]:
        f = ln.split('\t')
        if len(f) < 2: continue
        out[int(f[0])] = dict(zip(hdr, f))
    return out


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * q))]


def main():
    os.makedirs(os.path.join(rv.OUT, 'cc'), exist_ok=True)
    rows = rv.bench_pop() + rv.corpus_pop()
    pr = ec.probe(rows)
    num = ec.num
    cand = [i for i in range(len(rows)) if pr.get(i, {}).get('status') == 'ok' and num(pr[i], 'neol') > 0]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        fx = dict(zip(cand, ex.map(lambda i: ec.facts(rows[i]), cand)))
    revend = [i for i in cand if fx[i].get('DFA_SCAN') == 'rev-end']
    print('# b3cost at %s' % subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'],
          capture_output=True, text=True).stdout.strip())
    print('== population: rows (byte+utf8), parsed, neol>0 (path-final $/\\Z), rev-end among those')
    for pop in ('bench', 'corpus'):
        print('  %-6s rows %5d parsed %5d neol>0 %4d rev-end %4d  (end_pin: %s)' % (
            pop, sum(rows[i]['pop'] == pop for i in range(len(rows))),
            sum(rows[i]['pop'] == pop for i in pr if pr[i].get('status') == 'ok'),
            sum(rows[i]['pop'] == pop for i in cand), sum(rows[i]['pop'] == pop for i in revend),
            dict(collections.Counter(fx[i].get('end_pin') for i in revend if rows[i]['pop'] == pop))))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(work, [(i, rows[i]) for i in revend]))
    skipped = [r for r in res if 'skip' in r]
    ok = [r for r in res if 'skip' not in r]
    print('  text scanner could not rewrite: %d (%s)' % (len(skipped), ', '.join(rows[r['i']]['id'] for r in skipped)))
    pres = probe_rows(rows, ok)
    recs = []
    reasons = collections.Counter()
    for r in ok:
        i = r['i']; p = pres.get(i)
        row = rows[i]
        if p is None or p.get('status') != 'ok':
            reasons[(row['pop'], 'probe:' + (p.get('status') if p else 'missing'))] += 1
            continue
        te, ue = r['today_e'], r['untag_e']
        rec = dict(id=row['id'], pop=row['pop'], pat=row['pat'].decode('latin-1')[:70], enc=row['enc'],
                   tie=bool(te and te.get('tie')), today_raw=int(p['today']), untag_raw=int(p['untagged']),
                   today_m=int(p['today_post']), untag_m=int(p['untag_post']),
                   or_min=int(p['or_min']), tag=int(p['tag_min']), tag_trim=int(p['tag_trim']),
                   ncls_tag=int(p['ncls_tag']), cls_untag=int(p['cls_untag']),
                   today_e=te['states'] if te else None, untag_e=ue['states'] if ue else None,
                   today_b=te.get('bytes') if te else None, untag_b=ue.get('bytes') if ue else None,
                   untag_scan=ue['scan'] if ue else None, nrep=r['v']['nrep'])
        if rec['tag'] < 0:
            reasons[(row['pop'], 'tagged product overflow')] += 1
            continue
        if rec['today_e'] is None or rec['untag_e'] is None:
            reasons[(row['pop'], 'no emitted reverse tables (today=%s untag=%s)' % (
                rec['today_e'], rec['untag_e']))] += 1
        if rec['untag_e'] and r['untag_arrs']:
            rec['tag_b'] = tagged_bytes(r['untag_arrs'], rec['untag_e'], rec['cls_untag'],
                                        rec['tag'], rec['ncls_tag'])
        recs.append(rec)
    print('\n== excluded from the measured set (reason, count):')
    for k, n in sorted(reasons.items()):
        print('   %-7s %-50s %d' % (k[0], k[1], n))
    for pop in ('bench', 'corpus'):
        rs = [x for x in recs if x['pop'] == pop]
        st = [x for x in ok if rows[x['i']]['pop'] == pop and pres.get(x['i'], {}).get('status') != 'ok']
        print('   %-7s probe status not ok: %s' % (pop, dict(collections.Counter(
            pres.get(x['i'], {}).get('status', 'missing') for x in st))))
    # controls
    print('\n== CONTROL 1: model today (probe d->n) vs emitted reverse states')
    for pop in ('bench', 'corpus', 'all'):
        rs = [x for x in recs if (pop == 'all' or x['pop'] == pop) and x['today_e'] is not None]
        mism = [x for x in rs if x['today_m'] != x['today_e']]
        print('   %-7s compared %4d  equal %4d  MISMATCH %d' % (pop, len(rs), len(rs) - len(mism), len(mism)))
    for x in [x for x in recs if x['today_e'] is not None and x['today_m'] != x['today_e']][:30]:
        print('      MISMATCH %s  %s  model %d emitted %d' % (x['id'], x['pat'], x['today_m'], x['today_e']))
    print('== CONTROL 2: model untagged vs emitted proxy reverse states')
    rs = [x for x in recs if x['untag_e'] is not None]
    mism = [x for x in rs if x['untag_m'] != x['untag_e']]
    print('   compared %d equal %d MISMATCH %d' % (len(rs), len(rs) - len(mism), len(mism)))
    for x in mism[:30]:
        print('      MISMATCH %s  %s  model %d emitted %d' % (x['id'], x['pat'], x['untag_m'], x['untag_e']))
    print('== CONTROL 3: tag product with OR output vs untagged machine')
    mism = [x for x in recs if x['or_min'] != x['untag_raw']]
    print('   compared %d equal %d MISMATCH %d' % (len(recs), len(recs) - len(mism), len(mism)))
    for x in mism[:30]:
        print('      MISMATCH %s  %s  or %d untagged(raw) %d' % (x['id'], x['pat'], x['or_min'], x['untag_raw']))
    print('== scan-edge (post-pass) vs raw: today %d artifacts shrink (the emitted count is post), untagged proxy %d' % (
        sum(x['today_m'] != x['today_raw'] for x in recs), sum(x['untag_m'] != x['untag_raw'] for x in recs)))
    print('== (tagged trimmed of dead-language states differs from untrimmed on %d)' %
          sum(x['tag'] != x['tag_trim'] for x in recs))

    def table(label, rs):
        if not rs:
            return
        t, u, g = sum(x['today_m'] for x in rs), sum(x['untag_m'] for x in rs), sum(x['tag'] for x in rs)
        rt = [x['tag'] / x['today_m'] for x in rs]
        ru = [x['untag_m'] / x['today_m'] for x in rs]
        print('   %-14s n=%4d  states today %5d  untagged %5d (%.2fx)  tagged %5d (%.2fx)  '
              'ratio tagged/today median %.2f p90 %.2f max %.2f | untagged/today median %.2f p90 %.2f max %.2f  '
              '>2x: %d (tagged) %d (untagged)' % (
                  label, len(rs), t, u, u / t, g, g / t, statistics.median(rt), pct(rt, .9), max(rt),
                  statistics.median(ru), pct(ru, .9), max(ru),
                  sum(1 for q in rt if q > 2.0), sum(1 for q in ru if q > 2.0)))
    print('\n== STATES (minimized reachable; model today == emitted by control 1)')
    for pop in ('bench', 'corpus'):
        table(pop, [x for x in recs if x['pop'] == pop])
    table('all', recs)
    for x in recs: x['ver'] = x['or_min'] == x['untag_raw']
    table('verified (ctl3)', [x for x in recs if x['ver']])
    table('ctx-unverified', [x for x in recs if not x['ver']])
    table('scan-edge today', [x for x in recs if x['today_m'] != x['today_raw']])
    table('no scan-edge', [x for x in recs if x['today_m'] == x['today_raw']])
    table('with tie code', [x for x in recs if x['tie']])
    table('no tie code', [x for x in recs if not x['tie']])
    table('utf8', [x for x in recs if x['enc'] == 'utf8'])
    rr = [x['tag'] / x['today_raw'] for x in recs]
    print('   (sensitivity, tagged / today BEFORE the scan-edge pass: median %.2f p90 %.2f max %.2f)' % (
        statistics.median(rr), pct(rr, .9), max(rr)))
    sh = [x for x in recs if x['today_m'] != x['today_raw']]
    print('   scan-edge artifacts (today shrinks after the pass; the lowered forms do not): n=%d  today %d  tagged %d (%.2fx)' % (
        len(sh), sum(x['today_m'] for x in sh), sum(x['tag'] for x in sh), sum(x['tag'] for x in sh) / max(1, sum(x['today_m'] for x in sh))))
    print('\n== TABLE BYTES (emitted reverse-role static arrays; tagged = untagged proxy rescaled, see report)')
    for pop in ('bench', 'corpus', 'all'):
        rs = [x for x in recs if (pop == 'all' or x['pop'] == pop) and x.get('tag_b') and x['today_b'] and x['untag_b']]
        if rs:
            t, u, g = sum(x['today_b'] for x in rs), sum(x['untag_b'] for x in rs), sum(x['tag_b'] for x in rs)
            print('   %-7s n=%4d  today %8d B  untagged %8d B (%+.1f%%)  tagged %8d B (%+.1f%%)' % (
                pop, len(rs), t, u, 100.0 * (u / t - 1), g, 100.0 * (g / t - 1)))
    # distribution of tagged/today
    dist = collections.Counter()
    for x in recs:
        q = x['tag'] / x['today_m']
        dist['<1.0' if q < 1 else '1.0-1.25' if q <= 1.25 else '1.25-1.5' if q <= 1.5 else
             '1.5-2.0' if q <= 2.0 else '2.0-2.5' if q <= 2.5 else '>2.5'] += 1
    print('\n== tagged/today ratio histogram: ' + ', '.join('%s:%d' % kv for kv in sorted(dist.items())))
    print('\n== tagged/untagged ratio (the price of the tags alone): median %.2f p90 %.2f max %.2f' % (
        statistics.median(x['tag'] / x['untag_m'] for x in recs), pct([x['tag'] / x['untag_m'] for x in recs], .9),
        max(x['tag'] / x['untag_m'] for x in recs)))
    print('\n== TOP 10 GROWERS BY tagged/today ratio (id, pattern, today, untagged, tagged)')
    for x in sorted(recs, key=lambda x: (-x['tag'] / x['today_m'], -x['tag']))[:10]:
        print('   %-7s %-34s %-42s %4d %4d %4d  %.2fx' % (x['pop'], x['id'], x['pat'][:42], x['today_m'],
              x['untag_m'], x['tag'], x['tag'] / x['today_m']))
    print('\n== TOP 10 BY ABSOLUTE tagged growth')
    for x in sorted(recs, key=lambda x: -(x['tag'] - x['today_m']))[:10]:
        print('   %-7s %-34s %-42s %4d %4d %4d  %+d' % (x['pop'], x['id'], x['pat'][:42], x['today_m'],
              x['untag_m'], x['tag'], x['tag'] - x['today_m']))
    over = sorted([x for x in recs if x['tag'] / x['today_m'] > 2.0], key=lambda x: -x['tag'] / x['today_m'])
    print('\n== EVERY artifact over 2x today (tagged), n=%d' % len(over))
    for x in over:
        print('   %-7s %-34s %-50s %4d %4d %4d  %.2fx  (today before scan-edge %d; tagged/untagged %.2f)%s' % (
              x['pop'], x['id'], x['pat'][:50], x['today_m'], x['untag_m'], x['tag'], x['tag'] / x['today_m'],
              x['today_raw'], x['tag'] / x['untag_m'], '' if x['ver'] else '  [ctl3 unverified]'))
    print('   over 2x counting today BEFORE the scan-edge pass: %d;  tagged/untagged > 2x: %d' % (
        sum(1 for x in recs if x['tag'] > 2 * x['today_raw']), sum(1 for x in recs if x['tag'] > 2 * x['untag_m'])))
    print('\n== shrinkers / equal (tagged <= today): %d' % sum(1 for x in recs if x['tag'] <= x['today_m']))
    print('\n== PER-ARTIFACT TSV: pop id today untagged tagged today_b untag_b tag_b tie pattern')
    for x in recs:
        print('T\t%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%d\t%s' % (x['pop'], x['id'], x['today_m'], x['untag_m'], x['tag'],
              x['today_b'], x['untag_b'], x.get('tag_b'), x['tie'], x['pat']))


if __name__ == '__main__':
    main()
