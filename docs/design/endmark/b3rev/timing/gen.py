#!/usr/bin/env python3
"""b3rev timing (sub-lane of lane b3rev, 2026-10-12): which emitted FORM the B3
one-seed walk takes ([REVEND-WALK-FORM]), and D164 addendum 4's lowered tie
finishers.  Never run by make.  Reuses ../../b3meas/gen.py (imported, never
edited) for the population, the machine probe, the tagged product, the B3 twin,
the restyled control R, the load instrumentation and the subjects.

Arms (E, one artifact each; every arm is its own pcrec compile with its own
prefix, its search body spliced where it is not today's):
  T   today's shipped artifact            A   its A/A copy (same command, -p A)
  R   today's algorithm, plain style (b3meas's control; two seeds)
  V   R with today's PER-BYTE view probe in the loop (E2 ablation)
  S   R with today's STAY placement: non-accepting self-loop run skips tested
      at the loop TOP every iteration (E2 ablation)
  U   today's emitted text with the seed loop replaced by the one-seed rule
      (seed n-1 iff s[n-1]=='\\n' and n-1 >= startpos, else n; when seed n-1
      finds nothing, seed n's zero-length accept AT n is probed statically)
  P   the same one-seed algorithm in R's plain style ("Up")
  W   P with the seed's first step peeled per seed (the seed state a
      constant on each arm, as R's seed-n prelude has it)
  B   b3meas's B3 twin (tagged product, plain)  Q   B in today's step shape
      (stay placement; the tagged machine has no views)
Arms (part A): see aharness.c.

    PCREC=build/pcrec B3PROBE=build/scratch/b3revtime/b3meas_probe \\
    OUT=build/scratch/b3revtime TMPDIR=build/scratch/b3revtime/tmp \\
    python3 -I docs/design/endmark/b3rev/timing/gen.py ebuild|etime|abuild|atime [k,k,...]
"""
import collections, concurrent.futures as cf, importlib.util, json, os, random, re, struct, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
B3M = os.path.abspath(os.path.join(HERE, '..', '..', 'b3meas'))
spec = importlib.util.spec_from_file_location('bm', os.path.join(B3M, 'gen.py'))
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)
import pcre2                                      # docs/design/endmark/pcre2.py (bm put it on sys.path)
OUT = os.path.abspath(E['OUT'])
RES = os.path.join(HERE, 'results')
CC = ['gcc', '-O2', '-std=gnu11', '-w']
JOBS = int(E.get('JOBS', '6'))
CPU = E.get('CPU', '2')
MEAS = {r['k']: r for r in json.load(open(os.path.join(B3M, 'results', 'check.json')))}


def sel(rows):
    if len(sys.argv) > 2:
        want = set(sys.argv[2].split(','))
        rows = [r for r in rows if str(r['k']) in want]
    return rows

# ---------------------------------------------------------------- restyled walks


def arr(ty, name, vals):
    rows = ['        ' + ', '.join(str(v) for v in vals[i:i + 16]) + ',' for i in range(0, len(vals), 16)]
    return '    static const %s %s[%d] = {\n%s\n    };\n' % (ty, name, len(vals), '\n'.join(rows))


def restyle(M, prefix, views='prelude', stays='after', seeds='two'):
    """today's algorithm over today's machine (b3meas's R) with three switches:
    views   'prelude' = R (seed n pre-viewed, one eol probe after seed n's
            first step) | 'loop' = today's per-byte probe at the loop top;
    stays   'after' = R (every self-loop state's run skip behind the stop
            compare) | 'top' = today's: non-accepting ones tested at the loop
            top on every iteration, accepting ones stay behind the compare;
    seeds   'two' = today's seed loop | 'one' = the one-seed-by-last-byte rule.
    Only for artifacts without tie code (nl_last false)."""
    if M['natoms'] > 1 or M['clsctx']:
        return None
    S, C = M['n'], M['ncls']
    tr = [[M['TR'][q * C + c] for c in range(C)] for q in range(S)]
    runs = []
    for q in range(S):
        loop = [b for b in range(256) if tr[q][M['CLS'][b]] == q]
        if loop:
            runs.append((q, loop))
    top = [(q, l) for q, l in runs if stays == 'top' and not M['ACC'][q]]
    after = [(q, l) for q, l in runs if (q, l) not in top]
    rs = dict(after)
    order = [q for q in range(S) if q not in rs] + [q for q, _ in after]
    num = {q: k for k, q in enumerate(order)}
    stop = (S - len(after)) * C

    def pm(t):
        return 65535 if t < 0 else num[t] * C
    nxt, accp, eolv, endv = [0] * (S * C), [0] * (S * C), [65535] * S, [65535] * S
    for q in range(S):
        for c in range(C):
            nxt[num[q] * C + c] = pm(tr[q][c])
            accp[num[q] * C + c] = M['ACC'][q]
        if M['EOL'][q] >= 0:
            eolv[num[q]] = pm(M['EOL'][q])
        if M['END'][q] >= 0:
            endv[num[q]] = pm(M['END'][q])
    s0 = M['s0']
    seed_n = bm.view(M, s0)
    seed_n1 = M['EOL'][s0] if M['EOL'][s0] >= 0 else s0
    o = ['int %s_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n' % prefix,
         '    if (search_from > subject_length) return 0;\n',
         arr('unsigned char', 'r_cls', M['CLS']), arr('unsigned short', 'r_next', nxt),
         arr('unsigned char', 'r_acc', accp), arr('unsigned short', 'r_eolv', eolv)]
    if views == 'loop':
        o.append(arr('unsigned short', 'r_endv', endv))
    tabs = {}
    for q, loop in runs:
        if tuple(loop) not in tabs:
            tabs[tuple(loop)] = num[q]
            o.append(arr('unsigned char', 'r_run%d' % num[q], [1 if b in loop else 0 for b in range(256)]))

    def walk(ind):
        w = [ind + 'for (;;) {\n']
        for q, loop in top:
            w.append(ind + '    if (st == %du && pos + 1 < subject_length)\n' % pm(q) +
                     ind + '        while (pos > search_from && r_run%d[subject[pos - 1]]) pos--;\n' % tabs[tuple(loop)])
        if views == 'loop':
            w.append(ind + '    unsigned vs = st;\n' +
                     ind + '    if (__builtin_expect(pos + 1 >= subject_length, 0)) {\n' +
                     ind + '        if (pos == subject_length) {\n' +
                     ind + '            if (r_endv[st / %d] != 65535) vs = r_endv[st / %d];\n' % (C, C) +
                     ind + '            else if (r_eolv[st / %d] != 65535) vs = r_eolv[st / %d];\n' % (C, C) +
                     ind + '        } else if (subject[pos] == \'\\n\' && r_eolv[st / %d] != 65535) vs = r_eolv[st / %d];\n' % (C, C) +
                     ind + '    }\n')
        else:
            w.append(ind + '    unsigned vs = st;\n')
        w.append(ind + '    if (r_acc[vs]) mstart = pos;\n' +
                 ind + '    if (pos <= search_from) break;\n' +
                 ind + '    st = r_next[vs + r_cls[subject[--pos]]];\n' +
                 (ind + '  stepped:\n' if seeds == 'one-peel' else '') +
                 ind + '    if (st < %du) continue;\n' % stop +
                 ind + '    if (st == 65535) break;\n')
        guard = 'pos + 1 < subject_length && ' if views == 'loop' else ''
        for q, loop in after:
            w.append(ind + '    if (st == %du%s) { while (pos > search_from && r_run%d[subject[pos - 1]]) pos--; continue; }\n'
                     % (pm(q), (' && ' + guard[:-4]) if guard else '', tabs[tuple(loop)]))
        w.append(ind + '}\n')
        return ''.join(w)

    raw = pm(s0) if views == 'loop' else None
    if seeds == 'one-peel':
        if views != 'prelude':
            raise ValueError('one-seed is built in the prelude (R) style only')
        o.append('    int seed = subject_length > search_from && subject[subject_length - 1] == \'\\n\';\n'
                 '    size_t pos, mstart = (size_t)-1;\n'
                 '    unsigned st;\n'
                 '    if (seed) {   /* the seed state is a constant on each arm: its first step peeled */\n'
                 '        pos = subject_length - 1;\n'
                 '        if (r_acc[%du]) mstart = pos;\n' % pm(seed_n1) +
                 '        if (pos <= search_from) goto walked;\n'
                 '        st = r_next[%du + r_cls[subject[--pos]]];\n' % pm(seed_n1) +
                 '    } else {\n'
                 '        pos = subject_length;\n'
                 '        if (r_acc[%du]) mstart = pos;\n' % pm(seed_n) +
                 '        if (pos <= search_from) goto walked;\n'
                 '        st = r_next[%du + r_cls[subject[--pos]]];\n' % pm(seed_n) +
                 '    }\n'
                 '    goto stepped;\n')
        o.append(walk('    '))
        o.append('  walked:;\n'
                 '    size_t best, bend;\n'
                 '    if (mstart == (size_t)-1) {\n'
                 '        if (!(seed && r_acc[%du])) return 0;   /* seed n: its zero-length accept AT n */\n' % pm(seed_n) +
                 '        best = bend = subject_length;\n'
                 '    } else { best = mstart; bend = seed ? subject_length - 1 : subject_length; }\n')
    elif seeds == 'one':
        if views != 'prelude':
            raise ValueError('one-seed is built in the prelude (R) style only')
        o.append('    int seed = subject_length > search_from && subject[subject_length - 1] == \'\\n\';\n'
                 '    size_t pos = seed ? subject_length - 1 : subject_length, mstart = (size_t)-1;\n'
                 '    unsigned st = seed ? %du : %du;\n' % (pm(seed_n1), pm(seed_n)))
        o.append(walk('    '))
        o.append('    size_t best, bend;\n'
                 '    if (mstart == (size_t)-1) {\n'
                 '        if (!(seed && r_acc[%du])) return 0;   /* seed n: its zero-length accept AT n */\n' % pm(seed_n) +
                 '        best = bend = subject_length;\n'
                 '    } else { best = mstart; bend = seed ? subject_length - 1 : subject_length; }\n')
    else:
        o.append('    size_t best = (size_t)-1, bend = 0;\n'
                 '    for (int seed = 0; seed < 2; seed++) {\n'
                 '        size_t pos = subject_length, mstart = (size_t)-1;\n'
                 '        unsigned st = %du;\n' % (raw if views == 'loop' else pm(seed_n)) +
                 '        if (seed == 1) {\n'
                 '            if (subject_length == 0 || subject[subject_length - 1] != \'\\n\') break;\n'
                 '            pos = subject_length - 1;\n'
                 '            st = %du;\n' % (raw if views == 'loop' else pm(seed_n1)) +
                 '        }\n'
                 '        if (pos < search_from) break;\n')
        if views == 'prelude':
            o.append('        if (seed == 0) {\n'
                     '            if (r_acc[st]) mstart = pos;\n'
                     '            if (pos <= search_from) goto seed_done;\n'
                     '            st = r_next[st + r_cls[subject[--pos]]];\n'
                     '            if (st == 65535) goto seed_done;\n'
                     '            if (subject[pos] == \'\\n\' && r_eolv[st / %d] != 65535) st = r_eolv[st / %d];\n' % (C, C) +
                     '        }\n')
        o.append(walk('        '))
        o.append('      seed_done:\n'
                 '        if (mstart == (size_t)-1) continue;\n'
                 '        if (mstart < best) { best = mstart; bend = seed ? subject_length - 1 : subject_length; }\n'
                 '    }\n'
                 '    if (best == (size_t)-1) return 0;\n')
    o.append('    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)best; capture_spans[0][1] = (ptrdiff_t)bend; }\n'
             '    return 1;\n}\n')
    return ''.join(o)


def twin_today_shape(M, prefix, prio):
    """b3meas's B3 twin body with today's STAY placement: a non-accepting
    self-loop state's run skip is tested at the loop top on every iteration
    (today's `T_reverse_stayN` shape); accepting ones keep the after-compare
    edge.  The tagged machine has no views, so today's emitter would write no
    view probe for it."""
    txt, info = bm.twin_body(M, prefix, prio)
    S, C = M['S'], M['C']
    runs = []
    for s in range(S):
        loop = [b for b in range(256) if M['tr'][s][M['bytecls'][b]] == s]
        if loop:
            runs.append((s, loop))
    order = [s for s in range(S) if s not in dict(runs)] + [s for s, _ in runs]
    num = {s: k for k, s in enumerate(order)}
    tops = [(s, l) for s, l in runs if not (M['acc'][s])]
    if not tops:
        return txt, info, 0
    tabs = {}
    for s, loop in runs:
        tabs.setdefault(tuple(loop), num[s])
    lines = txt.split('\n')
    out = []
    for ln in lines:
        m = re.match(r'        if \(st == (\d+)u\) \{ while \(pos > search_from && b3_run(\d+)\[subject\[pos - 1\]\]\) pos--; continue; \}$', ln)
        if m and any(num[s] * C == int(m.group(1)) for s, _ in tops):
            continue                                  # moved to the loop top
        out.append(ln)
        if ln == '    for (;;) {':
            for s, loop in tops:
                out.append('        if (st == %du)\n            while (pos > search_from && b3_run%d[subject[pos - 1]]) pos--;'
                           % (num[s] * C, tabs[tuple(loop)]))
    return '\n'.join(out), info, len(tops)


def make_u(txt, p):
    """today's emitted search body (prefix p) with its seed loop replaced by the
    one-seed rule and the static probe of seed n's accept at n."""
    a, b = bm.search_span(txt, p)
    body = txt[a:b]
    old = '    for (int revend_seed = 0; revend_seed < 2; revend_seed++) {\n'
    if body.count(old) != 1:
        return None, 'no-two-seed-loop'
    m = re.search(r'\n        %s_reverse_state reverse_state = (\d+);\n' % p, body)
    if not m:
        return None, 'no-seed-line'
    seed = m.group(1)
    vb = re.search(r'\n(            %s_reverse_state reverse_view_state = reverse_state;\n.*?)'
                   r'(            if \(%s_reverse_accepts\([^\n]*\)\) match_start_position = rewind_position;\n)' % (p, p),
                   body, re.S)
    if not vb or 'while' in vb.group(1) or 'search_from' in vb.group(1):
        return None, 'ctx-accept'
    probe = ('    if (revend_start == (size_t)-1 && revend_pick) {   /* seed n: its zero-length accept AT n */\n'
             '        size_t rewind_position = subject_length, match_start_position = (size_t)-1;\n'
             '        %s_reverse_state reverse_state = %s;\n' % (p, seed) +
             ''.join(l[4:] + '\n' for l in (vb.group(1) + vb.group(2)).rstrip('\n').split('\n')) +
             '        if (match_start_position != (size_t)-1) { revend_start = subject_length; revend_end = subject_length; }\n'
             '    }\n')
    new = ('    int revend_pick = subject_length > search_from && subject[subject_length - 1] == \'\\n\';\n'
           '    for (int revend_seed = revend_pick; revend_seed == revend_pick; revend_seed = 2) {\n')
    body = body.replace(old, new)
    chk = ('        if (revend_seed == 1) {\n'
           '            if (subject_length == 0 || subject[subject_length - 1] != \'\\n\') break;\n'
           '            match_end_position = subject_length - 1;\n'
           '        }\n')
    if body.count(chk) != 1:
        return None, 'no-seed1-check'
    # the pick already read s[n-1]; today's re-check would be a second load
    body = body.replace(chk, '        if (revend_seed == 1) match_end_position = subject_length - 1;\n')
    tail ='    if (revend_start == (size_t)-1) return 0;\n'
    if body.count(tail) != 1:
        return None, 'no-tail'
    body = body.replace(tail, probe + tail)
    return txt[:a] + body + txt[b:], None


def splice(base, p, newbody):
    a, b = bm.search_span(base, p)
    return base[:a] + newbody + base[b:]

# ---------------------------------------------------------------- E build


def write_vars(d, names):
    open(os.path.join(d, 'vars.h'), 'w').write('#define VARS %s\n' % ' '.join('X(%s)' % n for n in names))


def ebuild_one(r, mt, tmach):
    k = r['k']
    d = os.path.join(OUT, 'e%d' % k)
    os.makedirs(d, exist_ok=True)
    res = dict(k=k, pops=r['pops'], nrows=r['nrows'], pat=r['pat'].decode('latin1'), icase=r['icase'])
    meas = MEAS.get(k, {})
    if r['enc'] != 'byte' or 'skip' in meas or not meas:
        res['skip'] = 'b3meas:' + meas.get('skip', 'absent')
        return res
    nocap = meas['nocap']
    res['nocap'] = nocap
    comp = lambda p: bm.pcrec(r['pat'], r['icase'], p, os.path.join(d, p + 'base.c'), nocap)
    T = comp('T')
    if T is None or bm.stamp(T, 'T', 'DFA_SCAN') != 'rev-end':
        res['skip'] = 'not-revend'
        return res
    open(os.path.join(d, 'T.c'), 'w').write(T)
    res['tie'] = 'revend_tie' in T
    res['two_seed'] = 'revend_seed < 2' in T
    res['cls'] = 'tie' if res['tie'] else ('notie' if res['two_seed'] else 'oneseed')
    if res['cls'] == 'oneseed':
        res['skip'] = 'oneseed (\\z only: no seed loop)'
        return res
    open(os.path.join(d, 'A.c'), 'w').write(comp('A'))
    tm = tmach.get(str(k))
    if not tm:
        res['skip'] = 'probe-failed'
        return res
    names = ['T', 'A']
    if res['tie']:
        Rb = bm.restyle_body(tm[0], 'R')
        M = bm.product(mt[str(k)][0], mt[str(k)][1]) if mt.get(str(k)) else 'probe-failed'
        if Rb is None or isinstance(M, str):
            res['skip'] = 'restyle/twin unbuilt: %s' % (M if isinstance(M, str) else 'ctx')
            return res
        prio = meas['prio']
        prio = prio if prio in ('const0', 'const1') else 'verify'
        res['prio'] = prio
        open(os.path.join(d, 'R.c'), 'w').write(splice(comp('R'), 'R', Rb))
        Bb, info = bm.twin_body(M, 'B', prio)
        open(os.path.join(d, 'B.c'), 'w').write(splice(comp('B'), 'B', Bb))
        Qb, _, ntop = twin_today_shape(M, 'Q', prio)
        res['q_tops'] = ntop
        open(os.path.join(d, 'Q.c'), 'w').write(splice(comp('Q'), 'Q', Qb))
        names += ['R', 'B', 'Q']
    else:
        bodies = dict(R=restyle(tm[0], 'R'), V=restyle(tm[0], 'V', views='loop'),
                      S=restyle(tm[0], 'S', stays='top'), P=restyle(tm[0], 'P', seeds='one'),
                      W=restyle(tm[0], 'W', seeds='one-peel'))
        if any(v is None for v in bodies.values()):
            res['skip'] = 'ctx (restyle unbuilt)'
            return res
        for p, bd in bodies.items():
            open(os.path.join(d, p + '.c'), 'w').write(splice(comp(p), p, bd))
        Ut, why = make_u(comp('U'), 'U')
        if Ut is None:
            res['skip'] = 'U unbuilt: ' + why
            return res
        open(os.path.join(d, 'U.c'), 'w').write(Ut)
        names += ['R', 'V', 'S', 'U', 'P', 'W']
        S_, C_ = tm[0]['n'], tm[0]['ncls']
        res['s_tops'] = sum(1 for q in range(S_) if not tm[0]['ACC'][q] and
                            any(tm[0]['TR'][q * C_ + tm[0]['CLS'][b]] == q for b in range(256)))
    res['arms'] = names
    with open(os.path.join(d, 'pat'), 'wb') as f:
        f.write(r['pat'])
    code = pcre2.Code(r['pat'], extra=0x00000008 if r['icase'] else 0)
    subs = bm.subjects(code, random.Random(k * 7919 + 1))
    bm.write_subjects(os.path.join(d, 'subjects.bin'), subs)
    al = bm.alphabet(r['pat'])
    res['alphabet'] = al.decode('latin1')
    # CHECK: every arm but A, load-instrumented
    ck = [n for n in names if n != 'A']
    files = []
    for n in ck:
        p = os.path.join(d, n + 'I.c')
        open(p, 'w').write(bm.instrument(open(os.path.join(d, n + '.c')).read()))
        files.append(p)
    cd = os.path.join(d, 'chk')
    os.makedirs(cd, exist_ok=True)
    write_vars(cd, ck)
    exe = os.path.join(d, 'check')
    pr = subprocess.run(CC + ['-DCHECK', '-I', cd, '-o', exe, os.path.join(HERE, 'harness.c')] + files + ['-lpcre2-8'],
                        capture_output=True, text=True, timeout=600)
    if pr.returncode:
        res['skip'] = 'check build: ' + pr.stderr[:400]
        return res
    pr = subprocess.run([exe, os.path.join(d, 'pat'), '1' if r['icase'] else '0', os.path.join(d, 'subjects.bin'),
                         al.decode('latin1'), '5'], capture_output=True, text=True, timeout=3600)
    if pr.returncode:
        res['skip'] = 'check rc=%d %s' % (pr.returncode, pr.stderr[:300])
        return res
    regs, exh = collections.defaultdict(dict), {}
    for ln in pr.stdout.split('\n'):
        f = ln.split('\t')
        if f[0] == 'check':
            regs[f[1]][f[4]] = dict(n=int(f[2]), nm=int(f[3]), wrong=int(f[5]), loads=float(f[6]))
        elif f[0] == 'exh':
            exh[f[1]] = dict(cells=int(f[2]), wrong=int(f[3]))
    res['regs'] = regs
    res['exh'] = exh
    res['wrong'] = {n: exh[n]['wrong'] + sum(regs[g][n]['wrong'] for g in regs) for n in ck}
    # TIME binary (built now; run by etime)
    td = os.path.join(d, 'tim')
    os.makedirs(td, exist_ok=True)
    good = [n for n in names if n == 'A' or res['wrong'][n] == 0]
    write_vars(td, good)
    pr = subprocess.run(CC + ['-DTIME', '-I', td, '-o', os.path.join(d, 'time'), os.path.join(HERE, 'harness.c')] +
                        [os.path.join(d, n + '.c') for n in good], capture_output=True, text=True, timeout=600)
    res['timed_arms'] = good if not pr.returncode else []
    return res


def safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:      # recorded, never silently dropped
        r = a[0]
        return dict(k=r['k'], pat=r['pat'].decode('latin1'), skip='error: %s' % str(e)[:300])


def tagged_inputs(rows):
    vin = []
    for r in rows:
        new, cnt = bm.cost.rewrite(r['pat'])
        if not cnt or new is None or new.count(bm.MARK) != cnt:
            continue
        pre = b'(?i)' if r['icase'] else b''
        vin.append((str(r['k']), pre + new.replace(bm.MARK, b'\\z'), pre + new.replace(bm.MARK, b'\\n\\z')))
    return vin


def ebuild():
    rows = sel(bm.read_pop())
    mt = bm.probe_machines(tagged_inputs(rows))
    tmach = bm.probe_machines([(str(r['k']), (b'(?i)' if r['icase'] else b'') + r['pat'],
                                (b'(?i)' if r['icase'] else b'') + r['pat']) for r in rows])
    with cf.ThreadPoolExecutor(JOBS) as ex:
        out = list(ex.map(lambda r: safe(ebuild_one, r, mt, tmach), rows))
    name = E.get('EOUT', 'echeck.json')
    json.dump(out, open(os.path.join(RES, name), 'w'))
    c = collections.Counter(r.get('cls', '-') if 'skip' not in r else 'skip:' + r['skip'][:30] for r in out)
    print(dict(c))
    for r in out:
        if 'wrong' in r and any(r['wrong'].values()):
            print('WRONG', r['k'], r['pat'], r['wrong'])


def etime():
    res = json.load(open(os.path.join(RES, E.get('EOUT', 'echeck.json'))))
    for r in sel(res):
        if 'skip' in r or not r.get('timed_arms'):
            continue
        if E.get('CLS') and r['cls'] != E['CLS']:
            continue
        d = os.path.join(OUT, 'e%d' % r['k'])
        p = subprocess.run(['taskset', '-c', CPU, os.path.join(d, 'time'), os.path.join(d, 'pat'),
                            '1' if r['icase'] else '0', os.path.join(d, 'subjects.bin')],
                           capture_output=True, text=True, timeout=3600)
        for ln in p.stdout.split('\n'):
            if ln.startswith('time\t'):
                print('%d\t%s' % (r['k'], ln[5:]), flush=True)

# ---------------------------------------------------------------- A build


def lowered(pat):
    new, cnt = bm.cost.rewrite(pat)
    if not cnt or new is None or new.count(bm.MARK) != cnt:
        return None
    return new.replace(bm.MARK, b'(?:\\n)?\\z')


def states_of(txt, p, mach):
    m = re.search(r'static const unsigned short %s_%s_next_state\[(\d+)\]' % (p, mach), txt)
    c = re.search(r'static const unsigned char %s_%s_byte_class\[256\] = \{\n(.*?)\n    \};' % (p, mach), txt, re.S)
    if not m or not c:
        return None
    ncls = max(int(x) for x in re.findall(r'\d+', c.group(1))) + 1
    return int(m.group(1)) // ncls


def abuild_one(r):
    k = r['k']
    d = os.path.join(OUT, 'a%d' % k)
    os.makedirs(d, exist_ok=True)
    meas = MEAS.get(k, {})
    res = dict(k=k, pops=r['pops'], pat=r['pat'].decode('latin1'), icase=r['icase'])
    if 'skip' in meas:
        res['skip'] = 'b3meas:' + meas['skip']
        return res
    low = lowered(r['pat'])
    if low is None:
        res['skip'] = 'no rewrite'
        return res
    res['lowered'] = low.decode('latin1')
    nocap = meas['nocap']
    res['nocap'] = nocap
    res['prio'] = meas['prio']
    res['cyclic'] = meas['twin']['cyclic']

    def comp(pat, p, extra=()):
        cmd = [bm.PCREC, '--features', 'all', '-p', p, '-o', os.path.join(d, p + '.c')] + list(extra)
        if r['icase']:
            cmd.append('-i')
        if nocap:
            cmd.append('--no-captures')
        cmd += ['--pattern', pat]
        pr = subprocess.run(cmd, capture_output=True, timeout=300)
        if pr.returncode:
            raise RuntimeError('pcrec %s: %s' % (p, pr.stderr[:300]))
        return open(os.path.join(d, p + '.c')).read()
    arts = dict(T=comp(r['pat'], 'T'), A=comp(r['pat'], 'A'), L=comp(low, 'L'),
                N=comp(r['pat'], 'N', ['-fno-rev-end']), M=comp(r['pat'], 'M', ['-fno-rev-end']),
                K=comp(low, 'K', ['-fno-rev-end']))
    res['stamps'] = {p: dict(engine=bm.stamp(t, p, 'ENGINE'), scan=bm.stamp(t, p, 'DFA_SCAN'),
                             match=bm.stamp(t, p, 'DFA_MATCH')) for p, t in arts.items()}
    if any(res['stamps'][p]['engine'] != 'dfa' for p in arts):
        res['skip'] = 'not dfa: %s' % {p: s['engine'] for p, s in res['stamps'].items()}
        return res
    res['states'] = {p: {m: states_of(arts[p], p, m) for m in ('forward', 'reverse', 'anchored')} for p in arts}
    with open(os.path.join(d, 'pat'), 'wb') as f:
        f.write(r['pat'])
    code = pcre2.Code(r['pat'], extra=0x00000008 if r['icase'] else 0)
    subs = bm.subjects(code, random.Random(k * 7919 + 1))
    with open(os.path.join(d, 'asubjects.bin'), 'wb') as f:
        for name, lst in subs.items():
            if not name.endswith('-nl-m'):
                continue
            for s in lst:
                m = code.match(s, 0)
                f.write(name.encode() + b'\0' + struct.pack('<II', len(s), m[0][0]) + s)
    files = [os.path.join(d, p + '.c') for p in arts]
    for mode in ('CHECK', 'TIME'):
        pr = subprocess.run(CC + ['-D' + mode, '-I', d, '-o', os.path.join(d, mode.lower()),
                                  os.path.join(HERE, 'aharness.c')] + files + (['-lpcre2-8'] if mode == 'CHECK' else []),
                            capture_output=True, text=True, timeout=600)
        if pr.returncode:
            res['skip'] = '%s build: %s' % (mode, pr.stderr[:400])
            return res
    pr = subprocess.run([os.path.join(d, 'check'), os.path.join(d, 'pat'), '1' if r['icase'] else '0',
                         os.path.join(d, 'asubjects.bin')], capture_output=True, text=True, timeout=1800)
    res['check'] = {}
    for ln in pr.stdout.split('\n'):
        f = ln.split('\t')
        if f[0] == 'acheck':
            res['check'][f[1]] = dict(n=int(f[2]), end_n1=int(f[3]), bad=[int(x) for x in f[4:10]])
    res['wrong'] = sum(sum(v['bad']) for v in res['check'].values())
    return res


def abuild():
    rows = [r for r in bm.read_pop() if MEAS.get(r['k'], {}).get('today_tie')]
    rows = sel(rows)
    with cf.ThreadPoolExecutor(JOBS) as ex:
        out = list(ex.map(lambda r: safe(abuild_one, r), rows))
    json.dump(out, open(os.path.join(RES, 'acheck.json'), 'w'))
    for r in out:
        print(r['k'], r['pat'], r.get('skip', 'wrong=%d' % r.get('wrong', -1)))


def atime():
    res = json.load(open(os.path.join(RES, 'acheck.json')))
    for r in sel(res):
        if 'skip' in r or r['wrong']:
            continue
        d = os.path.join(OUT, 'a%d' % r['k'])
        p = subprocess.run(['taskset', '-c', CPU, os.path.join(d, 'time'), os.path.join(d, 'pat'),
                            '1' if r['icase'] else '0', os.path.join(d, 'asubjects.bin')],
                           capture_output=True, text=True, timeout=3600)
        for ln in p.stdout.split('\n'):
            if ln.startswith('atime\t'):
                print('%d\t%s' % (r['k'], ln[6:]), flush=True)


def e1():
    """E1's census: which of today's form elements each built artifact's T
    walk carries, beside R's run-skip coverage.  Writes results/e1_census.json."""
    res = json.load(open(os.path.join(RES, 'echeck.json')))
    out = []
    for r in res:
        if 'skip' in r:
            continue
        d = os.path.join(OUT, 'e%d' % r['k'])
        t = open(os.path.join(d, 'T.c')).read()
        a = t.index('int T_search(const unsigned char *subject')
        body = t[a:t.index('\n}\n', a)]
        R = open(os.path.join(d, 'R.c')).read()
        out.append(dict(k=r['k'], cls=r['cls'],
                        view_probe='reverse_view_state = T_reverse_view_take' in body,
                        end_view='T_reverse_end_view' in body,
                        stay_top='_reverse_stay' in body,
                        edge='goto T_revend_scan_views' in body,
                        edge_range=bool(re.search(r'\(unsigned\)\(subject\[rewind_position - 1\] - \d+\) <= \d+u', body)),
                        edge_bitmap=bool(re.search(r'T_reverse_scan\d+\[', body)),
                        scan_edge_stamp=bm.stamp(t, 'T', 'DFA_SCAN_EDGE'),
                        uniform_accept='T_reverse_accepts(reverse_view_state)' in body,
                        tie_verify='T_match(&revend_ctx)' in body,
                        r_runs=len(set(re.findall(r'r_run(\d+)\[', R)))))
    json.dump(out, open(os.path.join(RES, 'e1_census.json'), 'w'))
    c = collections.Counter()
    for x in out:
        for f, v in x.items():
            if f not in ('k', 'cls', 'scan_edge_stamp', 'r_runs') and v:
                c[(x['cls'], f)] += 1
        c[(x['cls'], 'R has a run skip')] += x['r_runs'] > 0
        c[(x['cls'], 'T has a run skip (stay or edge)')] += x['stay_top'] or x['edge']
    for k in sorted(c):
        print(k, c[k])


if __name__ == '__main__':
    {'ebuild': ebuild, 'etime': etime, 'abuild': abuild, 'atime': atime, 'e1': e1}[sys.argv[1]]()
