#!/usr/bin/env python3
"""b3rev (lane b3rev, 2026-10-12): every machine a B3 artifact carries, counted
(b3rev_probe.c), on three populations.  COUNTS ONLY: no clock is read here
(timing is timing/).

  census   the 266 rev-end `$`/`\\Z` artifacts (b3cost's rule: tail_probe
           neol > 0 and RX_DFA_SCAN == rev-end; bench read-only + corpus),
           per artifact: the selection row, reverse today/untagged/tagged
           (minimized and after scan-edge, the S3-fixed pass and the shipped
           one), forward and anchored today/lowered/tagged (D164 add. 4),
           mark_prio's class and cost; CONTROLS against the CLI-emitted C.
  sweep    the C2 family `\\s{0,N}$`, `[a-z]{0,N}\\s{0,N}$` (+ two siblings)
           over N, against the 32,000 state cap and the 1e6 byte cap.
  refusal  the C3 refusal-SET compare on tests/resource's witnesses, the
           sweep family and the rev-end population, plain and the
           emit_sweep `lowsize`/`lowboth` reference builds.

    PCREC=build/pcrec PROBE=build/scratch/tail_probe B3REV=build/scratch/b3rev/b3rev_probe \\
    BENCH=/home/pcrec/projects/pcrec-bench CORPUS=. OUT=build/scratch/b3rev/run \\
    python3 -I docs/design/endmark/b3rev/b3rev.py census|sweep|refusal

The tag variants come from one rewriter (`rw`): each path-final `$`/`\\Z` is
the mark's tail, and each path-final `\\z` is an UNMARKED end (d = 0, S5):
  today X$ | untagged X(?:\\n)?\\z | t0 X\\z | t1 X\\n\\z (an unmarked `\\z`
  becomes `[^\\s\\S]`, the empty class, so its arm dies at the seed: the d = 1 machine holds marked ends
  only) | G X\\G (the probe patches `\\G` into the tail with its own accepts).
"""
import collections, concurrent.futures as cf, importlib.util, json, os, re, statistics, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
spec = importlib.util.spec_from_file_location('cost', os.path.join(HERE, '..', 'census', 'cost.py'))
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)
rv = cost.rv
B3REV = os.path.abspath(E['B3REV'])
JOBS = int(E.get('JOBS', '6'))
RES = os.path.join(HERE, 'results')
OUT = os.path.abspath(E['OUT'])
LOOK_OPEN = cost.LOOK_OPEN


def _skip_class(p, i):
    n = len(p)
    j = i + 1
    if p[j:j + 1] == b'^': j += 1
    if p[j:j + 1] == b']': j += 1
    while j < n and p[j:j + 1] != b']':
        if p[j:j + 1] == b'\\': j += 1
        elif p[j:j + 2] == b'[:':
            k = p.find(b':]', j + 2)
            if k >= 0: j = k + 1
        j += 1
    return j + 1


def rw(p, tail, ztail):
    """cost.rewrite's path-final scanner, with path-final `\\z` as a second
    kind: returns (new, n_dollar, n_z) with `$`/`\\Z` -> tail and `\\z` ->
    ztail (None leaves `\\z`); (None, 0, 0) where the scanner declines."""
    if b'\\Q' in p:
        return None, 0, 0
    n = len(p)
    i, stack, cands, mflag = 0, [], [], False
    while i < n:
        c = p[i:i + 1]
        if c == b'\\':
            nx = p[i + 1:i + 2]
            if nx == b'Z': cands.append((i, 2, 'eol', list(stack), mflag))
            if nx == b'z': cands.append((i, 2, 'z', list(stack), mflag))
            i += 2
            continue
        if c == b'[':
            i = _skip_class(p, i)
            continue
        if c == b'(':
            if p[i:i + 3] == b'(?#':
                k = p.find(b')', i); i = (k if k >= 0 else n) + 1; continue
            m = re.match(rb'\(\?([a-zA-Z^-]*)\)', p[i:])
            if m:
                on, _, off = m.group(1).partition(b'-')
                if b'm' in on: mflag = True
                if b'm' in off: mflag = False
                i += m.end(); continue
            stack.append([i, p[i:].startswith(LOOK_OPEN) or p[i:].startswith(b'(?(')])
            i += 1
            continue
        if c == b')':
            if stack: stack.pop()
            i += 1
            continue
        if c == b'$':
            cands.append((i, 1, 'dollar', list(stack), mflag))
        i += 1
    if not cands:
        return p, 0, 0
    close, st, i = {}, [], 0
    while i < n:
        c = p[i:i + 1]
        if c == b'\\': i += 2; continue
        if c == b'[': i = _skip_class(p, i); continue
        if p[i:i + 3] == b'(?#':
            k = p.find(b')', i); i = (k if k >= 0 else n) + 1; continue
        if c == b'(':
            m = re.match(rb'\(\?([a-zA-Z^-]*)\)', p[i:])
            if m: i += m.end(); continue
            st.append(i)
        elif c == b')' and st:
            close[st.pop()] = i
        i += 1

    def tail_after(pos, groups):
        q = pos
        while True:
            m = re.match(rb'\(\?[a-zA-Z^-]*\)', p[q:])
            if not m: break
            q += m.end()
        for g in reversed(groups):
            nxt = p[q:q + 1]
            if nxt == b'|': q = close.get(g[0], n)
            elif nxt not in (b')', b''): return False
            if g[1]: return False
            cl = close.get(g[0])
            if cl is None: return False
            q = cl + 1
            if p[q:q + 1] in (b'*', b'+', b'{'): return False
            if p[q:q + 1] == b'?': q += 1
        return p[q:q + 1] in (b'', b'|')

    out, last, nd, nz = [], 0, 0, 0
    for (idx, ln, kind, groups, ml) in cands:
        if not tail_after(idx + ln, groups):
            continue
        if kind == 'z':
            if ztail is None: continue
            out.append(p[last:idx]); out.append(ztail); last = idx + ln; nz += 1
            continue
        if kind == 'dollar' and ml:
            return None, 0, 0          # (?m)$ never reaches rev-end (S8)
        out.append(p[last:idx]); out.append(tail); last = idx + ln; nd += 1
    out.append(p[last:])
    return b''.join(out), nd, nz


def variants(pat):
    u, nd, nz = rw(pat, b'(?:\\n)?\\z', None)
    if u is None or not nd:
        return None
    return dict(untagged=u, t0=rw(pat, b'\\z', None)[0], t1=rw(pat, b'\\n\\z', b'[^\\s\\S]')[0],
                g=rw(pat, b'\\G', None)[0], nrep=nd, nz=rw(pat, b'$', b'[^\\s\\S]')[2])


def emitted(pat, enc, icase, tag, extra=()):
    """role -> states of the CLI-emitted artifact (and the stamps)."""
    tmpd = os.path.join(OUT, 'cc')
    path = os.path.join(tmpd, tag + '.c')
    cmd = rv.NICE + [rv.PCREC, '--features', 'all', '-o', path] + list(extra)
    if icase: cmd.append('-i')
    if enc == 'utf8': cmd += ['-e', 'utf8']
    cmd += ['--pattern', pat]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return dict(rc='timeout')
    if p.returncode != 0:
        return dict(rc=p.returncode, err=p.stderr.decode('latin-1')[-200:])
    try:
        txt = open(path, 'rb').read()
    finally:
        for ext in ('.c', '.h'):
            try: os.unlink(path[:-2] + ext)
            except OSError: pass
    d = cost.stamps(txt)
    m = cost.machines(txt)
    d['m'] = {k: dict(states=v['states'], bytes=v['bytes'], ncls=v['ncls']) for k, v in m.items()}
    d['rc'] = 0
    return d


def run_probe(items):
    """items: (key, enc, icase, pat, variants) -> key -> probe row dict"""
    inp = []
    for key, enc, icase, pat, v in items:
        pre = b'(?i)' if icase else b''
        inp.append('\t'.join([str(key), enc, (pre + pat).hex(), (pre + v['untagged']).hex(),
                              (pre + v['t0']).hex(), (pre + v['t1']).hex(), (pre + v['g']).hex()]))
    # one probe process per row (a crash costs its own row only), in parallel
    def one(ln):
        r = subprocess.run(rv.NICE + ['gnutimeout', '600', B3REV], input=(ln + '\n').encode(),
                           capture_output=True)
        if r.returncode:
            return 'id\tstatus\n%s\tprobe-rc-%d\n' % (ln.split('\t')[0], r.returncode)
        return r.stdout.decode()
    with cf.ThreadPoolExecutor(JOBS) as ex:
        outs = list(ex.map(one, inp))
    res = {}
    for o in outs:
        lines = o.split('\n')
        if not lines or not lines[0]: continue
        hdr = lines[0].split('\t')
        for ln in lines[1:]:
            f = ln.split('\t')
            if len(f) < 2: continue
            d = dict(zip(hdr, f))
            for k, x in list(d.items()):
                if k not in ('id', 'status'):
                    try: d[k] = int(x)
                    except ValueError: pass
            res[f[0]] = d
    return res


# ------------------------------------------------------------------ selection

ROWS = ('deny', 'one-seed', 'tagged', 'two-seed', 'overflow')


def select(p):
    """The proposed first-match table (endmark.md §R3.1), from probe facts.
    `deny` is a flag and never fires on the census."""
    if not p.get('nl_last'):
        return 'one-seed'
    if p.get('status') != 'ok' or p.get('r_tag', -1) < 0:
        return 'overflow'
    if p['tie_pairs'] == 0:
        return 'two-seed'
    lowered = [p.get('f_umin', -1), p.get('a_ok', 0)]
    if lowered[0] < 0:
        return 'overflow'
    return 'tagged'


MPC = {0: 'none', 1: 'const0', 2: 'const1', 3: 'state-dep'}


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * q))] if xs else 0


def census():
    import census as ec                      # docs/design/endmark/census.py
    os.makedirs(os.path.join(OUT, 'cc'), exist_ok=True)
    rows = rv.bench_pop() + rv.corpus_pop()
    pr = ec.probe(rows)
    num = ec.num
    cand = [i for i in range(len(rows)) if pr.get(i, {}).get('status') == 'ok' and num(pr[i], 'neol') > 0]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        fx = dict(zip(cand, ex.map(lambda i: ec.facts(rows[i]), cand)))
    revend = [i for i in cand if fx[i].get('DFA_SCAN') == 'rev-end']
    head = subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    print('# b3rev census at %s (gcc %s)' % (head, subprocess.run(['gcc', '-dumpfullversion'], capture_output=True, text=True).stdout.strip()))
    print('== population: rev-end with a path-final $/\\Z: bench %d, corpus %d' % (
        sum(rows[i]['pop'] == 'bench' for i in revend), sum(rows[i]['pop'] == 'corpus' for i in revend)))
    vs, skipped = {}, []
    for i in revend:
        v = variants(rows[i]['pat'])
        if v is None: skipped.append(i)
        else: vs[i] = v
    print('   rewriter declined: %d %s' % (len(skipped), [rows[i]['id'] for i in skipped]))
    print('   with an unmarked path-final \\z arm (S5): %d' % sum(1 for v in vs.values() if v['nz']))

    def emits(i):
        r = rows[i]
        return i, dict(today=emitted(r['pat'], r['enc'], r['icase'], 't%d' % i),
                       today_norev=emitted(r['pat'], r['enc'], r['icase'], 'n%d' % i, ['-fno-rev-end']),
                       low_norev=emitted(vs[i]['untagged'], r['enc'], r['icase'], 'l%d' % i, ['-fno-rev-end']))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        em = dict(ex.map(emits, list(vs)))
    pres = run_probe([(i, rows[i]['enc'], rows[i]['icase'], rows[i]['pat'], vs[i]) for i in vs])
    recs = []
    for i in vs:
        p = pres.get(str(i))
        r = rows[i]
        rec = dict(id=r['id'], pop=r['pop'], enc=r['enc'], icase=bool(r['icase']),
                   pat=r['pat'].decode('latin-1'), nz=vs[i]['nz'], probe=p, emit=em[i])
        rec['row'] = select(p) if p else 'probe-failed'
        recs.append(rec)
    json.dump(recs, open(os.path.join(RES, 'census.json'), 'w'), indent=0, default=str)
    report_census(recs)


def g(rec, k, role=None, which='today'):
    e = rec['emit'].get(which) or {}
    if role:
        return ((e.get('m') or {}).get(role) or {}).get(k)
    return e.get(k)


def report_census(recs):
    ok = [r for r in recs if r['probe'] and r['probe'].get('status') in ('ok', 'tag-overflow')]
    print('   probed %d, probe failed %d' % (len(ok), len(recs) - len(ok)))
    # --- controls
    print('\n== CONTROLS (each: compared / equal / MISMATCH)')

    def ctl(name, pairs):
        pairs = [(r, a, b) for (r, a, b) in pairs if a is not None and b is not None and a >= 0 and b >= 0]
        mm = [(r, a, b) for (r, a, b) in pairs if a != b]
        print('   %-62s %4d %4d %4d' % (name, len(pairs), len(pairs) - len(mm), len(mm)))
        for r, a, b in mm[:8]:
            print('       MISMATCH %-40s %-28s model %s emitted %s' % (r['id'][:40], r['pat'][:28], a, b))
        return mm
    ctl('C1 reverse today, probe post-scan-edge == emitted', [(r, r['probe']['r_today_post'], g(r, 'states', 'reverse')) for r in ok])
    ctl('C2 forward today, probe post == emitted (-fno-rev-end)', [(r, r['probe']['f_today_post'], g(r, 'states', 'forward', 'today_norev')) for r in ok])
    ctl('C3 anchored today, probe post == emitted (-fno-rev-end)', [(r, r['probe']['a_today_post'], g(r, 'states', 'anchored', 'today_norev')) for r in ok])
    ctl('C4 forward lowered (patched \\G NFA) post == emitted X\\n?\\z', [(r, r['probe']['f_upost'], g(r, 'states', 'forward', 'low_norev')) for r in ok])
    ctl('C5 anchored lowered post == emitted X\\n?\\z', [(r, r['probe']['a_upost'], g(r, 'states', 'anchored', 'low_norev')) for r in ok])
    ctl('C6 reverse untagged == product with OR output (minimized)', [(r, r['probe']['r_or'], r['probe']['r_untag']) for r in ok if r['probe']['status'] == 'ok'])
    ctl('C7 reverse untagged post == OR product rebuilt, shipped pass', [(r, r['probe']['r_or_post'], r['probe']['r_untag_post']) for r in ok if r['probe']['status'] == 'ok'])
    ctl('C8 forward tagged model, b ignored == pcrec minimized', [(r, r['probe']['f_model'], r['probe']['f_umin']) for r in ok if not r['probe']['f_unmod']])
    ctl('C9 anchored tagged model, b ignored == pcrec minimized', [(r, r['probe']['a_model'], r['probe']['a_umin']) for r in ok if not r['probe']['a_unmod'] and r['probe']['a_ok']])
    ctl('C10 forward: closure accept == pcrec END accept (mismatch count 0)', [(r, r['probe']['f_accmis'], 0) for r in ok if not r['probe']['f_unmod']])
    ctl('C11 anchored: closure accept == pcrec END accept', [(r, r['probe']['a_accmis'], 0) for r in ok if not r['probe']['a_unmod'] and r['probe']['a_ok']])
    ctl('C12 forward model post (b ignored, rebuilt) == pcrec post', [(r, r['probe']['f_model_post'], r['probe']['f_upost']) for r in ok if not r['probe']['f_unmod']])
    ctl('C13 today tie code (emitted revend_tie) == probe nl_last', [(r, int(bool(g(r, 'revend_tie'))), r['probe']['nl_last']) for r in ok])
    bc = [r for r in ok if r['probe']['f_bconf'] or r['probe']['a_bconf']]
    print('   b-conflicts (pre-sets into one END state disagree on b; tagged would need a split): %d %s' % (
        len(bc), [(r['id'], r['probe']['f_bconf'], r['probe']['a_bconf']) for r in bc][:6]))
    # --- the selection
    print('\n== THE SELECTION (first-match rows, §R3.1)')
    by = collections.defaultdict(list)
    for r in recs:
        by[r['row']].append(r)
    for row in ROWS + ('probe-failed',):
        xs = by.get(row, [])
        print('   %-10s %4d  (bench %d, corpus %d; utf8 %d)' % (row, len(xs), sum(x['pop'] == 'bench' for x in xs),
              sum(x['pop'] == 'corpus' for x in xs), sum(x['enc'] == 'utf8' for x in xs)))
    for row in ('tagged', 'two-seed', 'overflow'):
        print('   %s: %s' % (row, ', '.join('%s %s' % (x['pat'][:24], x['enc'] if x['enc'] != 'byte' else '') for x in by.get(row, []))))
    # tie facts
    tg = by.get('tagged', [])
    print('\n== THE TIE FACT on the tagged set (%d)' % len(tg))
    print('   class-dependent ties (S2: a tie under some context atoms only): %d' % sum(1 for r in tg if r['probe']['tie_classdep']))
    print('   ties at the absent atom (startpos/subject-start boundary): %d' % sum(1 for r in tg if r['probe']['tie_absent']))
    mpc = collections.Counter((MPC.get(r['probe']['mp_cls']) if r['probe']['mp_ok'] == 1 else
                               ('unmodelled-ctx' if r['probe']['mp_ok'] == -2 else 'overflow')) for r in tg)
    print('   mark_prio: %s' % dict(mpc))
    mpn = [r for r in tg if r['probe']['mp_ok'] == 1 and r['probe']['mp_cls'] == 0]
    print('   mark_prio none although the machine ties (should be 0): %d %s' % (len(mpn), [r['pat'] for r in mpn][:5]))
    sts = [r['probe']['mp_states'] for r in tg if r['probe']['mp_ok'] == 1]
    if sts:
        print('   mark_prio cost (unpruned anchored states): total %d, median %d, max %d (cap %d)' % (
            sum(sts), statistics.median(sts), max(sts), 32000))
    # --- sizes
    print('\n== MACHINE SIZES (states; "post" = after the scan-edge pass = emitted)')

    def line(name, xs, a, b):
        xs = [r for r in xs if r['probe'].get(a, -1) is not None and r['probe'].get(b, -1) is not None
              and r['probe'].get(a, -1) >= 0 and r['probe'].get(b, -1) >= 0]
        if not xs:
            print('   %-46s n/a' % name); return
        ta = sum(r['probe'][a] for r in xs); tb = sum(r['probe'][b] for r in xs)
        rat = [r['probe'][b] / r['probe'][a] for r in xs if r['probe'][a]]
        print('   %-46s n %3d  %6d -> %6d (%.2fx)  per-artifact med %.2f p90 %.2f max %.2f  +max %d' % (
            name, len(xs), ta, tb, tb / ta if ta else 0, statistics.median(rat), pct(rat, 0.9), max(rat),
            max(r['probe'][b] - r['probe'][a] for r in xs)))
    for setname, xs in (('ALL rev-end', [r for r in ok]), ('TAGGED set', tg)):
        print('  -- %s' % setname)
        xs = [r for r in xs if r['probe']['status'] == 'ok']
        line('reverse: today -> tagged (minimized)', xs, 'r_today', 'r_tag')
        line('reverse: today post -> tagged post (S3-fixed pass)', xs, 'r_today_post', 'r_tag_post')
        line('reverse: tagged -> tagged post (what the pass buys)', xs, 'r_tag', 'r_tag_post')
        line('reverse: untagged post -> tagged post', xs, 'r_untag_post', 'r_tag_post')
        fx = [r for r in xs if not r['probe']['f_unmod']]
        line('forward: today -> lowered untagged (min)', xs, 'f_today', 'f_umin')
        line('forward: today post -> lowered untagged post', xs, 'f_today_post', 'f_upost')
        line('forward: today post -> lowered TAGGED post', fx, 'f_today_post', 'f_tag_post')
        line('forward: lowered untagged -> tagged (min)', fx, 'f_umin', 'f_tag')
        ax = [r for r in xs if r['probe']['a_ok'] and not r['probe']['a_unmod'] and r['probe']['a_today'] >= 0]
        line('anchored: today post -> lowered TAGGED post', ax, 'a_today_post', 'a_tag_post')
        line('anchored: lowered untagged -> tagged (min)', ax, 'a_umin', 'a_tag')
    s3 = [r for r in ok if r['probe']['status'] == 'ok' and r['probe']['r_tag_post'] != r['probe']['r_tag_post_unfixed']]
    s3f = [r for r in ok if not r['probe']['f_unmod'] and r['probe']['f_tag_post'] != r['probe']['f_tag_post_unfixed']]
    print('\n== S3: artifacts where the SHIPPED pass (accept truth) merges what the fixed pass (accept value) keeps:'
          ' reverse %d %s; forward %d %s' % (len(s3), [r['pat'][:20] for r in s3][:6], len(s3f), [r['pat'][:20] for r in s3f][:6]))
    unm = [r for r in ok if r['probe']['f_unmod']]
    print('   forward/anchored tagged model unmodelled (context axis): %d' % len(unm))
    print('\n== PER-ARTIFACT TSV: row id enc pat | rev today_post untag_post tag tag_post | fwd today_post upost tag_post | anch today_post upost tag_post | mark_prio')
    for r in sorted(recs, key=lambda x: (ROWS.index(x['row']) if x['row'] in ROWS else 9, x['id'])):
        p = r['probe'] or {}
        print('\t'.join(str(x) for x in (r['row'], r['id'], r['enc'], r['pat'][:40],
              p.get('r_today_post'), p.get('r_untag_post'), p.get('r_tag'), p.get('r_tag_post'),
              p.get('f_today_post'), p.get('f_upost'), p.get('f_tag_post'),
              p.get('a_today_post'), p.get('a_upost'), p.get('a_tag_post'),
              MPC.get(p.get('mp_cls')) if p.get('mp_ok') == 1 else p.get('mp_ok'))))


# ---------------------------------------------------------------------- sweep

FAMILIES = [
    ('s0N', lambda N: b'\\s{0,%d}$' % N),
    ('az0N_s0N', lambda N: b'[a-z]{0,%d}\\s{0,%d}$' % (N, N)),
    ('w1N_s0N', lambda N: b'\\w{1,%d}\\s{0,%d}$' % (N, N)),
    ('dot0N', lambda N: b'(?s).{0,%d}$' % N),
]
NS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]


def sweep():
    os.makedirs(os.path.join(OUT, 'cc'), exist_ok=True)
    items, meta = [], {}
    for fam, mk in FAMILIES:
        for N in NS:
            pat = mk(N)
            v = variants(pat)
            key = '%s_%d' % (fam, N)
            meta[key] = (fam, N, pat)
            items.append((key, 'byte', False, pat, v))

    def emits(it):
        key, enc, icase, pat, v = it
        return key, dict(today=emitted(pat, enc, icase, 'sw' + key), low=emitted(v['untagged'], enc, icase, 'sl' + key, ['-fno-rev-end']))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        em = dict(ex.map(emits, items))
    pres = run_probe(items)
    out = []
    print('# b3rev sweep (C2): states per machine vs N; cap 32,000 states/machine, 1,000,000 emitted bytes')
    print('fam\tN\ttoday_rc\ttoday_bytes\tr_today_post\tr_tag\tr_tag_post\tr_reach\tf_today_post\tf_tag_post\t'
          'a_today_post\ta_tag_post\tmp_states\tmp_cls\tlow_bytes\tpred_tag_bytes')
    for key, (fam, N, pat) in meta.items():
        p = pres.get(key, {})
        e = em[key]
        tb = (e['today'] or {}).get('len')
        lb = (e['low'] or {}).get('len')
        # predicted tagged artifact bytes: today's text + the reverse next_state growth (2 B per cell)
        pred = None
        if tb and p.get('r_tag_post', -1) >= 0:
            rm = ((e['today'].get('m') or {}).get('reverse') or {})
            pred = tb + 6 * max(0, p['r_tag_post'] - p['r_today_post']) * max(1, rm.get('ncls', 1))
        row = [fam, N, e['today'].get('rc'), tb, p.get('r_today_post'), p.get('r_tag'), p.get('r_tag_post'), p.get('r_reach'),
               p.get('f_today_post'), p.get('f_tag_post'), p.get('a_today_post'), p.get('a_tag_post'),
               p.get('mp_states'), MPC.get(p.get('mp_cls')), lb, pred]
        out.append(row)
        print('\t'.join(str(x) for x in row))
    json.dump(out, open(os.path.join(RES, 'sweep.json'), 'w'))


# -------------------------------------------------------------------- refusal

REFS = {
    'plain': ('', 1000000),
    'lowsize': ('-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000', 60000),
    'lowboth': ('-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000 '
                '-DPCREC_MAX_AUTO_DFA_ELEMS=3000', 60000),
}
RESOURCE = [rb'(a|b){0,12000}', rb'(a|b){0,30000}', rb'(a|b){1,30000}', rb'(a|b)*a(a|b){20}', rb'((a)|bc){0,4000}d',
            rb'a{0,20000}', rb'a{0,25000}', rb'a{5,25000}', rb'a{20000}', rb'a{8000}', rb'a{9000}', rb'(ab){0,30000}',
            rb'[a-z]{0,30000}', rb'(?:[a-z][0-9]){0,8000}', rb'(?:[a-z][0-9]){1,13000}', rb'[a-zA-Z0-9_.-]{9000}']
RESOURCE_U8 = [rb'\p{L}+', rb'(?:\p{L}?)+', rb'\p{L}', rb'[^\p{C}\p{M}\p{P}]', rb'(\p{L})']
SWEEP_N = [1024, 2048, 2560, 3072, 3328, 3584, 4096, 6144, 8192, 10240, 11264, 12288, 16384]
COMMENT = re.compile(rb'/\*.*?\*/|//[^\n]*', re.S)
INIT = re.compile(rb'static const [^=\[]*?rx_(\w+?)_(\w+)\[(\d+)\]\s*=\s*\{(.*?)\};', re.S)


def build_ref(name):
    flags, _ = REFS[name]
    if name == 'plain':
        return os.path.abspath(rv.PCREC)
    out = os.path.join(OUT, 'pcrec_' + name)
    if os.path.exists(out):
        return out
    srcs = subprocess.run(['bash', '-c', '. tests/lib/lib_srcs.sh; pcrec_lib_srcs .'], cwd=REPO,
                          capture_output=True, text=True).stdout.split()
    subprocess.run(['gcc', '-O1', '-std=gnu11', '-Ilib', '-Isrc'] + flags.split() + ['-o', out, 'cli/main.c'] + srcs,
                   cwd=REPO, check=True)
    return out


def refkey(comp, pat, enc, icase, tag):
    """ok/refusal key of one compile, plus the artifact's facts."""
    tmpd = os.path.join(OUT, 'rf')
    path = os.path.join(tmpd, tag + '.c')
    cmd = rv.NICE + ['gnutimeout', '300', comp, '--features', 'all', '-o', path]
    if icase: cmd.append('-i')
    if enc == 'utf8': cmd += ['-e', 'utf8']
    cmd += ['--pattern', pat]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        first = (p.stderr.decode('latin-1').strip().split('\n') or [''])[0]
        return dict(key='refuse:' + re.sub(r'\d+', 'N', first)[:90] if p.returncode != 124 else 'timeout')
    try:
        txt = open(path, 'rb').read()
    finally:
        for ext in ('.c', '.h'):
            try: os.unlink(path[:-2] + ext)
            except OSError: pass
    d = cost.stamps(txt)
    body = COMMENT.sub(b'', txt)
    roles = collections.defaultdict(lambda: [0, 0])     # role -> [init bytes, next_state cells]
    for m in INIT.finditer(body):
        roles[m.group(1).decode()][0] += len(m.group(0))
    mach = cost.machines(txt)
    return dict(key='ok', scan=d['DFA_SCAN'], tie=d['revend_tie'], bytes=len(body),
                rb={k: v[0] for k, v in roles.items()}, rs={k: v['states'] for k, v in mach.items()})


def refusal():
    os.makedirs(os.path.join(OUT, 'rf'), exist_ok=True)
    comps = {k: build_ref(k) for k in REFS}
    recs = json.load(open(os.path.join(RES, 'census.json')))
    pop = []
    for r in recs:
        pop.append(('revend', r['id'], r['pat'].encode('latin-1'), r['enc'], r['icase']))
    for fam, mk in FAMILIES:
        for N in SWEEP_N:
            pop.append(('sweep', '%s_%d' % (fam, N), mk(N), 'byte', False))
    for w in RESOURCE:
        for suf in (b'$', b'\\s*$'):
            pop.append(('resource', (w + suf).decode(), w + suf, 'byte', False))
    for w in RESOURCE_U8:
        for suf in (b'$', b'\\s*$'):
            pop.append(('resource', (w + suf).decode() + ' utf8', w + suf, 'utf8', False))
    # the probe once per distinct pattern (machines do not depend on the byte caps)
    items = []
    for k, (src, ident, pat, enc, icase) in enumerate(pop):
        v = variants(pat)
        if v: items.append((k, enc, icase, pat, v))
    pres = run_probe(items)

    def job(a):
        k, name = a
        src, ident, pat, enc, icase = pop[k]
        return (k, name), refkey(comps[name], pat, enc, icase, '%s_%d' % (name, k))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = dict(ex.map(job, [(k, n) for k in range(len(pop)) for n in REFS]))
    print('# b3rev refusal-set compare (C3): keys = (population, pattern, variant) -> ok | refusal class')
    print('# B3 never refuses by design: a tagged build over the state cap or an artifact over a byte cap DECLINES to')
    print('# today\'s machines (rows `overflow` / fit_rungs `drop-end-mark`), so the shipped refusal set is unchanged by')
    print('# construction. What is counted here is the set the declines must catch: keys that WOULD join the refusal set')
    print('# if B3 had no decline (predicted from the probe\'s tagged/lowered states and today\'s bytes per state).')
    out = []
    for name, (flags, cap) in REFS.items():
        before, would = set(), set()
        dstate, dsize, tagged_ok = [], [], 0
        for k, (src, ident, pat, enc, icase) in enumerate(pop):
            r = res[(k, name)]
            key = (src, ident)
            if r['key'] != 'ok':
                before.add((key, r['key']))
                continue
            p = pres.get(str(k))
            if not p or r.get('scan') != 'rev-end' or not r.get('tie'):
                continue      # B3's tagged row does not apply: no added machine
            if p.get('tie_pairs', 0) == 0:
                continue      # two-seed row: today's machines
            tagged_ok += 1
            caps_states = max(p.get('r_tag', -1), p.get('f_umin', -1), p.get('a_umin', -1))
            if p.get('status') != 'ok' or p.get('r_tag', 0) < 0 or caps_states >= 32000:
                dstate.append(ident); would.add((key, 'refuse:state-cap (tagged/lowered machine)'))
                continue
            rbyt, rsta = r['rb'].get('reverse', 0), max(1, r['rs'].get('reverse', 1))
            abyt, asta = r['rb'].get('anchored', 0), max(1, r['rs'].get('anchored', 1))
            pred = r['bytes'] + (p['r_tag_post'] - p['r_today_post']) * rbyt / rsta
            if abyt and p.get('a_tag_post', -1) >= 0:
                pred += (p['a_tag_post'] - p['a_today_post']) * abyt / asta
            pred += 64 * 3      # the back table's declaration and the walk's text, a rough constant
            out.append(dict(variant=name, src=src, id=ident, today=r['bytes'], pred=int(pred), cap=cap))
            if pred > cap:
                dsize.append((ident, r['bytes'], int(pred)))
                would.add((key, 'refuse:size-cap (tagged artifact)'))
        print('\n== variant %-8s (byte cap %d): population %d, today refused %d, tagged-row artifacts that compile %d'
              % (name, cap, len(pop), len(before), tagged_ok))
        print('   refusal set if B3 had NO decline: +%d keys (state-cap %d, size-cap %d); with the declines: +0' % (
            len(would), len(dstate), len(dsize)))
        for i in dstate[:12]: print('      state-cap decline: %s' % i)
        for i, a, b in dsize[:12]: print('      size-cap decline:  %-40s today %d -> predicted %d' % (i[:40], a, b))
        by = collections.Counter(k for (_, k) in before)
        for k, n in sorted(by.items()): print('   today refused: %4d  %s' % (n, k))
    json.dump(dict(pop=[(a, b, c.decode('latin-1'), d, e) for (a, b, c, d, e) in pop],
                   res={'%d|%s' % k: v for k, v in res.items()}, pred=out), open(os.path.join(RES, 'refusal.json'), 'w'))


if __name__ == '__main__':
    os.makedirs(RES, exist_ok=True)
    {'census': census, 'sweep': sweep, 'refusal': refusal}[sys.argv[1]]()
