#!/usr/bin/env python3
"""pred.py CASEFOLDING PCREC PATTERN_TEXT... -- per caseless literal pattern
(text only, no metacharacters), print the required run under each stage of
docs/design/alt_normal_form.md:
  today   MEASURED: pcrec -e utf8 --emit-facts on '(?i)TEXT'
  s0      MEASURED control: today's lowering spelled as bytes, no seal
  s1      MEASURED: the stage-1 lowering spelled as a byte pattern (exact
          products factored into position classes, other length groups left
          as alternations, no A_EMPTY seal), pcrec -e byte with altcls denied
  s2c     INFERRED: + superset hull in rr_alt (equal-width groups), cube domain
  s3      INFERRED: + set positions (D187), exact and superset
  s3m     INFERRED: s3 + one affix position each side of a mixed-width letter
Also the DFA size of today vs s1 (next-state table entries, artifact bytes).
Run positions in the inferred columns: info = sum(8 - ceil(log2 |S|)),
floor 16 bits, the best run by info (leftmost on a tie)."""
import sys, subprocess, collections, math, re, tempfile, os

cf, pcrec = sys.argv[1], sys.argv[2]
groups = collections.defaultdict(set)
for line in open(cf, encoding='utf-8'):
    line = line.split('#')[0].strip()
    if not line: continue
    f = [x.strip() for x in line.split(';')]
    if f[1] not in ('C', 'S'): continue
    s, d = int(f[0], 16), int(f[2], 16)
    groups[d] |= {s, d}
cls_of = {}
for d, mem in groups.items():
    for m in mem: cls_of[m] = mem

def members(ch):
    return sorted(cls_of.get(ord(ch), {ord(ch)}))

def facts(enc, pat, extra=()):
    out = subprocess.run([pcrec, '-e', enc, *extra, '--emit-facts', '--pattern', pat],
                         capture_output=True, text=True, timeout=30).stdout
    d = {}
    for l in out.splitlines():
        p = l.split('\t')
        if len(p) > 6 and p[1] in ('req_whole_run', 'req_run'): d[p[1]] = p[6]
        if len(p) > 2 and p[1] in ('RX_DFA_SCAN', 'RX_DFA_PREFILTER', 'RX_ENGINE'): d[p[1]] = p[2]
    return d

def npos(run):
    if run in (None, 'none', ''): return 0
    return len(run.split('@')[0].split('/')[0]) // 2

def size(enc, pat, extra=()):
    with tempfile.TemporaryDirectory(dir=os.environ.get('PCREC_TMPDIR')) as t:
        o = os.path.join(t, 'a.c')
        subprocess.run([pcrec, '-e', enc, *extra, '-p', 'rx', '-o', o, '--pattern', pat],
                       capture_output=True, timeout=60)
        src = open(o).read()
    n = 0
    for m in re.finditer(r'_next_state\[[^\]]*\]\s*=\s*\{(.*?)\};', src, re.S):
        n += len([x for x in m.group(1).split(',') if x.strip()])
    return n, len(src)

def bx(b): return '\\x%02x' % b
def setx(s):
    s = sorted(s)
    return bx(s[0]) if len(s) == 1 else '[' + ''.join(bx(b) for b in s) + ']'

def char_parts(ch):
    """[(width, [position sets], exact)] one per length group."""
    encs = [chr(c).encode() for c in members(ch)]
    by = collections.defaultdict(list)
    for e in encs: by[len(e)].append(e)
    parts = []
    for w in sorted(by):
        es = by[w]
        pos = [set(e[i] for e in es) for i in range(w)]
        prod = math.prod(len(p) for p in pos)
        parts.append((w, pos, prod == len(es), es))
    return parts

def boxed(es):
    """u8_box's shape for single code points: members sharing all but the
    last byte with contiguous last bytes are one branch (a byte range)."""
    by = collections.defaultdict(list)
    for e in sorted(es): by[e[:-1]].append(e[-1])
    out = []
    for pre, lasts in sorted(by.items()):
        lasts.sort(); run = [lasts[0]]
        for b in lasts[1:] + [None]:
            if b is not None and b == run[-1] + 1: run.append(b); continue
            r = bx(run[0]) if len(run) == 1 else '[%s-%s]' % (bx(run[0]), bx(run[-1]))
            out.append(''.join(bx(x) for x in pre) + r)
            if b is not None: run = [b]
    return out

def s1_spell(text, factor=True):
    """factor=False is the CONTROL: today's lowering spelled as bytes (no
    product factoring, no seal), so s0 -> s1 isolates the factoring."""
    out = []
    for ch in text:
        if ord(ch) < 0x80 and len(members(ch)) == 1: out.append(bx(ord(ch))); continue
        parts = char_parts(ch)
        if all(w == 1 for w, _, _, _ in parts):
            out.append(setx(parts[0][1][0])); continue
        alts = []
        for w, pos, exact, es in parts:
            if exact and factor: alts.append(''.join(setx(p) for p in pos))
            else: alts.extend(boxed(es))
        out.append(alts[0] if len(alts) == 1 else '(?:' + '|'.join(alts) + ')')
    return ''.join(out)

def is_cube(s):
    s = sorted(s); k = 0xFF
    for b in s[1:]: k &= ~(b ^ s[0])
    return (1 << (8 - bin(k & 0xFF).count('1'))) == len(s)

def info(s): return 8 - math.ceil(math.log2(len(s)))

def best_run(text, sets_ok, superset_ok, affix):
    """Sequence of positions or breaks; return (positions, bits)."""
    seq = []
    for ch in text:
        parts = char_parts(ch)
        if len(parts) == 1:
            w, pos, exact, _ = parts[0]
            if exact or superset_ok: seq.extend(pos); continue
            seq.append(None); continue
        if affix:
            first = set().union(*[p[0] for _, p, _, _ in parts])
            last = set().union(*[p[-1] for _, p, _, _ in parts])
            seq.extend([first, None, last])
        else:
            seq.append(None)
    def ok(s):
        if s is None: return False
        if len(s) == 1: return True
        if sets_ok: return len(s) < 256
        return len(s) <= 2 and is_cube(s)
    best, cur = (0, 0), []
    for s in seq + [None]:
        if ok(s): cur.append(s); continue
        bits = sum(info(x) for x in cur)
        if bits > best[1]: best = (len(cur), bits)
        cur = []
    return best if best[1] >= 16 else (0, best[1])

deny = ('-fno-altcls-merge', '-fno-altcls-factor')
print('pattern\ttoday\ts0\ts1\ts2c\ts3\ts3m\ttoday_scan/pf\ts1_scan/pf\tentries today/s0->s1\tbytes s0->s1')
for text in sys.argv[3:]:
    t = facts('utf8', '(?i)' + text)
    sp = s1_spell(text)
    s = facts('byte', sp, deny)
    r2 = best_run(text, False, True, False)
    r3 = best_run(text, True, True, False)
    r3m = best_run(text, True, True, True)
    s0 = s1_spell(text, False)
    f0 = facts('byte', s0, deny)
    et, _ = size('utf8', '(?i)' + text)
    e0, b0 = size('byte', s0, deny)
    e1, b1 = size('byte', sp, deny)
    print('\t'.join([text, str(npos(t.get('req_whole_run'))), str(npos(f0.get('req_whole_run'))), str(npos(s.get('req_whole_run'))),
                     str(r2[0]), str(r3[0]), str(r3m[0]),
                     '%s/%s' % (t.get('RX_DFA_SCAN'), t.get('RX_DFA_PREFILTER')),
                     '%s/%s' % (s.get('RX_DFA_SCAN'), s.get('RX_DFA_PREFILTER')),
                     '%d/%d->%d' % (et, e0, e1), '%d->%d' % (b0, b1)]))
