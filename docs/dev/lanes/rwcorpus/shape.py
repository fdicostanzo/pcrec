# shape.py -- run as: python3 -I shape.py CORPUS_DIR MANIFEST.tsv  > table.md
# Basic shape facts per manifest file: size, lines, line-length quantiles,
# top-10 bytes, ASCII / UTF-8 multibyte / invalid shares, distinct bytes.
import collections, sys

def q(s, p):
    return s[min(len(s) - 1, int(p * len(s)))]

def shape(path):
    d = open(path, 'rb').read()
    n = len(d)
    hist = collections.Counter(d)
    ascii_ = sum(v for k, v in hist.items() if k < 128)
    t = d.decode('utf-8', 'surrogateescape')
    inv = sum(1 for ch in t if '\udc80' <= ch <= '\udcff') if n - ascii_ else 0
    multi = n - ascii_ - inv
    lens = sorted(len(x) for x in d.split(b'\n'))
    top = ' '.join('%s:%.1f%%' % (repr(bytes([k]))[2:-1], 100.0 * v / n) for k, v in hist.most_common(10))
    return (n, d.count(b'\n'), lens[0], q(lens, .5), q(lens, .9), q(lens, .99), lens[-1], len(hist),
            100.0 * ascii_ / n, 100.0 * multi / n, 100.0 * inv / n, top)

def main(C, man):
    print('| file | bytes | lines | len min/p50/p90/p99/max | distinct | ASCII % | UTF-8 multibyte % | invalid % | top-10 bytes |')
    print('|---|---|---|---|---|---|---|---|---|')
    for ln in open(man).read().splitlines()[1:]:
        c, f = ln.split('\t')[:2]
        if '/raw/' in f and c != 'binary':
            continue
        n, nl, a, b, c9, c99, z, dist, pa, pm, pi, top = shape(f'{C}/{f}')
        print(f'| {f} | {n} | {nl} | {a}/{b}/{c9}/{c99}/{z} | {dist} | {pa:.2f} | {pm:.2f} | {pi:.2f} | `{top}` |'.replace('|`', '| `'))

if __name__ == '__main__':
    main(*sys.argv[1:3])
