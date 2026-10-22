#!/usr/bin/env python3
"""substd27 differential runner: pcrec's compiled substitution vs libpcre2.

usage: run_diff.py CASES.tsv [CASES.tsv...] [--work DIR] [--pcrec BIN]

CASES.tsv columns (tab-separated, '#' comments; fields use lib/esc.py's
escapes):  id  family  flags  pattern  template  unset  limit  subject  [mode]
  flags   extra pcrec compile flags (always plus --features all), e.g. -e utf8
  unset   empty | error   (substb2: error = the run-time flag RX_SUBST_STRICT)
  limit   all | N
  subject the subject bytes, or <NULL> for a NULL pointer (length 0)
  mode    diff (default) | nogap (element without RX_SUBST_GAPS vs
          PCRE2_SUBSTITUTE_REPLACEMENT_ONLY) | expect:BYTES (pcrec-only
          expectation, no libpcre2 comparison) | known:N (a documented §9
          difference row N: printed, not a failure)

Every rx and subst artifact is compiled once; one driver TU includes every
header (subst_api.md §1¶3) and the support unit (`pcrec --emit-support`,
§10), linked under -fsanitize=address,undefined.

substb2: driven through the R4 interface (the driver's header says how); the
`unset` column is the run-time RX_SUBST_STRICT flag of the case (no `--unset=`
at template compile, so one subst artifact serves both), never a compile
argument.
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from esc import unesc, esc, cstr  # noqa: E402
from ref_pcre2 import ref  # noqa: E402

# substfix (adoption): paths from the environment, not the writer's cell.
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TIMEOUT = os.environ.get('TIMEOUT_BIN', 'timeout')
CC = os.environ.get('CC', 'gcc')
SAN = ['-fsanitize=address,undefined', '-fno-sanitize-recover=undefined', '-g', '-O1', '-std=gnu11']


def sh(args, **kw):
    return subprocess.run([TIMEOUT, '120'] + args, capture_output=True, **kw)


def load(paths):
    cases = []
    for p in paths:
        for ln in open(p, encoding='utf-8'):
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#'):
                continue
            f = ln.split('\t')
            while len(f) < 9:
                f.append('')
            cid, fam, flags, pat, tpl, unset, limit, subj, mode = f[:9]
            cases.append(dict(id=cid, fam=fam, flags=flags, pat=unesc(pat), tpl=unesc(tpl),
                              unset=unset or 'empty', limit=limit or 'all',
                              snull=subj == '<NULL>', subj=b'' if subj == '<NULL>' else unesc(subj),
                              mode=mode or 'diff'))
    ids = [c['id'] for c in cases]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit('duplicate ids: %s' % sorted(dup))
    return cases


def tenc(flags):
    """substfix: the template's encoding is the case's -e (subst_api.md §2¶5)."""
    f = flags.split()
    return 'utf8' if ('-e' in f and f[f.index('-e') + 1] == 'utf8') or '--encoding=utf8' in f else 'byte'


def main():
    argv = sys.argv[1:]
    work = None
    pcrec = os.environ.get('PCREC', os.path.join(ROOT, 'build', 'pcrec'))
    if '--work' in argv:
        i = argv.index('--work'); work = argv[i + 1]; del argv[i:i + 2]
    if '--pcrec' in argv:
        i = argv.index('--pcrec'); pcrec = argv[i + 1]; del argv[i:i + 2]
    if not work:
        sys.exit('run_diff.py: --work DIR is required')
    os.makedirs(work, exist_ok=True)
    cases = load(argv)

    rxs, subs = {}, {}
    for c in cases:
        rxs.setdefault((c['flags'], c['pat']), 'r%d' % len(rxs))
        subs.setdefault((c['tpl'], tenc(c['flags'])), 's%d' % len(subs))

    def comp_rx(item):
        (flags, pat), pfx = item
        r = sh([pcrec, '--features', 'all'] + flags.split() + ['-p', pfx, '-o', '%s/%s.c' % (work, pfx),
                                                              '--pattern', pat])
        return pfx, r.returncode, r.stderr.decode('latin-1').strip()

    def comp_sub(item):
        (tpl, enc), pfx = item
        tf = '%s/%s.tpl' % (work, pfx)
        open(tf, 'wb').write(tpl)
        r = sh([pcrec, '-p', pfx, '-e', enc, '-o', '%s/%s.c' % (work, pfx),
                '--subst-file', tf])
        return pfx, r.returncode, r.stderr.decode('latin-1').strip()

    with ThreadPoolExecutor(4) as ex:
        rxres = {p: (rc, e) for p, rc, e in ex.map(comp_rx, rxs.items())}
        subres = {p: (rc, e) for p, rc, e in ex.map(comp_sub, subs.items())}
    ok_rx = {p for p, (rc, _) in rxres.items() if rc == 0}
    ok_sub = {p for p, (rc, _) in subres.items() if rc == 0}

    def cc(pfx):
        r = sh([CC] + SAN + ['-c', '-I', work, '-o', '%s/%s.o' % (work, pfx), '%s/%s.c' % (work, pfx)])
        return pfx, r.returncode, r.stderr.decode('latin-1')[-2000:]
    with ThreadPoolExecutor(4) as ex:
        ccres = list(ex.map(cc, sorted(ok_rx | ok_sub)))
    for pfx, rc, err in ccres:
        if rc:
            print('CC-FAIL %s: %s' % (pfx, err))
            ok_rx.discard(pfx); ok_sub.discard(pfx)

    runnable = []
    for c in cases:
        c['rx'] = rxs[(c['flags'], c['pat'])]
        c['sub'] = subs[(c['tpl'], tenc(c['flags']))]
        if c['rx'] in ok_rx and c['sub'] in ok_sub:
            runnable.append(c)
    r = sh([pcrec, '--emit-support', '-o', work + '/support.h'])   # substb2: the support unit (§10)
    if r.returncode:
        sys.exit('--emit-support failed:\n' + r.stderr.decode('latin-1')[-2000:])
    with open(work + '/cases_hdrs.inc', 'w') as h:
        for p in sorted(ok_rx | ok_sub):
            h.write('#include "%s.h"\n' % p)
    with open(work + '/cases_tab.inc', 'w') as h:
        h.write('static const struct tcase cases[] = {\n')
        for c in runnable:
            lim = 'SIZE_MAX' if c['limit'] == 'all' else '(size_t)%s' % c['limit']
            h.write('  { %s, &%s_info, &%s_subst_info, %s, %d, %d, %s, %d, %d },\n' % (
                cstr(c['id'].encode()), c['rx'], c['sub'], cstr(c['subj']), len(c['subj']),
                int(c['snull']), lim, int(c['mode'] == 'nogap'), int(c['unset'] == 'error')))
        if not runnable:
            h.write('  { "none", 0, 0, 0, 0, 0, 0, 0, 0 },\n')
        h.write('};\n')
    objs = ['%s/%s.o' % (work, p) for p in sorted(ok_rx | ok_sub)]
    r = sh([CC] + SAN + ['-I', work, '-I', HERE, '-o', work + '/driver', HERE + '/diff_driver.c'] + objs)
    if r.returncode:
        sys.exit('driver build failed:\n' + r.stderr.decode('latin-1')[-4000:])
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:abort_on_error=0', UBSAN_OPTIONS='print_stacktrace=1')
    res = {}
    for c in runnable:   # one process per case: a sanitizer abort is that case's verdict alone
        r = subprocess.run([TIMEOUT, '30', work + '/driver', c['id']], capture_output=True, env=env)
        out = r.stdout.decode('latin-1').strip()
        res[c['id']] = (r.returncode, out, r.stderr.decode('latin-1')[-3000:])

    stats = dict(PASS=0, FAIL=0, KNOWN=0, FINDING=0, PCREC_REFUSED=0, REF_ONLY=0)
    lines = []
    for c in cases:
        v, why = verdict(c, rxres, subres, res)
        stats[v] = stats.get(v, 0) + 1
        lines.append('%s\t%s\t%s\t%s' % (v, c['id'], c['fam'], why))
    with open(work + '/verdicts.tsv', 'w') as h:
        h.write('\n'.join(lines) + '\n')
    for ln in lines:
        if not ln.startswith('PASS'):
            print(ln)
    print('TOTAL %d  %s' % (len(cases), '  '.join('%s=%d' % kv for kv in sorted(stats.items()))))


def verdict(c, rxres, subres, res):
    lim = c['limit'] if c['limit'] == 'all' else int(c['limit'])
    mode = c['mode']
    if mode.startswith('expect:') or mode.startswith('expectrc:'):
        want = None
    elif lim == 0:
        want = dict(kind='ok', out=c['subj'], n=0)
    else:
        want = ref(c['pat'], c['flags'], c['tpl'], c['subj'], lim, c['unset'], gaps=mode != 'nogap')
    rrc, rerr = rxres[c['rx']]
    src, serr = subres[c['sub']]
    known = mode.startswith('known:') or mode.startswith('finding:')
    klabel = 'KNOWN' if mode.startswith('known:') else 'FINDING'
    if src != 0:
        if want and want['kind'] == 'err' and want['code'] in (-35, -58, -59, -49) and want['where'] == 'substitute':
            return 'PASS', 'template refused; pcre2 %d' % want['code']
        # substfix: a utf8 template is UTF-checked at compile (subst_api.md
        # §2¶3, §9 row 13), where pcre2 returns a UTF-8 error at substitute
        if (want and want['kind'] == 'err' and -23 <= want['code'] <= -3 and want['where'] == 'substitute'
                and tenc(c['flags']) == 'utf8'):
            return 'PASS', 'template refused at compile; pcre2 UTF-8 error %d' % want['code']
        if mode == 'tplrefuse':
            return 'PASS', 'template refused as expected'
        return (klabel if known else 'FAIL'), 'template refused (%s) but pcre2 %s' % (serr[:150], want)
    if mode == 'tplrefuse':
        return 'FAIL', 'template compiled, expected refusal'
    if rrc != 0:
        return 'PCREC_REFUSED', 'pattern: ' + rerr[:150]
    if c['id'] not in res:
        return 'FAIL', 'not run'
    prc, out, err = res[c['id']]
    if prc != 0 or 'runtime error' in err or 'Sanitizer' in err:
        return 'FAIL', 'driver exit %d: %s | %s' % (prc, out, err.replace('\n', ' ')[:600])
    f = out.split()
    if f[1] == 'BIND':
        got = ('BIND', int(f[2]), int(f[3]))
    else:
        rc0, len0, k0 = int(f[2]), int(f[3]), int(f[4])
        rc1, len1, k1 = int(f[6]), int(f[7]), int(f[8])
        hexo, notes = f[10], f[12]
        got = ('RUN', rc0, len0, k0, rc1, len1, k1, b'' if hexo == '-' else bytes.fromhex(hexo), notes)
    if mode.startswith('expect:') or mode.startswith('expectrc:'):
        if mode.startswith('expect:'):
            e = unesc(mode[7:])
            ok = got[0] == 'RUN' and got[1] == 0 and got[7] == e and got[8] == 'ok'
        else:
            e = mode[9:]
            ok = (got[0] + ' ' + str(got[1])) == e or (got[0] == 'BIND' and 'BIND %d %d' % (got[1], got[2]) == e)
        return ('PASS' if ok else 'FAIL'), 'want %s got %s' % (e, show(got))
    if got[0] == 'BIND' and got[1] == -16 and want['kind'] == 'err' and want['code'] == -55:
        # pcre2 met an unset group before the unknown one; ask it again with
        # UNSET_EMPTY: an unknown reference is then -49, which pcrec moves to
        # the setup (§9 row 4)
        w2 = ref(c['pat'], c['flags'], c['tpl'], c['subj'], lim, 'empty', gaps=mode != 'nogap')
        if w2['kind'] == 'err' and w2['code'] == -49:
            return 'PASS', 'MISSING_REF at the setup; pcre2 -49 under UNSET_EMPTY (§9 row 4)'
    if want['kind'] == 'ok':
        ok = (got[0] == 'RUN' and got[1] == 0 and got[4] == 0 and got[7] == want['out']
              and got[3] == want['n'] and got[6] == want['n'] and got[2] == len(want['out']) and got[8] == 'ok')
    elif want['where'] == 'compile':
        return 'REF_ONLY', 'pcre2 cannot compile (%d); pcrec %s' % (want['code'], show(got))
    elif want['code'] == -49:
        ok = got[0] == 'BIND' and got[1] == -16
    elif want['code'] == -60:
        # §4¶5 / §9 row 9: a span the splice cannot express is BADSPAN
        ok = got[0] == 'RUN' and got[1] == -12 and got[2] == 0 and got[3] == 0 and got[8] == 'ok'
    elif want['code'] == -55:
        ok = got[0] == 'RUN' and got[1] == -14 and got[2] == 0 and got[3] == 0 and got[8] == 'ok'
    else:
        ok = False
    if ok:
        return ('FIXED?' if known else 'PASS'), mode if known else ''
    return (klabel if known else 'FAIL'), mode + ' | pcre2 %s | pcrec %s' % (showref(want), show(got))


def show(g):
    if g[0] == 'BIND':
        return 'BIND rc=%d bad=%d' % (g[1], g[2])
    return 'size(rc=%d len=%d k=%d) exact(rc=%d len=%d k=%d) out=%r notes=%s' % (g[1], g[2], g[3], g[4], g[5], g[6], esc(g[7]), g[8])


def showref(w):
    if w['kind'] == 'ok':
        return 'ok n=%d out=%r' % (w['n'], esc(w['out']))
    return 'err %d (%s)' % (w['code'], w['where'])


if __name__ == '__main__':
    main()
