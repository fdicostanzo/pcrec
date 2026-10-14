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

if __name__ == '__main__' and len(sys.argv) < 4:
    main(*sys.argv[1:3])

# scripts.py-style appendix: python3 -I shape.py CORPUS MANIFEST --scripts
def scripts(C, man):
    import unicodedata
    B = [(0x0400, 0x04FF, 'Cyrillic'), (0x0370, 0x03FF, 'Greek'), (0x0590, 0x05FF, 'Hebrew'),
         (0x0600, 0x06FF, 'Arabic'), (0x0900, 0x097F, 'Devanagari'), (0x3040, 0x30FF, 'Kana'),
         (0x4E00, 0x9FFF, 'CJK'), (0x3400, 0x4DBF, 'CJK-ExtA'), (0xF900, 0xFAFF, 'CJK-compat'),
         (0x0080, 0x024F, 'Latin-ext')]
    print('| file | non-ASCII chars | script shares of non-ASCII chars |')
    print('|---|---|---|')
    for ln in open(man).read().splitlines()[1:]:
        f = ln.split('\t')[1]
        if not f.startswith('nonenglish/'):
            continue
        t = open(f'{C}/{f}', 'rb').read().decode('utf-8', 'replace')
        c = collections.Counter()
        for ch in t:
            o = ord(ch)
            if o >= 128:
                c[next((n for a, b, n in B if a <= o <= b), 'other')] += 1
        tot = sum(c.values()) or 1
        print(f'| {f} | {tot} | ' + ', '.join(f'{k} {100 * v / tot:.0f}%' for k, v in c.most_common(4)) + ' |')

if len(sys.argv) > 3 and sys.argv[3] == '--scripts':
    scripts(*sys.argv[1:3])
