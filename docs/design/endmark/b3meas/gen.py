#!/usr/bin/env python3
"""b3meas (lane b3meas, 2026-10-12): today's SHIPPED rev-end search against a
B3 hand twin, answer-checked, load-counted and timed.  Never run by make.

Population: the 266 rev-end `$`/`\\Z` artifacts (b3cost's rule: tail_probe
neol > 0 and RX_DFA_SCAN == rev-end; bench read-only + corpus), deduplicated by
(pattern, enc, icase), plus five end-anchored idioms.  Per artifact:

  today  `pcrec --features all [-i] -p T` (the shipped artifact; a pattern
         whose shipped engine is the VM because of captures is compiled
         `--no-captures` and flagged `nocap`: its group-0 artifact).
  A      the same command with `-p A` (the A/A control).
  twin   the same artifact with T_search's body REPLACED by B3's one walk:
         the TAGGED reverse machine (the product of pcrec's own minimized
         reverse DFAs for tag0 = X\\z and tag1 = X\\n\\z, probe.c, Moore-
         minimized on the accept pair = the mark distance set), seeded once at
         n, every self-looping state given a run-skip (today's scan-edge
         bitmap, applied to all of them), and at the smallest accepting
         position: one distance -> end = n - d; two (a tie) -> `mark_prio`:
         const c -> end = n - c, otherwise verify-at (today's anchored
         `_match` from s*).  `mark_prio` is classified EMPIRICALLY: the twin is
         first built verify-at, every tie in the check cells records the end
         libpcre2 chose, and a single observed distance makes it const.  The
         static fact can only be weaker, so const rows are B3's best case.
  Excluded from the twin (reported): utf8, a context axis (natoms > 1 /
  clsctx: \\b \\B one-char lookarounds), a position view on a non-seed state.

Checks (harness.c -DCHECK, libpcre2-8 linked): every timed subject, plus every
start position of every subject over a pattern-derived alphabet to length 5.
A twin with ANY wrong answer is not timed.

    PCREC=build/pcrec PROBE=build/scratch/tail_probe B3PROBE=build/scratch/b3meas_probe \\
    BENCH=/home/pcrec/projects/pcrec-bench CORPUS=. OUT=build/scratch/b3meas \\
    python3 -I docs/design/endmark/b3meas/gen.py pop|check|time
"""
import collections, concurrent.futures as cf, importlib.util, json, os, random, re, struct, subprocess, sys

E = os.environ
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.abspath(E['OUT'])
RES = os.path.join(HERE, 'results')
sys.path.insert(0, os.path.join(HERE, '..'))
spec = importlib.util.spec_from_file_location('cost', os.path.join(HERE, '..', 'census', 'cost.py'))
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)
rv = cost.rv
import census as ec                      # docs/design/endmark/census.py
import pcre2                             # docs/design/endmark/pcre2.py
PCREC = os.path.abspath(E['PCREC'])
B3PROBE = os.path.abspath(E['B3PROBE'])
JOBS = int(E.get('JOBS', '6'))
MARK = b'()(?:\\n)?\\z'
CC = ['gcc', '-O2', '-std=gnu11', '-w']

IDIOMS = [rb'\s+$', rb'[ \t]+$', rb'\.(?:txt|log)$', rb'\d+$', rb';\s*$']

# ---------------------------------------------------------------- population

def pop():
    os.makedirs(OUT, exist_ok=True)
    rows = rv.bench_pop() + rv.corpus_pop()
    pr = ec.probe(rows)
    cand = [i for i in range(len(rows)) if pr.get(i, {}).get('status') == 'ok' and ec.num(pr[i], 'neol') > 0]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        fx = dict(zip(cand, ex.map(lambda i: ec.facts(rows[i]), cand)))
    revend = [i for i in cand if fx[i].get('DFA_SCAN') == 'rev-end']
    seen = collections.OrderedDict()
    for i in revend:
        r = rows[i]
        k = (r['pat'], r['enc'], r['icase'])
        if k not in seen:
            seen[k] = dict(pops=set(), ids=[], pat=r['pat'], enc=r['enc'], icase=r['icase'])
        seen[k]['pops'].add(r['pop'])
        seen[k]['ids'].append(r['id'])
    for p in IDIOMS:
        k = (p, 'byte', False)
        if k not in seen:
            seen[k] = dict(pops=set(), ids=[], pat=p, enc='byte', icase=False)
        seen[k]['pops'].add('idiom')
    with open(os.path.join(RES, 'population.tsv'), 'w') as f:
        f.write('# b3meas population: %d rev-end rows (%d bench, %d corpus) -> %d distinct (pattern,enc,icase) + idioms\n'
                % (len(revend), sum(rows[i]['pop'] == 'bench' for i in revend),
                   sum(rows[i]['pop'] == 'corpus' for i in revend), len(seen)))
        f.write('k\tpops\tnrows\tenc\ticase\tpattern_hex\tfirst_id\n')
        for k, (key, v) in enumerate(seen.items()):
            f.write('%d\t%s\t%d\t%s\t%d\t%s\t%s\n' % (k, ','.join(sorted(v['pops'])), len(v['ids']), v['enc'],
                                                    int(v['icase']), v['pat'].hex(), v['ids'][0] if v['ids'] else '-'))


def read_pop():
    out = []
    for ln in open(os.path.join(RES, 'population.tsv')):
        if ln.startswith('#') or ln.startswith('k\t'):
            continue
        f = ln.rstrip('\n').split('\t')
        out.append(dict(k=int(f[0]), pops=f[1], nrows=int(f[2]), enc=f[3], icase=f[4] == '1',
                        pat=bytes.fromhex(f[5]), id=f[6]))
    return out

# ---------------------------------------------------------------- compile today

def pcrec(pat, icase, prefix, path, nocap):
    cmd = [PCREC, '--features', 'all', '-p', prefix, '-o', path]
    if icase: cmd.append('-i')
    if nocap: cmd.append('--no-captures')
    cmd += ['--pattern', pat]
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    if p.returncode:
        return None
    return open(path).read()


def stamp(txt, prefix, name):
    m = re.search(r'#define %s_%s "([^"]*)"' % (prefix, name), txt)
    return m.group(1) if m else None


def search_span(txt, prefix):
    """(start, end) of `int P_search(...) { ... }` in txt (to the first column-0 `}`)."""
    a = txt.index('int %s_search(const unsigned char *subject' % prefix)
    b = txt.index('\n}\n', a) + 3
    return a, b

# ---------------------------------------------------------------- machines

def probe_machines(rowsin):
    inp = ''.join('%s\tbyte\t%s\t%s\n' % (rid, t0.hex(), t1.hex()) for rid, t0, t1 in rowsin)
    res = subprocess.run([B3PROBE], input=inp.encode(), capture_output=True, timeout=3600)
    out, cur, m = {}, None, None
    for ln in res.stdout.decode().split('\n'):
        f = ln.split()
        if not f:
            continue
        if f[0] == 'ROW':
            cur = f[1]
            out[cur] = None if f[2] != 'ok' else []
        elif f[0] == 'M':
            m = dict(n=int(f[2]), ncls=int(f[3]), natoms=int(f[4]), clsctx=int(f[5]), s0=int(f[6]))
            out[cur].append(m)
        else:
            m[f[0]] = [int(x) for x in f[1:]]
    return out


def view(m, s):
    e = m['END'][s]
    if e >= 0:
        return e
    return m['EOL'][s] if m['EOL'][s] >= 0 else s


def product(A, B):
    """The tagged machine: reachable pairs from the seed (views of s0 taken, the
    walk starts at n), Moore-minimized on (acc0, acc1).  Returns the machine or
    an exclusion reason."""
    for m in (A, B):
        if m['natoms'] > 1 or m['clsctx']:
            return 'ctx'
        for s in range(m['n']):
            if s != m['s0'] and (m['EOL'][s] >= 0 or m['END'][s] >= 0):
                return 'interior-view'
    jc, jmap = {}, []
    for b in range(256):
        jmap.append(jc.setdefault((A['CLS'][b], B['CLS'][b]), len(jc)))
    cls = list(jc.keys())
    C = len(cls)
    seed = (view(A, A['s0']), view(B, B['s0']))
    idx, st = {seed: 0}, [seed]
    tr = []
    i = 0
    while i < len(st):
        a, b = st[i]
        row = []
        for ca, cb in cls:
            x = A['TR'][a * A['ncls'] + ca] if a >= 0 else -1
            y = B['TR'][b * B['ncls'] + cb] if b >= 0 else -1
            if x < 0 and y < 0:
                row.append(-1)
                continue
            if (x, y) not in idx:
                idx[(x, y)] = len(st)
                st.append((x, y))
            row.append(idx[(x, y)])
        tr.append(row)
        i += 1
    n = len(st)
    acc = [(A['ACC'][a] if a >= 0 else 0) | ((B['ACC'][b] if b >= 0 else 0) << 1) for a, b in st]
    # Moore: dead sink is index n
    part = acc + [0]
    sink = n
    while True:
        sig = {}
        newp = []
        for q in range(n + 1):
            row = tr[q] if q < n else [-1] * C
            key = (part[q],) + tuple(part[sink if t < 0 else t] for t in row)
            newp.append(sig.setdefault(key, len(sig)))
        if len(sig) == len(set(part)):
            part = newp
            break
        part = newp
    dead_blk = part[sink]
    blocks = sorted(set(part[q] for q in range(n)) - {dead_blk}, key=lambda b: min(q for q in range(n) if part[q] == b))
    bid = {b: k for k, b in enumerate(blocks)}
    rep = {b: min(q for q in range(n) if part[q] == b) for b in blocks}
    S = len(blocks)
    mtr = [[(-1 if (t < 0 or part[t] == dead_blk) else bid[part[t]]) for t in tr[rep[b]]] for b in blocks]
    macc = [acc[rep[b]] for b in blocks]
    if part[0] == dead_blk:
        return 'dead-seed'
    # merge identical columns
    cols = {}
    colmap = []
    for c in range(C):
        key = tuple(mtr[s][c] for s in range(S))
        colmap.append(cols.setdefault(key, len(cols)))
    C2 = len(cols)
    ntr = [[None] * C2 for _ in range(S)]
    for c in range(C):
        for s in range(S):
            ntr[s][colmap[c]] = mtr[s][c]
    bytecls = [colmap[jmap[b]] for b in range(256)]
    # X unbounded <=> the tagged reverse machine has a cycle among live states
    color, cyclic = [0] * S, False
    def dfs(u):
        nonlocal cyclic
        color[u] = 1
        for t in ntr[u]:
            if t < 0 or cyclic:
                continue
            if color[t] == 1:
                cyclic = True
            elif color[t] == 0:
                dfs(t)
        color[u] = 2
    dfs(bid[part[0]])
    return dict(S=S, C=C2, seed=bid[part[0]], tr=ntr, acc=macc, bytecls=bytecls,
                ties=any(a == 3 for a in macc), reach=n, cyclic=cyclic)

# ---------------------------------------------------------------- the twin's C

def twin_body(M, prefix, prio):
    """B3's search body over the tagged machine M; prio = 'none'|'const0'|'const1'|'verify'."""
    S, C = M['S'], M['C']
    runs = []
    for s in range(S):
        loop = [b for b in range(256) if M['tr'][s][M['bytecls'][b]] == s]
        if loop:
            runs.append((s, loop))
    order = [s for s in range(S) if s not in dict(runs)] + [s for s, _ in runs]
    num = {s: k for k, s in enumerate(order)}
    stop = (S - len(runs)) * C
    def pm(t):
        return 65535 if t < 0 else num[t] * C
    nxt = [0] * (S * C)
    accp = [0] * (S * C)
    for s in range(S):
        for c in range(C):
            nxt[num[s] * C + c] = pm(M['tr'][s][c])
            accp[num[s] * C + c] = M['acc'][s]
    def arr(ty, name, vals):
        rows = ['        ' + ', '.join(str(v) for v in vals[i:i + 16]) + ',' for i in range(0, len(vals), 16)]
        return '    static const %s %s[%d] = {\n%s\n    };\n' % (ty, name, len(vals), '\n'.join(rows))
    o = ['int %s_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n' % prefix,
         '    if (search_from > subject_length) return 0;\n',
         arr('unsigned char', 'b3_cls', M['bytecls']),
         arr('unsigned short', 'b3_next', nxt),
         arr('unsigned char', 'b3_acc', accp)]
    tabs = {}                               # identical run bitmaps share one table
    for s, loop in runs:
        key = tuple(loop)
        if key not in tabs:
            tabs[key] = num[s]
            o.append(arr('unsigned char', 'b3_run%d' % num[s], [1 if b in loop else 0 for b in range(256)]))
    o.append('    // ---- B3: ONE reverse walk from n over the tagged machine; b3_acc = the\n'
             '    // mark distance set (bit 0: X ends at n, bit 1: X ends at n-1 before a final newline).\n'
             '    size_t pos = subject_length, best = (size_t)-1;\n'
             '    unsigned st = %d, bacc = 0;\n' % pm(M['seed']) +
             '    for (;;) {\n'
             '        unsigned a = b3_acc[st];\n'
             '        if (a) { best = pos; bacc = a; }\n'
             '        if (pos <= search_from) break;\n'
             '        st = b3_next[st + b3_cls[subject[--pos]]];\n'
             '        if (st < %du) continue;\n' % stop +
             '        if (st == 65535) break;\n')
    for s, loop in runs:
        o.append('        if (st == %du) { while (pos > search_from && b3_run%d[subject[pos - 1]]) pos--; continue; }\n'
                 % (num[s] * C, tabs[tuple(loop)]))
    o.append('    }\n'
             '    if (best == (size_t)-1) return 0;\n'
             '    size_t end = (bacc & 1) ? subject_length : subject_length - 1;\n')
    if M['ties']:
        o.append('    if (bacc == 3) {\n#ifdef B3_CHECK\n        { extern int b3tw_tie; b3tw_tie = 1; }\n#endif\n')
        if prio == 'const0':
            o.append('        end = subject_length;\n')
        elif prio == 'const1':
            o.append('        end = subject_length - 1;\n')
        else:
            o.append('        rx_ctx b3_ctx = { .subject = subject, .len = subject_length, .pos = best };\n'
                     '        ptrdiff_t b3_len = %s_match(&b3_ctx);\n' % prefix +
                     '        if (b3_len < 0) return (int)b3_len;\n'
                     '        end = best + (size_t)b3_len;\n')
        o.append('    }\n')
    o.append('    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)best; capture_spans[0][1] = (ptrdiff_t)end; }\n'
             '    return 1;\n}\n')
    return ''.join(o), dict(S=S, C=C, runs=len(runs), cyclic=M['cyclic'],
                            bytes=256 + 2 * S * C + S * C + 256 * len(tabs))


def restyle_body(M, prefix):
    """The CONTROL R: today's algorithm (seed n, then seed n-1 before a final
    newline, over today's own minimized reverse machine X$ with its end/eol views,
    a tie decided by one verify-at run) in twin_body's code style (same table
    layout, same run-skip on every self-loop state)."""
    if M['natoms'] > 1 or M['clsctx']:
        return None
    S, C = M['n'], M['ncls']
    tr = [[M['TR'][q * C + c] for c in range(C)] for q in range(S)]
    runs = []
    for q in range(S):
        loop = [b for b in range(256) if tr[q][M['CLS'][b]] == q]
        if loop:
            runs.append((q, loop))
    rs = dict(runs)
    order = [q for q in range(S) if q not in rs] + [q for q, _ in runs]
    num = {q: k for k, q in enumerate(order)}
    stop = (S - len(runs)) * C
    def pm(t):
        return 65535 if t < 0 else num[t] * C
    nxt, accp, eolv = [0] * (S * C), [0] * (S * C), [65535] * S
    for q in range(S):
        for c in range(C):
            nxt[num[q] * C + c] = pm(tr[q][c])
            accp[num[q] * C + c] = M['ACC'][q]
        if M['EOL'][q] >= 0:
            eolv[num[q]] = pm(M['EOL'][q])
    s0 = M['s0']
    seed_n = view(M, s0)
    seed_n1 = M['EOL'][s0] if M['EOL'][s0] >= 0 else s0
    def arr(ty, name, vals):
        rows = ['        ' + ', '.join(str(v) for v in vals[i:i + 16]) + ',' for i in range(0, len(vals), 16)]
        return '    static const %s %s[%d] = {\n%s\n    };\n' % (ty, name, len(vals), '\n'.join(rows))
    o = ['int %s_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n' % prefix,
         '    if (search_from > subject_length) return 0;\n',
         arr('unsigned char', 'r_cls', M['CLS']), arr('unsigned short', 'r_next', nxt),
         arr('unsigned char', 'r_acc', accp), arr('unsigned short', 'r_eolv', eolv)]
    tabs = {}
    for q, loop in runs:
        if tuple(loop) not in tabs:
            tabs[tuple(loop)] = num[q]
            o.append(arr('unsigned char', 'r_run%d' % num[q], [1 if b in loop else 0 for b in range(256)]))
    o.append('    size_t best = (size_t)-1, bend = 0;\n    int tie = 0;\n'
             '    for (int seed = 0; seed < 2; seed++) {\n'
             '        size_t pos = subject_length, mstart = (size_t)-1;\n'
             '        unsigned st = %du;\n' % pm(seed_n) +
             '        if (seed == 1) {\n'
             '            if (subject_length == 0 || subject[subject_length - 1] != \'\\n\') break;\n'
             '            pos = subject_length - 1;\n'
             '            st = %du;\n' % pm(seed_n1) +
             '        }\n'
             '        if (pos < search_from) break;\n'
             '        if (seed == 0) {   /* the one step that can land on the eol view at n-1 */\n'
             '            if (r_acc[st]) mstart = pos;\n'
             '            if (pos <= search_from) goto seed_done;\n'
             '            st = r_next[st + r_cls[subject[--pos]]];\n'
             '            if (st == 65535) goto seed_done;\n'
             '            if (subject[pos] == \'\\n\' && r_eolv[st / %du] != 65535) st = r_eolv[st / %du];\n' % (C, C) +
             '        }\n'
             '        for (;;) {\n'
             '            if (r_acc[st]) mstart = pos;\n'
             '            if (pos <= search_from) break;\n'
             '            st = r_next[st + r_cls[subject[--pos]]];\n'
             '            if (st < %du) continue;\n' % stop +
             '            if (st == 65535) break;\n')
    for q, loop in runs:
        o.append('            if (st == %du) { while (pos > search_from && r_run%d[subject[pos - 1]]) pos--; continue; }\n'
                 % (num[q] * C, tabs[tuple(loop)]))
    o.append('        }\n'
             '      seed_done:\n'
             '        if (mstart == (size_t)-1) continue;\n'
             '        if (mstart < best) { best = mstart; bend = seed ? subject_length - 1 : subject_length; tie = 0; }\n'
             '        else if (mstart == best) tie = 1;\n'
             '    }\n'
             '    if (best == (size_t)-1) return 0;\n'
             '    if (tie) {\n'
             '        rx_ctx r_ctx = { .subject = subject, .len = subject_length, .pos = best };\n'
             '        ptrdiff_t r_len = %s_match(&r_ctx);\n' % prefix +
             '        if (r_len < 0) return (int)r_len;\n'
             '        bend = best + (size_t)r_len;\n'
             '    }\n'
             '    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)best; capture_spans[0][1] = (ptrdiff_t)bend; }\n'
             '    return 1;\n}\n')
    return ''.join(o)


def today_rev_bytes(txt, prefix):
    a, b = search_span(txt, prefix)
    body = txt[a:b]
    tot = 0
    for m in re.finditer(r'static const (unsigned (?:char|short|int)) (\w+)\[(\d+)\]', body):
        if 'reverse' in m.group(2):
            tot += int(m.group(3)) * {'unsigned char': 1, 'unsigned short': 2, 'unsigned int': 4}[m.group(1)]
    return tot


def instrument(txt):
    """every `subject[...]` read -> `(b3_loads++, subject[...])` (balanced brackets)."""
    out, i = [], 0
    pat = re.compile(r'(?<![\w.>])subject\[')
    while True:
        m = pat.search(txt, i)
        if not m:
            out.append(txt[i:])
            break
        out.append(txt[i:m.start()])
        j, depth = m.end(), 1
        while depth:
            depth += {'[': 1, ']': -1}.get(txt[j], 0)
            j += 1
        out.append('(b3_loads++, ' + txt[m.start():j] + ')')
        i = j
    return 'extern unsigned long b3_loads;\n' + ''.join(out)

# ---------------------------------------------------------------- subjects

TAILS = ['', ' ', '   ', ' \t', '\t', ' 12345', '1024', ' file.txt', ' /var/log/app.log', ' notes.TXT',
         ';', ';  ', 'x;', ' done', 'abc', ' xabc', 'a', ' c', 'ccc', '/usr/bin/', ' =', ' 3.14', ' ERROR',
         ' DONE', '--']
WORDS = ['user', 'id', 'GET', '/index.html', 'status=200', 'took', 'ms', 'host', 'ok', 'retry', 'conn',
         'from', '10.0.0.7', 'path', 'key=value', '[INFO]', '12:34:56', 'size', 'bytes', 'warn', 'cache',
         'miss', 'job', 'queue', 'level', 'trace', 'x86_64', 'v2.3.1', 'done.', 'error:', 'a', 'cc']


def body(rng, n):
    w = []
    while sum(len(x) + 1 for x in w) < n:
        w.append(rng.choice(WORDS))
    return ' '.join(w)[:n].rstrip(' \t') or 'x'


def subjects(code, rng):
    """{regime: [subject bytes]}; regimes L (40-200 B lines), K4 (4 KiB), M1 (1 MiB),
    each with/without a final newline, each matching (m) / not (n) by libpcre2."""
    out = collections.OrderedDict()
    def put(name, s, want):
        lst = out.setdefault(name, [])
        if len(lst) < want:
            lst.append(s)
    def cls(s):
        return 'm' if code.match(s, 0) else 'n'
    tails = TAILS[:]
    for rnd in range(6):
        rng.shuffle(tails)
        for t in tails:
            ln = (body(rng, rng.randint(40, 200) - len(t)) + t).encode()
            for nl in (b'\n', b''):
                s = ln + nl
                put('L-%s-%s' % ('nl' if nl else 'nonl', cls(s)), s, 24)
    for big, want, nm in ((4096, 6, 'K4'), (1 << 20, 2, 'M1')):
        lines = []                          # one base text per size; the last line varies
        tot = 0
        while tot < big - 220:
            l = body(rng, rng.randint(40, 200))
            lines.append(l)
            tot += len(l) + 1
        base = ('\n'.join(lines) + '\n').encode()
        for t in TAILS:
            blob = base + (body(rng, 60) + t).encode()
            for nl in (b'\n', b''):
                s = blob + nl
                put('%s-%s-%s' % (nm, 'nl' if nl else 'nonl', cls(s)), s, want)
    order = ['%s-%s-%s' % (a, b, c) for a in ('L', 'K4', 'M1') for b in ('nl', 'nonl') for c in ('m', 'n')]
    return collections.OrderedDict((k, out[k]) for k in order if k in out)


def write_subjects(path, subs):
    with open(path, 'wb') as f:
        for name, lst in subs.items():
            for s in lst:
                f.write(name.encode() + b'\0' + struct.pack('<I', len(s)) + s)


def alphabet(pat):
    al = set(b'a \n.c1;x/')
    for ch in re.findall(rb'[A-Za-z0-9]', pat.replace(b'\\s', b'').replace(b'\\d', b'').replace(b'\\w', b'')
                         .replace(b'\\W', b'').replace(b'\\n', b'').replace(b'\\z', b'').replace(b'\\Z', b'')
                         .replace(b'\\B', b'').replace(b'\\b', b''))[:4]:
        al.add(ch[0])
    al.add(ord('\t'))
    return bytes(sorted(al))[:10]

# ---------------------------------------------------------------- per artifact

def build_check(d, files, defs):
    exe = os.path.join(d, 'check')
    p = subprocess.run(CC + ['-DCHECK', '-DB3_CHECK'] + defs + ['-o', exe, os.path.join(HERE, 'harness.c')] + files +
                       ['-lpcre2-8'], capture_output=True, text=True, timeout=300)
    if p.returncode:
        raise RuntimeError(p.stderr[:2000])
    return exe


def run_check(exe, d, r, subf, al):
    p = subprocess.run([exe, os.path.join(d, 'pat'), '1' if r['icase'] else '0', subf, al.decode('latin1'), '5'],
                       capture_output=True, text=True, timeout=1800)
    if p.returncode:
        raise RuntimeError('check rc=%d %s' % (p.returncode, p.stderr[:500]))
    return p.stdout


def parse_check(txt):
    regs, ties, wrong, exh = {}, None, None, None
    for ln in txt.split('\n'):
        f = ln.split('\t')
        if f[0] == 'check':
            regs[f[1]] = dict(n=int(f[2]), nm=int(f[3]), tw=int(f[4]), bw=int(f[5]), tl=float(f[6]), bl=float(f[7]),
                              ties=int(f[8]), rw=int(f[9]), rl=float(f[10]))
        elif f[0] == 'ties':
            ties = tuple(int(x) for x in f[1:])
        elif f[0] == 'wrong':
            wrong = tuple(int(x) for x in f[1:])
        elif f[0] == 'exhaustive':
            exh = tuple(int(x) for x in f[1:])
    return regs, ties, wrong, exh


def artifact(r, machines, tmach):
    d = os.path.join(OUT, 'a%d' % r['k'])
    os.makedirs(d, exist_ok=True)
    res = dict(k=r['k'], pops=r['pops'], nrows=r['nrows'], pat=r['pat'].decode('latin1'), enc=r['enc'],
               icase=r['icase'])
    if r['enc'] != 'byte':
        res['skip'] = 'utf8'
        return res
    nocap = False
    T = pcrec(r['pat'], r['icase'], 'T', os.path.join(d, 'T.c'), False)
    if T is None or stamp(T, 'T', 'ENGINE') != 'dfa':
        nocap = True
        T = pcrec(r['pat'], r['icase'], 'T', os.path.join(d, 'T.c'), True)
    if T is None or stamp(T, 'T', 'ENGINE') != 'dfa' or stamp(T, 'T', 'DFA_SCAN') != 'rev-end':
        res['skip'] = 'not-revend-dfa'
        return res
    res['nocap'] = nocap
    res['today_tie'] = 'revend_tie' in T
    res['today_relocate'] = 'search_from = revend_start' in T
    res['today_rev_bytes'] = today_rev_bytes(T, 'T')
    res['today_rev_states'] = None
    m = re.search(r'rx_reverse_is_accepting\[(\d+)\]', T)
    A = pcrec(r['pat'], r['icase'], 'A', os.path.join(d, 'A.c'), nocap)
    Bbase = pcrec(r['pat'], r['icase'], 'B', os.path.join(d, 'Bbase.c'), nocap)
    mach = machines.get(str(r['k']))
    if not mach:
        res['skip'] = 'probe-failed'
        return res
    M = product(mach[0], mach[1])
    if isinstance(M, str):
        res['skip'] = M
        return res
    res['twin_ties'] = M['ties']
    with open(os.path.join(d, 'pat'), 'wb') as f:
        f.write(r['pat'])
    code = pcre2.Code(r['pat'], extra=0x00000008 if r['icase'] else 0)
    subs = subjects(code, random.Random(r['k'] * 7919 + 1))
    subf = os.path.join(d, 'subjects.bin')
    write_subjects(subf, subs)
    al = alphabet(r['pat'])

    tm = tmach.get(str(r['k']))
    Rbody = restyle_body(tm[0], 'R') if tm else None
    if Rbody is None:
        res['skip'] = 'restyle-unbuilt'
        return res
    Rbase = pcrec(r['pat'], r['icase'], 'R', os.path.join(d, 'Rbase.c'), nocap)
    a_, b_ = search_span(Rbase, 'R')
    Rtxt = Rbase[:a_] + Rbody + Rbase[b_:]
    open(os.path.join(d, 'R.c'), 'w').write(Rtxt)
    open(os.path.join(d, 'RI.c'), 'w').write(instrument(Rtxt))

    def make_twin(prio):
        body, info = twin_body(M, 'B', prio)
        a, b = search_span(Bbase, 'B')
        return Bbase[:a] + body + Bbase[b:], info

    prio = 'none' if not M['ties'] else 'verify'
    Btxt, info = make_twin(prio)
    open(os.path.join(d, 'TI.c'), 'w').write(instrument(T))
    open(os.path.join(d, 'BI.c'), 'w').write(instrument(Btxt))
    exe = build_check(d, [os.path.join(d, 'TI.c'), os.path.join(d, 'BI.c'), os.path.join(d, 'RI.c')], [])
    regs, ties, wrong, exh = parse_check(run_check(exe, d, r, subf, al))
    if M['ties']:
        if ties[0] and not ties[1] and not ties[2]:
            prio = 'const0'
        elif ties[1] and not ties[0] and not ties[2]:
            prio = 'const1'
        elif ties[0] or ties[1] or ties[2]:
            prio = 'state-dependent'
        else:
            prio = 'unobserved'
        if prio in ('const0', 'const1'):
            Btxt, info = make_twin(prio)
            open(os.path.join(d, 'BI.c'), 'w').write(instrument(Btxt))
            exe = build_check(d, [os.path.join(d, 'TI.c'), os.path.join(d, 'BI.c'), os.path.join(d, 'RI.c')], [])
            regs, ties2, wrong, exh = parse_check(run_check(exe, d, r, subf, al))
    res.update(prio=prio, ties_obs=ties, wrong=wrong, exh=exh, regs=regs, twin=info, alphabet=al.decode('latin1'))
    open(os.path.join(d, 'B.c'), 'w').write(Btxt)
    # object sizes of the search functions (measured): today vs twin, -O2
    for nm, src in (('T', os.path.join(d, 'T.c')), ('B', os.path.join(d, 'B.c')), ('R', os.path.join(d, 'R.c'))):
        o = os.path.join(d, nm + '.o')
        subprocess.run(CC + ['-c', '-o', o, src], check=True, timeout=300)
        sz = subprocess.run(['nm', '-S', '--size-sort', o], capture_output=True, text=True).stdout
        fn = [ln.split() for ln in sz.split('\n') if ln.endswith(' %s_search' % nm)]
        res['%s_search_text' % nm] = int(fn[0][1], 16) if fn else None
        res['%s_obj' % nm] = sum(int(x) for x in subprocess.run(['size', o], capture_output=True, text=True)
                                 .stdout.split('\n')[1].split()[:2])
    return res


def check():
    rows = read_pop()
    if E.get('ONLY'):
        rows = [r for r in rows if str(r['k']) in E['ONLY'].split(',')]
    vin = []
    for r in rows:
        new, cnt = cost.rewrite(r['pat'])
        if not cnt or new is None or new.count(MARK) != cnt:
            continue
        pre = b'(?i)' if r['icase'] else b''
        vin.append((str(r['k']), pre + new.replace(MARK, b'\\z'), pre + new.replace(MARK, b'\\n\\z')))
    machines = probe_machines(vin)
    tmach = probe_machines([(str(r['k']), (b'(?i)' if r['icase'] else b'') + r['pat'],
                             (b'(?i)' if r['icase'] else b'') + r['pat']) for r in rows])
    with cf.ThreadPoolExecutor(JOBS) as ex:
        out = list(ex.map(lambda r: safe(r, machines, tmach), rows))
    with open(os.path.join(OUT, E.get('CHECKOUT', 'check.json')), 'w') as f:
        json.dump(out, f)


def safe(r, machines, tmach):
    try:
        return artifact(r, machines, tmach)
    except Exception as e:     # recorded, never silently dropped
        return dict(k=r['k'], pat=r['pat'].decode('latin1'), skip='error: %s' % str(e)[:300])


def time_():
    res = []
    for fn in sorted(os.listdir(OUT)):
        if fn.startswith('check') and fn.endswith('.json'):
            res += json.load(open(os.path.join(OUT, fn)))
    sel = E.get('SELECT')
    for r in res:
        if 'skip' in r or list(r['wrong']) != [0, 0]:      # a twin that disagrees is not timed
            continue
        timed = 'bench' in r['pops'] or 'idiom' in r['pops'] or 'synthetic' in r['pops'] or r.get('today_tie')
        if sel and str(r['k']) not in sel.split(','):
            continue
        if not timed:
            continue
        d = os.path.join(OUT, 'a%d' % r['k'])
        exe = os.path.join(d, 'time')
        subprocess.run(CC + ['-DTIME', '-o', exe, os.path.join(HERE, 'harness.c'), os.path.join(d, 'T.c'),
                             os.path.join(d, 'A.c'), os.path.join(d, 'B.c'), os.path.join(d, 'R.c')],
                       check=True, timeout=300)
        p = subprocess.run(['taskset', '-c', E.get('CPU', '7'), exe, os.path.join(d, 'pat'),
                            '1' if r['icase'] else '0', os.path.join(d, 'subjects.bin')],
                           capture_output=True, text=True, timeout=3600)
        for ln in p.stdout.split('\n'):
            if ln.startswith('time\t'):
                print('%d\t%s' % (r['k'], ln[5:]), flush=True)


def states():
    """today's reverse machine size (pcrec's minimized X$ DFA, pre-scan-edge) per
    artifact, beside the tagged twin's, for the cost side."""
    rows = read_pop()
    tm = probe_machines([(str(r['k']), (b'(?i)' if r['icase'] else b'') + r['pat'],
                          (b'(?i)' if r['icase'] else b'') + r['pat']) for r in rows if r['enc'] == 'byte'])
    out = {k: dict(n=v[0]['n'], ncls=v[0]['ncls']) for k, v in tm.items() if v}
    with open(os.path.join(OUT, 'states.json'), 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    {'pop': pop, 'check': check, 'time': time_, 'states': states}[sys.argv[1]]()
