# manifest.py -- run as: python3 -I manifest.py CORPUS_DIR (--write|--check) SOURCES.tsv MANIFEST.tsv
# Rows: raw downloads (from sources.tsv) + derived subjects (CORPUS/derived.tsv, written by prep.py).
# --check exits 1 on any sha mismatch of a non-volatile row; VOLATILE rows only warn.
import hashlib, os, sys

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def main(C, mode, src, man):
    rows = []
    for ln in open(src).read().splitlines()[1:]:
        c, rel, url, lic, date = ln.split('\t')
        p = rel
        rows.append((c, f'{c}/{p}', url, lic, date))
    date = rows[0][4]
    for ln in open(f'{C}/derived.tsv').read().splitlines():
        c, name, frm, lic = ln.split('\t')
        rows.append((c, f'{c}/{name}', frm, lic, date))
    out = []
    for c, rel, url, lic, d in rows:
        p = f'{C}/{rel}'
        out.append((c, rel, str(os.path.getsize(p)), sha(p), url, lic, d))
    if mode == '--write':
        with open(man, 'w') as f:
            f.write('class\tfile\tbytes\tsha256\turl\tlicense\tdate\n')
            for r in out:
                f.write('\t'.join(r) + '\n')
        print('wrote', len(out), 'rows')
        return 0
    old = {l.split('\t')[1]: l.split('\t') for l in open(man).read().splitlines()[1:]}
    bad = 0
    for r in out:
        o = old.get(r[1])
        if o is None or o[3] != r[3]:
            vol = 'VOLATILE' in r[5]
            print(('WARN' if vol else 'FAIL'), r[1], 'sha256 differs from manifest')
            bad += 0 if vol else 1
    print('checked', len(out), 'rows,', bad, 'failures')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:5]))
