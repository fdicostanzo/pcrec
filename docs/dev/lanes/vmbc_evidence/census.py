"""census.py PCREC MODE (--rx FILE... | --corpus TREE) [--limit N]
Population of the B/C rules: compile each pattern (default engine, --features all),
run vmopt MODE on VM artifacts, count movers. Prints one TSV row per artifact on
stdout (name, sets, dead, calls, W_total, restores_kept, status) and a summary on stderr."""
import os, re, subprocess, sys
V = '/var/tmp/pcrec-pcrec/scratch/vmbc'
pcrec, mode = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
limit = 0
if '--limit' in args:
    i = args.index('--limit'); limit = int(args[i+1]); args = args[:i] + args[i+2:]
pats = []
if args[0] == '--rx':
    for f in args[1:]:
        pats.append((os.path.basename(f), ['--pattern-file', f] if False else None, open(f, 'rb').read()))
else:
    tree = args[1]
    for root, _, files in os.walk(os.path.join(tree, 'tests')):
        for f in sorted(files):
            if not f.endswith('.rxt'):
                continue
            r = subprocess.run([pcrec, '--list-source', os.path.join(root, f)], capture_output=True, timeout=60)
            for ln in r.stdout.split(b'\n'):
                fl = ln.split(b'\t')
                if len(fl) >= 5 and fl[0] in (b'pattern', b'pattern-esc'):
                    pats.append((f, 'esc', fl[4]))
    seen = set(); u = []
    for p in pats:
        if p[2] in seen: continue
        seen.add(p[2]); u.append(p)
    pats = u
if limit:
    pats = pats[:limit]
tmp = os.path.join(V, 'tw', 'census.c'); out = os.path.join(V, 'tw', 'census_o.c')
tot = dict(n=0, vm=0, movers=0, dead_movers=0, call_movers=0, sets=0, dead=0, W=0, kept=0, bail=0)
for name, how, pat in pats:
    tot['n'] += 1
    if how == 'esc':
        cmd = [pcrec, '-p', 'rx', '--features', 'all', '--pattern-esc', '--pattern', '"' + pat.decode('latin-1').replace('"', '\\"') + '"', '-o', tmp]
    else:
        # a bench .rx file: the pattern text, newline-terminated; strip one trailing newline
        txt = pat.decode('latin-1')
        if txt.endswith('\n'): txt = txt[:-1]
        cmd = [pcrec, '-p', 'rx', '--features', 'all', '--pattern', txt, '-o', tmp]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(tmp):
        continue
    if b'_match_anchored(const' not in open(tmp, 'rb').read():
        os.unlink(tmp); continue
    r = subprocess.run(['python3', '-I', os.path.join(V, 'tools', 'vmopt.py'), '-m', mode, tmp, out], capture_output=True, text=True, timeout=300)
    os.unlink(tmp)
    st = dict(kv.split('=', 1) for kv in r.stderr.split() if '=' in kv and not kv.startswith('status'))
    status = 'ok' if 'status=ok' in r.stderr else 'bail'
    if status != 'ok':
        tot['bail'] += 1; print('%s\t%s\tBAIL\t%s' % (name, pat[:50], r.stderr.strip()[-80:])); continue
    sets, dead, calls = int(st.get('sets', 0)), int(st.get('dead', 0)), int(st.get('calls', 0))
    if sets == 0: continue
    tot['vm'] += 1
    W, kept = int(st.get('W', 0)), int(st.get('restores_kept', 0))
    # per-site W total: W counts per region; restores_kept is per site, so compare with snapshots
    snapd = int(st.get('snap_dropped', 0))
    mv = dead > 0 or snapd > 0
    tot['movers'] += mv; tot['dead_movers'] += dead > 0; tot['call_movers'] += snapd > 0
    tot['sets'] += sets; tot['dead'] += dead; tot['kept'] += kept
    print('%s\t%r\tsets=%d dead=%d calls=%d snap_dropped=%d restores_kept=%d' % (name, pat[:60], sets, dead, calls, snapd, kept))
sys.stderr.write('census %s: patterns %d, VM artifacts with a slot write %d, movers %d (dead writes %d, narrowed calls %d), bails %d, sets %d, dead sets %d\n'
                 % (mode, tot['n'], tot['vm'], tot['movers'], tot['dead_movers'], tot['call_movers'], tot['bail'], tot['sets'], tot['dead']))
