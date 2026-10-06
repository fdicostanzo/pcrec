import sys, os, hashlib
sys.dont_write_bytecode = True
B = '/Users/fdicostanzo/pcrec-bench/bench/capability'
sys.path.insert(0, B); sys.path.insert(0, os.path.dirname(os.path.dirname(B)))
import gen_subjects as gs
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
man = {l.split('\t')[0]: l.split('\t')[2] for l in open(B + '/manifest.tsv').read().splitlines()[1:]}
bad = 0
for sid, desc, body in gs.build():
    open(os.path.join(out, sid + '.bin'), 'wb').write(body)
    if hashlib.sha256(body).hexdigest() != man[sid]: bad += 1; print('HASH MISMATCH', sid)
print(len(gs.SUBJECTS), 'subjects written;', bad, 'hash mismatches vs manifest.tsv')
