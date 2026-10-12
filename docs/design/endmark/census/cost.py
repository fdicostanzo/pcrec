#!/usr/bin/env python3
"""emcensus COST instrument: today's DFA machines vs the lowered form
`X END_MARK \\n? \\z` for every path-final `$` / `\\Z` / `(?m)$` pattern.
COMPILE-SIDE ONLY.  Population: docs/dev/optloop/revend/census.py's builders
(bench + corpus) filtered by tail_probe's neol/nmeol/nz > 0.

The lowered machine is a TEXT PROXY: each path-final `$`/`\\Z` is rewritten to
`()(?:\\n)?\\z` and each path-final `(?m)$` to `()(?:\\n|\\z)`, `()` standing for
END_MARK (endmark.md's own instrument), then compiled WITH `--no-captures` so the
empty group is an epsilon.  Baseline and proxy are compared under the same
flags.  Fidelity limits: see docs/dev/lanes/emcensus_report.md.

    PCREC=build/pcrec PROBE=build/tmp/tail_probe BENCH=/home/pcrec/projects/pcrec-bench \\
    CORPUS=. OUT=build/tmp/emc python3 -I docs/design/endmark/census/cost.py [rows.tsv]
"""
import collections, concurrent.futures as cf, importlib.util, os, re, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
spec = importlib.util.spec_from_file_location(
    'rv', os.path.join(REPO, 'docs', 'dev', 'optloop', 'revend', 'census.py'))
rv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rv)
sys.path.insert(0, os.path.join(REPO, 'docs', 'design', 'endmark'))
JOBS = int(E.get('JOBS', '6'))
NOCAP_ONLY = False

LOOK_OPEN = (b'(?=', b'(?!', b'(?<=', b'(?<!', b'(?*', b'(?<*', b'(*')


def rewrite(p):
    """Return (new_pattern, n_replaced) rewriting path-final $ / \\Z; (None, 0)
    when the text carries a construct the scanner will not guess about."""
    if b'\\Q' in p:
        return None, 0
    n = len(p)
    i = 0
    stack = []          # per open group: [start_index, is_lookaround]
    cands = []          # (index, length, kind, [open groups])
    mflag = False
    while i < n:
        c = p[i:i + 1]
        if c == b'\\':
            if p[i + 1:i + 2] == b'Z':
                cands.append((i, 2, 'eol', list(stack), mflag))
            i += 2
            continue
        if c == b'[':
            j = i + 1
            if p[j:j + 1] == b'^':
                j += 1
            if p[j:j + 1] == b']':
                j += 1
            while j < n and p[j:j + 1] != b']':
                if p[j:j + 1] == b'\\':
                    j += 1
                elif p[j:j + 2] == b'[:':
                    k = p.find(b':]', j + 2)
                    if k >= 0:
                        j = k + 1
                j += 1
            i = j + 1
            continue
        if c == b'(':
            if p[i:i + 3] == b'(?#':
                k = p.find(b')', i)
                i = (k if k >= 0 else n) + 1
                continue
            m = re.match(rb'\(\?([a-zA-Z^-]*)\)', p[i:])
            if m:                       # inline option
                fl = m.group(1)
                on, _, off = fl.partition(b'-')
                if b'm' in on:
                    mflag = True
                if b'm' in off:
                    mflag = False
                i += m.end()
                continue
            look = p[i:].startswith(LOOK_OPEN) or p[i:].startswith(b'(?(')
            stack.append([i, look])
            i += 1
            continue
        if c == b')':
            if stack:
                stack.pop()
            i += 1
            continue
        if c == b'$':
            cands.append((i, 1, 'dollar', list(stack), mflag))
        i += 1
    if not cands:
        return p, 0

    # matching close paren for each open index
    close = {}
    st = []
    i = 0
    # re-scan cheaply: reuse the same walk but only parens (classes/escapes skipped)
    while i < n:
        c = p[i:i + 1]
        if c == b'\\':
            i += 2; continue
        if c == b'[':
            j = i + 1
            if p[j:j + 1] == b'^': j += 1
            if p[j:j + 1] == b']': j += 1
            while j < n and p[j:j + 1] != b']':
                if p[j:j + 1] == b'\\': j += 1
                elif p[j:j + 2] == b'[:':
                    k = p.find(b':]', j + 2)
                    if k >= 0: j = k + 1
                j += 1
            i = j + 1; continue
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
        """is the position just after a candidate (pos) a path end?"""
        q = pos
        while True:                              # trailing `(?-m)` etc. consume nothing
            m = re.match(rb'\(\?[a-zA-Z^-]*\)', p[q:])
            if not m: break
            q += m.end()
        for g in reversed(groups):
            nxt = p[q:q + 1]
            if nxt == b'|':
                # skip the remaining alternatives to the group's close
                q = close.get(g[0], n)
            elif nxt != b')' and nxt != b'':
                return False
            if g[1]:
                return False                    # inside a lookaround/conditional
            cl = close.get(g[0])
            if cl is None:
                return False
            q = cl + 1
            if p[q:q + 1] in (b'*', b'+', b'{'):
                return False
            if p[q:q + 1] == b'?':
                q += 1
        nxt = p[q:q + 1]
        return nxt in (b'', b'|')

    # alternation: `a$|b` -- at top level `|` ends a path too
    out = []
    last = 0
    cnt = 0
    for (idx, ln, kind, groups, ml) in cands:
        # the char after the candidate must be end / | / )
        if not tail_after(idx + ln, groups):
            continue
        # top-level `|`-ended: only if every enclosing group chain is a tail
        out.append(p[last:idx])
        out.append(b'()(?:\\n|\\z)' if (kind == 'dollar' and ml) else b'()(?:\\n)?\\z')
        last = idx + ln
        cnt += 1
    out.append(p[last:])
    return b''.join(out), cnt


ARR = re.compile(rb'static const (unsigned (?:char|short|int|long)|uint\d+_t|int|char|signed char|short) rx_(\w+?)_(\w+)\[(\d+)\]')
SIZE = {b'unsigned char': 1, b'unsigned short': 2, b'unsigned int': 4, b'unsigned long': 8,
        b'int': 4, b'char': 1, b'signed char': 1, b'short': 2}


def machines(txt):
    """role -> dict(states, bytes, classes) from the emitted C's static tables."""
    roles = collections.defaultdict(lambda: dict(bytes=0, ns=0, ncls=0, arrays=0, eolv=0))
    for m in ARR.finditer(txt):
        ty, role, name, cnt = m.group(1), m.group(2).decode(), m.group(3).decode(), int(m.group(4))
        sz = SIZE.get(ty, 4) * cnt
        r = roles[role]
        r['bytes'] += sz
        r['arrays'] += 1
        if name == 'next_state':
            r['ns'] = cnt
        if name == 'eol_view':
            r['eolv'] = cnt
        if name == 'byte_class':
            # class count = max class id + 1, read off the initializer
            i = m.end()
            j = txt.find(b'};', i)
            vals = [int(x) for x in re.findall(rb'\d+', txt[i:j])]
            r['ncls'] = (max(vals) + 1) if vals else 0
    for r in roles.values():
        r['states'] = r['eolv'] or (r['ns'] // r['ncls'] if r['ncls'] else 0)
    return dict(roles)


def stamps(txt):
    d = {}
    for k in ('ENGINE', 'DFA_SCAN', 'DFA_START', 'DFA_MATCH', 'END_WINDOW'):
        m = re.search(rb'#define RX_%s "([^"]*)"' % k.encode(), txt)
        d[k] = m.group(1).decode() if m else ''
    d['revend_tie'] = b'revend_tie' in txt
    d['nl_last'] = b'nl_last' in txt
    d['eol_view'] = txt.count(b'eol_view')
    d['len'] = len(txt)
    return d


def compile_(pat, enc, icase, nocap, tmpd, tag):
    path = os.path.join(tmpd, tag + '.c')
    cmd = rv.NICE + [rv.PCREC, '--features', 'all', '-o', path]
    if nocap:
        cmd.append('--no-captures')
    if icase:
        cmd.append('-i')
    if enc == 'utf8':
        cmd += ['-e', 'utf8']
    cmd += ['--pattern', pat]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    if p.returncode != 0:
        return None
    try:
        txt = open(path, 'rb').read()
    finally:
        for ext in ('.c', '.h'):
            try: os.unlink(path[:-2] + ext)
            except OSError: pass
    d = stamps(txt)
    d['m'] = machines(txt)
    return d


def work(job):
    i, r, tmpd = job
    out = dict(i=i)
    new, cnt = rewrite(r['pat'])
    out['nrep'] = cnt
    out['new'] = new
    if not cnt:
        return out
    out['df_base'] = compile_(r['pat'], r['enc'], r['icase'], False, tmpd, 'b%ddf' % i)
    out['nc_base'] = compile_(r['pat'], r['enc'], r['icase'], True, tmpd, 'b%dnc' % i)
    out['nc_low'] = compile_(new, r['enc'], r['icase'], True, tmpd, 'l%dnc' % i)
    return out


def main():
    tmpd = os.path.join(rv.OUT, 'cc')
    os.makedirs(tmpd, exist_ok=True)
    rows = rv.bench_pop() + rv.corpus_pop()
    # probe (population filter): neol/nmeol/nz come from tail_probe
    import census as ec                     # docs/design/endmark/census.py
    pr = ec.probe(rows)
    pop = [i for i in range(len(rows)) if pr.get(i, {}).get('status') == 'ok' and
           any(int(pr[i].get(k, '0') or 0) for k in ('neol', 'nmeol', 'nz'))]
    print('# emcensus cost at %s' % subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'],
          capture_output=True, text=True).stdout.strip())
    c = collections.Counter((rows[i]['pop'], rows[i]['enc']) for i in range(len(rows)))
    print('== populations (rows): ' + ', '.join('%s/%s=%d' % (k[0], k[1], v) for k, v in sorted(c.items())))
    ok = collections.Counter(rows[i]['pop'] for i in range(len(rows)) if pr.get(i, {}).get('status') == 'ok')
    print('== parsed by probe: ' + ', '.join('%s=%d' % kv for kv in sorted(ok.items())))
    print('== path-final $/\\Z/(?m)$/\\z patterns (probe neol|nmeol|nz>0): ' +
          ', '.join('%s=%d' % kv for kv in sorted(collections.Counter(rows[i]['pop'] for i in pop).items())))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(work, [(i, rows[i], tmpd) for i in pop]))
    # \z-only patterns: probe nz counts \Z and \z together? keep honest: count rewritten
    rewritten = [r for r in res if r['nrep']]
    print('== rewritten by the text scanner: %d of %d (unrewritten: %d)' %
          (len(rewritten), len(pop), len(pop) - len(rewritten)))
    for r in res:
        if not r['nrep']:
            print('   UNREWRITTEN %s  %s' % (rows[r['i']]['id'], rows[r['i']]['pat'].decode('latin-1')[:70]))
    return rows, res


def summarise(rows, res):
    def total(d):
        return (sum(m['states'] for m in d['m'].values()), sum(m['bytes'] for m in d['m'].values()))
    den0 = collections.Counter()
    for r in res:
        if r['nrep']:
            b = r.get('df_base')
            den0[(rows[r['i']]['pop'], b['ENGINE'] if b else 'compile-failed')] += 1
    print('\n== rewritten patterns by SHIPPED-default engine today (captures on): ' +
          ', '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(den0.items())))
    print('   (the proxy `()` is a capture group, so it is compared only under --no-captures)')
    for tag, label in (('nc', '--no-captures (baseline and proxy both; DFA for every shape that can)'),):
        print('\n==== %s ====' % label)
        den = collections.Counter()
        paired = []
        for r in res:
            if not r['nrep']:
                continue
            b, l = r.get(tag + '_base'), r.get(tag + '_low')
            kind = 'ml' if re.search(rb'\(\?[a-z]*m', rows[r['i']]['pat']) else 'plain'
            pop = rows[r['i']]['pop']
            if b is None or l is None:
                den[(pop, 'compile-failed(base=%s low=%s)' % (b is not None, l is not None))] += 1
                continue
            eb, el = b['ENGINE'], l['ENGINE']
            den[(pop, 'engine %s->%s' % (eb, el))] += 1
            if not b['m'] and not l['m']:
                continue
            paired.append((r, b, l))
        print('denominators (artifact engine before->after):')
        for k in sorted(den):
            print('   %-7s %s  %d' % (k[0], k[1], den[k]))
        # per-pair role comparison
        dstat = collections.Counter()
        grow = []
        for r, b, l in paired:
            pop = rows[r['i']]['pop']
            sb, bb = total(b); sl, bl = total(l)
            dstat[(pop, 'both-have-tables' if sb and sl else 'tables %s->%s' % (bool(sb), bool(sl)))] += 1
            if not (sb and sl):
                continue
            grow.append(dict(id=rows[r['i']]['id'], pat=rows[r['i']]['pat'].decode('latin-1')[:60],
                             pop=pop, sb=sb, sl=sl, bb=bb, bl=bl, scb=b['DFA_SCAN'], scl=l['DFA_SCAN'],
                             rb=sorted(b['m']), rl=sorted(l['m']),
                             tie=b['revend_tie'], lenb=b['len'], lenl=l['len'],
                             kind=('ml' if re.search(rb'\(\?[a-z]*m', rows[r['i']]['pat']) else 'plain'), mb={k: v['states'] for k, v in b['m'].items()},
                             ml={k: v['states'] for k, v in l['m'].items()}))
        print('table presence:')
        for k in sorted(dstat):
            print('   %-7s %-28s %d' % (k[0], k[1], dstat[k]))
        report(grow)


def report(grow):
    if not grow:
        return
    print('\nSTATE-COUNT delta, TOTAL over all tabulated machines of the artifact (lowered - today), n=%d:' % len(grow))
    dist = collections.Counter(g['sl'] - g['sb'] for g in grow)
    for d in sorted(dist):
        print('   %+4d states: %d' % (d, dist[d]))
    for pop in ('bench', 'corpus'):
        gs = [g for g in grow if g['pop'] == pop]
        if gs:
            print('   %s n=%d  sum states %d -> %d  sum table bytes %d -> %d  emitted-C bytes %d -> %d' % (
                pop, len(gs), sum(g['sb'] for g in gs), sum(g['sl'] for g in gs),
                sum(g['bb'] for g in gs), sum(g['bl'] for g in gs),
                sum(g['lenb'] for g in gs), sum(g['lenl'] for g in gs)))
    import statistics
    for kind in ('plain', 'ml'):
        gs = [g for g in grow if g['kind'] == kind]
        if gs:
            print('   kind %-5s n=%d  states %d -> %d (%+.1f%%)  table B %d -> %d (%+.1f%%)  median total delta %+.1f states' % (
                kind, len(gs), sum(g['sb'] for g in gs), sum(g['sl'] for g in gs),
                100.0 * (sum(g['sl'] for g in gs) / sum(g['sb'] for g in gs) - 1),
                sum(g['bb'] for g in gs), sum(g['bl'] for g in gs),
                100.0 * (sum(g['bl'] for g in gs) / sum(g['bb'] for g in gs) - 1),
                statistics.median(g['sl'] - g['sb'] for g in gs)))
    rel = sorted((g['sl'] / g['sb'], g['id']) for g in grow)
    print('   per-artifact state ratio: median %.2fx, p90 %.2fx, max %.2fx' % (
        rel[len(rel) // 2][0], rel[int(len(rel) * .9)][0], rel[-1][0]))
    # same-role comparison
    print('\nSAME-ROLE state deltas (role present before and after), count by delta:')
    rd = collections.defaultdict(collections.Counter)
    for g in grow:
        for role in g['mb']:
            if role in g['ml']:
                rd[role][g['ml'][role] - g['mb'][role]] += 1
    for role in sorted(rd):
        print('   role %-10s ' % role + ', '.join('%+d:%d' % (d, n) for d, n in sorted(rd[role].items())))
    rb = collections.Counter()
    for g in grow:
        rb[(tuple(g['rb']), tuple(g['rl']), g['scb'], g['scl'])] += 1
    print('\nroute change (roles, DFA_SCAN) before -> after:')
    for k, n in rb.most_common(20):
        print('   %4d  %s %s -> %s %s' % (n, '+'.join(k[0]), k[2], '+'.join(k[1]), k[3]))
    print('\nWORST BY TOTAL STATE GROWTH (top 15):')
    for g in sorted(grow, key=lambda g: (g['sl'] - g['sb']), reverse=True)[:15]:
        print('   %-7s %+4d states (%d->%d) %+6d table B (%d->%d)  %s  %s' % (
            g['pop'], g['sl'] - g['sb'], g['sb'], g['sl'], g['bl'] - g['bb'], g['bb'], g['bl'], g['id'], g['pat']))
    print('\nWORST BY TABLE-BYTES GROWTH (top 10):')
    for g in sorted(grow, key=lambda g: (g['bl'] - g['bb']), reverse=True)[:10]:
        print('   %-7s %+6d table B (%d->%d) %+4d states  %s  %s' % (
            g['pop'], g['bl'] - g['bb'], g['bb'], g['bl'], g['sl'] - g['sb'], g['id'], g['pat']))
    print('\nBEST (shrinks), top 8:')
    for g in sorted(grow, key=lambda g: (g['sl'] - g['sb']))[:8]:
        print('   %-7s %+4d states (%d->%d) %+6d table B  %s  %s' % (
            g['pop'], g['sl'] - g['sb'], g['sb'], g['sl'], g['bl'] - g['bb'], g['id'], g['pat']))
    # the E3 gate: no machine grows by more than one
    over = [g for g in grow if any(g['ml'].get(role, 0) - n > 1 for role, n in g['mb'].items())]
    print('\nE3 GATE (a same-role machine grows by more than 1 state): %d of %d artifacts' % (len(over), len(grow)))
    for g in over[:15]:
        print('   %s  %s  %s -> %s' % (g['id'], g['pat'], g['mb'], g['ml']))


if __name__ == '__main__':
    rows, res = main()
    summarise(rows, res)
