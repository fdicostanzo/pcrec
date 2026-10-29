"""census_tg.py SAMPLE.tsv OUT.tsv : lane trailgen's dynamic trail census over a declared bench sample.

Per pattern (one pcrec compile, single process): emit with lane/trailgc's pcrec (D183),
check the artifact is VM, make the B+C twin (vmbc's vmopt.py -m BCd), the R twin
(variants.py, register-resident run cursors) and the no-trail bound, build each with
gdrv.c (every non-overlapping match over the bench subject, default arm), and record:
  static: SET sites, dead (B) sites, linked/spliced calls
  dynamic (counting twins): trail entries, frames pushed, entries undone; per subject byte
  instructions:u per pass ((REPS=3 - REPS=1)/2): stock, R, notrail, BCd, BCd+R
  identity: matches + span checksum of every twin equal stock's
"""
import os, re, subprocess, sys
T = '/var/tmp/pcrec-pcrec/scratch/trailgen'
PCREC = '/home/pcrec/projects/pcrec/worktrees/trailgen/build/pcrec'
BENCH = '/home/pcrec/projects/pcrec-bench/bench'
VMOPT = '/var/tmp/pcrec-pcrec/scratch/vmbc/tools/vmopt.py'


def sh(cmd, timeout=300, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=e)


def instr(drv, subj):
    def one(reps):
        r = sh(['perf', 'stat', '-x,', '-e', 'instructions:u', drv, subj], timeout=600, env={'REPS': str(reps)})
        for l in r.stderr.split('\n'):
            if 'instructions' in l:
                return int(l.split(',')[0])
        raise RuntimeError('perf: ' + r.stderr[-200:])
    return (one(3) - one(1)) / 2.0


def main():
    rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
    out = open(sys.argv[2], 'a')
    for sb, pid, sid, spath, nbytes, reg, form, thex in rows:
        name = '%s__%s' % (sb, pid)
        d = os.path.join(T, 'cs', name)
        os.makedirs(os.path.join(d, 'src'), exist_ok=True)
        os.makedirs(os.path.join(d, 'srcB'), exist_ok=True)
        if sb == 'subst':
            subj = os.path.join(T, 'subj', 'acc-small.bin')
        elif spath != '-':
            subj = spath
        else:
            subj = os.path.join(BENCH, sb, 'throughput', sid + '.bin')
        res = {'name': name, 'subject': os.path.basename(subj)}
        try:
            text = bytes.fromhex(thex).decode('utf-8')
            if os.path.exists(os.path.join(d, 'src', 'rx.h')):   # emitted by an earlier pass of this sample
                r = subprocess.CompletedProcess([], 0, '', '')
            else:
                r = sh([PCREC, '-p', 'rx', '--features', 'all', '--pattern', text, '-o', os.path.join(d, 'src', 'rx.c')], timeout=120)
            if r.returncode != 0:
                raise RuntimeError('pcrec rc=%d %s' % (r.returncode, r.stderr.strip()[-120:]))
            c = open(os.path.join(d, 'src', 'rx.c')).read()
            m = re.search(r'#define RX_ENGINE "(\w+)"', c)
            res['engine'] = m.group(1) if m else '?'
            if res['engine'] != 'vm':
                raise RuntimeError('engine ' + res['engine'])
            m = re.search(r'#define RX_VM_CALL_SPLICED (\d+)', c); res['spliced'] = int(m.group(1)) if m else 0
            m = re.search(r'#define RX_VM_CALL_LINKED (\d+)', c); res['linked'] = int(m.group(1)) if m else 0
            res['set_sites'] = len(re.findall(r'^\s*RX_SET\(', c, re.M))
            res['push_sites'] = len(re.findall(r'^\s*RX_(PUSH|CALL)\(', c, re.M))
            r = sh(['python3', '-I', VMOPT, '-m', 'BCd', os.path.join(d, 'src', 'rx.c'), os.path.join(d, 'srcB', 'rx.c')])
            st = dict(kv.split('=', 1) for kv in r.stderr.split() if '=' in kv)
            res['vmopt'] = st.get('status', '?')
            res['dead_sites'] = st.get('dead', '-')
            res['snap_dropped'] = st.get('snap_dropped', '-')
            haveB = res['vmopt'] == 'ok'
            if haveB:
                open(os.path.join(d, 'srcB', 'rx.h'), 'w').write(open(os.path.join(d, 'src', 'rx.h')).read())
            builds = [('stock', 'src', 'stock'), ('cnt', 'src', 'cnt'), ('R', 'src', 'R'), ('notrail', 'src', 'notrail')]
            if haveB:
                builds += [('B', 'srcB', 'stock'), ('Bcnt', 'srcB', 'cnt'), ('BR', 'srcB', 'R')]
            bins = {}
            for tag, sdir, mode in builds:
                r = sh(['bash', os.path.join(T, 'mkv.sh'), os.path.join(d, sdir), os.path.join(d, tag), mode, os.path.join(T, 'gdrv.c')], timeout=600)
                if r.returncode != 0:
                    res['build_' + tag] = 'FAIL'
                    continue
                bins[tag] = os.path.join(d, tag, 'drv')
            outs = {}
            for tag in bins:
                r = sh([bins[tag], subj], timeout=600, env={'REPS': '1'})
                outs[tag] = r.stdout.strip()
                if tag in ('cnt', 'Bcnt'):
                    m = re.search(r'tg trail=(\d+) push=(\d+) undo=(\d+)', r.stderr)
                    if m:
                        res[tag + '_trail'], res[tag + '_push'], res[tag + '_undo'] = (int(x) for x in m.groups())
            ref = outs.get('stock', '')
            res['matches'] = (re.search(r'matches=(\d+)', ref) or [0, '?'])[1]
            res['err'] = (re.search(r'err=(-?\d+)', ref) or [0, '?'])[1]
            res['n'] = (re.search(r'n=(\d+)', ref) or [0, '0'])[1]
            res['ident'] = ','.join('%s=%s' % (t, 'ok' if outs[t] == ref else 'DIFF') for t in outs if t not in ('stock', 'notrail'))
            for tag in ('stock', 'R', 'notrail', 'B', 'BR'):
                if tag in bins:
                    res['i_' + tag] = '%.0f' % instr(bins[tag], subj)
            res['status'] = 'ok'
        except Exception as e:  # noqa
            res['status'] = 'skip: %s' % str(e)[:160]
        out.write('\t'.join('%s=%s' % kv for kv in res.items()) + '\n')
        out.flush()
        sys.stderr.write('%s %s\n' % (name, res.get('status')))


main()
