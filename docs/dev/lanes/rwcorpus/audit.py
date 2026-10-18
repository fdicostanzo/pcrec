#!/usr/bin/env python3
"""Audit a corpus class dir: encoding validity, mojibake, script mix, CRLF, PG header labels.
Usage: python3 -I audit.py CLASSDIR   (reads only)"""
import sys, os, re, unicodedata, collections
d = sys.argv[1]
MOJ = re.compile('Ã[\u0080-¿]|â€|Ð[\u0080-¿]|Î[\u0080-¿]|å[\u0080-¿]{2}|ã\u0081|ã\u0082')
def script(c):
    o = ord(c)
    if c.isascii(): return 'ascii'
    n = unicodedata.name(c, '')
    for k in ('CJK','HIRAGANA','KATAKANA','CYRILLIC','GREEK','HEBREW','LATIN','HANGUL','ARABIC'):
        if n.startswith(k): return k
    return 'other'
for f in sorted(os.listdir(d)):
    b = open(os.path.join(d, f), 'rb').read()
    try: t = b.decode('utf-8'); ok = 'utf8'
    except UnicodeDecodeError as e: t = b.decode('utf-8', 'replace'); ok = 'INVALID@%d' % e.start
    h = t[:4000]
    lang = re.search(r'^Language:\s*(.+)$', h, re.M); enc = re.search(r'^Character set encoding:\s*(.+)$', h, re.M)
    title = re.search(r'^Title:\s*(.+)$', h, re.M)
    sc = collections.Counter(script(c) for c in t if c.isalpha())
    tot = sum(sc.values()) or 1
    top = ' '.join('%s%d%%' % (k[:4], 100*v//tot) for k, v in sc.most_common(3))
    moj = len(MOJ.findall(t))
    crlf = b.count(b'\r\n'); lf = b.count(b'\n')
    print('\t'.join([f, ok, 'lang=' + (lang.group(1).strip() if lang else '?'), 'enc=' + (enc.group(1).strip() if enc else '?'),
        'moj=%d' % moj, 'crlf=%d/%d' % (crlf, lf), top, (title.group(1).strip() if title else '?')[:50]]))
