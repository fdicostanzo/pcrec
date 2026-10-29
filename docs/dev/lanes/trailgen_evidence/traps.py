"""traps.py : UNDO-DEAD (vmopt_tg -m BCdU) and R on the trap witnesses (vmbc's list + capture/
alternation/loop/backreference shapes). Stock pcrec (lane/trailgc) is the reference; every
subject, default arm and _in arm at trail caps 4/16/1000; every capture compared."""
import os, subprocess, sys, itertools
T = '/var/tmp/pcrec-pcrec/scratch/trailgen'
PCREC = '/home/pcrec/projects/pcrec/worktrees/trailgen/build/pcrec'
W = '/home/pcrec/projects/pcrec/worktrees/trailgen'
CASES = [
    (r'^(a(?1)?b)\1$', ['aabbaabb', 'abab', 'aabbab', 'ab']),
    (r'^((?>a(?1)?))a$', ['aaa', 'aa', 'a', 'aaaa']),
    (r'^((a)(?1)?(b))$', ['ab', 'aabb', 'aaabbb', 'aab']),
    (r'^(a\Kb)(?1)$', ['abab', 'ab', 'abb']),
    (r'(?:a|bc){3}+', ['abca', 'aaa', 'bcbcbc', 'abcbca', 'xaaab']),
    (r'(a)|b', ['b', 'a', 'cb', 'ca']),
    (r'(a|ab)(c|bcd)(d*)', ['abcd', 'acd', 'abcdd', 'xabcd']),
    (r'^(?:(a)|b)*$', ['ab', 'ba', 'bab', 'aab', 'bb', '']),
    (r'(a)?b\1', ['abab', 'bb', 'ab', 'aba', 'b']),
    (r'(\w)(\w)\2\1', ['abba', 'xabbay', 'abab', 'aaaa']),
    (r'(?:(a)|(b))+c', ['abc', 'bac', 'aac', 'bbc', 'c', 'abac']),
    (r'(a+)+b', ['aaab', 'aaa', 'ab']),
    (r'(?=(a))a(b)?', ['ab', 'a', 'b']),
    (r'(?:x(a)|x(b))c', ['xac', 'xbc', 'xc']),
    (r'^(?:(a)|(a)b)*c', ['abc', 'aabc', 'ababc', 'c']),
    (r'(a)(?:b|(c))*d\2?', ['abd', 'acd', 'acbd', 'abcbd']),
    (r'((a)|b)+?c(?(2)x|y)', ['ac', 'acx', 'bcy', 'abcx', 'bacx']),
    (r'(?|(a)|(b))\1', ['aa', 'bb', 'ab']),
]
cdrv = '/var/tmp/pcrec-pcrec/scratch/vmbc/cdrv.c'
def build(d):
    return subprocess.run(['gcc', '-O2', '-std=gnu11', '-I' + W + '/lib', '-I' + d, '-DHDR="rx.h"', '-DPFX_search=rx_search',
                           '-DPFX_search_in=rx_search_in', '-DPFX_NCAPS=RX_NCAPS', '-DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE',
                           '-DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE', '-DPFX_buffers=rx_buffers', '-o', d + '/cdrv', cdrv, d + '/rx.c'],
                          capture_output=True, text=True).returncode == 0
tot = bad = 0; nU = 0; notvm = 0
for ci, (pat, subs) in enumerate(CASES):
    d = os.path.join(T, 'traps', 'c%02d' % ci)
    os.makedirs(d + '/stock', exist_ok=True); os.makedirs(d + '/U', exist_ok=True); os.makedirs(d + '/UR', exist_ok=True)
    r = subprocess.run([PCREC, '-p', 'rx', '--features', 'all', '--engine=vm', '--pattern', pat, '-o', d + '/stock/rx.c'], capture_output=True, text=True)
    if r.returncode != 0:
        print('EMIT-FAIL', pat, r.stderr.strip()[-100:]); continue
    r = subprocess.run(['python3', '-I', T + '/vmopt_tg.py', '-m', 'BCdU', d + '/stock/rx.c', d + '/U/rx.c'], capture_output=True, text=True)
    st = r.stderr.strip()
    open(d + '/U/rx.h', 'w').write(open(d + '/stock/rx.h').read())
    r2 = subprocess.run(['python3', '-I', T + '/variants.py', 'R', d + '/U/rx.c', d + '/UR/rx.c'], capture_output=True, text=True)
    open(d + '/UR/rx.h', 'w').write(open(d + '/stock/rx.h').read())
    oks = [build(d + '/' + t) for t in ('stock', 'U', 'UR')]
    print('%-28s %s builds=%s R=%s' % (pat, st.split(' ', 3)[-1][:110], oks, 'ok' if r2.returncode == 0 else r2.stderr.strip()[-60:]))
    for s in subs:
        sp = d + '/sub.bin'; open(sp, 'w').write(s)
        for cap in (None, ('64', '4'), ('64', '16'), ('64', '1000')):
            a = [sp] + (list(cap) if cap else [])
            ref = subprocess.run([d + '/stock/cdrv'] + a, capture_output=True, text=True).stdout.strip()
            for t in ('U', 'UR'):
                if not os.path.exists(d + '/' + t + '/cdrv'):
                    continue
                got = subprocess.run([d + '/' + t + '/cdrv'] + a, capture_output=True, text=True).stdout.strip()
                tot += 1
                if got != ref and not (ref == 'rc=-3'):
                    bad += 1; print('  DIFF', t, repr(s), cap, 'stock', ref, 'twin', got)
print('traps: %d patterns, %d cells, %d diffs (a twin answering where stock gave up is not a diff)' % (len(CASES), tot, bad))
