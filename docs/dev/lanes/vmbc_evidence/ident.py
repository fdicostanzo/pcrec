"""ident.py K : answer identity of the B/C/BC twins against stock for pattern K (cscan|json).
Every subject: the default arm, and the _in arm at NF=200000 with trail caps
8..huge. A twin cell must equal stock's cell, except where stock gives up
(rc=-3) at that cap: then a twin answer must equal stock's huge-buffer answer."""
import os, re, subprocess, sys, random
V = '/var/tmp/pcrec-pcrec/scratch/vmbc'
K = sys.argv[1]
B = '/home/pcrec/projects/pcrec-bench/bench/unusual/throughput'
def dec(s):
    out = bytearray(); i = 0
    m = {'"': 34, '\\': 92, 'n': 10, 't': 9, 'r': 13, 'f': 12, 'v': 11, '0': 0, 'e': 27, 'a': 7}
    while i < len(s):
        c = s[i]
        if c == '\\':
            d = s[i+1]
            if d == 'x': out.append(int(s[i+2:i+4], 16)); i += 4; continue
            out.append(m[d]); i += 2; continue
        out += c.encode('latin-1'); i += 1
    return bytes(out)
subs = []
if K == 'cscan':
    txt = subprocess.run(['git', '-C', '/home/pcrec/projects/pcrec', 'show', 'lane/trailgc:tests/recursion/cscan.rxt'], capture_output=True).stdout.decode('latin-1')
    for l in txt.split('\n'):
        mm = re.match(r'^(m|n|ms|g) "((?:[^"\\]|\\.)*)"', l)
        if mm: subs.append(dec(mm.group(2)))
    subs += [b"(?{ " + b"abc_1 " * k + b"})" for k in (1, 10, 100)]
    subs += [b"(?{ " + b"{" * k + b"x" + b"}" * k + b" })" for k in (1, 5, 20, 60)]
    subs += [b"(?{ " + b"/* c */ 'a' \"s\\\"\" 1'0 \\\n x" * k + b" })" for k in (1, 50)]
    subs += [b"(?{ " + b"{ a<%b%>c\\\n{'x'}" * k + b" })" for k in (1, 7)]
    subs += [b"(?{ " + b"{" * k + b" })" for k in (1, 3)]   # unbalanced: no match
    big = ['idents-1m', 'splice-1m', 'nest-brace-1k', 'nest-paren-1k', 'comment-5m', 'literal-100k', 'nest-digraph-10k']
else:
    random.seed(7)
    def val(d):
        r = random.random()
        if d > 6 or r < 0.3: return random.choice(['1', '-0.5e+3', '"a\\"b"', 'true', 'null', '"\\u00e9x"', '12', '""'])
        if r < 0.65: return '[' + ', '.join(val(d+1) for _ in range(random.randint(0, 3))) + ']'
        return '{' + ','.join('"k%d" : %s' % (i, val(d+1)) for i in range(random.randint(0, 3))) + '}'
    for i in range(150):
        v = val(0).encode()
        if i % 3 == 1 and len(v) > 2:
            j = random.randrange(len(v)); v = v[:j] + random.choice([b',', b']', b'}', b'"', b'x', b'']) + v[j+1:]
        subs.append(v)
    subs += [b'[' * k + b'1' + b']' * k for k in (1, 5, 30, 200)]
    subs += [b'[' * k + b'1' + b']' * (k - 1) for k in (3, 30)]
    big = ['js-near-1m']
    for f in sorted(os.listdir('/var/tmp/pcrec-pcrec/scratch/trailgc2/gap/jsubj'))[:4]:
        subs.append(open('/var/tmp/pcrec-pcrec/scratch/trailgc2/gap/jsubj/' + f, 'rb').read())
for b in big:
    subs.append(open('%s/%s.bin' % (B, b), 'rb').read()[:200000] if b not in ('nest-brace-1k', 'nest-paren-1k') else open('%s/%s.bin' % (B, b), 'rb').read())
caps = [None, (200000, 8), (200000, 16), (200000, 32), (200000, 64), (200000, 256), (400000, 4000000)]
p = os.path.join(V, 'tw', K + '_sub.bin')
def run(mode, cap):
    a = [os.path.join(V, 'b', '%s_%s' % (K, mode), 'cdrv'), p]
    if cap: a += [str(cap[0]), str(cap[1])]
    return subprocess.run(a, capture_output=True, text=True, timeout=120).stdout.strip()
bad = 0; cells = 0; twin_answers_stock_gaveup = 0; twin_gaveup_stock_answered = 0; matches = 0
for si, s in enumerate(subs):
    open(p, 'wb').write(s)
    ref = run('stock', caps[-1])
    if ref.startswith('rc=1'): matches += 1
    st = {c: run('stock', c) for c in caps}
    for mode in os.environ.get('MODES', 'B C BC').split():
        for c in caps:
            t = run(mode, c); cells += 1
            if t == st[c]: continue
            if st[c] == 'rc=-3' and t == ref: twin_answers_stock_gaveup += 1; continue
            if t == 'rc=-3' and st[c] != 'rc=-3': twin_gaveup_stock_answered += 1; print('TWIN-GAVEUP', K, mode, si, c, st[c]); continue
            bad += 1; print('DIFF', K, mode, si, c, 'stock', st[c][:80], 'twin', t[:80])
print('ident %s: subjects %d (matching %d), cells %d, diffs %d, twin answers where stock gave up %d, twin gives up where stock answered %d'
      % (K, len(subs), matches, cells, bad, twin_answers_stock_gaveup, twin_gaveup_stock_answered))
