# prep.py -- run as: python3 -I prep.py CORPUS_DIR
"""Derive the subject files from the raw downloads. Usage: prep.py CORPUS_DIR

Reads archives with tarfile/zipfile (data filter, nothing is executed or
built), writes derived subjects next to raw/ in each class dir, and prints
nothing on success.  Deterministic: same raws -> same bytes.  Scrubbing
(IPv4 -> hashed 10.x.y.z, e-mail addresses, rhost=/user= values) applies to
the logs, code, markup and structured classes; prose is left as published.
DERIVED is the table manifest.py reads for the provenance rows.
"""
import hashlib, io, os, re, sys, tarfile, zipfile

MAXOUT = 40 << 20
IPV4 = re.compile(rb'(?<!\d)(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\d.]*\d)')
EMAIL = re.compile(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
RHOST = re.compile(rb'\b(rhost|user)=\S+')
CONN = re.compile(rb'(connection from \S+ \()[^)]*\)')

def ip_sub(m):
    if any(int(g) > 255 for g in m.groups()):
        return m.group(0)
    h = hashlib.sha1(m.group(0)).digest()
    return b'10.%d.%d.%d' % (h[0], h[1], h[2])

def scrub(b, ips=False, kv=False):
    b = EMAIL.sub(b'user@example.invalid', b)
    if ips:
        b = IPV4.sub(ip_sub, b)
    if kv:
        b = RHOST.sub(rb'\1=scrubbed', b)
        b = CONN.sub(rb'\1host.invalid)', b)
    return b

def cut(b, cap=MAXOUT):
    """Truncate at a line boundary under cap."""
    if len(b) <= cap:
        return b
    i = b.rfind(b'\n', 0, cap)
    return b[:i + 1]

def tar_members(path):
    with tarfile.open(path) as t:
        for m in sorted(t.getmembers(), key=lambda m: m.name):
            if m.isfile():
                yield m.name, t.extractfile(m).read()

def zip_members(path):
    with zipfile.ZipFile(path) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('/'):
                yield n, z.read(n)

def nl(b):
    return b if b.endswith(b'\n') or not b else b + b'\n'

def write(C, cls, name, data):
    os.makedirs(f'{C}/{cls}', exist_ok=True)
    with open(f'{C}/{cls}/{name}', 'wb') as f:
        f.write(data)

DERIVED = []   # (class, name, derived-from description, license)

def derive(C, cls, name, src, lic, data):
    write(C, cls, name, data)
    DERIVED.append((cls, name, 'derived by prep.py from ' + src, lic))

def logs(C):
    R = f'{C}/logs/raw/'
    lh = 'CC-BY-4.0 (Loghub, Zenodo 8196385); IPv4/email/rhost/user scrubbed'
    for arch, member, out in [('Apache.tar.gz', 'Apache.log', 'apache_error.log'),
                              ('Linux.tar.gz', 'Linux.log', 'linux_syslog.log'),
                              ('Zookeeper.tar.gz', 'Zookeeper.log', 'zookeeper.log')]:
        d = dict(tar_members(R + arch))[member]
        derive(C, 'logs', out, 'logs/raw/' + arch, lh, cut(scrub(d, True, True)))
    d = b''.join(nl(v) for k, v in tar_members(R + 'OpenStack.tar.gz') if k.endswith('.log'))
    derive(C, 'logs', 'openstack.log', 'logs/raw/OpenStack.tar.gz (*.log sorted, concatenated, cut at 40 MiB)', lh,
           cut(scrub(d, True, True)))
    d = b''.join(nl(v) for k, v in zip_members(R + 'Hadoop.zip') if k.endswith('.log'))
    derive(C, 'logs', 'hadoop.log', 'logs/raw/Hadoop.zip (*.log sorted, concatenated)', lh, cut(scrub(d, True, True)))
    with zipfile.ZipFile(R + 'BGL.zip') as z:
        n = [x for x in z.namelist() if x.endswith('.log')][0]
        with z.open(n) as f:
            d = f.read(MAXOUT + (1 << 20))
    derive(C, 'logs', 'bgl.log', 'logs/raw/BGL.zip first 40 MiB (line boundary)', lh, cut(scrub(d, True, True)))
    d = open(R + 'apache_logs', 'rb').read()
    derive(C, 'logs', 'apache_access.log', 'logs/raw/apache_logs',
           'Apache-2.0 (elastic/examples); IPv4/email scrubbed', scrub(d, True, True))

CODE_EXT = {'c': ('.c', '.h'), 'javascript': ('.js',), 'rust': ('.rs',), 'python': ('.py',),
            'go': ('.go',), 'java': ('.java',)}
CODE_SRC = [('c', 'lua-5.4.7.tar.gz', 'MIT'), ('c', 'redis-7.2.4.tar.gz', 'BSD-3-Clause'),
            ('javascript', 'jquery-3.7.1.tar.gz', 'MIT'), ('rust', 'ripgrep-14.1.0.tar.gz', 'MIT OR Unlicense'),
            ('python', 'django-5.0.tar.gz', 'BSD-3-Clause'), ('go', 'cobra-1.8.0.tar.gz', 'Apache-2.0'),
            ('java', 'guava-33.0.0.tar.gz', 'Apache-2.0')]

def code(C):
    acc = {}
    for lang, arch, lic in CODE_SRC:
        for k, v in tar_members(f'{C}/code/raw/{arch}'):
            if '/deps/' in k or '/node_modules/' in k or len(v) > (2 << 20):
                continue
            if k.endswith(CODE_EXT[lang]):
                acc.setdefault(lang, []).append((arch, lic, nl(v)))
    for lang, items in sorted(acc.items()):
        d = b''.join(x[2] for x in items)
        derive(C, 'code', f'{lang}.src', 'code/raw/' + ', '.join(sorted({x[0] for x in items})) +
               f' (*{"/*".join(CODE_EXT[lang])} files sorted by path, concatenated, no deps/, cut at 40 MiB)',
               ' + '.join(sorted({x[1] for x in items})) + '; emails scrubbed', cut(scrub(d)))

def markup(C):
    pth = f'{C}/markup/raw/python-3.12.7-docs-html.tar.bz2'
    lic = 'PSF License Agreement / 0BSD (Python documentation); emails scrubbed'
    html = b''.join(nl(v) for k, v in tar_members(pth) if k.endswith('.html'))
    derive(C, 'markup', 'python_docs.html', 'markup/raw/python-3.12.7-docs-html.tar.bz2 (*.html sorted, concatenated, cut at 40 MiB)',
           lic, cut(scrub(html)))
    rst = b''.join(nl(v) for k, v in tar_members(f'{C}/code/raw/django-5.0.tar.gz') if '/docs/' in k and k.endswith('.txt'))
    derive(C, 'markup', 'django_docs.rst', 'code/raw/django-5.0.tar.gz (docs/**/*.txt, reStructuredText)',
           'BSD-3-Clause (Django; docs CC-BY-3.0-or-BSD per upstream); emails scrubbed', cut(scrub(rst)))
    js = b''.join(nl(v) for k, v in tar_members(f'{C}/code/raw/jquery-3.7.1.tar.gz') if k.endswith('.md'))
    if js:
        derive(C, 'markup', 'jquery_md.md', 'code/raw/jquery-3.7.1.tar.gz (*.md)', 'MIT; emails scrubbed', cut(scrub(js)))

def structured(C):
    R = f'{C}/structured/raw/'
    gz = dict(zip_members(R + 'gaz_place.zip'))
    n = [k for k in gz if k.endswith('.txt')][0]
    derive(C, 'structured', 'census_gazetteer_places.tsv', 'structured/raw/gaz_place.zip', 'US Government work, public domain', gz[n])
    xml = b''.join(nl(v) for k, v in zip_members(R + 'BILLS-118-1-hr.zip') if k.endswith('.xml'))
    derive(C, 'structured', 'govinfo_bills.xml', 'structured/raw/BILLS-118-1-hr.zip (*.xml sorted, concatenated, cut at 40 MiB)',
           'US Government work, public domain; emails scrubbed', cut(scrub(xml)))
    for f in ('usgs_2024q1.csv', 'usgs_2024q1.geojson', 'ne_10m_admin_0_countries.geojson'):
        derive(C, 'structured', f, 'structured/raw/' + f, 'see raw row', open(R + f, 'rb').read())

def binary(C):
    src = f'{C}/code/raw/django-5.0.tar.gz'
    import gzip
    d = gzip.open(src, 'rb').read()
    derive(C, 'binary', 'django-5.0.tar', 'code/raw/django-5.0.tar.gz gunzipped (uncompressed tar: headers + mixed text/.mo/images)', 'BSD-3-Clause', cut(d, 48 << 20))
    d = gzip.open(f'{C}/binary/raw/libpng-1.6.43.tar.gz', 'rb').read()
    derive(C, 'binary', 'libpng-1.6.43.tar', 'binary/raw/libpng-1.6.43.tar.gz gunzipped (tar with PNG files)', 'PNG Reference Library License v2', d)
    for cls, rel in [('binary', 'binary/raw/libpng-1.6.43.tar.gz'), ('binary', 'markup/raw/python-3.12.7-docs-html.tar.bz2'),
                     ('binary', 'structured/raw/BILLS-118-1-hr.zip')]:
        d = open(f'{C}/{rel}', 'rb').read()
        derive(C, cls, os.path.basename(rel), rel + ' (verbatim copy: compressed, high-entropy stream)', 'see raw row', d)

def main(C):
    logs(C); code(C); markup(C); structured(C); binary(C)
    with open(f'{C}/derived.tsv', 'w') as f:
        for r in DERIVED:
            f.write('\t'.join(r) + '\n')

if __name__ == '__main__':
    main(sys.argv[1])
