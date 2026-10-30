#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's find-any family,
#   lane simdset).
"""memfn/tests/run_g2_any.py -- G2's FIND-ANY family: the standalone kernel
`mf_kernel_find_any` (memfn/src/vany.c, lane simdset; NOT ROUTED, so no
pcrec site reaches it and this family is its only answer check). Run by
run_g2.sh (both tiers) as its section 4y, and on its own:

    python3 memfn/tests/run_g2_any.py [--root TREE] [--seed N] [--sets N] [--keep] [--quick]

Written by the kernel's author (not D27-blinded): its independent controls
are G2's own scalar byte loop, the generated space and the guard pages.

WHAT IT CHECKS, AND AGAINST WHAT
  1. THE SPACE (g2/g2_any_gen.c): byte sets, K 2..3, its fixed head (0x00,
     0xFF, high-bit, duplicates, one-bit neighbours, a case pair) then
     random; each set rendered at four level choices (none, w16 alone, w32
     alone, both). Every refusal the generator asks (K 1 and 4, a bad name,
     a level past mf_levels(), a sink without vprintf) must be refused.
     Population floors per class (K35), literals below.
  2. ANSWERS, PER BUILD: the rendered file compiled -Wall -Wextra -Werror at
     x86-64 (w16 live), x86-64-v3 (w32 live; w16 through the ladder's
     fall-through and its own arm), -mgeneral-regs-only (neither: the body)
     and ASan+UBSan at x86-64-v3, and run by g2/g2_any_driver.c against ITS
     OWN byte loop (exact position): every length 0..73, a hit at every
     position, every alignment, guard pages at s + n and below s + pos. A
     wrong answer or a fault is red; checks per build >= CHECK_FLOOR.
  3. PLANTS: the rendered text mutated per level (each edit counted: it must
     apply once per helper of the level); each must be RED where its level
     is live and GREEN where it is compiled out; the three that move a read
     bound by one byte must FAULT (a signal), not merely answer wrong.
  4. INSTRUCTION CLASSES: no PDEP/PEXT and no gather in the x86-64-v3
     driver (levels.def's `forbid`), read with objdump.
On a host that cannot run a level, its builds are BUILT, not run: printed
`SKIPPED ARM <level>: <why>; N checks NOT run`, never a silent pass. A host
that is not x86-64 runs the portable build alone (every level SKIPPED).

Prints `checks passed: N` / `checks failed: N`; exit 1 on any failure.
"""
import argparse
import concurrent.futures
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --- the expectations and floors: literals, written here --------------------
# the register width of each level stamp, written HERE (not read from the
# kit): the plants move bounds by these
VW = {'w16': 16, 'w32': 32}
# builds: name, flags, live levels, the host need (None: any x86-64)
BUILDS = [
    ('x86-64',      ['-O2', '-march=x86-64'],       {'w16'},        None),
    ('x86-64-v3',   ['-O2', '-march=x86-64-v3'],    {'w16', 'w32'}, 'x86-64-v3'),
    ('gpr-only',    ['-O2', '-mgeneral-regs-only'], set(),          None),
    ('asan-x86-64-v3', ['-O1', '-march=x86-64-v3', '-fsanitize=address,undefined',
                        '-fno-sanitize-recover=all', '-fno-omit-frame-pointer'],
     {'w16', 'w32'}, 'x86-64-v3'),
]
NEEDS = {'x86-64-v3': 'AVX2'}
# answer checks per full build: 20,292,480 measured (Linux dev box,
# 2026-10-29, seed 20261029, 40 sets); ~80%
CHECK_FLOOR = 16000000
# the space's populations (40 sets at the default seed; ~80% of measured,
# each measurement in parentheses)
POP_FLOOR = {
    'kernels': 128,        # (160)
    'levels-0': 32,        # each level choice (40 each)
    'levels-1': 32,
    'levels-2': 32,
    'levels-3': 32,
    'k2': 12, 'k3': 12,    # sets by K
    'dup': 4,              # a set with a repeated byte
    'zero': 3, 'ff': 3,    # 0x00 / 0xFF a member
    'high': 16,            # a member >= 0x80
}
# PLANTS: name -> (helper kind, (old, new) text edit with {VW}/{VW1}, the
# edit's count per helper, fault?). Each edit is applied inside every helper
# of its kind and must match exactly `per` times in each; `member-dropped`
# skips the helpers of a one-member kernel (a duplicated set has no v1).
PLANTS = [
    ('final-late',     'lvl', ('subject + (n - {VW})))', 'subject + (n - {VW} + 1)))'), 1, True),
    ('loop-past',      'lvl', ('for (; n - i >= {VW};', 'for (; n - i >= {VW1};'), 1, True),
    ('entry-short',    'lvl', ('n - pos < {VW})', 'n - pos < {VW1})'), 1, True),
    ('no-final',       'lvl', ('    if (i == n) return n;\n', '    return n;\n'), 1, False),
    ('high-lane',      'lvl', ('return i + (size_t)__builtin_ctz(m)',
                               'return i + (size_t)(31 - __builtin_clz(m))'), 1, False),
    ('member-dropped', 'lvl', ('(x, v1)', '(x, v0)'), 2, False),
    ('body-last',      'body', ('i < n; i++)', 'i + 1 < n; i++)'), 1, False),
]
GREEN_STRIDE = '5'       # a plant run that must stay green runs every 5th kernel

passed = failed = 0
SKIPPED = {}


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    print('FAIL: ' + msg)


def sh(cmd, timeout=600):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


PROBE_C = '''#include <stdio.h>
int main(void)
{
    __builtin_cpu_init();
    printf("x86-64-v3 %d\\n", __builtin_cpu_supports("x86-64-v3") != 0);
    return 0;
}
'''


def host_skips(work):
    """The levels this host cannot run: the compiler's own level definition,
    probed at plain -march=x86-64; G2A_SKIP_ARMS=x86-64-v3 forces a skip."""
    skip = {}
    src, exe = os.path.join(work, 'probe.c'), os.path.join(work, 'probe')
    open(src, 'w').write(PROBE_C)
    r = sh(['gcc', '-O0', '-march=x86-64', '-o', exe, src])
    if r.returncode:
        sys.exit('run_g2_any: host-level probe failed to build: ' + r.stderr[-500:])
    r = sh([exe])
    host = dict(l.split() for l in r.stdout.splitlines())
    if r.returncode or set(host) != set(NEEDS):
        sys.exit('run_g2_any: host-level probe failed to run: rc=%d %r' % (r.returncode, r.stdout))
    for lv, need in NEEDS.items():
        if host[lv] != '1':
            skip[lv] = 'host lacks %s' % need
    for lv in filter(None, os.environ.get('G2A_SKIP_ARMS', '').replace(' ', '').split(',')):
        if lv not in NEEDS:
            sys.exit('run_g2_any: G2A_SKIP_ARMS=%s: only %s can be skipped' % (lv, sorted(NEEDS)))
        skip[lv] = 'forced by G2A_SKIP_ARMS (%s)' % NEEDS[lv]
    return skip


HELPER = re.compile(r'static inline size_t (g2a_\d+)__(w16|w32|body)\(.*?\n\}\n', re.S)


def plant_text(text, kind, lvl, old, new, per):
    """The text with the edit applied inside every helper of (kind, lvl);
    None unless it matched exactly `per` times in each (a helper with none
    is skipped for the member plant only) and in at least one helper."""
    out, last, nhelp = [], 0, 0
    for m in HELPER.finditer(text):
        if (kind == 'body') != (m.group(2) == 'body') or (kind == 'lvl' and m.group(2) != lvl):
            continue
        c = m.group(0).count(old)
        if c == 0 and old == '(x, v1)':
            continue
        if c != per:
            return None
        nhelp += 1
        out.append(text[last:m.start()])
        out.append(m.group(0).replace(old, new))
        last = m.end()
    out.append(text[last:])
    return ''.join(out) if nhelp else None


def build(root, work, name, flags, kernels, tag, extra=()):
    exe = os.path.join(work, 'drv-%s-%s' % (name, tag))
    r = sh(['gcc'] + flags + ['-Wall', '-Wextra', '-Werror'] + list(extra) +
           ['-DG2A_KERNELS="%s"' % kernels,
                              '-o', exe, os.path.join(HERE, 'g2', 'g2_any_driver.c')])
    return exe, r


def run_drv(exe, args, asan):
    env = dict(os.environ)
    if asan:
        env['ASAN_OPTIONS'] = 'detect_leaks=0'
    r = subprocess.run([exe] + args, capture_output=True, text=True, timeout=600, env=env)
    m = re.search(r'^checks (\d+)$', r.stdout, re.M)
    return r, int(m.group(1)) if m else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(HERE)))
    ap.add_argument('--seed', default='20261029')
    ap.add_argument('--sets', type=int, default=40)
    ap.add_argument('--lib', help='the kit library the generator links')
    ap.add_argument('--keep', action='store_true')
    ap.add_argument('--quick', action='store_true', help='accepted for run_g2.sh; the family '
                    'is one tier (~30 s)')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    work = tempfile.mkdtemp(prefix='g2any.', dir=os.environ.get('TMPDIR'))
    try:
        run(a, root, work)
    finally:
        if a.keep:
            print('kept: ' + work)
        else:
            shutil.rmtree(work, ignore_errors=True)
    for lv, (why, n) in sorted(SKIPPED.items()):
        print('SKIPPED ARM %s: %s; %d checks NOT run (built, not run)' % (lv, why, n))
    print('skipped arms: %d' % len(SKIPPED))
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


def population(meta):
    pop = dict.fromkeys(POP_FLOOR, 0)
    seen = set()
    for line in open(meta):
        kid, k, b, lv = line.rstrip('\n').split('\t')
        pop['kernels'] += 1
        pop['levels-' + lv] = pop.get('levels-' + lv, 0) + 1
        bs = [int(x) for x in b.split(',')][:int(k)]
        key = (k, b)
        if key in seen:
            continue
        seen.add(key)
        pop['k' + k] += 1
        pop['dup'] += len(set(bs)) < len(bs)
        pop['zero'] += 0 in bs
        pop['ff'] += 255 in bs
        pop['high'] += any(x >= 128 for x in bs)
    return pop


def run(a, root, work):
    gen = os.path.join(work, 'gen')
    r = sh(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', os.path.join(root, 'memfn', 'include'),
            '-o', gen, os.path.join(HERE, 'g2', 'g2_any_gen.c'),
            a.lib or os.path.join(root, 'build', 'libpcrec.a')])
    if r.returncode:
        bad('generator build failed: ' + r.stderr[-2000:])
        return
    r = sh([gen, a.seed, str(a.sets), work])
    if r.returncode:
        bad('generator failed: ' + (r.stderr + r.stdout)[-2000:])
        return
    ok()
    # 1. the space's populations
    pop = population(os.path.join(work, 'g2a_meta.tsv'))
    for key, floor in POP_FLOOR.items():
        (ok() if pop[key] >= floor else bad('population %s %d < floor %d' % (key, pop[key], floor)))
    print('space ' + ' '.join('%s=%d' % kv for kv in sorted(pop.items())))

    kernels = os.path.join(work, 'g2a_kernels.c')
    text = open(kernels).read()
    x86 = platform.machine() in ('x86_64', 'AMD64')
    skip = host_skips(work) if x86 else {}
    builds = BUILDS if x86 else [('native', ['-O2'], set(), None)]
    if not x86:
        for lv in VW:
            SKIPPED['level ' + lv] = ('host is %s, not x86-64' % platform.machine(), 0)

    # 2. answers per build
    jobs = int(os.environ.get('G2A_JOBS', '4'))
    def answer(b):
        name, flags, live, need = b
        exe, r = build(root, work, name, flags, kernels, 'plain')
        if r.returncode:
            return name, 'build', r.stderr[-1500:], 0
        if need in skip:
            return name, 'skip', skip[need], 0
        rr, n = run_drv(exe, [], 'asan' in name)
        return name, rr.returncode, rr.stdout[-1500:] + rr.stderr[-1500:], n
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(answer, builds))
    for name, rc, out, n in res:
        if rc == 'build':
            bad('%s: the rendered kernels do not compile: %s' % (name, out))
        elif rc == 'skip':
            SKIPPED[name] = (out, max([x[3] for x in res if isinstance(x[1], int)] + [0]))
        elif rc != 0:
            bad('%s: rc %s: %s' % (name, rc, out))
        elif n < CHECK_FLOOR:
            bad('%s: %d answer checks < floor %d' % (name, n, CHECK_FLOOR))
        else:
            ok()
        if rc not in ('build', 'skip'):
            print('build %s: checks %d rc %s' % (name, n, rc))

    # 3. plants, at the three plain builds
    plain = [b for b in builds if 'asan' not in b[0]]
    tasks = []
    for pname, kind, (old, new), per, fault in PLANTS:
        for lvl in (VW if kind == 'lvl' else ['body']):
            vw = VW.get(lvl, 0)
            o, nw = old.format(VW=vw, VW1=vw - 1), new.format(VW=vw, VW1=vw - 1)
            t = plant_text(text, kind, lvl, o, nw, per)
            if t is None:
                bad('plant %s@%s: the edit does not apply once per helper' % (pname, lvl))
                continue
            path = os.path.join(work, 'plant-%s-%s.c' % (pname, lvl))
            open(path, 'w').write(t)
            for b in plain:
                tasks.append((pname, lvl, fault, path, b))
    def plant(task):
        pname, lvl, fault, path, (name, flags, live, need) = task
        # a dropped member leaves its broadcast unused
        exe, r = build(root, work, name, flags, path, '%s-%s' % (pname, lvl),
                       ['-Wno-unused-variable'])
        if r.returncode:
            return task, 'build', r.stderr[-800:]
        if need in skip:
            return task, 'skip', None
        is_live = lvl == 'body' or lvl in live
        rr, _ = run_drv(exe, ['1', 'stop'] if is_live else [GREEN_STRIDE], False)
        return task, rr.returncode, rr.stdout[-600:]
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        pres = list(ex.map(plant, tasks))
    for (pname, lvl, fault, path, (name, flags, live, need)), rc, out in pres:
        tag = 'plant %s@%s at %s' % (pname, lvl, name)
        if rc == 'build':
            bad(tag + ': does not compile: ' + out)
            continue
        if rc == 'skip':
            n0 = SKIPPED.get(name, ('', 0))
            SKIPPED[name] = (skip[need], n0[1])
            continue
        is_live = lvl == 'body' or lvl in live
        print('%s: %s' % (tag, 'GREEN' if rc == 0 else 'FAULT' if rc < 0 else 'RED'))
        if not is_live:
            (ok() if rc == 0 else bad(tag + ': compiled out, yet red (rc %s): %s' % (rc, out)))
        elif fault:
            (ok() if rc < 0 else bad(tag + ': must FAULT, rc %s: %s' % (rc, out)))
        else:
            (ok() if rc != 0 else bad(tag + ': stayed GREEN at a live level'))
    print('plants: %d runs' % len(pres))

    # 4. instruction classes in the w32 build
    if x86:
        exe = os.path.join(work, 'drv-x86-64-v3-plain')
        if os.path.exists(exe):
            r = sh(['objdump', '-d', '--no-show-raw-insn', exe])
            hits = sorted(set(re.findall(r'\b(pdep|pext|v?p?gather\w*)\b', r.stdout)))
            (ok() if r.returncode == 0 and not hits else
             bad('instruction classes: objdump rc %d, forbidden %s' % (r.returncode, hits)))


if __name__ == '__main__':
    sys.exit(main())
