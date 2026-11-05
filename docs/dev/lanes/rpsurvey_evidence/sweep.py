#!/usr/bin/env python3
"""[RUN-POS-SET] survey sweep. usage: sweep.py WORKTREE BENCH_ROOT OUT.tsv
Population: tests/**/*.rxt pattern rows (via `pcrec --list-source`, the
emit_sweep.py enumerator's method) + pcrec-bench bench/*/patterns/*.rx.
Each (pattern, flags) is compiled with --emit-facts under -e utf8 and -e byte;
patterns with a caseless scope and a literal k/s also get a TWIN with k->q,
s->t (outside escapes/classes/groups) under -e utf8."""
import os, sys, re, subprocess, glob
W, B, OUT = sys.argv[1:4]
P = os.path.join(W, 'build', 'pcrec')


def dec(s):
    b = s.encode('utf-8', 'surrogateescape'); o = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i+1]
            m = {ord('t'): 9, ord('n'): 10, ord('r'): 13, 0x5C: 0x5C}
            if n in m: o.append(m[n]); i += 2; continue
            if n == ord('x') and i + 3 < len(b):
                try: o.append(int(bytes(b[i+2:i+4]), 16)); i += 4; continue
                except ValueError: pass
        o.append(c); i += 1
    return bytes(o)


pops = []  # (source, id, pattern bytes, flags)
for f in sorted(glob.glob(os.path.join(W, 'tests', '**', '*.rxt'), recursive=True)):
    r = subprocess.run([P, '--list-source', f], capture_output=True)
    for ln in r.stdout.decode('utf-8', 'surrogateescape').splitlines():
        if ln.startswith('#') or not ln.strip(): continue
        x = ln.split('\t')
        if len(x) < 9 or x[0] not in ('pattern', 'pattern-esc'): continue
        pops.append(('corpus', os.path.relpath(f, W) + ':' + x[1], dec(x[4]), x[5]))
for f in sorted(glob.glob(os.path.join(B, 'bench', '*', 'patterns', '*.rx'))):
    sub = f.split('/')[-3]
    pops.append(('bench:' + sub, sub + '/' + os.path.basename(f)[:-3], open(f, 'rb').read(), ''))
seen = set(); uniq = []
for p in pops:
    if p[0] == 'corpus':
        if (p[2], p[3]) in seen: continue
        seen.add((p[2], p[3]))
    uniq.append(p)
print('population', len(pops), 'unique', len(uniq), file=sys.stderr)


def facts(pat, enc, flags):
    if b'\0' in pat: return None
    argv = [P.encode(), b'-e', enc.encode(), b'--features', b'all', b'--emit-facts']
    if 'i' in flags: argv.append(b'-i')
    if 'u' in flags: argv.append(b'--ucp')
    argv += [b'--pattern', pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0: return None
    d = {}
    for ln in r.stdout.decode('utf-8', 'replace').splitlines():
        t = ln.split('\t')
        if len(t) >= 7 and t[0] == enc and t[2] == 'pattern':
            d[t[1]] = t[6]
        elif len(t) == 3 and t[0] == enc:
            d[t[1]] = t[2].strip('"')
    return d


def runlen(v):
    if not v or v == 'none': return 0
    return len(v.split('@')[0].split('/')[0]) // 2


def summarize(d):
    if d is None: return ('ERR',) * 6
    return (str(runlen(d.get('req_whole_run'))), str(runlen(d.get('req_run'))),
            d.get('RX_ENGINE', ''), d.get('RX_DFA_SCAN', ''),
            d.get('RX_DFA_PREFILTER', ''), d.get('RX_REQ_HANDOFF', ''))


def caseless(p, flags):
    s = p.decode('utf-8', 'replace')
    return 'i' in flags or re.search(r'\(\?[a-zA-Z]*i', s) is not None


def twin(p):
    """k->q, s->t, K->Q, S->T outside escapes, [..] classes, (?..) heads, {..}."""
    s = p.decode('utf-8', 'surrogateescape'); o = []; i = 0; changed = False
    m = {'k': 'q', 'K': 'Q', 's': 't', 'S': 'T'}
    while i < len(s):
        c = s[i]
        if c == '\\': o.append(s[i:i+2]); i += 2; continue
        if c == '[':
            j = i + 1
            if j < len(s) and s[j] == '^': j += 1
            if j < len(s) and s[j] == ']': j += 1
            while j < len(s) and s[j] != ']':
                j += 2 if s[j] == '\\' else 1
            o.append(s[i:j+1]); i = j + 1; continue
        if c == '(' and s[i:i+2] == '(?':
            j = i + 2
            while j < len(s) and s[j] not in ':)': j += 1
            o.append(s[i:j]); i = j; continue
        if c == '{':
            j = s.find('}', i); j = len(s) - 1 if j < 0 else j
            o.append(s[i:j+1]); i = j + 1; continue
        if c in m: o.append(m[c]); changed = True
        else: o.append(c)
        i += 1
    return ''.join(o).encode('utf-8', 'surrogateescape') if changed else None


hdr = ['source', 'id', 'flags', 'caseless', 'pattern', 'wr_byte', 'run_byte', 'wr_utf8',
       'run_utf8', 'eng_utf8', 'scan_utf8', 'pf_utf8', 'hand_utf8', 'twin_wr_utf8',
       'twin_run_utf8', 'twin_eng', 'twin_scan', 'twin_pf', 'twin_hand']
with open(OUT, 'w') as fo:
    fo.write('\t'.join(hdr) + '\n')
    for src, id_, pat, flags in uniq:
        cl = caseless(pat, flags)
        b = summarize(facts(pat, 'byte', flags)); u = summarize(facts(pat, 'utf8', flags))
        t = ('',) * 6
        if cl:
            tp = twin(pat)
            if tp is not None: t = summarize(facts(tp, 'utf8', flags))
        esc = pat.decode('utf-8', 'replace').replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
        fo.write('\t'.join([src, id_, flags, '1' if cl else '0', esc, b[0], b[1], u[0], u[1], u[2], u[3], u[4], u[5], t[0], t[1], t[2], t[3], t[4], t[5]]) + '\n')
