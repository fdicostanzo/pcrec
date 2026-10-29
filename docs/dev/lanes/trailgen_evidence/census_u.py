"""census_u.py CENSUS.tsv OUT.tsv : second pass over the same sample (no pcrec compile):
the UNDO-DEAD twin (vmopt_tg.py -m BCdU) and UNDO-DEAD + R, built with gdrv.c;
identity (matches + span checksum) against the stock run, trail counts, instructions."""
import os, re, subprocess, sys
T = '/var/tmp/pcrec-pcrec/scratch/trailgen'
sys.path.insert(0, T)


def sh(cmd, timeout=600, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=e)


def instr(drv, subj):
    def one(reps):
        r = sh(['perf', 'stat', '-x,', '-e', 'instructions:u', drv, subj], env={'REPS': str(reps)})
        for l in r.stderr.split('\n'):
            if 'instructions' in l:
                return int(l.split(',')[0])
        raise RuntimeError('perf')
    return (one(3) - one(1)) / 2.0


out = open(sys.argv[2], 'a')
for l in open(sys.argv[1]):
    d = dict(kv.split('=', 1) for kv in l.rstrip('\n').split('\t'))
    if d.get('status') != 'ok':
        continue
    base = os.path.join(T, 'cs', d['name'])
    sb = d['name'].split('__')[0]
    subj = os.path.join(T, 'subj', 'acc-small.bin') if sb == 'subst' else os.path.join(
        '/home/pcrec/projects/pcrec-bench/bench', sb, 'throughput', d['subject'])
    if not os.path.exists(subj):
        subj = os.path.join('/home/pcrec/projects/pcrec-bench/bench/capability/subjects', d['subject'])
    res = {'name': d['name']}
    os.makedirs(os.path.join(base, 'srcU'), exist_ok=True)
    r = sh(['python3', '-I', os.path.join(T, 'vmopt_tg.py'), '-m', 'BCdU', os.path.join(base, 'src', 'rx.c'), os.path.join(base, 'srcU', 'rx.c')])
    st = dict(kv.split('=', 1) for kv in r.stderr.split() if '=' in kv)
    res['vmoptU'] = st.get('status', '?'); res['undo_dead_sites'] = st.get('undo_dead', '-')
    if res['vmoptU'] != 'ok':
        out.write('\t'.join('%s=%s' % kv for kv in res.items()) + '\n'); out.flush(); continue
    open(os.path.join(base, 'srcU', 'rx.h'), 'w').write(open(os.path.join(base, 'src', 'rx.h')).read())
    bins = {}
    for tag, mode in (('U', 'stock'), ('Ucnt', 'cnt'), ('UR', 'R')):
        r = sh(['bash', os.path.join(T, 'mkv.sh'), os.path.join(base, 'srcU'), os.path.join(base, tag), mode, os.path.join(T, 'gdrv.c')])
        if r.returncode == 0:
            bins[tag] = os.path.join(base, tag, 'drv')
        else:
            res['build_' + tag] = 'FAIL'
    ref = sh([os.path.join(base, 'stock', 'drv'), subj], env={'REPS': '1'}).stdout.strip()
    idl = []
    for tag in bins:
        r = sh([bins[tag], subj], env={'REPS': '1'})
        idl.append('%s=%s' % (tag, 'ok' if r.stdout.strip() == ref else 'DIFF'))
        if tag == 'Ucnt':
            m = re.search(r'tg trail=(\d+) push=(\d+) undo=(\d+)', r.stderr)
            if m:
                res['Ucnt_trail'] = m.group(1)
    res['identU'] = ','.join(idl)
    for tag in ('U', 'UR'):
        if tag in bins:
            res['i_' + tag] = '%.0f' % instr(bins[tag], subj)
    out.write('\t'.join('%s=%s' % kv for kv in res.items()) + '\n'); out.flush()
    sys.stderr.write('%s %s\n' % (d['name'], res['identU']))
