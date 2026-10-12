# docs/dev/lanes/r16b_movers.py (lane r16b, R-16): base vs tree at -fmemfn-simd over every 8th distinct corpus pattern
# (argv 2: K, default 8; emit_sweep's own enumeration), both engines: every changed line must lie
# inside a `__w16(` helper or be the guarded-bytes stamp; no `__w32(` helper
# line may move (usage: python3 r16b_movers.py TREE [K] [BASE_PCREC]); count movers and w16-with-KB artifacts in the base.
import re, subprocess, sys
W = sys.argv[1]
sys.path.insert(0, W + '/scripts')
import emit_sweep as es
REF = sys.argv[3] if len(sys.argv) > 3 else W + '/build/r16b-ref/pcrec'   # the base build
NEW = W + '/build/pcrec'
EVERY = int(sys.argv[2]) if len(sys.argv) > 2 else 8
pats = es.distinct_patterns(es.enumerate_corpus(NEW, W, 30), every=EVERY)
def comp(b, p, eng):
    cmd = [b, '-p', 'rx', '--features', 'all', '-fmemfn-simd', '-o', '-'] + (['--engine=vm'] if eng else [])
    r = subprocess.run(cmd + ['--pattern', p], capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None
HEAD = re.compile(rb'^static inline size_t \w+__(w16|w32|body)\(')
stats = dict(pairs=0, movers=0, kb16_base=0, bad=0, w16_lines=0, stamp_lines=0)
for p in pats:
    p = p[2] if isinstance(p, tuple) else p
    for eng in (0, 1):
        try:
            a, b = comp(REF, p, eng), comp(NEW, p, eng)
        except subprocess.TimeoutExpired:
            continue
        if a is None or b is None: continue
        stats['pairs'] += 1
        al = a.split(b'\n')
        lvl, kb16 = None, False
        for x in al:
            m = HEAD.match(x)
            if m: lvl = m.group(1)
            elif x.startswith(b'}'): lvl = None
            if lvl == b'w16' and b'vb = ' in x: kb16 = True   # KB's broadcast (mb only where masked)
        stats['kb16_base'] += kb16
        if a == b:
            if kb16: print('w16-with-KB artifact NOT moved:', p, eng); stats['bad'] += 1
            continue
        stats['movers'] += 1
        bl = b.split(b'\n')
        if len(al) != len(bl): print('line count moved:', p, eng); stats['bad'] += 1; continue
        lvl = None
        for x, y in zip(al, bl):
            m = HEAD.match(y)
            if m: lvl = m.group(1)
            elif y.startswith(b'}'): lvl = None
            if x == y: continue
            if b'_SIMD_GUARDED_BYTES' in x: stats['stamp_lines'] += 1; continue
            if lvl == b'w16': stats['w16_lines'] += 1; continue
            print('unexpected line moved (%s):' % lvl, p, eng, y[:100]); stats['bad'] += 1; break
        if not kb16: print('mover without a w16 KB in base:', p, eng); stats['bad'] += 1
print('patterns', len(pats), stats)
