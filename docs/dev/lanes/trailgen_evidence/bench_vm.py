"""bench_vm.py STORE BENCHDIR : for the newest auto-caps pcrec record per subbench, every VM-routed pattern
with its canonical text and the largest subject it is timed on. TSV:
subbench pattern_id subject_id subject_path bytes regime form text_hex"""
import json, os, sys, glob, hashlib
root, bench = sys.argv[1], sys.argv[2]
sha2path = {}
for p in glob.glob(os.path.join(bench, '**', '*'), recursive=True):
    if os.path.isfile(p) and ('/subjects/' in p or '/cases/' in p) and 0 < os.path.getsize(p) < 600_000_000:
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        sha2path.setdefault(h, p)
best = {}
for sb in sorted(os.listdir(root)):
    name = sb.split('@')[0]
    for f in glob.glob(os.path.join(root, sb, 'pcrec_*_auto-caps*', '*.jsonl')):
        ts = f.rsplit('__', 1)[1]
        if name not in best or (sb, ts) > best[name][0]:
            best[name] = ((sb, ts), f)
for name, (_, f) in sorted(best.items()):
    head = None; eng = {}; subj = {}; texts = {}; pairs = {}
    for l in open(f):
        d = json.loads(l)
        if head is None:
            head = d
            for s in d.get('subjects', []):
                subj[s['subject_id']] = s
            for p in d.get('patterns', []):
                texts[p['pattern_id']] = p.get('canonical_text')
            continue
        if d.get('kind') == 'compile' and 'engine_metadata' in d:
            eng[d['pattern_id']] = d['engine_metadata'].get('engine')
        elif d.get('kind') == 'match':
            pairs.setdefault(d['pattern_id'], set()).add((d['subject_id'], d.get('regime'), d.get('form')))
    for k in sorted(eng):
        if eng[k] != 'vm':
            continue
        cands = []
        for sid, reg, form in pairs.get(k, ()):
            s = subj.get(sid, {})
            cands.append((s.get('bytes_offered', 0), sid, sha2path.get(s.get('sha256'), '-'), reg, form))
        cands.sort(reverse=True)
        t = (texts.get(k) or '').encode('utf-8').hex()
        if not cands:
            print('%s\t%s\t-\t-\t0\t-\t-\t%s' % (name, k, t)); continue
        b, sid, path, reg, form = cands[0]
        print('%s\t%s\t%s\t%s\t%d\t%s\t%s\t%s' % (name, k, sid, path, b, reg, form, t))
