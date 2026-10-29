"""census.py PCREC OUTDIR (--rx FILE... | --list TSV) : population of candidate D.
Compiles each pattern (--features all, default engine), and on VM artifacts runs
altd.py (-m AL, ALTD_RULE=kind, ALTD_FOLLOW=1) into OUTDIR; one TSV row per pattern
on stdout: name, route, choice sites, rewritten (alt / loop+opt), declined, classes."""
import os, re, subprocess, sys
A = '/var/tmp/pcrec-pcrec/scratch/altd'
W = '/home/pcrec/projects/pcrec/worktrees/trailgc'
pcrec, out = sys.argv[1], sys.argv[2]
pats = []
if sys.argv[3] == '--rx':
    for f in sys.argv[4:]:
        pats.append((os.path.basename(f), open(f, 'rb').read().decode('latin-1')))
else:
    for ln in open(sys.argv[4], encoding='latin-1'):
        n, p = ln.rstrip('\n').split('\t', 1)
        pats.append((n, p))
os.makedirs(out, exist_ok=True)
tot = dict(n=0, vm=0, movers=0, alt=0, loop=0, declined=0, sites=0, refused=0)
for name, pat in pats:
    tot['n'] += 1
    c = os.path.join(out, 'a.c'); ir = os.path.join(out, 'a.ir'); o = os.path.join(out, 'o.c')
    r = subprocess.run([pcrec, '--features', 'all', '-p', 'rx', '-o', c, '--pattern', pat], capture_output=True, timeout=120)
    if r.returncode:
        print('%s\terror' % name); continue
    txt = open(c, encoding='latin-1').read()
    if 'RX_PUSH(&&' not in txt:
        print('%s\tnon-vm-or-no-push' % name); continue
    tot['vm'] += 1
    subprocess.run([pcrec, '--features', 'all', '-p', 'rx', '--emit-ir', '--pattern', pat], stdout=open(ir, 'w'), stderr=subprocess.DEVNULL, timeout=120)
    env = dict(os.environ, ALTD_RULE='kind', ALTD_FOLLOW='1', ALTD_CFLAGS='-I%s/lib -I%s' % (W, out))
    r = subprocess.run(['python3', '-I', A + '/tools/altd.py', '-m', 'AL', c, ir, o], capture_output=True, text=True, env=env, timeout=300)
    if r.returncode:
        tot['refused'] += 1; print('%s\trefused\t%s' % (name, r.stderr.strip().split('\n')[-1][:80])); continue
    log = r.stderr.split('\n')
    alt = sum(1 for l in log if re.match(r'\s+rx_\w+ branch ', l))
    loop = sum(1 for l in log if re.match(r'\s+rx_\w+ (the loop|another iter|body pref)', l))
    dec = sum(1 for l in log if ' decline ' in l or ' keep ' in l)
    m = re.search(r'sites=(\d+) rewritten=(\d+) classes=(\d+)', r.stderr)
    tot['sites'] += int(m.group(1)); tot['alt'] += alt; tot['loop'] += loop; tot['declined'] += dec
    if int(m.group(2)): tot['movers'] += 1
    print('%s\tvm\tsites=%s\trewritten=%s\talt=%d\tloop_opt=%d\tdeclined=%d\tclasses=%s' % (name, m.group(1), m.group(2), alt, loop, dec, m.group(3)))
    sys.stdout.flush()
sys.stderr.write('census: %s\n' % ' '.join('%s=%d' % kv for kv in tot.items()))
